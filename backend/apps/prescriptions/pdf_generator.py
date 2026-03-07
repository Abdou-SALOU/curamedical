from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io

def generate_prescription_pdf(prescription):
    """Génère un PDF professionnel pour une ordonnance"""
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
        f"Dr. {prescription.consultation.doctor.get_full_name()}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.5*cm))

    # Séparateur
    story.append(Table([['']], colWidths=[16*cm],
                        style=[('LINEBELOW', (0,0), (-1,-1), 1, colors.grey)]))
    story.append(Spacer(1, 0.5*cm))

    # Infos patient
    patient = prescription.consultation.patient
    story.append(Paragraph(f"<b>Patient :</b> {patient.full_name}", styles['Normal']))
    story.append(Paragraph(f"<b>Âge :</b> {patient.age} ans", styles['Normal']))
    story.append(Paragraph(
        f"<b>Date :</b> {prescription.created_at:%d/%m/%Y}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.8*cm))

    # Titre
    title_style = ParagraphStyle('title', fontSize=16,
                                  spaceAfter=12, fontName='Helvetica-Bold',
                                  alignment=1)
    story.append(Paragraph("ORDONNANCE", title_style))

    # Médicaments
    for i, item in enumerate(prescription.items.all(), 1):
        med_style = ParagraphStyle('med', fontSize=11,
                                    fontName='Helvetica-Bold', spaceAfter=2)
        story.append(Paragraph(f"{i}. {item.medication} — {item.dosage}", med_style))
        story.append(Paragraph(
            f"&nbsp;&nbsp;&nbsp;{item.frequency} pendant {item.duration}",
            styles['Normal']
        ))
        if item.instructions:
            story.append(Paragraph(
                f"&nbsp;&nbsp;&nbsp;<i>{item.instructions}</i>",
                styles['Normal']
            ))
        story.append(Spacer(1, 0.3*cm))

    # Notes générales
    if prescription.notes:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(f"<b>Notes :</b> {prescription.notes}", styles['Normal']))

    # Signature
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Signature du médecin", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer