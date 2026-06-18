from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.utils import timezone
from .models import RendezVous
from .serializers import (
    RendezVousSerializer,
    RendezVousListSerializer,
    SerializerMiseAJourStatut
)
from .filters import RendezVousFilter
from apps.users.permissions import (
    EstMedecinOuSecretaire,
)


class RendezVousViewSet(viewsets.ModelViewSet):
    queryset = RendezVous.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RendezVousFilter
    search_fields = ['patient__nom', 'patient__prenom', 'motif']
    ordering_fields = ['date_heure', 'cree_le']
    ordering = ['date_heure']

    def get_serializer_class(self):
        if self.action == 'list':
            return RendezVousListSerializer
        return RendezVousSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve', 'update_statut', 'corbeille']:
            return [permissions.IsAuthenticated()]
        return [EstMedecinOuSecretaire()]

    def get_queryset(self):
        user = self.request.user
        qs = RendezVous.objects.select_related('patient', 'medecin').filter(est_supprime=False)
        if user.role == 'medecin':
            return qs.filter(medecin=user)
        if user.role == 'secretaire':
            return qs.all()
        if user.role == 'patient':
            return qs.filter(patient__utilisateur=user)
        # Administrateur : aucun accès aux données médicales
        return RendezVous.objects.none()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.est_supprime = True
        instance.supprime_le = timezone.now()
        instance.save(update_fields=['est_supprime', 'supprime_le'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='corbeille')
    def corbeille(self, request):
        user = request.user
        qs = RendezVous.objects.select_related('patient', 'medecin').filter(est_supprime=True)
        if user.role == 'medecin':
            qs = qs.filter(medecin=user)
        elif user.role == 'patient':
            qs = qs.filter(patient__utilisateur=user)
        serializer = RendezVousListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='restaurer')
    def restaurer(self, request, pk=None):
        instance = RendezVous.objects.filter(pk=pk, est_supprime=True).first()
        if not instance:
            return Response({'detail': 'Introuvable dans la corbeille.'}, status=status.HTTP_404_NOT_FOUND)
        instance.est_supprime = False
        instance.supprime_le = None
        instance.save(update_fields=['est_supprime', 'supprime_le'])
        return Response({'detail': 'Rendez-vous restauré.'})

    @action(detail=True, methods=['delete'], url_path='supprimer-definitif')
    def supprimer_definitif(self, request, pk=None):
        instance = RendezVous.objects.filter(pk=pk, est_supprime=True).first()
        if not instance:
            return Response({'detail': 'Introuvable dans la corbeille.'}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'patient':
            try:
                patient = user.patient_profile
                serializer.save(patient=patient)
            except Exception:
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Votre compte n'est pas lié à un dossier patient. Contactez le secrétariat.")
        else:
            serializer.save()

    @action(
        detail=True,
        methods=['patch'],
        url_path='update-statut',
        permission_classes=[permissions.IsAuthenticated]
    )
    def update_statut(self, request, pk=None):
        """Changer le statut d'un RDV. Les patients ne peuvent qu'annuler une DEMANDE."""
        rendez_vous = self.get_object()

        if request.user.role == 'patient':
            if not hasattr(request.user, 'patient_profile') or rendez_vous.patient != request.user.patient_profile:
                return Response({'detail': "Non autorisé."}, status=status.HTTP_403_FORBIDDEN)
            if request.data.get('statut') != 'ANNULE':
                return Response({'detail': "Vous ne pouvez qu'annuler un rendez-vous."}, status=status.HTTP_403_FORBIDDEN)
            if rendez_vous.statut != 'DEMANDE':
                return Response({'detail': "Vous ne pouvez annuler qu'une demande en attente. Contactez le secrétariat."}, status=status.HTTP_400_BAD_REQUEST)
        elif request.user.role not in ['secretaire', 'medecin']:
            return Response({'detail': "Non autorisé."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SerializerMiseAJourStatut(data=request.data)
        if serializer.is_valid():
            rendez_vous.statut = serializer.validated_data['statut']
            rendez_vous.save()
            return Response({'statut': 'mis à jour'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=['get'],
        url_path='stats',
        permission_classes=[EstMedecinOuSecretaire]
    )
    def stats(self, request):
        """Stats générales pour le dashboard."""
        aujourd_hui = timezone.now().date()
        qs = self.get_queryset()
        return Response({
            'total_aujourd_hui': qs.filter(date_heure__date=aujourd_hui).count(),
            'planifies': qs.filter(statut='PLANIFIE').count(),
            'confirmes': qs.filter(statut='CONFIRME').count(),
            'annules': qs.filter(statut='ANNULE').count(),
            'termines': qs.filter(statut='TERMINE').count(),
        })

    @action(
        detail=False, methods=['get'],
        url_path='stats/taux',
        permission_classes=[EstMedecinOuSecretaire]
    )
    def stats_taux(self, request):
        """Taux RDV honorés vs annulés."""
        qs = self.get_queryset()
        total = qs.count()
        if total == 0:
            return Response({'total': 0, 'taux_honore': 0, 'taux_annule': 0})
        termines = qs.filter(statut='TERMINE').count()
        annules = qs.filter(statut='ANNULE').count()
        return Response({
            'total': total,
            'termines': termines,
            'annules': annules,
            'planifies': qs.filter(statut='PLANIFIE').count(),
            'confirmes': qs.filter(statut='CONFIRME').count(),
            'taux_honore': round(termines / total * 100, 1),
            'taux_annule': round(annules / total * 100, 1),
        })
