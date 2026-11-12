"""Schematic animations for Titik Heran #53 (run in the episode work dir; needs img/349818.jpg from Pixabay and
../geo/ne_50m_land.geojson from Natural Earth; writes clips/skema_konstruksi.mp4, skema_peta.mp4, skema_kutipan.mp4 and
skema_sumedang.mp4).
konstruksi: Pixabay 349818 is a page of the 18 dated construction photos of the Eiffel Tower (Aug 1887 - Mar 1889); the
  panels run as a stop-motion so the tower grows, with the date of each photo in Indonesian; the last one (12 Mar 1889) holds.
peta: Natural Earth from the Atlantic to Java; a dashed ship line Batavia -> Suez -> Marseille -> Paris draws itself,
  "1889" pops; the route is a sketch ("rute perkiraan"), not the ship's log.
kutipan: an old paper card, the 1913 Debussy line in Indonesian appearing phrase by phrase on the VO words; no face.
sumedang: West Java from Natural Earth; Sumedang pulses, "Museum Prabu Geusan Ulun" pops on "Sumedang".
Event times are seconds from the start of each clip, read off `render.py 53 plan` (konstruksi starts at 2,03, peta at 7,03,
kutipan at 17,47, sumedang at 24,43). Text stays out of the watermark band (y 935-985), the title zone (y < 660) and the
captions (y >= 1210).
usage: python3 skema53.py [konstruksi|peta|kutipan|sumedang ...] [--sheet out.jpg t1,t2,...]
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, encode, dashed
from skema35 import sheet, blur, sepia
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema49 import path_upto

N = {"konstruksi": 62, "peta": 106, "kutipan": 116, "sumedang": 52}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
RG = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


# ---------- konstruksi ----------
COLS = [5, 148, 291, 434, 569, 709, 852, 995, 1138]
DATES = ["10 Agt 1887", "9 Sep 1887", "8 Okt 1887", "10 Nov 1887", "14 Des 1887", "15 Mar 1888", "10 Apr 1888",
         "10 Mei 1888", "Jun 1888", "Jul 1888", "14 Agt 1888", "14 Sep 1888", "14 Okt 1888", "14 Nov 1888",
         "26 Des 1888", "20 Jan 1889", "12 Feb 1889", "12 Mar 1889"]


def panels():
    src = Image.open("img/349818.jpg").convert("RGB")
    out = []
    for (y0, y1) in ((12, 284), (316, 584)):
        for x in COLS:
            out.append(src.crop((x + 3, y0, x + 126, y1)))
    return out


def skema_konstruksi(times=None):
    ps = panels()
    sc = 2.7
    pw, ph = round(123 * sc), round(272 * sc)
    big = [p.resize((pw, ph), Image.LANCZOS) for p in ps]
    bgs = []
    for p in ps:
        a = np.asarray(p.resize((W // 4, H // 4), Image.BILINEAR).resize((W, H), Image.BILINEAR), np.float32)
        a = sepia(blur(a, 12), 0.6) * 0.42
        bgs.append(to_img(a))
    tone = []
    for b in big:
        a = sepia(np.asarray(b, np.float32), 0.35)
        tone.append(to_img(a))
    dates = [pill(d, 38, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200)) for d in DATES]
    cx, cy = 540, 930
    t_end = 1.45
    frames = []
    for i in range(N["konstruksi"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        k = min(int(t / t_end * len(ps)), len(ps) - 1)
        im = bgs[k].convert("RGBA")
        sh = Image.new("RGBA", (W, H))
        ImageDraw.Draw(sh).rectangle([cx - pw // 2 + 10, cy - ph // 2 + 14, cx + pw // 2 + 10, cy + ph // 2 + 14], fill=(0, 0, 0, 150))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
        im.paste(tone[k], (cx - pw // 2, cy - ph // 2))
        d = ImageDraw.Draw(im)
        d.rectangle([cx - pw // 2, cy - ph // 2, cx + pw // 2, cy + ph // 2], outline=(240, 232, 210), width=4)
        last = k == len(ps) - 1
        put1(im, dates[k], 880, 700, scale=min(pop(t, t_end, 0.3), 1.12) if last and t > t_end else 1.0)
        frames.append(im.convert("RGB"))
    return frames


# ---------- maps ----------
def land_layer(px, box):
    lon0, lon1, lat0, lat1 = box
    geo = json.load(open("../geo/ne_50m_land.geojson"))
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for f in geo["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for p in polys:
            ring = p[0]
            xs = [q[0] for q in ring]
            ys = [q[1] for q in ring]
            if max(xs) < lon0 - 3 or min(xs) > lon1 + 3 or max(ys) < lat0 - 3 or min(ys) > lat1 + 3:
                continue
            d.polygon([tuple(c * S for c in px(*q)) for q in ring], fill=(52, 108, 60, 255), outline=(150, 200, 150, 255))
    return lay.resize((W, H), Image.LANCZOS)


def sea_base():
    v = (YY / H)[..., None]
    sea = np.array([16, 44, 86], np.float32) * (1 - v) + np.array([6, 18, 42], np.float32) * v
    return to_img(sea).convert("RGBA")


def pulse(im, x, y, col, t, t0):
    a = ramp(t, t0, t0 + 0.2)
    if a <= 0:
        return
    ph = (t - t0) % 0.9 / 0.9
    rl = Image.new("RGBA", (W, H))
    rd = ImageDraw.Draw(rl)
    r = 10 + 40 * ph
    rd.ellipse([x - r, y - r, x + r, y + r], outline=col + (int(220 * (1 - ph) * a),), width=4)
    rd.ellipse([x - 11, y - 11, x + 11, y + 11], fill=col + (int(255 * a),), outline=(255, 255, 255, int(255 * a)), width=3)
    im.alpha_composite(rl)


# ---------- peta ----------
P_LON0, P_LON1, P_LAT1 = -12.0, 116.0, 54.0
PK = W / (P_LON1 - P_LON0)
P_Y0 = 670


def ppx(lon, lat):
    return ((lon - P_LON0) * PK, P_Y0 + (P_LAT1 - lat) * PK)


BATAVIA, PARIS = (106.8, -6.1), (2.35, 48.86)
ROUTE = [BATAVIA, (104.5, -5.0), (100.0, 4.0), (95.0, 6.0), (80.5, 5.6), (60.0, 12.0), (44.0, 12.5), (43.3, 12.8),
         (38.0, 21.0), (33.0, 28.5), (32.5, 30.0), (32.3, 31.3), (25.0, 34.0), (15.0, 37.5), (9.0, 40.5), (5.4, 43.3),
         (4.8, 45.8), PARIS]


def skema_peta(times=None):
    base = sea_base()
    base.alpha_composite(land_layer(ppx, (P_LON0, P_LON1, -12, P_LAT1)))
    sh = Image.new("RGBA", (W, H))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H], fill=(0, 0, 0, 40))
    base.alpha_composite(sh)
    pts = [ppx(*q) for q in ROUTE]
    bx, by = pts[0]
    fx, fy = pts[-1]
    lab_j = pill("Jawa", 32)
    lab_p = pill("Paris", 32, col=(255, 255, 255), bg=(150, 30, 30, 220))
    lab_y = pill("1889", 54, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(28, 14))
    note = pill("rute perkiraan", 24, col=(210, 210, 215), bg=(10, 14, 24, 170))
    t_go, t_end, t_y = 0.2, 1.9, 1.55   # the line lands while "enam puluh lima" is said
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        u = ease((t - t_go) / (t_end - t_go))
        if u > 0.01:
            dl = Image.new("RGBA", (W * S, H * S))
            dashed(ImageDraw.Draw(dl), path_upto(pts, u), YELLOW + (255,), 5, dash=14, gap=9)
            im.alpha_composite(dl.resize((W, H), Image.LANCZOS))
        pulse(im, bx, by, (255, 220, 60), t, 0.0)
        pulse(im, fx, fy, (255, 70, 50), t, t_end - 0.1)
        put1(im, lab_j, bx - 20, by + 70, a=ramp(t, 0.05, 0.3))
        put1(im, lab_p, fx + 20, fy - 62, a=ramp(t, t_end - 0.1, t_end + 0.15))
        if t > t_y:
            put1(im, lab_y, 760, 860, scale=min(pop(t, t_y, 0.35), 1.1))
        put1(im, note, 540, 1170, a=ramp(t, 0.2, 0.45))
        frames.append(im.convert("RGB"))
    return frames


# ---------- kutipan ----------
QUOTE = [  # (text, y, size, font, colour, show at)
    ("“Dibanding gamelan,", 750, 62, XB, (40, 30, 20), 1.57),
    ("tabuhan Eropa", 828, 62, XB, (40, 30, 20), 2.76),
    ("cuma bising", 898, 70, XB, (170, 40, 30), 3.51),
    ("sirkus keliling.”", 1035, 62, XB, (40, 30, 20), 3.62),
]


def paper():
    n = 0.6 * blur(np.random.default_rng(53).standard_normal((H, W)).astype(np.float32), 1.2) + \
        0.4 * blur(np.random.default_rng(54).standard_normal((H, W)).astype(np.float32), 30) * 6
    a = np.array([232, 218, 186], np.float32) * (1 + 0.035 * np.clip(n, -3, 3))[..., None]
    r = np.hypot((XX - 540) / 540, (YY - 940) / 520)
    return a * (1 - 0.25 * np.clip(r - 0.6, 0, 1))[..., None]


def skema_kutipan(times=None):
    bg = to_img(np.array([30, 24, 18], np.float32) * np.ones((H, W, 1), np.float32)).convert("RGBA")
    pap = to_img(paper()).convert("RGBA")
    m = Image.new("L", (W, H))
    ImageDraw.Draw(m).rounded_rectangle([60, 680, 1020, 1195], radius=18, fill=255)
    card = Image.new("RGBA", (W, H))
    card.paste(pap, (0, 0), m)
    sh = Image.new("RGBA", (W, H))
    ImageDraw.Draw(sh).rounded_rectangle([74, 698, 1034, 1213], radius=18, fill=(0, 0, 0, 170))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    bg.alpha_composite(card)
    d = ImageDraw.Draw(bg)
    d.line([(110, 712), (970, 712)], fill=(120, 100, 76), width=2)
    sprites = []
    for (txt, y, size, font, col, t0) in QUOTE:
        f = ImageFont.truetype(font, size * S)
        x0, y0, x1, y1 = f.getbbox(txt)
        sp = Image.new("RGBA", (x1 - x0 + 20 * S, y1 - y0 + 20 * S))
        ImageDraw.Draw(sp).text((10 * S - x0, 10 * S - y0), txt, font=f, fill=col + (255,))
        sprites.append((sp, y, t0))
    att = Image.new("RGBA", (700 * S, 60 * S))
    ImageDraw.Draw(att).text((350 * S, 30 * S), "— Claude Debussy, 1913", font=ImageFont.truetype(RG, 36 * S), fill=(70, 56, 40, 255), anchor="mm")
    frames = []
    for i in range(N["kutipan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        for sp, y, t0 in sprites:
            if t > t0 - 0.05:
                u = ease((t - t0 + 0.05) / 0.25)
                put1(im, sp, 540, y + 14 * (1 - u), a=u)
        put1(im, att, 600, 1135, a=ramp(t, 0.1, 0.35))
        frames.append(im.convert("RGB"))
    return frames


# ---------- sumedang ----------
S_LON0, S_LON1, S_LAT1 = 105.3, 109.3, -5.75
SK = W / (S_LON1 - S_LON0)
S_Y0 = 670
SUMEDANG = (107.92, -6.86)


def spx(lon, lat):
    return ((lon - S_LON0) * SK, S_Y0 + (S_LAT1 - lat) * SK)


def skema_sumedang(times=None):
    base = sea_base()
    base.alpha_composite(land_layer(spx, (S_LON0, S_LON1, -8.5, S_LAT1)))
    sh = Image.new("RGBA", (W, H))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H], fill=(0, 0, 0, 40))
    base.alpha_composite(sh)
    x, y = spx(*SUMEDANG)
    lab_s = pill("Sumedang", 40, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220))
    lab_m = pill("Museum Prabu Geusan Ulun", 34)
    lab_j = pill("Jawa Barat", 30, col=(210, 210, 215), bg=(10, 14, 24, 170))
    t_s = 0.91
    frames = []
    for i in range(N["sumedang"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        pulse(im, x, y, (255, 220, 60), t, 0.0)
        put1(im, lab_j, 230, 900, a=ramp(t, 0.0, 0.25))
        put1(im, lab_s, x, y - 75, scale=min(pop(t, 0.3, 0.3), 1.1) if t > 0.3 else 0)
        if t > t_s:
            put1(im, lab_m, 540, 1150, scale=min(pop(t, t_s, 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"konstruksi": skema_konstruksi, "peta": skema_peta, "kutipan": skema_kutipan, "sumedang": skema_sumedang}

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
