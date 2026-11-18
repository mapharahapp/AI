"""Schematic animations for Titik Heran #66 (run in the episode work dir; needs img/10371331.jpg and img/6062044.jpg;
writes clips/skema_desa.mp4, skema_penampang.mp4, skema_peta.mp4 and skema_raksasa.mp4).
desa: a coastal hill in cross-section over the dark dusk Dardanelles photo, its sea side cut into a steep face by the waves;
  little huts pop on top with "?" and a pill "DESA PURBA? · dugaan sejak 2011".
penampang: the same hill opened up as the 2024 rescue dig read it (Polat, TRMuseum 2026): rows of stones set in mud on the
  sea side, a green clay cap, a black carried-in fill with pottery bits and tuna bones; a red stamp "TUMULUS" and labels.
peta: a not-to-scale sketch: the strait on top, the mound on the shore, TROYA inland, a dashed ±10 km line, and Rhoiteion,
  where Strabo placed Ajax's tomb. No compass and no real coastline: the exact spot is not published.
raksasa: a 1,7 m person beside a 5 m skeleton (the size Philostratus gave, 11 cubits) with a metre ruler that counts up.
Event times are seconds from the start of each clip, read off `render.py 66 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 690 for three-line titles) and the captions (y >= 1210).
usage: python3 skema66.py [desa|penampang|peta|raksasa ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed
from skema23 import smooth
from skema27 import stamp_sprite
from skema35 import sheet, SERIF_BI
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema53 import XB
from skema61 import cover

N = {"desa": 82, "penampang": 66, "peta": 50, "raksasa": 64}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 66 plan`: desa "Bukit" 0.04, "dulu" 0.94, "dikira" 1.24, "desa" 1.65; penampang "ternyata" 0.03,
# "gundukan" 0.59, "buatan" 0.99, "manusia" 1.33; peta "dekat" 0.04, "lokasi" 0.34, "catatan" 0.64, "kuno" 1.01;
# raksasa "kerangkanya" 0.02, "setinggi" 0.72, "lima" 1.06, "meter" 1.28
T = {"hill": 0.0, "huts": 1.15, "desa": 1.6,
     "open": 0.0, "stamp": 0.55, "lab1": 0.95, "lab2": 1.3,
     "map": 0.0, "line": 0.25, "rho": 0.62,
     "person": 0.0, "grow0": 0.2, "grow1": 1.15, "five": 1.2, "src": 1.35}
SEA = (40, 92, 140)
WHITE = (255, 255, 255)


def graded(path, cx, cy, k, blur=0, sepia=False):
    im = cover(path, cx, cy)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im, np.float32)
    if sepia:
        a = a @ np.array([[.393, .349, .272], [.769, .686, .534], [.189, .168, .131]], np.float32)
    return to_img(a * k).convert("RGBA")


def two(pts):
    return [(x * S, y * S) for x, y in pts]


# ---------- the hill in cross-section (desa, penampang) ----------
GROUND = 1150          # land surface on the right
SEA_Y = 1085           # sea level
CLIFF_X = 300          # the eroded face
TOP = [(CLIFF_X, 1150), (CLIFF_X + 6, 1010), (CLIFF_X + 30, 890), (380, 790), (470, 735), (580, 718), (690, 735),
       (790, 800), (880, 900), (950, 1060), (1000, 1150)]
HILL = smooth(TOP, 3)


def scene(open_k=0.0):
    """sea, beach and the hill; open_k 0 = plain earth, 1 = the section the 2024 dig found"""
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    d.rectangle([0, SEA_Y * S, CLIFF_X * S, 1200 * S], fill=SEA + (230,))
    for k in range(4):   # wave crests hitting the face
        y = SEA_Y + 10 + 24 * k
        d.arc([(CLIFF_X - 120 - 40 * k) * S, (y - 14) * S, (CLIFF_X - 20 - 40 * k) * S, (y + 14) * S], 200, 340, fill=WHITE + (160,), width=4 * S)
    d.rectangle([0, 1150 * S, W * S, 1200 * S], fill=(120, 96, 64, 255))           # bedrock and beach under everything
    poly = HILL + [(1000, 1150), (CLIFF_X, 1150)]
    earth = (128, 98, 62, 255)
    d.polygon(two(poly), fill=earth)
    if open_k > 0:
        sec = Image.new("RGBA", (W * S, H * S))
        ds = ImageDraw.Draw(sec)
        ds.polygon(two(poly), fill=(34, 30, 28, 255))                                   # black, soft carried-in fill
        rng = np.random.default_rng(5)
        for _ in range(55):                                                              # pottery bits and tuna bones
            x, y = rng.uniform(360, 920), rng.uniform(780, 1130)
            if not inside(poly, x, y):
                continue
            if rng.random() < 0.6:
                r = rng.uniform(6, 11)
                a0 = rng.uniform(0, 6.28)
                ds.polygon(two([(x + r * math.cos(a0 + q * 2.1), y + r * math.sin(a0 + q * 2.1)) for q in range(3)]), fill=(196, 104, 60, 255))
            else:
                ds.ellipse([(x - 5) * S, (y - 3) * S, (x + 5) * S, (y + 3) * S], fill=(235, 230, 215, 255))
        cap = smooth(TOP, 3)
        ds.line(two(cap), fill=(96, 150, 84, 255), width=18 * S, joint="curve")     # green clay cap
        for row in range(5):                                                             # stone rows set in mud, sea side
            y = 1135 - row * 34
            x0 = CLIFF_X + 18 + row * 10
            for j in range(4 - row // 2):
                cx = x0 + j * 40
                ds.ellipse([(cx - 17) * S, (y - 13) * S, (cx + 17) * S, (y + 13) * S], fill=(150, 150, 146, 255), outline=(70, 70, 66, 255), width=2 * S)
        a = np.asarray(sec, np.float32)
        a[..., 3] *= open_k
        lay.alpha_composite(Image.fromarray(a.astype(np.uint8)))
        d = ImageDraw.Draw(lay)
    d.line(two(HILL), fill=WHITE + (235,), width=5 * S, joint="curve")
    return lay.resize((W, H), Image.LANCZOS)


def inside(poly, x, y):
    c = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            c = not c
    return c


def hut():
    sp = Image.new("RGBA", (90 * S, 80 * S))
    d = ImageDraw.Draw(sp)
    d.polygon(two([(10, 38), (45, 8), (80, 38)]), fill=(214, 170, 96, 255), outline=(60, 40, 20, 255))
    d.rectangle([18 * S, 38 * S, 72 * S, 74 * S], fill=(170, 122, 70, 255), outline=(60, 40, 20, 255), width=2 * S)
    d.rectangle([38 * S, 52 * S, 52 * S, 74 * S], fill=(60, 40, 20, 255))
    return sp


def skema_desa(times=None):
    bg = graded("img/10371331.jpg", 0.5, 0.5, 0.45, blur=4)
    hill = scene(0.0)
    hs = hut()
    q = pill("?", 40, col=(20, 20, 20), bg=YELLOW + (240,), edge=WHITE + (220,), pad=(16, 6))
    lab = pill("DESA PURBA?  ·  dugaan sejak 2011", 34, col=(20, 20, 20), bg=YELLOW + (240,), edge=WHITE + (220,), pad=(22, 10))
    sea_lab = pill("laut", 28, col=WHITE, bg=(10, 14, 24, 190), pad=(16, 8))
    frames = []
    for i in range(N["desa"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        a = ramp(t, 0.0, 0.35)
        h = hill.copy()
        h.putalpha(h.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(h, (0, round(30 * (1 - ease(t / 0.35)))))
        put1(im, sea_lab, 150, 1140, a=a)
        for k, (x, y) in enumerate([(480, 700), (590, 684), (700, 702)]):
            if t > T["huts"] + 0.08 * k:
                put1(im, hs, x, y, scale=min(pop(t, T["huts"] + 0.08 * k, 0.3), 1.08))
        if t > T["huts"] + 0.3:
            put1(im, q, 780, 640 + 0, scale=min(pop(t, T["huts"] + 0.3, 0.3), 1.1))
        if t > T["desa"]:
            put1(im, lab, 600, 1030, scale=min(pop(t, T["desa"], 0.3), 1.06))
        frames.append(im.convert("RGB"))
    return frames


def skema_penampang(times=None):
    bg = graded("img/10371331.jpg", 0.5, 0.5, 0.3, blur=8)
    shut = scene(0.0)
    opn = scene(1.0)
    stamp = stamp_sprite("TUMULUS", 78, angle=-8)
    l1 = pill("batu penahan + tanah liat hijau", 30, col=(20, 20, 20), bg=YELLOW + (240,), edge=WHITE + (220,), pad=(18, 9))
    l2 = pill("tanah diangkut dari permukiman lain", 30, col=WHITE, bg=(10, 14, 24, 215), pad=(18, 9))
    src = pill("digali Okt 2024 · Polat, TRMuseum 2026", 24, col=(230, 230, 235), bg=(10, 14, 24, 190))
    frames = []
    for i in range(N["penampang"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        k = ramp(t, 0.05, 0.45)
        im.alpha_composite(shut if k <= 0 else (opn if k >= 1 else Image.blend(shut, opn, k)))
        if t > T["stamp"]:
            put1(im, stamp, 640, 880, scale=min(pop(t, T["stamp"], 0.25), 1.08) * 0.9)
        if t > T["lab1"]:
            put1(im, l1, 330, 1015, scale=min(pop(t, T["lab1"], 0.3), 1.06))
        if t > T["lab2"]:
            put1(im, l2, 640, 1100, scale=min(pop(t, T["lab2"], 0.3), 1.06))
        put1(im, src, 760, 1180, a=ramp(t, 0.3, 0.6))
        frames.append(im.convert("RGB"))
    return frames


# ---------- peta ----------
MOUND, TROY, RHO = (300, 905), (760, 1120), (470, 860)
COAST = smooth([(-20, 880), (120, 900), (240, 896), (300, 892), (380, 872), (470, 846), (560, 836), (660, 812),
                (800, 800), (920, 772), (1100, 750)], 3)


def map_base():
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 680 * S, W * S, 1200 * S], fill=(54, 62, 44, 255))                   # land
    d.polygon(two(COAST + [(1100, 680), (-20, 680)]), fill=SEA + (255,))                 # the strait
    d.line(two(COAST), fill=WHITE + (200,), width=4 * S, joint="curve")
    for k in range(3):
        y = 720 + 30 * k
        d.line(two([(560 + 60 * k, y), (640 + 60 * k, y - 6)]), fill=WHITE + (90,), width=3 * S)
    d.text((240 * S, 712 * S), "SELAT DARDANELLA", font=ImageFont.truetype(SERIF_BI, 46 * S), fill=(200, 222, 240, 255))
    # Troy's walls as a small ring of ruins
    d.ellipse([(TROY[0] - 28) * S, (TROY[1] - 20) * S, (TROY[0] + 28) * S, (TROY[1] + 20) * S], outline=(225, 205, 160, 255), width=5 * S)
    return lay.resize((W, H), Image.LANCZOS)


def skema_peta(times=None):
    base = map_base()
    l_m = pill("gundukan Işıldaktepe Altı", 30, col=(20, 20, 20), bg=YELLOW + (240,), edge=WHITE + (220,), pad=(18, 9))
    l_t = pill("TROYA", 34, col=WHITE, bg=(10, 14, 24, 215), pad=(20, 9))
    l_d = pill("±10 km", 32, col=(20, 20, 20), bg=WHITE + (235,), edge=WHITE + (235,), pad=(16, 8))
    l_r = pill("Rhoiteion: makam Ajax menurut Strabo", 28, col=WHITE, bg=(150, 30, 24, 230), edge=WHITE + (200,), pad=(18, 9))
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = Image.new("RGBA", (W, H), (12, 16, 24, 255))
        a = ramp(t, 0.0, 0.25)
        b = base.copy()
        b.putalpha(b.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(b)
        lay = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(lay)
        u = ease((t - T["line"]) / 0.4)
        L = math.hypot(TROY[0] - MOUND[0], TROY[1] - MOUND[1])
        if u > 0:
            dashed(d, [MOUND, TROY], WHITE + (240,), 4, dash=18, gap=12, upto=L * u)
        pr = 14 + 6 * math.sin(t * 9)
        d.ellipse([(MOUND[0] - pr) * S, (MOUND[1] - pr) * S, (MOUND[0] + pr) * S, (MOUND[1] + pr) * S], fill=YELLOW + (int(255 * a),))
        if t > T["rho"]:
            k = ramp(t, T["rho"], T["rho"] + 0.15)
            d.ellipse([(RHO[0] - 9) * S, (RHO[1] - 9) * S, (RHO[0] + 9) * S, (RHO[1] + 9) * S], fill=(230, 60, 50, int(255 * k)))
        im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        put1(im, l_m, 300, 1010, scale=min(pop(t, 0.15, 0.3), 1.06))
        put1(im, l_t, TROY[0], TROY[1] + 52, scale=min(pop(t, 0.3, 0.3), 1.06))
        if u > 0.5:
            put1(im, l_d, (MOUND[0] + TROY[0]) / 2 + 40, (MOUND[1] + TROY[1]) / 2 + 30, scale=min(pop(t, T["line"] + 0.2, 0.3), 1.06))
        if t > T["rho"]:
            put1(im, l_r, 640, 800, scale=min(pop(t, T["rho"], 0.3), 1.05))
        frames.append(im.convert("RGB"))
    return frames


# ---------- raksasa ----------
FEET, PX_M = 1188, 98          # 5 m = 490 px: the skeleton's skull top sits at y ~698, under the two-line title
GX, PXP = 420, 800             # skeleton and person centres


def skeleton(h):
    """a simple front-view skeleton h px tall, feet at (0, 0) of a local frame (y up), as line segments and circles"""
    u = h / 100
    segs, rings = [], []
    rings.append(((0, 93), 6.5 * u))                                   # skull
    segs += [((0, 86.5), (0, 52))]                                     # spine
    for k in range(5):                                                 # ribs
        y = 80 - 5 * k
        w = 9 - 0.6 * k
        segs += [((0, y), (-w, y - 3)), ((0, y), (w, y - 3))]
    segs += [((-11, 82), (11, 82))]                                    # collarbones
    segs += [((-11, 82), (-15, 63)), ((-15, 63), (-17, 47)), ((11, 82), (15, 63)), ((15, 63), (17, 47))]   # arms
    segs += [((-8, 52), (8, 52)), ((-8, 52), (-6, 46)), ((8, 52), (6, 46))]                               # pelvis
    segs += [((-6, 47), (-7, 25)), ((-7, 25), (-7, 3)), ((6, 47), (7, 25)), ((7, 25), (7, 3))]             # legs
    segs += [((-7, 3), (-12, 0)), ((7, 3), (12, 0))]                                                        # feet
    return [((a[0] * u, a[1] * u), (b[0] * u, b[1] * u)) for a, b in segs], [((c[0] * u, c[1] * u), r) for c, r in rings]


def person_sprite(h):
    sp = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(sp)
    u = h / 100

    def P(x, y):
        return ((PXP + x * u) * S, (FEET - y * u) * S)
    col = (190, 196, 206, 255)
    d.ellipse([*P(-6.5, 100), *P(6.5, 87)], fill=col)
    d.rounded_rectangle([*P(-11, 85), *P(11, 48)], radius=int(5 * u * S), fill=col)
    d.line([P(-8, 50), P(-7, 2)], fill=col, width=int(7 * u * S))
    d.line([P(8, 50), P(7, 2)], fill=col, width=int(7 * u * S))
    d.line([P(-12, 82), P(-15, 50)], fill=col, width=int(5 * u * S))
    d.line([P(12, 82), P(15, 50)], fill=col, width=int(5 * u * S))
    return sp.resize((W, H), Image.LANCZOS)


def skema_raksasa(times=None):
    bg = graded("img/6062044.jpg", 0.5, 0.5, 0.28, blur=10, sepia=True)
    segs, rings = skeleton(5 * PX_M)
    full = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(full)
    bone = (238, 228, 205, 255)
    for (a, b) in segs:
        d.line([((GX + a[0]) * S, (FEET - a[1]) * S), ((GX + b[0]) * S, (FEET - b[1]) * S)], fill=bone, width=9 * S)
    for (c, r) in rings:
        d.ellipse([(GX + c[0] - r) * S, (FEET - c[1] - r) * S, (GX + c[0] + r) * S, (FEET - c[1] + r) * S], outline=bone, width=8 * S)
        d.ellipse([(GX + c[0] - r * 0.45) * S, (FEET - c[1] - r * 0.15) * S, (GX + c[0] - r * 0.1) * S, (FEET - c[1] + r * 0.2) * S], fill=bone)
        d.ellipse([(GX + c[0] + r * 0.1) * S, (FEET - c[1] - r * 0.15) * S, (GX + c[0] + r * 0.45) * S, (FEET - c[1] + r * 0.2) * S], fill=bone)
    skel = full.resize((W, H), Image.LANCZOS)
    pers = person_sprite(1.7 * PX_M)
    ruler = Image.new("RGBA", (W * S, H * S))
    dr = ImageDraw.Draw(ruler)
    dr.line([(110 * S, FEET * S), (110 * S, (FEET - 5 * PX_M) * S)], fill=WHITE + (220,), width=4 * S)
    fm = ImageFont.truetype(XB, 30 * S)
    for m in range(6):
        y = FEET - m * PX_M
        dr.line([(98 * S, y * S), (130 * S, y * S)], fill=WHITE + (220,), width=4 * S)
        if m and not 935 <= y <= 985:
            dr.text((140 * S, y * S), f"{m} m", font=fm, fill=WHITE + (220,), anchor="lm")
    ruler = ruler.resize((W, H), Image.LANCZOS)
    l_p = pill("manusia ±1,7 m", 28, col=WHITE, bg=(10, 14, 24, 215), pad=(16, 8))
    l_g = pill("11 hasta ≈ 5 METER", 36, col=(20, 20, 20), bg=YELLOW + (240,), edge=WHITE + (220,), pad=(22, 10))
    src = pill("kisah Philostratus, ±abad ke-3 M", 26, col=(230, 230, 235), bg=(10, 14, 24, 200))
    frames = []
    for i in range(N["raksasa"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        a = ramp(t, 0.0, 0.2)
        r = ruler.copy()
        r.putalpha(r.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(r)
        p = pers.copy()
        p.putalpha(p.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(p)
        g = ease((t - T["grow0"]) / (T["grow1"] - T["grow0"]))
        if g > 0:   # the skeleton is revealed from the feet up, with a bright line at the edge
            top = round(FEET + 6 - (5 * PX_M + 20) * g)
            s2 = skel.copy()
            m = Image.new("L", (W, H))
            ImageDraw.Draw(m).rectangle([0, top, W, H], fill=255)
            s2.putalpha(Image.fromarray((np.asarray(s2.getchannel("A"), np.float32) * np.asarray(m, np.float32) / 255).astype(np.uint8)))
            im.alpha_composite(s2)
            if g < 1:
                ImageDraw.Draw(im).line([(GX - 120, top), (GX + 120, top)], fill=YELLOW + (200,), width=3)
            hm = 5 * g
            meter = pill(f"{hm:.1f} m".replace(".", ","), 30, col=(20, 20, 20), bg=YELLOW + (235,), pad=(14, 7))
            if g < 1:
                put1(im, meter, 200, top)
        put1(im, l_p, 948, 1110, a=a)
        if t > T["five"]:
            put1(im, l_g, 720, 760, scale=min(pop(t, T["five"], 0.3), 1.08))
        if t > T["src"]:
            put1(im, src, 720, 830, a=ramp(t, T["src"], T["src"] + 0.2))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"desa": skema_desa, "penampang": skema_penampang, "peta": skema_peta, "raksasa": skema_raksasa}

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
