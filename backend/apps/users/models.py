from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Modèle utilisateur personnalisé avec rôles"""

    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('doctor', 'Médecin'),
        ('secretary', 'Secrétaire'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='secretary'
    )
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_doctor(self):
        return self.role == 'doctor'

    @property
    def is_secretary(self):
        return self.role == 'secretary'

    @property
    def is_admin(self):
        return self.role == 'admin'