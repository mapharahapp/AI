"""Schematic animations for Titik Heran #62 (run in the episode work dir; writes clips/skema_inti.mp4, skema_waktu.mp4).
inti: a Lago Coba sediment core (layered mud, the high-mercury layers glow red) and two bars: mercury at the start
  (0,02 ug/g) and at the peak (2,3 ug/g), the second climbing at "melonjak"; a ">100X" pill at "seratus" and the note
  "siput & ganggang lenyap" (Waters et al., Science Advances, 4 Nov 2026).
waktu: a timeline 0-900 M; a red band grows from 535 to 810 M over Cenote Xcach (mercury above the severe-harm level).
Event times are seconds from the start of each clip, read off `render.py 62 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 660) and the captions (y >= 1210).
usage: python3 skema62.py [inti|waktu ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode
from skema35 import sheet, MED
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema53 import XB

N = {"inti": 151, "waktu": 132}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# set from `render.py 62 plan`: inti "merkurinya" 1.86, "melonjak" 2.47, "seratus" 3.45, "lipat" 4.20;
# waktu "se-no-te" 0.62, "bertahan" 1.92, "tiga" 2.71, "tahun" 3.46
T = {"glow": 1.8, "bar": 2.4, "x100": 3.4, "lenyap": 3.95, "xcach": 0.55, "band0": 1.85, "band1": 3.45}
RED = (232, 52, 44)


def bg_grad():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = np.array([14, 22, 30], np.float32) * np.ones((H, W, 1), np.float32)
    a *= (1.15 - 0.4 * np.clip(np.hypot((xx - 540) / 800, (yy - 930) / 900), 0, 1))[..., None]
    return to_img(a).convert("RGBA")


def text(d, xy, s, size, fill, font=XB, anchor="mm"):
    d.text(xy, s, font=ImageFont.truetype(font, size), fill=fill, anchor=anchor)


# ---------- inti ----------
CORE = (110, 700, 280, 1110)            # x0, y0, x1, y1 of the core tube
BASE, BX1, BX2, BWD, BTOP = 1110, 520, 800, 150, 760   # bar baseline, bar centres, width, top of the tall bar


def core_layers():
    rng = np.random.default_rng(62)
    x0, y0, x1, y1 = CORE
    y, out = y0, []
    while y < y1:
        h = int(rng.integers(14, 42))
        c = np.array([96, 74, 52], np.float32) * rng.uniform(0.75, 1.15)
        out.append((y, min(y + h, y1), tuple(int(v) for v in c)))
        y += h
    return out


def skema_inti(times=None):
    bg = bg_grad()
    layers = core_layers()
    hot = [k for k, (a, b, _) in enumerate(layers) if 760 < a < 900]   # the upper-middle layers carry the mercury
    src = pill("Science Advances, 4 Nov 2026", 24, col=(215, 220, 228), bg=(10, 14, 24, 190))
    lcore = pill("inti lumpur Lago Cobá", 26, col=(255, 255, 255), bg=(10, 14, 24, 215))
    x100 = pill(">100X", 64, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230), pad=(28, 10))
    lny = pill("siput & ganggang lenyap", 30, col=(255, 255, 255), bg=(120, 24, 20, 225), edge=(255, 140, 120, 200))
    frames = []
    for i in range(N["inti"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        d = ImageDraw.Draw(im)
        # the core slides up into place
        u = ease(t / 0.45)
        dy = round(120 * (1 - u))
        g = ramp(t, T["glow"], T["glow"] + 0.4) * (0.8 + 0.2 * math.sin(t * 8))
        for k, (a, b, c) in enumerate(layers):
            col = c
            if k in hot:
                col = tuple(int(c[j] * (1 - g) + RED[j] * g) for j in range(3))
            d.rectangle([CORE[0], a + dy, CORE[2], b + dy], fill=col + (255,))
        d.rounded_rectangle([CORE[0] - 6, CORE[1] - 6 + dy, CORE[2] + 6, CORE[3] + 6 + dy], radius=18, outline=(220, 228, 236, 200), width=4)
        put1(im, lcore, (CORE[0] + CORE[2]) / 2 + 20, 1160, a=ramp(t, 0.3, 0.6))
        # axis and bars
        a0 = ramp(t, 0.5, 0.8)
        d.line([(400, BASE), (960, BASE)], fill=(200, 205, 215, int(220 * a0)), width=4)
        h2 = (BASE - BTOP) * ease((t - T["bar"]) / 0.9)
        h1 = max(4, (BASE - BTOP) * 0.02 / 2.3) * a0
        d.rectangle([BX1 - BWD / 2, BASE - h1, BX1 + BWD / 2, BASE], fill=(120, 170, 210, int(255 * a0)))
        if h2 > 1:
            d.rectangle([BX2 - BWD / 2, BASE - h2, BX2 + BWD / 2, BASE], fill=RED + (255,))
        text(d, (BX1, BASE - h1 - 30), "0,02", 40, (220, 230, 240, int(255 * a0)))
        text(d, (BX1, BASE + 34), "AWAL", 30, (200, 205, 215, int(255 * a0)))
        text(d, (BX2, BASE + 34), "PUNCAK", 30, (200, 205, 215, int(255 * a0)))
        if t > T["bar"] + 0.5:
            text(d, (BX2, BASE - h2 - 30), "2,3", 44, (255, 255, 255, int(255 * ramp(t, T["bar"] + 0.5, T["bar"] + 0.8))))
        text(d, (680, BASE + 78), "merkuri, µg per gram lumpur", 26, (170, 178, 190, int(255 * a0)), font=MED)
        put1(im, src, 540, 690, a=ramp(t, 0.6, 0.9))
        if t > T["x100"]:
            put1(im, x100, 560, 850, scale=min(pop(t, T["x100"], 0.3), 1.1))
        if t > T["lenyap"]:
            put1(im, lny, 790, 1040, scale=min(pop(t, T["lenyap"], 0.3), 1.08))
        frames.append(im.convert("RGB"))
    return frames


# ---------- waktu ----------
X0, X1, AY = 100, 980, 1010           # 0 M at X0, 900 M at X1, axis y


def mx(year):
    return X0 + (X1 - X0) * year / 900


def skema_waktu(times=None):
    bg = bg_grad()
    xc = pill("CENOTE XCACH", 44, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230), pad=(26, 12))
    rng_l = pill("±535–810 M", 34, col=(255, 255, 255), bg=(120, 24, 20, 225), edge=(255, 140, 120, 200))
    sub = pill("merkuri di atas batas bahaya berat", 26, col=(225, 228, 232), bg=(10, 14, 24, 200))
    frames = []
    for i in range(N["waktu"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        lay = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(lay)
        a0 = ramp(t, 0.0, 0.3)
        w = ease(t / 0.5)
        d.line([(X0, AY), (X0 + (X1 - X0) * w, AY)], fill=(220, 226, 236, int(255 * a0)), width=5)
        for y in (0, 300, 600, 900):
            if mx(y) <= X0 + (X1 - X0) * w + 1:
                d.line([(mx(y), AY - 12), (mx(y), AY + 12)], fill=(220, 226, 236, 255), width=4)
                text(d, (mx(y), AY + 44), f"{y} M" if y == 900 else str(y), 32, (200, 206, 216, 255))
        # the red band
        b = ease((t - T["band0"]) / (T["band1"] - T["band0"]))
        if b > 0:
            xe = mx(535) + (mx(810) - mx(535)) * b
            d.rectangle([mx(535), 800, xe, AY - 4], fill=RED + (225,))
            glow = lay.filter(ImageFilter.GaussianBlur(14))
            im.alpha_composite(glow)
        im.alpha_composite(lay)
        if t > T["xcach"]:
            put1(im, xc, mx(672), 730, scale=min(pop(t, T["xcach"], 0.3), 1.1))
        if t > T["band0"] + 0.3:
            put1(im, rng_l, mx(672), 1110, a=ramp(t, T["band0"] + 0.3, T["band0"] + 0.6))
            put1(im, sub, 540, 1170, a=ramp(t, T["band0"] + 0.5, T["band0"] + 0.8))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"inti": skema_inti, "waktu": skema_waktu}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    os.makedirs("clips", exist_ok=True)
    for name in args or list(N):
        fr = FUN[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
