import uuid
from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from apps.patients.models import Patient
from django.conf import settings


class RendezVous(models.Model):
    CHOIX_STATUT = (
        ('DEMANDE', 'En attente'),
        ('PLANIFIE', 'Planifié'),
        ('CONFIRME', 'Confirmé'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    )

    CHOIX_TYPE = (
        ('PRESENTIEL', 'Au cabinet'),
        ('EN_LIGNE', 'En ligne (Téléconsultation)'),
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='rendez_vous'
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rendez_vous',
        limit_choices_to={'role': 'medecin'}
    )
    date_heure = models.DateTimeField("Date et heure du rendez-vous")
    duree = models.IntegerField("Durée estimée (minutes)", default=30)
    motif = models.CharField("Motif de consultation", max_length=255)
    statut = models.CharField(
        "Statut",
        max_length=20,
        choices=CHOIX_STATUT,
        default='PLANIFIE'
    )
    type_consultation = models.CharField(
        "Type de consultation",
        max_length=20,
        choices=CHOIX_TYPE,
        default='PRESENTIEL'
    )
    lien_visio = models.CharField(
        "Lien Visioconférence (Salle Jitsi)",
        max_length=100,
        blank=True,
        null=True
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    est_supprime = models.BooleanField("Supprimé", default=False)
    supprime_le = models.DateTimeField("Date de suppression", null=True, blank=True)

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['date_heure']

    def __str__(self):
        return (
            f"RDV {self.patient} avec Dr. {self.medecin.last_name} "
            f"le {self.date_heure.strftime('%d/%m/%Y %H:%M')}"
        )

    def get_heure_fin(self):
        return self.date_heure + timedelta(minutes=self.duree)

    def save(self, *args, **kwargs):
        # Auto-générer un identifiant de salle unique si c'est une téléconsultation et qu'il n'y a pas de lien
        if self.type_consultation == 'EN_LIGNE' and not self.lien_visio:
            unique_id = uuid.uuid4().hex[:8]
            self.lien_visio = f"CuraMedical-RDV-{unique_id}"
        elif self.type_consultation == 'PRESENTIEL':
            self.lien_visio = None
            
        super().save(*args, **kwargs)

    def clean(self):
        """Validation des conflits horaires aussi côté modèle (admin Django)."""
        if not self.date_heure or not self.medecin_id:
            return
        fin = self.get_heure_fin()
        conflits = RendezVous.objects.filter(
            medecin=self.medecin,
            statut__in=['PLANIFIE', 'CONFIRME', 'EN_COURS'],
            date_heure__lt=fin,
            date_heure__gte=self.date_heure - timedelta(minutes=self.duree),
        ).exclude(pk=self.pk)
        if conflits.exists():
            rdv = conflits.first()
            raise ValidationError(
                f"Conflit horaire : Dr. {self.medecin.last_name} a déjà "
                f"un RDV à {rdv.date_heure.strftime('%H:%M')}."
            )

