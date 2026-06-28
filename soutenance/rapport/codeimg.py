# -*- coding: utf-8 -*-
"""Rendu des extraits de code en images façon éditeur VS Code (thème sombre).

Coloration syntaxique via Pygments, puis composition d'une fenêtre d'éditeur
(barre de titre, pastilles, nom de fichier) et coins arrondis + ombre portée
via Pillow, pour un rendu « capture d'écran » professionnel.
"""
import io
import os
import hashlib

from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import get_lexer_by_name
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTDIR = os.path.join(os.path.dirname(__file__), "_codeimg")
os.makedirs(OUTDIR, exist_ok=True)

# Thème proche de « One Dark » / VS Code Dark+
EDITOR_BG = (40, 44, 52)      # #282c34
TITLE_BG  = (33, 37, 43)      # #21252b
TXT_FG    = (171, 178, 191)   # #abb2bf
DOTS = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]

FONT_PATHS = [
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\CascadiaCode.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
]


def _font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return mask


def render(code, language="python", filename="", font_size=30):
    """Génère l'image et renvoie (chemin_png, largeur_px, hauteur_px)."""
    key = hashlib.md5((language + "|" + filename + "|" + code).encode("utf-8")).hexdigest()[:12]
    out = os.path.join(OUTDIR, f"code_{key}.png")
    # (re)génère systématiquement pour rester synchrone avec le contenu

    try:
        lexer = get_lexer_by_name(language)
    except Exception:
        lexer = get_lexer_by_name("text")

    fmt = ImageFormatter(
        style="one-dark",
        font_name="Consolas",
        font_size=font_size,
        line_numbers=True,
        line_number_bg="#21252b",
        line_number_fg="#5c6370",
        line_number_separator=False,
        line_number_pad=10,
        image_pad=int(font_size * 0.8),
        line_pad=int(font_size * 0.32),
    )
    try:
        png = highlight(code, lexer, fmt)
        body = Image.open(io.BytesIO(png)).convert("RGB")
    except Exception:
        # Repli : rendu texte simple si la police pose problème
        fmt2 = ImageFormatter(style="one-dark", font_size=font_size, line_numbers=True)
        png = highlight(code, lexer, fmt2)
        body = Image.open(io.BytesIO(png)).convert("RGB")

    w = body.width
    # ── Barre de titre ──────────────────────────────────────────────────────
    title_h = int(font_size * 1.7)
    editor = Image.new("RGB", (w, title_h + body.height), EDITOR_BG)
    draw = ImageDraw.Draw(editor)
    draw.rectangle([0, 0, w, title_h], fill=TITLE_BG)

    # pastilles type macOS / fenêtre
    r = max(5, int(font_size * 0.2))
    cy = title_h // 2
    x0 = int(font_size * 0.9)
    for i, col in enumerate(DOTS):
        cx = x0 + i * int(r * 3.2)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    # nom de fichier centré
    if filename:
        f = _font(int(font_size * 0.62))
        try:
            tb = draw.textbbox((0, 0), filename, font=f)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
        except Exception:
            tw, th = len(filename) * font_size // 2, font_size
        draw.text(((w - tw) // 2, (title_h - th) // 2 - tb[1] if 'tb' in dir() else (title_h - th)//2),
                  filename, fill=TXT_FG, font=f)

    editor.paste(body, (0, title_h))

    # ── Coins arrondis + ombre portée sur fond blanc ────────────────────────
    radius = int(font_size * 0.55)
    margin = int(font_size * 1.3)
    canvas = Image.new("RGB", (w + 2 * margin, editor.height + 2 * margin), (255, 255, 255))

    # ombre
    shadow = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    sd = ImageDraw.Draw(shadow)
    off = int(font_size * 0.18)
    sd.rounded_rectangle(
        [margin, margin + off, margin + w, margin + editor.height + off],
        radius=radius, fill=(20, 30, 25, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(int(font_size * 0.45)))
    canvas.paste(Image.new("RGB", canvas.size, (255, 255, 255)), (0, 0))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), shadow).convert("RGB")

    # éditeur aux coins arrondis
    mask = _rounded_mask(editor.size, radius)
    canvas.paste(editor, (margin, margin), mask)

    canvas.save(out, "PNG")
    return out, canvas.width, canvas.height
