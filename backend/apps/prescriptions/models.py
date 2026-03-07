from django.db import models
from apps.consultations.models import Consultation

class Prescription(models.Model):
    consultation = models.OneToOneField(
        Consultation, on_delete=models.CASCADE,
        related_name='prescription'
    )

    notes = models.TextField(blank=True, verbose_name='Instructions générales')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ordonnance'
        ordering = ['-created_at']

    def __str__(self):
        return f"Ordonnance — {self.consultation.patient} — {self.created_at:%d/%m/%Y}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE,
        related_name='items'
    )
    medication = models.CharField(max_length=200, verbose_name='Médicament')
    dosage = models.CharField(max_length=100, verbose_name='Dosage')
    frequency = models.CharField(max_length=100, verbose_name='Posologie')
    duration = models.CharField(max_length=100, verbose_name='Durée')
    instructions = models.TextField(blank=True, verbose_name='Instructions')

    class Meta:
        verbose_name = 'Ligne ordonnance'

    def __str__(self):
        return f"{self.medication} — {self.dosage}"