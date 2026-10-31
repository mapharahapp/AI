"""Schematic animations for Titik Heran #27 (run in the episode work dir after `dl.py i:4040800 i:316611`;
writes clips/skema_peta.mp4, skema_asah.mp4 and skema_karat.mp4).
usage: python3 skema27.py GEO_DIR [peta|asah|karat ...] [--sheet out.jpg t1,t2,...]
       (GEO_DIR holds ne_10m_land.geojson from github.com/nvkelso/natural-earth-vector, folder geojson/;
       --sheet saves those frames as a contact sheet instead of encoding)
skema_peta: the Java Sea from the Natural Earth coastlines: a red pin on Banjarmasin (1859); the diamond leaves along a dashed route,
stops at Batavia and goes on through the Sunda Strait toward the Netherlands (shipped December 1861, arrived 1862; KNAW provenance report).
skema_asah: loose cut diamonds and tweezers (Pixabay 4040800, an illustration, not the Banjarmasin diamond) laid out like render.py's
kind b with a slow push; glints on "diasah", then a red "TIDAK TERJUAL" stamp on "tetap" (it never sold; Journal of Gemmology 2023).
skema_karat: a rough octahedron for the stone of about 70 carats (69 7/8 old carats in 1864) turns over the darkened, blurred
Pixabay 316611; the cushion brilliant cut from it in 1870 (38.23 carats, Rijksmuseum) shows through on the pause after "karat",
the rough cracks on "dan" and its outer shards fall on "pulang", while the counter runs from 70 to 38.
Event times are seconds from the start of each shot, read off `render.py 27 plan`.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, BOLD, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, dashed, glow_sprite, encode
from skema13 import navy
from skema17 import label
from skema18 import clip_ring
from skema24 import kind_b

N = {"peta": 70, "asah": 96, "karat": 150}
GEO = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in N else "geo"
RED, PALE_RED = (226, 40, 36), (255, 120, 110)


def gem(w=60):
    """a brilliant seen from the side, white with pale blue facets, on a soft glow; a 2x sprite centred on the stone"""
    sp = Image.new("RGBA", (2 * w * S, 2 * w * S))
    sp.alpha_composite(glow_sprite(w // 2, (200, 235, 255)).resize((2 * w * S, 2 * w * S)))
    d = ImageDraw.Draw(sp)
    c, g = w, w - 0.06 * w  # centre and girdle line (1x, sprite coordinates)
    gl, gr, tl, tr, tt, cu = c - 0.5 * w, c + 0.5 * w, c - 0.28 * w, c + 0.28 * w, g - 0.2 * w, g + 0.48 * w
    line = (110, 160, 215, 255)
    d.polygon(sc([(gl, g), (tl, tt), (tr, tt), (gr, g)]), fill=(236, 248, 255, 255))
    d.polygon(sc([(gl, g), (gr, g), (c, cu)]), fill=(186, 222, 250, 255))
    for x0, x1 in ((tl, c - 0.25 * w), (tr, c + 0.25 * w), (c, c)):
        d.line(sc([(x0, tt), (x1, g)]), fill=line, width=S)
    for x0 in (c - 0.25 * w, c + 0.25 * w, c):
        d.line(sc([(x0, g), (c, cu)]), fill=line, width=S)
    d.line(sc([(gl, g), (tl, tt), (tr, tt), (gr, g), (c, cu), (gl, g), (gr, g)]), fill=(70, 120, 180, 255), width=2 * S, joint="curve")
    return sp


def glint(r):
    """a four-point star with a glowing core, 2x sprite 4r wide"""
    sp = glow_sprite(r // 2, (255, 255, 255))
    sp = sp.resize((4 * r * S, 4 * r * S))
    d = ImageDraw.Draw(sp)
    c, k = 2 * r * S, 0.09 * r * S
    d.polygon([(c - 2 * r * S, c), (c, c - k), (c + 2 * r * S, c), (c, c + k)], fill=(255, 255, 255, 255))
    d.polygon([(c, c - 2 * r * S), (c + k, c), (c, c + 2 * r * S), (c - k, c)], fill=(255, 255, 255, 255))
    return sp


# ---------- skema_peta ----------
K, LON0, LAT0, CY = 80, 110.5, -4.0, 840
BANJAR, BATAVIA = (114.59, -3.32), (106.82, -6.1)
# along the sea west of Batavia, round the corner of Banten and out through the Sunda Strait
WEST = [(106.35, -5.98), (105.85, -6.02), (105.4, -6.45), (103.2, -7.3)]


def xy(lon, lat):
    return 540 + (lon - LON0) * K, CY - (lat - LAT0) * K


def land():
    rings = []
    for f in json.load(open(os.path.join(GEO, "ne_10m_land.geojson")))["features"]:
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            r = poly[0]
            lo, la = [p[0] for p in r], [p[1] for p in r]
            if max(lo) < 100 or min(lo) > 121 or max(la) < -20 or min(la) > 10:
                continue
            c = clip_ring(r, 100, -20, 121, 10)
            if len(c) > 2:
                rings.append(c)
    return rings


def dot_sprite(r, col):
    """a town dot with a white rim as a 2x sprite centred on the town"""
    sp = Image.new("RGBA", (4 * r * S, 4 * r * S))
    ImageDraw.Draw(sp).ellipse([r * S, r * S, 3 * r * S, 3 * r * S], fill=col + (255,), outline=(255, 255, 255, 255), width=3 * S)
    return sp


def spline(P, n=14):
    """a Catmull-Rom curve through the points (1x)"""
    P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        for u in (k / n for k in range(n)):
            out.append(tuple(0.5 * (2 * b + (c - a) * u + (2 * a - 5 * b + 4 * c - e) * u * u + (3 * b - a - 3 * c + e) * u ** 3)
                             for a, b, c, e in zip(P[i - 1], P[i], P[i + 1], P[i + 2])))
    return out + [P[-2]]


def route():
    """the voyage as a 1x polyline: a slight bow across the Java Sea, then round Banten and west out of the frame;
    and its length up to Batavia"""
    p0, p2 = xy(*BANJAR), xy(*BATAVIA)
    p1 = ((p0[0] + p2[0]) / 2, (p0[1] + p2[1]) / 2 - 70)
    pts = [((1 - u) ** 2 * p0[0] + 2 * u * (1 - u) * p1[0] + u * u * p2[0], (1 - u) ** 2 * p0[1] + 2 * u * (1 - u) * p1[1] + u * u * p2[1])
           for u in (k / 48 for k in range(49))]
    to_batavia = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    return pts + spline([p2] + [xy(*q) for q in WEST])[1:], to_batavia


def along(pts, s):
    """the point at length s along a polyline"""
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        if s <= L:
            return a[0] + (b[0] - a[0]) * s / L, a[1] + (b[1] - a[1]) * s / L
        s -= L
    return pts[-1]


def peta(times):
    bg = navy(560, 900)
    base = layer()
    d = ImageDraw.Draw(base)
    for r in land():
        d.polygon(sc([xy(*q) for q in r]), fill=(150, 134, 102, 255), outline=(96, 84, 62, 255), width=2 * S)
    base = down(base)
    pts, to_bat = route()
    total = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    red_dot, white_dot, stone = dot_sprite(11, RED), dot_sprite(9, (250, 250, 250)), gem(58)
    lab_banjar = label([("BANJARMASIN", 40, WHITE, True), ("1859", 38, PALE_RED, True)], edge=RED + (230,))
    lab_bat = label([("BATAVIA", 34, WHITE, True)])
    lab_nl = label([("ke Belanda", 36, YELLOW, True), ("tiba 1862", 32, WHITE, False)], edge=YELLOW + (220,))
    pb, pbt = xy(*BANJAR), xy(*BATAVIA)
    # berlian 0.04, ini 0.43, jadi 0.66, rampasan 0.89, perang. 1.40
    t_go, t_bat, t_on, t_out = 0.6, 1.2, 1.32, 1.95
    out = []
    for t in times:
        im = bg.copy()
        im.alpha_composite(fade(base, ramp(t, 0.0, 0.12)))
        # how far the stone has come: it eases into Batavia, waits a beat, then speeds off west
        s = to_bat * ramp(t, t_go, t_bat) + (total - to_bat + 60) * (min(max((t - t_on) / (t_out - t_on), 0.0), 1.0) ** 1.6)
        top = layer()
        d = ImageDraw.Draw(top)
        dashed(d, pts, fill=(255, 255, 255, 235), width=5, dash=18, gap=12, upto=s)
        for k in range(2):  # Banjarmasin pulses red, the place it was taken from
            u = ((t - 0.1) / 1.1 + k / 2) % 1
            r = 14 + 46 * u
            d.ellipse([(pb[0] - r) * S, (pb[1] - r) * S, (pb[0] + r) * S, (pb[1] + r) * S], outline=RED + (round(230 * (1 - u) * ramp(t, 0.05, 0.2)),), width=4 * S)
        put(top, white_dot, *pbt, scale=pop(t, t_bat - 0.12))
        put(top, red_dot, *pb, scale=pop(t, 0.02))
        put(top, lab_banjar, pb[0] - 70, pb[1] - 110, a=ramp(t, 0.08, 0.2), scale=pop(t, 0.08))
        put(top, lab_bat, pbt[0] + 46, pbt[1] + 58, a=ramp(t, t_bat - 0.08, t_bat + 0.04), scale=pop(t, t_bat - 0.08))
        put(top, lab_nl, 150, 900, a=ramp(t, 1.45, 1.57), scale=pop(t, 1.45))
        x, y = along(pts, s) if s < total else (-200, 0)
        bob = 4 * math.sin(2 * math.pi * t / 0.9)
        put(top, stone, x, y - 30 + bob, a=ramp(t, 0.06, 0.2), scale=pop(t, 0.06))
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_asah ----------
# a few of the stones in the photo (1x frame coordinates of the band before the push) that catch the light in turn
GLINTS = [(455, 773, 0.95), (262, 845, 1.08), (700, 878, 1.2), (580, 1150, 1.32), (352, 973, 1.44), (828, 830, 1.56), (174, 973, 1.66)]


def stamp_sprite(text="TIDAK TERJUAL", size=84, angle=8):
    """a red rubber stamp: a double frame round the word, the ink broken by speckles, tilted, over a soft dark shadow that keeps
    it readable on the bright stones; 2x sprite"""
    f = ImageFont.truetype(BOLD, size * S)
    x0, y0, x1, y1 = f.getbbox(text)
    pad, m = 36 * S, 50 * S
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    sp = Image.new("RGBA", (w + 2 * m, h + 2 * m))
    d = ImageDraw.Draw(sp)
    col = (222, 26, 34, 255)
    d.rounded_rectangle([m, m, m + w, m + h], radius=18 * S, outline=col, width=10 * S)
    d.rounded_rectangle([m + 17 * S, m + 17 * S, m + w - 17 * S, m + h - 17 * S], radius=10 * S, outline=col, width=3 * S)
    d.text((m + pad - x0, m + pad - y0), text, font=f, fill=col)
    rng = np.random.default_rng(7)
    speck = (rng.random((sp.height // 6, sp.width // 6)) > 0.08).astype(np.float32)
    mk = Image.fromarray((speck * 255).astype(np.uint8)).resize(sp.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(S))
    a = np.asarray(sp.getchannel("A"), np.float32) * np.asarray(mk, np.float32) / 255
    sp.putalpha(Image.fromarray(a.astype(np.uint8)))
    sh = Image.new("RGBA", sp.size)
    ImageDraw.Draw(sh).rounded_rectangle([m - 14 * S, m - 14 * S, m + w + 14 * S, m + h + 14 * S], radius=26 * S, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(16 * S))
    sh.alpha_composite(sp)
    return sh.rotate(angle, resample=Image.BICUBIC, expand=True)


def asah(times):
    base, top_y, band_h = kind_b("img/4040800.jpg")
    base = base.convert("RGB")
    stamp, star = stamp_sprite(), glint(26)
    # Di 0.05, Belanda 0.32, ia 0.83, diasah... 0.94, tetap 1.91, tak 2.22, laku. 2.37
    t_st, d_st = 1.9, 0.11
    out = []
    for t in times:
        k = 1.0 + 0.07 * t / 3.2  # the slow push
        dx = dy = 0.0
        if t > t_st + d_st:  # the frame jolts as the stamp lands
            e = math.exp(-(t - t_st - d_st) / 0.07)
            dx, dy = 9 * e * math.sin(70 * (t - t_st)), 7 * e * math.cos(55 * (t - t_st))
        big = base.resize((round(W * k), round(H * k)), Image.BICUBIC)
        x0, y0 = (big.width - W) / 2 + dx, (big.height - H) / 2 + dy
        im = big.crop((round(x0), round(y0), round(x0) + W, round(y0) + H)).convert("RGBA")
        top = layer()
        for gx, gy, g0 in GLINTS:
            u = (t - g0) / 0.42
            if 0 < u < 1:
                put(top, star, 540 + (gx - 540) * k - dx, 960 + (gy - 960) * k - dy, a=math.sin(math.pi * u), scale=0.35 + 0.65 * math.sin(math.pi * u))
        u = min(max((t - t_st) / d_st, 0.0), 1.0)
        if u > 0:
            put(top, stamp, 540, 1085, a=min(1.0, 3 * u), scale=1.75 - 0.75 * u * u)
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_karat ----------
SC, SA, SB, TILT = (540, 830), 225, 245, 0.3  # stone centre (1x), octahedron half-width and half-height, view from a little above
OCT = np.array([(SA, 0, 0), (0, 0, SA), (-SA, 0, 0), (0, 0, -SA), (0, SB, 0), (0, -SB, 0)], float)
OCT_F = [(4, i, (i + 1) % 4) for i in range(4)] + [(5, (i + 1) % 4, i) for i in range(4)]
OCT_E = [(i, (i + 1) % 4) for i in range(4)] + [(4, i) for i in range(4)] + [(5, i) for i in range(4)]
LIGHT = np.array([-0.45, 0.6, 0.66]) / np.linalg.norm([-0.45, 0.6, 0.66])


def turn(P, th):
    """rotate points (n, 3) about the vertical axis by th, then tip the top toward the viewer by TILT (viewer on +z)"""
    c, s, ct, st = math.cos(th), math.sin(th), math.cos(TILT), math.sin(TILT)
    x1, z1 = P[:, 0] * c + P[:, 2] * s, -P[:, 0] * s + P[:, 2] * c
    return np.stack([x1, P[:, 1] * ct - z1 * st, P[:, 1] * st + z1 * ct], 1)


def screen(Q):
    return [(SC[0] + x, SC[1] - y) for x, y, _ in Q]


def brilliant():
    """vertices and edges of the cushion brilliant inside the octahedron: girdle on the equator, table at 0.35 SB, culet at -0.75 SB"""
    def cushion(phi, s):  # a squircle whose flat sides face the octahedron's faces
        a = phi - math.pi / 4
        return s / (abs(math.cos(a)) ** 3 + abs(math.sin(a)) ** 3) ** (1 / 3)
    G = [(cushion(p, 0.66 * SA) * math.cos(p), 0.0, cushion(p, 0.66 * SA) * math.sin(p)) for p in (2 * math.pi * j / 16 for j in range(16))]
    T = [(0.55 * cushion(p, 0.66 * SA) * math.cos(p), 0.35 * SB, 0.55 * cushion(p, 0.66 * SA) * math.sin(p))
         for p in (2 * math.pi * k / 8 for k in range(8))]
    P = np.array(G + T + [(0.0, -0.75 * SB, 0.0)])
    t0, cu = 16, 24
    E = [(j, (j + 1) % 16) for j in range(16)] + [(t0 + k, t0 + (k + 1) % 8) for k in range(8)]
    E += [(t0 + k, 2 * k) for k in range(8)] + [(t0 + k, 2 * k + 1) for k in range(8)] + [(t0 + (k + 1) % 8, 2 * k + 1) for k in range(8)]
    E += [(2 * k, cu) for k in range(8)]
    return P, E


def cracks(rng):
    """a jagged crack across each face of the octahedron, as barycentric points (face, [(u, v, w), ...])"""
    out = []
    for f in range(8):
        a, b = rng.uniform(0.2, 0.8), rng.uniform(0.2, 0.8)
        p0, p1 = np.array([1 - a, a, 0.0]), np.array([1 - b, 0.0, b])  # from edge AB to edge AC
        pts = [p0]
        for i in range(1, 6):
            q = p0 + (p1 - p0) * i / 6 + rng.normal(0, 0.05, 3)
            q = np.clip(q, 0.02, None)
            pts.append(q / q.sum())
        out.append((f, pts + [p1]))
    return out


def shards(rng):
    """the octahedron's faces each split into four triangles (3D, stone coordinates), with a random fling and spin"""
    out = []
    for i, j, k in OCT_F:
        A, B, C = OCT[i], OCT[j], OCT[k]
        ab, bc, ca = (A + B) / 2, (B + C) / 2, (C + A) / 2
        for tri in ((A, ab, ca), (ab, B, bc), (ca, bc, C), (ab, bc, ca)):
            out.append((np.array(tri), rng.uniform(170, 330), rng.uniform(-7, 7), rng.uniform(-40, 40)))
    return out


def shade(n, front):
    v = 0.5 + 0.5 * max(0.0, float(n @ LIGHT))
    return tuple(round(c * v) for c in (176, 206, 232)) + ((120 if front else 46),)


def karat(times):
    im0 = Image.open("img/316611.jpg").convert("RGB")
    k = max(W / im0.width, H / im0.height)
    im0 = im0.resize((round(im0.width * k), round(im0.height * k)), Image.LANCZOS)
    im0 = im0.crop(((im0.width - W) // 2, (im0.height - H) // 2, (im0.width - W) // 2 + W, (im0.height - H) // 2 + H))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.5 * np.clip(np.hypot((xx - 540) / 700, (yy - 900) / 1100), 0, 1)[..., None]
    bg = np.asarray(im0.filter(ImageFilter.GaussianBlur(26)), np.float32) * 0.5 * vig
    bg = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
    BP, BE = brilliant()
    rng = np.random.default_rng(27)
    CR, SH = cracks(rng), shards(rng)
    star = glint(30)
    # Tapi 0.05, ia 0.40, pergi 0.63, seberat 1.02, tujuh 1.40, puluh 1.64, karat... 1.87, dan 2.64, pulang 2.80, tinggal 3.34,
    # tiga 3.65, puluh 3.88, delapan. 4.03
    t_cut, t_crack, t_br, t_n0, t_n1 = 1.95, 2.5, 2.84, 3.34, 4.08
    old = (text_sprite([("batu mentah, 1859", 38, (220, 228, 236), False)]), text_sprite([("setelah diasah, 1870", 38, (220, 228, 236), False)]))
    out = []
    for t in times:
        th = 0.35 + 0.42 * t
        im = bg.copy()
        top = layer()
        d = ImageDraw.Draw(top)
        grow = ramp(t, 0.05, 0.55)
        # the rough stone, until it breaks
        if t < t_br:
            Q = turn(OCT, th)
            faces = []
            for i, j, kk in OCT_F:
                n = np.cross(OCT[j] - OCT[i], OCT[kk] - OCT[i])
                n = n if n @ (OCT[i] + OCT[j] + OCT[kk]) > 0 else -n
                n = turn(n[None] / np.linalg.norm(n), th)[0]
                faces.append(((Q[i, 2] + Q[j, 2] + Q[kk, 2]) / 3, (i, j, kk), n))
            for _, f, n in sorted(faces, key=lambda f: f[0]):
                col = shade(n, n[2] > 0)
                d.polygon(sc(screen(Q[list(f)])), fill=col[:3] + (round(col[3] * grow),))
            for i, j in OCT_E:
                front = (Q[i, 2] + Q[j, 2]) / 2 > -1
                d.line(sc(screen(Q[[i, j]])), fill=(226, 240, 255, round((235 if front else 90) * grow)), width=(3 if front else 2) * S)
            u = ramp(t, t_crack, t_br - 0.04)
            if u > 0:
                for f, bary in CR:
                    A = OCT[list(OCT_F[f])]
                    P3 = turn(np.array([b @ A for b in bary]), th)
                    pts = screen(P3)
                    n = max(2, round(len(pts) * u))
                    front = P3[:, 2].mean() > 0
                    d.line(sc(pts[:n]), fill=(40, 52, 70, 230 if front else 110), width=(3 if front else 2) * S, joint="curve")
        else:  # the shards fly off and fall
            dt = t - t_br
            fl = ramp(t, t_br + 0.3, t_br + 0.85)
            items = []
            for tri, speed, spin, lift in SH:
                Q = turn(tri, t_br * 0.42 + 0.35)
                c = Q.mean(0)
                n = np.cross(tri[1] - tri[0], tri[2] - tri[0])
                n = n if n @ tri.mean(0) > 0 else -n
                n = turn(n[None] / np.linalg.norm(n), t_br * 0.42 + 0.35)[0]
                dirn = np.array([c[0], -c[1]]) / (np.hypot(c[0], c[1]) + 1e-6)
                off = dirn * speed * dt + np.array([0.0, (lift - 140) * dt + 0.5 * 1700 * dt * dt])
                a = spin * dt
                pts = [(SC[0] + c[0] + off[0] + (x - c[0]) * math.cos(a) - (-(y - c[1])) * math.sin(a),
                        SC[1] - c[1] + off[1] + (x - c[0]) * math.sin(a) + (-(y - c[1])) * math.cos(a)) for x, y, _ in Q]
                items.append((c[2], pts, shade(n, n[2] > 0)))
            for _, pts, col in sorted(items, key=lambda it: it[0]):
                d.polygon(sc(pts), fill=col[:3] + (round(col[3] * 1.4 * (1 - fl)),), outline=(226, 240, 255, round(200 * (1 - fl))), width=2 * S)
        # the cut stone inside: dashed while it is only a plan, bright once it is free
        cut = ramp(t, t_cut, t_cut + 0.3)
        if cut > 0:
            Q = turn(BP, th)
            bright = ramp(t, t_br, t_br + 0.35)
            glow = Image.new("RGBA", (W, H))
            gd = ImageDraw.Draw(glow)
            for i, j in sorted(BE, key=lambda e: Q[e[0], 2] + Q[e[1], 2]):
                front = (Q[i, 2] + Q[j, 2]) / 2 > -1
                seg = screen(Q[[i, j]])
                if bright < 1:
                    d.line(sc(seg), fill=(255, 226, 90, round((190 if front else 80) * cut * (1 - bright))), width=2 * S)
                if bright > 0:
                    d.line(sc(seg), fill=(236, 248, 255, round((250 if front else 110) * bright)), width=(3 if front else 2) * S)
                    gd.line(seg, fill=(150, 210, 255, round(200 * bright)), width=7)
            if bright > 0:
                im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9)))
        # the counter under the stone
        if t >= t_n0:
            u = ramp(t, t_n0, t_n1)
            num = f"{round(70 - 32 * u)} KARAT"
            col = (255, round(255 - 135 * min(1.0, 3 * u)), round(255 - 145 * min(1.0, 3 * u)))
        else:
            num, col = "±70 KARAT", WHITE
        put(top, text_sprite([(num, 74, col, True)]), 540, 1116, a=ramp(t, 0.63, 0.75), scale=pop(t, 0.63) * (1 + 0.08 * math.sin(math.pi * ramp(t, t_n1 - 0.06, t_n1 + 0.14))))
        sw = ramp(t, t_n0, t_n0 + 0.25)
        put(top, old[0], 540, 1176, a=ramp(t, 0.7, 0.82) * (1 - sw))
        put(top, old[1], 540, 1176, a=sw)
        if t > 4.05:  # a last sparkle on the table
            u = (t - 4.05) / 0.5
            if u < 1:
                Q = turn(BP, th)
                tx, ty = screen(Q[[16 + 7]])[0]
                put(top, star, tx, ty, a=math.sin(math.pi * u), scale=0.4 + 0.6 * math.sin(math.pi * u))
        im.alpha_composite(down(top))
        out.append(im)
    return out


OUT = {"peta": "clips/skema_peta.mp4", "asah": "clips/skema_asah.mp4", "karat": "clips/skema_karat.mp4"}

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
            encode(globals()[name]([i / FPS for i in range(N[name])]), OUT[name])
