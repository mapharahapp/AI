"""Schematic animations and the cover for Titik Heran #81 (run in the episode work dir; needs ../geo/ne_10m_land.geojson
and ../geo/ne_50m_land.geojson from Natural Earth, see skema68).
pulau: North Maluku close-up (380 px per degree, north up): Ternate, Tidore, Moti, Makian and Bacan light up one by one
  with a pin and a name pill, Halmahera to the east, pill "tempat asal cengkeh". Until the colonial era cloves grew only
  on these small islands (naskah #81 section 1).
peta: East Asia (15,7 px per degree): a dashed straight line draws from North Maluku (Ternate) to Luoyang, the Eastern
  Han capital; great-circle distance Ternate-Luoyang ~4.070 km, so the title says "+-4.000 KM" and the tag says
  "jarak garis lurus" (the real trade went by sea through many hands).
cover: img/cover81.jpg from Arif's H6 (red lacquer box of cloves): title "CENGKEH MALUKU / DIKIRA RACUN" in the dark
  upper third, small "ilustrasi" tag.
Event times are seconds from the start of each clip, read off `render.py 81 plan`. Text stays out of the watermark
band (y 935-985), the title zone (y < ~620) and the captions (y >= 1210).
usage: python3 skema81.py [pulau|peta|cover ...] [--sheet out.jpg t1,t2,...]
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed, text_sprite
from skema35 import sheet
from skema37 import to_img, put1, noise
from skema46 import pill, ease, wanted
from skema68 import pulse

WHITE, CLOVE = (255, 255, 255), (150, 62, 40)
N = {"pulau": 60, "peta": 64}
# from `render.py 81 plan`: pulau = shot 14 ("pulau-pulau" 0.05, "kecil" 0.66, "Maluku..." 0.96, cut 1.80);
# peta = shot 15 ("empat" 0.03, "ribu" 0.37, "kilometer" 0.75, "jauhnya!" 1.21, cut 1.97)
YY = np.mgrid[0:H, 0:W][0].astype(np.float32)


def land_layer(path, proj, box, fill, outline):
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    polys = []
    for f in json.load(open(path))["features"]:
        g = f["geometry"]
        for p in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            ring = p[0]
            xs, ys = [q[0] for q in ring], [q[1] for q in ring]
            if max(xs) < box[0] or min(xs) > box[1] or max(ys) < box[2] or min(ys) > box[3]:
                continue
            pts = [proj(*q) for q in ring]
            polys.append((ring, pts))
            d.polygon([(x * S, y * S) for x, y in pts], fill=fill, outline=outline)
    return lay.resize((W, H), Image.LANCZOS), polys


def inside(ring, lon, lat):
    c = False
    for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]):
        if (y0 > lat) != (y1 > lat) and lon < x0 + (lat - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def sea(top=(10, 40, 70), bottom=(8, 28, 52)):
    u = (YY / H)[..., None]
    return np.array(top, np.float32) * (1 - u) + np.array(bottom, np.float32) * u


def finish(im, top=640):
    """texture plus dark bands under the titles and the captions"""
    a = np.asarray(im, np.float32)
    tex = noise((H, W), [(40, 0.6), (9, 0.4)], 3)[..., None]
    a[..., :3] *= 0.92 + 0.16 * tex
    shade = np.clip(np.maximum((top - YY) / 380, (YY - 1180) / 260), 0, 1)[..., None] * 0.8
    a[..., :3] *= 1 - shade
    return to_img(a).convert("RGBA")


# ---------- pulau: North Maluku ----------
K1, LON1, LAT1, Y1 = 380.0, 126.225, 0.79, 680   # Ternate (127.33 E, 0.79 N) at (420, 680)


def xy1(lon, lat):
    return ((lon - LON1) * K1, Y1 + (LAT1 - lat) * K1)


ISLANDS = [  # name, (lon, lat) of a point on the island, label centre, event time
    ("Ternate", (127.33, 0.80), (205, 672), 0.10),
    ("Tidore", (127.40, 0.68), (230, 732), 0.30),
    ("Moti", (127.42, 0.46), (265, 806), 0.50),
    ("Makian", (127.40, 0.32), (245, 866), 0.68),
    ("Bacan", (127.50, -0.62), (225, 1140), 0.86),
]


def skema_pulau(times=None):
    base = Image.fromarray(sea().astype(np.uint8)).convert("RGBA")
    lay, polys = land_layer("../geo/ne_10m_land.geojson", xy1, (126.0, 129.5, -1.6, 2.2), (70, 96, 62, 255), (150, 178, 120, 255))
    base.alpha_composite(lay)
    base = finish(base)
    hl = []
    for name, (lon, lat), lab, t0 in ISLANDS:
        ring = next((r for r, _ in polys if inside(r, lon, lat)), None)
        L = Image.new("RGBA", (W * S, H * S))
        if ring:
            ImageDraw.Draw(L).polygon([(x * S, y * S) for x, y in (xy1(*q) for q in ring)], fill=YELLOW + (255,), outline=WHITE + (255,))
        else:   # Moti is missing from Natural Earth 10m: a small oval of its size (~6 x 5 km)
            cx, cy = xy1(lon, lat)
            ImageDraw.Draw(L).ellipse([(cx - 11) * S, (cy - 9) * S, (cx + 11) * S, (cy + 9) * S], fill=YELLOW + (255,), outline=WHITE + (255,))
        hl.append((L.resize((W, H), Image.LANCZOS), pill(name, 30, (20, 20, 20), YELLOW + (240,), (255, 255, 255, 200)), xy1(lon, lat), lab, t0))
    hal = pill("Halmahera", 26, (220, 230, 210), (10, 20, 30, 170))
    asal = pill("tempat asal cengkeh", 30, WHITE, CLOVE + (235,), (255, 255, 255, 180), pad=(24, 12))
    frames = []
    for i in range(N["pulau"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        put1(im, hal, 760, 760, a=ramp(t, 0.0, 0.25))
        for L, lab_sp, (px, py), (lx, ly), t0 in hl:
            a = ramp(t, t0, t0 + 0.15)
            if a <= 0:
                continue
            Lc = L.copy()
            Lc.putalpha(Lc.getchannel("A").point(lambda v, a=a: int(v * a)))
            im.alpha_composite(Lc)
            d = ImageDraw.Draw(im)
            d.line([(lx + lab_sp.width / (2 * S) - 6, ly), (px - 12, py)], fill=(255, 255, 255, int(200 * a)), width=3)
            put1(im, lab_sp, lx, ly, scale=min(pop(t, t0, 0.3), 1.08))
        put1(im, asal, 300, 1046, scale=min(pop(t, 1.05, 0.3), 1.06))
        frames.append(im.convert("RGB"))
    return frames


# ---------- peta: North Maluku -> Luoyang ----------
K2, LON2, Y2 = 15.7, 85.5, 640   # Luoyang (112.45 E, 34.62 N) sits at y 640


def xy2(lon, lat):
    return ((lon - LON2) * K2, Y2 + (34.62 - lat) * K2)


LUOYANG, TERNATE = xy2(112.45, 34.62), xy2(127.33, 0.79)


def skema_peta(times=None):
    base = Image.fromarray(sea().astype(np.uint8)).convert("RGBA")
    lay, _ = land_layer("../geo/ne_50m_land.geojson", xy2, (80.0, 160.0, -50.0, 80.0), (82, 94, 64, 255), (150, 166, 120, 255))
    base.alpha_composite(lay)
    base = finish(base, top=600)
    lu = pill("Luoyang · ibu kota Han", 28, WHITE, (10, 14, 24, 220))
    ma = pill("Maluku Utara", 28, (20, 20, 20), YELLOW + (240,), (255, 255, 255, 200))
    cn = pill("TIONGKOK", 24, (225, 225, 210), (0, 0, 0, 0), (0, 0, 0, 0))
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        put1(im, cn, xy2(102.0, 27.0)[0], xy2(102.0, 27.0)[1], a=ramp(t, 0.0, 0.3))
        u = ease((t - 0.08) / 1.05)
        L = Image.new("RGBA", (W * S, H * S))
        if u > 0.01:
            dl = ImageDraw.Draw(L)
            L_len = ((LUOYANG[0] - TERNATE[0]) ** 2 + (LUOYANG[1] - TERNATE[1]) ** 2) ** 0.5
            dashed(dl, [TERNATE, LUOYANG], (20, 20, 20, 170), 11, dash=26, gap=14, upto=u * L_len)
            dashed(dl, [TERNATE, LUOYANG], YELLOW + (255,), 7, dash=26, gap=14, upto=u * L_len)
        im.alpha_composite(L.resize((W, H), Image.LANCZOS))
        pulse(im, TERNATE[0], TERNATE[1], (255, 210, 0), t, 0.0)
        put1(im, ma, TERNATE[0] + 10, TERNATE[1] + 52, a=ramp(t, 0.0, 0.2))
        if t > 1.1:
            pulse(im, LUOYANG[0], LUOYANG[1], (255, 70, 50), t, 1.1)
            put1(im, lu, LUOYANG[0] + 20, LUOYANG[1] + 50, scale=min(pop(t, 1.1, 0.3), 1.06))
        frames.append(im.convert("RGB"))
    return frames


# ---------- cover ----------
def cover():
    im = Image.open("img/H6.jpg").convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")
    a = np.asarray(im, np.float32)
    a[..., :3] *= 1 - np.clip((760 - YY) / 520, 0, 1)[..., None] * 0.45   # a little darker behind the title
    im = to_img(a).convert("RGBA")
    t = text_sprite([("CENGKEH MALUKU", 92, YELLOW, True), ("DIKIRA RACUN", 104, WHITE, True)], gap=10)
    put1(im, t, 540, 400)
    put1(im, pill("ilustrasi", 24, WHITE), 960, 1860)
    im.convert("RGB").save("img/cover81.jpg", quality=93)
    print("img/cover81.jpg")


if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or ["pulau", "peta", "cover"]
    fns = {"pulau": skema_pulau, "peta": skema_peta}
    for name in todo:
        if name == "cover":
            cover()
            continue
        fr = fns[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, f"clips/skema_{name}.mp4")
