from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Prescription
from .pdf_generator import generate_prescription_pdf
from apps.common.utils import send_to_n8n_automation

@receiver(post_save, sender=Prescription)
def trigger_prescription_automation(sender, instance, created, **kwargs):
    # Désactivé ici pour éviter l'envoi du PDF sans les médicaments.
    # L'envoi est désormais géré dans le PrescriptionSerializer.create()
    pass
