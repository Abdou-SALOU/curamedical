# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "architecture_curamedical_simplifiee.png"

W, H = 2200, 1350
BG = "#f7f9fc"
INK = "#172033"
MUTED = "#596579"
LINE = "#526176"


def font(size: int, bold: bool = False):
    for path in [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


F_TITLE = font(52, True)
F_SUB = font(24)
F_CARD = font(30, True)
F_BODY = font(22)
F_SMALL = font(18)


def rounded(draw, box, fill, outline="#cfd8e6", width=2, radius=26):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def measure(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def wrapped(draw, x, y, text, fnt, width, fill=MUTED, gap=8):
    lines = []
    current = ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if measure(draw, candidate, fnt)[0] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += measure(draw, line, fnt)[1] + gap
    return y


def card(draw, box, title, body, color, icon):
    x1, y1, x2, y2 = box
    rounded(draw, box, "#ffffff")
    draw.rounded_rectangle((x1, y1, x2, y1 + 14), radius=8, fill=color)
    draw.ellipse((x1 + 30, y1 + 42, x1 + 86, y1 + 98), fill=color)
    tw, th = measure(draw, icon, font(26, True))
    draw.text((x1 + 58 - tw / 2, y1 + 70 - th / 2), icon, font=font(26, True), fill="#ffffff")
    draw.text((x1 + 110, y1 + 45), title, font=F_CARD, fill=INK)
    wrapped(draw, x1 + 32, y1 + 125, body, F_BODY, x2 - x1 - 64)


def arrow(draw, start, end, label=None):
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=LINE, width=5)
    head = 18
    if x2 >= x1:
        pts = [(x2, y2), (x2 - head, y2 - 10), (x2 - head, y2 + 10)]
    else:
        pts = [(x2, y2), (x2 + head, y2 - 10), (x2 + head, y2 + 10)]
    draw.polygon(pts, fill=LINE)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        tw, th = measure(draw, label, F_SMALL)
        draw.rounded_rectangle((mx - tw / 2 - 12, my - th / 2 - 8, mx + tw / 2 + 12, my + th / 2 + 8), radius=10, fill=BG, outline="#d9e1ee")
        draw.text((mx - tw / 2, my - th / 2), label, font=F_SMALL, fill=LINE)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((80, 55), "Architecture simplifiée de CuraMedical", font=F_TITLE, fill=INK)
    draw.text((82, 120), "Vue globale des couches principales et des flux essentiels du projet.", font=F_SUB, fill=MUTED)

    users = (90, 330, 400, 580)
    front = (520, 280, 890, 630)
    back = (1030, 250, 1470, 670)
    db = (1620, 275, 2050, 535)
    ia = (1620, 640, 2050, 900)
    ext = (1030, 820, 1470, 1115)

    card(
        draw,
        users,
        "Utilisateurs",
        "Administrateur, médecin, secrétaire et patient utilisent l'application selon leurs droits d'accès.",
        "#0891b2",
        "U",
    )
    card(
        draw,
        front,
        "Frontend React",
        "Interface web Vite/React : tableaux de bord, patients, rendez-vous, consultations, ordonnances, admin et espace patient.",
        "#10b981",
        "R",
    )
    card(
        draw,
        back,
        "Backend Django REST",
        "API centrale sécurisée par JWT. Elle orchestre les modules métier : utilisateurs, patients, rendez-vous, consultations, prescriptions, chat et WhatsApp.",
        "#2563eb",
        "API",
    )
    card(
        draw,
        db,
        "Base PostgreSQL",
        "Stockage des comptes, dossiers patients, rendez-vous, consultations, ordonnances, messages WhatsApp et journaux d'audit.",
        "#7c3aed",
        "DB",
    )
    card(
        draw,
        ia,
        "Service IA Flask",
        "Analyse les symptômes, propose des diagnostics indicatifs et aide le chatbot grâce au modèle ML et à Groq/LLaMA.",
        "#db2777",
        "IA",
    )
    card(
        draw,
        ext,
        "Services externes",
        "Twilio WhatsApp, n8n, SMTP Email et Jitsi complètent le système pour les notifications, documents PDF et téléconsultations.",
        "#f97316",
        "S",
    )

    arrow(draw, (400, 455), (520, 455), "navigateur")
    arrow(draw, (890, 455), (1030, 455), "requêtes API")
    arrow(draw, (1470, 405), (1620, 405), "données")
    arrow(draw, (1470, 555), (1620, 770), "analyse IA")
    arrow(draw, (1250, 670), (1250, 820), "notifications / PDF / visio")
    arrow(draw, (1620, 770), (1470, 555), "suggestions")

    rounded(draw, (90, 1190, 2110, 1280), "#ffffff")
    draw.text((120, 1215), "Résumé", font=font(25, True), fill=INK)
    wrapped(
        draw,
        260,
        1215,
        "Le frontend communique avec l'API Django. Le backend applique les règles métier, stocke les données dans PostgreSQL, sollicite le service IA pour l'aide au diagnostic et s'appuie sur des services externes pour la communication et la téléconsultation.",
        F_BODY,
        1760,
    )

    draw.text((80, 1310), "Source : analyse du dépôt CuraMedical.", font=F_SMALL, fill="#7a8699")
    img.save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()
