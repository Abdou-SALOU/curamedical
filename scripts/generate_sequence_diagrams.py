# -*- coding: utf-8 -*-
"""
Régénère les diagrammes de séquence CORRIGÉS pour le rapport CuraMedical,
dans le même style sombre que les originaux (Mermaid dark).

Corrige :
  • Diagramme IA   : port 5000 (et non 5555), payload { symptoms }
  • Diagramme PDF  : flux réel (Thread async, 1 PDF ordonnance,
                     Email SMTP + n8n + WhatsApp/Twilio)

Sortie : screenshots/curamedical-rapport/diagramme/
         - sequence_suggestion_ia_corrige.png
         - sequence_ordonnance_notification_corrige.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

# ── Palette thème sombre (proche Mermaid dark) ────────────────────────────
BG        = "#1a1b1e"
ACTOR_FC  = "#2c2f33"
ACTOR_EC  = "#8b95a1"
TXT       = "#e8eaed"
LIFELINE  = "#565c64"
ARROW     = "#d3d8de"
NOTE_FC   = "#4a4f57"
NOTE_EC   = "#6c727b"
NOTE_TXT  = "#f4f5f6"
LABEL_TXT = "#dfe3e8"
DIV_FC    = "#3a3f45"


def render_sequence(participants, steps, out_path, title=None,
                    col_w=3.2, row_h=1.0, top_pad=1.6, bottom_pad=1.0):
    """
    participants : liste de libellés (str), un par lifeline.
    steps : liste de tuples :
        ("msg",    i, j, "texte")      -> flèche pleine i->j
        ("return", i, j, "texte")      -> flèche pointillée i->j (retour)
        ("self",   i, i, "texte")      -> auto-message (boucle) sur i
        ("note",   i, j, "texte")      -> note (boîte) couvrant les colonnes i..j
        ("divider",None,None,"texte")  -> bandeau séparateur (ex. zone async)
    """
    n = len(participants)
    n_rows = len(steps)

    fig_w = max(8.0, n * col_w + 1.5)
    fig_h = top_pad + bottom_pad + n_rows * row_h + 2.4
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=200)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    X0, DX = 1.2, col_w
    xs = [X0 + i * DX for i in range(n)]
    x_left, x_right = xs[0] - DX * 0.55, xs[-1] + DX * 0.55

    y_head = top_pad + n_rows * row_h + 1.0
    y_first = y_head - 1.4
    y_foot = bottom_pad - 0.2

    ax.set_xlim(x_left - 0.6, x_right + 0.6)
    ax.set_ylim(y_foot - 0.9, y_head + 1.6)
    ax.axis("off")

    if title:
        ax.text((x_left + x_right) / 2, y_head + 1.15, title, ha="center",
                va="center", color=TXT, fontsize=13.5, fontweight="bold")

    # Lifelines + boîtes acteurs (haut et bas)
    box_w = DX * 0.82
    for i, name in enumerate(participants):
        ax.plot([xs[i], xs[i]], [y_foot + 0.55, y_head - 0.35],
                color=LIFELINE, lw=1.3, zorder=1)
        for yc in (y_head, y_foot):
            b = FancyBboxPatch(
                (xs[i] - box_w / 2, yc - 0.35), box_w, 0.7,
                boxstyle="round,pad=0.02,rounding_size=0.06",
                linewidth=1.4, edgecolor=ACTOR_EC, facecolor=ACTOR_FC, zorder=4)
            ax.add_patch(b)
            ax.text(xs[i], yc, name, ha="center", va="center", color=TXT,
                    fontsize=8.6, fontweight="bold", zorder=5, linespacing=1.1)

    # Étapes
    y = y_first
    for kind, i, j, text in steps:
        if kind == "divider":
            ax.add_patch(Rectangle((x_left, y - 0.18), x_right - x_left, 0.5,
                                   facecolor=DIV_FC, edgecolor="none", zorder=2))
            ax.text((x_left + x_right) / 2, y + 0.07, text, ha="center",
                    va="center", color="#aeb6bf", fontsize=8.2,
                    fontstyle="italic", zorder=3)
            y -= row_h
            continue

        if kind == "note":
            xa, xb = xs[i], xs[j]
            nx0 = min(xa, xb) - box_w * 0.55
            nx1 = max(xa, xb) + box_w * 0.55
            nb = FancyBboxPatch(
                (nx0, y - 0.30), nx1 - nx0, 0.62,
                boxstyle="round,pad=0.02,rounding_size=0.05",
                linewidth=1.2, edgecolor=NOTE_EC, facecolor=NOTE_FC, zorder=4)
            ax.add_patch(nb)
            ax.text((nx0 + nx1) / 2, y + 0.01, text, ha="center", va="center",
                    color=NOTE_TXT, fontsize=8.0, zorder=5, linespacing=1.15)
            y -= row_h
            continue

        if kind == "self":
            x = xs[i]
            loop_w = DX * 0.42
            ax.add_patch(FancyArrowPatch(
                (x, y), (x + loop_w, y), arrowstyle="-",
                connectionstyle="arc3,rad=0", color=ARROW, lw=1.4, zorder=3))
            ax.add_patch(FancyArrowPatch(
                (x + loop_w, y), (x + loop_w, y - 0.28), arrowstyle="-",
                color=ARROW, lw=1.4, zorder=3))
            ax.add_patch(FancyArrowPatch(
                (x + loop_w, y - 0.28), (x + 0.05, y - 0.28), arrowstyle="-|>",
                mutation_scale=12, color=ARROW, lw=1.4, zorder=3))
            ax.text(x + loop_w + 0.25, y - 0.14, text, ha="left", va="center",
                    color=LABEL_TXT, fontsize=8.0, zorder=5, linespacing=1.15)
            y -= row_h
            continue

        # msg / return
        xa, xb = xs[i], xs[j]
        dashed = kind == "return"
        ls = (0, (4, 3)) if dashed else "-"
        ax.add_patch(FancyArrowPatch(
            (xa, y), (xb, y), arrowstyle="-|>", mutation_scale=13,
            color=ARROW, lw=1.5, linestyle=ls, zorder=3))
        ax.text((xa + xb) / 2, y + 0.20, text, ha="center", va="bottom",
                color=LABEL_TXT, fontsize=8.0, zorder=5, linespacing=1.2)
        y -= row_h

    plt.savefig(out_path, dpi=200, bbox_inches="tight",
                facecolor=BG, pad_inches=0.25)
    plt.close(fig)
    print(f"[OK] {out_path}")


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "soutenance", "screenshots", "curamedical-rapport", "diagramme")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Diagramme 3 corrigé : Suggestion IA ───────────────────────────────────
participants_ia = [
    "Médecin\n(React)", "Backend\nDjango", "Microservice\nFlask (port 5000)",
    "Modèle\nRandom Forest",
]
steps_ia = [
    ("msg",    0, 1, "POST /api/consultations/suggestions-ia/\n{ symptomes:[...], age, genre, tension }"),
    ("msg",    1, 2, "POST http://ia-service:5000/predict\n{ symptoms:[...] }"),
    ("msg",    2, 3, "model.predict_proba(vecteur symptômes)"),
    ("return", 3, 2, "Probabilités par pathologie"),
    ("note",   2, 2, "Top 3 + traduction EN→FR\n+ niveau de risque"),
    ("return", 2, 1, "{ suggestions: [top 3 + scores] }"),
    ("return", 1, 0, "{ disponible: true, suggestions: [...] }"),
    ("note",   0, 0, "Affichage des 3 pathologies\navec barres de progression"),
]
render_sequence(
    participants_ia, steps_ia,
    os.path.join(OUT_DIR, "sequence_suggestion_ia.png"),
    title="Séquence — Aide au diagnostic IA", col_w=3.6)

# ── Diagramme 4 corrigé : Ordonnance → PDF + notifications ─────────────────
participants_rx = [
    "Médecin\n(React)", "Django API\n(Serializer)", "ReportLab\n(pdf_generator)",
    "SMTP\nGmail", "n8n + Twilio\nWhatsApp", "Patient",
]
steps_rx = [
    ("msg",    0, 1, "POST /api/prescriptions/\n{ consultation, lignes:[...] }"),
    ("self",   1, 1, "Sauvegarde Prescription + lignes"),
    ("return", 1, 0, "HTTP 201 Created  (réponse immédiate)"),
    ("divider", None, None, "Thread asynchrone (daemon)  —  send_notification()"),
    ("msg",    1, 2, "generate_prescription_pdf(prescription)"),
    ("return", 2, 1, "PDF ordonnance  (1 seul fichier)"),
    ("msg",    1, 3, "EmailMessage + pièce jointe ordonnance_{id}.pdf"),
    ("return", 3, 5, "Email reçu  (1 PDF : ordonnance)"),
    ("msg",    1, 4, "send_to_n8n_automation() + WhatsAppService.send_pdf()"),
    ("return", 4, 5, "Notification WhatsApp / n8n (lien PDF)"),
]
render_sequence(
    participants_rx, steps_rx,
    os.path.join(OUT_DIR, "sequence_ordonnance_notification.png"),
    title="Séquence — Création d'ordonnance, PDF & notifications",
    col_w=3.5, row_h=1.05)
