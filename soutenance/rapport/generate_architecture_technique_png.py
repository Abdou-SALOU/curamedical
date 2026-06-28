# -*- coding: utf-8 -*-
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "architecture_curamedical_technique.png"

W, H = 2400, 1500
BG = "#f5f8fc"
INK = "#162033"
MUTED = "#5d687a"
LINE = "#526176"
DOCKER = "#2496ed"
REACT = "#10b981"
DJANGO = "#14532d"
POSTGRES = "#336791"
AI = "#d946ef"
N8N = "#ea4b71"
EXT = "#f97316"


def font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


F_TITLE = font(56, True)
F_SUB = font(24)
F_SECTION = font(26, True)
F_CARD = font(28, True)
F_BODY = font(20)
F_SMALL = font(17)
F_ICON = font(24, True)


def text_size(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def rounded(draw, box, fill, outline="#cbd5e1", width=2, radius=24):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap(draw, x, y, text, fnt, max_width, fill=MUTED, gap=6):
    line = ""
    for word in text.split():
        candidate = (line + " " + word).strip()
        if text_size(draw, candidate, fnt)[0] <= max_width:
            line = candidate
        else:
            draw.text((x, y), line, font=fnt, fill=fill)
            y += text_size(draw, line, fnt)[1] + gap
            line = word
    if line:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += text_size(draw, line, fnt)[1] + gap
    return y


def center(draw, xy, text, fnt, fill=INK):
    tw, th = text_size(draw, text, fnt)
    draw.text((xy[0] - tw / 2, xy[1] - th / 2), text, font=fnt, fill=fill)


def arrow(draw, start, end, label=None, color=LINE, width=5, elbow=False):
    x1, y1 = start
    x2, y2 = end
    if elbow:
        mid = ((x1 + x2) / 2, y1)
        pts = [(x1, y1), mid, (mid[0], y2), (x2, y2)]
        draw.line(pts, fill=color, width=width, joint="curve")
    else:
        draw.line((x1, y1, x2, y2), fill=color, width=width)

    angle = math.atan2(y2 - y1, x2 - x1)
    head = 18
    spread = 0.55
    p1 = (x2 - head * math.cos(angle - spread), y2 - head * math.sin(angle - spread))
    p2 = (x2 - head * math.cos(angle + spread), y2 - head * math.sin(angle + spread))
    draw.polygon([end, p1, p2], fill=color)

    if label:
        lx, ly = (x1 + x2) / 2, (y1 + y2) / 2
        tw, th = text_size(draw, label, F_SMALL)
        draw.rounded_rectangle((lx - tw / 2 - 12, ly - th / 2 - 8, lx + tw / 2 + 12, ly + th / 2 + 8), radius=10, fill=BG, outline="#d6dee9")
        center(draw, (lx, ly), label, F_SMALL, color)


def draw_docker_logo(draw, x, y, scale=1.0):
    c = DOCKER
    block = int(18 * scale)
    gap = int(4 * scale)
    rows = [
        (2, 3),
        (1, 4),
        (0, 5),
    ]
    for row, (offset, count) in enumerate(rows):
        for i in range(count):
            bx = x + (offset + i) * (block + gap)
            by = y + row * (block + gap)
            draw.rounded_rectangle((bx, by, bx + block, by + block), radius=3, fill=c)
    hull_y = y + 3 * (block + gap) + 5
    draw.rounded_rectangle((x + 5, hull_y, x + 145 * scale, hull_y + 34 * scale), radius=16, fill=c)
    draw.polygon([(x + 145 * scale, hull_y + 5), (x + 178 * scale, hull_y + 12), (x + 145 * scale, hull_y + 24)], fill=c)
    draw.ellipse((x + 150 * scale, y + 15 * scale, x + 170 * scale, y + 35 * scale), fill=c)


def draw_react_icon(draw, cx, cy, r=32):
    for angle in [0, 60, -60]:
        draw.ellipse((cx - r * 1.6, cy - r * 0.55, cx + r * 1.6, cy + r * 0.55), outline=REACT, width=4)
        # Pillow has no rotated ellipse here; add simple orbital lines for a compact icon.
        break
    draw.ellipse((cx - r * 1.6, cy - r * 0.55, cx + r * 1.6, cy + r * 0.55), outline=REACT, width=4)
    draw.line((cx - r * 1.25, cy - r, cx + r * 1.25, cy + r), fill=REACT, width=4)
    draw.line((cx - r * 1.25, cy + r, cx + r * 1.25, cy - r), fill=REACT, width=4)
    draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=REACT)


def draw_db_icon(draw, cx, cy, color=POSTGRES):
    draw.ellipse((cx - 36, cy - 26, cx + 36, cy + 10), fill=color)
    draw.rectangle((cx - 36, cy - 8, cx + 36, cy + 42), fill=color)
    draw.ellipse((cx - 36, cy + 24, cx + 36, cy + 60), fill=color)
    draw.ellipse((cx - 36, cy - 26, cx + 36, cy + 10), outline="#ffffff", width=3)
    center(draw, (cx, cy + 18), "DB", F_ICON, "#ffffff")


def icon_circle(draw, cx, cy, color, text):
    draw.ellipse((cx - 42, cy - 42, cx + 42, cy + 42), fill=color)
    center(draw, (cx, cy), text, F_ICON, "#ffffff")


def card(draw, box, title, body, color, icon_kind, icon_text=""):
    x1, y1, x2, y2 = box
    rounded(draw, box, "#ffffff")
    draw.rounded_rectangle((x1, y1, x2, y1 + 14), radius=8, fill=color)

    if icon_kind == "docker":
        draw_docker_logo(draw, x1 + 30, y1 + 35, 0.55)
    elif icon_kind == "react":
        draw_react_icon(draw, x1 + 70, y1 + 78, 30)
    elif icon_kind == "db":
        draw_db_icon(draw, x1 + 70, y1 + 55, color)
    else:
        icon_circle(draw, x1 + 70, y1 + 70, color, icon_text)

    draw.text((x1 + 130, y1 + 45), title, font=F_CARD, fill=INK)
    wrap(draw, x1 + 34, y1 + 128, body, F_BODY, x2 - x1 - 68)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((80, 55), "Architecture technique du projet CuraMedical", font=F_TITLE, fill=INK)
    draw.text((82, 125), "Structure des composants et liaisons principales entre les services.", font=F_SUB, fill=MUTED)

    # Utilisateurs hors Docker
    card(
        draw,
        (85, 410, 425, 650),
        "Utilisateurs",
        "Administrateur, médecin, secrétaire et patient.",
        "#0891b2",
        "circle",
        "U",
    )

    # Docker host
    docker_box = (520, 240, 1775, 1230)
    rounded(draw, docker_box, "#eef7ff", outline=DOCKER, width=4, radius=34)
    draw_docker_logo(draw, 555, 275, 0.75)
    draw.text((715, 292), "Docker Compose", font=F_SECTION, fill=DOCKER)
    draw.text((715, 328), "Conteneurs du projet CuraMedical", font=F_SMALL, fill=MUTED)

    frontend = (600, 455, 945, 710)
    backend = (1075, 415, 1495, 760)
    db = (1075, 865, 1495, 1110)
    ia = (600, 850, 945, 1110)
    n8n = (1555, 480, 1715, 680)

    card(draw, frontend, "Frontend", "React + Vite. Interface web et navigation par rôles.", REACT, "react")
    card(draw, backend, "Backend API", "Django REST Framework. Auth JWT, règles métier et orchestration des modules.", "#2563eb", "circle", "API")
    card(draw, db, "Base de données", "PostgreSQL. Données patients, RDV, consultations, prescriptions et audit.", POSTGRES, "db")
    card(draw, ia, "Service IA", "Flask + scikit-learn. Analyse des symptômes et suggestions diagnostiques.", AI, "circle", "IA")
    card(draw, n8n, "n8n", "Workflows et webhooks de notification.", N8N, "circle", "n8n")

    # External systems
    ext_box = (1870, 240, 2320, 1230)
    rounded(draw, ext_box, "#fff8f1", outline="#fed7aa", width=3, radius=34)
    draw.text((1910, 292), "Services externes", font=F_SECTION, fill="#9a3412")

    card(draw, (1930, 400, 2265, 575), "Twilio", "WhatsApp patient.", EXT, "circle", "WA")
    card(draw, (1930, 645, 2265, 820), "Groq / LLaMA", "Compréhension langage naturel.", "#7c3aed", "circle", "LLM")
    card(draw, (1930, 890, 2265, 1065), "SMTP + Jitsi", "Emails, PDF et téléconsultation.", "#f59e0b", "circle", "EXT")

    # Main links
    arrow(draw, (425, 530), (600, 580), "navigateur")
    arrow(draw, (945, 580), (1075, 580), "HTTP REST")
    arrow(draw, (1285, 760), (1285, 865), "ORM")
    arrow(draw, (1075, 660), (945, 935), "requête IA")
    arrow(draw, (945, 985), (1075, 700), "résultat IA")
    arrow(draw, (1495, 570), (1555, 570), "webhook")

    # External links
    arrow(draw, (1715, 580), (1930, 490), "notifications")
    arrow(draw, (1495, 520), (1930, 735), "LLM")
    arrow(draw, (1495, 690), (1930, 975), "email / visio")
    arrow(draw, (1715, 635), (1930, 520), "WhatsApp")

    # Small internal labels
    draw.text((605, 1185), "frontend:3000", font=F_SMALL, fill=DOCKER)
    draw.text((1078, 1185), "backend:8000  |  db:5432  |  ia-service:5000  |  n8n:5678", font=F_SMALL, fill=DOCKER)

    img.save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()
