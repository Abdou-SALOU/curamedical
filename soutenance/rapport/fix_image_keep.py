# -*- coding: utf-8 -*-
"""
Affine le keep-with-next des images : une image ne doit etre rendue solidaire
du paragraphe suivant QUE si ce dernier est sa legende (Figure/Capture/Tableau).
Si l'image est suivie d'un TITRE ou de texte (cas des organigrammes de la
section "Environnement de developpement"), on retire le keep-with-next pour ne
pas creer de chaine qui pousse le titre suivant en bas de page (orphelin).
"""
import os, re
import docx
from docx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.join(HERE, "..", "screenshots", "curamedical-rapport",
                    "Rapport_CuraMedical.docx")

d = docx.Document(DOCX)
paras = d.paragraphs
cap = re.compile(r'^(Figure|Capture|Tableau)\s')

def has_img(p):
    return len(p._element.findall(".//" + qn("a:blip"))) > 0

set_true = set_false = 0
for i, p in enumerate(paras):
    if not has_img(p):
        continue
    nxt = paras[i + 1] if i + 1 < len(paras) else None
    if nxt is not None and cap.match(nxt.text.strip()):
        if not p.paragraph_format.keep_with_next:
            p.paragraph_format.keep_with_next = True
        set_true += 1
    else:
        if p.paragraph_format.keep_with_next:
            p.paragraph_format.keep_with_next = False
        set_false += 1
print(f"[img-keep] solidaire-legende={set_true}  detache(suivi titre/texte)={set_false}")
d.save(DOCX)
print("SAVED")
