"""Schematic animations and the cover for Titik Heran #87 (run in the episode work dir).
garis: horizontal timeline 1837-1935: Queen Victoria's reign 1837-1901, the dot "1901 ratu wafat", then "1930 kisah
  sayembara muncul" (the oldest known trace of the GBP 100 legend: David Fairchild, Exploring for Plants, 1930) and an
  arc "29 TAHUN" between them.
medali: the same timeline, a gold dot pops at 1855, inside the reign (the first mangosteen to fruit in England, Syon House),
  then a gold medal with "MEDALI EMAS BANKSIAN · Horticultural Society London · 1855" (The Horticulturist, 1855).
cover: img/cover87.jpg from Higgsfield H4 (mangosteens on a velvet cushion with a crown) with the title.
Event times are seconds from the start of each clip, read off `render.py 87 plan`. Text stays out of the watermark band
(y 935-985, so the timeline sits at y 760), the title zone (y < ~600) and the captions (y >= 1210).
usage: python3 skema87.py [garis|medali|cover ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, pop, ramp, encode, text_sprite
from skema35 import sheet
from skema37 import to_img, put1, noise, wanted
from skema74 import backdrop

WHITE, GREY = (255, 255, 255), (205, 200, 210)
PURPLE, RED, GOLD = (150, 70, 170), (235, 60, 60), (240, 190, 60)
N = {"garis": 125, "medali": 72}
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
Y0, X_A, X_B, Y_A, Y_B = 760, 1837, 1935, 90, 990


def xof(year):
    return X_A_PX + (year - X_A) * (X_B_PX - X_A_PX) / (X_B - X_A)


X_A_PX, X_B_PX = Y_A, Y_B
T_REIGN, T_1930, T_ARC = 0.0, 0.85, 1.2


def base_bg(seed):
    bg = backdrop((34, 18, 40), (10, 6, 14), glow=(40, 20, 48), gx=540, gy=860)
    a = np.asarray(bg, np.float32).copy()
    a[..., :3] *= (0.93 + 0.14 * noise((H, W), [(40, 0.6), (9, 0.4)], seed))[..., None]
    return to_img(a).convert("RGBA")


def axis(im, u=1.0, reign=1.0, skip=()):
    L = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(L)
    xe = X_A_PX + (X_B_PX - X_A_PX) * u
    d.line([(X_A_PX * S, Y0 * S), (xe * S, Y0 * S)], fill=(235, 230, 240, 190), width=4 * S)
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 28 * S)
    for yr in (1840, 1860, 1880, 1900, 1920):
        x = xof(yr)
        if x <= xe and yr not in skip:
            d.line([(x * S, (Y0 - 10) * S), (x * S, (Y0 + 10) * S)], fill=(235, 230, 240, 160), width=3 * S)
            d.text((x * S, (Y0 + 40) * S), str(yr), font=f, fill=(210, 205, 215, 170), anchor="mm")
    if reign > 0:
        xr = xof(1837) + (xof(1901) - xof(1837)) * reign
        d.rounded_rectangle([(xof(1837) * S, (Y0 - 16) * S), (xr * S, (Y0 + 16) * S)], radius=14 * S, fill=PURPLE + (210,))
    im.alpha_composite(L.resize((W, H), Image.LANCZOS))


def dot(im, x, col, k, r=15):
    if k <= 0:
        return
    d = ImageDraw.Draw(im)
    rr = r * min(k, 1.15)
    d.ellipse([x - rr, Y0 - rr, x + rr, Y0 + rr], fill=col + (255,), outline=(30, 20, 30, 255), width=3)


def skema_garis(times=None):
    bg = base_bg(87)
    l_reign = text_sprite([("Ratu Victoria bertakhta", 36, (225, 200, 235), True), ("1837–1901", 30, GREY, False)])
    l_1901 = text_sprite([("1901", 50, WHITE, True), ("ratu wafat", 32, GREY, False)])
    l_1930 = text_sprite([("1930", 58, RED, True), ("kisah sayembara", 32, WHITE, False), ("baru muncul", 32, WHITE, False)])
    l_29 = text_sprite([("29 TAHUN", 56, YELLOW, True)])
    l_src = text_sprite([("jejak tertua yang diketahui:", 28, GREY, False),
                         ("buku David Fairchild, \"Exploring for Plants\" (1930)", 28, GREY, False)])
    frames = []
    for i in range(N["garis"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        axis(im, ramp(t, 0, 0.35), ramp(t, 0.1, 0.5), skip=(1900,))
        kr = ramp(t, 0.3, 0.6)
        if kr > 0:
            put1(im, l_reign, (xof(1837) + xof(1901)) / 2, Y0 - 66, a=kr)
        k1 = pop(t, 0.45, 0.3)
        dot(im, xof(1901), WHITE, k1)
        if k1 > 0:
            put1(im, l_1901, xof(1901), Y0 + 112, a=min(1, k1 * 1.4))
        k3 = pop(t, T_1930, 0.3)
        dot(im, xof(1930), RED, k3, r=18)
        if k3 > 0:
            put1(im, l_1930, xof(1930) - 20, Y0 + 128, a=min(1, k3 * 1.4))
        ka = ramp(t, T_ARC, T_ARC + 0.5)
        if ka > 0:
            L = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(L)
            x0, x1 = xof(1901), xof(1930)
            cx, r = (x0 + x1) / 2, (x1 - x0) / 2
            box = [(cx - r) * S, (Y0 - r * 0.9) * S, (cx + r) * S, (Y0 + r * 0.9) * S]
            d.arc(box, 180, 180 + 180 * ka, fill=YELLOW + (240,), width=6 * S)
            im.alpha_composite(L.resize((W, H), Image.LANCZOS))
            k29 = pop(t, T_ARC + 0.3, 0.3)
            if k29 > 0:
                put1(im, l_29, cx, Y0 - r * 0.9 - 40, a=min(1, k29 * 1.4), scale=min(k29, 1.06))
                put1(im, l_src, 540, 1130, a=min(1, k29 * 1.2))
        frames.append(im.convert("RGB"))
    return frames


def medal_sprite(r=110):
    m = Image.new("RGBA", (int(2.6 * r) * S, int(3.2 * r) * S))
    d = ImageDraw.Draw(m)
    cx, cy = 1.3 * r * S, 2.0 * r * S
    # ribbon
    d.polygon([(cx - 0.75 * r * S, 0), (cx - 0.05 * r * S, 0), (cx + 0.25 * r * S, cy - 0.6 * r * S), (cx - 0.35 * r * S, cy - 0.6 * r * S)],
              fill=(30, 50, 120, 255))
    d.polygon([(cx + 0.05 * r * S, 0), (cx + 0.75 * r * S, 0), (cx + 0.35 * r * S, cy - 0.6 * r * S), (cx - 0.25 * r * S, cy - 0.6 * r * S)],
              fill=(40, 70, 160, 255))
    for k in range(40, 0, -1):
        u = k / 40
        col = tuple(int(c1 * u + c2 * (1 - u)) for c1, c2 in zip((176, 120, 30), (255, 226, 120)))
        rr = r * S * u
        d.ellipse([cx - rr - (1 - u) * 0.2 * r * S, cy - rr - (1 - u) * 0.25 * r * S,
                   cx + rr - (1 - u) * 0.2 * r * S, cy + rr - (1 - u) * 0.25 * r * S], fill=col + (255,))
    d.ellipse([cx - r * S, cy - r * S, cx + r * S, cy + r * S], outline=(150, 100, 20, 255), width=5 * S)
    d.ellipse([cx - 0.78 * r * S, cy - 0.78 * r * S, cx + 0.78 * r * S, cy + 0.78 * r * S], outline=(200, 150, 50, 200), width=3 * S)
    return m


def skema_medali(times=None):
    bg = base_bg(871)
    l_1855 = text_sprite([("1855", 48, GOLD, True), ("manggis pertama", 30, WHITE, False), ("berbuah di Inggris", 30, WHITE, False)])
    l_m = text_sprite([("MEDALI EMAS BANKSIAN", 56, GOLD, True), ("Horticultural Society, London · 1855", 34, WHITE, False),
                       ("saat Ratu Victoria masih bertakhta", 30, GREY, False)])
    medal = medal_sprite(115)
    frames = []
    for i in range(N["medali"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        fa = 1 - 0.75 * ramp(t, 0.3, 0.6)          # the timeline dims once the medal lands
        tl = Image.new("RGBA", (W, H))
        axis(tl, 1.0, 1.0)
        k = pop(t, 0.0, 0.25)
        dot(tl, xof(1855), GOLD, k, r=17)
        if k > 0:
            put1(tl, l_1855, xof(1855), Y0 + 118, a=min(1, k * 1.4))
        tl.putalpha(tl.getchannel("A").point(lambda v: int(v * fa)))
        im.alpha_composite(tl)
        km = pop(t, 0.3, 0.35)
        if km > 0:
            put1(im, medal, 540, 745, a=min(1, km * 1.5), scale=min(km, 1.06))
            put1(im, l_m, 540, 1095, a=min(1, km * 1.3))
        frames.append(im.convert("RGB"))
    return frames


def cover():
    im = Image.open("img/H4.jpg").convert("RGB")
    a = np.asarray(im, np.float32)
    a *= 1 - np.clip((820 - YY) / 560, 0, 1)[..., None] * 0.55
    im = to_img(a).convert("RGBA")
    t = text_sprite([("MANGGIS BIKIN", 74, WHITE, True), ("RATU INGGRIS", 74, WHITE, True),
                     ("RELA BAYAR £100?", 92, YELLOW, True)], gap=10)
    put1(im, t, 540, 330)
    im.convert("RGB").save("img/cover87.jpg", quality=93)
    print("img/cover87.jpg")


if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or ["garis", "medali", "cover"]
    fns = {"garis": skema_garis, "medali": skema_medali}
    for name in todo:
        if name == "cover":
            cover()
            continue
        fr = fns[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, f"clips/skema_{name}.mp4")
