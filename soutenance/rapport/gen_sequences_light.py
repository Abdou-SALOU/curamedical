# -*- coding: utf-8 -*-
"""
Regenere les 3 diagrammes de sequence du rapport CuraMedical sur FOND BLANC
(theme clair), avec un style unifie (meme moteur matplotlib que les diagrammes
IA et ordonnance d'origine). Recree aussi le diagramme d'authentification JWT
(qui n'avait pas de generateur) dans le meme style.

Sortie : soutenance/screenshots/curamedical-rapport/_peek/seq_light/
    - sequence_suggestion_ia.png        (Figure 2)
    - sequence_authentification.jpg     (Figure 3)
    - sequence_ordonnance_notification.png (Figure 4)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

# Palette theme CLAIR (fond blanc, professionnel, charte verte du rapport)
BG        = "#ffffff"
ACTOR_FC  = "#e9f1ff"
ACTOR_EC  = "#2f4b6e"
TXT       = "#16202b"
LIFELINE  = "#9aa7b4"
ARROW     = "#2b3a47"
NOTE_FC   = "#fff6d6"
NOTE_EC   = "#d9c069"
NOTE_TXT  = "#37320f"
LABEL_TXT = "#1c2730"
DIV_FC    = "#dfe7f0"
DIV_TXT   = "#52606d"


def render_sequence(participants, steps, out_path, title=None,
                    col_w=3.2, row_h=1.0, top_pad=1.6, bottom_pad=1.0):
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

    y = y_first
    for kind, i, j, text in steps:
        if kind == "divider":
            ax.add_patch(Rectangle((x_left, y - 0.18), x_right - x_left, 0.5,
                                   facecolor=DIV_FC, edgecolor="none", zorder=2))
            ax.text((x_left + x_right) / 2, y + 0.07, text, ha="center",
                    va="center", color=DIV_TXT, fontsize=8.2,
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
    "screenshots", "curamedical-rapport", "diagramme")
os.makedirs(OUT_DIR, exist_ok=True)

# Figure 2 : Aide au diagnostic IA
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

# Figure 3 : Authentification par jeton JWT (recree dans le meme style)
participants_jwt = [
    "Utilisateur\n(React)", "Zustand\nStore", "Backend\nDjango", "SimpleJWT",
]
steps_jwt = [
    ("msg",    0, 2, "POST /api/token/\n{ username, password }"),
    ("msg",    2, 3, "Vérification des identifiants"),
    ("return", 3, 2, "Access Token (8 h) + Refresh Token (7 j)"),
    ("return", 2, 0, "{ access, refresh }"),
    ("msg",    0, 1, "login(data) → stockage des jetons (localStorage)"),
    ("msg",    0, 2, "GET /api/users/me/\nHeader : Authorization: Bearer {access}"),
    ("return", 2, 0, "{ id, username, role, ... }"),
    ("msg",    0, 1, "Mise à jour de l'état utilisateur"),
    ("note",   0, 0, "Redirection vers le tableau de bord\ncorrespondant au rôle"),
]
render_sequence(
    participants_jwt, steps_jwt,
    os.path.join(OUT_DIR, "sequence_authentification.jpg"),
    title="Séquence — Authentification par jeton JWT", col_w=3.5, row_h=1.0)

# Figure 4 : Ordonnance -> PDF + notifications
participants_rx = [
    "Médecin\n(React)", "Django API\n(Serializer)", "ReportLab\n(pdf_generator)",
    "SMTP\nGmail", "n8n + Twilio\nWhatsApp", "Patient",
]
steps_rx = [
    ("msg",    0, 1, "POST /api/prescriptions/\n{ consultation, lignes:[...] }"),
    ("self",   1, 1, "Sauvegarde Prescription + lignes"),
    ("return", 1, 0, "HTTP 201 Created  (réponse immédiate)"),
    ("divider", None, None, "Thread asynchrone (daemon)  ·  send_notification()"),
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
    title="Séquence — Création d'ordonnance, PDF et notifications",
    col_w=3.5, row_h=1.05)

print("Termine.")
