"""Schematic and reconstruction animations for Titik Heran #37 (run in the episode work dir after `dl.py i:3400179 i:1835823`;
writes clips/skema_peta.mp4, skema_kerangka.mp4, skema_tulang.mp4, skema_anak.mp4, skema_rekor.mp4 and skema_hidup.mp4).
usage: python3 skema37.py GEO_DIR [peta|kerangka|tulang|anak|rekor|hidup ...] [--sheet out.jpg t1,t2,...]
       (GEO_DIR holds ne_10m_land.geojson and ne_50m_admin_0_countries.geojson from github.com/nvkelso/natural-earth-vector,
       folder geojson/; --sheet saves those frames as a contact sheet instead of encoding)
No photo of Liang Tebo or of the skeleton (TB1) is free to use, so everything about the find is drawn:
skema_peta: Borneo and its neighbours from the Natural Earth coastlines over the dimmed Kapuas river photo (Pixabay 3400179, West
  Kalimantan, a stand-in). A dot pulses in the Sangkulirang-Mangkalihat karst of East Kalimantan: the cave's exact spot is not
  published, so the dot marks the karst.
skema_kerangka: a line-art skeleton (a diagram, not TB1's bones) lying face up on a dark burial patch on the mossy ledge of a cave
  photo (Pixabay 1835823, a stand-in; a tiny explorer on the rock is painted out). It is uncovered head to toe; the left lower leg
  (the distal third of the tibia and fibula, and the foot) is never drawn, and on "tanpa" a red dashed ghost shows what is missing.
  Face up with the head on the left, the body's left side is the upper side of the frame.
skema_tulang: close on the stump: the clean oblique cut glints on "rapi"; on "Bukan digigit" a fang sign is struck out; on
  "sembuh" the cut end rounds over (the healed bone end the researchers describe).
skema_anak: the reconstruction: a child's silhouette standing on the right leg with a wooden stick (the stick is a guess),
  backlit on a dark ledge in the same cave; a warm glow rises on "selamat".
skema_rekor: the two records as bars: Kalimantan 31.000 years (Maloney et al., Nature 2022) and France 7.000 years (the Neolithic
  farmer of Buthiers-Boulancourt), and the 24.000-year gap between them.
skema_hidup: the child grows into a teenager (6 to 9 more years) and three adults fade in by a fire glow on "dirawat".
Event times are seconds from the start of each clip, read off `render.py 37 plan`: skema_peta starts at 4,40 ("Liang" 0,41),
skema_kerangka at 6,27 ("tiga" 1,78, "tanpa" 3,73), skema_tulang at 11,53 ("rapi" 0,52, "Bukan" 1,49, "digigit" 1,79,
"Tulangnya" 2,80, "sembuh" 3,21), skema_anak at 15,53 ("Dan" 2,40, "selamat" 2,67), skema_rekor at 19,17 ("Prancis" 1,12,
"tujuh" 2,04, "ribu" 2,26, "lalu" 2,71), skema_hidup at 22,47 ("hidup" 0,24, "dirawat" 2,68).
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, text_sprite, chaikin, encode
from skema13 import navy
from skema18 import clip_ring
from skema35 import blur, sheet
from skema36 import edge_fill

N = {"peta": 66, "kerangka": 168, "tulang": 130, "anak": 120, "rekor": 110, "hidup": 128}  # each clip runs ~0,3 s past its shot
GEO = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in N else "geo"
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
RED, GOLD = (232, 44, 40), (255, 188, 86)
BONE = np.array([238, 231, 214], np.float32)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def wanted(i, times):
    return times is None or any(abs(i / FPS - x) < 0.5 / FPS for x in times)


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def noise(shape, scales, seed):
    """value noise: random grids of the given cell sizes, upscaled smoothly and mixed by weight (0-1)"""
    rng = np.random.default_rng(seed)
    h, w = shape
    out, tot = np.zeros((h, w), np.float32), 0.0
    for cell, amp in scales:
        g = rng.random((max(2, h // cell + 2), max(2, w // cell + 2)))
        out += np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w + 2 * cell, h + 2 * cell), Image.BICUBIC),
                          np.float32)[cell:cell + h, cell:cell + w] / 255 * amp
        tot += amp
    return out / tot


def mask_of(img2x):
    return np.asarray(img2x.resize((W, H), Image.LANCZOS), np.float32) / 255


def shift(a, dx=0, dy=0):
    return np.roll(np.roll(a, dy, 0), dx, 1)


def put1(base, sp, cx, cy, a=1.0, scale=1.0):
    """composite a 2x sprite centred on (cx, cy) onto a 1x image"""
    if a <= 0.01 or scale <= 0.01:
        return
    sp = sp.resize((max(1, round(sp.width * scale / S)), max(1, round(sp.height * scale / S))), Image.LANCZOS)
    if a < 1:
        sp.putalpha(sp.getchannel("A").point(lambda v: int(v * a)))
    base.alpha_composite(sp, (round(cx - sp.width / 2), round(cy - sp.height / 2)))


def put_left(base, sp, x, cy, a=1.0):
    """a text_sprite with its text's left edge at x (text_sprite pads 24 px on each side)"""
    put1(base, sp, x - 24 + sp.width / (2 * S), cy, a)


# ---------- the photos ----------
def cave(dy=0, s=1.5, x0=100):
    """the cave with the light beam (1835823, a stand-in) scaled by s, its column x0 on the left edge, moved down dy rows"""
    a = np.asarray(Image.open("img/1835823.jpg").convert("RGB"), np.float32).copy()
    for y in range(522, 555):  # paint out the tiny explorer on the rock: each row bridged across from the mist on either side
        l, r = a[y, 450], a[y, 488]
        a[y, 451:488] = l + (r - l) * (np.arange(1, 38, dtype=np.float32) / 38)[:, None]
    a[518:558, 446:492] = blur(a[510:566, 438:500], 1.5)[8:48, 8:54]
    im = to_img(a)
    big = np.asarray(im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS), np.float32)[:, x0:x0 + W]
    f = np.zeros((H, W, 3), np.float32)
    top, bot = max(0, dy), min(H, dy + big.shape[0])
    f[top:bot] = big[top - dy:bot - dy]
    if top > 0:
        f[:top] = edge_fill(big[:6], top, up=True)
    if bot < H:
        f[bot:] = edge_fill(big[-6:], H - bot, up=False)
    return f


def river():
    """3400179 (the Kapuas at dusk, a stand-in) covering the frame, dimmed and cooled so the map reads on it"""
    im = Image.open("img/3400179.jpg").convert("RGB")
    s = H / im.height
    big = np.asarray(im.resize((round(im.width * s), H), Image.LANCZOS), np.float32)
    x0 = (big.shape[1] - W) // 2
    f = blur(big[:, x0:x0 + W], 2.5)
    navy_ = np.array([10, 24, 50], np.float32)
    return f * 0.42 + navy_ * 0.58 * (0.6 + 0.4 * (YY / H))[..., None]


# ---------- skema_peta ----------
K, LON0, LAT0, CX, CY = 64, 114.0, 1.2, 520, 1080  # px per degree; LAT0 is the dot's latitude, on row CY
DOT = (118.05, 1.2)  # in the Sangkulirang-Mangkalihat karst, East Kalimantan (on land at the base of the peninsula)


def mxy(lon, lat):
    return CX + (lon - LON0) * K, CY + (LAT0 - lat) * K


def land_rings(lon0, lat0, lon1, lat1, path="ne_10m_land.geojson"):
    rings = []
    for f in json.load(open(os.path.join(GEO, path)))["features"]:
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            r = poly[0]
            lo, la = [p[0] for p in r], [p[1] for p in r]
            if max(lo) < lon0 or min(lo) > lon1 or max(la) < lat0 or min(la) > lat1:
                continue
            c = clip_ring(r, lon0, lat0, lon1, lat1)
            if len(c) > 2:
                rings.append(c)
    return rings


def is_borneo(r):
    lo, la = [p[0] for p in r], [p[1] for p in r]
    return 108 < min(lo) < 110 and 118 < max(lo) < 120 and -5 < min(la) < -3 and 6 < max(la) < 8


def peta_layer():
    """the map at 1x as RGBA: Borneo lit, its neighbours dim, coastlines white"""
    rings = land_rings(100, -14, 130, 14)
    g = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for r in sorted(rings, key=is_borneo):
        pts = [(x * S, y * S) for x, y in (mxy(*p) for p in r)]
        if is_borneo(r):
            d.polygon(pts, fill=(44, 82, 58, 235), outline=(255, 255, 255, 235), width=3 * S)
        else:
            d.polygon(pts, fill=(30, 48, 52, 170), outline=(255, 255, 255, 105), width=2 * S)
    return g.resize((W, H), Image.LANCZOS)


def skema_peta(times=None):
    bg = river()
    mp = peta_layer()
    lab = text_sprite([("LIANG TEBO", 44, YELLOW, True), ("karst Sangkulirang-Mangkalihat", 26, WHITE, False)], gap=6)
    box = Image.new("RGBA", lab.size, (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([14 * S, 16 * S, lab.width - 14 * S, lab.height - 16 * S], radius=14 * S,
                                          fill=(8, 24, 54, 215), outline=(255, 255, 255, 80), width=3 * S)
    box.alpha_composite(lab)
    dx, dy = mxy(*DOT)
    t_dot = 0.36  # "Liang" at 0,41
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        z = 1.0 + 0.05 * ramp(t, 0, N["peta"] / FPS)  # a slow push towards the dot
        a_map = ramp(t, 0.0, 0.3)
        m = mp.resize((round(W * z), round(H * z)), Image.BICUBIC)
        ox, oy = round(dx - dx * z), round(dy - dy * z)
        layer_ = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer_.paste(m, (ox, oy))
        im = to_img(bg).convert("RGBA")
        if a_map < 1:
            layer_.putalpha(layer_.getchannel("A").point(lambda v: int(v * a_map)))
        im.alpha_composite(layer_)
        # the dot: a glow, pulsing rings, a yellow core
        p = pop(t, t_dot, 0.32)
        if p > 0:
            ov = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            for k in range(3):
                ph = (t - t_dot - 0.05 - k * 0.42) / 1.25
                if 0 <= ph <= 1:
                    r, a = 16 + 70 * ph, 230 * (1 - ph)
                    d.ellipse([(dx - r) * S, (dy - r) * S, (dx + r) * S, (dy + r) * S], outline=YELLOW + (int(a),), width=4 * S)
            r = 13 * p
            d.ellipse([(dx - r - 5) * S, (dy - r - 5) * S, (dx + r + 5) * S, (dy + r + 5) * S], fill=(0, 0, 0, 120))
            d.ellipse([(dx - r) * S, (dy - r) * S, (dx + r) * S, (dy + r) * S], fill=YELLOW + (255,))
            im.alpha_composite(ov.resize((W, H), Image.LANCZOS))
        put1(im, box, dx - 255, dy - 4, a=ramp(t, t_dot + 0.12, t_dot + 0.3), scale=0.9 + 0.1 * pop(t, t_dot + 0.12, 0.3))
        frames.append(im.convert("RGB"))
    return frames


# ---------- the skeleton ----------
class Pen:
    """draws parts of the skeleton in model coordinates (1x, the whole body in frame) through a zoom: model point P lands on
    screen point C, scaled by z. Every part is filled light and outlined dark, in drawing order, so overlaps stay readable."""

    def __init__(self, z=1.0, P=(0, 0), C=(0, 0), ow=2.3):
        self.z, self.P, self.C = z, P, C
        self.ow = ow * z ** 0.55 * S
        self.L, self.A = Image.new("L", (W * S, H * S), 0), Image.new("L", (W * S, H * S), 0)
        self.dl, self.da = ImageDraw.Draw(self.L), ImageDraw.Draw(self.A)

    def xy(self, p):
        return ((self.C[0] + (p[0] - self.P[0]) * self.z) * S, (self.C[1] + (p[1] - self.P[1]) * self.z) * S)

    def cap(self, pts, w, light=255):
        q = [self.xy(p) for p in pts]
        for width, val in ((w * self.z * S + 2 * self.ow, 92), (w * self.z * S, light)):
            r = width / 2
            for dr in (self.dl, self.da):
                v = val if dr is self.dl else 255
                dr.line(q, fill=v, width=max(1, round(width)), joint="curve")
                for x, y in (q[0], q[-1]):
                    dr.ellipse([x - r, y - r, x + r, y + r], fill=v)

    def ell(self, c, rx, ry, light=255, hole=False):
        x, y = self.xy(c)
        rx, ry = rx * self.z * S, ry * self.z * S
        if hole:
            self.dl.ellipse([x - rx, y - ry, x + rx, y + ry], fill=34)
            return
        for dr in (self.dl, self.da):
            dr.ellipse([x - rx - self.ow, y - ry - self.ow, x + rx + self.ow, y + ry + self.ow], fill=92 if dr is self.dl else 255)
            dr.ellipse([x - rx, y - ry, x + rx, y + ry], fill=light if dr is self.dl else 255)

    def poly(self, pts, light=255, hole=False):
        q = [self.xy(p) for p in pts]
        if hole:
            self.dl.polygon(q, fill=34)
            return
        self.dl.polygon(q, fill=light, outline=92, width=max(1, round(self.ow)))
        self.da.polygon(q, fill=255, outline=255, width=max(1, round(self.ow)))

    def line(self, pts, w, val=34):
        self.dl.line([self.xy(p) for p in pts], fill=val, width=max(1, round(w * self.z ** 0.7 * S)), joint="curve")

    def rrect(self, c, w, h, r):
        x, y = self.xy(c)
        w, h, r = w * self.z * S / 2, h * self.z * S / 2, r * self.z * S
        self.dl.rounded_rectangle([x - w, y - h, x + w, y + h], radius=r, fill=255, outline=92, width=max(1, round(self.ow)))
        self.da.rounded_rectangle([x - w, y - h, x + w, y + h], radius=r, fill=255, outline=255, width=max(1, round(self.ow)))

    def done(self):
        return mask_of(self.L), mask_of(self.A)


Y0 = 930
CUT_T = 0.665  # the left tibia and fibula end two thirds of the way down (their distal third is missing)


def leg_bones(s):
    """(femur, tibia, fibula) as (start, end, width) for side s: -1 the body's left (upper in the frame), +1 its right"""
    return (((558, Y0 + s * 44), (752, Y0 + s * 30), 14), ((770, Y0 + s * 29), (928, Y0 + s * 25), 12.5),
            ((778, Y0 + s * 42), (925, Y0 + s * 37), 6.5))


def stump_poly(p0, p1, w, t_cut, slant, heal, n=14):
    """a bone shaft from p0 towards p1 cut at fraction t_cut by an oblique cut (its two edges end `slant` px apart along the
    axis); heal 0..1 rounds the cut end over into a smooth cap, a little thicker (the healed end)"""
    ux, uy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    nx, ny = -uy, ux
    c = t_cut * L
    h = w / 2 * (1 + 0.1 * heal)
    a0, a1 = c - slant / 2, c + slant / 2  # where the +n and -n edges end
    pts_sharp = [(a0 + (a1 - a0) * k / (n - 1), h - 2 * h * k / (n - 1)) for k in range(n)]
    cr = c - 0.35 * slant - 0.25 * w  # the rounded cap's centre on the axis
    pts_round = []
    for k in range(n):
        ph = math.pi / 2 - math.pi * k / (n - 1)
        pts_round.append((cr + 0.95 * h * math.cos(ph) + 0.18 * slant * math.sin(ph), h * math.sin(ph)))
    e = heal * heal * (3 - 2 * heal)
    end = [(sa + (ra - sa) * e, sb + (rb - sb) * e) for (sa, sb), (ra, rb) in zip(pts_sharp, pts_round)]
    shaft = [(0, w / 2)] + [(a, b) for a, b in end] + [(0, -w / 2)]
    out = [(p0[0] + ux * a + nx * b, p0[1] + uy * a + ny * b) for a, b in shaft]
    face = (p0[0] + ux * c, p0[1] + uy * c), (ux, uy), (nx, ny), h, slant
    return out, face


def draw_skeleton(pen, groups=("body", "rightleg", "leftleg"), heal=0.0, cut_face=0.0):
    """the skeleton lying face up, head on the left (model coordinates in px; the body's left side is the upper side)"""
    if "body" in groups:
        # arms along the sides (drawn first, the ribs and pelvis lie over their ends)
        for s in (-1, 1):
            pen.cap([(302, Y0 + s * 90), (430, Y0 + s * 97)], 9)
            pen.ell((430, Y0 + s * 97), 7, 7)
            pen.cap([(434, Y0 + s * 94), (540, Y0 + s * 100)], 5)
            pen.cap([(434, Y0 + s * 103), (540, Y0 + s * 106)], 5)
            pen.ell((548, Y0 + s * 103), 9, 8)
            for k in range(5):
                yy = Y0 + s * (93 + k * 5)
                pen.cap([(556, yy), (578, yy + s * (k - 2) * 1.5)], 3)
                pen.cap([(582, yy + s * (k - 2) * 1.5), (598 - abs(k - 2) * 3, yy + s * (k - 2) * 2.5)], 2.6)
            pen.ell((300, Y0 + s * 90), 10, 10)
        # spine: neck, chest and lower back
        for x in range(268, 297, 9):
            pen.rrect((x, Y0), 7, 15, 3)
        for k in range(12):
            pen.rrect((304 + k * 11.6, Y0), 9.5, 18, 3)
        for k in range(5):
            pen.rrect((446 + k * 14, Y0), 12, 25, 4)
        # ribs and breastbone
        for k in range(10):
            x0 = 310 + k * 12.5
            R = 46 + 22 * math.sin(math.pi * (k + 2) / 13)
            for s in (-1, 1):
                pts = [(x0 + 30 * u * u + 6 * u, Y0 + s * (10 + (R - 10) * math.sin(u * math.pi * 0.62))) for u in np.linspace(0, 1, 9)]
                pen.cap(pts, 4.6)
        pen.cap([(306, Y0), (378, Y0)], 12)
        pen.ell((307, Y0), 10, 11)
        # collarbones
        for s in (-1, 1):
            pen.cap([(304, Y0 + s * 10), (307, Y0 + s * 34), (300, Y0 + s * 60), (297, Y0 + s * 82)], 6)
        # pelvis
        for s in (-1, 1):
            wing = chaikin([(506, Y0 + s * 13), (502, Y0 + s * 44), (513, Y0 + s * 74), (535, Y0 + s * 77), (558, Y0 + s * 57),
                            (570, Y0 + s * 35), (558, Y0 + s * 15)], 2)
            pen.poly(wing)
            pen.poly(chaikin([(514, Y0 + s * 24), (512, Y0 + s * 46), (521, Y0 + s * 64), (536, Y0 + s * 65), (550, Y0 + s * 50),
                              (552, Y0 + s * 30)], 2), light=206)  # the hollow of the hip bone
            pen.cap([(566, Y0 + s * 38), (586, Y0 + s * 6)], 9)
            pen.cap([(560, Y0 + s * 44), (582, Y0 + s * 48), (590, Y0 + s * 22)], 7)
            pen.ell((576, Y0 + s * 32), 7, 8, hole=True)
        pen.poly([(510, Y0 - 15), (510, Y0 + 15), (552, Y0 + 6), (552, Y0 - 6)])
        # skull, top of the head on the left, face up
        pen.ell((201, Y0), 42, 34)
        pen.poly(chaikin([(222, Y0 - 30), (249, Y0 - 25), (263, Y0 - 11), (263, Y0 + 11), (249, Y0 + 25), (222, Y0 + 30)], 2))
        pen.ell((205, Y0 - 15), 10, 11, hole=True)
        pen.ell((205, Y0 + 15), 10, 11, hole=True)
        pen.poly([(221, Y0), (235, Y0 - 7), (235, Y0 + 7)], hole=True)
        pen.line([(245, Y0 - 15), (245, Y0 + 15)], 2.6)
        for y in (-9, -3, 3, 9):
            pen.line([(240, Y0 + y), (250, Y0 + y)], 1.6)
    for s, g in ((1, "rightleg"), (-1, "leftleg")):
        if g not in groups:
            continue
        (f0, f1, fw), (t0, t1, tw), (b0, b1, bw) = leg_bones(s)
        pen.ell((556, Y0 + s * 42), 10, 10)
        pen.cap([f0, (566, Y0 + s * 50), f1], fw)
        pen.ell((570, Y0 + s * 58), 8, 7)
        pen.ell((748, Y0 + s * 23), 9, 8)
        pen.ell((748, Y0 + s * 37), 9, 8)
        if s == 1:
            pen.cap([b0, b1], bw)
            pen.ell(b0, 5, 5)
            pen.ell(b1, 5.5, 5.5)
            pen.cap([t0, t1], tw)
            pen.ell((770, Y0 + s * 23), 9, 7)
            pen.ell((770, Y0 + s * 35), 9, 7)
            pen.ell((930, Y0 + s * 20), 6, 6)
            draw_foot(pen, s)
        else:  # the stump: both bones end in a clean oblique cut
            fib, ffib = stump_poly(b0, b1, bw, CUT_T - 0.03, 9, heal)
            pen.poly(fib)
            pen.ell(b0, 5, 5)
            tib, ftib = stump_poly(t0, t1, tw, CUT_T, 12, heal)
            pen.poly(tib)
            pen.ell((770, Y0 + s * 23), 9, 7)
            pen.ell((770, Y0 + s * 35), 9, 7)
            if cut_face > 0.01:  # the flat cut faces, seen a little from the side, with the hollow inside each bone
                for (c, u, n_, h, slant), wid in ((ffib, bw), (ftib, tw)):
                    k = cut_face * (1 - heal) ** 2
                    if k > 0.02:
                        draw_face(pen, c, u, n_, h, slant, wid, k)
        pen.ell((760, Y0 + s * 30), 7, 8)  # kneecap


def draw_face(pen, c, u, n_, h, slant, wid, k):
    """the flat oblique cut face of a bone, seen a little from the side: an ellipse on the cut line (from the +n edge, the
    nearer end, to the -n edge), with the hollow of the bone inside it"""
    pts, inner = [], []
    for j in range(28):
        a = 2 * math.pi * j / 28
        al, ac = math.cos(a), math.sin(a)
        for scale, lst in ((1.0, pts), (0.52, inner)):
            pa = al * scale
            x = c[0] + n_[0] * pa * h - u[0] * pa * slant / 2 + u[0] * ac * wid * 0.2 * k * scale
            y = c[1] + n_[1] * pa * h - u[1] * pa * slant / 2 + u[1] * ac * wid * 0.2 * k * scale
            lst.append((x, y))
    pen.poly(pts, light=246)
    pen.poly(inner, light=168)


def draw_foot(pen, s):
    pen.ell((940, Y0 + s * 27), 12, 14)
    for k in range(5):
        a = math.radians(30 + 9 * k) * 1.0
        x0, y0 = 948, Y0 + s * (19 + k * 4.5)
        x1, y1 = x0 + 24 * math.cos(a), y0 + s * 24 * math.sin(a)
        pen.cap([(x0, y0), (x1, y1)], 4.2)
        x2, y2 = x1 + 12 * math.cos(a + 0.12), y1 + s * 12 * math.sin(a + 0.12)
        pen.cap([(x1 + 2 * math.cos(a), y1 + s * 2 * math.sin(a)), (x2, y2)], 3.4)


def ghost_mask(pen_args):
    """the missing distal third of the left tibia and fibula and the left foot, as a mask"""
    pen = Pen(*pen_args)
    (f0, f1, fw), (t0, t1, tw), (b0, b1, bw) = leg_bones(-1)
    pen.cap([(t0[0] + (t1[0] - t0[0]) * (CUT_T - 0.02), t0[1] + (t1[1] - t0[1]) * (CUT_T - 0.02)), t1], tw)
    pen.cap([(b0[0] + (b1[0] - b0[0]) * (CUT_T - 0.05), b0[1] + (b1[1] - b0[1]) * (CUT_T - 0.05)), b1], bw)
    pen.ell((930, Y0 - 20), 6, 6)
    draw_foot(pen, -1)
    return pen.done()[1]


def ghost_shape(pen_args):
    """the missing part as one smooth shape (the toes merged into a foot outline)"""
    gm = ghost_mask(pen_args)
    g = Image.fromarray((gm * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(3))
    return np.clip((np.asarray(g, np.float32) / 255 - 0.35) * 4, 0, 1)


def bones_rgb(Lm, Am, sh_r=2.0, depth=0.22):
    """bone colour from the light/outline layer, shaded darker towards the edges (sh_r: how far the shading reaches)"""
    sh = np.clip(blur(Am, sh_r) * 1.25, 0, 1)
    return BONE * Lm[..., None] * ((1 - depth) + depth * sh)[..., None]


def soil(shape_box, seed=7, cx=560, cy=935, rx=470, ry=150):
    """an irregular dark burial patch: alpha and colour"""
    rng = np.random.default_rng(seed)
    pts = []
    for k in range(32):
        a = 2 * math.pi * k / 32
        r = 1 + 0.07 * math.sin(3 * a + 1) + 0.05 * math.sin(7 * a + 2) + rng.uniform(-0.03, 0.03)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(chaikin(pts, 3), fill=255)
    alpha = np.asarray(m.filter(ImageFilter.GaussianBlur(12)), np.float32) / 255
    n = noise((H, W), [(70, 1.0), (18, 0.7), (5, 0.45)], seed)
    col = np.array([50, 36, 26], np.float32) * (0.55 + 0.7 * n[..., None])
    return alpha, col


def kerangka_bg():
    bg = blur(cave(0), 1.6) * 0.5
    a, col = soil(None)
    bg = bg * (1 - 0.94 * a[..., None]) + col * 0.94 * a[..., None]
    beam = np.exp(-((XX - 600) ** 2) / (2 * 260.0 ** 2)) * np.clip(1.25 - YY / 1500, 0, 1)  # the beam's light on the patch
    return bg * (1 + 0.35 * beam[..., None])


STUMP = (875, Y0 - 28)  # the stump's end in model coordinates


def composite_bones(bg, Lm, Am, reveal=None, glow=0.0, sh_r=2.0, depth=0.22, shadow_px=6):
    if reveal is not None:
        Am = Am * reveal
    shadow = blur(shift(Am, shadow_px, round(shadow_px * 1.3)), shadow_px)
    out = bg * (1 - 0.55 * shadow * (1 - Am))[..., None]
    out = out + (blur(Am, 9) * 30 * (1 + glow))[..., None] * np.array([1.0, 0.97, 0.9], np.float32)
    col = bones_rgb(Lm, Am, sh_r, depth)
    return out * (1 - Am[..., None]) + col * Am[..., None]


def skema_kerangka(times=None):
    bg = kerangka_bg()
    t_rev0, t_rev1, t_ghost = 0.0, 1.45, 3.73  # uncovered during "kerangka manusia purba"; the ghost on "tanpa"
    t_zoom0, t_zoom1 = 4.35, N["kerangka"] / FPS
    still = None
    frames = []
    for i in range(N["kerangka"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        u = ramp(t, t_zoom0, t_zoom1 + 0.25)
        z = 1 + 0.55 * u
        C = (STUMP[0] + (700 - STUMP[0]) * u, STUMP[1] + (930 - STUMP[1]) * u)
        pen_args = (z, STUMP, C)
        if u <= 0 and still is not None:
            Lm, Am = still
        else:
            pen = Pen(*pen_args)
            draw_skeleton(pen)
            Lm, Am = pen.done()
            if u <= 0:
                still = (Lm, Am)
        if u > 0:  # the background zooms too
            bz = to_img(bg).resize((round(W * z), round(H * z)), Image.BICUBIC)
            ox, oy = round(C[0] - STUMP[0] * z), round(C[1] - STUMP[1] * z)
            canvas = Image.new("RGB", (W, H))
            canvas.paste(bz, (ox, oy))
            b = np.asarray(canvas, np.float32)
        else:
            b = bg
        front = 120 + (1010 - 120) * ramp(t, t_rev0, t_rev1)
        reveal = np.clip((front - XX) / 60, 0, 1) if t < t_rev1 + 0.1 else None
        out = composite_bones(b, Lm, Am, reveal)
        if t < t_rev1 + 0.1:  # a soft dust glow at the uncovering edge
            band = np.exp(-((XX - front) ** 2) / (2 * 22.0 ** 2)) * np.exp(-((YY - 930) ** 2) / (2 * 80.0 ** 2))
            out = out + (band * 55 * (1 - ramp(t, t_rev1 - 0.15, t_rev1 + 0.1)))[..., None] * np.array([1, 0.92, 0.75], np.float32)
        if t >= t_ghost:
            gm = ghost_shape(pen_args)
            g_img = Image.fromarray((gm * 255).astype(np.uint8))
            edge = np.clip(np.asarray(g_img.filter(ImageFilter.MaxFilter(5)), np.float32) / 255 - gm, 0, 1)
            dash = ((XX // 11 + YY // 11) % 2).astype(np.float32)
            k = ramp(t, t_ghost, t_ghost + 0.25)
            pulse = 0.7 + 0.3 * math.cos(2 * math.pi * (t - t_ghost) / 0.7)
            red = np.array(RED, np.float32)
            fa = gm * 0.26 * k * pulse
            out = out * (1 - fa[..., None]) + fa[..., None] * red
            ea = np.clip(edge * 1.8, 0, 1) * dash * k
            out = out * (1 - ea[..., None]) + ea[..., None] * red
            # a red ring round the stump's end
            sx, sy = C[0] + (STUMP[0] - STUMP[0]) * z, C[1]
            rr = (36 + 4 * math.sin(2 * math.pi * (t - t_ghost) / 0.7)) * z
            ring_ = np.exp(-((np.sqrt((XX - sx) ** 2 + (YY - sy) ** 2) - rr) ** 2) / (2 * 2.6 ** 2)) * ramp(t, t_ghost + 0.15, t_ghost + 0.4)
            out = out * (1 - ring_[..., None]) + ring_[..., None] * red
        frames.append(to_img(out))
    return frames


# ---------- skema_tulang ----------
def tulang_bg():
    n = noise((H, W), [(90, 1.0), (24, 0.7), (6, 0.5)], 11)
    col = np.array([56, 40, 29], np.float32) * (0.55 + 0.8 * n[..., None])
    beam = np.exp(-((XX - 640) ** 2) / (2 * 420.0 ** 2)) * np.clip(1.3 - YY / 1700, 0, 1)
    vig = np.clip(1 - 0.55 * (((XX - 560) / 900) ** 2 + ((YY - 980) / 1100) ** 2), 0.25, 1)
    return col * (0.75 + 0.6 * beam[..., None]) * vig[..., None]


def fang_sign(t, t_on, t_strike, t_off, r=122):
    """an animal-jaw sign in a white ring, struck out by a red ring and bar; RGBA at 2x"""
    sz = int(2.4 * r * S)
    im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = sz / 2
    R = r * S
    d.ellipse([c - R, c - R, c + R, c + R], fill=(8, 18, 40, 200), outline=(255, 255, 255, 235), width=5 * S)
    # an open animal mouth: a thick upper gum with two long fangs and small teeth, a lower gum with two short fangs
    wht = (255, 255, 255, 255)
    up = [(c + R * x, c + R * y) for x, y in chaikin([(-0.6, -0.12), (-0.42, -0.4), (0.0, -0.5), (0.42, -0.4), (0.6, -0.12),
                                                      (0.36, -0.2), (0.0, -0.25), (-0.36, -0.2)], 2)]
    d.polygon(up, fill=wht)
    for sgn in (-1, 1):
        x = c + sgn * 0.33 * R
        d.polygon([(x - 0.1 * R, c - 0.24 * R), (x + 0.1 * R, c - 0.24 * R), (x + sgn * 0.015 * R, c + 0.2 * R)], fill=wht)
    for k in (-1, 0, 1):
        x = c + k * 0.12 * R
        d.polygon([(x - 0.05 * R, c - 0.26 * R), (x + 0.05 * R, c - 0.26 * R), (x, c - 0.11 * R)], fill=wht)
    lo = [(c + R * x, c + R * y) for x, y in chaikin([(-0.52, 0.3), (-0.3, 0.37), (0.0, 0.4), (0.3, 0.37), (0.52, 0.3),
                                                      (0.4, 0.55), (0.0, 0.62), (-0.4, 0.55)], 2)]
    d.polygon(lo, fill=wht)
    for sgn in (-1, 1):
        x = c + sgn * 0.27 * R
        d.polygon([(x - 0.08 * R, c + 0.38 * R), (x + 0.08 * R, c + 0.38 * R), (x - sgn * 0.01 * R, c + 0.06 * R)], fill=wht)
    u = ramp(t, t_strike, t_strike + 0.22)
    if u > 0:
        R2 = R * 1.06
        d.arc([c - R2, c - R2, c + R2, c + R2], -90, -90 + 360 * u, fill=RED + (255,), width=12 * S)
        v = ramp(t, t_strike + 0.12, t_strike + 0.3)
        if v > 0:
            a = math.radians(-45)
            x0, y0 = c - math.cos(a) * R2 * 0.95, c - math.sin(a) * R2 * 0.95
            x1, y1 = c + math.cos(a) * R2 * 0.95, c + math.sin(a) * R2 * 0.95
            d.line([(x0, y0), (x0 + (x1 - x0) * v, y0 + (y1 - y0) * v)], fill=RED + (255,), width=13 * S)
    return im


def skema_tulang(times=None):
    bg = tulang_bg()
    t_rapi, t_bukan, t_gigit, t_tul, t_sembuh = 0.52, 1.49, 1.79, 2.80, 3.21
    frames = []
    for i in range(N["tulang"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        z = 6.4 + 2.6 * ramp(t, 0, 0.5) + 0.6 * ramp(t, 0.5, N["tulang"] / FPS)
        C = (640, 1010)
        heal = ramp(t, t_sembuh - 0.05, t_sembuh + 0.6)
        pen = Pen(z, STUMP, C, ow=1.3)
        draw_skeleton(pen, groups=("leftleg",), heal=heal, cut_face=1.0)
        Lm, Am = pen.done()
        # a fine grain along the shafts
        grain = noise((H, W), [(6, 1.0), (2, 0.5)], 5)
        Lm = Lm * (0.93 + 0.07 * grain)
        out = composite_bones(bg, Lm, Am, glow=0.4, sh_r=16, depth=0.42, shadow_px=14)
        # the glint: a bright spot running along the tibia's cut, then a flash
        (f0, f1, fw), (t0, t1, tw), (b0, b1, bw) = leg_bones(-1)
        _, (c, uu, nn, half, ang) = stump_poly(t0, t1, tw, CUT_T, 12, 0)
        g = ramp(t, t_rapi, t_rapi + 0.45)
        if 0 < g < 1 or (t_rapi + 0.45 <= t < t_rapi + 0.9):
            px = c[0] + nn[0] * tw / 2 * (1 - 2 * g) - uu[0] * 6 * (1 - 2 * g)
            py = c[1] + nn[1] * tw / 2 * (1 - 2 * g) - uu[1] * 6 * (1 - 2 * g)
            sx, sy = C[0] + (px - STUMP[0]) * z, C[1] + (py - STUMP[1]) * z
            fl = 1.0 if g < 1 else math.exp(-(t - t_rapi - 0.45) / 0.12)
            r2 = (XX - sx) ** 2 + (YY - sy) ** 2
            star = (np.exp(-r2 / (2 * 9.0 ** 2)) + 0.45 * np.exp(-r2 / (2 * 40.0 ** 2))) * fl
            star += 0.5 * fl * np.exp(-((XX - sx) ** 2) / (2 * 2.5 ** 2)) * np.exp(-((YY - sy) ** 2) / (2 * 60.0 ** 2))
            star += 0.5 * fl * np.exp(-((YY - sy) ** 2) / (2 * 2.5 ** 2)) * np.exp(-((XX - sx) ** 2) / (2 * 60.0 ** 2))
            out = out + star[..., None] * np.array([255, 246, 210], np.float32)
        # a yellow dashed guide along the cut plane, past both edges
        gd = ramp(t, t_rapi + 0.1, t_rapi + 0.45) * (1 - ramp(t, t_bukan - 0.2, t_bukan + 0.1))
        im = to_img(out).convert("RGBA")
        if gd > 0:
            ov = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            ex, ey = (nn[0] * tw / 2 - uu[0] * 6), (nn[1] * tw / 2 - uu[1] * 6)  # half the cut line, model px
            ax_, ay_ = C[0] + (c[0] - STUMP[0]) * z, C[1] + (c[1] - STUMP[1]) * z
            vx, vy = ex * z * 2.6, ey * z * 2.6
            for k in range(-9, 9):
                a, b = k / 9, (k + 0.55) / 9
                d.line([((ax_ + vx * a) * S, (ay_ + vy * a) * S), ((ax_ + vx * b) * S, (ay_ + vy * b) * S)],
                       fill=YELLOW + (int(235 * gd),), width=5 * S)
            im.alpha_composite(ov.resize((W, H), Image.LANCZOS))
        a_sign = ramp(t, t_bukan - 0.05, t_bukan + 0.15) * (1 - ramp(t, t_tul - 0.05, t_tul + 0.2))
        if a_sign > 0:
            sp = fang_sign(t, t_bukan, t_gigit, t_tul)
            put1(im, sp, 838, 790, a=a_sign, scale=0.85 + 0.15 * pop(t, t_bukan - 0.05, 0.3))
        out = np.asarray(im.convert("RGB"), np.float32)
        if heal > 0:  # a warm glow round the healed end
            ex_, ey_ = C[0] + (c[0] - STUMP[0]) * z, C[1] + (c[1] - STUMP[1]) * z
            r2 = (XX - ex_) ** 2 + (YY - ey_) ** 2
            gl = np.exp(-r2 / (2 * 70.0 ** 2)) * heal * (0.55 + 0.45 * math.exp(-max(t - t_sembuh - 0.6, 0) / 0.5))
            out = out + gl[..., None] * np.array(GOLD, np.float32) * 0.55
        frames.append(to_img(out))
    return frames


# ---------- silhouettes ----------
# poses in body heights: (u, v), u to the right of the figure's centre line, v up from the ground; limbs are point lists with a
# width at each point. "R" limbs are on the viewer's left. The child and the teenager stand on the right leg (viewer's left);
# the left leg (viewer's right) ends a third of the way above the ankle, and a wooden stick takes the weight on that side.
CHILD = {"head": (0.0, 0.905), "head_r": 0.088, "neck": [(0.0, 0.8), (0.0, 0.85)], "neck_w": 0.05,
         "torso": [(-0.04, 0.835), (-0.117, 0.802), (-0.128, 0.766), (-0.116, 0.7), (-0.092, 0.612), (-0.098, 0.532),
                   (-0.06, 0.48), (0.06, 0.48), (0.098, 0.532), (0.092, 0.612), (0.116, 0.7), (0.128, 0.766), (0.117, 0.802),
                   (0.04, 0.835)],
         "wrap": [(-0.103, 0.565), (-0.118, 0.402), (-0.06, 0.39), (0.0, 0.405), (0.06, 0.39), (0.118, 0.402), (0.103, 0.565)],
         "legR": [(-0.05, 0.49), (-0.054, 0.266), (-0.056, 0.17), (-0.058, 0.04)], "legR_w": [0.08, 0.052, 0.056, 0.032],
         "footR": [(-0.068, 0.018), 0.05, 0.019],
         "legL": [(0.05, 0.49), (0.076, 0.272), (0.084, 0.142)], "legL_w": [0.08, 0.052, 0.046],
         "armR": [(-0.112, 0.78), (-0.15, 0.62), (-0.147, 0.475)], "armR_w": [0.05, 0.036, 0.03],
         "handR": [(-0.147, 0.458), 0.024],
         "armL": [(0.112, 0.78), (0.176, 0.655), (0.205, 0.58)], "armL_w": [0.05, 0.036, 0.03],
         "handL": [(0.208, 0.572), 0.025],
         "stick": [(0.214, 0.77), (0.268, 0.0)], "stick_w": 0.025,
         "hair": [(-0.5, 0.72, 0.42), (0.1, 0.9, 0.45), (0.6, 0.7, 0.4), (-0.85, 0.3, 0.3), (0.85, 0.32, 0.3)]}
TEEN = {"head": (0.0, 0.928), "head_r": 0.071, "neck": [(0.0, 0.815), (0.0, 0.875)], "neck_w": 0.047,
        "torso": [(-0.043, 0.85), (-0.127, 0.818), (-0.139, 0.78), (-0.126, 0.712), (-0.095, 0.62), (-0.1, 0.54),
                  (-0.062, 0.488), (0.062, 0.488), (0.1, 0.54), (0.095, 0.62), (0.126, 0.712), (0.139, 0.78), (0.127, 0.818),
                  (0.043, 0.85)],
        "wrap": [(-0.106, 0.575), (-0.121, 0.408), (-0.062, 0.396), (0.0, 0.41), (0.062, 0.396), (0.121, 0.408), (0.106, 0.575)],
        "legR": [(-0.052, 0.5), (-0.056, 0.27), (-0.058, 0.172), (-0.06, 0.038)], "legR_w": [0.078, 0.048, 0.054, 0.03],
        "footR": [(-0.07, 0.017), 0.048, 0.018],
        "legL": [(0.052, 0.5), (0.078, 0.278), (0.086, 0.144)], "legL_w": [0.078, 0.048, 0.044],
        "armR": [(-0.12, 0.8), (-0.157, 0.632), (-0.151, 0.48)], "armR_w": [0.048, 0.034, 0.028],
        "handR": [(-0.151, 0.463), 0.023],
        "armL": [(0.12, 0.8), (0.184, 0.67), (0.212, 0.592)], "armL_w": [0.048, 0.034, 0.028],
        "handL": [(0.215, 0.584), 0.024],
        "stick": [(0.222, 0.788), (0.276, 0.0)], "stick_w": 0.023,
        "hair": [(-0.5, 0.72, 0.42), (0.1, 0.9, 0.45), (0.6, 0.7, 0.4), (-0.85, 0.3, 0.3), (0.85, 0.32, 0.3)]}
ADULT = {"head": (0.0, 0.935), "head_r": 0.066, "neck": [(0.0, 0.83), (0.0, 0.885)], "neck_w": 0.05,
         "torso": [(-0.045, 0.865), (-0.135, 0.832), (-0.149, 0.79), (-0.135, 0.72), (-0.1, 0.626), (-0.106, 0.546),
                   (-0.065, 0.496), (0.065, 0.496), (0.106, 0.546), (0.1, 0.626), (0.135, 0.72), (0.149, 0.79), (0.135, 0.832),
                   (0.045, 0.865)],
         "wrap": [(-0.11, 0.582), (-0.126, 0.412), (-0.06, 0.4), (0.0, 0.415), (0.06, 0.4), (0.126, 0.412), (0.11, 0.582)],
         "legR": [(-0.056, 0.505), (-0.068, 0.276), (-0.071, 0.18), (-0.075, 0.038)], "legR_w": [0.086, 0.05, 0.056, 0.031],
         "footR": [(-0.089, 0.017), 0.05, 0.018],
         "legL": [(0.056, 0.505), (0.063, 0.276), (0.065, 0.18), (0.067, 0.038)], "legL_w": [0.086, 0.05, 0.056, 0.031],
         "footL": [(0.081, 0.017), 0.05, 0.018],
         "armR": [(-0.13, 0.812), (-0.168, 0.646), (-0.161, 0.49)], "armR_w": [0.053, 0.038, 0.03],
         "handR": [(-0.161, 0.472), 0.024],
         "armL": [(0.13, 0.812), (0.166, 0.646), (0.154, 0.49)], "armL_w": [0.053, 0.038, 0.03],
         "handL": [(0.154, 0.472), 0.024],
         "hair": [(-0.45, 0.75, 0.38), (0.15, 0.88, 0.4), (0.6, 0.68, 0.34)]}


def lerp_pose(a, b, u):
    def mix(x, y):
        if isinstance(x, (int, float)):
            return x + (y - x) * u
        return [mix(p, q) for p, q in zip(x, y)] if isinstance(x, list) else tuple(mix(p, q) for p, q in zip(x, y))
    return {k: mix(a[k], b[k]) for k in a if k in b}


def draw_figure(d, pose, x0, ground, h, flip=False):
    """a silhouette on a 2x 'L' layer"""
    f = -1 if flip else 1

    def P(p):
        return ((x0 + f * p[0] * h) * S, (ground - p[1] * h) * S)

    def limb(pts, ws):
        q = [P(p) for p in pts]
        for (a, b), w0, w1 in zip(zip(q, q[1:]), ws, ws[1:]):  # a tapered segment: a quad between two discs
            r0, r1 = w0 * h * S / 2, w1 * h * S / 2
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            d.polygon([(a[0] + nx * r0, a[1] + ny * r0), (b[0] + nx * r1, b[1] + ny * r1),
                       (b[0] - nx * r1, b[1] - ny * r1), (a[0] - nx * r0, a[1] - ny * r0)], fill=255)
            for (x, y), r in ((a, r0), (b, r1)):
                d.ellipse([x - r, y - r, x + r, y + r], fill=255)

    def ell(c, rx, ry):
        x, y = P(c)
        d.ellipse([x - rx * h * S, y - ry * h * S, x + rx * h * S, y + ry * h * S], fill=255)
    d.polygon([P(p) for p in chaikin(pose["torso"], 2)], fill=255)
    d.polygon([P(p) for p in chaikin(pose["wrap"], 1)], fill=255)
    limb(pose["neck"], [pose["neck_w"]] * 2)
    hx, hy = pose["head"]
    r = pose["head_r"]
    ell((hx, hy), r * 0.9, r)
    for dx, dy, rr in pose.get("hair", []):
        ell((hx + dx * r, hy + dy * r * 0.8), rr * r, rr * r * 0.9)
    if "long_hair" in pose:  # hair down to the shoulders
        d.polygon([P((hx + x * r, hy + y * r)) for x, y in chaikin([(-0.95, 0.2), (-1.1, -0.9), (-0.7, -1.45), (0.7, -1.45),
                                                                     (1.1, -0.9), (0.95, 0.2), (0.0, 0.9)], 2)], fill=255)
    limb(pose["legR"], pose["legR_w"])
    fr = pose["footR"]
    ell(fr[0], fr[1], fr[2])
    limb(pose["legL"], pose["legL_w"])
    if "footL" in pose:
        fl = pose["footL"]
        ell(fl[0], fl[1], fl[2])
    for arm, hand in (("armR", "handR"), ("armL", "handL")):
        limb(pose[arm], pose[arm + "_w"])
        ell(pose[hand][0], pose[hand][1] * 0.85, pose[hand][1] * 1.25)
    if "stick" in pose:
        (sx0, sy0), (sx1, sy1) = pose["stick"]
        limb([(sx0, sy0), (sx1, sy1)], [pose["stick_w"], pose["stick_w"] * 0.85])
        ell((sx0 - 0.002, sy0 + 0.004), pose["stick_w"] * 0.8, pose["stick_w"] * 0.7)
    if "bowl" in pose:  # a half-shell bowl held out in the hand
        (bx, by), bw = pose["bowl"]
        x, y = P((bx, by))
        R = bw * h * S
        d.chord([x - R, y - 0.75 * R, x + R, y + 0.75 * R], 0, 180, fill=255)


def ledge_top(x):
    return 1172 + 9 * math.sin(x / 140 + 0.7) + 5 * math.sin(x / 47 + 2.0) + 0.0042 * (x - 560) ** 2 / 10


def ledge():
    """the dark rock in the foreground the figures stand on: alpha"""
    m = Image.new("L", (W * S, H * S), 0)
    top = [(x * S, ledge_top(x) * S) for x in range(-10, W + 11, 6)]
    ImageDraw.Draw(m).polygon(top + [((W + 10) * S, H * S), (-10 * S, H * S)], fill=255)
    return mask_of(m)


def light_up(bg, m, beam_rim=1.0, fire_rim=0.0, halo=1.0, fill=(9, 9, 11), alpha=1.0):
    """composite a silhouette mask over the background, with a thin light rim (beam from above, fire from below)"""
    up = np.clip(m - shift(m, 0, 4), 0, 1)       # edges facing up
    side = np.clip(m - shift(m, 3, 0), 0, 1) + np.clip(m - shift(m, -3, 0), 0, 1)
    down_ = np.clip(m - shift(m, 0, -4), 0, 1)   # edges facing down
    lum = blur(bg.mean(2), 18) / 255
    rim = blur(up * 0.95 + side * 0.55, 0.8) * beam_rim * np.clip(lum * 1.8, 0.15, 1)
    frim = blur(down_ * 0.6 + side * 0.4, 0.8) * fire_rim
    hal = np.clip(blur(m, 9) - m, 0, 1) * halo * np.clip(lum * 1.6, 0, 1)
    out = bg + (hal * 60 * alpha)[..., None]
    ma = (m * alpha)[..., None]
    col = np.array(fill, np.float32) + rim[..., None] * np.array([255, 244, 222], np.float32) * 0.9 \
        + frim[..., None] * np.array([255, 150, 60], np.float32)
    return out * (1 - ma) + col * ma


def dust(t, seed=3, n=70, region=(380, 900, 250, 1150)):
    """motes drifting in the beam: an additive layer (0-1), to be weighted by how lit the background is"""
    rng = np.random.default_rng(seed)
    lay = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(lay)
    x0, x1, y0, y1 = region
    for k in range(n):
        x = rng.uniform(x0, x1) + 30 * math.sin(0.4 * t + k) + rng.uniform(-6, 6) * t
        y = rng.uniform(y0, y1) - rng.uniform(8, 25) * t
        r = rng.uniform(1.0, 2.6)
        a = int(255 * (0.4 + 0.6 * (0.5 + 0.5 * math.sin(2.4 * t + k * 1.7))))
        d.ellipse([x - r, y - r, x + r, y + r], fill=a)
    return np.asarray(lay.filter(ImageFilter.GaussianBlur(0.9)), np.float32) / 255


CAVE_SCENE = None


def cave_scene():
    """the cave moved down so the beam falls behind the figures, and a dark ledge for them to stand on: (rgb, ledge alpha, lit)"""
    global CAVE_SCENE
    if CAVE_SCENE is None:
        bg = cave(260)
        lm = ledge()
        rim = np.clip(lm - shift(lm, 0, 3), 0, 1) * np.exp(-((XX - 640) ** 2) / (2 * 300.0 ** 2))
        out = bg * (1 - lm[..., None]) + np.array([7, 7, 8], np.float32) * lm[..., None]
        out = out + blur(rim, 1.0)[..., None] * np.array([150, 170, 90], np.float32)
        CAVE_SCENE = (out, lm, np.clip(blur(bg.mean(2), 6) / 255 * 1.6, 0, 1))
    return CAVE_SCENE


CHILD_X, CHILD_H, TEEN_H = 600, 450, 500


def skema_anak(times=None):
    base, lm, lit = cave_scene()
    t_in, t_sel = 0.0, 2.67  # "selamat" at 2,67
    g = ledge_top(CHILD_X)
    lay = Image.new("L", (W * S, H * S), 0)
    draw_figure(ImageDraw.Draw(lay), CHILD, CHILD_X, g + 2, CHILD_H)
    m = mask_of(lay)
    frames = []
    for i in range(N["anak"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        warm = ramp(t, t_sel - 0.08, t_sel + 0.35)
        bg = base.copy()
        if warm > 0:  # a warm light swells behind the child
            r2 = (XX - CHILD_X) ** 2 + (YY - (g - 0.6 * CHILD_H)) ** 2
            gl = (np.exp(-r2 / (2 * 190.0 ** 2)) * 0.62 + np.exp(-r2 / (2 * 520.0 ** 2)) * 0.26) * warm
            gl *= (1 + 0.25 * math.exp(-max(t - t_sel - 0.35, 0) / 0.25)) * (1 - 0.8 * lm)
            bg = bg * (1 + 0.18 * warm) + gl[..., None] * np.array(GOLD, np.float32)
        bg = bg + (dust(t) * lit)[..., None] * np.array([255, 245, 225], np.float32) * 0.8
        out = light_up(bg, m, beam_rim=1.0 + 0.6 * warm, alpha=ramp(t, t_in, t_in + 0.25))
        frames.append(to_img(out))
    return frames


def skema_hidup(times=None):
    base, lm, lit = cave_scene()
    t_grow0, t_grow1, t_care = 0.2, 2.0, 2.68  # "hidup" 0,24, "dirawat" 2,68
    fire = (590, 1420)  # off screen in front of the ledge: only its glow and sparks show
    g = ledge_top(CHILD_X)
    # the adults: x, height, facing left, opacity, and what they do
    left = dict(ADULT)
    right = dict(ADULT, armL=[(0.13, 0.812), (0.205, 0.7), (0.285, 0.672)], handL=[(0.292, 0.674), 0.024],
                 bowl=[(0.312, 0.655), 0.055])  # facing the teenager, holding out a bowl
    back = dict(ADULT, long_hair=True, hair=[], head_r=0.064)
    adults = [(205, 420, False, (40, 32, 27), back), (372, 476, False, (10, 9, 9), left), (850, 470, True, (10, 9, 9), right)]
    frames = []
    for i in range(N["hidup"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        u = ramp(t, t_grow0, t_grow1)
        pose = lerp_pose(CHILD, TEEN, u)
        h = CHILD_H + (TEEN_H - CHILD_H) * u
        fl = 0.85 + 0.1 * math.sin(2 * math.pi * 3.1 * t) + 0.05 * math.sin(2 * math.pi * 7.3 * t + 1)
        r2 = (XX - fire[0]) ** 2 + (YY - fire[1]) ** 2
        fg = (np.exp(-r2 / (2 * 260.0 ** 2)) * 0.8 + np.exp(-r2 / (2 * 700.0 ** 2)) * 0.32) * fl * (1 - 0.82 * lm)
        out = base + fg[..., None] * np.array([255, 128, 40], np.float32) * 0.8
        out = out + (dust(t, seed=5, n=40, region=(300, 860, 700, 1180)) * (1 - lm))[..., None] * np.array([255, 170, 80], np.float32)
        care = ramp(t, t_care - 0.05, t_care + 0.4)
        if care > 0:
            for x, ah, flip, fill, p in adults:
                p = dict(p)
                if x == 372:  # reaches for the teenager's shoulder
                    sx, sy = CHILD_X + pose["armR"][0][0] * h, g - pose["armR"][0][1] * h
                    hu, hv = (sx - x) / ah, (ledge_top(x) - sy) / ah
                    p["armL"] = [(0.13, 0.812), ((0.13 + hu) / 2 + 0.02, (0.812 + hv) / 2 - 0.07), (hu - 0.02, hv + 0.005)]
                    p["handL"] = [(hu - 0.012, hv + 0.004), 0.024]
                lay = Image.new("L", (W * S, H * S), 0)
                draw_figure(ImageDraw.Draw(lay), p, x, ledge_top(x) + 2, ah, flip=flip)
                out = light_up(out, mask_of(lay), beam_rim=0.8, fire_rim=0.9, alpha=care, fill=fill)  # the one at the back hazier
        lay = Image.new("L", (W * S, H * S), 0)
        draw_figure(ImageDraw.Draw(lay), pose, CHILD_X, g + 2, h)
        out = light_up(out, mask_of(lay), beam_rim=1.0, fire_rim=0.9)
        rng = np.random.default_rng(9)  # sparks rising from the fire
        sp = Image.new("L", (W, H), 0)
        dsp = ImageDraw.Draw(sp)
        for k in range(26):
            ph = (t * rng.uniform(0.25, 0.5) + rng.uniform(0, 1)) % 1
            x = fire[0] + rng.uniform(-200, 200) + 40 * math.sin(6 * ph + k)
            y = 1300 - 600 * ph
            r = rng.uniform(1.2, 2.4)
            dsp.ellipse([x - r, y - r, x + r, y + r], fill=int(255 * (1 - ph) ** 1.5))
        spa = np.asarray(sp.filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255
        out = out + spa[..., None] * np.array([255, 170, 70], np.float32)
        frames.append(to_img(out))
    return frames


# ---------- skema_rekor ----------
def outline_icon(rings, box, fill, edge):
    """rings (lon, lat) fitted into a box (cx, cy, size): RGBA at 1x"""
    cx, cy, size = box
    lo = [p[0] for r in rings for p in r]
    la = [p[1] for r in rings for p in r]
    k = math.cos(math.radians((min(la) + max(la)) / 2))
    sx = size / max((max(lo) - min(lo)) * k, max(la) - min(la))
    mx, my = (min(lo) + max(lo)) / 2, (min(la) + max(la)) / 2
    g = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for r in rings:
        d.polygon([((cx + (x - mx) * k * sx) * S, (cy - (y - my) * sx) * S) for x, y in r], fill=fill, outline=edge, width=3 * S)
    return g.resize((W, H), Image.LANCZOS)


def france_rings():
    for f in json.load(open(os.path.join(GEO, "ne_50m_admin_0_countries.geojson")))["features"]:
        if f["properties"].get("ADMIN") == "France":
            g = f["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            return [p[0] for p in polys if -6 < sum(q[0] for q in p[0]) / len(p[0]) < 10 and 41 < sum(q[1] for q in p[0]) / len(p[0]) < 52]
    raise SystemExit("France not found")


def skema_rekor(times=None):
    bg = np.asarray(navy(540, 900, xs=range(0, W + 1, 135), ys=range(-45, H + 1, 135)).convert("RGB"), np.float32)
    borneo = [r for r in land_rings(105, -6, 122, 9) if is_borneo(r)]
    ico_k = outline_icon(borneo, (160, 655, 150), YELLOW + (255,), (255, 255, 255, 255))
    ico_f = outline_icon(france_rings(), (160, 870, 132), (235, 235, 235, 255), (255, 255, 255, 255))
    X0, X1 = 270, 965
    xf = X0 + (X1 - X0) * 7 / 31
    # the two bars and the bracket: the bar labels stay above the watermark band (y 935-985), the bracket below it
    YK, YF, YB = (610, 700), (825, 915), 1010
    lab_k = text_sprite([("KALIMANTAN", 50, YELLOW, True)])
    lab_f = text_sprite([("PRANCIS", 50, WHITE, True)])
    gap = text_sprite([("+24.000 TAHUN", 66, YELLOW, True), ("lebih tua", 42, WHITE, True)], gap=12)
    t_k, t_f0, t_f1, t_gap = 0.05, 1.3, 2.3, 2.66
    font = ImageFont.truetype(XB, 40 * S)
    frames = []
    for i in range(N["rekor"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = to_img(bg).convert("RGBA")
        ak = ramp(t, t_k, t_k + 0.25)
        af = ramp(t, 1.05, 1.3)
        for ico, a in ((ico_k, ak), (ico_f, af)):
            if a > 0:
                c = ico.copy()
                c.putalpha(c.getchannel("A").point(lambda v: int(v * a)))
                im.alpha_composite(c)
        put_left(im, lab_k, X0, YK[0] - 36, a=ak)
        put_left(im, lab_f, X0, YF[0] - 36, a=af)
        ov = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        gk = ramp(t, t_k + 0.1, t_k + 0.75)
        xk = X0 + (X1 - X0) * gk
        if gk > 0:
            d.rounded_rectangle([X0 * S, YK[0] * S, max(X0 + 14, xk) * S, YK[1] * S], radius=12 * S, fill=YELLOW + (255,))
            if gk > 0.05:
                # counter: navy inside the bar, yellow where it still runs past the growing bar's end
                num = f"{round(31 * gk):d}.000 tahun lalu"
                tx = max(X0 * S + 18 * S, xk * S - font.getlength(num) - 22 * S)
                ty = (YK[0] + YK[1]) / 2 * S
                tl, tyl = Image.new("RGBA", ov.size, (0, 0, 0, 0)), Image.new("RGBA", ov.size, (0, 0, 0, 0))
                ImageDraw.Draw(tl).text((tx, ty), num, font=font, fill=(10, 24, 50, 255), anchor="lm")
                ImageDraw.Draw(tyl).text((tx, ty), num, font=font, fill=YELLOW + (255,), anchor="lm")
                cut = int(xk * S)
                tl.paste(tyl.crop((cut, 0, ov.width, ov.height)), (cut, 0))
                ov.alpha_composite(tl)
        gf = ramp(t, t_f0, t_f1)
        xff = X0 + (xf - X0) * gf
        if af > 0:
            d.rounded_rectangle([X0 * S, YF[0] * S, max(X0 + 14, xff) * S, YF[1] * S], radius=12 * S, fill=(236, 236, 236, int(255 * af)))
            if gf > 0.02:
                n7 = round(7 * gf)
                d.text(((xff + 20) * S, (YF[0] + YF[1]) / 2 * S), f"{n7:d}.000 tahun lalu" if n7 else "0", font=font,
                       fill=(255, 255, 255, 255), anchor="lm")
        ag = ramp(t, t_gap, t_gap + 0.22)
        if ag > 0:
            for x, ytop in ((xf, YF[1]), (X1, YK[1])):  # dashed guides down from both bar ends
                for yy in range(int(ytop) + 8, YB, 20):
                    d.line([(x * S, yy * S), (x * S, min(YB, yy + 11) * S)], fill=YELLOW + (int(220 * ag),), width=4 * S)
            L = (X1 - xf) * ramp(t, t_gap, t_gap + 0.3)
            mid = (xf + X1) / 2
            d.line([((mid - L / 2) * S, YB * S), ((mid + L / 2) * S, YB * S)], fill=YELLOW + (255,), width=6 * S)
            for x, sgn in ((mid - L / 2, 1), (mid + L / 2, -1)):
                d.polygon([(x * S, YB * S), ((x + sgn * 26) * S, (YB - 14) * S), ((x + sgn * 26) * S, (YB + 14) * S)], fill=YELLOW + (255,))
        im.alpha_composite(ov.resize((W, H), Image.LANCZOS))
        if ag > 0:
            put1(im, gap, (xf + X1) / 2, YB + 74, a=ag, scale=0.8 + 0.2 * pop(t, t_gap, 0.3))
        frames.append(im.convert("RGB"))
    return frames


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != GEO]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or list(N)
    for name, fn in [("peta", skema_peta), ("kerangka", skema_kerangka), ("tulang", skema_tulang), ("anak", skema_anak),
                     ("rekor", skema_rekor), ("hidup", skema_hidup)]:
        if name in todo:
            fr = fn(times)
            if times is not None:
                sheet(fr, name, out)
            else:
                encode(fr, f"clips/skema_{name}.mp4")
