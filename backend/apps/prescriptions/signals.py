from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Prescription
from .pdf_generator import generate_prescription_pdf
from apps.common.utils import send_to_n8n_automation

@receiver(post_save, sender=Prescription)
def trigger_prescription_automation(sender, instance, created, **kwargs):
    if created:
        # Données de base
        data = {
            "event": "new_prescription",
            "patient_name": instance.consultation.appointment.patient.full_name,
            "patient_email": instance.consultation.appointment.patient.email,
            "doctor_name": instance.consultation.doctor.get_full_name(),
            "date": instance.created_at.strftime("%d/%m/%Y"),
            "details": f"Nouvelle ordonnance générée le {instance.created_at.strftime('%d/%m/%Y')}"
        }
        
        # Génération du PDF
        pdf_buffer = generate_prescription_pdf(instance)
        
        # Envoi à n8n
        send_to_n8n_automation(
            data, 
            binary_data=pdf_buffer.getvalue(), 
            filename=f"ordonnance_{instance.id}.pdf"
        )
