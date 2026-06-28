# -*- coding: utf-8 -*-
"""
Corrige l'exces de keep-with-next : une legende de figure/capture est TRAILING
(placee APRES son image). Elle ne doit pas etre rendue solidaire de l'image
SUIVANTE (autre figure), sinon on cree une chaine keep-with-next a travers
toute la section des captures. On retire donc keep_with_next des paragraphes
de legende "Figure ..." / "Capture ...".
"""
import os, re
import docx
from docx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.join(HERE, "..", "screenshots", "curamedical-rapport",
                    "Rapport_CuraMedical.docx")

d = docx.Document(DOCX)
cap = re.compile(r'^(Figure|Capture)\s')
n = 0
for p in d.paragraphs:
    if p.paragraph_format.keep_with_next and cap.match(p.text.strip()):
        p.paragraph_format.keep_with_next = False
        n += 1
print(f"[fix] keep_with_next retire de {n} legendes Figure/Capture")
d.save(DOCX)
print("SAVED")
