from django.db import models
from django.conf import settings
from apps.patients.models import Patient
from apps.appointments.models import RendezVous


class Consultation(models.Model):

    # Lien avec le rendez-vous
    rendez_vous = models.OneToOneField(
        RendezVous,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='consultation'
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='consultations'
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consultations',
        limit_choices_to={'role': 'medecin'}
    )

    # Contenu médical
    symptomes = models.JSONField("Symptômes observés", default=list, blank=True)
    examen_clinique = models.TextField("Résultats examen clinique", blank=True, null=True)
    diagnostic = models.TextField("Diagnostic retenu", blank=True, null=True)
    notes = models.TextField("Notes du médecin", blank=True, null=True)

    # Module IA — stocké en JSON
    suggestions_ia = models.JSONField(
        "Suggestions IA",
        blank=True,
        null=True,
        help_text="Top 3 pathologies suggérées par l'IA avec scores de confiance"
    )
    ia_utilisee = models.BooleanField("Module IA utilisé", default=False)

    # Métadonnées
    date_consultation = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    est_supprime = models.BooleanField("Supprimé", default=False)
    supprime_le = models.DateTimeField("Date de suppression", null=True, blank=True)

    class Meta:
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"
        ordering = ['-date_consultation']

    def __str__(self):
        return (
            f"Consultation {self.patient.nom_complet} "
            f"— Dr. {self.medecin.last_name} "
            f"le {self.date_consultation.strftime('%d/%m/%Y')}"
        )
from auditlog.registry import auditlog
auditlog.register(Consultation)
