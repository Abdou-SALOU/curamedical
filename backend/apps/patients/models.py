from django.db import models
from django.conf import settings


class Patient(models.Model):
    GROUPE_SANGUIN_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    # Lien vers l'utilisateur (optionnel — un patient peut ne pas avoir de compte)
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patient_profile',  # ← résout le ⚠️ de appointments
        verbose_name="Compte utilisateur"
    )

    # Identité
    nom = models.CharField("Nom", max_length=100)
    prenom = models.CharField("Prénom", max_length=100)
    date_naissance = models.DateField("Date de naissance")
    sexe = models.CharField("Sexe", max_length=1, choices=SEXE_CHOICES)
    cin = models.CharField("CIN", max_length=20, unique=True, blank=True, null=True)

    # Coordonnées
    telephone = models.CharField("Téléphone", max_length=15)
    email = models.EmailField("Email", blank=True, null=True)
    adresse = models.TextField("Adresse", blank=True, null=True)
    ville = models.CharField("Ville", max_length=100, blank=True, null=True)

    # Informations médicales
    groupe_sanguin = models.CharField(
        "Groupe sanguin",
        max_length=3,
        choices=GROUPE_SANGUIN_CHOICES,
        blank=True,
        null=True
    )
    allergies = models.TextField("Allergies connues", blank=True, null=True)
    antecedents_medicaux = models.TextField("Antécédents médicaux", blank=True, null=True)
    medicaments_en_cours = models.TextField("Médicaments en cours", blank=True, null=True)

    # Métadonnées
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    est_archive = models.BooleanField("Archivé", default=False)

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom.upper()} {self.prenom}"

    @property
    def nom_complet(self):
        return f"{self.nom.upper()} {self.prenom}"

    @property
    def age(self):
        if not self.date_naissance:
            return "-"
        from datetime import date
        aujourd_hui = date.today()
        # On vérifie si l'anniversaire est déjà passé cette année
        anniversaire_passe = (
            (aujourd_hui.month, aujourd_hui.day)
            < (self.date_naissance.month, self.date_naissance.day)
        )
        return aujourd_hui.year - self.date_naissance.year - (1 if anniversaire_passe else 0)
from auditlog.registry import auditlog
auditlog.register(Patient)
