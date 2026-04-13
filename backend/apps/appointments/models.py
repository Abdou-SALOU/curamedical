from django.db import models
from apps.patients.models import Patient
from apps.users.models import User

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planifié'),
        ('confirmed', 'Confirmé'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE,
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='appointments',
        limit_choices_to={'role': 'doctor'}
    )
    scheduled_at = models.DateTimeField(verbose_name='Date et heure')
    duration = models.IntegerField(default=30, verbose_name='Durée (min)')
    reason = models.CharField(max_length=255, verbose_name='Motif')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='planned'
    )
    is_teleconsultation = models.BooleanField(
        default=False, verbose_name='Téléconsultation'
    )
    teleconsultation_link = models.URLField(
        blank=True, null=True, verbose_name='Lien Visio (Jitsi)'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rendez-vous'
        verbose_name_plural = 'Rendez-vous'
        ordering = ['scheduled_at']

    def __str__(self):
        return f"{self.patient} — {self.scheduled_at:%d/%m/%Y %H:%M}"