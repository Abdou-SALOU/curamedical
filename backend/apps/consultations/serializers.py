from rest_framework import serializers
from .models import Consultation
from apps.appointments.serializers import AppointmentSerializer

class ConsultationSerializer(serializers.ModelSerializer):
    appointment_detail = AppointmentSerializer(
        source='appointment', read_only=True
    )
    patient_name = serializers.CharField(
        source='patient.full_name', read_only=True
    )

    class Meta:
        model = Consultation
        fields = '__all__'