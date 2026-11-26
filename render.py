#!/usr/bin/env python3
"""Render the news-image-20261125 entry picture (build time only).

Draws a 1024x1024 newspaper front page for Wednesday 25 November 2026:
a masthead, a hero panel on the Strait of Hormuz tanker fires, and six
smaller panels covering the day's other big stories across regions and
fields. Everything is drawn with Pillow here, at build time; the graded
entrypoint (main.py) only copies the finished entry.png.

Stories verified live on 26 Nov 2026 (Just Security Early Edition 25 Nov,
Reuters via BusinessWorld, Open Chronicle global brief, UN News):
  HERO   Strait of Hormuz — two oil tankers hit naval mines and burn.
  RIYADH Houthi drone hits a tower in Riyadh, 11 people hurt.
  SAMARA Ukraine drones set two Russian refineries ablaze.
  NEW YORK Huawei convicted of trade-secret theft and bank fraud.
  ORBIT  Shenzhou-24 docks; Pakistan's first astronaut reaches Tiangong.
  PACIFIC Australia and Solomon Islands sign a security treaty.
  Ticker: Sudan drone strikes kill 19; COP31 ends with no deal;
  Gaza: Israel kills Hamas security chief Abuelouf.
"""

import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

DEJAVU = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = DEJAVU + "DejaVuSerif-Bold.ttf"
SANS_B = DEJAVU + "DejaVuSans-Bold.ttf"
SANS = DEJAVU + "DejaVuSans.ttf"

PAPER = (246, 241, 231)
NAVY = (18, 34, 56)
GOLD = (217, 164, 65)
WHITE = (255, 255, 255)
SEA = (14, 42, 51)
FLAME = (255, 122, 26)
FLAME_Y = (255, 194, 26)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, lines, fnt, fill, leading=None):
    x, y = xy
    lh = leading or int(fnt.size * 1.22)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def vgrad(draw, box, top, bottom):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0))
        col = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(x0, y), (x1, y)], fill=col)


def flame(draw, cx, base_y, h, w, seed=0):
    """A stylised flame: layered teardrops in red, orange, yellow, pale."""
    rng = random.Random(seed)
    for i, col in enumerate(
        [(255, 60, 10), FLAME, FLAME_Y, (255, 230, 120)]
    ):
        fh = h * (1.0 - i * 0.22)
        fw = w * (1.0 - i * 0.18)
        x0, x1 = cx - fw / 2, cx + fw / 2
        y0, y1 = base_y - fh, base_y
        draw.pieslice([x0, y0, x1, y1], 180, 360, fill=col)
        draw.polygon(
            [(cx - fw * 0.28, base_y - fh * 0.55),
             (cx + rng.uniform(-4, 4), base_y - fh * 1.08),
             (cx + fw * 0.28, base_y - fh * 0.55)],
            fill=col,
        )


def smoke(img, box, cx, base_y, h, seed=0):
    """A rising smoke column, clipped to box, drawn on a translucent overlay."""
    x0, y0, x1, y1 = box
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    rng = random.Random(seed)
    y = base_y
    r = 15
    while y > base_y - h and y > y0 + 4:
        drift = (base_y - y) * 0.20
        bx0 = max(x0, cx - r + drift)
        bx1 = min(x1, cx + r + drift)
        od.ellipse([bx0, y - r, bx1, y + r], fill=(52, 52, 52, 105))
        y -= int(r * 0.9)
        r = int(r * 1.10)
    merged = Image.alpha_composite(img.convert("RGBA"), overlay)
    img.paste(merged.convert("RGB"), (0, 0))


def tanker(draw, x, y, w, h):
    """A dark oil-tanker silhouette with deck blocks and a funnel."""
    hull = (16, 16, 18)
    draw.polygon(
        [(x, y + h * 0.55), (x + w, y + h * 0.55),
         (x + w * 0.94, y + h), (x + w * 0.06, y + h)],
        fill=hull,
    )
    draw.rectangle([x + w * 0.08, y + h * 0.30, x + w * 0.42, y + h * 0.55],
                   fill=(30, 30, 34))
    draw.rectangle([x + w * 0.60, y + h * 0.22, x + w * 0.86, y + h * 0.55],
                   fill=(30, 30, 34))
    draw.rectangle([x + w * 0.64, y + h * 0.05, x + w * 0.72, y + h * 0.24],
                   fill=(200, 60, 30))
    for i in range(5):
        bx = x + w * (0.10 + i * 0.07)
        draw.rectangle([bx, y + h * 0.36, bx + w * 0.035, y + h * 0.48],
                       fill=(255, 190, 60))


def waves(draw, box, y0, y1, col):
    """Short wave arcs, clipped to the box's x-range."""
    x0, _, x1, _ = box
    rng = random.Random(7)
    for y in range(y0, y1, 9):
        x = x0
        while x < x1:
            ln = rng.randint(18, 42)
            draw.arc([x, y - 3, min(x + ln, x1), y + 3], 200, 340,
                     fill=col, width=2)
            x += ln + rng.randint(6, 18)


# ---------------------------------------------------------------- scene art
# Every art function receives the exact box it may draw in: (x0, y0, x1, y1).
# Nothing may be drawn outside it.
def art_hormuz(img, d, box):
    x0, y0, x1, y1 = box
    vgrad(d, (x0, y0, x1, y0 + 190), (38, 52, 70), (196, 106, 40))
    d.ellipse([x0 + 700, y0 + 118, x0 + 780, y0 + 198], fill=(255, 214, 130))
    vgrad(d, (x0, y0 + 190, x1, y1), SEA, (10, 30, 38))
    d.polygon([(x0, y0 + 190), (x0 + 260, y0 + 150), (x0 + 520, y0 + 188),
               (x0 + 760, y0 + 158), (x1, y0 + 190), (x1, y0 + 210),
               (x0, y0 + 210)], fill=(52, 44, 40))
    waves(d, box, y0 + 250, y1 - 8, (70, 130, 145))
    tanker(d, x0 + 120, y0 + 250, 300, 92)
    tanker(d, x0 + 560, y0 + 285, 260, 78)
    flame(d, x0 + 250, y0 + 262, 120, 74, seed=1)
    flame(d, x0 + 330, y0 + 258, 88, 52, seed=2)
    flame(d, x0 + 690, y0 + 292, 96, 60, seed=3)
    smoke(img, box, x0 + 250, y0 + 175, 130, seed=4)
    smoke(img, box, x0 + 700, y0 + 210, 105, seed=5)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse([x0 + 150, y0 + 330, x0 + 420, y0 + 380],
               fill=(255, 122, 26, 70))
    od.ellipse([x0 + 600, y0 + 350, x0 + 800, y0 + 392],
               fill=(255, 122, 26, 55))
    merged = Image.alpha_composite(img.convert("RGBA"), overlay)
    img.paste(merged.convert("RGB"), (0, 0))


def art_tower(img, d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (24, 38, 66), (120, 70, 60))
    for tx, tw, th in [(24, 52, 62), (92, 44, 78), (156, 60, 96), (238, 40, 58)]:
        d.rectangle([x0 + tx, y1 - th, x0 + tx + tw, y1], fill=(16, 20, 30))
        for wy in range(y1 - th + 8, y1 - 6, 12):
            d.rectangle([x0 + tx + 5, wy, x0 + tx + tw - 5, wy + 4],
                        fill=(255, 205, 90))
    flame(d, x0 + 186, y1 - 92, 42, 28, seed=11)
    smoke(img, box, x0 + 186, y1 - 118, 52, seed=12)


def art_refinery(img, d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (30, 30, 44), (90, 44, 30))
    for tx in (20, 78, 136):
        d.ellipse([x0 + tx, y1 - 40, x0 + tx + 48, y1 - 18], fill=(70, 72, 80))
        d.rectangle([x0 + tx, y1 - 28, x0 + tx + 48, y1], fill=(52, 54, 62))
    for tx in (210, 250):
        d.rectangle([x0 + tx, y1 - 78, x0 + tx + 12, y1], fill=(40, 40, 48))
    flame(d, x0 + 216, y1 - 76, 36, 24, seed=21)
    flame(d, x0 + 256, y1 - 76, 30, 20, seed=22)
    smoke(img, box, x0 + 236, y1 - 100, 48, seed=23)


def art_court(img, d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (44, 52, 66), (96, 88, 74))
    d.polygon([(x0 + 96, y1 - 78), (x0 + 224, y1 - 78),
               (x0 + 208, y1 - 96), (x0 + 112, y1 - 96)], fill=(200, 190, 160))
    for i in range(5):
        cx = x0 + 106 + i * 24
        d.rectangle([cx, y1 - 76, cx + 10, y1 - 8], fill=(214, 206, 188))
    d.rectangle([x0 + 98, y1 - 10, x0 + 222, y1], fill=(180, 170, 146))
    # small scales of justice at the right
    d.rectangle([x0 + 258, y1 - 66, x0 + 262, y1 - 16], fill=(150, 140, 112))
    d.rectangle([x0 + 238, y1 - 66, x0 + 282, y1 - 62], fill=(150, 140, 112))
    d.polygon([(x0 + 238, y1 - 46), (x0 + 250, y1 - 62),
               (x0 + 262, y1 - 46)], fill=(150, 140, 112))
    d.polygon([(x0 + 258, y1 - 46), (x0 + 270, y1 - 62),
               (x0 + 282, y1 - 46)], fill=(150, 140, 112))


def art_space(img, d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(8, 12, 30))
    rng = random.Random(31)
    for _ in range(46):
        sx = rng.randint(x0 + 4, x1 - 4)
        sy = rng.randint(y0 + 4, y1 - 12)
        r = rng.choice([1, 1, 2])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))
    rx, ry = x0 + 150, y0 + 62
    d.polygon([(rx - 15, ry + 34), (rx, ry - 42), (rx + 15, ry + 34)],
              fill=(230, 230, 235))
    d.rectangle([rx - 15, ry + 32, rx + 15, ry + 46], fill=(200, 60, 40))
    d.polygon([(rx - 27, ry + 46), (rx - 13, ry + 26), (rx - 13, ry + 46)],
              fill=(180, 40, 30))
    d.polygon([(rx + 27, ry + 46), (rx + 13, ry + 26), (rx + 13, ry + 46)],
              fill=(180, 40, 30))
    flame(d, rx, ry + 50, 30, 18, seed=32)
    d.ellipse([x0 + 220, y0 + 12, x0 + 296, y0 + 44], outline=(160, 190, 230),
              width=4)
    d.rectangle([x0 + 240, y0 + 22, x0 + 276, y0 + 34], fill=(160, 190, 230))


def art_treaty(img, d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (20, 70, 90), (60, 130, 110))
    # Australia: blue field, canton cross, white stars
    ax = x0 + 48
    d.rectangle([ax, y0 + 14, ax + 4, y1 - 26], fill=(220, 220, 210))
    d.rectangle([ax + 4, y0 + 14, ax + 76, y0 + 53], fill=(0, 40, 90))
    d.rectangle([ax + 4, y0 + 14, ax + 30, y0 + 53], fill=(200, 30, 30))
    d.rectangle([ax + 4, y0 + 30, ax + 30, y0 + 37], fill=(255, 255, 255))
    d.rectangle([ax + 15, y0 + 14, ax + 19, y0 + 53], fill=(255, 255, 255))
    for sx, sy in [(58, 22), (66, 38), (44, 44)]:
        d.ellipse([ax + sx - 2, y0 + sy - 2, ax + sx + 2, y0 + sy + 2],
                  fill=(255, 255, 255))
    # Solomon Islands: blue over green, yellow diagonal, white stars
    sx = x0 + 172
    d.rectangle([sx, y0 + 14, sx + 4, y1 - 26], fill=(220, 220, 210))
    d.polygon([(sx + 4, y0 + 14), (sx + 76, y0 + 14), (sx + 76, y0 + 28),
               (sx + 4, y0 + 53)], fill=(0, 60, 120))
    d.polygon([(sx + 4, y0 + 53), (sx + 76, y0 + 28), (sx + 76, y0 + 53)],
              fill=(0, 110, 60))
    d.polygon([(sx + 4, y0 + 44), (sx + 76, y0 + 19), (sx + 76, y0 + 28),
               (sx + 4, y0 + 53)], fill=(255, 215, 0))
    for px, py in [(190, 26), (206, 34), (222, 26)]:
        d.ellipse([x0 + px - 2, y0 + py - 2, x0 + px + 2, y0 + py + 2],
                  fill=(255, 255, 255))
    d.rectangle([x0, y1 - 26, x1, y1], fill=(16, 60, 80))
    waves(d, box, y1 - 22, y1 - 4, (90, 170, 190))


def art_sudan(img, d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (70, 44, 26), (150, 90, 40))
    d.polygon([(x0, y1 - 34), (x0 + 90, y1 - 48), (x0 + 180, y1 - 32),
               (x0 + 300, y1 - 44), (x1, y1 - 30), (x1, y1), (x0, y1)],
              fill=(120, 84, 44))
    for hx in (30, 120, 220):
        d.polygon([(x0 + hx, y1 - 34), (x0 + hx + 22, y1 - 56),
                   (x0 + hx + 44, y1 - 34)], fill=(96, 64, 34))
    smoke(img, box, x0 + 150, y1 - 62, 48, seed=41)
    flame(d, x0 + 150, y1 - 46, 30, 20, seed=42)


ART = {
    "hormuz": art_hormuz,
    "tower": art_tower,
    "refinery": art_refinery,
    "court": art_court,
    "space": art_space,
    "treaty": art_treaty,
    "sudan": art_sudan,
}


def draw_panel(img, d, box, art_key, kicker, headline):
    x0, y0, x1, y1 = box
    label_h = 80
    art_box = (x0, y0, x1, y1 - label_h)
    ART[art_key](img, d, art_box)
    d.rectangle([x0, y1 - label_h, x1, y1], fill=NAVY)
    f_k = font(SANS_B, 16)
    f_h = font(SANS_B, 20)
    d.text((x0 + 10, y1 - label_h + 7), kicker, font=f_k, fill=GOLD)
    lines = wrap(d, headline, f_h, (x1 - x0) - 20)
    text_block(d, (x0 + 10, y1 - label_h + 27), lines[:2], f_h, WHITE,
               leading=22)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 112], fill=NAVY)
    d.rectangle([0, 112, W, 116], fill=GOLD)
    f_title = font(SERIF_B, 46)
    title = "THE WORLD IN ONE PICTURE"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 12), title, font=f_title, fill=WHITE)
    f_date = font(SANS_B, 25)
    date = "WEDNESDAY  •  25 NOVEMBER 2026"
    dw = d.textlength(date, font=f_date)
    d.text(((W - dw) / 2, 66), date, font=f_date, fill=GOLD)

    # ---- hero: Strait of Hormuz ----
    hero = (16, 132, W - 16, 566)
    art_hormuz(img, d, hero)
    d.rectangle([hero[0], hero[3] - 108, hero[2], hero[3]], fill=NAVY)
    d.rectangle([hero[0], hero[3] - 108, hero[2], hero[3] - 104], fill=GOLD)
    f_k = font(SANS_B, 20)
    d.text((hero[0] + 14, hero[3] - 100), "STRAIT OF HORMUZ  —  TOP STORY",
           font=f_k, fill=GOLD)
    f_h = font(SANS_B, 33)
    d.text((hero[0] + 14, hero[3] - 72), "Two oil tankers hit mines and burn",
           font=f_h, fill=WHITE)
    f_s = font(SANS, 20)
    d.text((hero[0] + 14, hero[3] - 34),
           "Iran says the ships strayed off route — oil fears spike",
           font=f_s, fill=(215, 220, 228))
    d.rectangle(hero, outline=(120, 110, 95), width=2)

    # ---- six panels ----
    cells = [
        ("tower", "RIYADH", "Houthi drone hits a tower — 11 hurt"),
        ("refinery", "SAMARA, RUSSIA", "Ukraine drones set two refineries ablaze"),
        ("court", "NEW YORK", "Huawei convicted of trade-secret theft"),
        ("space", "ORBIT", "Pakistan's first astronaut reaches Tiangong"),
        ("treaty", "CANBERRA", "Australia–Solomons sign security treaty"),
        ("sudan", "SUDAN", "Drone strikes kill 19 civilians"),
    ]
    gx, gy = 16, 582
    cw, ch, gap = 320, 188, 8
    for i, (key, kick, head) in enumerate(cells):
        cx = gx + (i % 3) * (cw + gap)
        cy = gy + (i // 3) * (ch + gap)
        draw_panel(img, d, (cx, cy, cx + cw, cy + ch), key, kick, head)
        d.rectangle([cx, cy, cx + cw, cy + ch], outline=(120, 110, 95), width=2)

    # ---- bottom ticker ----
    d.rectangle([0, 970, W, H], fill=NAVY)
    d.rectangle([0, 970, W, 974], fill=GOLD)
    tick = ("ALSO:  GAZA — Israel kills Hamas security chief Abuelouf  •  "
            "COP31 ends with no deal  •  Dow tops 50,000")
    f_t = font(SANS_B, 19)
    while d.textlength(tick, font=f_t) > W - 24 and f_t.size > 14:
        f_t = font(SANS_B, f_t.size - 1)
    tw = d.textlength(tick, font=f_t)
    d.text(((W - tw) / 2, 986), tick, font=f_t, fill=(225, 228, 235))

    img.save(OUT, optimize=True)
    print("saved", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
