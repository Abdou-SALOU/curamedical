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
        'doc_name': ParagraphStyle('DN', fontSize=13, fontName='Helvetica-Bold', textColor=GREEN_DARK, spaceAfter=2),
        'doc_info': ParagraphStyle('DI', fontSize=9,  fontName='Helvetica', textColor=GREY),
        'cli_name': ParagraphStyle('CN', fontSize=11, fontName='Helvetica-Bold', textColor=GREEN_DARK, alignment=2, spaceAfter=2),
        'cli_info': ParagraphStyle('CI', fontSize=9,  fontName='Helvetica', textColor=GREY, alignment=2),
        'title':    ParagraphStyle('T',  fontSize=16, fontName='Helvetica-Bold', textColor=WHITE, alignment=1),
        'section':  ParagraphStyle('S',  fontSize=11, fontName='Helvetica-Bold', textColor=GREEN_DARK, spaceBefore=10, spaceAfter=4),
        'body':     ParagraphStyle('B',  fontSize=10, fontName='Helvetica', textColor=DARK, spaceAfter=3, leading=14),
        'ia_note':  ParagraphStyle('IA', fontSize=8,  fontName='Helvetica-Oblique', textColor=GREY),
        'sig_lbl':  ParagraphStyle('SL', fontSize=9,  fontName='Helvetica', textColor=GREY, alignment=2),
        'sig_name': ParagraphStyle('SN', fontSize=10, fontName='Helvetica-Bold', textColor=GREEN_DARK, alignment=2),
        'pat_key':  ParagraphStyle('PK', fontSize=9,  fontName='Helvetica-Bold', textColor=GREEN_DARK),
        'pat_val':  ParagraphStyle('PV', fontSize=9,  fontName='Helvetica', textColor=DARK),
        'footer':   ParagraphStyle('F',  fontSize=8,  fontName='Helvetica-Oblique', textColor=GREY, alignment=1),
    }


def generate_consultation_report_pdf(consultation):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            topMargin=1.5*cm, bottomMargin=2*cm,
                            leftMargin=2.5*cm, rightMargin=2.5*cm)
    st = _st()
    story = []

    medecin    = consultation.medecin
    patient    = consultation.patient
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
    story.append(Table([[Paragraph("COMPTE RENDU DE CONSULTATION", st['title'])]],
                       colWidths=[PAGE_W],
                       style=[('BACKGROUND',(0,0),(-1,-1),GREEN),
                              ('TOPPADDING',(0,0),(-1,-1),8),
                              ('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(Spacer(1, 0.5*cm))

    # ── Patient ────────────────────────────────────────────────────────
    sexe    = 'Masculin' if patient.sexe == 'M' else 'Féminin'
    date_str = consultation.date_consultation.strftime('%d/%m/%Y à %H:%M')
    pdata = [
        [Paragraph("Patient(e) :", st['pat_key']), Paragraph(patient.nom_complet, st['pat_val']),
         Paragraph("Âge :", st['pat_key']),  Paragraph(f"{patient.age} ans", st['pat_val'])],
        [Paragraph("Sexe :", st['pat_key']),  Paragraph(sexe, st['pat_val']),
         Paragraph("Date de consultation :", st['pat_key']), Paragraph(date_str, st['pat_val'])],
    ]
    story.append(Table(pdata, colWidths=[3*cm, 5*cm, 3.5*cm, 4*cm],
                       style=[('BACKGROUND',(0,0),(-1,-1),GREEN_LIGHT),
                              ('BOX',(0,0),(-1,-1),1,GREEN),
                              ('TOPPADDING',(0,0),(-1,-1),6),
                              ('BOTTOMPADDING',(0,0),(-1,-1),6),
                              ('LEFTPADDING',(0,0),(-1,-1),8),
                              ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(Spacer(1, 0.4*cm))

    # ── Sections cliniques ─────────────────────────────────────────────
    def add_section(label, content):
        if not content:
            return
        story.append(Paragraph(label, st['section']))
        story.append(HRFlowable(width='100%', thickness=1, color=GREEN_LIGHT, spaceAfter=4))
        text = ', '.join(content) if isinstance(content, list) else content
        story.append(Paragraph(text, st['body']))

    add_section("Motif &amp; Symptômes",   consultation.symptomes)
    add_section("Examen Clinique",          consultation.examen_clinique)
    add_section("Diagnostic Retenu",        consultation.diagnostic)

    if consultation.ia_utilisee and consultation.suggestions_ia:
        story.append(Paragraph(
            "ℹ️ Ce diagnostic a été assisté par l'IA CuraMedical.",
            st['ia_note']
        ))

    add_section("Notes du Médecin", consultation.notes)

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
        "Document généré par CuraMedical — Strictement confidentiel.",
        st['footer']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
