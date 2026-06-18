from django.db import models
from django.conf import settings
from apps.patients.models import Patient
from apps.consultations.models import Consultation


class Prescription(models.Model):
    """Ordonnance liée à une consultation."""

    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name='prescription'
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        limit_choices_to={'role': 'medecin'}
    )

    notes_generales = models.TextField(
        "Notes générales",
        blank=True, null=True
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    est_supprime = models.BooleanField("Supprimé", default=False)
    supprime_le = models.DateTimeField("Date de suppression", null=True, blank=True)

    class Meta:
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"
        ordering = ['-cree_le']

    def __str__(self):
        return (
            f"Ordonnance {self.patient.nom_complet} "
            f"— Dr. {self.medecin.last_name} "
            f"le {self.cree_le.strftime('%d/%m/%Y')}"
        )


class LignePrescription(models.Model):
    """Un médicament dans une ordonnance."""

    UNITE_CHOICES = [
        ('comprime', 'Comprimé'),
        ('gelule', 'Gélule'),
        ('sachet', 'Sachet'),
        ('ampoule', 'Ampoule'),
        ('sirop', 'Sirop (ml)'),
        ('gouttes', 'Gouttes'),
        ('creme', 'Crème'),
        ('autre', 'Autre'),
    ]

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    medicament = models.CharField("Médicament", max_length=200)
    dosage = models.CharField("Dosage", max_length=100)         # ex: 500mg
    unite = models.CharField(
        "Unité",
        max_length=20,
        choices=UNITE_CHOICES,
        default='comprime'
    )
    frequence = models.CharField("Fréquence", max_length=100)  # ex: 2x/jour
    duree = models.CharField("Durée", max_length=100)          # ex: 7 jours
    instructions = models.TextField(
        "Instructions particulières",
        blank=True, null=True
    )

    class Meta:
        verbose_name = "Ligne de prescription"
        verbose_name_plural = "Lignes de prescription"

    def __str__(self):
        return f"{self.medicament} {self.dosage} — {self.frequence} pendant {self.duree}"
from auditlog.registry import auditlog
auditlog.register(Prescription)
