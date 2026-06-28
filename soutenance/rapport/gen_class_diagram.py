# -*- coding: utf-8 -*-
"""Génère un diagramme de classes UML fidèle au code de CuraMedical
(Pillow). Entités et cardinalités alignées sur les modèles Django réels :
Utilisateur, Patient, RendezVous, Consultation, Prescription, LignePrescription.
Pas de classe « Examen » (non implémentée)."""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "..", "screenshots",
                   "curamedical-rapport", "diagramme", "classe_curamedical.png")
OUT = os.path.abspath(OUT)

S = 2  # super-échantillonnage (rendu net puis réduction)
W, H = 1400 * S, 900 * S

BORDER = (51, 65, 85)        # #334155
HEADER = (231, 244, 236)     # #E7F4EC vert clair
TITLECOL = (14, 90, 57)      # #0E5A39 vert foncé
INK = (31, 42, 51)
LINE = (71, 85, 105)
CARD = (40, 60, 50)
NOTE_BG = (255, 249, 230)
NOTE_BD = (212, 197, 120)


def font(sz, bold=False):
    paths = ([r"C:\Windows\Fonts\segoeuib.ttf"] if bold else [r"C:\Windows\Fonts\segoeui.ttf"])
    paths += [r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz * S)
            except Exception:
                pass
    return ImageFont.load_default()


F_TITLE = font(19, bold=True)
F_ATTR = font(15)
F_CARD = font(14, bold=True)
F_NOTE = font(14)

img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)


def tw(txt, f):
    b = d.textbbox((0, 0), txt, font=f)
    return b[2] - b[0], b[3] - b[1]


class Box:
    def __init__(self, name, attrs, methods, x, y, w):
        self.name = name
        self.attrs = attrs
        self.methods = methods
        self.x, self.y, self.w = x * S, y * S, w * S
        pad = 8 * S
        lh = int(22 * S)
        self.lh = lh
        self.pad = pad
        self.hh = int(34 * S)  # header height
        n = max(1, len(attrs))
        m = max(1, len(methods))
        self.ah = n * lh + pad
        self.mh = m * lh + pad
        self.h = self.hh + self.ah + self.mh

    def draw(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        # corps
        d.rectangle([x, y, x + w, y + h], fill="white", outline=BORDER, width=2 * S)
        # header
        d.rectangle([x, y, x + w, y + self.hh], fill=HEADER, outline=BORDER, width=2 * S)
        twn, thn = tw(self.name, F_TITLE)
        d.text((x + (w - twn) / 2, y + (self.hh - thn) / 2 - 2 * S), self.name, font=F_TITLE, fill=TITLECOL)
        # attributs
        ay = y + self.hh
        d.line([x, ay, x + w, ay], fill=BORDER, width=2 * S)
        cy = ay + self.pad // 2
        for a in self.attrs:
            d.text((x + self.pad, cy), a, font=F_ATTR, fill=INK)
            cy += self.lh
        # méthodes
        my = ay + self.ah
        d.line([x, my, x + w, my], fill=BORDER, width=2 * S)
        cy = my + self.pad // 2
        for mth in self.methods:
            d.text((x + self.pad, cy), mth, font=F_ATTR, fill=INK)
            cy += self.lh

    # points d'ancrage
    def L(self): return (self.x, self.y + self.h // 2)
    def R(self): return (self.x + self.w, self.y + self.h // 2)
    def T(self): return (self.x + self.w // 2, self.y)
    def B(self): return (self.x + self.w // 2, self.y + self.h)


# ── Définition des classes ──────────────────────────────────────────────────
patient = Box("Patient",
    ["+ id : int", "+ nom : string", "+ prenom : string", "+ date_naissance : date",
     "+ sexe : enum", "+ telephone : string", "+ groupe_sanguin : enum",
     "+ allergies : text", "+ antecedents : text"],
    ["+ age()", "+ archiver()"], x=40, y=60, w=320)

utilisateur = Box("Utilisateur",
    ["+ id : int", "+ username : string", "+ nom : string", "+ prenom : string",
     "+ role : enum", "+ specialite : enum"],
    ["+ authentifier()"], x=40, y=560, w=320)

rdv = Box("RendezVous",
    ["+ id : int", "+ date_heure : datetime", "+ duree : int", "+ motif : string",
     "+ statut : enum", "+ type_consultation : enum", "+ lien_visio : string"],
    ["+ verifierConflit()"], x=560, y=60, w=330)

consultation = Box("Consultation",
    ["+ id : int", "+ symptomes : json", "+ examen_clinique : text",
     "+ diagnostic : text", "+ notes : text", "+ suggestions_ia : json",
     "+ ia_utilisee : bool"],
    ["+ solliciterIA()"], x=560, y=500, w=340)

ordonnance = Box("Ordonnance",
    ["+ id : int", "+ notes_generales : text", "+ cree_le : datetime"],
    ["+ genererPDF()"], x=1020, y=520, w=330)

ligne = Box("LignePrescription",
    ["+ id : int", "+ medicament : string", "+ dosage : string", "+ unite : enum",
     "+ frequence : string", "+ duree : string", "+ instructions : text"],
    ["+ __str__()"], x=1020, y=80, w=340)

boxes = [patient, utilisateur, rdv, consultation, ordonnance, ligne]


# ── Connecteurs ─────────────────────────────────────────────────────────────
def diamond(pt, dirxy, size=9):
    """Losange plein (composition) au point pt, orienté selon dirxy (unitaire)."""
    import math
    dx, dy = dirxy
    n = math.hypot(dx, dy) or 1
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    s = size * S
    cx, cy = pt[0] + dx * s, pt[1] + dy * s
    pts = [(pt[0], pt[1]),
           (cx + px * s * 0.6, cy + py * s * 0.6),
           (pt[0] + dx * 2 * s, pt[1] + dy * 2 * s),
           (cx - px * s * 0.6, cy - py * s * 0.6)]
    d.polygon(pts, fill=LINE, outline=LINE)


def card(pt, txt, off=(0, 0)):
    w, h = tw(txt, F_CARD)
    d.text((pt[0] + off[0] * S - w / 2, pt[1] + off[1] * S - h / 2), txt, font=F_CARD, fill=CARD)


def assoc(p1, p2, c1, c2, dia=None, label=None):
    d.line([p1, p2], fill=LINE, width=2 * S)
    card(p1, c1, off=_near(p1, p2, 16))
    card(p2, c2, off=_near(p2, p1, 16))
    if dia == 1:
        diamond(p1, (p2[0] - p1[0], p2[1] - p1[1]))
    elif dia == 2:
        diamond(p2, (p1[0] - p2[0], p1[1] - p2[1]))
    if label:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        w, h = tw(label, F_CARD)
        d.text((mx - w / 2, my - h - 4 * S), label, font=F_CARD, fill=(120, 80, 30))


def _near(a, b, dpx):
    """Décalage (en px non-scalés) pour placer la cardinalité près de a, vers b."""
    import math
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1
    return (dx / n * dpx / S, dy / n * dpx / S + (-10 if abs(dx) > abs(dy) else 0))


# dessiner les boîtes
for bx in boxes:
    bx.draw()

# associations (cardinalités fidèles au code)
# Utilisateur 1 — 0..1 Patient (compte patient, OneToOne)
assoc(patient.B(), utilisateur.T(), "0..1", "1", dia=None)
# Patient 1 — 0..* RendezVous (composition)
assoc(patient.R(), rdv.L(), "1", "0..*", dia=1)
# RendezVous 1 — 0..1 Consultation
assoc(rdv.B(), consultation.T(), "1", "0..1", dia=None)
# Consultation 1 — 0..1 Ordonnance (composition)
assoc(consultation.R(), ordonnance.L(), "1", "0..1", dia=1)
# Ordonnance 1 — 1..* LignePrescription (composition)
assoc(ordonnance.T(), ligne.B(), "1", "1..*", dia=1)
# Utilisateur (médecin) 1 — 0..* Consultation
assoc(utilisateur.R(), consultation.L(), "1", "0..*", label="médecin")

# ── Note explicative ─────────────────────────────────────────────────────────
note_lines = [
    "Note : le médecin est un Utilisateur (role = medecin).",
    "Il est également lié aux RendezVous, Consultations et",
    "Ordonnances. La Consultation référence aussi directement",
    "le Patient. Tous les identifiants sont des clés primaires.",
]
nx, ny = 980 * S, 690 * S
nw = 400 * S
nh = (len(note_lines) * int(20 * S)) + 18 * S
fold = 16 * S
d.polygon([(nx, ny), (nx + nw - fold, ny), (nx + nw, ny + fold),
           (nx + nw, ny + nh), (nx, ny + nh)], fill=NOTE_BG, outline=NOTE_BD)
d.line([(nx + nw - fold, ny), (nx + nw - fold, ny + fold), (nx + nw, ny + fold)], fill=NOTE_BD, width=S)
cy = ny + 9 * S
for ln in note_lines:
    d.text((nx + 10 * S, cy), ln, font=F_NOTE, fill=(90, 70, 20))
    cy += int(20 * S)

# ── Titre du diagramme ────────────────────────────────────────────────────────
ttl = "Diagramme de classes — CuraMedical"
w, h = tw(ttl, F_TITLE)
d.text(((W - w) / 2, 16 * S), ttl, font=F_TITLE, fill=TITLECOL)

# réduction (anti-aliasing)
img = img.resize((W // S, H // S), Image.LANCZOS)
img.save(OUT, "PNG")
print("OK ->", OUT)
