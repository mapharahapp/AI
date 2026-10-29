"""Schematic animations for Titik Heran #18 (run in the episode work dir; writes clips/skema_garis.mp4, skema_kekova.mp4,
skema_dasar.mp4 and skema_guci.mp4).
usage: python3 skema18.py GEO_DIR [garis|kekova|dasar|guci ...] [--sheet out.jpg t1,t2,...]
       (GEO_DIR holds ne_10m_land.geojson from github.com/nvkelso/natural-earth-vector; --sheet saves those frames as a contact sheet)
skema_garis: a timeline 3000-2000 BC: the Kekova wreck's estimated span (±2700-2400 BC) over the Great Pyramid of Giza (±2560 BC),
then the old record, the cargo at Dokos in Greece (±2200 BC).
skema_kekova: the eastern Mediterranean, zooming in on Kekova Island off Antalya, where the wreck lies at ±30 m.
skema_dasar: a cross-section of the sloping seabed: the wooden hull fades away and leaves the jars and three stone anchors,
so there is no wood to radiocarbon-date (BBC, Al Jazeera). Hull, jars and anchors are drawn schematically.
skema_guci: the jars match Early Bronze Age jars from Egypt and the Levant; the first clay analysis points to the Jordan Valley.
Event times are seconds from the start of each shot, read off `render.py 18 plan`.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, dashed, chaikin, encode, glow_sprite
from skema13 import navy, marker
from skema17 import ring, arrow, label

GEO = sys.argv[1] if len(sys.argv) > 1 else "geo"
RED, GREEN, PALE = (255, 84, 64), (120, 230, 110), (200, 214, 235)
LAND, COAST = (222, 200, 150), (120, 100, 68)
COS = math.cos(math.radians(35))  # one longitude scale for every map view, so a zoom does not stretch the coast


# ---------- shared drawings ----------
def jar_pts(cx, cy, h):
    """an Early Bronze Age jar (rim, short neck, wide shoulder, flat base), centred on (cx, cy), h px tall (1x)"""
    right = [(0.12, 0), (0.12, 0.045), (0.08, 0.07), (0.08, 0.15), (0.2, 0.21), (0.29, 0.31), (0.31, 0.43), (0.28, 0.6),
             (0.2, 0.82), (0.12, 1.0)]
    pts = right + [(-x, y) for x, y in reversed(right)]
    return [(cx + x * h, cy + (y - 0.5) * h) for x, y in pts]


def jar(d, cx, cy, h, fill, edge, w=3):
    d.polygon(sc(jar_pts(cx, cy, h)), fill=fill, outline=edge, width=w * S)
    for sx in (-1, 1):  # two loop handles on the shoulder
        hx, hy, r = cx + sx * 0.3 * h, cy - 0.24 * h, 0.075 * h
        a0 = -90 if sx > 0 else 90  # PIL arcs run clockwise from 3 o'clock: the loop bulges outward
        d.arc([(hx - r) * S, (hy - r) * S, (hx + r) * S, (hy + r) * S], a0, a0 + 180, fill=edge, width=max(2, w) * S)


def check(d, cx, cy, r, a=1.0):
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=(40, 140, 70, round(240 * a)),
              outline=(255, 255, 255, round(230 * a)), width=3 * S)
    d.line(sc([(cx - 0.45 * r, cy + 0.02 * r), (cx - 0.1 * r, cy + 0.38 * r), (cx + 0.5 * r, cy - 0.35 * r)]),
           fill=(255, 255, 255, round(255 * a)), width=max(3, round(r * 0.22)) * S, joint="curve")


def clip_ring(ring_, lon0, lat0, lon1, lat1):
    """Sutherland-Hodgman clip of a lon/lat ring to a box (the box is wider than any view, so its edges stay off screen)"""
    pts = ring_
    for inside, cut in ((lambda p: p[0] >= lon0, lambda a, b: (lon0, a[1] + (b[1] - a[1]) * (lon0 - a[0]) / (b[0] - a[0]))),
                        (lambda p: p[0] <= lon1, lambda a, b: (lon1, a[1] + (b[1] - a[1]) * (lon1 - a[0]) / (b[0] - a[0]))),
                        (lambda p: p[1] >= lat0, lambda a, b: (a[0] + (b[0] - a[0]) * (lat0 - a[1]) / (b[1] - a[1]), lat0)),
                        (lambda p: p[1] <= lat1, lambda a, b: (a[0] + (b[0] - a[0]) * (lat1 - a[1]) / (b[1] - a[1]), lat1))):
        out, prev = [], pts[-1] if pts else None
        for cur in pts:
            if inside(cur):
                if not inside(prev):
                    out.append(cut(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cut(prev, cur))
            prev = cur
        pts = out
        if not pts:
            break
    return pts


def med_land():
    rings = []
    for f in json.load(open(os.path.join(GEO, "ne_10m_land.geojson")))["features"]:
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            r = poly[0]
            lo, la = [p[0] for p in r], [p[1] for p in r]
            if max(lo) < 18 or min(lo) > 44 or max(la) < 24 or min(la) > 46:
                continue
            c = clip_ring(r, 18, 24, 44, 46)
            if len(c) > 2:
                rings.append(c)
    return rings


def view(clon, clat, k, cy):
    return lambda lon, lat: (540 + (lon - clon) * k * COS, cy - (lat - clat) * k)


def land_layer(rings, xy):
    lay = layer()
    d = ImageDraw.Draw(lay)
    for r in rings:
        p = [xy(*q) for q in r]
        xs, ys = [x for x, _ in p], [y for _, y in p]
        if max(xs) < -50 or min(xs) > W + 50 or max(ys) < -50 or min(ys) > H + 50:
            continue
        d.polygon(sc(p), fill=LAND + (255,), outline=COAST + (255,), width=2 * S)
    return down(lay)


# ---------- skema_garis ----------
def year_x(y):  # years BC -> x
    return 110 + (3000 - y) * 0.86


def pyramid_sprite(w=84):
    s = Image.new("RGBA", (2 * w * S, 2 * w * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    c, h = w * S, 0.62 * w * S
    d.polygon([(c - w / 2 * S, c + h / 2), (c + w / 2 * S, c + h / 2), (c, c - h / 2)], fill=(232, 192, 112, 255))
    d.polygon([(c, c - h / 2), (c + w / 2 * S, c + h / 2), (c + 0.1 * w * S, c + h / 2)], fill=(186, 146, 78, 255))
    d.line([(c - w / 2 * S, c + h / 2), (c, c - h / 2), (c + w / 2 * S, c + h / 2)], fill=(110, 80, 34, 255), width=3 * S)
    return s


def boat_sprite(L=120, col=(214, 170, 110)):
    s = Image.new("RGBA", (round(1.2 * L * S), round(0.8 * L * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    ox, oy = 0.1 * L, 0.5 * L
    hull = [(0, -0.07), (0.12, 0), (0.88, 0), (1.0, -0.1), (0.93, 0.1), (0.72, 0.19), (0.3, 0.19), (0.08, 0.1)]
    d.polygon([((ox + x * L) * S, (oy + y * L) * S) for x, y in hull], fill=col + (255,), outline=(90, 60, 30, 255), width=2 * S)
    d.line([((ox + 0.5 * L) * S, oy * S), ((ox + 0.5 * L) * S, (oy - 0.42 * L) * S)], fill=(90, 60, 30, 255), width=3 * S)
    d.polygon([((ox + 0.53 * L) * S, (oy - 0.4 * L) * S), ((ox + 0.8 * L) * S, (oy - 0.07 * L) * S),
               ((ox + 0.53 * L) * S, (oy - 0.05 * L) * S)], fill=(240, 232, 214, 255))
    return s


def garis(times):
    AY = 1000
    bg = navy(540, 980)
    k0, k1, xg, xd = year_x(2700), year_x(2400), year_x(2560), year_x(2200)
    lab_k = text_sprite([("KAPAL KEKOVA", 54, YELLOW, True), ("±2700–2400 SM", 38, WHITE, False)], gap=6)
    lab_g = text_sprite([("Piramida Giza", 36, WHITE, True), ("±2560 SM", 32, WHITE, False)], gap=4)
    lab_d = text_sprite([("Dokos, Yunani", 36, WHITE, True), ("±2200 SM", 32, WHITE, False)], gap=4)
    old = label([("rekor lama", 32, WHITE, False)])
    new = label([("rekor baru?", 40, YELLOW, True)], edge=YELLOW + (230,))
    end0, end1 = text_sprite([("3000 SM", 28, PALE, False)]), text_sprite([("2000 SM", 28, PALE, False)])
    pyr, boat = pyramid_sprite(110), boat_sprite(150)
    # Umurnya 0.05, hingga 0.55, empat 0.98, tahun 2.24, diklaim 2.95, kapal 3.58, karam 3.90, tertua 4.29, dunia 4.88
    t_giza, t_band0, t_band1, t_klab, t_dokos, t_new = 0.25, 0.5, 1.3, 0.98, 2.95, 4.29
    frames = []
    for t in times:
        im = bg.copy()
        glow = layer()
        dg = ImageDraw.Draw(glow)
        top = layer()
        d = ImageDraw.Draw(top)
        u = ramp(t, 0.0, 0.35)
        if u > 0:
            xe = 90 + 900 * u
            d.line(sc([(90, AY), (xe, AY)]), fill=(255, 255, 255, 235), width=5 * S)
            for y in range(3000, 1999, -100):
                x = year_x(y)
                if x <= xe:
                    tk = 16 if y % 500 == 0 else 9
                    d.line(sc([(x, AY - tk), (x, AY + tk)]), fill=(255, 255, 255, 200), width=3 * S)
        put(top, end0, 130, 1040, a=ramp(t, 0.15, 0.4))
        put(top, end1, 950, 1040, a=ramp(t, 0.25, 0.5))
        # the Great Pyramid, below the axis
        g = pop(t, t_giza)
        if g > 0:
            dashed(d, [(xg, AY + 6), (xg, AY + 50)], (255, 255, 255, 170), 3, dash=8, gap=6)
            put(top, pyr, xg, 1094, scale=g)
            put(top, lab_g, xg, 1188, a=ramp(t, t_giza + 0.1, t_giza + 0.3))
        # the Kekova span grows over it
        b = ramp(t, t_band0, t_band1)
        if b > 0:
            xb = k0 + (k1 - k0) * b
            boost = 1 + 0.5 * math.exp(-((t - t_new - 0.1) / 0.25) ** 2) + 0.25 * math.exp(-((t - 2.24) / 0.2) ** 2)
            wd = xb - k0  # PIL needs a corner radius no larger than half the box
            dg.rounded_rectangle(sc([(k0 - 6, AY - 30), (xb + 6, AY + 30)]), radius=min(24, (wd + 12) / 2) * S,
                                 fill=YELLOW + (min(255, round(150 * boost)),))
            if wd > 2:
                d.rounded_rectangle(sc([(k0, AY - 19), (xb, AY + 19)]), radius=min(16, wd / 2) * S, fill=(255, 214, 40, 255))
        kl = pop(t, t_klab)
        if kl > 0:
            d.line(sc([(497, 890), (497, AY - 24)]), fill=YELLOW + (round(220 * min(1, kl)),), width=3 * S)
            put(top, lab_k, 497, 826, scale=kl)
        # the old record, Dokos
        dk = pop(t, t_dokos)
        if dk > 0:
            dashed(d, [(xd, AY + 6), (xd, AY + 34)], (255, 255, 255, 170), 3, dash=8, gap=6)
            put(top, boat, xd, 1086, scale=dk)
            put(top, lab_d, xd, 1188, a=ramp(t, t_dokos + 0.1, t_dokos + 0.3))
            put(top, old, xd, 930, a=ramp(t, t_dokos + 0.35, t_dokos + 0.55), scale=pop(t, t_dokos + 0.35))
        put(top, new, 497, 722, scale=pop(t, t_new))
        im.alpha_composite(down(glow).filter(ImageFilter.GaussianBlur(10)))
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


# ---------- skema_kekova ----------
KEK = (29.86, 36.17)
V_MED = (32.4, 33.5, 110, 950)  # the eastern Mediterranean view of skema_guci: centre lon, lat, px per degree, y of the centre
V_KEK = (KEK[0], KEK[1], 300, 950)


def kekova(times):
    rings = med_land()
    bg = navy(540, 950)
    lab_tr = text_sprite([("TURKI", 56, (70, 56, 34), True)])
    lab_sea = text_sprite([("L A U T   T E N G A H", 28, (190, 214, 240), True)])
    lab_spot = label([("lokasi temuan", 36, WHITE, True)], edge=YELLOW + (230,))
    dot = marker()
    # Ditemukan 0.03, di 0.62, dasar 0.74, laut 1.05, Turki 1.29
    t_z0, t_z1, t_pulse, t_tr, t_spot = 0.05, 1.45, 0.62, 1.29, 0.9
    frames = []
    for t in times:
        z = ramp(t, t_z0, t_z1)
        clon = V_MED[0] + (V_KEK[0] - V_MED[0]) * z
        clat = V_MED[1] + (V_KEK[1] - V_MED[1]) * z
        k = math.exp(math.log(V_MED[2]) + (math.log(V_KEK[2]) - math.log(V_MED[2])) * z)
        xy = view(clon, clat, k, 950)
        im = bg.copy()
        im.alpha_composite(land_layer(rings, xy))
        top = layer()
        d = ImageDraw.Draw(top)
        x, y = xy(*KEK)
        if t >= t_pulse:
            for ph0 in (0.0, 0.45):
                ph = ((t - t_pulse + ph0) % 0.9) / 0.9
                ring(d, x, y, 16 + 60 * ph, YELLOW, 230 * (1 - ph) ** 1.5, w=4)
        put(top, dot, x, y, scale=0.75 * pop(t, 0.1))
        put(top, lab_spot, x, y + 86, a=ramp(t, t_spot, t_spot + 0.15), scale=pop(t, t_spot))
        put(top, lab_tr, *xy(30.4, 37.0), a=ramp(t, t_tr - 0.1, t_tr + 0.1), scale=pop(t, t_tr - 0.1))
        put(top, lab_sea, *xy(29.5, 35.3), a=0.8 * ramp(t, 0.6, 0.9))
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


# ---------- skema_dasar ----------
BED = [(-10, 935), (200, 978), (420, 1026), (640, 1074), (860, 1124), (1090, 1180)]


def bed_y(x):
    return float(np.interp(x, [p[0] for p in BED], [p[1] for p in BED]))


def water():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = np.clip((yy - 300) / 1300, 0, 1)[..., None]
    col = np.array([34, 118, 150]) * (1 - v) + np.array([8, 34, 68]) * v
    for x0, wd in ((180, 90), (470, 140), (780, 110)):  # light shafts from the surface
        col += (np.exp(-((xx - x0 - 0.35 * (yy - 300)) / wd) ** 2) * np.clip(1 - (yy - 300) / 1100, 0, 1))[..., None] * np.array([14, 30, 30])
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")


def dasar(times):
    bg = water()
    sand = layer()
    ds = ImageDraw.Draw(sand)
    ds.polygon(sc(BED + [(1090, H + 10), (-10, H + 10)]), fill=(176, 154, 112, 255))
    ds.line(sc(BED), fill=(214, 196, 150, 255), width=5 * S)
    rng = np.random.default_rng(18)
    for x in rng.uniform(0, W, 14):  # rocks on the slope
        r = rng.uniform(14, 34)
        y = bed_y(x) + rng.uniform(4, 60)
        ds.ellipse([(x - r * 1.4) * S, (y - r * 0.7) * S, (x + r * 1.4) * S, (y + r * 0.7) * S], fill=(120, 112, 96, 255))
    sand = down(sand)
    ang = math.atan2(BED[-1][1] - BED[0][1], BED[-1][0] - BED[0][0])
    ca, sa = math.cos(ang), math.sin(ang)
    cx, L = 520, 740

    def rot(x, y):  # hull coordinates (0..1 along, metres-ish up) -> screen, lying on the slope
        px, py = (x - 0.5) * L, y * L
        return cx + px * ca - py * sa, bed_y(cx) - 14 + px * sa + py * ca
    hull = [(0, -0.12), (0.1, -0.06), (0.9, -0.06), (1.0, -0.16), (0.94, 0.0), (0.74, 0.07), (0.28, 0.07), (0.07, 0.0)]
    hull_s = [rot(*p) for p in hull]
    jars = [(0.28 + 0.06 * k + 0.02 * (k % 2), -0.03 - 0.02 * (k % 3)) for k in range(9)]
    anchors = [(-0.05, 0.02, 3), (1.04, 0.03, 3), (0.62, 0.05, 1)]
    flakes = [(rng.uniform(0.08, 0.92), rng.uniform(-0.05, 0.06), rng.uniform(40, 150), rng.uniform(0, 0.6), rng.uniform(3, 7))
              for _ in range(140)]
    lab_hull = label([("lambung kayu: lenyap", 38, WHITE, True)])
    lab_jar = text_sprite([("guci", 46, YELLOW, True)])
    lab_anc = text_sprite([("jangkar batu", 38, WHITE, True)])
    badge = label([("UJI KARBON", 50, WHITE, True), ("tak ada kayu yang tersisa", 32, PALE, False)])
    # Masalahnya 0.05, kayu 1.27, kapalnya 1.54, sudah 1.98, lenyap 2.21, Umurnya 3.24, tak 4.02, bisa 4.18, diuji 4.50, karbon 4.93
    t_gone0, t_gone1, t_lab, t_badge, t_x = 1.27, 2.45, 2.5, 3.24, 4.02
    frames = []
    for t in times:
        im = bg.copy()
        im.alpha_composite(sand)
        top = layer()
        d = ImageDraw.Draw(top)
        g = ramp(t, t_gone0, t_gone1)  # how far the hull has gone
        if g < 1:
            hl = layer()
            dh = ImageDraw.Draw(hl)
            dh.polygon(sc(hull_s), fill=(132, 88, 48, 255), outline=(70, 44, 22, 255))
            for f in (0.25, 0.5, 0.75):  # planks
                dh.line(sc([rot(0.05 + 0.02 * f, -0.06 + 0.13 * f), rot(0.95 - 0.04 * f, -0.06 + 0.13 * f)]), fill=(96, 62, 32, 255), width=3 * S)
            for x in np.linspace(0.16, 0.84, 7):  # ribs
                dh.line(sc([rot(x, -0.07), rot(x, 0.065)]), fill=(84, 54, 28, 255), width=4 * S)
            im.alpha_composite(fade(down(hl), 0.92 * (1 - g)))
        if g > 0:
            dashed(d, hull_s + hull_s[:1], (255, 255, 255, round(120 * min(1, g * 2))), 3, dash=14, gap=10)
            for fx, fy, rise, dl, r in flakes:  # wood flakes drifting off
                q = ramp(t, t_gone0 + dl, t_gone0 + dl + 0.9)
                if 0 < q < 1:
                    x, y = rot(fx, fy)
                    y -= rise * q
                    d.ellipse([(x - r) * S, (y - r * 0.6) * S, (x + r) * S, (y + r * 0.6) * S], fill=(150, 100, 56, round(220 * (1 - q))))
        drop = 6 * g
        for k, (jx, jy) in enumerate(jars):
            x, y = rot(jx, jy)
            jar(d, x, y + drop - 44, 96, (196, 128, 84, 255), (92, 52, 30, 255), w=2)
        for ax, ay, holes in anchors:
            x, y = rot(ax, ay)
            y += drop
            d.polygon(sc([(x - 40, y + 28), (x + 40, y + 28), (x + 27, y - 34), (x - 27, y - 34)]), fill=(140, 140, 132, 255),
                      outline=(70, 70, 66, 255), width=2 * S)
            for h in range(holes):
                hy = y - 18 + 21 * h if holes == 3 else y - 10
                d.ellipse([(x - 7) * S, (hy - 7) * S, (x + 7) * S, (hy + 7) * S], fill=(60, 60, 56, 255))
        # labels once the hull has gone
        put(top, lab_hull, 450, 765, a=ramp(t, t_lab - 0.2, t_lab), scale=pop(t, t_lab - 0.2))
        jx, jy = rot(0.52, -0.05)
        put(top, lab_jar, jx, jy - 150, a=ramp(t, t_lab + 0.2, t_lab + 0.4))
        axx, ayy = rot(1.04, 0.03)
        put(top, lab_anc, min(axx, 900), ayy + 84, a=ramp(t, t_lab + 0.35, t_lab + 0.55))
        bb = pop(t, t_badge)
        if bb > 0:
            put(top, badge, 750, 650, scale=bb)
            xr = ramp(t, t_x, t_x + 0.3)  # a red cross over the badge
            if xr > 0:
                for (x0, y0), (x1, y1) in (((540, 580), (960, 720)), ((540, 720), (960, 580))):
                    d.line(sc([(x0, y0), (x0 + (x1 - x0) * xr, y0 + (y1 - y0) * xr)]), fill=RED + (245,), width=11 * S)
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


# ---------- skema_guci ----------
EGYPT, LEVANT = (31.3, 31.65), (35.57, 32.3)  # a jar off the Nile Delta; the Jordan Valley


def guci(times):
    xy = view(*V_MED)
    bg = navy(540, 950)
    bg.alpha_composite(land_layer(med_land(), xy))
    dot = marker()
    kx, ky = xy(*KEK)
    jk = (kx - 40, ky + 118)  # the Kekova jar, in the sea below the find spot
    je, jl = xy(*EGYPT), xy(*LEVANT)
    lab_k = label([("guci Kekova", 36, YELLOW, True)], edge=YELLOW + (230,))
    lab_e = label([("MESIR", 40, WHITE, True)])
    lab_l = label([("TIMUR TENGAH", 38, WHITE, True), ("Lembah Yordan", 28, PALE, False)])
    # Bentuknya 0.03, cocok 0.65, dengan 1.12, guci 1.36, Zaman 1.64, Perunggu 1.91, dari 2.44, Mesir 2.62, dan 3.09, Timur 3.25, Tengah 3.49
    t_cocok, t_ref, t_eg, t_lv = 0.65, 1.36, 2.62, 3.25

    def link(a, b, bend):
        mx, my = (a[0] + b[0]) / 2 + bend[0], (a[1] + b[1]) / 2 + bend[1]
        return [((1 - s) ** 2 * a[0] + 2 * (1 - s) * s * mx + s * s * b[0], (1 - s) ** 2 * a[1] + 2 * (1 - s) * s * my + s * s * b[1])
                for s in np.linspace(0, 1, 40)]
    path_e, path_l = link(jk, je, (-60, 0)), link(jk, jl, (0, 60))
    len_e = sum(math.dist(p, q) for p, q in zip(path_e, path_e[1:]))
    len_l = sum(math.dist(p, q) for p, q in zip(path_l, path_l[1:]))
    frames = []
    for t in times:
        im = bg.copy()
        glow = layer()
        dg = ImageDraw.Draw(glow)
        top = layer()
        d = ImageDraw.Draw(top)
        put(top, dot, kx, ky, scale=0.7)
        boost = 1 + 0.6 * math.exp(-((t - t_cocok - 0.12) / 0.22) ** 2)
        dg.ellipse([(jk[0] - 60 * boost) * S, (jk[1] - 70 * boost) * S, (jk[0] + 60 * boost) * S, (jk[1] + 70 * boost) * S],
                   fill=YELLOW + (round(110 * boost),))
        for path, L, t0 in ((path_e, len_e, t_eg), (path_l, len_l, t_lv)):
            u = ramp(t, t0, t0 + 0.45)
            if u > 0:
                dashed(d, path, (255, 255, 255, 220), 4, dash=16, gap=11, upto=u * L)
        jar(d, jk[0], jk[1], 150, (255, 206, 60, 255), (110, 70, 0, 255), w=3)
        put(top, lab_k, jk[0], jk[1] + 124, a=ramp(t, 0.1, 0.3))
        for (x, y), t0, lab, ly in ((je, t_eg, lab_e, 102), (jl, t_lv, lab_l, 124)):
            a = ramp(t, t_ref + (0.15 if lab is lab_l else 0), t_ref + 0.35 + (0.15 if lab is lab_l else 0))
            if a <= 0:
                continue
            f = ramp(t, t0, t0 + 0.2)
            fill = (round(255 * f), round(206 * f + 40 * (1 - f)), round(60 * f + 60 * (1 - f)), round(255 * max(a * 0.35, f)))
            jar(d, x, y, 124 * (1 + 0.12 * math.exp(-((t - t0 - 0.1) / 0.15) ** 2)), fill, (255, 255, 255, round(230 * a)), w=3)
            put(top, lab, x, y + ly, a=ramp(t, t0, t0 + 0.15), scale=pop(t, t0))
            c = pop(t, t0 + 0.35)
            if c > 0:
                check(d, x + 70, y - 62, 30 * c)
        im.alpha_composite(down(glow).filter(ImageFilter.GaussianBlur(16)))
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


N = {"garis": 177, "kekova": 72, "dasar": 177, "guci": 138}
if __name__ == "__main__":
    args = sys.argv[2:]
    sheet = None
    if "--sheet" in args:
        i = args.index("--sheet")
        sheet, ts = args[i + 1], [float(v) for v in args[i + 2].split(",")]
        args = args[:i]
    for name in args or list(N):
        if sheet:
            fr = [f.convert("RGB").resize((W // 3, H // 3)) for f in globals()[name](ts)]
            sh = Image.new("RGB", (len(fr) * W // 3, H // 3))
            for k, f in enumerate(fr):
                sh.paste(f, (k * W // 3, 0))
            sh.save(sheet.replace(".jpg", f"_{name}.jpg"), quality=85)
        else:
            encode(globals()[name]([i / FPS for i in range(N[name])]), f"clips/skema_{name}.mp4")
