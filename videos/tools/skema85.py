"""Image prep, schematic animations and the cover for Titik Heran #85 (run in the episode work dir; the map needs
../geo/ne_50m_land.geojson from Natural Earth, see skema68).
prep: img/H5k.jpg (Arif's Higgsfield H5, the envoy handing the golden cage over, cropped to the envoy and the cage so the
  seated emperor's face stays out of the frame).
garis: vertical timeline (not to scale, so the labels fit): +-1230 the cockatoo at Emperor Frederick II's court (Dalton et al.
  2018: the four drawings in De arte venandi cum avibus, made 1241-1248, of a gift sent to Frederick by the "Sultan of
  Babylon", al-Kamil, whose friendship led to the 1229 Treaty of Jaffa), 1292 Marco Polo in Sumatra (the first European
  on record in the archipelago), 1512 the Portuguese reach Maluku. A yellow line runs down the axis on "jauh sebelum".
peta: Natural Earth land, 7,6 px per degree: the possible home range (eastern Indonesia, New Guinea, northern
  Australia; Dalton et al.: a sulphur-crested or Triton cockatoo) hatched, a boat line to Java, then up the South China
  Sea to Canton; then the rest of the route Dalton et al. suggest (overland Silk Road to Cairo, then by sea to Sicily /
  southern Italy) appears as a faint dashed line just before the cut to the caravan.
kartu: the gift card ("Sultan Babilonia" = the Sultan of Egypt al-Kamil, for Emperor Frederick II), with the 4 drawings
  and the 250 years before Mantegna's 1496 painting.
cover: img/cover85.jpg from Pixabay 6604629 (a real sulphur-crested cockatoo) with the title.
Event times are seconds from the start of each clip, read off `render.py 85 plan`. Text stays out of the watermark
band (y 935-985), the title zone (y < ~600) and the captions (y >= 1210).
usage: python3 skema85.py [prep|garis|peta|kartu|cover ...] [--sheet out.jpg t1,t2,...]
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed, text_sprite
from skema35 import sheet
from skema37 import to_img, put1, noise
from skema46 import pill, ease, wanted
from skema68 import pulse
from skema74 import backdrop

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
WHITE, GREY, SAND = (255, 255, 255), (200, 196, 186), (226, 214, 190)
N = {"garis": 172, "peta": 72, "kartu": 54}
# from `render.py 85 plan`: see the shot list in the naskah
T_1230, T_JAUH, T_1292, T_1512, T_NUS = 0.67, 2.29, 3.31, 3.87, 4.39   # garis ("delapan", "jauh", "orang", "sampai", "Nusantara!")
T_JAWA, T_LALU, T_TIONGKOK = 0.21, 1.01, 1.33                            # peta
T_ROWS = (0.0, 0.14, 0.28, 0.45, 0.7, 0.85)                              # kartu
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def left_sprite(lines, gap=6):
    """left-aligned lines of (text, size, colour, bold) with a soft shadow, as a 2x sprite; returns (sprite, width 1x)"""
    fonts = [ImageFont.truetype(XB if b else MED, size * S) for _, size, _, b in lines]
    boxes = [f.getbbox(t) for f, (t, *_) in zip(fonts, lines)]
    m = 16 * S
    w = max(b[2] - b[0] for b in boxes) + 2 * m
    h = sum(b[3] - b[1] for b in boxes) + gap * S * (len(lines) - 1) + 2 * m
    sh, tx = Image.new("RGBA", (w, h)), Image.new("RGBA", (w, h))
    ds, dt = ImageDraw.Draw(sh), ImageDraw.Draw(tx)
    y = m
    for f, b, (t, _, col, _) in zip(fonts, boxes, lines):
        ds.text((m - b[0] + 2 * S, y - b[1] + 3 * S), t, font=f, fill=(0, 0, 0, 210))
        dt.text((m - b[0], y - b[1]), t, font=f, fill=col + (255,))
        y += b[3] - b[1] + gap * S
    sh = sh.filter(ImageFilter.GaussianBlur(4 * S))
    sh.alpha_composite(tx)
    return sh


def put_l(im, sp, x, cy, a=1.0, dx=0.0):
    """sprite with its left text edge at x (left_sprite pads 16 px)"""
    put1(im, sp, x - 16 + sp.width / (2 * S) + dx, cy, a=a)


# ---------- prep ----------
def prep():
    # H5: the envoy (left), the cage (centre); the seated emperor's face sits right of x ~1190, so keep x < 1101
    Image.open("img/H5.jpg").crop((0, 422, 1101, 2380)).resize((1080, 1920), Image.LANCZOS).save("img/H5k.jpg", quality=95)
    print("img/H5k.jpg")


# ---------- garis: timeline ----------
# not to scale (the labels need the room): the dots sit at the label rows, the watermark band stays empty
AX, YTOP, YBOT = 190, 640, 1120
DOT = {1230: 688, 1292: 836, 1512: 1052}


def skema_garis(times=None):
    bg = backdrop((44, 32, 20), (12, 10, 8), glow=(46, 30, 12), gx=560, gy=900)
    a = np.asarray(bg, np.float32).copy()
    a[..., :3] *= (0.93 + 0.14 * noise((H, W), [(36, 0.6), (8, 0.4)], 85))[..., None]
    bg = to_img(a).convert("RGBA")
    l1230 = left_sprite([("±1230", 88, YELLOW, True), ("kakaktua di istana kaisar", 40, WHITE, False)])
    l1292 = left_sprite([("1292", 68, WHITE, True), ("Marco Polo singgah di Sumatra,", 33, SAND, False),
                         ("orang Eropa pertama yang tercatat", 33, SAND, False)])
    l1512 = left_sprite([("1512", 68, WHITE, True), ("Portugis tiba di Maluku", 38, SAND, False)])
    # a round badge of the real bird (Pixabay 6604629) beside the +-1230 row
    src = Image.open("img/6604629.jpg").convert("RGBA").crop((330, 20, 930, 620)).resize((236 * S, 236 * S), Image.LANCZOS)
    badge = Image.new("RGBA", (256 * S, 256 * S))
    m = Image.new("L", (236 * S, 236 * S))
    ImageDraw.Draw(m).ellipse([0, 0, 236 * S - 1, 236 * S - 1], fill=255)
    badge.paste(src, (10 * S, 10 * S), m)
    ImageDraw.Draw(badge).ellipse([6 * S, 6 * S, 250 * S, 250 * S], outline=YELLOW + (255,), width=6 * S)
    labels = ((1230, l1230, T_1230, 704, (255, 225, 0)), (1292, l1292, T_1292, 856, (255, 255, 255)),
              (1512, l1512, T_1512, 1068, (255, 255, 255)))
    frames = []
    for i in range(N["garis"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        L = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(L)
        yb = YTOP + (YBOT - YTOP) * ease(t / 0.5)
        d.line([(AX * S, YTOP * S), (AX * S, yb * S)], fill=(235, 225, 205, 170), width=6 * S)
        d.polygon([((AX - 16) * S, (yb - 4) * S), ((AX + 16) * S, (yb - 4) * S), (AX * S, (yb + 22) * S)],
                  fill=(235, 225, 205, 170))
        # the years run on: a yellow line down the axis from the cockatoo to 1292, then 1512
        if t >= T_JAUH:
            yf = DOT[1230] + (DOT[1292] - DOT[1230]) * ease((t - T_JAUH) / (T_1292 - T_JAUH))
            if t >= T_1292:
                yf = DOT[1292] + (DOT[1512] - DOT[1292]) * ease((t - T_1292) / (T_1512 - T_1292))
            d.line([(AX * S, DOT[1230] * S), (AX * S, yf * S)], fill=YELLOW + (235,), width=10 * S)
        im.alpha_composite(L.resize((W, H), Image.LANCZOS))
        for year, sp, t0, cy, col in labels:
            k = pop(t, t0, 0.3)
            if k <= 0:
                continue
            if year == 1230 and t >= T_NUS:      # the cockatoo got there first: its dot keeps pulsing
                pulse(im, AX, DOT[year], col, t, T_NUS)
            else:
                dd = ImageDraw.Draw(im)
                r = 15 * min(k, 1.1)
                dd.ellipse([AX - r, DOT[year] - r, AX + r, DOT[year] + r], fill=col + (255,), outline=(40, 30, 20, 255), width=3)
            put_l(im, sp, AX + 50, cy, a=min(1, k * 1.3), dx=30 * (1 - min(k, 1)))
        kb = pop(t, T_1230 + 0.1, 0.35)
        if kb > 0:
            put1(im, badge, 880, 712, a=min(1, kb * 1.3), scale=min(kb, 1.05) * (1 + 0.04 * math.sin(math.pi * ramp(t, T_NUS, T_NUS + 0.4))))
        frames.append(im.convert("RGB"))
    return frames


# ---------- peta: route ----------
K, LON0, LAT0, YM = 7.6, 2.0, 45.0, 640


def xy(lon, lat):
    return ((lon - LON0) * K, YM + (LAT0 - lat) * K)


def land(path="../geo/ne_50m_land.geojson"):
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for f in json.load(open(path))["features"]:
        g = f["geometry"]
        for p in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            ring = p[0]
            xs, ys = [q[0] for q in ring], [q[1] for q in ring]
            if max(xs) < -10 or min(xs) > 160 or max(ys) < -60 or min(ys) > 130:
                continue
            d.polygon([(xy(*q)[0] * S, xy(*q)[1] * S) for q in ring], fill=(96, 88, 64, 255), outline=(170, 156, 116, 255))
    return lay.resize((W, H), Image.LANCZOS)


ZONE = [(123.5, -1.5), (128, 1.5), (134, 0.5), (141, -1.5), (148, -5), (148, -13), (142, -15.5), (135, -14.5),
        (129, -12.5), (124, -9.5), (122, -5)]
START = (127.5, -6.0)                                   # Banda Sea, where the boat line leaves the zone
BOAT = [START, (122, -6.2), (116, -6.0), (110.6, -6.3)]
JAWA, KANTON, KAIRO, ITALIA = (110.4, -7.0), (113.3, 23.1), (31.2, 30.0), (14.5, 38.0)
SEA = [JAWA, (108.6, -2.5), (108.0, 4.0), (110.3, 12.0), (113.3, 22.4)]
SILK = [KANTON, (108.9, 34.3), (94.7, 40.1), (76.0, 39.5), (67.0, 39.7), (61.8, 37.6), (44.4, 33.3), (36.3, 33.5),
        KAIRO, (24, 33.5), (17.5, 36.0), ITALIA]


def plen(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def map_base():
    v = (YY / H)[..., None]
    sea = np.array((14, 46, 74), np.float32) * (1 - v) + np.array((8, 30, 52), np.float32) * v
    base = Image.fromarray(sea.astype(np.uint8)).convert("RGBA")
    base.alpha_composite(land())
    a = np.asarray(base, np.float32)
    a[..., :3] *= (0.92 + 0.16 * noise((H, W), [(40, 0.6), (9, 0.4)], 85))[..., None]
    a[..., :3] *= 1 - np.clip(np.maximum((610 - YY) / 380, (YY - 1185) / 240), 0, 1)[..., None] * 0.82
    base = to_img(a).convert("RGBA")
    # the possible home range, hatched
    L = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(L)
    zp = [(xy(*q)[0] * S, xy(*q)[1] * S) for q in ZONE]
    d.polygon(zp, fill=(255, 225, 0, 46))
    M = Image.new("L", (W * S, H * S))
    ImageDraw.Draw(M).polygon(zp, fill=255)
    hat = Image.new("RGBA", (W * S, H * S))
    dh = ImageDraw.Draw(hat)
    for k in range(-60, 120):
        x = k * 14 * S
        dh.line([(x, 0), (x + 2000 * S, 2000 * S)], fill=(255, 225, 0, 90), width=2 * S)
    L.alpha_composite(Image.composite(hat, Image.new("RGBA", hat.size), M))
    pts = [xy(*q) for q in ZONE] + [xy(*ZONE[0])]
    dashed(d, pts, (255, 225, 0, 220), 3, dash=14, gap=9)
    base.alpha_composite(L.resize((W, H), Image.LANCZOS))
    return base


def boat_icon():
    sp = Image.new("RGBA", (60 * S, 60 * S))
    d = ImageDraw.Draw(sp)
    d.polygon([(8 * S, 38 * S), (52 * S, 38 * S), (44 * S, 48 * S), (16 * S, 48 * S)], fill=(250, 245, 235, 255))
    d.polygon([(30 * S, 6 * S), (30 * S, 36 * S), (50 * S, 34 * S)], fill=(250, 245, 235, 255))
    d.line([(30 * S, 4 * S), (30 * S, 40 * S)], fill=(250, 245, 235, 255), width=3 * S)
    return sp


def point_at(pts, u):
    """point at length u along a polyline (1x coordinates)"""
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        if u <= L:
            k = u / L if L else 0
            return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        u -= L
    return pts[-1]


def skema_peta(times=None):
    base = map_base()
    boat, bp, sp_, silk = boat_icon(), [xy(*q) for q in BOAT], [xy(*q) for q in SEA], [xy(*q) for q in SILK]
    zone_lab = left_sprite([("asal kemungkinan: Indonesia timur,", 30, (255, 236, 150), False),
                            ("Papua, atau Australia utara", 30, (255, 236, 150), False)], gap=4)
    jawa = pill("JAWA", 32, (20, 20, 20), YELLOW + (240,), (255, 255, 255, 200))
    kanton = left_sprite([("KANTON", 34, WHITE, True), ("Tiongkok", 26, SAND, False)], gap=2)
    kairo = left_sprite([("KAIRO, MESIR", 30, (230, 230, 230), True)])
    italia = left_sprite([("ITALIA", 30, (230, 230, 230), True)])
    jalur = left_sprite([("Jalur Sutra", 32, (230, 220, 195), False)])
    jx, jy = xy(*JAWA)
    kx, ky = xy(*KANTON)
    cx, cy = xy(*KAIRO)
    ix, iy = xy(*ITALIA)
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        put_l(im, zone_lab, 470, 1150, a=ramp(t, 0.0, 0.25))
        L = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(L)
        ub = ease(t / 0.32)                               # boat line: Banda Sea -> Java
        if ub > 0:
            d.line([(x * S, y * S) for x, y in [point_at(bp, plen(bp) * k / 20) for k in range(int(20 * ub) + 1)]],
                   fill=YELLOW + (255,), width=7 * S, joint="curve")
        us = ease((t - T_LALU) / (T_TIONGKOK + 0.05 - T_LALU))   # Java -> Canton
        if us > 0:
            d.line([(x * S, y * S) for x, y in [point_at(sp_, plen(sp_) * k / 30) for k in range(int(30 * us) + 1)]],
                   fill=YELLOW + (255,), width=7 * S, joint="curve")
        uk = ease((t - (T_TIONGKOK + 0.2)) / 0.65)       # the rest of the suggested route, faint
        if uk > 0:
            dashed(d, silk, (240, 236, 225, 190), 4, dash=16, gap=11, upto=uk * plen(silk))
        im.alpha_composite(L.resize((W, H), Image.LANCZOS))
        if 0 < ub < 1 or (us > 0 and us < 1):            # the boat rides the line it is drawing
            px, py = point_at(bp, plen(bp) * ub) if ub < 1 else point_at(sp_, plen(sp_) * us)
            put1(im, boat, px, py - 18)
        dd = ImageDraw.Draw(im)
        if uk > 0.25:
            put_l(im, jalur, 430, 640, a=ramp(uk, 0.25, 0.45))
        if uk > 0.8:
            for (x, y), lab, lx, ly in (((cx, cy), kairo, cx - 40, cy + 38), ((ix, iy), italia, ix + 16, iy - 34)):
                dd.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(235, 235, 235, 255), outline=(30, 30, 30, 255), width=2)
                put_l(im, lab, lx, ly, a=ramp(uk, 0.8, 1.0))
        if t >= T_JAWA:
            pulse(im, jx, jy, (255, 225, 0), t, T_JAWA)
            k = pop(t, T_JAWA, 0.3)
            put1(im, jawa, jx - 110, jy + 6, a=min(1, k), scale=min(k, 1.05))
        if t >= T_TIONGKOK:
            pulse(im, kx, ky, (255, 255, 255), t, T_TIONGKOK)
            k = pop(t, T_TIONGKOK, 0.3)
            put_l(im, kanton, kx + 26, ky + 10, a=min(1, k), dx=20 * (1 - min(k, 1)))
        frames.append(im.convert("RGB"))
    return frames


# ---------- kartu ----------
def skema_kartu(times=None):
    bg = backdrop((44, 30, 18), (10, 8, 6), glow=(44, 28, 10), gy=920)
    panel = Image.new("RGBA", (W * S, H * S))
    ImageDraw.Draw(panel).rounded_rectangle([100 * S, 640 * S, 980 * S, 1190 * S], radius=34 * S,
                                            fill=(14, 12, 10, 220), outline=(255, 225, 0, 150), width=3 * S)
    bg.alpha_composite(panel.resize((W, H), Image.LANCZOS))
    rows = [(text_sprite([("HADIAH", 76, YELLOW, True)]), 705),
            (text_sprite([("'SULTAN BABILONIA'", 50, WHITE, True)]), 790),
            (text_sprite([("(Sultan Mesir al-Kamil)", 32, SAND, False)]), 852),
            (text_sprite([("UNTUK KAISAR", 44, WHITE, True), ("FREDERICK II", 56, YELLOW, True)], gap=6), 1052),
            (text_sprite([("4 gambar kakaktua di kitabnya, kini di Vatikan", 26, GREY, False)]), 1128),
            (text_sprite([("250 tahun lebih tua dari lukisan Mantegna (1496)", 26, GREY, False)]), 1162)]
    frames = []
    for i in range(N["kartu"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        for (sp, y), t0 in zip(rows, T_ROWS):
            k = pop(t, t0, 0.26)
            if k > 0:
                put1(im, sp, 540, y + 14 * (1 - min(k, 1)), a=min(1, k * 1.4), scale=min(k, 1.04))
        frames.append(im.convert("RGB"))
    return frames


# ---------- cover ----------
def cover():
    src = Image.open("img/6604629.jpg").convert("RGB")
    face = src.crop((300, 0, 900, 853)).resize((1080, 1535), Image.LANCZOS)
    im = Image.new("RGB", (W, H))
    top = src.crop((300, 0, 900, 120)).resize((1080, 420), Image.LANCZOS).filter(ImageFilter.GaussianBlur(30))
    im.paste(top, (0, 0))
    im.paste(face, (0, 385))
    a = np.asarray(im, np.float32)
    a *= 1 - np.clip((760 - YY) / 520, 0, 1)[..., None] * 0.62
    im = to_img(a).convert("RGBA")
    t = text_sprite([("KAKAKTUA", 138, YELLOW, True), ("DI ISTANA KAISAR EROPA", 64, WHITE, True),
                     ("800 TAHUN LALU", 64, WHITE, True)], gap=10)
    put1(im, t, 540, 445)
    im.convert("RGB").save("img/cover85.jpg", quality=93)
    print("img/cover85.jpg")


if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or ["prep", "garis", "peta", "kartu", "cover"]
    fns = {"garis": skema_garis, "peta": skema_peta, "kartu": skema_kartu}
    for name in todo:
        if name in ("prep", "cover"):
            {"prep": prep, "cover": cover}[name]()
            continue
        fr = fns[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, f"clips/skema_{name}.mp4")
