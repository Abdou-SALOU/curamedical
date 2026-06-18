from django.http import HttpResponse
from .report_generator import generate_consultation_report_pdf


def generer_pdf_compte_rendu(consultation):
    """Génère et retourne le PDF du compte rendu (même rendu que le PDF WhatsApp/email)."""
    buffer = generate_consultation_report_pdf(consultation)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="compte_rendu_{consultation.id}'
        f'_{consultation.patient.nom}_{consultation.patient.prenom}.pdf"'
    )
    return response
