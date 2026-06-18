import logging
import threading

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Patient
from apps.common.utils import send_to_n8n_automation

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Patient)
def trigger_patient_registration_automation(sender, instance, created, **kwargs):
    """Déclenche une notification n8n lors de la création d'un nouveau patient."""
    if created and instance.email:
        details = (
            f"Bienvenue sur CuraMedical, {instance.first_name}. "
            "Votre compte patient a été créé avec succès."
        )

        data = {
            "event": "new_patient",
            "patient_name": instance.full_name,
            "patient_email": instance.email,
            "patient_tel": instance.telephone,
            "doctor_name": "Administration CuraMedical",
            "date": instance.created_at.strftime("%d/%m/%Y %H:%M"),
            "details": details,
        }

        # Envoi à n8n en arrière-plan (daemon=True pour ne pas bloquer l'arrêt du serveur)
        thread = threading.Thread(
            target=send_to_n8n_automation,
            args=(data,),
            daemon=True,
        )
        thread.start()
