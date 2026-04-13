import requests
from django.conf import settings
from django.http import HttpResponse
from rest_framework import generics, status, permissions, exceptions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.appointments.models import Appointment
from .models import Consultation
from .serializers import ConsultationSerializer
from .report_generator import generate_consultation_report_pdf
from apps.common.permissions import IsDoctor, IsDoctorOrSecretary


class ConsultationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConsultationSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsDoctor()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Consultation.objects.select_related(
            'appointment__patient',
            'appointment__doctor',
            'doctor',
        )

        # Si l'utilisateur est un patient, il ne voit que ses propres consultations
        if user.role == 'patient':
            if hasattr(user, 'patient_profile'):
                queryset = queryset.filter(appointment__patient=user.patient_profile)
            else:
                return Consultation.objects.none()

        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(appointment__patient_id=patient_id)
        return queryset

    def perform_create(self, serializer):
        appointment_id = self.request.data.get('appointment')
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            # Met à jour le statut du rendez-vous automatiquement
            appointment.status = 'completed'
            appointment.save()
            serializer.save(doctor=appointment.doctor)
        except Appointment.DoesNotExist:
            serializer.save(doctor=self.request.user)


class ConsultationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsDoctor()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.role == 'patient':
            if not hasattr(user, 'patient_profile') or obj.appointment.patient != user.patient_profile:
                raise exceptions.PermissionDenied("Accès interdit")
        return obj


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_consultation_report_pdf(request, pk):
    try:
        consultation = Consultation.objects.select_related(
            'appointment__patient',
            'doctor'
        ).get(pk=pk)
        
        # Sécurité : Un patient ne peut télécharger que son compte-rendu
        if request.user.role == 'patient':
            if not hasattr(request.user, 'patient_profile') or consultation.appointment.patient != request.user.patient_profile:
                return Response({'error': 'Accès interdit'}, status=403)
                
    except Consultation.DoesNotExist:
        return Response({'error': 'Consultation introuvable'}, status=404)

    pdf_buffer = generate_consultation_report_pdf(consultation)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="compte_rendu_{consultation.id}.pdf"'
    )
    return response
@api_view(['POST'])
@permission_classes([IsDoctor])
def get_ia_suggestions(request):
    symptoms = request.data.get('symptoms', [])
    if not symptoms:
        return Response({'error': 'Aucun symptome fourni'}, status=status.HTTP_400_BAD_REQUEST)

    payload = {
        'symptoms': symptoms,
        'age': request.data.get('age', 30),
        'gender': request.data.get('gender', 'M'),
        'blood_pressure': request.data.get('blood_pressure', 'Normal'),
        'cholesterol': request.data.get('cholesterol', 'Normal'),
    }

    try:
        response = requests.post(f"{settings.IA_SERVICE_URL}/predict", json=payload, timeout=8)
        response.raise_for_status()
        return Response(response.json())
    except requests.exceptions.RequestException:
        return Response(
            {'error': 'Service IA temporairement indisponible', 'degraded': True},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
