# -*- coding: utf-8 -*-
"""
Phase 1 des corrections de mise en page :
  A. Anti-orphelin (keep-with-next) :
       - styles de titres (Heading 1/2/3) : solidaires du paragraphe suivant
       - tout paragraphe precedant une image : solidaire de l'image
       - tout paragraphe-image : solidaire de sa legende (paragraphe suivant)
  B. SOMMAIRE limite au corps : on borne le champ TOC du SOMMAIRE par un
     signet "CORPS" (Introduction -> fin des Annexes), via le commutateur \\b.
     La TABLE DES MATIERES (complete) n'est pas touchee.
"""
import os
import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.join(HERE, "..", "screenshots", "curamedical-rapport",
                    "Rapport_CuraMedical.docx")

d = docx.Document(DOCX)
paras = d.paragraphs

def has_img(p):
    return len(p._element.findall(".//" + qn("a:blip"))) > 0

# ---- A. keep-with-next ----------------------------------------------------
for sname in ("Heading 1", "Heading 2", "Heading 3"):
    try:
        pf = d.styles[sname].paragraph_format
        pf.keep_with_next = True
        pf.keep_together = True
    except KeyError:
        pass

n_before = n_img = 0
for i, p in enumerate(paras):
    nxt = paras[i + 1] if i + 1 < len(paras) else None
    if nxt is not None and has_img(nxt):
        p.paragraph_format.keep_with_next = True      # texte/titre -> image
        n_before += 1
    if has_img(p):
        p.paragraph_format.keep_with_next = True       # image -> legende
        n_img += 1
print(f"[keep] styles titres + {n_before} para avant-image + {n_img} para-image")

# ---- B. SOMMAIRE borne par signet CORPS -----------------------------------
# reperes : INTRODUCTION GENERALE (1er titre du corps) ... derniere annexe
def find_para(pred):
    for i, p in enumerate(paras):
        if pred(p):
            return i
    return None

i_intro = find_para(lambda p: p.style.name == "Heading 1"
                     and p.text.strip().upper().startswith("INTRODUCTION GÉNÉRALE"))
i_tdm = find_para(lambda p: p.style.name == "Heading 1"
                  and p.text.strip().upper().startswith("TABLE DES MATIÈRES"))
assert i_intro and i_tdm and i_intro < i_tdm, (i_intro, i_tdm)
# fin du corps = dernier paragraphe avant le saut de page qui precede la TDM
i_end = i_tdm - 1
print(f"[somm] corps: para {i_intro} (INTRODUCTION) -> {i_end} (avant TDM {i_tdm})")

# ids de signet existants pour eviter collision
existing = set()
for bm in d.element.findall(".//" + qn("w:bookmarkStart")):
    try:
        existing.add(int(bm.get(qn("w:id"))))
    except (TypeError, ValueError):
        pass
bid = max(existing) + 1 if existing else 9000
NAME = "CORPS"

# bookmarkStart au debut du paragraphe INTRODUCTION (apres pPr)
ps = paras[i_intro]._element
bs = OxmlElement("w:bookmarkStart")
bs.set(qn("w:id"), str(bid)); bs.set(qn("w:name"), NAME)
ppr = ps.find(qn("w:pPr"))
if ppr is not None:
    ppr.addnext(bs)
else:
    ps.insert(0, bs)
# bookmarkEnd a la fin du paragraphe de fin de corps
pe = paras[i_end]._element
be = OxmlElement("w:bookmarkEnd")
be.set(qn("w:id"), str(bid))
pe.append(be)

# modifier le code de champ du SOMMAIRE : ajouter  \b CORPS
somm = find_para(lambda p: p.style.name == "Heading 1"
                 and p.text.strip().upper() == "SOMMAIRE")
# le champ TOC se trouve juste apres (1er paragraphe toc), on cherche l'instrText
modified = False
for i in range(somm, somm + 6):
    for it in paras[i]._element.findall(".//" + qn("w:instrText")):
        if it.text and "TOC" in it.text and "\\b" not in it.text:
            it.text = it.text.rstrip() + " \\b " + NAME + " "
            modified = True
            print(f"[somm] champ TOC borne (para {i}) -> {it.text.strip()!r}")
            break
    if modified:
        break
assert modified, "champ TOC du SOMMAIRE introuvable"

d.save(DOCX)
print("SAVED")
