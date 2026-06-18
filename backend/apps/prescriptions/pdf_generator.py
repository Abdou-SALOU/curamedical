from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image, HRFlowable
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
import io
import os
from django.conf import settings

GREEN       = HexColor('#10b981')
GREEN_DARK  = HexColor('#059669')
GREEN_LIGHT = HexColor('#d1fae5')
DARK        = HexColor('#0f172a')
GREY        = HexColor('#64748b')
WHITE       = colors.white
PAGE_W      = A4[0] - 5*cm


def _st():
    return {
        'doc_name':  ParagraphStyle('DN',  fontSize=13, fontName='Helvetica-Bold', textColor=GREEN_DARK, spaceAfter=2),
        'doc_info':  ParagraphStyle('DI',  fontSize=9,  fontName='Helvetica', textColor=GREY),
        'cli_name':  ParagraphStyle('CN',  fontSize=11, fontName='Helvetica-Bold', textColor=GREEN_DARK, alignment=2, spaceAfter=2),
        'cli_info':  ParagraphStyle('CI',  fontSize=9,  fontName='Helvetica', textColor=GREY, alignment=2),
        'title':     ParagraphStyle('T',   fontSize=17, fontName='Helvetica-Bold', textColor=WHITE, alignment=1),
        'section':   ParagraphStyle('S',   fontSize=11, fontName='Helvetica-Bold', textColor=GREEN_DARK, spaceBefore=8, spaceAfter=3),
        'body':      ParagraphStyle('B',   fontSize=10, fontName='Helvetica', textColor=DARK, spaceAfter=3, leading=14),
        'th':        ParagraphStyle('TH',  fontSize=9,  fontName='Helvetica-Bold', textColor=WHITE),
        'sig_lbl':   ParagraphStyle('SL',  fontSize=9,  fontName='Helvetica', textColor=GREY, alignment=2),
        'sig_name':  ParagraphStyle('SN',  fontSize=10, fontName='Helvetica-Bold', textColor=GREEN_DARK, alignment=2),
        'pat_key':   ParagraphStyle('PK',  fontSize=9,  fontName='Helvetica-Bold', textColor=GREEN_DARK),
        'pat_val':   ParagraphStyle('PV',  fontSize=9,  fontName='Helvetica', textColor=DARK),
        'footer':    ParagraphStyle('F',   fontSize=8,  fontName='Helvetica-Oblique', textColor=GREY, alignment=1),
    }


def generate_prescription_pdf(prescription):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            topMargin=1.5*cm, bottomMargin=2*cm,
                            leftMargin=2.5*cm, rightMargin=2.5*cm)
    st = _st()
    story = []

    medecin = prescription.medecin
    patient = prescription.patient
    specialite = getattr(medecin, 'specialite', '') or 'Médecin'
    tel_med    = getattr(medecin, 'telephone', '') or 'N/A'

    # ── En-tête ────────────────────────────────────────────────────────
    left = [
        Paragraph(f"DR. {medecin.get_full_name().upper()}", st['doc_name']),
        Paragraph(f"Spécialité : {specialite}", st['doc_info']),
        Paragraph(f"Tél : {tel_med}", st['doc_info']),
    ]
    right = [
        Paragraph("Clinique CuraMedical", st['cli_name']),
        Paragraph("Quartier des Hôpitaux", st['cli_info']),
        Paragraph("20360 Casablanca, Maroc", st['cli_info']),
        Paragraph("Tél : +212 5 22 00 00 00", st['cli_info']),
    ]
    story.append(Table([[left, right]], colWidths=[PAGE_W*0.55, PAGE_W*0.45],
                       style=[('VALIGN',(0,0),(-1,-1),'TOP'),
                              ('LEFTPADDING',(0,0),(-1,-1),0),
                              ('RIGHTPADDING',(0,0),(-1,-1),0)]))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width='100%', thickness=2, color=GREEN, spaceAfter=6))

    # ── Titre ──────────────────────────────────────────────────────────
    story.append(Table([[Paragraph("ORDONNANCE MÉDICALE", st['title'])]],
                       colWidths=[PAGE_W],
                       style=[('BACKGROUND',(0,0),(-1,-1),GREEN),
                              ('TOPPADDING',(0,0),(-1,-1),8),
                              ('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(Spacer(1, 0.5*cm))

    # ── Patient ────────────────────────────────────────────────────────
    sexe = 'Masculin' if patient.sexe == 'M' else 'Féminin'
    pdata = [
        [Paragraph("Patient(e) :", st['pat_key']), Paragraph(patient.nom_complet, st['pat_val']),
         Paragraph("Âge :", st['pat_key']),  Paragraph(f"{patient.age} ans", st['pat_val'])],
        [Paragraph("Sexe :", st['pat_key']),  Paragraph(sexe, st['pat_val']),
         Paragraph("Date :", st['pat_key']),  Paragraph(prescription.cree_le.strftime('%d/%m/%Y'), st['pat_val'])],
    ]
    story.append(Table(pdata, colWidths=[2.5*cm, 5.5*cm, 2*cm, 5.5*cm],
                       style=[('BACKGROUND',(0,0),(-1,-1),GREEN_LIGHT),
                              ('BOX',(0,0),(-1,-1),1,GREEN),
                              ('TOPPADDING',(0,0),(-1,-1),6),
                              ('BOTTOMPADDING',(0,0),(-1,-1),6),
                              ('LEFTPADDING',(0,0),(-1,-1),8),
                              ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(Spacer(1, 0.6*cm))

    # ── Médicaments ────────────────────────────────────────────────────
    story.append(Paragraph("Prescriptions :", st['section']))
    story.append(HRFlowable(width='100%', thickness=1, color=GREEN_LIGHT, spaceAfter=4))

    rows = [[Paragraph("Médicament &amp; Dosage", st['th']),
             Paragraph("Posologie / Fréquence", st['th']),
             Paragraph("Durée", st['th'])]]

    for ligne in prescription.lignes.all():
        note = f" <i>Note: {ligne.instructions}</i>" if ligne.instructions else ""
        rows.append([
            Paragraph(f"<b>{ligne.medicament}</b> {ligne.dosage} {ligne.unite or ''}", st['body']),
            Paragraph(f"{ligne.frequence}{note}", st['body']),
            Paragraph(str(ligne.duree), st['body']),
        ])

    story.append(Table(rows, colWidths=[6.5*cm, 6.5*cm, 2.5*cm],
                       style=[('BACKGROUND',(0,0),(-1,0),GREEN),
                              ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE, GREEN_LIGHT]),
                              ('BOX',(0,0),(-1,-1),1,GREEN),
                              ('INNERGRID',(0,0),(-1,-1),0.5,GREEN_LIGHT),
                              ('TOPPADDING',(0,0),(-1,-1),6),
                              ('BOTTOMPADDING',(0,0),(-1,-1),6),
                              ('LEFTPADDING',(0,0),(-1,-1),6),
                              ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))

    if prescription.notes_generales:
        story.append(Spacer(1, 0.4*cm))
        story.append(Paragraph(f"<b>Notes :</b> {prescription.notes_generales}", st['body']))

    # ── Signature ──────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    sig_path = os.path.join(settings.BASE_DIR, 'apps', 'common', 'signature.png')
    sig_els = [Paragraph("Signature &amp; Cachet du Médecin :", st['sig_lbl']), Spacer(1, 0.2*cm)]
    if os.path.exists(sig_path):
        img = Image(sig_path, width=4*cm, height=4*cm)
        img.hAlign = 'RIGHT'
        sig_els.append(img)
    else:
        sig_els.append(Spacer(1, 1.5*cm))
    sig_els.append(Paragraph(f"<b>Dr. {medecin.get_full_name()}</b>", st['sig_name']))
    story.append(Table([[sig_els]], colWidths=[PAGE_W],
                       style=[('ALIGN',(0,0),(-1,-1),'RIGHT')]))

    # ── Pied de page ───────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', thickness=1, color=GREEN_LIGHT))
    story.append(Paragraph(
        "Document généré par CuraMedical — Réservé à l'usage exclusif du patient.",
        st['footer']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
