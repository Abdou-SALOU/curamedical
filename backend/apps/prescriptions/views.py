from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Prescription
from .serializers import PrescriptionSerializer
from .pdf_generator import generate_prescription_pdf
from apps.users.permissions import IsDoctorOrAdmin


class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Prescription.objects.select_related(
            'consultation__appointment__patient',
            'consultation__doctor'
        )

        # Si l'utilisateur est un patient, il ne voit que ses propres ordonnances
        if user.role == 'patient':
            if hasattr(user, 'patient_profile'):
                queryset = queryset.filter(consultation__appointment__patient=user.patient_profile)
            else:
                return Prescription.objects.none()

        return queryset


class PrescriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsDoctorOrAdmin]  # ← Secrétaire bloquée


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_prescription_pdf(request, pk):
    try:
        prescription = Prescription.objects.select_related(
            'consultation__appointment__patient',
            'consultation__doctor'
        ).get(pk=pk)
        
        # Sécurité : Un patient ne peut télécharger que son ordonnance
        if request.user.role == 'patient':
            if not hasattr(request.user, 'patient_profile') or prescription.consultation.appointment.patient != request.user.patient_profile:
                return Response({'error': 'Accès interdit'}, status=403)
                
    except Prescription.DoesNotExist:
        return Response({'error': 'Ordonnance introuvable'}, status=404)

    pdf_buffer = generate_prescription_pdf(prescription)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="ordonnance_{prescription.id}.pdf"'
    )
    return response