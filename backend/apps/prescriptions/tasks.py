"""Tâches Celery des ordonnances (email + n8n + WhatsApp)."""
import logging

from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from apps.common.utils import send_to_n8n_automation
from .models import Prescription
from .pdf_generator import generate_prescription_pdf

logger = logging.getLogger(__name__)


@shared_task(name='prescriptions.send_notification')
def send_prescription_notification_task(prescription_id):
    """Génère le PDF de l'ordonnance et notifie le patient (email, n8n, WhatsApp)."""
    try:
        prescription = Prescription.objects.select_related('patient', 'medecin').prefetch_related('lignes').get(pk=prescription_id)
    except Prescription.DoesNotExist:
        logger.warning("[Prescription] Ordonnance %s introuvable — notification ignorée.", prescription_id)
        return

    patient = prescription.patient
    salutation = "Monsieur" if patient.sexe == 'M' else "Madame"
    date_str = prescription.cree_le.strftime("%d/%m/%Y")
    medicaments = ", ".join(
        f"{l.medicament} {l.dosage}" for l in prescription.lignes.all()
    )

    # Générer le PDF une seule fois
    try:
        pdf_buffer = generate_prescription_pdf(prescription)
        pdf_bytes = pdf_buffer.getvalue()
    except Exception as e:
        logger.error("[Prescription] PDF échoué: %s", e)
        pdf_bytes = None

    # ── Email direct Django ──────────────────────────────────────
    if getattr(patient, 'email', None) and pdf_bytes:
        try:
            from django.core.mail import EmailMessage
            subject = f"CuraMedical — Votre ordonnance du {date_str}"
            body = (
                f"Bonjour {salutation} {patient.nom_complet},\n\n"
                f"Veuillez trouver ci-joint votre ordonnance établie le {date_str} "
                f"par Dr. {prescription.medecin.get_full_name()}.\n\n"
                f"Médicaments prescrits : {medicaments}\n\n"
                "Cordialement,\nL'équipe CuraMedical"
            )
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[patient.email],
            )
            email.attach(
                f"ordonnance_{prescription.id}.pdf",
                pdf_bytes,
                'application/pdf',
            )
            email.send(fail_silently=False)
            logger.info("[Prescription] Email envoyé à %s", patient.email)
        except Exception as e:
            logger.error("[Prescription] Email échoué (%s): %s", patient.email, e)

    # ── WhatsApp + n8n ───────────────────────────────────────────
    try:
        pdf_path = default_storage.save(
            f"prescriptions/ordonnance_{prescription.id}.pdf",
            ContentFile(pdf_bytes or b''),
        )
        base_url = getattr(settings, 'PUBLIC_BASE_URL', '').rstrip('/')
        pdf_url = f"{base_url}{settings.MEDIA_URL}{pdf_path}" if base_url else ""
        data = {
            "event": "new_prescription",
            "patient_name": patient.nom_complet,
            "patient_email": patient.email,
            "patient_tel": patient.telephone,
            "doctor_name": prescription.medecin.get_full_name(),
            "date": date_str,
            "pdf_url": pdf_url,
            "details": (
                f"Bonjour {salutation} {patient.nom}, votre ordonnance du {date_str} "
                f"contient : {medicaments}."
            ),
        }
        if pdf_bytes:
            send_to_n8n_automation(
                data,
                binary_data=pdf_bytes,
                filename=f"ordonnance_{prescription.id}.pdf",
            )
        if patient.telephone and pdf_url:
            from apps.whatsapp.service import WhatsAppService
            caption = (
                f"Bonjour {patient.nom_complet}, voici votre ordonnance du {date_str}. "
                f"Médicaments : {medicaments}. — CuraMedical"
            )
            WhatsAppService().send_pdf(patient.telephone, pdf_url, caption)
    except Exception as e:
        logger.error("[Prescription] Erreur envoi n8n/WhatsApp : %s", e)
