from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Appointment
from apps.common.utils import send_to_n8n_automation
import uuid

@receiver(pre_save, sender=Appointment)
def auto_generate_jitsi_link(sender, instance, **kwargs):
    if instance.is_teleconsultation and not instance.teleconsultation_link:
        unique_id = uuid.uuid4().hex[:12]
        instance.teleconsultation_link = f"https://meet.jit.si/medpredict_{unique_id}"

@receiver(post_save, sender=Appointment)
def trigger_appointment_reminder_automation(sender, instance, created, **kwargs):
    if created:
        # Envoie un premier signal d'enregistrement de rendez-vous
        details = f"Votre rendez-vous est prévu pour le {instance.scheduled_at.strftime('%d/%m/%Y %H:%M')}."
        if instance.is_teleconsultation and instance.teleconsultation_link:
            details += f" Il s'agit d'une téléconsultation. Lien pour vous connecter : {instance.teleconsultation_link}"

        data = {
            "event": "appointment_confirmed",
            "patient_name": instance.patient.full_name,
            "patient_email": instance.patient.email,
            "doctor_name": instance.doctor.get_full_name(),
            "date": instance.scheduled_at.strftime("%d/%m/%Y %H:%M"),
            "details": details,
            "is_teleconsultation": instance.is_teleconsultation,
            "teleconsultation_link": instance.teleconsultation_link
        }
        
        
        # Envoi à n8n en arrière-plan
        import threading
        thread = threading.Thread(target=send_to_n8n_automation, args=(data,))
        thread.start()
        
        # NOTE : Les rappels à J-1 devraient idéalement être gérés par une tâche planifiée (Celery)
        # ou par n8n lui-même via un délai d'attente (Wait node) basé sur l'heure du rendez-vous.
