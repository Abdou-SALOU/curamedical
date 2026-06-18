"""Tâches Celery des consultations.

Ces tâches sont exécutées par le worker (ou en thread de repli) afin de ne
jamais bloquer la requête HTTP de création de consultation.
"""
import logging

from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from apps.common.utils import send_to_n8n_automation
from .models import Consultation
from .utils import generer_pdf_compte_rendu

logger = logging.getLogger(__name__)


def _format_consultation_value(value, fallback):
    if not value:
        return fallback
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if str(item).strip()) or fallback
    if isinstance(value, dict):
        return ", ".join(f"{key}: {val}" for key, val in value.items()) or fallback
    return str(value)


@shared_task(name='consultations.send_report')
def send_consultation_report_task(consultation_id):
    """Génère le PDF du compte-rendu et l'envoie via n8n + WhatsApp."""
    try:
        consultation = Consultation.objects.select_related('patient', 'medecin').get(pk=consultation_id)
        patient = consultation.patient
        if not patient.email and not patient.telephone:
            return

        symptomes = _format_consultation_value(consultation.symptomes, "Non renseignes")
        diagnostic = consultation.diagnostic or "Non renseigne"
        examen_clinique = consultation.examen_clinique or "Non renseigne"
        notes = consultation.notes or "Non renseigne"

        if isinstance(consultation.symptomes, (list, dict)):
            consultation.symptomes = symptomes
        pdf_response = generer_pdf_compte_rendu(consultation)
        pdf_path = default_storage.save(
            f"consultations/compte_rendu_{consultation.id}.pdf",
            ContentFile(pdf_response.content),
        )
        base_url = getattr(settings, 'PUBLIC_BASE_URL', '').rstrip('/')
        pdf_url = f"{base_url}{settings.MEDIA_URL}{pdf_path}" if base_url else ''
        date_str = consultation.date_consultation.strftime('%d/%m/%Y')
        conclusion = diagnostic
        details = (
            f"Conclusion retenue par le medecin : {conclusion}\n\n"
            f"Symptomes observes : {symptomes}\n\n"
            f"Examen clinique : {examen_clinique}\n\n"
            f"Notes du medecin : {notes}"
        )
        data = {
            'event': 'new_consultation_report',
            'patient_name': patient.nom_complet,
            'patient_email': patient.email,
            'patient_tel': patient.telephone,
            'doctor_name': consultation.medecin.get_full_name() or consultation.medecin.username,
            'date': date_str,
            'details': details,
            'symptomes': symptomes,
            'diagnostic': diagnostic,
            'examen_clinique': examen_clinique,
            'notes': notes,
            'conclusion': conclusion,
            'pdf_url': pdf_url,
        }
        send_to_n8n_automation(
            data,
            binary_data=pdf_response.content,
            filename=f"compte_rendu_consultation_{consultation.id}.pdf",
        )
        if patient.telephone and pdf_url:
            from apps.whatsapp.service import WhatsAppService
            caption = (
                f"Bonjour {patient.nom_complet}, voici votre compte-rendu de consultation "
                f"du {date_str}. Conclusion retenue : {conclusion}. Le PDF est joint. "
                "CuraMedical"
            )
            WhatsAppService().send_pdf(patient.telephone, pdf_url, caption)
    except Exception as exc:
        logger.error("[CONSULTATION] Erreur envoi rapport (n8n/WhatsApp) : %s", exc)
