import logging
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from rest_framework import viewsets, filters, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Prescription
from .serializers import (
    PrescriptionSerializer,
    PrescriptionListSerializer
)
from .utils import generer_pdf_ordonnance
from apps.users.permissions import (
    EstMedecin,
    EstStaffOuAdministrateur,
    EstAdministrateur,
    EstPatient,
)

logger = logging.getLogger(__name__)


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['medecin', 'patient']
    search_fields = ['patient__nom', 'patient__prenom', 'lignes__medicament']
    ordering_fields = ['cree_le']
    ordering = ['-cree_le']

    def get_serializer_class(self):
        if self.action == 'list':
            return PrescriptionListSerializer
        return PrescriptionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [EstMedecin()]
        if self.action in ['destroy', 'restaurer', 'supprimer_definitif']:
            return [EstStaffOuAdministrateur()]
        if self.action == 'corbeille':
            return [permissions.IsAuthenticated()]
        if self.action == 'ordonnance_pdf':
            if not self.request.user.is_authenticated:
                return [permissions.IsAuthenticated()]
            return [EstMedecin() if getattr(self.request.user, 'role', '') == 'medecin' else EstPatient()]
        if self.action == 'envoyer_whatsapp':
            return [permissions.IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [EstStaffOuAdministrateur()]

    def get_queryset(self):
        user = self.request.user
        qs = Prescription.objects.select_related(
            'patient', 'medecin'
        ).prefetch_related('lignes').filter(est_supprime=False)

        if user.role == 'medecin':
            return qs.filter(medecin=user)
        if user.role == 'patient':
            return qs.filter(patient__utilisateur=user)
        if user.role == 'secretaire':
            return qs.all()
        # Administrateur : aucun accès aux données médicales
        return Prescription.objects.none()

    def destroy(self, request, *args, **kwargs):
        from django.utils import timezone
        instance = self.get_object()
        instance.est_supprime = True
        instance.supprime_le = timezone.now()
        instance.save(update_fields=['est_supprime', 'supprime_le'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='corbeille')
    def corbeille(self, request):
        user = request.user
        qs = Prescription.objects.select_related('patient', 'medecin').prefetch_related('lignes').filter(est_supprime=True)
        if user.role == 'medecin':
            qs = qs.filter(medecin=user)
        elif user.role == 'patient':
            qs = qs.filter(patient__utilisateur=user)
        serializer = PrescriptionListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='restaurer')
    def restaurer(self, request, pk=None):
        instance = Prescription.objects.filter(pk=pk, est_supprime=True).first()
        if not instance:
            return Response({'detail': 'Introuvable dans la corbeille.'}, status=status.HTTP_404_NOT_FOUND)
        instance.est_supprime = False
        instance.supprime_le = None
        instance.save(update_fields=['est_supprime', 'supprime_le'])
        return Response({'detail': 'Ordonnance restaurée.'})

    @action(detail=True, methods=['delete'], url_path='supprimer-definitif')
    def supprimer_definitif(self, request, pk=None):
        instance = Prescription.objects.filter(pk=pk, est_supprime=True).first()
        if not instance:
            return Response({'detail': 'Introuvable dans la corbeille.'}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        consultation = serializer.validated_data.get('consultation')
        patient = consultation.patient if consultation else None
        if not patient:
            raise ValidationError({'patient': 'Patient introuvable depuis la consultation.'})
        serializer.save(medecin=self.request.user, patient=patient)

    @action(
        detail=True,
        methods=['get'],
        url_path='ordonnance-pdf'
    )
    def ordonnance_pdf(self, request, pk=None):
        """Génère et retourne le PDF de l'ordonnance."""
        prescription = self.get_object()

        # Vérification patient : seul le patient propriétaire peut télécharger
        if request.user.role == 'patient':
            if not hasattr(request.user, 'patient_profile') or \
               prescription.patient != request.user.patient_profile:
                from rest_framework.response import Response
                return Response(
                    {'detail': 'Vous n\'avez pas accès à ce document.'},
                    status=403
                )

        return generer_pdf_ordonnance(prescription)

    @action(
        detail=True,
        methods=['post'],
        url_path='envoyer-whatsapp',
    )
    def envoyer_whatsapp(self, request, pk=None):
        """Génère le PDF de l'ordonnance et l'envoie au patient via WhatsApp."""
        from apps.prescriptions.pdf_generator import generate_prescription_pdf
        from apps.whatsapp.service import WhatsAppService

        prescription = self.get_object()

        # Seul le médecin propriétaire ou le staff peut déclencher l'envoi
        user = request.user
        if user.role == 'medecin' and prescription.medecin != user:
            return Response({'detail': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)
        if user.role == 'patient':
            return Response({'detail': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)

        patient = prescription.patient
        phone = getattr(patient, 'telephone', None)
        if not phone:
            return Response(
                {'detail': 'Le patient n\'a pas de numéro de téléphone enregistré.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Générer le PDF et le sauvegarder dans media/
        try:
            pdf_buffer = generate_prescription_pdf(prescription)
        except Exception as e:
            logger.error('Erreur génération PDF ordonnance %s : %s', pk, e)
            return Response({'detail': 'Erreur lors de la génération du PDF.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        filename = f"prescriptions/ordonnance_{prescription.id}.pdf"
        saved_path = default_storage.save(filename, ContentFile(pdf_buffer.read()))

        # Construire l'URL publique
        base_url = (
            settings.PUBLIC_BASE_URL.rstrip('/')
            if getattr(settings, 'PUBLIC_BASE_URL', '')
            else request.build_absolute_uri('/').rstrip('/')
        )
        public_url = f"{base_url}{settings.MEDIA_URL}{saved_path}"

        # Envoyer via Twilio WhatsApp
        caption = (
            f"Bonjour {patient.prenom}, voici votre ordonnance du "
            f"{prescription.cree_le.strftime('%d/%m/%Y')} "
            f"— Dr. {prescription.medecin.get_full_name()}.\n"
            f"Clinique CuraMedical."
        )
        try:
            svc = WhatsAppService()
            msg = svc.send_pdf(phone, public_url, caption)
        except Exception as e:
            logger.error('Erreur envoi WhatsApp ordonnance %s : %s', pk, e)
            return Response(
                {'detail': f'Erreur Twilio : {e}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({
            'detail': 'Ordonnance envoyée via WhatsApp.',
            'message_sid': msg.sid,
            'to': phone,
            'pdf_url': public_url,
        })
