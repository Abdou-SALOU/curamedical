# -*- coding: utf-8 -*-
"""Régénère les PDF d'exemple (ordonnance + compte rendu) avec le NOUVEAU cachet,
puis les convertit en images pour le rapport. Code des générateurs identique à
celui du produit (backend/apps/.../*_generator.py), sans dépendance Django.
"""
import io
import os
import types
import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image, HRFlowable
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
import fitz  # PyMuPDF

ROOT = r"c:\2CI-ISI\S2\Projet en Systèmes Informatiques\MedPredict\CuraMedical"
SHOTS = os.path.join(ROOT, "soutenance", "screenshots", "curamedical-rapport")
SIG_PATH = os.path.join(ROOT, "backend", "apps", "common", "signature.png")  # nouveau cachet

GREEN       = HexColor('#10b981')
GREEN_DARK  = HexColor('#059669')
GREEN_LIGHT = HexColor('#d1fae5')
DARK        = HexColor('#0f172a')
GREY        = HexColor('#64748b')
WHITE       = colors.white
PAGE_W      = A4[0] - 5 * cm


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
        'ia_note':   ParagraphStyle('IA',  fontSize=8,  fontName='Helvetica-Oblique', textColor=GREY),
        'sig_lbl':   ParagraphStyle('SL',  fontSize=9,  fontName='Helvetica', textColor=GREY, alignment=2),
        'sig_name':  ParagraphStyle('SN',  fontSize=10, fontName='Helvetica-Bold', textColor=GREEN_DARK, alignment=2),
        'pat_key':   ParagraphStyle('PK',  fontSize=9,  fontName='Helvetica-Bold', textColor=GREEN_DARK),
        'pat_val':   ParagraphStyle('PV',  fontSize=9,  fontName='Helvetica', textColor=DARK),
        'footer':    ParagraphStyle('F',   fontSize=8,  fontName='Helvetica-Oblique', textColor=GREY, alignment=1),
    }


def generate_prescription_pdf(prescription, path):
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=1.5*cm, bottomMargin=2*cm,
                            leftMargin=2.5*cm, rightMargin=2.5*cm)
    st = _st(); story = []
    medecin = prescription.medecin; patient = prescription.patient
    specialite = getattr(medecin, 'specialite', '') or 'Médecin'
    tel_med = getattr(medecin, 'telephone', '') or 'N/A'

    left = [Paragraph(f"DR. {medecin.get_full_name().upper()}", st['doc_name']),
            Paragraph(f"Spécialité : {specialite}", st['doc_info']),
            Paragraph(f"Tél : {tel_med}", st['doc_info'])]
    right = [Paragraph("Clinique CuraMedical", st['cli_name']),
             Paragraph("Quartier des Hôpitaux", st['cli_info']),
             Paragraph("20360 Casablanca, Maroc", st['cli_info']),
             Paragraph("Tél : +212 5 22 00 00 00", st['cli_info'])]
    story.append(Table([[left, right]], colWidths=[PAGE_W*0.55, PAGE_W*0.45],
                       style=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width='100%', thickness=2, color=GREEN, spaceAfter=6))
    story.append(Table([[Paragraph("ORDONNANCE MÉDICALE", st['title'])]], colWidths=[PAGE_W],
                       style=[('BACKGROUND',(0,0),(-1,-1),GREEN),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(Spacer(1, 0.5*cm))
    sexe = 'Masculin' if patient.sexe == 'M' else 'Féminin'
    pdata = [[Paragraph("Patient(e) :", st['pat_key']), Paragraph(patient.nom_complet, st['pat_val']),
              Paragraph("Âge :", st['pat_key']), Paragraph(f"{patient.age} ans", st['pat_val'])],
             [Paragraph("Sexe :", st['pat_key']), Paragraph(sexe, st['pat_val']),
              Paragraph("Date :", st['pat_key']), Paragraph(prescription.cree_le.strftime('%d/%m/%Y'), st['pat_val'])]]
    story.append(Table(pdata, colWidths=[2.5*cm, 5.5*cm, 2*cm, 5.5*cm],
                       style=[('BACKGROUND',(0,0),(-1,-1),GREEN_LIGHT),('BOX',(0,0),(-1,-1),1,GREEN),
                              ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                              ('LEFTPADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph("Prescriptions :", st['section']))
    story.append(HRFlowable(width='100%', thickness=1, color=GREEN_LIGHT, spaceAfter=4))
    rows = [[Paragraph("Médicament &amp; Dosage", st['th']), Paragraph("Posologie / Fréquence", st['th']), Paragraph("Durée", st['th'])]]
    for ligne in prescription.lignes.all():
        note = f" <i>Note: {ligne.instructions}</i>" if ligne.instructions else ""
        rows.append([Paragraph(f"<b>{ligne.medicament}</b> {ligne.dosage} {ligne.unite or ''}", st['body']),
                     Paragraph(f"{ligne.frequence}{note}", st['body']), Paragraph(str(ligne.duree), st['body'])])
    story.append(Table(rows, colWidths=[6.5*cm, 6.5*cm, 2.5*cm],
                       style=[('BACKGROUND',(0,0),(-1,0),GREEN),('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE, GREEN_LIGHT]),
                              ('BOX',(0,0),(-1,-1),1,GREEN),('INNERGRID',(0,0),(-1,-1),0.5,GREEN_LIGHT),
                              ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                              ('LEFTPADDING',(0,0),(-1,-1),6),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    if prescription.notes_generales:
        story.append(Spacer(1, 0.4*cm))
        story.append(Paragraph(f"<b>Notes :</b> {prescription.notes_generales}", st['body']))
    story.append(Spacer(1, 1*cm))
    sig_els = [Paragraph("Signature &amp; Cachet du Médecin :", st['sig_lbl']), Spacer(1, 0.2*cm)]
    if os.path.exists(SIG_PATH):
        img = Image(SIG_PATH, width=4*cm, height=4*cm); img.hAlign = 'RIGHT'; sig_els.append(img)
    sig_els.append(Paragraph(f"<b>Dr. {medecin.get_full_name()}</b>", st['sig_name']))
    story.append(Table([[sig_els]], colWidths=[PAGE_W], style=[('ALIGN',(0,0),(-1,-1),'RIGHT')]))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', thickness=1, color=GREEN_LIGHT))
    story.append(Paragraph("Document généré par CuraMedical — Réservé à l'usage exclusif du patient.", st['footer']))
    doc.build(story)


def generate_consultation_report_pdf(consultation, path):
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=1.5*cm, bottomMargin=2*cm,
                            leftMargin=2.5*cm, rightMargin=2.5*cm)
    st = _st(); story = []
    medecin = consultation.medecin; patient = consultation.patient
    specialite = getattr(medecin, 'specialite', '') or 'Médecin'
    tel_med = getattr(medecin, 'telephone', '') or 'N/A'
    left = [Paragraph(f"DR. {medecin.get_full_name().upper()}", st['doc_name']),
            Paragraph(f"Spécialité : {specialite}", st['doc_info']),
            Paragraph(f"Tél : {tel_med}", st['doc_info'])]
    right = [Paragraph("Clinique CuraMedical", st['cli_name']),
             Paragraph("Quartier des Hôpitaux", st['cli_info']),
             Paragraph("20360 Casablanca, Maroc", st['cli_info']),
             Paragraph("Tél : +212 5 22 00 00 00", st['cli_info'])]
    story.append(Table([[left, right]], colWidths=[PAGE_W*0.55, PAGE_W*0.45],
                       style=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width='100%', thickness=2, color=GREEN, spaceAfter=6))
    story.append(Table([[Paragraph("COMPTE RENDU DE CONSULTATION", st['title'])]], colWidths=[PAGE_W],
                       style=[('BACKGROUND',(0,0),(-1,-1),GREEN),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(Spacer(1, 0.5*cm))
    sexe = 'Masculin' if patient.sexe == 'M' else 'Féminin'
    date_str = consultation.date_consultation.strftime('%d/%m/%Y à %H:%M')
    pdata = [[Paragraph("Patient(e) :", st['pat_key']), Paragraph(patient.nom_complet, st['pat_val']),
              Paragraph("Âge :", st['pat_key']), Paragraph(f"{patient.age} ans", st['pat_val'])],
             [Paragraph("Sexe :", st['pat_key']), Paragraph(sexe, st['pat_val']),
              Paragraph("Date de consultation :", st['pat_key']), Paragraph(date_str, st['pat_val'])]]
    story.append(Table(pdata, colWidths=[3*cm, 5*cm, 3.5*cm, 4*cm],
                       style=[('BACKGROUND',(0,0),(-1,-1),GREEN_LIGHT),('BOX',(0,0),(-1,-1),1,GREEN),
                              ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                              ('LEFTPADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(Spacer(1, 0.4*cm))

    def add_section(label, content):
        if not content:
            return
        story.append(Paragraph(label, st['section']))
        story.append(HRFlowable(width='100%', thickness=1, color=GREEN_LIGHT, spaceAfter=4))
        text = ', '.join(content) if isinstance(content, list) else content
        story.append(Paragraph(text, st['body']))

    add_section("Motif &amp; Symptômes", consultation.symptomes)
    add_section("Examen Clinique", consultation.examen_clinique)
    add_section("Diagnostic Retenu", consultation.diagnostic)
    if consultation.ia_utilisee and consultation.suggestions_ia:
        story.append(Paragraph("Ce diagnostic a été assisté par l'IA CuraMedical.", st['ia_note']))
    add_section("Notes du Médecin", consultation.notes)
    story.append(Spacer(1, 1*cm))
    sig_els = [Paragraph("Signature &amp; Cachet du Médecin :", st['sig_lbl']), Spacer(1, 0.2*cm)]
    if os.path.exists(SIG_PATH):
        img = Image(SIG_PATH, width=4*cm, height=4*cm); img.hAlign = 'RIGHT'; sig_els.append(img)
    sig_els.append(Paragraph(f"<b>Dr. {medecin.get_full_name()}</b>", st['sig_name']))
    story.append(Table([[sig_els]], colWidths=[PAGE_W], style=[('ALIGN',(0,0),(-1,-1),'RIGHT')]))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', thickness=1, color=GREEN_LIGHT))
    story.append(Paragraph("Document généré par CuraMedical — Strictement confidentiel.", st['footer']))
    doc.build(story)


# ── Données d'exemple (cohérentes avec la démonstration) ────────────────────
def medecin():
    m = types.SimpleNamespace(specialite="Médecin Généraliste", telephone="+212 6 12 34 56 78")
    m.get_full_name = lambda: "Nouridine SAWADOGO"
    return m

def patient():
    return types.SimpleNamespace(nom_complet="LAHLOU Fatima Zahra", age=32, sexe="F")

def ligne(med, dos, unite, freq, duree, instr=None):
    return types.SimpleNamespace(medicament=med, dosage=dos, unite=unite, frequence=freq, duree=duree, instructions=instr)

def build_prescription():
    lignes = [
        ligne("Amoxicilline", "500 mg", "gélule", "3 fois par jour", "7 jours", "À prendre au cours des repas"),
        ligne("Paracétamol", "1000 mg", "comprimé", "3 fois par jour si fièvre", "5 jours"),
        ligne("Sirop antitussif", "", "sirop", "1 cuillère, 3 fois/jour", "5 jours"),
    ]
    mgr = types.SimpleNamespace(all=lambda: lignes)
    return types.SimpleNamespace(
        medecin=medecin(), patient=patient(), lignes=mgr,
        notes_generales="Repos recommandé et hydratation abondante. Réévaluation si la fièvre persiste au-delà de 48 h.",
        cree_le=datetime.datetime(2026, 5, 19, 10, 30),
    )

def build_consultation():
    return types.SimpleNamespace(
        medecin=medecin(), patient=patient(),
        symptomes=["Fièvre (38,7 °C)", "Toux", "Maux de gorge", "Céphalées"],
        examen_clinique="Gorge érythémateuse avec adénopathies cervicales sensibles. Auscultation pulmonaire claire, "
                        "absence de signe de détresse respiratoire.",
        diagnostic="Angine aiguë d'allure bactérienne.",
        notes="Repos, hydratation, antalgiques. Contrôle si aggravation ou fièvre persistante au-delà de 48 heures.",
        ia_utilisee=True,
        suggestions_ia=[{"disease": "Angine", "confidence": 72.0}],
        date_consultation=datetime.datetime(2026, 5, 19, 10, 30),
    )


def pdf_to_png(pdf_path, png_path, dpi=170):
    d = fitz.open(pdf_path)
    page = d.load_page(0)
    zoom = dpi / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    pix.save(png_path)
    d.close()


if __name__ == '__main__':
    ord_pdf = os.path.join(SHOTS, "ordonnance-exemple.pdf")
    cr_pdf  = os.path.join(SHOTS, "compte-rendu-exemple.pdf")
    generate_prescription_pdf(build_prescription(), ord_pdf)
    generate_consultation_report_pdf(build_consultation(), cr_pdf)
    pdf_to_png(ord_pdf, os.path.join(SHOTS, "38-ordonnance-pdf.png"))
    pdf_to_png(cr_pdf,  os.path.join(SHOTS, "39-compte-rendu-pdf.png"))
    print("PDFs + PNGs régénérés avec le nouveau cachet.")
