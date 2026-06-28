# -*- coding: utf-8 -*-
"""
Génère le diagramme d'architecture globale du projet CuraMedical (PNG).
Usage : python scripts/generate_architecture.py
Sortie : Diagramme_uml/architecture_globale.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

# ── Palette ───────────────────────────────────────────────────────────────
C_BG        = "#f5f7fa"
C_USER      = "#34495e"
C_FRONT     = "#2c7be5"   # bleu React
C_BACK      = "#0b8457"   # vert Django
C_IA        = "#8e44ad"   # violet IA
C_N8N       = "#e8590c"   # orange n8n
C_DB        = "#1f6feb"   # bleu DB
C_EXT       = "#c0392b"   # rouge services externes
C_BORDER    = "#ffffff"
WHITE       = "#ffffff"
INK         = "#1b2733"

fig, ax = plt.subplots(figsize=(17, 12), dpi=200)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")
fig.patch.set_facecolor(C_BG)
ax.set_facecolor(C_BG)


def box(x, y, w, h, color, title, lines=None, title_size=12, body_size=8.5,
        text_color=WHITE, round_pad=0.018, alpha=1.0):
    """Boîte arrondie avec titre + lignes optionnelles."""
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.2,rounding_size={round_pad*100}",
        linewidth=1.4, edgecolor=C_BORDER, facecolor=color, alpha=alpha,
        mutation_aspect=0.55, zorder=3,
    )
    ax.add_patch(p)
    if lines:
        ax.text(x + w / 2, y + h - h * 0.20, title, ha="center", va="center",
                fontsize=title_size, fontweight="bold", color=text_color, zorder=4)
        ax.text(x + w / 2, y + h * 0.42, "\n".join(lines), ha="center", va="center",
                fontsize=body_size, color=text_color, zorder=4, linespacing=1.5)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=title_size, fontweight="bold", color=text_color, zorder=4)


def arrow(p1, p2, color="#5b6b7b", style="-|>", lw=1.8, ls="-", rad=0.0,
          label=None, label_pos=0.5, label_dy=1.4, fontsize=7.5):
    a = FancyArrowPatch(
        p1, p2, arrowstyle=style, mutation_scale=14,
        linewidth=lw, color=color, linestyle=ls,
        connectionstyle=f"arc3,rad={rad}", zorder=2,
    )
    ax.add_patch(a)
    if label:
        mx = p1[0] + (p2[0] - p1[0]) * label_pos
        my = p1[1] + (p2[1] - p1[1]) * label_pos + label_dy
        ax.text(mx, my, label, ha="center", va="center", fontsize=fontsize,
                color="#33414f", zorder=5,
                bbox=dict(boxstyle="round,pad=0.18", fc="#ffffff", ec="#d0d7de", lw=0.6))


# ── Titre ─────────────────────────────────────────────────────────────────
ax.text(50, 97.5, "CuraMedical — Architecture Globale du Système",
        ha="center", va="center", fontsize=20, fontweight="bold", color=INK)
ax.text(50, 94.3, "Gestion intelligente de cabinet médical · Microservices conteneurisés (Docker Compose)",
        ha="center", va="center", fontsize=10.5, color="#54626f", style="italic")

# ── Cadre Docker network ──────────────────────────────────────────────────
net = FancyBboxPatch((3, 5), 94, 80,
                     boxstyle="round,pad=0.2,rounding_size=1.2",
                     linewidth=1.6, edgecolor="#9aa7b4", facecolor="#ffffff",
                     linestyle=(0, (6, 4)), alpha=0.55, zorder=1)
ax.add_patch(net)
ax.text(6.2, 83, "Réseau Docker  ·  curamedical_network", ha="left", va="center",
        fontsize=9.5, color="#5b6b7b", fontweight="bold", zorder=2)

# ── 1. Utilisateurs ───────────────────────────────────────────────────────
ax.text(50, 89.6, "ACTEURS", ha="center", fontsize=9, color="#7a8794", fontweight="bold")
users = [
    ("Administrateur", 13.5),
    ("Médecin", 31.0),
    ("Secrétaire", 48.5),
    ("Patient (Web)", 66.0),
]
for label, ux in users:
    box(ux, 85.5, 16, 3.4, C_USER, label, title_size=9.5)
box(83.5, 85.5, 13, 3.4, "#128c7e", "Patient WhatsApp", title_size=8.8)

# ── 2. Frontend ───────────────────────────────────────────────────────────
box(8, 67.5, 60, 13.5, C_FRONT,
    "FRONTEND  ·  React 19 + Vite + Tailwind   (port 3000)",
    [
        "Pages : Login · Dashboard · Patients · RDV · Consultations · Ordonnances · Admin",
        "Composants : Navbar · Layout · ChatbotWidget · PrivateRoute (RBAC) · Toasts",
        "État : Zustand (auth, toasts)   ·   Données : React Query + Axios",
        "FullCalendar (planning)  ·  Recharts (stats)  ·  Jitsi (téléconsultation)",
    ],
    title_size=11.5, body_size=8.3)

# ── 3. Backend ────────────────────────────────────────────────────────────
box(8, 44, 60, 18.5, C_BACK,
    "BACKEND  ·  Django 4.2 + Django REST Framework   (port 8000)",
    [
        "Authentification : JWT (SimpleJWT)  ·  RBAC par rôle  ·  Journal d'audit",
        "",
        "Apps :  users · patients · appointments · consultations",
        "             prescriptions · chat · whatsapp · common",
        "",
        "Génération PDF (ordonnances) · Rapports consultation · Signals Django",
        "Documentation API : drf-spectacular (Swagger / OpenAPI)",
    ],
    title_size=11.5, body_size=8.4)

# ── 4. Microservice IA ────────────────────────────────────────────────────
box(72, 44, 24, 18.5, C_IA,
    "MICROSERVICE IA",
    [
        "Flask  (port 5000)",
        "",
        "•  Random Forest",
        "    → diagnostic /predict",
        "•  Classif. d'intention (SVM)",
        "•  Traduction FR <-> EN",
        "•  Client Groq (LLM)",
    ],
    title_size=11, body_size=8.2)

# ── 5. n8n ────────────────────────────────────────────────────────────────
box(72, 26, 24, 14.5, C_N8N,
    "AUTOMATISATION  ·  n8n",
    [
        "Orchestration (port 5678)",
        "",
        "Webhook ordonnances",
        "Notifications WhatsApp",
        "Workflows événementiels",
    ],
    title_size=10.5, body_size=8.2)

# ── 6. Base de données ────────────────────────────────────────────────────
box(8, 26, 26, 14.5, C_DB,
    "BASE DE DONNÉES",
    [
        "PostgreSQL 15",
        "",
        "Volume persistant Docker",
        "(postgres_data)",
        "Utilisateurs · Patients · RDV",
        "Consultations · Ordonnances",
    ],
    title_size=11, body_size=8.2)

# ── 7. Services externes ──────────────────────────────────────────────────
ax.text(50, 22.5, "SERVICES EXTERNES (Cloud / SaaS)", ha="center", fontsize=9,
        color="#7a8794", fontweight="bold")
ext = [
    ("Groq API\n(LLM llama-3.3-70b)", 37.5),
    ("Twilio\n(WhatsApp)", 56.0),
    ("SMTP Email\n(Gmail)", 71.5),
]
for label, ux in ext:
    box(ux, 9.5, 14.5, 8.5, C_EXT, label, title_size=9.0)
box(8, 9.5, 18, 8.5, "#525f6b", "Jitsi Meet\n(Vidéo / Téléconsult.)", title_size=9.0)

# ── Flèches : flux de données ─────────────────────────────────────────────
# Utilisateurs → Frontend
for ux in [21.5, 39, 56.5]:
    arrow((ux, 85.4), (ux, 81.2), color="#7a8794", lw=1.6)
arrow((74, 85.4), (74, 62.6), color="#128c7e", lw=1.6, rad=-0.05,
      label="webhook entrant", label_pos=0.15)

# Frontend ↔ Backend
arrow((35, 67.4), (35, 62.6), color="#33414f", lw=2.2,
      label="API REST / JSON · JWT", label_pos=0.5, label_dy=0.0)
arrow((42, 62.6), (42, 67.4), color="#33414f", lw=1.6, rad=0.0)

# Frontend → Jitsi
arrow((14, 67.4), (14, 18.2), color="#525f6b", lw=1.5, ls=(0, (4, 3)), rad=0.18,
      label="WebRTC vidéo", label_pos=0.06)

# Backend → DB
arrow((24, 44), (24, 40.6), color="#1f6feb", lw=2.2,
      label="ORM (psql)", label_pos=0.5, label_dy=0.0)

# Backend ↔ IA
arrow((68, 55), (72, 55), color="#8e44ad", lw=2.2,
      label="HTTP /predict /brain", label_pos=0.5, label_dy=1.5)
arrow((72, 51), (68, 51), color="#8e44ad", lw=1.5)

# Backend → n8n
arrow((68, 47), (72, 34), color="#e8590c", lw=1.8, rad=-0.12,
      label="webhook", label_pos=0.5)

# IA → Groq
arrow((84, 44), (44.7, 18.1), color="#c0392b", lw=1.6, ls=(0, (4, 3)), rad=0.1,
      label="appel LLM", label_pos=0.12)

# n8n → Twilio
arrow((84, 26), (63.2, 18.1), color="#e8590c", lw=1.6, rad=0.12,
      label="envoi WhatsApp", label_pos=0.3)

# Backend → SMTP
arrow((60, 44), (78.7, 18.1), color="#c0392b", lw=1.5, ls=(0, (4, 3)), rad=-0.1,
      label="emails", label_pos=0.2)

# ── Légende ───────────────────────────────────────────────────────────────
legend_items = [
    (C_FRONT, "Frontend (React)"),
    (C_BACK,  "Backend (Django/DRF)"),
    (C_IA,    "IA (Flask/ML/LLM)"),
    (C_N8N,   "Automatisation (n8n)"),
    (C_DB,    "Base de données"),
    (C_EXT,   "Services externes"),
]
handles = [Line2D([0], [0], marker="s", color="none", markerfacecolor=c,
                  markersize=11, label=t) for c, t in legend_items]
leg = ax.legend(handles=handles, loc="lower center", ncol=6, frameon=True,
                bbox_to_anchor=(0.5, -0.02), fontsize=8.5, handletextpad=0.4,
                columnspacing=1.1, borderpad=0.7)
leg.get_frame().set_edgecolor("#d0d7de")
leg.get_frame().set_facecolor("#ffffff")

# ── Export ────────────────────────────────────────────────────────────────
out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "soutenance", "screenshots", "curamedical-rapport", "diagramme")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "architecture_globale.png")
plt.savefig(out_path, dpi=200, bbox_inches="tight", facecolor=C_BG, pad_inches=0.3)
print(f"[OK] Diagramme généré : {out_path}")
