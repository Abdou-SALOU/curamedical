from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from .models import Consultation
from .serializers import (
    ConsultationSerializer,
    ConsultationListSerializer,
)
from .ia_client import obtenir_suggestions_ia
from .utils import generer_pdf_compte_rendu
from .tasks import send_consultation_report_task
from apps.common.tasks import dispatch_task
from apps.users.permissions import (
    EstMedecin,
    EstStaffOuAdministrateur,
    EstAdministrateur,
    EstPatient
)


class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['medecin', 'patient', 'ia_utilisee']
    search_fields = ['symptomes', 'diagnostic', 'patient__nom', 'patient__prenom']
    ordering_fields = ['date_consultation']
    ordering = ['-date_consultation']

    def get_serializer_class(self):
        if self.action == 'list':
            return ConsultationListSerializer
        return ConsultationSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [EstMedecin()]
        if self.action in ['destroy', 'restaurer', 'supprimer_definitif']:
            return [EstStaffOuAdministrateur()]
        if self.action == 'corbeille':
            return [permissions.IsAuthenticated()]
        if self.action in [
            'suggestions_ia', 'stats_pathologies', 'stats_periode', 'stats_ia'
        ]:
            return [EstMedecin()]
        if self.action == 'compte_rendu_pdf':
            if not self.request.user.is_authenticated:
                return [permissions.IsAuthenticated()]
            return [EstMedecin() if getattr(self.request.user, 'role', '') == 'medecin' else EstPatient()]
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [EstStaffOuAdministrateur()]

    def get_queryset(self):
        user = self.request.user
        qs = Consultation.objects.select_related('patient', 'medecin').filter(est_supprime=False)
        if user.role == 'medecin':
            return qs.filter(medecin=user)
        if user.role == 'patient':
            return qs.filter(patient__utilisateur=user)
        if user.role == 'secretaire':
            return qs.all()
        # Administrateur : aucun accès aux données médicales
        return Consultation.objects.none()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.est_supprime = True
        instance.supprime_le = timezone.now()
        instance.save(update_fields=['est_supprime', 'supprime_le'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='corbeille')
    def corbeille(self, request):
        user = request.user
        qs = Consultation.objects.select_related('patient', 'medecin').filter(est_supprime=True)
        if user.role == 'medecin':
            qs = qs.filter(medecin=user)
        elif user.role == 'patient':
            qs = qs.filter(patient__utilisateur=user)
        from .serializers import ConsultationListSerializer
        serializer = ConsultationListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='restaurer')
    def restaurer(self, request, pk=None):
        instance = Consultation.objects.filter(pk=pk, est_supprime=True).first()
        if not instance:
            return Response({'detail': 'Introuvable dans la corbeille.'}, status=status.HTTP_404_NOT_FOUND)
        instance.est_supprime = False
        instance.supprime_le = None
        instance.save(update_fields=['est_supprime', 'supprime_le'])
        return Response({'detail': 'Consultation restaurée.'})

    @action(detail=True, methods=['delete'], url_path='supprimer-definitif')
    def supprimer_definitif(self, request, pk=None):
        instance = Consultation.objects.filter(pk=pk, est_supprime=True).first()
        if not instance:
            return Response({'detail': 'Introuvable dans la corbeille.'}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        rdv = serializer.validated_data.get('rendez_vous')
        patient = serializer.validated_data.get('patient') or (rdv.patient if rdv else None)
        if not patient:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'patient': 'Patient requis (ou sélectionnez un rendez-vous).'})
        consultation = serializer.save(medecin=self.request.user, patient=patient)
        if consultation.rendez_vous:
            consultation.rendez_vous.statut = 'TERMINE'
            consultation.rendez_vous.save(update_fields=['statut'])
        # Compte-rendu PDF + n8n + WhatsApp en tâche de fond (Celery / thread de repli)
        dispatch_task(send_consultation_report_task, consultation.id)

    # ─── Module IA ────────────────────────────────────────────

    @action(detail=False, methods=['post'], url_path='suggestions-ia')
    def suggestions_ia(self, request):
        """Appelle le microservice IA — retourne top 3 pathologies."""
        symptomes = request.data.get('symptomes', [])
        if not symptomes:
            return Response(
                {'detail': 'Veuillez fournir au moins un symptôme.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        age = int(request.data.get('age', 30) or 30)
        gender = request.data.get('gender', 'M')
        blood_pressure = request.data.get('blood_pressure', 'Normal')
        cholesterol = request.data.get('cholesterol', 'Normal')
        genre = 'Male' if gender == 'M' else 'Female'

        suggestions = obtenir_suggestions_ia(
            symptomes, age=age, genre=genre,
            tension=blood_pressure, cholesterol=cholesterol
        )
        if not suggestions:
            return Response({
                'disponible': False,
                'message': 'Module IA temporairement indisponible.',
                'suggestions': []
            })
        return Response({
            'disponible': True,
            'suggestions': suggestions,
            'avertissement': "Outil d'aide — ne remplace pas le diagnostic médical."
        })

    # ─── PDF ──────────────────────────────────────────────────

    @action(detail=True, methods=['get'], url_path='compte-rendu-pdf')
    def compte_rendu_pdf(self, request, pk=None):
        """Génère et retourne le PDF du compte rendu."""
        consultation = self.get_object()

        # Vérification patient : seul le patient propriétaire peut télécharger
        if request.user.role == 'patient':
            if not hasattr(request.user, 'patient_profile') or \
               consultation.patient != request.user.patient_profile:
                return Response(
                    {'detail': 'Vous n\'avez pas accès à ce document.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        return generer_pdf_compte_rendu(consultation)

    # ─── Stats Dashboard BF-06 ────────────────────────────────

    @action(
        detail=False, methods=['get'],
        url_path='stats',
        permission_classes=[EstStaffOuAdministrateur]
    )
    def stats(self, request):
        """Stats générales pour le dashboard."""
        qs = self.get_queryset()
        maintenant = timezone.now()
        avec_ia = qs.filter(ia_utilisee=True).count()
        total = qs.count()
        return Response({
            'total': total,
            'ce_mois': qs.filter(
                date_consultation__month=maintenant.month,
                date_consultation__year=maintenant.year
            ).count(),
            'avec_ia': avec_ia,
            'taux_ia': round(avec_ia / total * 100, 1) if total > 0 else 0,
        })

    @action(
        detail=False, methods=['get'],
        url_path='stats/pathologies',
        permission_classes=[EstMedecin]
    )
    def stats_pathologies(self, request):
        """Répartition des pathologies diagnostiquées — BF-06."""
        pathologies = (
            self.get_queryset()
            .exclude(diagnostic__isnull=True)
            .exclude(diagnostic__exact='')
            .values('diagnostic')
            .annotate(total=Count('diagnostic'))
            .order_by('-total')[:10]
        )
        return Response(list(pathologies))

    @action(
        detail=False, methods=['get'],
        url_path='stats/periode',
        permission_classes=[EstMedecin]
    )
    def stats_periode(self, request):
        """Consultations par semaine ou par mois — BF-06."""
        periode = request.query_params.get('periode', 'mois')
        qs = self.get_queryset()
        if periode == 'semaine':
            data = (
                qs.annotate(periode=TruncWeek('date_consultation'))
                .values('periode')
                .annotate(total=Count('id'))
                .order_by('periode')
            )
        else:
            data = (
                qs.annotate(periode=TruncMonth('date_consultation'))
                .values('periode')
                .annotate(total=Count('id'))
                .order_by('periode')
            )
        return Response(list(data))

    @action(
        detail=False, methods=['get'],
        url_path='stats/ia',
        permission_classes=[EstMedecin]
    )
    def stats_ia(self, request):
        """Statistiques d'utilisation du module IA — BF-06."""
        qs = self.get_queryset()
        total = qs.count()
        avec_ia = qs.filter(ia_utilisee=True).count()
        return Response({
            'total_consultations': total,
            'avec_ia': avec_ia,
            'sans_ia': total - avec_ia,
            'taux_utilisation': round(avec_ia / total * 100, 1) if total > 0 else 0,
        })
