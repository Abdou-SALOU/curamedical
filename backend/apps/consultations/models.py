from django.db import models
from apps.appointments.models import Appointment
from apps.users.models import User

class Consultation(models.Model):
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE,
        related_name='consultation'
    )
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='consultations'
    )

    # Données cliniques
    symptoms = models.JSONField(default=list, verbose_name='Symptômes')
    clinical_exam = models.TextField(blank=True, verbose_name='Examen clinique')
    diagnosis = models.CharField(max_length=255, verbose_name='Diagnostic retenu')
    notes = models.TextField(blank=True, verbose_name='Notes')

    # Suggestions IA (stockées à titre informatif)
    ia_suggestions = models.JSONField(
        null=True, blank=True,
        verbose_name='Suggestions IA'
    )
    ia_used = models.BooleanField(default=False, verbose_name='IA consultée')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Consultation'
        ordering = ['-created_at']

    def __str__(self):
        return f"Consultation {self.appointment.patient} — {self.created_at:%d/%m/%Y}"

    @property
    def patient(self):
        return self.appointment.patient