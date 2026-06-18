#!/usr/bin/env python3
"""Regenerate the app icon at pglu/assets/pglu.ico (needs Pillow: pip install pillow).
End users don't run this — the .ico is committed. Run only to change the icon."""

import os

from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "..", "pglu", "assets", "pglu.ico")
SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def render(s: int) -> Image.Image:
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # rounded dark background
    d.rounded_rectangle([s * .05, s * .05, s * .95, s * .95], radius=s * .22, fill=(13, 19, 31, 255))
    # robot face panel (cyan)
    d.rounded_rectangle([s * .22, s * .30, s * .78, s * .72], radius=s * .12, fill=(34, 211, 238, 255))
    # eyes
    r = s * .055
    for cx in (s * .38, s * .62):
        d.ellipse([cx - r, s * .47 - r, cx + r, s * .47 + r], fill=(13, 19, 31, 255))
    # mouth
    d.rounded_rectangle([s * .37, s * .58, s * .63, s * .625], radius=s * .02, fill=(13, 19, 31, 255))
    # antenna
    w = max(2, int(s * .03))
    d.line([s * .5, s * .30, s * .5, s * .19], fill=(129, 140, 248, 255), width=w)
    d.ellipse([s * .5 - s * .045, s * .12, s * .5 + s * .045, s * .21], fill=(129, 140, 248, 255))
    return img


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    big = render(256)
    big.save(OUT, format="ICO", sizes=SIZES)
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
