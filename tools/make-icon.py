"""Render the 몰입 퀘스트 app icon: a quest pennant and three stars on the brand green tile.

Outputs under assets/icon/: icon-1024.png (master), icon.ico (Windows), icon-foreground.png
(Android adaptive foreground on transparent), and the sizes macOS/Android packaging scripts use.
Pillow only; no network.
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/icon"
OUT.mkdir(parents=True, exist_ok=True)

GREEN = (23, 61, 54, 255)      # .sidebar background
LIGHT = (239, 250, 245, 255)   # sidebar text
GOLD = (242, 201, 76, 255)
SCALE = 4
SIZE = 1024 * SCALE


def star(cx, cy, r, draw, fill):
    import math
    points = []
    for i in range(10):
        radius = r if i % 2 == 0 else r * 0.45
        angle = math.radians(-90 + i * 36)
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    draw.polygon(points, fill=fill)


def pennant(draw, scale=1.0, offset=(0, 0)):
    """Flag pole and pennant centred in a 1024 box; `scale` shrinks it for the adaptive foreground."""
    s = SCALE * scale
    ox, oy = offset
    pole_x = 330 * s + ox
    top, bottom = 200 * s + oy, 840 * s + oy
    draw.rounded_rectangle([pole_x - 28 * s, top, pole_x + 28 * s, bottom], radius=28 * s, fill=LIGHT)
    draw.ellipse([pole_x - 46 * s, top - 46 * s, pole_x + 46 * s, top + 46 * s], fill=GOLD)
    flag = [(pole_x + 28 * s, 250 * s + oy), (770 * s + ox, 360 * s + oy), (pole_x + 28 * s, 520 * s + oy)]
    draw.polygon(flag, fill=LIGHT)
    draw.polygon([(pole_x + 28 * s, 250 * s + oy), (pole_x + 28 * s, 520 * s + oy), (610 * s + ox, 390 * s + oy)], fill=GOLD)
    for i, (sx, sy, r) in enumerate([(560, 650, 42), (650, 720, 54), (750, 800, 66)]):
        star(sx * s + ox, sy * s + oy, r * s, draw, GOLD if i == 2 else LIGHT)


def tile():
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=SIZE * 0.22, fill=GREEN)
    pennant(draw)
    return image.resize((1024, 1024), Image.LANCZOS)


def foreground():
    # Android adaptive icons are cropped to a circle inside the middle 66%, so draw the motif small.
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    pennant(draw, scale=0.6, offset=(SIZE * 0.2, SIZE * 0.2))
    return image.resize((1024, 1024), Image.LANCZOS)


master = tile()
master.save(OUT / "icon-1024.png")
master.save(OUT / "icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
foreground().save(OUT / "icon-foreground.png")
for size in (48, 72, 96, 144, 192, 512):
    master.resize((size, size), Image.LANCZOS).save(OUT / f"icon-{size}.png")
print("icons written to", OUT)
