from rest_framework import serializers
from .models import Appointment
from apps.patients.serializers import PatientListSerializer
from apps.users.serializers import UserSerializer

class AppointmentSerializer(serializers.ModelSerializer):
    patient_detail = PatientListSerializer(source='patient', read_only=True)
    doctor_detail = UserSerializer(source='doctor', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, data):
        """Vérifie les conflits horaires"""
        doctor = data.get('doctor')
        scheduled_at = data.get('scheduled_at')
        duration = data.get('duration', 30)

        if doctor and scheduled_at:
            from datetime import timedelta
            end_time = scheduled_at + timedelta(minutes=duration)

            conflicts = Appointment.objects.filter(
                doctor=doctor,
                status__in=['planned', 'confirmed', 'in_progress'],
                scheduled_at__lt=end_time,
            ).exclude(pk=self.instance.pk if self.instance else None)

            for appt in conflicts:
                from datetime import timedelta
                appt_end = appt.scheduled_at + timedelta(minutes=appt.duration)
                if appt_end > scheduled_at:
                    raise serializers.ValidationError(
                        f"Conflit horaire avec un rendez-vous existant à "
                        f"{appt.scheduled_at:%H:%M}"
                    )
        return data