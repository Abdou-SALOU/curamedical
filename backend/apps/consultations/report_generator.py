from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io

def generate_consultation_report_pdf(consultation):
    """Génère un compte-rendu médical professionnel"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                             topMargin=2*cm, bottomMargin=2*cm,
                             leftMargin=2.5*cm, rightMargin=2.5*cm)

    styles = getSampleStyleSheet()
    story = []

    # En-tête cabinet
    header_style = ParagraphStyle('header', fontSize=14,
                                   spaceAfter=6, fontName='Helvetica-Bold')
    story.append(Paragraph("Cabinet Médical — MedPredict", header_style))
    story.append(Paragraph(
        f"Compte-rendu de consultation — Dr. {consultation.doctor.get_full_name()}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.5*cm))

    # Séparateur
    story.append(Table([['']], colWidths=[16*cm],
                        style=[('LINEBELOW', (0,0), (-1,-1), 1, colors.grey)]))
    story.append(Spacer(1, 0.5*cm))

    # Infos patient
    patient = consultation.patient
    story.append(Paragraph(f"<b>Patient :</b> {patient.full_name}", styles['Normal']))
    story.append(Paragraph(f"<b>Âge :</b> {patient.age} ans", styles['Normal']))
    story.append(Paragraph(
        f"<b>Date de consultation :</b> {consultation.created_at:%d/%m/%Y}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.8*cm))

    # Titre du rapport
    title_style = ParagraphStyle('title', fontSize=16,
                                  spaceAfter=12, fontName='Helvetica-Bold',
                                  alignment=1)
    story.append(Paragraph("COMPTE-RENDU MÉDICAL", title_style))

    # Corps du rapport
    body_style = ParagraphStyle('body', fontSize=11, spaceAfter=8)
    
    # Symptômes
    if consultation.symptoms:
        story.append(Paragraph("<b>Symptômes rapportés :</b>", styles['Normal']))
        story.append(Paragraph(", ".join(consultation.symptoms), styles['Normal']))
        story.append(Spacer(1, 0.3*cm))

    # Examen clinique
    if consultation.clinical_exam:
        story.append(Paragraph("<b>Examen clinique :</b>", styles['Normal']))
        story.append(Paragraph(consultation.clinical_exam, styles['Normal']))
        story.append(Spacer(1, 0.3*cm))

    # Diagnostic
    story.append(Paragraph("<b>Diagnostic retenu :</b>", styles['Normal']))
    story.append(Paragraph(consultation.diagnosis, styles['Normal']))
    story.append(Spacer(1, 0.3*cm))

    # Suggestions IA
    if consultation.ia_used and consultation.ia_suggestions:
        story.append(Paragraph("<i>Note : Ce diagnostic a été assisté par l'IA MedPredict.</i>", 
                               ParagraphStyle('ia_note', fontSize=9, textColor=colors.grey)))

    # Notes additionnelles
    if consultation.notes:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("<b>Notes complémentaires :</b>", styles['Normal']))
        story.append(Paragraph(consultation.notes, styles['Normal']))

    # Signature
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Signature du médecin", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer
