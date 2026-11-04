"""Render assets/og-card.png, the 1200x630 link-preview card for every page
without its own figure (Home, CV, Blog index, ...).

Not part of the site build. Dev dependency: `pip install pillow`. Uses Segoe UI
from C:\\Windows\\Fonts (pass --font-dir to use another folder with
segoeui.ttf / segoeuib.ttf / seguisb.ttf).

Text comes from papers.json (name, identity_tag, interests) so the card can't
drift from the site again — until 2026-11-04 it still showed the Korean name
and the old "Semiconductor AI Engineer" headline after the site moved on.
"""
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
X0 = 100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font-dir", default=r"C:\Windows\Fonts")
    args = ap.parse_args()
    font = lambda name, size: ImageFont.truetype(os.path.join(args.font_dir, name), size)
    with open(os.path.join(ROOT, "papers.json"), encoding="utf-8") as f:
        data = json.load(f)

    # dark background with a soft blue glow in the top-right corner
    img = Image.new("RGB", (W, H), "#0b0f15")
    glow = Image.new("RGB", (W, H), "#0b0f15")
    ImageDraw.Draw(glow).ellipse((700, -350, 1500, 350), fill="#1b2638")
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(160)), 1.0)
    d = ImageDraw.Draw(img)

    d.text((X0, 166), "PERSONAL HOMEPAGE · CV · BLOG", font=font("seguisb.ttf", 22), fill="#5aa2ff")
    d.text((X0, 214), data["name"], font=font("segoeuib.ttf", 76), fill="#f3f4f6")
    d.text((X0, 330), data["identity_tag"], font=font("segoeui.ttf", 32), fill="#a3aab5")

    x, y = X0, 418
    pill_font = font("segoeui.ttf", 22)
    for tag in data.get("interests", []):
        tw = d.textlength(tag, font=pill_font)
        box = (x, y, x + tw + 44, y + 52)
        if box[2] > W - 60:
            break
        d.rounded_rectangle(box, radius=26, fill="#11161d", outline="#2a313b", width=2)
        d.text((x + 22, y + 11), tag, font=pill_font, fill="#7db7ff")
        x = box[2] + 14

    d.text((X0, 552), "jihoonlee91.github.io", font=font("segoeui.ttf", 22), fill="#6b7280")
    out = os.path.join(ROOT, "assets", "og-card.png")
    img.save(out, optimize=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
