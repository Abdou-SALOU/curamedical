from django.http import HttpResponse
from .pdf_generator import generate_prescription_pdf


def generer_pdf_ordonnance(prescription):
    """Génère et retourne le PDF de l'ordonnance (même rendu que le PDF WhatsApp)."""
    buffer = generate_prescription_pdf(prescription)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="ordonnance_{prescription.id}'
        f'_{prescription.patient.nom}_{prescription.patient.prenom}.pdf"'
    )
    return response
