#!/usr/bin/env python3
"""Render the round-4 meme: a doctor's note / sick-leave certificate from
Leonida General Hospital, prescribing 2 weeks' sick leave in Vice City for
acute "GTA VI fever" after the 13-year wait. The real make.fun press-kit
ghost (assets/mark-1024.png) is the clinic's seal/stamp, bottom right.

Deterministic: same input files -> byte-identical meme.png.
Run: python3 render.py  (writes meme.png next to this script)
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GHOST_PATH = os.path.join(HERE, "assets", "mark-1024.png")
OUT_PATH = os.path.join(HERE, "meme.png")

W, H = 1024, 1024
PAPER = (251, 246, 233)      # warm certificate paper
NAVY = (18, 50, 74)          # ink
MAGENTA = (209, 14, 124)     # make.fun magenta (matches the ghost disc)
RED = (198, 40, 40)          # hospital cross
GREY = (90, 100, 110)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()

SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF_I = lambda s: font("DejaVuSerif-Italic.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)

def text_w(draw, text, f):
    return draw.textlength(text, font=f)

def draw_spaced(draw, xy, text, f, fill, spacing=3):
    """Draw text with extra letter spacing (for small-caps style lines)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + spacing
    return x

def main():
    ghost = Image.open(GHOST_PATH).convert("RGBA")
    assert ghost.size == (1024, 1024), f"ghost must be 1024x1024, got {ghost.size}"

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # --- paper borders -------------------------------------------------
    d.rectangle([24, 24, W - 25, H - 25], outline=NAVY, width=4)
    d.rectangle([38, 38, W - 39, H - 39], outline=NAVY, width=2)

    # --- header: red cross + hospital name -----------------------------
    # red cross, left
    cx, cy, s = 78, 78, 30
    d.rectangle([cx + s // 2 - 9, cy, cx + s // 2 + 9, cy + s], fill=RED)
    d.rectangle([cx, cy + s // 2 - 9, cx + s, cy + s // 2 + 9], fill=RED)
    # hospital name, two lines
    d.text((128, 58), "LEONIDA GENERAL", font=SERIF_B(50), fill=NAVY)
    d.text((128, 118), "HOSPITAL", font=SERIF_B(50), fill=NAVY)
    # cert number + city, top right
    num = "CERT. No. 261119"
    d.text((W - 78 - text_w(d, num, SANS_B(22)), 66), num, font=SANS_B(22), fill=GREY)
    d.text((W - 78 - text_w(d, "VICE CITY, LEONIDA", SANS(22)), 98),
           "VICE CITY, LEONIDA", font=SANS(22), fill=GREY)

    # --- navy band: document title --------------------------------------
    d.rectangle([38, 212, W - 39, 272], fill=NAVY)
    title = "MEDICAL CERTIFICATE  •  SICK NOTE"
    d.text(((W - text_w(d, title, SANS_B(38))) / 2, 222), title,
           font=SANS_B(38), fill=(255, 255, 255))

    # --- body rows -------------------------------------------------------
    rows = [
        ("PATIENT", "A GTA FAN"),
        ("DIAGNOSIS", 'ACUTE "GTA VI FEVER"'),
        ("CAUSE", "13-YEAR WAIT SINCE GTA V"),
        ("PRESCRIBED", "2 WEEKS' SICK LEAVE"),
        ("TREATMENT", "BED REST IN VICE CITY"),
    ]
    y = 300
    for label, value in rows:
        d.text((78, y), label, font=SANS_B(24), fill=MAGENTA)
        d.text((78, y + 28), value, font=SANS_B(40), fill=NAVY)
        # values sit above y 690; the seal starts at y 690, so only the
        # right border (x 947) limits their width, not the seal.
        assert 78 + text_w(d, value, SANS_B(40)) < 940, f"value too wide: {value}"
        y += 80
    # rows end at 300 + 5*80 = 700; italic note under them
    note = "Fit to play from launch day. No work, no meetings, no spoilers."
    d.text((78, 716), note, font=SERIF_I(32), fill=NAVY)

    # --- signature, bottom left ------------------------------------------
    d.text((78, 798), "Dr. Lucia", font=SERIF_I(50), fill=NAVY)
    d.line([(78, 858), (420, 858)], fill=NAVY, width=2)
    d.text((78, 868), "DR. LUCIA, MD  •  19 NOV 2026", font=SANS_B(22), fill=GREY)

    # --- clinic seal: the REAL make.fun ghost, rotated ---------------------
    # The ghost's own magenta disc + black outline already reads as a
    # stamp; no extra ring, so nothing crowds the signature or footer.
    seal = ghost.resize((250, 250), Image.LANCZOS)
    seal = seal.rotate(-8, resample=Image.BICUBIC, expand=False)
    img.paste(seal, (688, 690), seal)

    # --- footer band: the payer line sells make.fun in the meme's voice --
    d.rectangle([38, 948, W - 39, 986], fill=MAGENTA)
    foot = "CONSULTATION FEE $0.00 — PAID BY MY AI AGENT'S make.fun BOUNTY"
    assert text_w(d, foot, SANS_B(22)) < 900, "footer too wide"
    d.text(((W - text_w(d, foot, SANS_B(22))) / 2, 956), foot,
           font=SANS_B(22), fill=(255, 255, 255))

    img.save(OUT_PATH, "PNG", optimize=True)
    size = os.path.getsize(OUT_PATH)
    assert Image.open(OUT_PATH).size == (1024, 1024)
    assert size <= 1024 * 1024, f"meme.png {size} bytes > 1 MiB"
    print(f"wrote {OUT_PATH} ({size} bytes)")

if __name__ == "__main__":
    sys.exit(main())
