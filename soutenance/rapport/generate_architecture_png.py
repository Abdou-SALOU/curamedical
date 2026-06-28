# -*- coding: utf-8 -*-
from __future__ import annotations

import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "architecture_curamedical.png"


W, H = 3000, 2050
BG = "#f6f8fb"
INK = "#172033"
MUTED = "#556070"
LINE = "#68758a"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


F_TITLE = font(54, True)
F_SUB = font(25)
F_GROUP = font(28, True)
F_CARD = font(25, True)
F_BODY = font(21)
F_SMALL = font(18)
F_TAG = font(17, True)


def rounded(draw: ImageDraw.ImageDraw, box, fill, outline="#d6dde8", width=2, radius=24):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def center_text(draw, xy, text, fnt, fill=INK):
    tw, th = text_size(draw, text, fnt)
    draw.text((xy[0] - tw / 2, xy[1] - th / 2), text, font=fnt, fill=fill)


def wrapped(draw, x, y, text, fnt, fill=INK, max_width=360, line_gap=7):
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        probe = (current + " " + word).strip()
        if text_size(draw, probe, fnt)[0] <= max_width:
            current = probe
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += text_size(draw, line, fnt)[1] + line_gap
    return y


def pill(draw, x, y, text, fill, fg="#ffffff"):
    tw, th = text_size(draw, text, F_TAG)
    box = (x, y, x + tw + 26, y + th + 14)
    draw.rounded_rectangle(box, radius=16, fill=fill)
    draw.text((x + 13, y + 6), text, font=F_TAG, fill=fg)
    return box[2]


def card(draw, box, title, body_lines, fill, accent, tags=None):
    x1, y1, x2, y2 = box
    rounded(draw, box, fill=fill, outline="#cbd5e1", width=2, radius=22)
    draw.rounded_rectangle((x1, y1, x2, y1 + 12), radius=8, fill=accent)
    draw.text((x1 + 28, y1 + 28), title, font=F_CARD, fill=INK)
    y = y1 + 70
    for line in body_lines:
        y = wrapped(draw, x1 + 28, y, line, F_BODY, fill=MUTED, max_width=x2 - x1 - 56, line_gap=5)
        y += 8
    if tags:
        tx = x1 + 28
        ty = y2 - 42
        for t in tags:
            tx = pill(draw, tx, ty, t, accent) + 9


def group(draw, box, title, fill="#ffffff"):
    rounded(draw, box, fill=fill, outline="#cbd5e1", width=2, radius=28)
    draw.text((box[0] + 26, box[1] + 18), title, font=F_GROUP, fill=INK)


def arrow(draw, start, end, color=LINE, width=4, label=None, label_pos=0.5, curve=0):
    x1, y1 = start
    x2, y2 = end
    if curve == 0:
        draw.line((x1, y1, x2, y2), fill=color, width=width)
        lx = x1 + (x2 - x1) * label_pos
        ly = y1 + (y2 - y1) * label_pos
    else:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2 + curve
        pts = []
        for i in range(31):
            t = i / 30
            xa = (1 - t) * x1 + t * mx
            ya = (1 - t) * y1 + t * my
            xb = (1 - t) * mx + t * x2
            yb = (1 - t) * my + t * y2
            pts.append(((1 - t) * xa + t * xb, (1 - t) * ya + t * yb))
        draw.line(pts, fill=color, width=width, joint="curve")
        lx, ly = pts[int(len(pts) * label_pos)]

    angle = math.atan2(y2 - y1, x2 - x1)
    head = 18
    spread = 0.55
    p1 = (x2 - head * math.cos(angle - spread), y2 - head * math.sin(angle - spread))
    p2 = (x2 - head * math.cos(angle + spread), y2 - head * math.sin(angle + spread))
    draw.polygon([end, p1, p2], fill=color)

    if label:
        tw, th = text_size(draw, label, F_SMALL)
        pad = 8
        draw.rounded_rectangle(
            (lx - tw / 2 - pad, ly - th / 2 - pad, lx + tw / 2 + pad, ly + th / 2 + pad),
            radius=10,
            fill=BG,
            outline="#d7dee9",
        )
        center_text(draw, (lx, ly), label, F_SMALL, fill=color)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((90, 60), "Architecture complète du projet CuraMedical", font=F_TITLE, fill=INK)
    draw.text(
        (92, 128),
        "Application de gestion de cabinet médical avec API Django REST, frontend React, microservice IA, automatisation n8n et intégrations WhatsApp/Jitsi.",
        font=F_SUB,
        fill=MUTED,
    )

    # Groups
    group(draw, (70, 220, 440, 1690), "Acteurs")
    group(draw, (500, 220, 930, 1690), "Interface Web")
    group(draw, (990, 220, 1810, 1690), "Backend Django REST")
    group(draw, (1870, 220, 2300, 1690), "Données et IA")
    group(draw, (2360, 220, 2930, 1690), "Services externes")

    # Actors
    actor_data = [
        ("Administrateur", "Gestion utilisateurs, rôles, audit"),
        ("Médecin", "Patients, RDV, consultations, IA, ordonnances"),
        ("Secrétaire", "Accueil, patients, planning RDV"),
        ("Patient", "Profil, RDV, ordonnances, WhatsApp"),
    ]
    y = 320
    for title, desc in actor_data:
        card(draw, (110, y, 400, y + 190), title, [desc], "#ffffff", "#0891b2", ["Rôle"])
        y += 235

    # Frontend
    card(
        draw,
        (540, 330, 890, 580),
        "React + Vite",
        ["SPA protégée par routes privées, état global Zustand, appels API via Axios."],
        "#ffffff",
        "#10b981",
        ["3000", "JWT"],
    )
    card(
        draw,
        (540, 660, 890, 980),
        "Pages métier",
        [
            "Dashboard, Patients, Rendez-vous, Consultations, Ordonnances, Admin, Profil patient, Corbeille.",
            "Téléconsultation via salle dédiée.",
        ],
        "#ffffff",
        "#10b981",
        ["UI"],
    )
    card(
        draw,
        (540, 1060, 890, 1370),
        "Composants partagés",
        [
            "Navbar, Layout, PrivateRoute, Pagination, Toasts, modales, widgets graphiques et ChatbotWidget.",
        ],
        "#ffffff",
        "#10b981",
        ["UX"],
    )

    # Backend core
    card(
        draw,
        (1030, 315, 1770, 550),
        "API REST CuraMedical",
        [
            "Django 4.2 + DRF, JWT SimpleJWT, CORS, pagination, throttling, Swagger/OpenAPI.",
            "Entrée principale : /api/* et /admin/.",
        ],
        "#ffffff",
        "#2563eb",
        ["8000", "Gunicorn"],
    )
    modules = [
        ("users", "Utilisateur personnalisé : administrateur, médecin, secrétaire, patient. Permissions et audit."),
        ("patients", "Dossier patient, coordonnées, antécédents, allergies, archivage."),
        ("appointments", "Rendez-vous, conflits horaires, statuts, téléconsultation Jitsi."),
        ("consultations", "Examen, diagnostic, symptômes JSON, suggestions IA, compte rendu PDF."),
        ("prescriptions", "Ordonnances, lignes de médicaments, génération PDF, email/webhook."),
        ("whatsapp + chat", "Bot WhatsApp Twilio, conversations, chatbot interne et analyse de symptômes."),
    ]
    x_positions = [1030, 1405]
    y_positions = [630, 850, 1070]
    i = 0
    for y in y_positions:
        for x in x_positions:
            title, desc = modules[i]
            card(draw, (x, y, x + 330, y + 175), title, [desc], "#f8fbff", "#3b82f6")
            i += 1

    card(
        draw,
        (1150, 1320, 1650, 1505),
        "Génération documentaire",
        ["Templates HTML Django pour ordonnance et compte rendu, puis export PDF et partage par email/WhatsApp."],
        "#ffffff",
        "#64748b",
        ["PDF"],
    )

    # Data / IA
    card(
        draw,
        (1910, 330, 2260, 570),
        "PostgreSQL 15",
        [
            "Tables métier : users, patients, rendez-vous, consultations, prescriptions, WhatsAppConversation, WhatsAppMessage, auditlog.",
        ],
        "#ffffff",
        "#7c3aed",
        ["DB"],
    )
    card(
        draw,
        (1910, 660, 2260, 940),
        "Microservice IA Flask",
        [
            "/predict : top 3 diagnostics avec confiance.",
            "/brain : intention, réponse assistée et extraction symptômes.",
            "/symptoms : référentiel symptômes.",
        ],
        "#ffffff",
        "#db2777",
        ["5000", "REST"],
    )
    card(
        draw,
        (1910, 1030, 2260, 1265),
        "Modèles ML",
        [
            "Random Forest + LabelEncoder + features_list entraînés sur le dataset maladies/symptômes.",
            "Fallback par dictionnaire français vers anglais.",
        ],
        "#fffafd",
        "#db2777",
        ["scikit-learn"],
    )
    card(
        draw,
        (1910, 1350, 2260, 1535),
        "Stockage fichiers",
        ["Media Django, PDFs générés, templates, assets et volumes Docker persistants."],
        "#ffffff",
        "#7c3aed",
        ["media"],
    )

    # External services
    externals = [
        ("Groq / LLaMA", "Compréhension langage naturel, extraction d'entités, réponses IA."),
        ("Twilio WhatsApp", "Messages entrants/sortants, documents PDF envoyés aux patients."),
        ("n8n", "Workflows de notifications et webhooks prescriptions/rappels."),
        ("SMTP Email", "Emails de confirmation, ordonnances et comptes rendus."),
        ("Jitsi Meet", "Salles de téléconsultation générées par RDV."),
    ]
    y = 320
    for title, desc in externals:
        card(draw, (2400, y, 2890, y + 170), title, [desc], "#ffffff", "#f97316")
        y += 260

    # Arrows
    # Main request path
    arrow(draw, (400, 745), (540, 745), label="navigateur")
    arrow(draw, (890, 455), (1030, 430), label="Axios REST /api")
    arrow(draw, (1770, 430), (1910, 450), label="ORM")

    # Frontend pages to API modules
    arrow(draw, (890, 820), (1030, 720), label="CRUD métier")
    arrow(draw, (890, 1215), (1030, 1160), label="chatbot UI")

    # Backend modules persist through the API/ORM layer represented above.

    # IA path
    arrow(draw, (1735, 1160), (1910, 800), label="analyse symptômes", curve=-35)
    arrow(draw, (2085, 940), (2085, 1030), label="modèle")
    arrow(draw, (2260, 785), (2400, 405), label="LLM Groq", curve=-80)

    # External integrations, aligned by rows
    arrow(draw, (1735, 1160), (2400, 665), label="webhook WhatsApp", curve=-70)
    arrow(draw, (1650, 1410), (2400, 930), label="webhook n8n", curve=-35)
    arrow(draw, (1650, 1455), (2400, 1190), label="SMTP")
    arrow(draw, (1360, 935), (2400, 1450), label="salle Jitsi", curve=65)

    # Files/PDF storage
    arrow(draw, (1650, 1410), (1910, 1440), label="PDF / media")

    # Legend
    legend = (90, 1745, 2910, 1955)
    rounded(draw, legend, fill="#ffffff", outline="#cbd5e1", width=2, radius=24)
    draw.text((120, 1773), "Lecture du schéma", font=F_GROUP, fill=INK)
    legend_text = (
        "Le frontend React consomme l'API Django avec JWT. Le backend orchestre les modules métier, persiste les données dans PostgreSQL, "
        "appelle le microservice IA Flask pour les suggestions de diagnostic et délègue les communications à Twilio, n8n, SMTP et Jitsi. "
        "Les rôles applicatifs filtrent les accès aux pages et aux endpoints."
    )
    wrapped(draw, 120, 1820, legend_text, F_BODY, fill=MUTED, max_width=2700, line_gap=5)

    # Footer
    draw.text((90, 1985), "Source : analyse du dépôt CuraMedical, docker-compose.yml, settings Django, routes, modèles, frontend App.jsx et service IA.", font=F_SMALL, fill="#758195")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()
