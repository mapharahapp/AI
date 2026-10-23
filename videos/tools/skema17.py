"""Schematic animations for Titik Heran #17 (run in the episode work dir; writes clips/skema_jawa.mp4, skema_upwelling.mp4, skema_dangkal.mp4).
usage: python3 skema17.py GEO_DIR [jawa|upwelling|dangkal ...]   (GEO_DIR holds ne_10m_land.geojson from github.com/nvkelso/natural-earth-vector)
skema_jawa: Java from the Natural Earth coastline; the south coast lights up (the stranding hotspot in Putra et al. 2025, Scientific Reports),
with four recent strandings from the news: Cilacap (May 2026), Kebumen (15 Oct 2026), Purworejo (Dec 2025) and Parangkusumo, Bantul (18 Oct 2026).
skema_upwelling: a cross-section off the south coast in the dry season: the wind drives the surface water out to sea, cold water rich in
nutrients comes up along the slope near the coast and the plankton blooms. Simplified: the real wind blows along the coast.
skema_dangkal: a whale shark follows the anchovies up the beach slope and is caught in the shallows as the water drops.
Event times are seconds from the start of each shot, read off `render.py 17 plan`.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, dashed, chaikin, encode
from skema13 import navy, marker

GEO = sys.argv[1] if len(sys.argv) > 1 else "geo"
RED, CYAN, GREEN = (255, 84, 64), (120, 220, 255), (150, 236, 110)


def ring(d, x, y, r, col, a, w=5):
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], outline=col + (max(0, min(255, round(a))),), width=w * S)


def arrow(d, pts, col, width, upto=1.0, head=22):
    """a polyline drawn on up to the fraction `upto` of its length, with an arrowhead at the moving tip (1x coordinates)"""
    if upto <= 0.01:
        return
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    goal, out = upto * sum(seg), [pts[0]]
    for (a, b), L in zip(zip(pts, pts[1:]), seg):
        if goal <= L:
            out.append((a[0] + (b[0] - a[0]) * goal / L, a[1] + (b[1] - a[1]) * goal / L))
            break
        out.append(b)
        goal -= L
    d.line(sc(out), fill=col, width=width * S, joint="curve")
    (x0, y0), (x1, y1) = out[-2], out[-1]
    ang = math.atan2(y1 - y0, x1 - x0)
    tip = (x1 + math.cos(ang) * head * 0.5, y1 + math.sin(ang) * head * 0.5)
    d.polygon(sc([tip, (tip[0] - head * math.cos(ang - 0.45), tip[1] - head * math.sin(ang - 0.45)),
                  (tip[0] - head * math.cos(ang + 0.45), tip[1] - head * math.sin(ang + 0.45))]), fill=col)


def label(lines, box=(8, 24, 54, 215), edge=(255, 255, 255, 70)):
    """centred text lines on a rounded navy tag"""
    tx = text_sprite(lines, gap=8)
    bw, bh = tx.width - 22 * S, tx.height - 30 * S
    tag = Image.new("RGBA", tx.size, (0, 0, 0, 0))
    ImageDraw.Draw(tag).rounded_rectangle([(tx.width - bw) // 2, (tx.height - bh) // 2, (tx.width + bw) // 2, (tx.height + bh) // 2],
                                          radius=14 * S, fill=box, outline=edge, width=3 * S)
    tag.alpha_composite(tx)
    return tag


# ---------- skema_jawa ----------
K, LON0, LAT0, CY = 104, 110.0, -7.35, 900


def xy(lon, lat):
    return 540 + (lon - LON0) * K, CY + (LAT0 - lat) * K


def jawa(n=120):
    rings = []
    for f in json.load(open(os.path.join(GEO, "ne_10m_land.geojson")))["features"]:
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            lon = [p[0] for p in poly[0]]
            lat = [p[1] for p in poly[0]]
            if max(lon) > 103.5 and min(lon) < 116.5 and -10 < sum(lat) / len(lat) < -5.5:  # Java and the islands near it
                rings.append(poly[0])
    java = max((r for r in rings if 105 < sum(p[0] for p in r) / len(r) < 115 and sum(p[1] for p in r) / len(r) < -6), key=len)
    # the south coast: the stretch of the ring between its west and east ends that runs further south
    iw = min(range(len(java)), key=lambda i: java[i][0])
    ie = max(range(len(java)), key=lambda i: java[i][0])
    a, b = sorted((iw, ie))
    arc1, arc2 = java[a:b + 1], java[b:] + java[:a + 1]
    south = min((arc1, arc2), key=lambda r: sum(p[1] for p in r) / len(r))
    if south[0][0] > south[-1][0]:
        south = south[::-1]
    south = [xy(*p) for p in south]
    sl = np.cumsum([0] + [math.dist(p, q) for p, q in zip(south, south[1:])])
    bg = navy(540, CY, [xy(lon, 0)[0] for lon in range(105, 116)], [xy(0, lat)[1] for lat in (-6, -7, -8, -9, -10)])
    land = layer()
    d = ImageDraw.Draw(land)
    for r in rings:
        d.polygon(sc([xy(*p) for p in r]), fill=(150, 134, 102, 255) if r is not java else (222, 200, 150, 255),
                  outline=(96, 84, 62, 255) if r is not java else (120, 100, 68, 255))
    land = down(land)
    lab_java = text_sprite([("JAWA", 46, (70, 56, 34), True)])
    lab_sea = text_sprite([("S A M U D R A   H I N D I A", 28, (190, 214, 240), True)])
    lab_note = text_sprite([("contoh kasus 2025–2026 (berita)", 27, WHITE, False)])
    # (place, date, lon, lat, chip centre x), left to right along the coast
    cases = [("Cilacap", "Mei 2026", 109.02, -7.7, 150), ("Kebumen", "15 Okt 2026", 109.58, -7.79, 402),
             ("Purworejo", "Des 2025", 109.97, -7.88, 660), ("Parangkusumo", "18 Okt 2026", 110.32, -8.02, 922)]

    def on_coast(lon, lat):  # the closest point of the south coast, so the marker sits on the shore
        x, y = xy(lon, lat)
        return min(south, key=lambda p: math.dist(p, (x, y)))
    pts = [on_coast(lo, la) for _, _, lo, la, _ in cases]
    chips = [label([(p, 30, WHITE, True), (dt, 27, YELLOW, False)],
                   edge=YELLOW + (230,) if k == 3 else (255, 255, 255, 70)) for k, (p, dt, *_) in enumerate(cases)]
    dot = marker()
    chip_y = 1170
    # Selatan 0.04, Jawa 0.46, adalah 0.94, titik 1.34, paling 1.66, rawan 2.06, hiu 2.38, paus 2.54, terdampar 2.78
    t_coast0, t_coast1, t_java, t_mark, t_rawan, t_pulse = 0.05, 0.95, 0.46, 1.34, 2.06, 2.38
    frames = []
    for i in range(n):
        t = i / FPS
        im = bg.copy()
        im.alpha_composite(fade(land, ramp(t, 0.0, 0.2)) if t < 0.2 else land)
        glow = layer()
        dg = ImageDraw.Draw(glow)
        top = layer()
        d = ImageDraw.Draw(top)
        u = ramp(t, t_coast0, t_coast1)
        if u > 0:
            part = [p for p, L in zip(south, sl) if L <= u * sl[-1]]
            if len(part) > 1:
                boost = 1 + 0.35 * math.exp(-((t - t_rawan - 0.15) / 0.25) ** 2)
                dg.line(sc(part), fill=RED + (min(255, round(170 * boost)),), width=round(30 * boost) * S, joint="curve")
                d.line(sc(part), fill=(255, 150, 120, 255), width=7 * S, joint="curve")
        im.alpha_composite(down(glow).filter(ImageFilter.GaussianBlur(9)))
        put(top, lab_java, *xy(111.85, -7.42), a=ramp(t, t_java, t_java + 0.15), scale=pop(t, t_java))
        put(top, lab_sea, 540, 1500, a=0.75 * ramp(t, 0.1, 0.4))
        for k, ((x, y), (_, _, _, _, chx)) in enumerate(zip(pts, cases)):
            t0 = t_mark + 0.16 * k
            if t < t0:
                continue
            ln = ramp(t, t0, t0 + 0.18)
            ex, ey = x + (chx - x) * ln, y + 12 + (chip_y - 50 - y - 12) * ln
            d.line(sc([(x, y + 12), (ex, ey)]), fill=(255, 255, 255, 190), width=3 * S)
            if k == 3 and t >= t_pulse:
                for ph0 in (0.0, 0.45):
                    ph = ((t - t_pulse + ph0) % 0.9) / 0.9
                    ring(d, x, y, 14 + 52 * ph, YELLOW, 230 * (1 - ph) ** 1.5, w=4)
            put(top, dot, x, y, scale=0.6 * pop(t, t0))  # small dots: the four places sit close together
            put(top, chips[k], chx, chip_y, a=ramp(t, t0 + 0.08, t0 + 0.2), scale=pop(t, t0 + 0.08))
        put(top, lab_note, 540, 1575, a=0.85 * ramp(t, t_mark, t_mark + 0.25))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_jawa.mp4")


# ---------- cross-sections ----------
def sky_sea(surf):
    """navy sky over a sea that darkens with depth, as a full frame"""
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    v = np.clip((yy - surf) / (H - surf), 0, 1)[..., None]
    sea = np.array([30, 110, 150]) * (1 - v) + np.array([8, 34, 70]) * v
    sky_v = np.clip(yy / surf, 0, 1)[..., None]
    sky = np.array([12, 30, 66]) * (1 - sky_v) + np.array([28, 62, 112]) * sky_v
    rgb = np.where((yy < surf)[..., None], sky, sea)
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert("RGBA")


def poly_layer(pts, fill):
    lay = layer()
    ImageDraw.Draw(lay).polygon(sc(pts), fill=fill)
    return down(lay)


def sun(r=46):
    s = Image.new("RGBA", (6 * r * S, 6 * r * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    c = 3 * r * S
    for k in range(12):
        a = 2 * math.pi * k / 12
        d.line([(c + math.cos(a) * 1.35 * r * S, c + math.sin(a) * 1.35 * r * S), (c + math.cos(a) * 2.0 * r * S, c + math.sin(a) * 2.0 * r * S)],
               fill=(255, 214, 90, 255), width=7 * S)
    d.ellipse([c - r * S, c - r * S, c + r * S, c + r * S], fill=(255, 210, 70, 255), outline=(255, 240, 170, 255), width=4 * S)
    return s


SURF = 800
COAST = [(0, 650), (60, 642), (120, 668), (165, 728), (200, SURF)]
BED = [(200, SURF), (330, 858), (470, 928), (560, 1050), (650, 1200), (740, 1360), (820, 1500), (900, 1576), (1000, 1616), (1090, 1636)]


def bed_y(x):
    return float(np.interp(x, [p[0] for p in BED], [p[1] for p in BED]))


def upwelling(n=132):
    xs = list(range(200, W + 12, 6))
    base = sky_sea(SURF)
    rock = poly_layer(COAST + BED[1:] + [(1090, H + 10), (-10, H + 10), (-10, 650)], (88, 74, 58, 255))
    hill = layer()
    dh = ImageDraw.Draw(hill)
    dh.polygon(sc(COAST + [(200, SURF + 2), (-10, SURF + 2), (-10, 650)]), fill=(92, 128, 70, 255))
    dh.line(sc(COAST), fill=(140, 176, 104, 255), width=4 * S)
    hill = down(hill)
    lab_java = text_sprite([("JAWA", 38, WHITE, True)])
    lab_warm = text_sprite([("air hangat", 30, WHITE, False)])
    lab_cold = text_sprite([("AIR DINGIN", 40, CYAN, True), ("kaya nutrisi", 30, WHITE, False)], gap=2)
    lab_wind = text_sprite([("angin", 30, WHITE, False)])
    lab_plk = text_sprite([("plankton", 30, GREEN, True)])
    sunsp = sun()
    rise_path = [(990, 1470), (850, 1330), (720, 1150), (600, 1000), (470, 890), (330, 832)]
    rng = np.random.default_rng(17)
    plankton = [(x, rng.uniform(SURF + 6, min(SURF + 64, bed_y(x) - 8)), rng.uniform(3, 6.5), rng.uniform(0, 0.5))
                for x in rng.uniform(250, 560, 80)]
    # Kenapa 0.05, Tiap 1.27, kemarau 1.48, air 2.28, dingin 2.52, kaya 2.84, nutrisi 3.08, naik 3.56
    t_wind, t_sun, t_rise0, t_rise1, t_plk = 1.27, 1.48, 2.28, 3.5, 3.45
    frames = []
    for i in range(n):
        t = i / FPS
        im = base.copy()
        up = ramp(t, t_rise0, t_rise1)  # how far the cold water has come up near the coast
        cold_top = [(x, 1060 - up * 262 * math.exp(-(x - 200) / 230)) for x in xs]
        cold = layer()
        dc = ImageDraw.Draw(cold)
        dc.polygon(sc(cold_top + [(W + 12, bed_y(W + 12)), (W + 12, H + 10), (200, H + 10)]), fill=(30, 88, 204, 255))
        dc.line(sc(cold_top), fill=(110, 170, 255, 150), width=4 * S)
        im.alpha_composite(down(cold))
        im.alpha_composite(rock)
        im.alpha_composite(hill)
        top = layer()
        d = ImageDraw.Draw(top)
        d.line(sc([(200, SURF), (W + 10, SURF)]), fill=(200, 236, 255, 220), width=4 * S)
        put(top, lab_java, 92, 718, a=ramp(t, 0.05, 0.3))
        put(top, lab_warm, 880, 930, a=0.8 * ramp(t, 0.3, 0.6))
        put(top, sunsp, 930, 664, a=ramp(t, t_sun, t_sun + 0.1), scale=0.5 * pop(t, t_sun))
        w = ramp(t, t_wind, t_wind + 0.45)
        if w > 0:
            for x0, x1 in ((320, 520), (600, 800)):
                slide = 30 * ((t - t_wind) % 1.2) / 1.2
                arrow(d, [(x0 + slide, 742), (x1 + slide, 742)], (255, 255, 255, round(230 * min(1, w * 1.5))), 6, upto=w)
            put(top, lab_wind, 560, 700, a=ramp(t, t_wind + 0.2, t_wind + 0.4))
        s_ = ramp(t, t_wind + 0.35, t_wind + 0.8)
        if s_ > 0:
            for x0, x1 in ((560, 700), (760, 900)):
                arrow(d, [(x0, 850), (x1, 850)], (255, 255, 255, round(150 * s_)), 5, upto=s_, head=18)
        if up > 0:
            arrow(d, rise_path, CYAN + (240,), 9, upto=min(1, up * 1.08), head=30)
            for k in range(14):  # nutrients carried up along the arrow
                ph = (k / 14 + (t - t_rise0) * 0.55) % 1.0
                if ph > up:
                    continue
                L = [math.dist(a, b) for a, b in zip(rise_path, rise_path[1:])]
                g = ph * sum(L)
                for (a, b), l in zip(zip(rise_path, rise_path[1:]), L):
                    if g <= l:
                        px, py = a[0] + (b[0] - a[0]) * g / l, a[1] + (b[1] - a[1]) * g / l
                        break
                    g -= l
                off = 26 * math.sin(k * 2.3)
                r = 5
                d.ellipse([(px - r + off * 0.6) * S, (py - r + off) * S, (px + r + off * 0.6) * S, (py + r + off) * S], fill=(210, 245, 255, 220))
            put(top, lab_cold, 925, 1180, a=ramp(t, t_rise0 + 0.1, t_rise0 + 0.3), scale=pop(t, t_rise0 + 0.1))
        p = ramp(t, t_plk, t_plk + 0.5)
        if p > 0:
            for x, y, r, dl in plankton:
                q = ramp(t, t_plk + dl * 0.6, t_plk + dl * 0.6 + 0.2)
                if q > 0:
                    rr = r * (0.9 + 0.15 * math.sin(9 * t + x))
                    d.ellipse([(x - rr) * S, (y - rr) * S, (x + rr) * S, (y + rr) * S], fill=GREEN + (round(230 * q),))
            put(top, lab_plk, 640, 880, a=ramp(t, t_plk + 0.25, t_plk + 0.45))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_upwelling.mp4")


# ---------- skema_dangkal ----------
SHARK_TOP = [(0.0, -0.025), (0.02, -0.05), (0.06, -0.072), (0.14, -0.092), (0.26, -0.103), (0.40, -0.104), (0.46, -0.1), (0.5, -0.165),
             (0.52, -0.205), (0.545, -0.21), (0.56, -0.18), (0.575, -0.098), (0.66, -0.083), (0.72, -0.077), (0.735, -0.105),
             (0.755, -0.108), (0.77, -0.07), (0.83, -0.045), (0.87, -0.05), (0.93, -0.12), (0.99, -0.24), (1.0, -0.235),
             (0.975, -0.14), (0.935, -0.04), (0.925, 0.0)]
SHARK_BOT = [(0.95, 0.06), (0.985, 0.13), (0.97, 0.135), (0.915, 0.07), (0.87, 0.03), (0.83, 0.035), (0.78, 0.05), (0.765, 0.085),
             (0.745, 0.085), (0.73, 0.06), (0.62, 0.075), (0.59, 0.11), (0.57, 0.112), (0.555, 0.08), (0.42, 0.095), (0.33, 0.096),
             (0.375, 0.2), (0.36, 0.215), (0.29, 0.135), (0.22, 0.096), (0.13, 0.085), (0.05, 0.065), (0.015, 0.045), (0.0, 0.025)]


def shark_sprite(L):
    """a whale shark seen from the side, facing left, L px long at 1x; the 2x sprite's centre is the middle of the body axis"""
    s = L * S
    w2, h2 = int(1.04 * s), int(0.52 * s)
    ox, oy = 0.02 * s, 0.26 * s

    def P(pts):
        return [(ox + x * s, oy + y * s) for x, y in pts]
    m = Image.new("L", (w2, h2), 0)
    ImageDraw.Draw(m).polygon(P(chaikin(SHARK_TOP + SHARK_BOT, 1)), fill=255)
    yy, xx = np.mgrid[0:h2, 0:w2].astype(np.float32)
    yn = (yy - oy) / s
    v = np.clip((yn + 0.02) / 0.09, 0, 1)[..., None]  # dark back, pale belly
    rgb = np.array([46, 64, 94]) * (1 - v) + np.array([200, 208, 218]) * v
    im = Image.fromarray(np.dstack([rgb, np.asarray(m)]).astype(np.uint8), "RGBA")
    pat = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    d = ImageDraw.Draw(pat)
    rng = np.random.default_rng(5)
    for gx in np.arange(0.08, 0.9, 0.034):  # the checkerboard: pale bars and rows of white spots
        d.line([(ox + gx * s, oy - 0.1 * s), (ox + (gx + 0.004) * s, oy + 0.02 * s)], fill=(220, 230, 240, 45), width=max(2, round(0.003 * s)))
        for gy in np.arange(-0.088, 0.02, 0.026):
            x, y = ox + (gx + 0.017 + rng.uniform(-0.004, 0.004)) * s, oy + (gy + rng.uniform(-0.004, 0.004)) * s
            r = 0.0048 * s * rng.uniform(0.8, 1.2)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(236, 242, 250, 230))
    for gy in (-0.07, -0.04):  # the ridges along the side
        d.line([(ox + 0.16 * s, oy + gy * s), (ox + 0.8 * s, oy + (gy + 0.02) * s)], fill=(190, 205, 222, 90), width=max(2, round(0.004 * s)))
    pat.putalpha(Image.fromarray((np.asarray(pat)[..., 3].astype(np.float32) * np.asarray(m) / 255).astype(np.uint8)))
    im.alpha_composite(pat)
    d = ImageDraw.Draw(im)
    d.line(P([(0.003, 0.022), (0.075, 0.03)]), fill=(26, 32, 44, 255), width=max(2, round(0.006 * s)))  # mouth
    d.ellipse([ox + 0.058 * s, oy - 0.012 * s, ox + 0.074 * s, oy + 0.004 * s], fill=(20, 24, 32, 255))  # eye
    for k in range(5):  # gill slits
        x = 0.15 + 0.014 * k
        d.line(P([(x, -0.035), (x + 0.006, 0.0), (x, 0.045)]), fill=(30, 40, 58, 220), width=max(2, round(0.004 * s)))
    return im


def teri_sprite(L=34):
    s = L * S
    im = Image.new("RGBA", (int(1.3 * s), int(0.5 * s)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0.05 * s, 0.13 * s, 0.95 * s, 0.37 * s], fill=(214, 226, 236, 255))
    d.polygon([(0.9 * s, 0.25 * s), (1.25 * s, 0.08 * s), (1.18 * s, 0.25 * s), (1.25 * s, 0.42 * s)], fill=(196, 210, 224, 255))
    d.line([(0.2 * s, 0.25 * s), (0.85 * s, 0.25 * s)], fill=(150, 170, 190, 255), width=max(2, round(0.04 * s)))
    return im


SAND = [(-10, 838), (1090, 1100)]  # a gentle beach slope, ±13°


def sand_y(x):
    return float(np.interp(x, [p[0] for p in SAND], [p[1] for p in SAND]))


def dangkal(n=69):
    L = 520
    slope = math.degrees(math.atan2(SAND[1][1] - SAND[0][1], SAND[1][0] - SAND[0][0]))
    shark = shark_sprite(L).rotate(-slope, resample=Image.BICUBIC, expand=True)  # nose up the slope
    teri = teri_sprite()
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    v = np.clip((yy - 840) / (H - 840), 0, 1)[..., None]
    sand = Image.fromarray((np.array([198, 172, 122]) * (1 - v) + np.array([118, 98, 68]) * v).astype(np.uint8)).convert("RGBA")
    m = layer()
    dm = ImageDraw.Draw(m)
    dm.polygon(sc(SAND + [(1090, H + 10), (-10, H + 10)]), fill=(255,) * 4)
    rng = np.random.default_rng(9)
    for _ in range(160):
        x = rng.uniform(0, W)
        y = rng.uniform(sand_y(x) + 14, H)
        r = rng.uniform(2, 5)
        dm.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(150, 126, 86, 255))
    sand.putalpha(down(m).getchannel("A"))
    grains = layer()
    dg = ImageDraw.Draw(grains)
    for _ in range(160):
        x = rng.uniform(0, W)
        y = rng.uniform(sand_y(x) + 14, H)
        r = rng.uniform(2, 5)
        dg.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(96, 78, 52, 150))
    dg.line(sc(SAND), fill=(228, 206, 160, 255), width=5 * S)
    sand.alpha_composite(down(grains))
    lab_surut = text_sprite([("air surut", 30, WHITE, True)])
    school = [(rng.uniform(-70, 70), rng.uniform(-22, 22), rng.uniform(0.8, 1.15)) for _ in range(16)]
    cos = math.cos(math.radians(slope))
    # lalu 0.03, terjebak 0.27, di 0.83, air 1.03, dangkal 1.19
    t_stop, t_drop0, t_drop1, t_ring = 0.85, 0.5, 1.5, 0.8
    frames = []
    for i in range(n):
        t = i / FPS
        surf = 850 + 55 * ramp(t, t_drop0, t_drop1)
        im = sky_sea(surf)
        u = 1 - (1 - ramp(t, 0.0, t_stop)) ** 2  # swims up the slope, slowing as it grounds
        cx = 900 - 300 * u
        cy = sand_y(cx) - (0.1 * L + 46 * (1 - u)) / cos  # in the end its belly lies on the sand
        wob = 3 * math.sin(2 * math.pi * 2.2 * t) * (1 - ramp(t, t_stop, t_stop + 0.4))
        body = layer()
        body.alpha_composite(shark, (round(cx * S - shark.width / 2), round((cy + wob) * S - shark.height / 2)))
        for dx, dy, sz in school:  # anchovies running ahead into the shallows
            fx = cx - 0.5 * L - 90 + dx - 330 * ramp(t, 0.0, 1.0)
            fy = min(max(sand_y(fx) - 40 + dy, surf + 16), sand_y(fx) - 14)
            a = 1 - ramp(t, 0.6, 1.0)
            if a > 0 and fx > 40:
                put(body, teri, fx, fy, a=a, scale=sz)
        im.alpha_composite(down(body))
        water = layer()  # the water tints whatever is below the surface
        ImageDraw.Draw(water).rectangle([0, surf * S, W * S, H * S], fill=(40, 140, 190, 92))
        im.alpha_composite(down(water))
        im.alpha_composite(sand)
        top = layer()
        d = ImageDraw.Draw(top)
        x_shore = (surf - SAND[0][1]) / (SAND[1][1] - SAND[0][1]) * (SAND[1][0] - SAND[0][0]) + SAND[0][0]
        d.line(sc([(x_shore, surf), (W, surf)]), fill=(206, 238, 255, 230), width=4 * S)
        a = ramp(t, t_drop0, t_drop0 + 0.2)
        if a > 0:
            arrow(d, [(975, surf - 70), (975, surf - 12)], (255, 255, 255, round(220 * a)), 5, head=18)
            put(top, lab_surut, 975, surf - 104, a=a)
        if t >= t_ring:
            for ph0 in (0.0, 0.5):
                ph = ((t - t_ring + ph0) % 1.0) / 1.0
                ring(d, cx, cy, 170 + 140 * ph, RED, 235 * (1 - ph) ** 1.6, w=6)
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_dangkal.mp4")


if __name__ == "__main__":
    for name in sys.argv[2:] or ["jawa", "upwelling", "dangkal"]:
        globals()[name]()
