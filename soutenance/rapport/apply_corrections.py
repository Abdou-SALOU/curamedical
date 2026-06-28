# -*- coding: utf-8 -*-
"""
Applique les corrections finales au rapport (python-docx) :
  1. Remplace les 3 diagrammes de sequence par leurs versions FOND BLANC.
  2. Remplace les tirets d'incise (em dash) par des virgules / parentheses
     dans les paragraphes de prose.
  3. Corrige le texte d'intro de la section II.4 (second diagramme supprime).
  4. Corrige les typos de la legende de la Figure 9.
  5. Ajoute une description sous la figure du workflow n8n.
Ne touche PAS aux champs SEQ / TDM (mis a jour ensuite sous Word).
"""
import os, io
import docx
from docx.shared import Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.join(HERE, "..", "screenshots", "curamedical-rapport",
                    "Rapport_CuraMedical.docx")
SEQDIR = os.path.join(HERE, "..", "screenshots", "curamedical-rapport",
                      "_peek", "seq_light")

EM = "—"          # em dash
SP_EM_SP = " " + EM + " "

d = docx.Document(DOCX)
paras = d.paragraphs

# ---------------------------------------------------------------- 1. IMAGES
# (rId -> nouveau fichier) ; largeur conservee, hauteur = largeur * ratio
new_imgs = {
    "rId11": os.path.join(SEQDIR, "sequence_suggestion_ia.png"),        # Fig 2
    "rId12": os.path.join(SEQDIR, "sequence_authentification.jpg"),     # Fig 3
    "rId13": os.path.join(SEQDIR, "sequence_ordonnance_notification.png"),  # Fig 4
}

def shape_for_rid(rid):
    for sh in d.inline_shapes:
        blips = sh._inline.findall(".//" + qn("a:blip"))
        if blips and blips[0].get(qn("r:embed")) == rid:
            return sh
    return None

for rid, path in new_imgs.items():
    data = open(path, "rb").read()
    part = d.part.related_parts[rid]
    part._blob = data
    w, h = Image.open(io.BytesIO(data)).size
    aspect = h / w
    sh = shape_for_rid(rid)
    cur_w = sh.width
    sh.width = cur_w
    sh.height = Emu(int(round(cur_w * aspect)))
    print(f"[img] {rid} -> {os.path.basename(path)}  w={cur_w/360000:.2f}cm "
          f"h={sh.height/360000:.2f}cm")

# ---------------------------------------------------------------- 2. TIRETS
COMMA = [212, 222, 354, 382, 486, 537, 577, 580, 583, 609]
PARENS = [364, 387, 410, 605, 615]

def fix_comma(p):
    n = 0
    for r in p.runs:
        if EM in r.text:
            new = r.text.replace(SP_EM_SP, ", ")
            if new != r.text:
                n += r.text.count(SP_EM_SP)
                r.text = new
    return n

def fix_parens(p):
    dash_runs = [r for r in p.runs if EM in r.text]
    assert len(dash_runs) == 2, f"attendu 2 tirets, trouve {len(dash_runs)}"
    dash_runs[0].text = dash_runs[0].text.replace(SP_EM_SP, " (", 1)
    dash_runs[1].text = dash_runs[1].text.replace(SP_EM_SP, ") ", 1)
    return 2

total = 0
for i in COMMA:
    c = fix_comma(paras[i])
    assert c > 0, f"para {i}: aucun tiret remplace"
    total += c
for i in PARENS:
    total += fix_parens(paras[i])
print(f"[tirets] {total} tirets convertis sur {len(COMMA)+len(PARENS)} paragraphes")

# ---------------------------------------------------------------- 3. INTRO II.4
p301 = paras[301]
assert "second diagramme" in p301.text, "phrase 'second diagramme' introuvable"
new301 = ("Le diagramme d'activité formalise le parcours complet du patient, "
          "depuis son inscription jusqu'à la réception de ses documents, en "
          "distinguant les branches « téléconsultation » et "
          "« présentiel ».")
p301.runs[0].text = new301
for r in p301.runs[1:]:
    r.text = ""
print("[intro] phrase 'second diagramme' supprimee")

# ---------------------------------------------------------------- 4. TYPOS FIG 9
p389 = paras[389]
fixed = []
for r in p389.runs:
    if "diffuses" in r.text:
        r.text = r.text.replace("diffuses", "diffusés"); fixed.append("diffuses")
    if "l'editeur" in r.text:
        r.text = r.text.replace("l'editeur", "l'éditeur"); fixed.append("l'editeur")
assert "diffuses" in fixed and "l'editeur" in fixed, f"typos Fig9 non trouvees: {fixed}"
print("[fig9] typos corrigees:", fixed)

# ---------------------------------------------------------------- 5. DESC n8n
# inserer apres la legende Fig 9 (p389), avant le titre V.2 (p390)
p390 = paras[390]
assert p390.style.name.startswith("Heading"), f"p390 inattendu: {p390.style.name}"
desc = ("La capture ci-dessus présente le workflow tel qu'il est assemblé dans "
        "l'éditeur visuel de n8n. La chaîne débute par un nœud déclencheur "
        "« Webhook » qui reçoit l'événement émis par le backend, puis "
        "enchaîne les nœuds de mise en forme et de diffusion du message : un envoi par "
        "e-mail, avec le document PDF en pièce jointe le cas échéant, et un appel à "
        "la passerelle WhatsApp via Twilio. Trois scénarios sont ainsi pris en charge : le "
        "rappel adressé la veille d'un rendez-vous, la transmission des comptes rendus et des "
        "ordonnances à l'issue d'une consultation, et le message de bienvenue envoyé à "
        "chaque nouveau patient. Chaque branche peut être ajoutée ou ajustée directement "
        "dans cette interface, sans modification du code applicatif.")
newp = p390.insert_paragraph_before(desc, style="Normal")
newp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
print("[n8n] description inseree apres la legende Fig 9")

# ---------------------------------------------------------------- SAVE
d.save(DOCX)
print("SAVED:", os.path.abspath(DOCX))
