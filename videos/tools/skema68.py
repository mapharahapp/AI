"""Schematic animations for Titik Heran #68 (run in the episode work dir; needs img/7963244.jpg and ../geo/ne_50m_land.geojson
+ ../geo/ne_50m_rivers.geojson from Natural Earth; writes clips/skema_peta.mp4, skema_denah.mp4, skema_lebar.mp4, skema_rute.mp4).
peta: northern China at 60 px per degree with the Yellow River loop; the Qin Straight Road (Zhidao) is drawn as a straight
  yellow line from Xianyang (the capital) up to Jiuyuan (Baotou), "700+ KM" pops, then the Mu Us sand patch and a red pulse
  "Huangtuliang, Yulin". The road is drawn straight between its two ends: the real line is only partly traced, so the clip
  is labelled "skema, rute perkiraan"; the site position is approximate (Balasu, Yuyang district).
denah: the suspected lodging palace's footprint (core ±10.000 m²) rises out of the rippled sand photo, seen from above,
  with pills "±10.000 M²" and "diduga istana singgah kaisar".
lebar: a road band running into the distance, a span arrow "20–60 M" and little soldiers marching up it.
rute: the same map with the road already drawn: the convoy's dashed route from Shaqiu (where the emperor died) north to
  Jiuyuan, then a cart icon runs down the straight road to Xianyang, where the death was announced (Shiji).
Event times are seconds from the start of each clip, read off `render.py 68 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 700) and the captions (y >= 1210).
usage: python3 skema68.py [peta|denah|lebar|rute ...] [--sheet out.jpg t1,t2,...]
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed
from skema35 import sheet
from skema37 import to_img, put1, noise
from skema46 import pill, ease, wanted, path_upto
from skema61 import cover

N = {"peta": 86, "denah": 52, "lebar": 60, "rute": 62}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 68 plan`: peta "jalan" 0.04, "tol" 0.48, "tujuh" 0.90, "kilometer" 1.55; denah "terkubur" 0.05, "pasir" 0.62,
# "gurun" 0.93; lebar "Jalan" 0.05, "selebar" 0.44, "puluhan" 0.82, "meter" 1.12; rute "lalu" 0.03, "pulang" 0.57,
# "lewat" 0.91, "jalan" 1.14, "ini" 1.41
T = {"road0": 0.1, "road1": 1.5, "km": 0.9, "site": 1.85,
     "rise0": 0.05, "rise1": 0.85, "area": 0.85, "dug": 1.1,
     "band": 0.0, "span": 0.8,
     "conv0": 0.0, "conv1": 0.5, "cart0": 0.55, "cart1": 1.6, "xy": 1.55}
WHITE = (255, 255, 255)

# ---------- map ----------
LON0, LAT1, K, Y0 = 101.0, 41.8, 60.0, 700   # lat 41.8 N sits at y 700, 60 px per degree


def xy(lon, lat):
    return ((lon - LON0) * K, Y0 + (LAT1 - lat) * K)


XIANYANG, JIUYUAN = xy(108.70, 34.33), xy(109.82, 40.65)
SITE = xy(109.55, 38.50)                      # Huangtuliang, Balasu, Yuyang (Yulin): approximate
SHAQIU = xy(115.20, 37.00)
CONVOY = [SHAQIU, xy(114.0, 38.1), xy(112.8, 39.6), xy(111.2, 40.4), JIUYUAN]
MUUS = [(107.3, 39.3), (108.6, 39.65), (110.0, 39.35), (110.6, 38.7), (110.2, 38.0), (109.0, 37.6), (107.8, 37.7), (107.2, 38.4)]


def base_map():
    """sea, land in a dry earthy tone, the Yellow River, dark bands under the titles and captions"""
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    im = to_img(np.array([14, 34, 66], np.float32) * np.ones((H, W, 1), np.float32)).convert("RGBA")
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for f in json.load(open("../geo/ne_50m_land.geojson"))["features"]:
        g = f["geometry"]
        for p in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            ring = p[0]
            xs, ys = [q[0] for q in ring], [q[1] for q in ring]
            if max(xs) < 85 or min(xs) > 135 or max(ys) < 10 or min(ys) > 60:
                continue
            d.polygon([(x * S, y * S) for x, y in (xy(*q) for q in ring)], fill=(78, 84, 58, 255), outline=(150, 160, 120, 255))
    for f in json.load(open("../geo/ne_50m_rivers.geojson"))["features"]:
        if f["properties"].get("name") != "Huang":
            continue
        g = f["geometry"]
        for line in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
            d.line([(x * S, y * S) for x, y in (xy(*q) for q in line)], fill=(96, 168, 226, 255), width=5 * S, joint="curve")
    im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    tex = noise((H, W), [(40, 0.6), (9, 0.4)], 3)[..., None]
    a = np.asarray(im, np.float32)
    a[..., :3] *= 0.9 + 0.2 * tex
    shade = np.clip(np.maximum((720 - yy) / 420, (yy - 1180) / 260), 0, 1)[..., None] * 0.78   # titles on top, captions below
    a[..., :3] *= 1 - shade
    return to_img(a).convert("RGBA")


def sand_patch():
    lay = Image.new("RGBA", (W * S, H * S))
    ImageDraw.Draw(lay).polygon([(x * S, y * S) for x, y in (xy(*q) for q in MUUS)], fill=(222, 186, 112, 170))
    return lay.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(6))


def city(im, p, a=1.0, col=WHITE):
    if a <= 0:
        return
    d = ImageDraw.Draw(im)
    x, y = p
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=col + (int(255 * a),), outline=(20, 20, 20, int(255 * a)), width=3)


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


def road_layer(u, width=8):
    lay = Image.new("RGBA", (W * S, H * S))
    if u > 0.005:
        pts = path_upto([XIANYANG, JIUYUAN], u)
        d = ImageDraw.Draw(lay)
        d.line([(x * S, y * S) for x, y in pts], fill=(20, 20, 20, 160), width=(width + 6) * S)
        d.line([(x * S, y * S) for x, y in pts], fill=YELLOW + (255,), width=width * S)
    return lay.resize((W, H), Image.LANCZOS)


L_XY = pill("Xianyang · ibu kota", 28)
L_JY = pill("Jiuyuan (kini Baotou)", 28)
L_RIVER = pill("Sungai Kuning", 24, col=(200, 225, 245), bg=(10, 20, 40, 170))


def skema_peta(times=None):
    base = base_map()
    sand = sand_patch()
    km = pill("700+ KM", 52, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(26, 12))
    zd = pill("JALAN LURUS QIN · ±212 SM", 28, col=WHITE, bg=(10, 14, 24, 215))
    site = pill("Huangtuliang, Yulin", 28, col=WHITE, bg=(170, 30, 30, 230))
    musl = pill("Gurun Mu Us", 24, col=(60, 40, 10), bg=(236, 206, 140, 220), edge=(255, 255, 255, 140))
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        s = sand.copy()
        s.putalpha(s.getchannel("A").point(lambda v, a=ramp(t, T["site"] - 0.3, T["site"]): int(v * a)))
        im.alpha_composite(s)
        u = ease((t - T["road0"]) / (T["road1"] - T["road0"]))
        im.alpha_composite(road_layer(u))
        city(im, XIANYANG)
        city(im, JIUYUAN, a=ramp(t, T["road1"] - 0.2, T["road1"]))
        put1(im, L_XY, XIANYANG[0] + 40, XIANYANG[1] + 34, a=ramp(t, 0.0, 0.2))
        put1(im, L_JY, JIUYUAN[0] + 150, JIUYUAN[1] - 6, a=ramp(t, T["road1"] - 0.2, T["road1"]))
        put1(im, L_RIVER, xy(111.3, 36.6)[0] + 40, xy(111.3, 36.6)[1], a=ramp(t, 0.2, 0.5))
        if t > T["km"]:
            put1(im, km, 190, 1040, scale=min(pop(t, T["km"], 0.3), 1.1))
            put1(im, zd, 225, 1112, a=ramp(t, T["km"] + 0.15, T["km"] + 0.35))
        if t > T["site"]:
            pulse(im, SITE[0], SITE[1], (255, 70, 50), t, T["site"])
            put1(im, site, SITE[0] + 200, SITE[1] - 40, scale=min(pop(t, T["site"], 0.3), 1.06))
            put1(im, musl, xy(108.0, 39.95)[0], xy(108.0, 39.95)[1], a=ramp(t, T["site"], T["site"] + 0.25))
        frames.append(im.convert("RGB"))
    return frames


def skema_rute(times=None):
    base = base_map()
    base.alpha_composite(sand_patch())
    base.alpha_composite(road_layer(1.0))
    city(base, XIANYANG)
    city(base, JIUYUAN)
    sq = pill("Shaqiu: kaisar wafat", 28, col=WHITE, bg=(170, 30, 30, 230))
    an = pill("kematian diumumkan", 30, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(22, 10))
    src = pill("rute menurut Shiji, Sima Qian", 24, col=(230, 230, 235), bg=(10, 14, 24, 190))
    road = [JIUYUAN, XIANYANG]
    frames = []
    for i in range(N["rute"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        u = ease((t - T["conv0"]) / (T["conv1"] - T["conv0"]))
        dl = Image.new("RGBA", (W * S, H * S))
        dd = ImageDraw.Draw(dl)
        dashed(dd, path_upto(CONVOY, max(u, 0.01)), (255, 255, 255, 235), 5, dash=16, gap=10)
        v = ease((t - T["cart0"]) / (T["cart1"] - T["cart0"]))
        if v > 0:
            seg = path_upto(road, v)
            dd.line([(x * S, y * S) for x, y in seg], fill=(255, 120, 40, 255), width=9 * S)
        im.alpha_composite(dl.resize((W, H), Image.LANCZOS))
        pulse(im, SHAQIU[0], SHAQIU[1], (255, 70, 50), t, 0.0)
        put1(im, sq, SHAQIU[0] - 70, SHAQIU[1] + 62, a=ramp(t, 0.0, 0.2))
        city(im, XIANYANG)
        put1(im, L_XY, XIANYANG[0] + 40, XIANYANG[1] + 34)
        put1(im, L_JY, JIUYUAN[0] + 150, JIUYUAN[1] - 6)
        # the cart: a small box on two wheels riding the road
        cx, cy = path_upto(road, max(v, 0.0))[-1] if v > 0 else JIUYUAN
        if t > T["cart0"] - 0.1:
            cd = ImageDraw.Draw(im)
            cd.rounded_rectangle([cx - 26, cy - 22, cx + 26, cy + 6], radius=6, fill=(120, 70, 40, 255), outline=(20, 20, 20, 255), width=3)
            for wx in (cx - 16, cx + 16):
                cd.ellipse([wx - 9, cy + 2, wx + 9, cy + 20], fill=(30, 30, 30, 255), outline=(220, 200, 160, 255), width=3)
        if t > T["xy"]:
            put1(im, an, XIANYANG[0] - 175, XIANYANG[1] - 52, scale=min(pop(t, T["xy"], 0.3), 1.08))
        put1(im, src, 250, 1040, a=ramp(t, 0.2, 0.45))
        frames.append(im.convert("RGB"))
    return frames


# ---------- denah ----------
def skema_denah(times=None):
    bg = cover("img/7963244.jpg", 0.5, 0.62)
    a = np.asarray(bg, np.float32) * 0.62
    bg = to_img(a).convert("RGBA")
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    cx, cy, w, h = 540, 860, 640, 420
    wall, dark = (238, 214, 160, 255), (60, 40, 20, 200)
    d.rectangle([(cx - w // 2 + 8) * S, (cy - h // 2 + 10) * S, (cx + w // 2 + 8) * S, (cy + h // 2 + 10) * S], outline=dark, width=16 * S)
    d.rectangle([(cx - w // 2) * S, (cy - h // 2) * S, (cx + w // 2) * S, (cy + h // 2) * S], outline=wall, width=14 * S)
    for x0, y0, x1, y1 in [(-260, -170, -40, -10), (20, -170, 260, -10), (-260, 30, -110, 170), (-70, 30, 90, 170), (130, 30, 260, 170)]:
        d.rectangle([(cx + x0) * S, (cy + y0) * S, (cx + x1) * S, (cy + y1) * S], outline=wall, width=7 * S)
    d.line([(cx - w // 2) * S, (cy + 10) * S, (cx + w // 2) * S, (cy + 10) * S], fill=(120, 190, 230, 230), width=6 * S)   # water channel
    plan = lay.resize((W, H), Image.LANCZOS)
    sandn = noise((H, W), [(60, 0.6), (14, 0.4)], 11)
    area = pill("±10.000 M²", 50, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(26, 12))
    dug = pill("diduga istana singgah kaisar", 30, col=WHITE, bg=(10, 14, 24, 215))
    frames = []
    for i in range(N["denah"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        k = ease((t - T["rise0"]) / (T["rise1"] - T["rise0"]))
        if k > 0:   # sand blows off unevenly: the noise field decides which parts of the walls show first
            m = np.clip((k * 1.4 - sandn) * 4, 0, 1)
            p = plan.copy()
            p.putalpha(to_img(np.asarray(p.getchannel("A"), np.float32) * m).convert("L"))
            im.alpha_composite(p)
        if t > T["area"]:
            put1(im, area, 540, 872, scale=min(pop(t, T["area"], 0.3), 1.1))
        if t > T["dug"]:
            put1(im, dug, 540, 1140, a=ramp(t, T["dug"], T["dug"] + 0.2))
        frames.append(im.convert("RGB"))
    return frames


# ---------- lebar ----------
HZ, BOT = 760, 1200       # horizon and the near edge of the road


def road_x(y, half_near=430, half_far=26):
    k = (y - HZ) / (BOT - HZ)
    return half_far + (half_near - half_far) * k


def skema_lebar(times=None):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = np.array([34, 30, 46], np.float32) * (1 - (yy / HZ)[..., None].clip(0, 1)) + np.array([150, 110, 70], np.float32) * (yy / HZ)[..., None].clip(0, 1)
    ground = np.array([120, 96, 62], np.float32) * np.ones((H, W, 1), np.float32)
    g = noise((H, W), [(30, 0.5), (6, 0.5)], 5)[..., None]
    img = np.where((yy >= HZ)[..., None], ground * (0.85 + 0.3 * g), sky)
    shade = np.clip(np.maximum((720 - yy) / 420, (yy - 1180) / 260), 0, 1)[..., None] * 0.75
    bg = to_img(img * (1 - shade)).convert("RGBA")
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    poly = [(540 - road_x(HZ), HZ), (540 + road_x(HZ), HZ), (540 + road_x(BOT), BOT), (540 - road_x(BOT), BOT)]
    d.polygon([(x * S, y * S) for x, y in poly], fill=(196, 160, 104, 255))
    for sgn in (-1, 1):
        d.line([((540 + sgn * road_x(HZ)) * S, HZ * S), ((540 + sgn * road_x(BOT)) * S, BOT * S)], fill=(250, 230, 180, 255), width=4 * S)
    road = lay.resize((W, H), Image.LANCZOS)
    span = pill("20–60 M", 58, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(28, 12))
    rng = np.random.default_rng(4)
    troops = [(rng.uniform(-0.8, 0.8), rng.uniform(0, 1)) for _ in range(46)]
    frames = []
    for i in range(N["lebar"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        r = road.copy()
        r.putalpha(r.getchannel("A").point(lambda v, a=ramp(t, 0.0, 0.25): int(v * a)))
        im.alpha_composite(r)
        sd = ImageDraw.Draw(im)
        for lx, ph in sorted(troops, key=lambda q: (q[1] + t * 0.18) % 1):
            k = 1 - ((ph + t * 0.18) % 1)              # 1 near, 0 at the horizon: they march away
            y = HZ + (BOT - HZ) * k ** 1.6
            if y > BOT - 10:
                continue
            x = 540 + lx * road_x(y)
            hgt = 6 + 34 * k ** 1.6
            a = int(255 * ramp(t, 0.1, 0.35))
            sd.rectangle([x - hgt * 0.16, y - hgt, x + hgt * 0.16, y - hgt * 0.25], fill=(40, 30, 24, a))
            sd.ellipse([x - hgt * 0.13, y - hgt * 1.22, x + hgt * 0.13, y - hgt * 0.96], fill=(40, 30, 24, a))
            sd.line([(x - hgt * 0.08, y - hgt * 0.25), (x - hgt * 0.1, y)], fill=(40, 30, 24, a), width=max(1, int(hgt * 0.09)))
            sd.line([(x + hgt * 0.08, y - hgt * 0.25), (x + hgt * 0.1, y)], fill=(40, 30, 24, a), width=max(1, int(hgt * 0.09)))
        if t > T["span"]:
            k = ease((t - T["span"]) / 0.3)
            ya = 1110
            half = road_x(ya) * k
            al = Image.new("RGBA", (W * S, H * S))
            ad = ImageDraw.Draw(al)
            ad.line([((540 - half) * S, ya * S), ((540 + half) * S, ya * S)], fill=YELLOW + (255,), width=6 * S)
            for sgn in (-1, 1):
                x = 540 + sgn * half
                ad.polygon([(x * S, ya * S), ((x - sgn * 24) * S, (ya - 14) * S), ((x - sgn * 24) * S, (ya + 14) * S)], fill=YELLOW + (255,))
            im.alpha_composite(al.resize((W, H), Image.LANCZOS))
            put1(im, span, 540, 1040, scale=min(pop(t, T["span"] + 0.1, 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"peta": skema_peta, "denah": skema_denah, "lebar": skema_lebar, "rute": skema_rute}

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
