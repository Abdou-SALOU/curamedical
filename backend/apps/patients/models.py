from django.db import models

class Patient(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    # Lien vers l'utilisateur (si le patient dispose d'un accès)
    user = models.OneToOneField(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='patient_profile'
    )

    # Identité
    first_name = models.CharField(max_length=100, verbose_name='Prénom')
    last_name = models.CharField(max_length=100, verbose_name='Nom')
    date_of_birth = models.DateField(verbose_name='Date de naissance')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    national_id = models.CharField(max_length=20, unique=True, verbose_name='CIN')

    # Coordonnées
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    # Informations médicales
    blood_group = models.CharField(
        max_length=3, choices=BLOOD_GROUP_CHOICES,
        blank=True, verbose_name='Groupe sanguin'
    )
    allergies = models.TextField(blank=True, verbose_name='Allergies connues')
    medical_history = models.TextField(blank=True, verbose_name='Antécédents médicaux')

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Patient'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        b = self.date_of_birth
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))