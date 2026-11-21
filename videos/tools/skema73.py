"""Schematic animations for Titik Heran #73 (run in the episode work dir; needs ../geo/ne_50m_land.geojson and
../geo/ne_10m_land.geojson from Natural Earth; writes clips/skema_dunia.mp4, skema_jawa.mp4, skema_fosil.mp4 and
skema_nature.mp4).
dunia: dark world map (Natural Earth 1:50m); Homo erectus sites light up one after another (East Africa, Dmanisi in
  Georgia, Zhoukoudian in China, Sangiran in Java) along dashed routes, then go grey one by one until only Java glows,
  with a yellow "JAWA ?" pill on "Indonesia".
jawa: Java from Natural Earth 1:10m; the Bengawan Solo is drawn from Wonogiri past Surakarta, Ngandong and Cepu to its
  mouth near Gresik (a schematic course through those towns: Natural Earth has no Solo River), and a yellow pin
  "NGANDONG, BLORA" pops on "Solo".
fosil: Arif's Higgsfield H2 (a skull cap in river sand, AI illustration) with a slow push; a card with 12 skull-cap
  icons (the 12 calvaria Oppenoorth and ter Haar dug up in 1931-1933), "117-108 ribu tahun lalu (Nature, 2020)".
nature: a white journal-style card (plain text, no logo) slides up: "jurnal Nature · 18 Nov 2026", "Homo erectus di gua
  Baxian & Naxian", "Guangxi, China", "324-184 ribu tahun lalu". The rainforest finding itself is left to the VO.
Event times are seconds from the start of each clip, read off `render.py 73 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < ~640) and the captions (y >= 1210).
usage: python3 skema73.py [dunia|jawa|fosil|nature ...] [--sheet out.jpg t1,t2,...]
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed, text_sprite
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted, path_upto, smooth_open
from skema70 import push

WHITE, GREY = (255, 255, 255), (120, 128, 140)
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
N = {"dunia": 88, "jawa": 56, "fosil": 62, "nature": 68}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 73 plan`: dunia "ternyata" 0.05, "bertahan" 0.63, "paling" 0.98, "akhir" 1.30, "Indonesia" 1.77, cut 2.73;
# jawa "Bengawan" 0.03, "Solo" 0.42, "sekitar" 1.21, cut 1.70; fosil "seratus" 0.05, "sepuluh" 0.52, "ribu" 0.84,
# "tahun" 1.07, "lalu" 1.38, cut 1.97; nature "Tapi" 0.03, "studi" 0.55, "baru" 0.94, "jurnal" 1.33, "Neicer" 1.65, cut 2.17
T = {"route0": 0.05, "route1": 0.85, "off": (0.95, 1.15, 1.35), "java": 1.72, "zoom0": 1.6,
     "river0": 0.04, "river1": 0.9, "pin": 0.42,
     "icons0": 0.25, "icons1": 0.85, "age": 1.05, "dug": 0.9,
     "card": 0.0, "l1": 0.12, "l2": 0.52, "l3": 0.72, "l4": 1.0}

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def sea(top=(14, 30, 52), bot=(5, 11, 22)):
    v = (YY / H)[..., None]
    return to_img(np.array(top, np.float32) * (1 - v) + np.array(bot, np.float32) * v).convert("RGBA")


def land(px, box, fname, fill, edge):
    lon0, lon1, lat0, lat1 = box
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for f in json.load(open(f"../geo/{fname}"))["features"]:
        g = f["geometry"]
        for p in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            ring = p[0]
            xs, ys = [q[0] for q in ring], [q[1] for q in ring]
            if max(xs) < lon0 or min(xs) > lon1 or max(ys) < lat0 or min(ys) > lat1:
                continue
            d.polygon([tuple(c * S for c in px(*q)) for q in ring], fill=fill, outline=edge)
    return lay.resize((W, H), Image.LANCZOS)


def dot(im, x, y, col, a=1.0, r=11, ring=None):
    if a <= 0.01:
        return
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    if ring is not None:
        rr = r + 40 * ring
        d.ellipse([(x - rr) * S, (y - rr) * S, (x + rr) * S, (y + rr) * S], outline=col + (int(220 * (1 - ring) * a),),
                  width=4 * S)
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=col + (int(255 * a),),
              outline=(255, 255, 255, int(230 * a)), width=3 * S)
    lay = lay.resize((W, H), Image.LANCZOS)
    g = lay.filter(ImageFilter.GaussianBlur(8))
    im.alpha_composite(g)
    im.alpha_composite(lay)


def label(text, size=26, col=WHITE):
    return text_sprite([(text, size, col, True)])


# ---------- dunia ----------
D_LON0, D_LON1, D_LAT1 = 22.0, 130.0, 41.3
DK = W / (D_LON1 - D_LON0)
D_Y0 = 700
TOPFADE = np.clip((680 - YY) / 260, 0, 1)[..., None] * 0.75          # land under the titles is dimmed


def dpx(lon, lat):
    return ((lon - D_LON0) * DK, D_Y0 + (D_LAT1 - lat) * DK)


SITES = {"afrika": (36.0, 3.6), "georgia": (44.3, 41.3), "china": (115.9, 39.7), "jawa": (110.8, -7.45)}
ROUTES = [[(36.0, 3.6), (39.5, 16), (42, 30), (44.3, 41.3)],
          [(44.3, 41.3), (60, 42), (80, 42), (100, 41), (115.9, 39.7)],
          [(36.0, 3.6), (45, 13), (58, 22), (75, 21), (92, 21), (100, 10), (104, 1), (110.8, -7.45)]]
ROUTE_T = [(0.05, 0.35), (0.3, 0.62), (0.1, 0.8)]
SITE_T = {"afrika": 0.05, "georgia": 0.35, "china": 0.62, "jawa": 0.8}
OFF = {"afrika": T["off"][0], "georgia": T["off"][1], "china": T["off"][2]}
LAB = {"afrika": ("Afrika", 20, 46), "georgia": ("Georgia", 30, -44), "china": ("China", -20, -44), "jawa": ("Jawa", -84, 0)}


def skema_dunia(times=None):
    base = sea()
    base.alpha_composite(land(dpx, (D_LON0 - 5, D_LON1 + 5, -45, 60), "ne_50m_land.geojson", (40, 58, 62, 255),
                              (96, 126, 132, 255)))
    base = to_img(np.asarray(base.convert("RGB"), np.float32) * (1 - TOPFADE)).convert("RGBA")
    pts = {k: dpx(*v) for k, v in SITES.items()}
    routes = [smooth_open([dpx(*q) for q in r], 3) for r in ROUTES]
    labs = {k: label(v[0], 32) for k, v in LAB.items()}
    q = pill("JAWA ?", 40, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220), pad=(24, 12))
    frames = []
    for i in range(N["dunia"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        lay = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(lay)
        for r, (a0, a1) in zip(routes, ROUTE_T):
            u = ease((t - a0) / (a1 - a0))
            if u <= 0:
                continue
            fadeoff = 1 - 0.7 * ramp(t, T["off"][0], T["off"][2] + 0.2)
            L = sum(math.dist(p, q2) for p, q2 in zip(r, r[1:]))
            dashed(d, r, (255, 225, 0, int(200 * fadeoff)), 4, dash=18, gap=12, upto=L * u)
        im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        for k, (x, y) in pts.items():
            a = ramp(t, SITE_T[k], SITE_T[k] + 0.12)
            if a <= 0:
                continue
            if k == "jawa":
                big = ramp(t, T["java"], T["java"] + 0.25)
                ph = ((t - T["java"]) % 0.8) / 0.8 if t > T["java"] else None
                dot(im, x, y, YELLOW, a, 11 + 6 * big, ring=ph)
            else:
                off = ramp(t, OFF[k], OFF[k] + 0.15)
                col = tuple(int(c0 + (c1 - c0) * off) for c0, c1 in zip(YELLOW, GREY))
                dot(im, x, y, col, a * (1 - 0.45 * off), 11 - 3 * off)
            lt, dx, dy = LAB[k]
            la = a * (1 - 0.6 * (ramp(t, OFF[k], OFF[k] + 0.15) if k in OFF else 0))
            put1(im, labs[k], x + dx, y + dy, a=la)
        jx, jy = pts["jawa"]
        if t > T["zoom0"]:
            im = push(im, t - T["zoom0"], 1.1, 1.0, 1.22, jx, jy)
        put1(im, q, 700, 1096, scale=min(pop(t, T["java"] + 0.05, 0.3), 1.06))
        frames.append(im.convert("RGB"))
    return frames


# ---------- jawa ----------
J_LON0, J_LAT1, JK = 104.9, -5.75, 108.0
J_Y0 = 720


def jpx(lon, lat):
    return ((lon - J_LON0) * JK, J_Y0 + (J_LAT1 - lat) * JK)


SOLO = [(110.93, -7.82), (110.86, -7.70), (110.84, -7.57), (110.95, -7.47), (111.03, -7.42), (111.20, -7.37),
        (111.40, -7.32), (111.48, -7.24), (111.59, -7.15), (111.75, -7.17), (111.88, -7.15), (112.05, -7.12),
        (112.17, -7.11), (112.35, -7.01), (112.56, -6.90)]
NGANDONG = (111.40, -7.32)


def skema_jawa(times=None):
    base = sea((12, 34, 60), (5, 13, 26))
    base.alpha_composite(land(jpx, (104, 116, -9.5, -5.0), "ne_10m_land.geojson", (58, 96, 62, 255), (150, 196, 150, 255)))
    river = smooth_open([jpx(*q) for q in SOLO], 3)
    nx, ny = jpx(*NGANDONG)
    pin = pill("NGANDONG, BLORA", 34, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220))
    rl = label("Bengawan Solo", 28, (150, 215, 255))
    jl = label("JAWA", 30, (220, 236, 220))
    frames = []
    for i in range(N["jawa"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        u = ease((t - T["river0"]) / (T["river1"] - T["river0"]))
        if u > 0:
            lay = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(lay)
            p = path_upto(river, u)
            if len(p) > 1:
                d.line([(x * S, y * S) for x, y in p], fill=(90, 180, 255, 255), width=9 * S, joint="curve")
            lay = lay.resize((W, H), Image.LANCZOS)
            g = lay.filter(ImageFilter.GaussianBlur(7))
            im.alpha_composite(g)
            im.alpha_composite(lay)
        put1(im, jl, 300, 1010, a=ramp(t, 0.0, 0.2) * 0.85)
        put1(im, rl, 600, 1012, a=ramp(t, 0.25, 0.45))
        ph = ((t - T["pin"]) % 0.8) / 0.8 if t > T["pin"] else None
        dot(im, nx, ny, YELLOW, ramp(t, T["pin"], T["pin"] + 0.1), 12, ring=ph)
        im = push(im, t, 1.8, 1.0, 1.3, nx, ny)
        put1(im, pin, nx + 40, ny - 92, scale=min(pop(t, T["pin"] + 0.05, 0.3), 1.06))
        frames.append(im.convert("RGB"))
    return frames


# ---------- fosil ----------
def cap_icon(col=(236, 226, 204)):
    sp = Image.new("RGBA", (70 * S, 40 * S))
    d = ImageDraw.Draw(sp)
    pts = [(6, 30), (4, 22), (10, 14), (22, 8), (38, 6), (52, 10), (62, 18), (64, 28), (56, 32), (14, 32)]
    d.polygon([(x * S, y * S) for x, y in pts], fill=col + (255,), outline=(90, 70, 50, 255))
    d.line([(4 * S, 22 * S), (14 * S, 20 * S), (22 * S, 22 * S)], fill=(150, 120, 90, 255), width=2 * S)   # brow ridge
    return sp


def skema_fosil(times=None):
    src = Image.open("img/H2.jpg").convert("RGB")
    sc_ = max(W / src.width, H / src.height)
    src = src.resize((round(src.width * sc_), round(src.height * sc_)), Image.LANCZOS)
    x0, y0 = (src.width - W) // 2, (src.height - H) // 2
    bg = src.crop((x0, y0, x0 + W, y0 + H)).convert("RGBA")
    icon = cap_icon()
    age = pill("117–108 ribu tahun lalu · Nature, 2020", 30, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220))
    dug = label("12 tempurung kepala, digali 1931–1933", 30)
    frames = []
    for i in range(N["fosil"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = push(bg, t, 2.1, 1.0, 1.05, 540, 600)
        card = Image.new("RGBA", (W, H))
        a = ramp(t, 0.1, 0.3)
        ImageDraw.Draw(card).rounded_rectangle([80, 1000, 1000, 1196], radius=28, fill=(8, 8, 10, int(190 * a)),
                                               outline=(255, 255, 255, int(70 * a)), width=2)
        im.alpha_composite(card)
        for k in range(12):
            tk = T["icons0"] + (T["icons1"] - T["icons0"]) * k / 11
            put1(im, icon, 145 + k * 72, 1040, scale=min(pop(t, tk, 0.25), 1.08))
        put1(im, dug, 540, 1096, a=ramp(t, T["dug"], T["dug"] + 0.2))
        put1(im, age, 540, 1158, scale=min(pop(t, T["age"], 0.3), 1.06))
        frames.append(im.convert("RGB"))
    return frames


# ---------- nature ----------
def skema_nature(times=None):
    v = (YY / H)[..., None]
    bg = to_img(np.array([18, 44, 30], np.float32) * (1 - v) + np.array([5, 14, 9], np.float32) * v).convert("RGBA")
    CW, CH, CX0, CY0 = 860, 520, 110, 668
    card = Image.new("RGBA", (CW * S, CH * S))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, CW * S - 1, CH * S - 1], radius=22 * S, fill=(250, 248, 242, 255))
    d.rectangle([0, 0, CW * S, 14 * S], fill=(24, 92, 60, 255))
    F = lambda f, s: ImageFont.truetype(f, s * S)
    lines = [("jurnal Nature · 18 Nov 2026", F(XB, 46), (24, 92, 60), 62, "l1"),
             ("Homo erectus di gua Baxian & Naxian", F(MED, 38), (40, 40, 40), 146, "l2"),
             ("Guangxi, China", F(XB, 64), (20, 20, 20), 212, "l3"),
             ("324–184 ribu tahun lalu", F(XB, 46), (20, 20, 20), 396, "l4")]
    sprites = []
    for text, font, col, y, key in lines:
        lay = Image.new("RGBA", (CW * S, CH * S))
        ImageDraw.Draw(lay).text((54 * S, y * S), text, font=font, fill=col + (255,))
        sprites.append((lay, key))
    hl = Image.new("RGBA", (CW * S, CH * S))
    ImageDraw.Draw(hl).rounded_rectangle([38 * S, 382 * S, 660 * S, 462 * S], radius=14 * S, fill=YELLOW + (255,))
    rule = Image.new("RGBA", (CW * S, CH * S))
    ImageDraw.Draw(rule).line([(54 * S, 330 * S), ((CW - 54) * S, 330 * S)], fill=(200, 196, 186, 255), width=3 * S)
    frames = []
    for i in range(N["nature"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        c = card.copy()
        c.alpha_composite(rule)
        if t > T["l4"]:
            h2 = hl.copy()
            h2.putalpha(h2.getchannel("A").point(lambda q, a=ramp(t, T["l4"], T["l4"] + 0.15): int(q * a)))
            c.alpha_composite(h2)
        for lay, key in sprites:
            a = ramp(t, T[key], T[key] + 0.18)
            if a > 0:
                l2 = lay.copy()
                l2.putalpha(l2.getchannel("A").point(lambda q, a=a: int(q * a)))
                c.alpha_composite(l2)
        c = c.resize((CW, CH), Image.LANCZOS)
        im = bg.copy()
        sh = Image.new("RGBA", (W, H))
        y = CY0 + 700 * (1 - ease(t / 0.35))
        ImageDraw.Draw(sh).rounded_rectangle([CX0 + 10, y + 18, CX0 + CW + 10, y + CH + 18], radius=22, fill=(0, 0, 0, 120))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
        im.alpha_composite(c, (CX0, round(y)))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"dunia": skema_dunia, "jawa": skema_jawa, "fosil": skema_fosil, "nature": skema_nature}

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
