"""Schematic animations for Titik Heran #71 (run in the episode work dir; needs ../geo/ne_50m_admin_0_countries.geojson from
Natural Earth, img/1312229.jpg (Pixabay bantam) and Arif's Higgsfield image img/H3.jpg; writes clips/skema_peta.mp4,
skema_banten.mp4, skema_kamus.mp4, skema_tinggi.mp4).
peta: map of Indonesia (other countries dimmed), a yellow pin with a "?" drops on west Java and pulses; Indonesia brightens
  on "Indonesia".
banten: the same framing zooms into west Java and the Sunda Strait; the pin turns red with a white dot on "Banten" (Banten
  Lama, 106.15 E, 6.03 S: the old port the Europeans called Bantam).
kamus: the Pixabay bantam (moved down 280 px so its head clears the title), slow push; an old dictionary card slides up on
  "ayam kecil": "bantam (1749)" / "ayam kecil; dari Bantam, Jawa", then "Bantam = Banten" on "bantam" (Etymonline,
  Merriam-Webster).
tinggi: H3 (soldiers, Higgsfield) blurred and dimmed behind a height board 100-180 cm; a dashed red line "batas normal
  160 cm", a tall soldier silhouette and a short one, the 147-160 cm band lit (Wikipedia, Bantam (military)).
Event times are seconds from the start of each clip, read off `render.py 71 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < ~600) and the captions (y >= 1210).
usage: python3 skema71.py [peta|banten|kamus|tinggi ...] [--sheet out.jpg t1,t2,...]
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed
from skema35 import sheet
from skema37 import to_img, put1, noise
from skema46 import pill, ease, wanted
from skema70 import shifted, push

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
SERIF_B, SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
WHITE, RED = (255, 255, 255), (232, 44, 40)
N = {"peta": 74, "banten": 42, "kamus": 92, "tinggi": 68}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 71 plan`: peta "namanya" 0.03, "Indonesia" 1.37; banten "bandar" 0.04, "lada" 0.43, "Banten" 0.67;
# kamus "Di" 0.04, "Inggris" 0.27, "ayam" 0.90, "kecil" 1.14, "disebut" 1.53, "bantam" 1.97; tinggi "pendek" 0.03,
# "bernama" 0.42, "Bantam" 1.17
T = {"pin": 0.12, "indo": 1.3,
     "z0": 0.0, "z1": 0.62, "red": 0.64,
     "card": 0.85, "eq": 1.95,
     "short": 0.05, "band": 0.3, "lab": 0.45}

# ---------- map ----------
BANTEN = (106.15, -6.03)
K0, P0 = 1080 / 47.0, (267.7, 996.4)     # peta: 94.5-141.5 E across the width, lat 6 N at y 720
K1, P1 = 150.0, (560.0, 820.0)          # banten: west Java close up
SEA = np.array([14, 34, 66], np.float32)
FEATS = []
for f in json.load(open("../geo/ne_50m_admin_0_countries.geojson"))["features"]:
    g = f["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for p in polys:
        ring = p[0]
        xs, ys = [q[0] for q in ring], [q[1] for q in ring]
        if max(xs) < 85 or min(xs) > 150 or max(ys) < -20 or min(ys) > 20:
            continue
        FEATS.append((f["properties"].get("ADMIN") == "Indonesia", ring, (min(xs), max(xs), min(ys), max(ys))))
YY = np.mgrid[0:H, 0:W][0].astype(np.float32)
SHADE = np.clip(np.maximum((720 - YY) / 420, (YY - 1180) / 260), 0, 1)[..., None] * 0.78   # titles on top, captions below
TEX = noise((H, W), [(40, 0.6), (9, 0.4)], 3)[..., None]


def proj(k, p):
    return lambda lon, lat: (p[0] + (lon - BANTEN[0]) * k, p[1] - (lat - BANTEN[1]) * k)


def draw_map(k, p, bright=0.0):
    xy = proj(k, p)
    im = to_img(SEA * np.ones((H, W, 1), np.float32)).convert("RGBA")
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    lon0, lon1 = BANTEN[0] - p[0] / k - 1, BANTEN[0] + (W - p[0]) / k + 1
    lat1, lat0 = BANTEN[1] + p[1] / k + 1, BANTEN[1] - (H - p[1]) / k - 1
    for indo, ring, (a, b, c, e) in FEATS:
        if b < lon0 or a > lon1 or e < lat0 or c > lat1:
            continue
        col = tuple(int(v + (255 - v) * bright * 0.35) for v in (104, 150, 86)) if indo else (62, 70, 66)
        out = (190, 230, 160) if indo else (96, 104, 100)
        d.polygon([(x * S, y * S) for x, y in (xy(*q) for q in ring)], fill=col + (255,), outline=out + (255,))
    im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    a = np.asarray(im, np.float32)
    a[..., :3] *= (0.9 + 0.2 * TEX) * (1 - SHADE)
    return to_img(a).convert("RGBA")


def pin_sprite(col, mark):
    """a map pin, 2x sprite, the tip at the bottom centre"""
    r = 40 * S
    sp = Image.new("RGBA", (2 * r + 12 * S, 3 * r + 12 * S))
    d = ImageDraw.Draw(sp)
    cx, cy = sp.width // 2, r + 6 * S
    tip = (cx, sp.height - 6 * S)
    for off, c in ((3 * S, (0, 0, 0, 120)), (0, col + (255,))):
        d.polygon([(cx - r * 0.72, cy + r * 0.62), (cx + r * 0.72, cy + r * 0.62), (tip[0], tip[1] - off)], fill=c)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 255), width=3 * S)
    if mark == "?":
        f = ImageFont.truetype(XB, 52 * S)
        x0, y0, x1, y1 = f.getbbox("?")
        d.text((cx - (x0 + x1) / 2, cy - (y0 + y1) / 2), "?", font=f, fill=(20, 20, 20, 255))
    else:
        d.ellipse([cx - 14 * S, cy - 14 * S, cx + 14 * S, cy + 14 * S], fill=(255, 255, 255, 255))
    return sp


PIN_Q, PIN_R = pin_sprite(YELLOW, "?"), pin_sprite(RED, "o")


def place_pin(im, sp, x, y, a=1.0, scale=1.0):
    """pin tip on (x, y)"""
    put1(im, sp, x, y - sp.height / S / 2 * scale, a=a, scale=scale)


def pulse(im, x, y, col, t, t0, a=1.0):
    if t < t0:
        return
    ph = (t - t0) % 0.8 / 0.8
    rl = Image.new("RGBA", (W, H))
    r = 8 + 46 * ph
    ImageDraw.Draw(rl).ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], outline=col + (int(230 * (1 - ph) * a),), width=4)
    im.alpha_composite(rl)


def skema_peta(times=None):
    m0, m1 = draw_map(K0, P0, 0.0), draw_map(K0, P0, 1.0)
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = Image.blend(m0, m1, ramp(t, T["indo"], T["indo"] + 0.25))
        x, y = P0
        pulse(im, x, y, YELLOW, t, T["pin"] + 0.2)
        if t > T["pin"]:
            k = min(pop(t, T["pin"], 0.35), 1.1)
            place_pin(im, PIN_Q, x, y - 60 * (1 - min(k, 1)), a=ramp(t, T["pin"], T["pin"] + 0.1), scale=k)
        frames.append(im.convert("RGB"))
    return frames


L_JAWA = pill("JAWA", 30, col=(230, 240, 220), bg=(20, 40, 30, 150), edge=(255, 255, 255, 60))
L_SUM = pill("SUMATRA", 30, col=(230, 240, 220), bg=(20, 40, 30, 150), edge=(255, 255, 255, 60))


def skema_banten(times=None):
    frames = []
    for i in range(N["banten"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        u = ease((t - T["z0"]) / (T["z1"] - T["z0"]))
        k = K0 * (K1 / K0) ** u
        p = (P0[0] + (P1[0] - P0[0]) * u, P0[1] + (P1[1] - P0[1]) * u)
        im = draw_map(k, p, bright=1.0)
        xy = proj(k, p)
        a = ramp(t, T["z1"] - 0.15, T["z1"] + 0.1)
        put1(im, L_JAWA, *xy(107.9, -6.95), a=a)
        put1(im, L_SUM, *xy(104.6, -4.75), a=a)
        x, y = p
        red = t >= T["red"]
        pulse(im, x, y, RED if red else YELLOW, t, T["red"] if red else 0.0)
        sc = 1.0 + 0.25 * (pop(t, T["red"], 0.3) if red else 0) - (0.25 * ramp(t, T["red"] + 0.3, T["red"] + 0.5) if red else 0)
        place_pin(im, PIN_R if red else PIN_Q, x, y, scale=sc)
        frames.append(im.convert("RGB"))
    return frames


# ---------- dictionary card ----------
def card_sprite(step):
    w, h = 980, 206
    sp = Image.new("RGBA", ((w + 40) * S, (h + 40) * S))
    sh = Image.new("RGBA", sp.size)
    ImageDraw.Draw(sh).rounded_rectangle([24 * S, 28 * S, (w + 24) * S, (h + 28) * S], radius=16 * S, fill=(0, 0, 0, 150))
    sp.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * S)))
    paper = noise((h * S, w * S), [(30, 0.5), (6, 0.5)], 7)[..., None]
    pa = np.array([236, 226, 200], np.float32) * (0.93 + 0.1 * paper)
    pim = to_img(pa * np.ones((h * S, w * S, 1), np.float32)).convert("RGBA")
    m = Image.new("L", pim.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=16 * S, fill=255)
    pim.putalpha(m)
    sp.alpha_composite(pim, (20 * S, 20 * S))
    d = ImageDraw.Draw(sp)
    ink, brown = (34, 26, 20, 255), (150, 40, 26, 255)
    x0, y0 = 20 * S + 40 * S, 20 * S + 12 * S
    fb, fi, fs = ImageFont.truetype(SERIF_B, 80 * S), ImageFont.truetype(SERIF, 44 * S), ImageFont.truetype(XB, 38 * S)
    d.text((x0, y0), "bantam", font=fb, fill=ink)
    bx = x0 + d.textlength("bantam ", font=fb)
    d.text((bx, y0 + 30 * S), "(1749)", font=fi, fill=brown)
    d.text((x0, y0 + 94 * S), "ayam kecil; dari Bantam, Jawa", font=fi, fill=ink)
    if step:
        d.text((x0, y0 + 148 * S), "BANTAM = BANTEN", font=fs, fill=brown)
    return sp


def skema_kamus(times=None):
    bg = Image.open("img/1312229.jpg").convert("RGB")
    bg = bg.resize((1280, 1920), Image.LANCZOS).crop((120, 0, 1200, 1920))
    bg = shifted(bg, 280, edge=170)
    a = np.asarray(bg, np.float32)
    a *= 1 - np.clip((640 - YY) / 520, 0, 1)[..., None] * 0.55          # darker under the title
    bg = to_img(a)
    c0, c1 = card_sprite(False), card_sprite(True)
    frames = []
    for i in range(N["kamus"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = push(bg, t, N["kamus"] / FPS, 1.0, 1.06, cy=700).convert("RGBA")
        if t > T["card"]:
            u = ease((t - T["card"]) / 0.35)
            put1(im, c1 if t >= T["eq"] else c0, 540, 1094 + 140 * (1 - u), a=ramp(t, T["card"], T["card"] + 0.2))
        frames.append(im.convert("RGB"))
    return frames


# ---------- height board ----------
PX, CM0, Y0 = 6.5, 100, 1180          # 6,5 px per cm, 100 cm at y 1180


def ycm(cm):
    return Y0 - (cm - CM0) * PX


def soldier(d, cx, height, fill, outline=None, k=S):
    """upper body of a WWI soldier from behind (Brodie helmet, rifle on the shoulder), drawn on a 2x layer; cm from the top"""
    u = PX * height / 170.0                        # px per "body cm" (proportions of a 170 cm man)
    top = ycm(height)
    Y = lambda cm: (top + cm * u) * k
    X = lambda cm: (cx + cm * u) * k
    shapes = [
        ("e", [X(-9), Y(3), X(9), Y(24)]),                      # head
        ("p", [(X(-6), Y(22)), (X(6), Y(22)), (X(7), Y(30)), (X(-7), Y(30))]),   # neck
        ("p", [(X(-23), Y(32)), (X(-17), Y(28)), (X(17), Y(28)), (X(23), Y(32)), (X(25), Y(60)), (X(21), Y(95)),
               (X(-21), Y(95)), (X(-25), Y(60))]),               # torso
        ("p", [(X(-25), Y(33)), (X(-30), Y(40)), (X(-31), Y(80)), (X(-24), Y(82)), (X(-22), Y(45))]),   # left arm
        ("p", [(X(25), Y(33)), (X(30), Y(40)), (X(31), Y(80)), (X(24), Y(82)), (X(22), Y(45))]),        # right arm
        ("p", [(X(14), Y(-14)), (X(18), Y(-15)), (X(-6), Y(90)), (X(-11), Y(89))]),                      # rifle
        ("e", [X(-19), Y(5), X(19), Y(13)]),                     # helmet brim
        ("e", [X(-11), Y(-3), X(11), Y(12)]),                    # helmet crown
    ]
    for kind, pts in shapes:
        if kind == "e":
            d.ellipse(pts, fill=fill, outline=outline, width=4 * k if outline else 0)
        else:
            d.polygon(pts, fill=fill, outline=outline, width=4 * k if outline else 0)


def skema_tinggi(times=None):
    bg = Image.open("img/H3.jpg").convert("RGB").resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(9))
    a = np.asarray(bg, np.float32) * 0.42
    bg = to_img(a).convert("RGBA")
    board = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(board)
    d.rectangle([60 * S, int(ycm(184) * S), 1020 * S, int(ycm(100) * S)], fill=(214, 200, 168, 70))
    f = ImageFont.truetype(XB, 28 * S)
    for cm in range(110, 181, 10):
        y = ycm(cm) * S
        d.line([(60 * S, y), (1020 * S, y)], fill=(240, 230, 205, 120), width=2 * S)
        d.text((72 * S, y - 34 * S), f"{cm}", font=f, fill=(250, 240, 215, 230))
    board = board.resize((W, H), Image.LANCZOS)
    line = Image.new("RGBA", (W * S, H * S))
    dashed(ImageDraw.Draw(line), [(60, ycm(160)), (1020, ycm(160))], RED + (255,), 5, dash=22, gap=14)
    line = line.resize((W, H), Image.LANCZOS)
    band = Image.new("RGBA", (W, H))
    ImageDraw.Draw(band).rectangle([540, ycm(160), 1020, ycm(147)], fill=YELLOW + (90,))
    tall = Image.new("RGBA", (W * S, H * S))
    soldier(ImageDraw.Draw(tall), 325, 176, (24, 22, 20, 235), outline=(170, 160, 140, 255))
    tall = tall.resize((W, H), Image.LANCZOS)
    short = Image.new("RGBA", (W * S, H * S))
    soldier(ImageDraw.Draw(short), 720, 152, (30, 26, 18, 245), outline=YELLOW + (255,))
    short = short.resize((W, H), Image.LANCZOS)
    fade = Image.fromarray((np.clip((1190 - YY) / 40, 0, 1) * 255).astype(np.uint8))
    for sl in (tall, short):
        sl.putalpha(Image.fromarray((np.asarray(sl.getchannel("A"), np.float32) * np.asarray(fade, np.float32) / 255).astype(np.uint8)))
    lim = pill("batas normal: 160 cm", 30, col=WHITE, bg=(150, 26, 22, 235), edge=(255, 255, 255, 160))
    lb = pill("147–160 cm", 34, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(20, 10))
    lt = pill("tentara biasa", 26, col=(235, 230, 220), bg=(20, 20, 20, 190))
    frames = []
    for i in range(N["tinggi"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = push(bg, t, N["tinggi"] / FPS, 1.0, 1.04)
        im.alpha_composite(board)
        sl = tall.copy()
        sl.putalpha(sl.getchannel("A").point(lambda v: int(v * 0.85)))
        im.alpha_composite(sl)
        put1(im, lt, 235, ycm(176) - 34)
        if t > T["band"]:
            b = band.copy()
            b.putalpha(b.getchannel("A").point(lambda v, q=ramp(t, T["band"], T["band"] + 0.2): int(v * q)))
            im.alpha_composite(b)
        k = ease((t - T["short"]) / 0.3)
        s2 = Image.new("RGBA", (W, H))
        s2.alpha_composite(short, (0, int(80 * (1 - k))))
        s2.putalpha(s2.getchannel("A").point(lambda v, q=ramp(t, T["short"], T["short"] + 0.15): int(v * q)))
        im.alpha_composite(s2)
        im.alpha_composite(line)
        put1(im, lim, 790, ycm(160) - 92)
        if t > T["lab"]:
            put1(im, lb, 950, (ycm(160) + ycm(147)) / 2 + 60, scale=min(pop(t, T["lab"], 0.3), 1.08))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"peta": skema_peta, "banten": skema_banten, "kamus": skema_kamus, "tinggi": skema_tinggi}

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
