from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('administrateur', 'Administrateur'),
        ('medecin', 'Médecin'),
        ('secretaire', 'Secrétaire'),
        ('patient', 'Patient'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='patient',
        verbose_name="Rôle"
    )
    telephone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Téléphone"
    )

    SPECIALITE_CHOICES = [
        ('generaliste', 'Médecin Généraliste'),
        ('cardiologue', 'Cardiologue'),
        ('dermatologue', 'Dermatologue'),
        ('gynecologue', 'Gynécologue'),
        ('pediatre', 'Pédiatre'),
        ('ophtalmologue', 'Ophtalmologue'),
        ('dentiste', 'Dentiste'),
        ('radiologue', 'Radiologue'),
        ('chirurgien', 'Chirurgien'),
        ('neurologue', 'Neurologue'),
        ('pneumologue', 'Pneumologue'),
        ('rhumatologue', 'Rhumatologue'),
        ('endocrinologue', 'Endocrinologue'),
        ('gastro', 'Gastro-entérologue'),
        ('psy', 'Psychiatre / Psychologue'),
        ('urgentiste', 'Médecin Urgentiste'),
        ('autre', 'Autre spécialité'),
    ]

    specialite = models.CharField(
        max_length=30,
        choices=SPECIALITE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Spécialité"
    )

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def est_medecin(self):
        return self.role == 'medecin'

    @property
    def est_secretaire(self):
        return self.role == 'secretaire'

    @property
    def est_administrateur(self):
        return self.role == 'administrateur' or self.is_superuser

    @property
    def est_patient(self):
        return self.role == 'patient'
