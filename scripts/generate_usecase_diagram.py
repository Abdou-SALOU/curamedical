# -*- coding: utf-8 -*-
"""
Diagramme de cas d'utilisation CuraMedical — style StarUML.
Disposition en éventails verticaux (un acteur -> sa colonne de cas) pour des
liens bien espacés et lisibles. WhatsApp n'est PAS un acteur : c'est un canal
d'accès du patient, indiqué dans une note UML.

Sortie : screenshots/curamedical-rapport/diagramme/cas_utilisation.png
"""
import os
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Circle, Polygon, FancyArrowPatch

W, H = 1500, 1300
INK = "#2b2b2b"
GRID = "#dce4ec"
NOTE_FC = "#E9F7EF"
NOTE_EC = "#1f9d55"

fig, ax = plt.subplots(figsize=(15, 13), dpi=170)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis("off")

# ── Fond quadrillé ────────────────────────────────────────────────────────
for gx in range(0, W, 20):
    ax.plot([gx, gx], [0, H], color=GRID, lw=0.5, zorder=0)
for gy in range(0, H, 20):
    ax.plot([0, W], [gy, gy], color=GRID, lw=0.5, zorder=0)

# ── Boîte système (fill SOUS les liens) ───────────────────────────────────
ax.add_patch(Rectangle((200, 14), 1284, 1226, facecolor="white",
                        edgecolor=INK, lw=1.4, zorder=1))
ax.text(842, 34, "CuraMedical", ha="center", va="center", fontsize=15, color=INK, zorder=3)

UC = {}


# ── Helpers ───────────────────────────────────────────────────────────────
def actor(x, y, label):
    z = 5
    ax.add_patch(Circle((x, y), 12, facecolor="white", edgecolor=INK, lw=1.4, zorder=z))
    ax.plot([x, x], [y + 12, y + 46], color=INK, lw=1.4, zorder=z)
    ax.plot([x - 22, x + 22], [y + 25, y + 25], color=INK, lw=1.4, zorder=z)
    ax.plot([x, x - 16], [y + 46, y + 69], color=INK, lw=1.4, zorder=z)
    ax.plot([x, x + 16], [y + 46, y + 69], color=INK, lw=1.4, zorder=z)
    ax.text(x, y + 88, label, ha="center", va="center", fontsize=10.5, color=INK, zorder=z)


def usecase(name, cx, cy, w, label=None, h=48, fs=10.0):
    UC[name] = (cx, cy, w, h)
    ax.add_patch(Ellipse((cx, cy), w, h, facecolor="#FCFCFC", edgecolor=INK, lw=1.3, zorder=3))
    ax.text(cx, cy, label or name, ha="center", va="center", fontsize=fs,
            color=INK, zorder=4, linespacing=1.05)


def _edge(name, src):
    cx, cy, w, h = UC[name]
    a, b = w / 2, h / 2
    dx, dy = src[0] - cx, src[1] - cy
    denom = math.sqrt((dx / a) ** 2 + (dy / b) ** 2) or 1
    return (cx + dx / denom, cy + dy / denom)


def assoc(src, name):
    p = _edge(name, src)
    ax.plot([src[0], p[0]], [src[1], p[1]], color=INK, lw=1.5, zorder=2,
            solid_capstyle="round")


def generalization(p_from, p_tip, size=15):
    dx, dy = p_tip[0] - p_from[0], p_tip[1] - p_from[1]
    d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    px, py = -uy, ux
    base = (p_tip[0] - ux * size, p_tip[1] - uy * size)
    b1 = (base[0] + px * size * 0.55, base[1] + py * size * 0.55)
    b2 = (base[0] - px * size * 0.55, base[1] - py * size * 0.55)
    ax.plot([p_from[0], base[0]], [p_from[1], base[1]], color=INK, lw=1.5, zorder=2,
            solid_capstyle="round")
    ax.add_patch(Polygon([p_tip, b1, b2], closed=True, facecolor="white",
                         edgecolor=INK, lw=1.3, zorder=4))


def extend(name_from, name_to):
    a = _edge(name_from, UC[name_to][:2])
    b = _edge(name_to, UC[name_from][:2])
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="->", mutation_scale=15,
                                 color=INK, lw=1.1, linestyle=(0, (4, 3)), zorder=3))
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    ax.text(mx, my - 13, "«extend»", ha="center", va="center", fontsize=9.0, color=INK, zorder=4)


def note(x0, y0, w, h, text, anchor=None):
    f = 16
    x1, y1 = x0 + w, y0 + h
    main = [(x0, y0), (x1 - f, y0), (x1, y0 + f), (x1, y1), (x0, y1)]
    ax.add_patch(Polygon(main, closed=True, facecolor=NOTE_FC, edgecolor=NOTE_EC, lw=1.3, zorder=6))
    ax.add_patch(Polygon([(x1 - f, y0), (x1, y0 + f), (x1 - f, y0 + f)], closed=True,
                         facecolor="#d4efdd", edgecolor=NOTE_EC, lw=1.0, zorder=7))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center",
            fontsize=9.2, color="#1c5c38", zorder=8, linespacing=1.35)
    if anchor:
        ax.plot([anchor[0], x0 + 22], [anchor[1], y0 + 4], color=NOTE_EC, lw=1.1,
                linestyle=(0, (3, 3)), zorder=4)


# ── Acteurs (éventails verticaux) ─────────────────────────────────────────
actor(115, 155, "Medecin")
actor(35,  360, "Utilisateur")
actor(115, 495, "Secretaire")
actor(115, 720, "Administrateur")
actor(95,  1035, "Patient")

# ── Cas — Médecin ─────────────────────────────────────────────────────────
usecase("consultation", 535, 92, 548, "Réaliser une consultation Présentiel ou téléconsult", h=52, fs=10.0)
usecase("ia",          1015, 92, 150, "Solliciter IA")
usecase("ordonnance",   450, 165, 224, "Rédiger ordonnance")
usecase("pdf1",         730, 163, 152, "Génerer PDF")
usecase("compte_rendu", 455, 235, 234, "Génerer compte rendu")
usecase("pdf2",         730, 235, 152, "Génerer PDF")

# ── Cas — Utilisateur ─────────────────────────────────────────────────────
usecase("auth",         445, 360, 170, "S'authentifier")

# ── Cas — Secrétaire ──────────────────────────────────────────────────────
usecase("gerer_pat",    460, 458, 228, "Gérer dossier patients")
usecase("gerer_rdv",    462, 532, 178, "Gérer RDV")

# ── Cas — Administrateur ──────────────────────────────────────────────────
usecase("config",       460, 648, 208, "Configurer système")
usecase("gerer_users",  467, 722, 198, "Gérer utilisateurs")
usecase("audit",        465, 796, 218, "Consulter l'audit sécu")

# ── Cas partagé ───────────────────────────────────────────────────────────
usecase("teleconsult", 1060, 575, 220, "Participer Téléconsult")

# ── Cas — Patient (colonne verticale) ─────────────────────────────────────
usecase("inscrire",     500, 872, 138, "S'inscrire")
usecase("prendre_rdv",  522, 927, 184, "Prendre un RDV")
usecase("voir_rdv",     542, 982, 202, "Consulter ses RDV")
usecase("modifier_rdv", 560, 1037, 228, "Modifier / annuler un RDV", fs=9.4)
usecase("rx_pdf",       578, 1092, 244, "Recevoir ordonnance (PDF)", fs=9.3)
usecase("cr_pdf",       584, 1147, 252, "Recevoir compte-rendu (PDF)", fs=9.2)
usecase("symptomes_ia", 578, 1202, 244, "Analyser ses symptômes (IA)", fs=9.3)

# ── Associations ──────────────────────────────────────────────────────────
med = (140, 160)
for n in ("consultation", "ordonnance", "compte_rendu", "teleconsult"):
    assoc(med, n)

assoc((58, 364), "auth")

sec = (140, 500)
for n in ("gerer_pat", "gerer_rdv"):
    assoc(sec, n)

adm = (140, 725)
for n in ("config", "gerer_users", "audit"):
    assoc(adm, n)

pat = (118, 1045)
for n in ("inscrire", "prendre_rdv", "voir_rdv", "modifier_rdv",
          "rx_pdf", "cr_pdf", "symptomes_ia", "teleconsult"):
    assoc(pat, n)

# ── Généralisations → Utilisateur ─────────────────────────────────────────
generalization((108, 188), (56, 360))
generalization((104, 488), (64, 376))
generalization((104, 713), (70, 388))
generalization((58, 1020), (46, 394))

# ── «extend» ──────────────────────────────────────────────────────────────
extend("consultation", "ia")
extend("ordonnance", "pdf1")
extend("compte_rendu", "pdf2")

# ── Note : canal d'accès du patient ───────────────────────────────────────
note(6, 1150, 198, 78,
     "Le Patient accède au système\nvia l'application Web ou via\nWhatsApp (chatbot Twilio + IA).",
     anchor=(92, 1100))

# ── Export ────────────────────────────────────────────────────────────────
out = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "soutenance", "screenshots", "curamedical-rapport", "diagramme", "cas_utilisation.png")
plt.savefig(out, dpi=170, bbox_inches="tight", facecolor="white", pad_inches=0.18)
print(f"[OK] {out}")
