"""Schematic animations for Titik Heran #23 (run in the episode work dir; writes clips/skema_tuanan.mp4, skema_main.mp4 and
skema_selamat.mp4).
usage: python3 skema23.py GEO_DIR [tuanan|main|selamat ...] [--sheet out.jpg t1,t2,...]
       (GEO_DIR holds ne_10m_land.geojson and ne_50m_admin_0_boundary_lines_land.geojson from github.com/nvkelso/natural-earth-vector,
       folder geojson/; --sheet saves those frames as a contact sheet instead of encoding)
skema_tuanan: Borneo from the Natural Earth coastlines; the map closes in on the Tuanan research station (2°09'S 114°26'E, Mawas,
Central Kalimantan), where 31 wild mother-infant pairs were followed for ±32,000 hours over 15 years (Jacobson et al. 2026, PNAS;
Max Planck Society).
skema_main: a forest seen from above with the home ranges of two mothers. On an ordinary day mother A keeps to a short loop; on a
play day she walks much farther, towards mother B, whose infant is the same age, and the two infants play. Schematic: the paths
are not tracked data.
skema_selamat: 53 orangutans rescued from the fires in West Kalimantan, 1 Aug - 21 Oct 2026 (BKSDA and YIARI, via Mongabay):
one icon per animal and the count running up to 53.
Event times are seconds from the start of each shot, read off `render.py 23 plan`.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, BOLD, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, dashed, encode
from skema13 import navy, marker
from skema17 import ring, label
from skema18 import clip_ring

NAMES = ("tuanan", "main", "selamat")
GEO = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in NAMES else "geo"
FUR, FUR_D, FACE, MUZZLE = (204, 102, 40), (142, 62, 22), (214, 160, 120), (240, 204, 166)
TUANAN = (114.433, -2.15)


def orangutan_sprite(r, face=FACE):
    """an orangutan face as an icon of radius r (1x): shaggy orange head, a bare face with a pale muzzle, dark eyes"""
    im = Image.new("RGBA", (round(3 * r * S), round(3 * r * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = 1.5 * r * S

    def e(x, y, rx, ry, fill):
        d.ellipse([c + (x - rx) * S, c + (y - ry) * S, c + (x + rx) * S, c + (y + ry) * S], fill=fill)
    d.polygon([(c + r * S * (1.16 if k % 2 else 0.96) * math.cos(math.pi * k / 18 - 0.09),
                c + r * S * (1.16 if k % 2 else 0.96) * math.sin(math.pi * k / 18 - 0.09)) for k in range(36)], fill=FUR_D + (255,))
    e(0, 0, r, 0.97 * r, FUR + (255,))
    e(0, 0.12 * r, 0.7 * r, 0.7 * r, face + (255,))
    e(0, 0.42 * r, 0.46 * r, 0.34 * r, MUZZLE + (255,))
    for sx in (-1, 1):
        e(sx * 0.27 * r, -0.1 * r, 0.13 * r, 0.15 * r, (34, 22, 16, 255))
        e(sx * 0.27 * r - 0.04 * r, -0.15 * r, 0.045 * r, 0.045 * r, (255, 255, 255, 220))
        e(sx * 0.08 * r, 0.3 * r, 0.05 * r, 0.04 * r, (90, 56, 40, 255))
    d.arc([c - 0.2 * r * S, c + 0.36 * r * S, c + 0.2 * r * S, c + 0.6 * r * S], 20, 160, fill=(110, 66, 46, 255), width=max(1, round(0.06 * r * S)))
    return im


# ---------- skema_tuanan ----------
def borneo_land():
    rings = []
    for f in json.load(open(os.path.join(GEO, "ne_10m_land.geojson")))["features"]:
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            r = poly[0]
            lo, la = [p[0] for p in r], [p[1] for p in r]
            if max(lo) < 100 or min(lo) > 128 or max(la) < -12 or min(la) > 12:
                continue
            c = clip_ring(r, 100, -12, 128, 12)
            if len(c) > 2:
                rings.append(c)
    isl = next(r for r in rings if min(p[0] for p in r) < TUANAN[0] < max(p[0] for p in r) and
               min(p[1] for p in r) < TUANAN[1] < max(p[1] for p in r) and max(p[0] for p in r) - min(p[0] for p in r) < 12)
    borders = []
    for f in json.load(open(os.path.join(GEO, "ne_50m_admin_0_boundary_lines_land.geojson")))["features"]:
        g = f["geometry"]
        for ln in g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]:
            if all(108 < p[0] < 120 and -5 < p[1] < 8 for p in ln):
                borders.append(ln)
    return rings, isl, borders


def tuanan(times):
    rings, isl, borders = borneo_land()
    bg = navy(540, 900)
    lab_kal = text_sprite([("KALIMANTAN", 50, (70, 56, 34), True)])
    lab_my = text_sprite([("MALAYSIA", 30, (90, 76, 52), True)])
    lab_pin = label([("Stasiun Riset Tuanan", 40, WHITE, True), ("Kalimantan Tengah", 32, YELLOW, False)], edge=YELLOW + (230,))
    kartu = label([("31 pasang induk & anak", 40, WHITE, True), ("±32.000 jam pengamatan", 32, YELLOW, False)])
    dot = marker()
    # Lima 0.02, belas 0.33, tahun 0.71, diamati 1.08, di 1.54, Kalimantan 1.69, Tengah 2.15
    t_pin, t_z0, t_z1, t_card, t_lab = 0.3, 0.55, 1.65, 0.85, 1.6
    v0, v1 = (114.0, 0.9, 60.0), (114.6, -1.6, 125.0)
    out = []
    for t in times:
        z = ramp(t, t_z0, t_z1)
        clon, clat = v0[0] + (v1[0] - v0[0]) * z, v0[1] + (v1[1] - v0[1]) * z
        k = math.exp(math.log(v0[2]) + (math.log(v1[2]) - math.log(v0[2])) * z)

        def xy(lon, lat):
            return 540 + (lon - clon) * k, 900 - (lat - clat) * k
        im = bg.copy()
        lay = layer()
        d = ImageDraw.Draw(lay)
        for r in rings:
            p = [xy(*q) for q in r]
            xs, ys = [x for x, _ in p], [y for _, y in p]
            if max(xs) < -50 or min(xs) > W + 50 or max(ys) < -50 or min(ys) > H + 50:
                continue
            hot = r is isl
            d.polygon(sc(p), fill=(222, 200, 150, 255) if hot else (150, 134, 102, 255),
                      outline=(120, 100, 68, 255) if hot else (96, 84, 62, 255), width=2 * S)
        for ln in borders:
            dashed(d, [xy(*q) for q in ln], fill=(120, 100, 68, 200), width=3, dash=12, gap=9)
        im.alpha_composite(fade(down(lay), ramp(t, 0.0, 0.25)))
        top = layer()
        d = ImageDraw.Draw(top)
        out_a = 1 - ramp(t, t_z0, t_z0 + 0.4)
        put(top, lab_kal, *xy(113.0, 0.3), a=ramp(t, 0.1, 0.35) * out_a)
        put(top, lab_my, *xy(113.6, 2.75), a=0.9 * ramp(t, 0.1, 0.35) * out_a)
        px, py = xy(*TUANAN)
        if t >= t_pin:
            for ph0 in (0.0, 0.5):
                ph = ((t - t_pin + ph0) % 1.0) / 1.0
                ring(d, px, py, 16 + 64 * ph, YELLOW, 230 * (1 - ph) ** 1.5, w=4)
            put(top, dot, px, py, scale=pop(t, t_pin))
        put(top, lab_pin, px, py - 124, a=ramp(t, t_lab, t_lab + 0.15), scale=pop(t, t_lab))
        put(top, kartu, 540, 1120, a=ramp(t, t_card, t_card + 0.15), scale=pop(t, t_card))  # clear of the captions below
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_main ----------
def canopy(seed=23):
    """a rainforest seen from above: overlapping crowns lit from the top left, darkened so the marks on it read"""
    rng = np.random.default_rng(seed)
    im = Image.new("RGB", (W, H), (14, 44, 26))
    d = ImageDraw.Draw(im)
    crowns = sorted(((rng.uniform(-60, W + 60), rng.uniform(-60, H + 60), rng.uniform(24, 64), rng.uniform(0.7, 1.2))
                     for _ in range(1500)), key=lambda c: c[1])
    for x, y, r, g in crowns:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(int(12 * g), int(40 * g), int(22 * g)))
        d.ellipse([x - 0.95 * r - 2, y - 0.95 * r - 3, x + 0.88 * r - 2, y + 0.86 * r - 3], fill=(int(30 * g), int(88 * g), int(42 * g)))
        d.ellipse([x - 0.62 * r - 0.2 * r, y - 0.6 * r - 0.25 * r, x + 0.4 * r - 0.2 * r, y + 0.36 * r - 0.25 * r],
                  fill=(int(44 * g), int(116 * g), int(54 * g)))
    a = np.asarray(im.filter(ImageFilter.GaussianBlur(2.2)), np.float32) * 0.64
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= (1 - 0.45 * np.clip(((xx - 540) ** 2 + (yy - 900) ** 2) / 1000 ** 2, 0, 1))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def along(pts, u):
    """the point at fraction u of a polyline's length"""
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    goal = max(0.0, min(1.0, u)) * sum(seg)
    for (a, b), L in zip(zip(pts, pts[1:]), seg):
        if goal <= L:
            return a[0] + (b[0] - a[0]) * goal / max(L, 1e-6), a[1] + (b[1] - a[1]) * goal / max(L, 1e-6)
        goal -= L
    return pts[-1]


def part(pts, u):
    """the polyline cut at fraction u of its length"""
    if u <= 0:
        return []
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    goal, outp = min(1.0, u) * sum(seg), [pts[0]]
    for (a, b), L in zip(zip(pts, pts[1:]), seg):
        if goal <= L:
            outp.append((a[0] + (b[0] - a[0]) * goal / max(L, 1e-6), a[1] + (b[1] - a[1]) * goal / max(L, 1e-6)))
            return outp
        outp.append(b)
        goal -= L
    return outp


def smooth(pts, n=3):
    """Chaikin smoothing of an open polyline (skema11's chaikin closes the ring), keeping both ends"""
    for _ in range(n):
        q = [pts[0]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            q += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        pts = q + [pts[-1]]
    return pts


def burst(d, x, y, k, col=YELLOW):
    """a star burst of short rays, k from 0 to 1"""
    if k <= 0 or k >= 1:
        return
    for i in range(10):
        a = 2 * math.pi * i / 10 + 0.3
        r0, r1 = 34 + 50 * k, 58 + 70 * k
        d.line(sc([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))]),
               fill=col + (round(255 * (1 - k)),), width=6 * S)


def main(times):
    bg = canopy()
    A, B, R = (285, 1010), (800, 755), 198
    circ = [(math.cos(2 * math.pi * i / 120), math.sin(2 * math.pi * i / 120)) for i in range(121)]
    mom, baby = orangutan_sprite(48), orangutan_sprite(27, face=(232, 184, 150))
    loop = smooth([(A[0] + 80 * math.cos(a) + 8 * math.sin(3 * a), A[1] + 62 * math.sin(a)) for a in np.linspace(-2.4, 3.3, 30)], 2)
    path = smooth([A, (360, 905), (470, 915), (575, 852), (650, 828)], 3)
    lab_biasa = text_sprite([("hari biasa", 36, (235, 240, 235), True)])
    lab_main = text_sprite([("hari main", 42, YELLOW, True)])
    lab_play = text_sprite([("main!", 66, YELLOW, True)])
    # induk 0.05, berjalan 0.50, lebih 0.88, jauh 1.15, mendekati 1.79, induk 2.32, yang 2.70, anaknya 2.85, sebaya 3.16
    t_loop0, t_loop1, t_walk0, t_walk1, t_momB, t_kids, t_meet0, t_meet1 = 0.08, 0.55, 0.55, 1.75, 2.32, 2.85, 3.05, 3.4
    out = []
    for t in times:
        im = bg.copy()
        lay = layer()
        d = ImageDraw.Draw(lay)
        for (cx, cy), t0 in ((A, 0.0), (B, 0.1)):
            a = ramp(t, t0, t0 + 0.3)
            if a > 0:
                d.ellipse(sc([(cx - R, cy - R), (cx + R, cy + R)]), fill=(255, 255, 255, round(36 * a)))
                dashed(d, [(cx + R * x, cy + R * y) for x, y in circ], fill=(255, 255, 255, round(215 * a)), width=5, dash=18, gap=12)
        lp = part(loop, ramp(t, t_loop0, t_loop1))
        if len(lp) > 1:
            dashed(d, lp, fill=(240, 244, 240, round(240 * (1 - 0.4 * ramp(t, t_walk0, t_walk0 + 0.4)))), width=6, dash=10, gap=10)
        wp = part(path, ramp(t, t_walk0, t_walk1))
        if len(wp) > 1:
            dashed(d, wp, fill=YELLOW + (255,), width=8, dash=16, gap=11)
        im.alpha_composite(down(lay))
        top = layer()
        d = ImageDraw.Draw(top)
        put(top, lab_biasa, A[0], A[1] + 118, a=ramp(t, t_loop0 + 0.1, t_loop0 + 0.3) * (1 - 0.5 * ramp(t, t_walk0, t_walk0 + 0.4)))
        put(top, lab_main, 590, 985, a=ramp(t, t_walk0 + 0.4, t_walk0 + 0.6), scale=pop(t, t_walk0 + 0.4))
        mx, my = along(path, ramp(t, t_walk0, t_walk1))
        # the infants: A rides on its mother until they arrive, then both infants run to meet between them
        meet = (712, 792)
        m = ramp(t, t_meet0, t_meet1)
        ax, ay = mx + 40, my + 36
        bx0, by0 = B[0] + 10, B[1] + 62
        ax, ay = ax + (meet[0] - 28 - ax) * m, ay + (meet[1] - ay) * m
        bx, by = bx0 + (meet[0] + 28 - bx0) * m, by0 + (meet[1] - by0) * m
        if t >= t_momB:
            k = ramp(t, t_momB, t_momB + 0.5)
            ring(d, B[0], B[1], 62 + 44 * k, YELLOW, 255 * (1 - k), w=6)
        if t >= t_kids:  # same size rings: infants of the same age
            for x, y in ((ax, ay), (bx, by)):
                ring(d, x, y, 37 * pop(t, t_kids), YELLOW, 235, w=5)
        put(top, mom, *B, scale=pop(t, 0.15))
        put(top, baby, bx, by, scale=pop(t, 0.25))
        put(top, mom, mx, my, scale=pop(t, 0.05))
        put(top, baby, ax, ay, scale=pop(t, 0.12))
        if t >= t_meet1 - 0.05:
            burst(d, meet[0], meet[1], (t - t_meet1 + 0.05) / 0.45)
            put(top, lab_play, meet[0], meet[1] - 104, scale=pop(t, t_meet1 - 0.05))
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_selamat ----------
def selamat(times):
    bg = navy(540, 900)
    icon = orangutan_sprite(24)
    cols, x0, y0, dx, dy = 9, 148, 862, 98, 60
    cells = [(x0 + dx * (k % cols), y0 + dy * (k // cols)) for k in range(53)]
    head = text_sprite([("Kalimantan Barat · 1 Agu–21 Okt 2026", 38, WHITE, True), ("BKSDA & YIARI, via Mongabay", 28, (190, 214, 240), False)], gap=8)
    f_num = ImageFont.truetype(BOLD, 150 * S)
    # Lebih 0.05, dari 0.48, lima 0.79, puluh 1.09, orangutan 1.32, diselamatkan 1.77
    t_c0, t_c1, t_wave = 0.25, 1.32, 1.77
    out = []
    for t in times:
        im = bg.copy()
        top = layer()
        put(top, head, 540, 612, a=ramp(t, 0.0, 0.25))
        c = min(max((t - t_c0) / (t_c1 - t_c0), 0.0), 1.0)  # linear, so the count matches the icons
        if t >= t_c0:
            txt = str(round(53 * c))
            num = Image.new("RGBA", (600 * S, 200 * S), (0, 0, 0, 0))
            nd = ImageDraw.Draw(num)
            nd.text((303 * S, 106 * S), txt, font=f_num, fill=(0, 0, 0, 170), anchor="mm")
            nd.text((300 * S, 100 * S), txt, font=f_num, fill=YELLOW + (255,), anchor="mm")
            put(top, num, 540, 738, scale=pop(t, t_c1) if t >= t_c1 else 1.0)
        for k, (x, y) in enumerate(cells):
            tk = t_c0 + (t_c1 - t_c0) * (k + 1) / 53
            if t >= tk:
                w = t - t_wave - 0.012 * k  # a ripple of little hops across the grid on "diselamatkan"
                hop = 10 * math.sin(math.pi * w / 0.26) if 0 < w < 0.26 else 0.0
                put(top, icon, x, y - hop, scale=pop(t, tk, 0.2))
        im.alpha_composite(down(top))
        out.append(im)
    return out


N = {"tuanan": 84, "main": 123, "selamat": 87}
if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != GEO]
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
