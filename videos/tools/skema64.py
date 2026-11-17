"""Schematic animations for Titik Heran #64 (run in the episode work dir; needs img/3607859.jpg and img/3603448.jpg;
writes clips/skema_tanggal.mp4, skema_orbit.mp4, skema_kecepatan.mp4).
tanggal: an old paper card "AMERIKA UTARA / 13 November 1833" over a darkened photo of modern meteors.
orbit: the Sun, Earth's orbit and the near part of the 33-year orbit of comet 55P/Tempel-Tuttle (q 0,98 AU, e 0,905) with
  its dust trail; Earth moves along its orbit and lights up where it crosses the trail, then a pill "NOVEMBER" pops.
kecepatan: a meteor streak over the darkened photo, then a Jakarta-Surabaya line (±660 km straight) with a dot running it
  and a pill "±660 km ≈ 10 detik" (71 km/s; no map, a schematic).
Event times are seconds from the start of each clip, read off `render.py 64 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 640) and the captions (y >= 1210).
usage: python3 skema64.py [tanggal|orbit|kecepatan ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, glow_sprite
from skema35 import sheet, SERIF_BI, SERIF_I
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema53 import XB
from skema61 import cover, paper_card
from skema63 import graded

N = {"tanggal": 65, "orbit": 70, "kecepatan": 104}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# set from `render.py 64 plan`: tanggal "Hampir" 0.03, "dua" 0.50, "tahun" 0.97, "lalu" 1.28;
# orbit "dilewati" 0.02, "Bumi" 0.49, "setiap" 0.89, "November" 1.12;
# kecepatan "melesat" 0.23, "tujuh" 0.74, "kilometer" 1.68, "per" 2.31, "detik" 2.55
T = {"card": 0.05, "earth0": 0.0, "cross": 1.1, "nov": 1.15, "label": 0.3,
     "streak0": 0.2, "streak1": 0.75, "line": 1.25, "run0": 1.6, "run1": 2.35, "km": 2.45}
RED = (170, 40, 30, 255)
INK = (52, 38, 26, 255)


# ---------- tanggal ----------
def skema_tanggal(times=None):
    bg = graded("img/3607859.jpg", 0.5, 0.5, 0.55, blur=2)
    cw, ch = 780, 240
    card = paper_card(cw, ch)
    d = ImageDraw.Draw(card)
    ox, oy = 30, 30
    # card top on screen = 690 (the title ends near 680); all rows end above the watermark band (935)
    d.text((ox + cw / 2, oy + 40), "AMERIKA UTARA · DINI HARI", font=ImageFont.truetype(XB, 30), fill=RED, anchor="mm")
    d.line([(ox + 44, oy + 70), (ox + cw - 44, oy + 70)], fill=(150, 120, 90, 255), width=2)
    d.text((ox + cw / 2, oy + 128), "13 November 1833", font=ImageFont.truetype(SERIF_BI, 78), fill=INK, anchor="mm")
    d.text((ox + cw / 2, oy + 196), "dari Kanada sampai Karibia", font=ImageFont.truetype(SERIF_I, 28), fill=(90, 70, 50, 255), anchor="mm")
    frames = []
    for i in range(N["tanggal"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        u = ease((t - T["card"]) / 0.3)
        if u > 0:
            c = card.rotate(2.5 * (1 - u) - 1.0, resample=Image.BICUBIC, expand=True)
            c.putalpha(c.getchannel("A").point(lambda v: int(v * min(1, u * 1.4))))
            im.alpha_composite(c, (540 - c.width // 2, round(690 + 40 * (1 - u))))
        frames.append(im.convert("RGB"))
    return frames


# ---------- orbit ----------
SX, SY, RE = 540, 1000, 190          # the Sun and Earth's orbit radius (1 AU)
Q, E = 0.976, 0.905                   # comet 55P/Tempel-Tuttle: perihelion (AU) and eccentricity
TH_P = math.radians(160)              # perihelion direction on screen (left, a little low); the orbit runs off up-right
CROSS = math.radians(162)             # where Earth meets the trail


def comet_xy(nu):
    r = Q * (1 + E) / (1 + E * math.cos(nu)) * RE
    return SX + r * math.cos(TH_P + nu), SY + r * math.sin(TH_P + nu)


def space_bg():
    rng = np.random.default_rng(64)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = np.array([6, 10, 22], np.float32) * np.ones((H, W, 1), np.float32)
    a += np.exp(-((xx - SX) ** 2 + (yy - SY) ** 2) / 420 ** 2)[..., None] * np.array([18, 16, 10], np.float32)
    im = to_img(a).convert("RGBA")
    d = ImageDraw.Draw(im)
    for _ in range(420):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        v = int(rng.uniform(60, 200))
        r = rng.choice([0.6, 0.9, 1.3], p=[0.6, 0.3, 0.1])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(v, v, min(255, v + 20), 255))
    return im


def skema_orbit(times=None):
    bg = space_bg()
    rng = np.random.default_rng(33)
    st = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(st)
    d.ellipse([(SX - RE) * S, (SY - RE) * S, (SX + RE) * S, (SY + RE) * S], outline=(120, 170, 255, 150), width=3 * S)
    pts = [comet_xy(math.radians(v)) for v in np.linspace(-150, 150, 400)]
    d.line([(x * S, y * S) for x, y in pts], fill=(200, 200, 210, 110), width=2 * S, joint="curve")
    static = st.resize((W, H), Image.LANCZOS)
    sun = glow_sprite(34, (255, 200, 80))
    dust = []                             # (x, y, phase) along the near part of the orbit, thicker near perihelion
    for _ in range(900):
        nu = math.radians(rng.normal(0, 38))
        x, y = comet_xy(nu)
        dust.append((x + rng.normal(0, 7), y + rng.normal(0, 7), rng.uniform(0, 6.28)))
    fl = ImageFont.truetype(XB, 28 * S)
    lab = Image.new("RGBA", (W * S, H * S))
    dl = ImageDraw.Draw(lab)
    dl.text((SX * S, (SY + 64) * S), "MATAHARI", font=fl, fill=(255, 220, 140, 230), anchor="mm")
    dl.text(((SX + RE + 18) * S, (SY + 22) * S), "orbit Bumi", font=ImageFont.truetype(XB, 24 * S),
            fill=(150, 190, 255, 220), anchor="lm")   # just under the watermark band
    labels = lab.resize((W, H), Image.LANCZOS)
    trail = pill("jalur debu komet 55P/Tempel-Tuttle", 28, col=(235, 235, 240), bg=(10, 14, 24, 215))
    period = pill("mengitari Matahari ±33 tahun sekali", 24, col=(210, 210, 220), bg=(10, 14, 24, 190))
    nov = pill("NOVEMBER", 40, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230), pad=(26, 12))
    src = pill("skema · data orbit: NASA", 22, col=(200, 200, 210), bg=(10, 14, 24, 180))
    ex0 = CROSS + math.radians(-80)      # Earth starts 80 degrees before the crossing (it runs anticlockwise on screen)
    frames = []
    for i in range(N["orbit"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        im.alpha_composite(static)
        dd = Image.new("RGBA", (W, H))
        ddraw = ImageDraw.Draw(dd)
        for x, y, ph in dust:
            a = int(110 + 90 * math.sin(ph + t * 5))
            ddraw.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=(255, 236, 190, a))
        im.alpha_composite(dd)
        put1(im, sun, SX, SY, scale=1.0)
        im.alpha_composite(labels)
        k = min(t / T["cross"], 1.0) if t < T["cross"] else 1.0 + 0.12 * (t - T["cross"])
        ang = ex0 + (CROSS - ex0) * ease(k) if k <= 1 else CROSS + math.radians(10) * (k - 1)
        ex, ey = SX + RE * math.cos(ang), SY + RE * math.sin(ang)
        hit = ramp(t, T["cross"] - 0.15, T["cross"]) * (1 - ramp(t, T["cross"] + 0.5, T["cross"] + 0.9))
        if hit > 0:
            g = glow_sprite(40, (255, 230, 150))
            put1(im, g, ex, ey, a=hit, scale=1.0 + 0.6 * hit)
        earth = Image.new("RGBA", (60 * S, 60 * S))
        de = ImageDraw.Draw(earth)
        de.ellipse([8 * S, 8 * S, 52 * S, 52 * S], fill=(70, 140, 255, 255), outline=(220, 235, 255, 255), width=3 * S)
        put1(im, earth, ex, ey)
        ImageDraw.Draw(im).text((ex - 30, ey - 30), "BUMI", font=ImageFont.truetype(XB, 26), fill=(220, 235, 255, 255), anchor="rm")  # left of Earth, clear of MATAHARI
        if t > T["label"]:
            put1(im, trail, 660, 760, a=ramp(t, T["label"], T["label"] + 0.25))
            put1(im, period, 660, 812, a=ramp(t, T["label"] + 0.15, T["label"] + 0.4))
        if t > T["nov"]:
            put1(im, nov, 250, 1150, scale=min(pop(t, T["nov"], 0.3), 1.1))
        put1(im, src, 880, 1180, a=0.9)
        frames.append(im.convert("RGB"))
    return frames


# ---------- kecepatan ----------
JX, SBX, LY = 300, 780, 1050          # Jakarta and Surabaya dots, line height (not to scale on a map: a schematic)


def skema_kecepatan(times=None):
    bg = graded("img/3603448.jpg", 0.9, 0.5, 0.8)   # the photo's own green meteor stays in view, upper right
    city = ImageFont.truetype(XB, 30)
    km = pill("±660 km ≈ 10 detik", 40, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230), pad=(26, 12))
    frames = []
    a0, a1 = (1010, 690), (90, 905)       # the streak runs down-left across the middle
    for i in range(N["kecepatan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        u = ease((t - T["streak0"]) / (T["streak1"] - T["streak0"]))
        fade = 1 - ramp(t, T["streak1"], T["streak1"] + 0.6)
        if u > 0 and fade > 0:
            hx, hy = a0[0] + (a1[0] - a0[0]) * u, a0[1] + (a1[1] - a0[1]) * u
            tx, ty = a0[0] + (a1[0] - a0[0]) * max(0, u - 0.55), a0[1] + (a1[1] - a0[1]) * max(0, u - 0.55)
            lay = Image.new("RGBA", (W, H))
            dl = ImageDraw.Draw(lay)
            n = 30
            for k in range(n):
                f0, f1 = k / n, (k + 1) / n
                p0 = (tx + (hx - tx) * f0, ty + (hy - ty) * f0)
                p1 = (tx + (hx - tx) * f1, ty + (hy - ty) * f1)
                dl.line([p0, p1], fill=(200, 255, 220, int(255 * f1 * fade)), width=max(1, round(2 + 6 * f1)))
            glow = lay.filter(ImageFilter.GaussianBlur(8))
            im.alpha_composite(glow)
            im.alpha_composite(glow)
            im.alpha_composite(lay)
            put1(im, glow_sprite(14, (230, 255, 235)), hx, hy, a=fade)
        la = ramp(t, T["line"], T["line"] + 0.3)
        if la > 0:
            lay = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(lay)
            d.rounded_rectangle([(JX - 210) * S, (LY - 52) * S, (SBX + 180) * S, (LY + 52) * S], radius=26 * S, fill=(8, 12, 20, 190))
            d.line([(JX * S, LY * S), (SBX * S, LY * S)], fill=(255, 255, 255, 140), width=4 * S)
            r = 11
            for x in (JX, SBX):
                d.ellipse([(x - r) * S, (LY - r) * S, (x + r) * S, (LY + r) * S], fill=(255, 255, 255, 255))
            lay = lay.resize((W, H), Image.LANCZOS)
            dt = ImageDraw.Draw(lay)
            dt.text((JX - 24, LY), "Jakarta", font=city, fill=(255, 255, 255, 255), anchor="rm")
            dt.text((SBX + 24, LY), "Surabaya", font=city, fill=(255, 255, 255, 255), anchor="lm")
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * la)))
            im.alpha_composite(lay)
            g = ease((t - T["run0"]) / (T["run1"] - T["run0"]))
            if t > T["run0"]:
                x = JX + (SBX - JX) * g
                d2 = ImageDraw.Draw(im)
                d2.line([(JX, LY), (x, LY)], fill=YELLOW + (255,), width=6)
                put1(im, glow_sprite(12, YELLOW), x, LY)
        if t > T["km"]:
            put1(im, km, 540, 1150, scale=min(pop(t, T["km"], 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"tanggal": skema_tanggal, "orbit": skema_orbit, "kecepatan": skema_kecepatan}

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
