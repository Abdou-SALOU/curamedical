from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Consultation
from .report_generator import generate_consultation_report_pdf
from apps.common.utils import send_to_n8n_automation

@receiver(post_save, sender=Consultation)
def trigger_consultation_automation(sender, instance, created, **kwargs):
    if created:
        # Données de base
        data = {
            "event": "new_consultation_report",
            "patient_name": instance.appointment.patient.full_name,
            "patient_email": instance.appointment.patient.email,
            "doctor_name": instance.doctor.get_full_name(),
            "date": instance.created_at.strftime("%d/%m/%Y"),
            "details": f"Nouveau compte-rendu pour le diagnostic : {instance.diagnosis}"
        }
        
        import threading
        
        def run_automation():
            try:
                # Génération du PDF
                pdf_buffer = generate_consultation_report_pdf(instance)
                
                # Envoi à n8n
                send_to_n8n_automation(
                    data, 
                    binary_data=pdf_buffer.getvalue(), 
                    filename=f"compte_rendu_{instance.id}.pdf"
                )
            except Exception as e:
                print(f"Error in background automation: {e}")

        # Lancement en arrière-plan pour ne pas bloquer l'utilisateur
        thread = threading.Thread(target=run_automation)
        thread.start()
