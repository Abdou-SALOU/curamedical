from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import requests
from django.conf import settings
from .models import Consultation
from .serializers import ConsultationSerializer
from apps.appointments.models import Appointment
from apps.users.permissions import IsDoctorOrAdmin


class ConsultationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConsultationSerializer
    permission_classes = [IsDoctorOrAdmin]  # ← Secrétaire bloquée

    def get_queryset(self):
        queryset = Consultation.objects.select_related(
            'appointment__patient',
            'appointment__doctor',
            'doctor'
        )
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(appointment__patient_id=patient_id)
        return queryset

    def perform_create(self, serializer):
        appointment_id = self.request.data.get('appointment')
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            serializer.save(doctor=appointment.doctor)
        except Appointment.DoesNotExist:
            serializer.save(doctor=self.request.user)


class ConsultationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [IsDoctorOrAdmin]  # ← Secrétaire bloquée


@api_view(['POST'])
@permission_classes([IsDoctorOrAdmin])  # ← Secrétaire bloquée
def get_ia_suggestions(request):
    symptoms = request.data.get('symptoms', [])
    if not symptoms:
        return Response(
            {'error': 'Aucun symptôme fourni'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        response = requests.post(
            f"{settings.IA_SERVICE_URL}/predict",
            json={'symptoms': symptoms},
            timeout=5
        )
        return Response(response.json())
    except requests.exceptions.RequestException:
        return Response(
            {'error': 'Service IA temporairement indisponible', 'degraded': True},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )