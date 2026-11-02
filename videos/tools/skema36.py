"""Framing and animations for Titik Heran #36 (run in the episode work dir after
`dl.py i:3886500 i:3832301 i:2458500 i:1281266 i:1344300 i:922764`; writes img/3832301v.jpg, img/2458500v.jpg,
clips/skema_lemari.mp4, clips/skema_kalung.mp4 and clips/skema_tumbuh.mp4).
usage: python3 skema36.py [stills|lemari|kalung|tumbuh ...] [--sheet out.jpg t1,t2,...]   (--sheet saves those frames)
stills: the glass bottle (Pixabay 3832301, a museum piece, not from the find) set lower in its case so the title clears it, and the
Pompeii arch (2458500) set under the CTA title; the rows the photos do not reach continue their edge rows, smoothed.
skema_lemari: an old cupboard door with its key (3886500, a stand-in, not the Pompeii cupboard) framed on the key; on "isinya" the
seam beside the lock cracks open from the key outward and leaks gold light (added, not painted: a hot core, a glow, a bloom and a
warm spill over the key).
skema_kalung: the reconstruction. One striped cloth pouch (cut out of 1281266, a modern lavender sachet) in worn sepia on a dark
ground, its tied end up; on "kalung" 24 small amulets fly out of it one by one onto a cord: hands, feet, pine cones, grapes, Bes and
Mercury in bone, glass, pottery and crystal, the kinds and materials the Pompeii report lists. A small counter runs to 24.
The shapes are drawn to show the idea, not copied from the find (its photos are not free to use).
skema_tumbuh: the Roman child statue (1344300, Louvre) framed as in its own shot dissolves into the Pompeii fresco (922764) framed as
in the "pemiliknya" shot, and the finished necklace fades in, glowing, at the painted woman's neck.
Event times are seconds from the start of each clip, read off `render.py 36 plan`: skema_lemari starts at 0 ("isinya" 3,36),
skema_kalung at 15,73 ("kalung" 1,60, "dua" 2,00, "jimat" 2,72), skema_tumbuh at 20,67 ("jimat" 1,17, "pemiliknya" 2,01,
"disimpan" 3,28).
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode
from skema35 import blur, sepia, paste_center, sheet

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
N = {"lemari": 164, "kalung": 120, "tumbuh": 156}  # frames: each clip runs ~0,3 s past its shot
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


# ---------- stills ----------
def edge_fill(rows, n, up=True):
    """n rows continuing a photo edge: its edge rows averaged, smoothed sideways more the further they reach, darkened a little"""
    edge = rows.mean(0)  # (W, 3)
    out = np.zeros((n, W, 3), np.float32)
    for k in range(n):
        d = (k + 1) / n
        r = max(1, int(4 + 60 * d))
        c = np.cumsum(np.pad(edge, ((r + 1, r), (0, 0)), mode="edge"), 0)
        out[k] = (c[2 * r + 1:] - c[:-2 * r - 1]) / (2 * r + 1) * (1 - 0.12 * d)
    return out[::-1] if up else out


def reframe(src, s, x0, y0, out):
    """the photo scaled by s, its scaled pixel (x0, 0) at the frame's left edge and its top at frame row y0; edges continued"""
    im = Image.open(src).convert("RGB")
    big = np.asarray(im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS), np.float32)[:, x0:x0 + W]
    f = np.zeros((H, W, 3), np.float32)
    top, bot = max(0, y0), min(H, y0 + big.shape[0])
    f[top:bot] = big[top - y0:bot - y0]
    if top > 0:
        f[:top] = edge_fill(big[:6], top, up=True)
        f[max(0, top - 10):top + 10] = blur(f[max(0, top - 30):top + 30], 2)[top - 10 - max(0, top - 30):][:20]
    if bot < H:
        f[bot:] = edge_fill(big[-6:], H - bot, up=False)
        f[bot - 10:bot + 10] = blur(f[bot - 30:min(H, bot + 30)], 2)[20:40]
    Image.fromarray(f.clip(0, 255).astype(np.uint8)).save(out, quality=95)
    print(out)


def stills():
    reframe("img/3832301.jpg", 1.25, 41, 256, "img/3832301v.jpg")  # the bottle's neck lands at y ~680, under the title
    reframe("img/2458500.jpg", 1.5, 100, 262, "img/2458500v.jpg")  # the arch's top lands at y ~790, under the CTA


# ---------- skema_lemari ----------
LEM = (1.875, 853)  # scale of 3886500, and the crop's left edge in the scaled photo (the key on the left, the seam on the right)
SEAM = [(932, 0), (930, 480), (928, 960), (926, 1440), (924, 1920)]
KEY_Y = 919  # the key's height: the crack opens from here


def lemari_base():
    s, x0 = LEM
    im = Image.open("img/3886500.jpg").convert("RGB")
    big = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return np.asarray(big.crop((x0, 0, x0 + W, H)), np.float32)


def seam_x(y):
    return float(np.interp(y, [p[1] for p in SEAM], [p[0] for p in SEAM]))


def skema_lemari(times=None):
    base = lemari_base() * 0.93
    t_open, t_run = 3.36, 0.32  # "isinya", and how long the crack takes to run up and down

    def light(y0, y1, width, bl):
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).line([(seam_x(y), y) for y in np.linspace(y0, y1, 12)], fill=255, width=width)
        return np.asarray(m.filter(ImageFilter.GaussianBlur(bl)), np.float32)[..., None] / 255
    passes = [(3, 1.0, (255, 250, 232), 1.0), (14, 6, (255, 204, 120), 0.85), (90, 36, (255, 160, 70), 0.55)]
    full = [light(0, H, w, b) for w, b, *_ in passes]
    left = np.clip((seam_x(KEY_Y) - XX) / 1.0, 0, 1) * np.exp(-np.clip(seam_x(KEY_Y) - XX, 0, None) / 300)  # spill onto the key side
    frames = []
    for i in range(N["lemari"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        u = ramp(t, t_open, t_open + t_run)
        if u <= 0:
            frames.append(Image.fromarray(base.clip(0, 255).astype(np.uint8)))
            continue
        L = 1100 * u
        y0, y1 = max(0, KEY_Y - L), min(H, KEY_Y + L)
        masks = full if u >= 1 else [light(y0, y1, w, b) for w, b, *_ in passes]
        flare = 1 + 0.6 * math.exp(-max(t - t_open - t_run, 0) / 0.15) * (u >= 1)
        k = (0.9 + 0.07 * math.sin(2 * math.pi * 1.3 * (t - t_open)) + 0.03 * math.sin(2 * math.pi * 3.1 * t)) * flare
        out = base.copy()
        for m, (*_, col, a) in zip(masks, passes):
            out += m * np.array(col, np.float32) * a * k
        vert = np.clip(1 - np.abs(YY - KEY_Y) / max(L, 1), 0, 1) ** 0.5
        out += (left * vert * 0.30 * k * u)[..., None] * np.array([255, 170, 85], np.float32)
        if u < 1:  # bright points running ahead at both ends of the crack
            for yy in (y0, y1):
                r2 = (XX - seam_x(yy)) ** 2 + (YY - yy) ** 2
                out += (np.exp(-r2 / (2 * 10.0 ** 2)) + 0.5 * np.exp(-r2 / (2 * 40.0 ** 2)))[..., None] * np.array([255, 236, 200], np.float32)
        frames.append(Image.fromarray(out.clip(0, 255).astype(np.uint8)))
    return frames


# ---------- the amulets ----------
BONE, BONE_D = (232, 214, 174), (128, 98, 60)
MATERIALS = {"tulang": (BONE, BONE_D, False), "kaca biru": ((84, 142, 210), (30, 62, 120), True),
             "kaca hijau": ((112, 178, 124), (40, 92, 52), True), "kristal": ((218, 234, 244), (110, 132, 150), True),
             "gerabah": ((196, 112, 70), (102, 50, 26), False), "faiens": ((72, 172, 160), (24, 88, 80), True)}


def amulet(kind, mat, size=64):
    """one small hanging amulet as an RGBA sprite at 2x, its hanging loop at the top centre; size is its height at 1x"""
    fill, edge, shiny = MATERIALS[mat]
    k = size * S / 64  # drawn on a 64-unit grid
    im = Image.new("RGBA", (round(56 * k), round(70 * k)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    P = lambda pts: [(x * k, y * k) for x, y in pts]
    E = lambda x0, y0, x1, y1: [x0 * k, y0 * k, x1 * k, y1 * k]
    ow = max(1, round(1.6 * k))
    d.ellipse(E(23, 0, 33, 10), outline=edge + (255,), width=round(2.2 * k))  # the loop
    if kind == "tangan":  # an open hand, fingers down
        d.rounded_rectangle(E(14, 10, 42, 40), radius=8 * k, fill=fill, outline=edge, width=ow)
        for x in (15, 22, 29, 36):
            d.rounded_rectangle(E(x, 34, x + 6, 58 if x in (22, 29) else 54), radius=3 * k, fill=fill, outline=edge, width=ow)
        d.rounded_rectangle(E(38, 18, 46, 38), radius=4 * k, fill=fill, outline=edge, width=ow)
        d.rounded_rectangle(E(16, 26, 40, 40), radius=6 * k, fill=fill)
    elif kind == "kaki":  # a foot seen from below, toes down
        d.ellipse(E(17, 10, 39, 52), fill=fill, outline=edge, width=ow)
        for x, y, r in [(18, 51, 3.2), (24, 55, 3.4), (30, 56, 3.6), (36, 53, 3.4), (41, 48, 3.2)]:
            d.ellipse(E(x - r, y - r, x + r, y + r), fill=fill, outline=edge, width=ow)
    elif kind == "pinus":  # a pine cone with its scales
        d.ellipse(E(16, 10, 40, 60), fill=fill, outline=edge, width=ow)
        for j in range(-3, 5):
            d.line(P([(16 + 6 * j, 12), (40 + 6 * j, 58)]), fill=edge + (160,), width=ow)
            d.line(P([(40 - 6 * j, 12), (16 - 6 * j, 58)]), fill=edge + (160,), width=ow)
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).ellipse(E(16, 10, 40, 60), fill=255)
        bg = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(bg).ellipse(E(23, 0, 33, 10), outline=edge + (255,), width=round(2.2 * k))
        bg.paste(im, (0, 0), mask)
        ImageDraw.Draw(bg).ellipse(E(16, 10, 40, 60), outline=edge, width=ow)
        im, d = bg, ImageDraw.Draw(bg)
    elif kind == "anggur":  # a bunch of grapes
        d.line(P([(28, 9), (28, 16)]), fill=edge, width=round(2.4 * k))
        for x, y in [(18, 22), (28, 21), (38, 22), (23, 31), (33, 31), (18, 40), (28, 40), (38, 40), (23, 49), (33, 49), (28, 58)]:
            d.ellipse(E(x - 5.5, y - 5.5, x + 5.5, y + 5.5), fill=fill, outline=edge, width=ow)
    elif kind == "bes":  # Bes: a squat god with a feather crown, a broad face and a beard, bowed legs
        for x in (20, 25, 30, 35):
            d.rounded_rectangle(E(x, 9, x + 4, 20), radius=2 * k, fill=fill, outline=edge, width=ow)
        d.ellipse(E(15, 16, 41, 38), fill=fill, outline=edge, width=ow)
        d.polygon(P([(19, 32), (37, 32), (28, 44)]), fill=fill, outline=edge)
        d.rounded_rectangle(E(19, 40, 37, 54), radius=4 * k, fill=fill, outline=edge, width=ow)
        d.line(P([(21, 53), (18, 60), (23, 62)]), fill=edge, width=round(3 * k))
        d.line(P([(35, 53), (38, 60), (33, 62)]), fill=edge, width=round(3 * k))
        for x in (23, 33):
            d.ellipse(E(x - 2, 24, x + 2, 28), fill=edge)
    elif kind == "merkurius":  # Mercury: a head in the winged hat (petasos)
        d.ellipse(E(17, 22, 39, 50), fill=fill, outline=edge, width=ow)
        d.chord(E(14, 12, 42, 34), 180, 360, fill=fill, outline=edge, width=ow)
        d.line(P([(12, 24), (44, 24)]), fill=edge, width=ow)
        d.polygon(P([(14, 22), (2, 12), (6, 22), (2, 26)]), fill=fill, outline=edge)
        d.polygon(P([(42, 22), (54, 12), (50, 22), (54, 26)]), fill=fill, outline=edge)
        d.ellipse(E(23, 33, 26, 36), fill=edge)
        d.ellipse(E(30, 33, 33, 36), fill=edge)
    if shiny:  # glass and crystal catch the light
        hl = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(hl).ellipse(E(20, 16, 27, 24), fill=(255, 255, 255, 170))
        im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(1.5 * k)))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))  # a soft dark edge, so a pale amulet reads on any ground
    sh.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(3 * k)).point(lambda v: int(v * 0.55)))
    sh.alpha_composite(im)
    return sh


ORDER = [("tangan", "tulang"), ("anggur", "kaca biru"), ("kaki", "gerabah"), ("bes", "faiens"), ("pinus", "tulang"),
         ("merkurius", "kristal"), ("tangan", "kaca hijau"), ("kaki", "tulang"), ("anggur", "kaca hijau"), ("pinus", "gerabah"),
         ("bes", "tulang"), ("merkurius", "kaca biru"), ("tangan", "kristal"), ("kaki", "faiens"), ("anggur", "tulang"),
         ("pinus", "kaca biru"), ("bes", "gerabah"), ("merkurius", "tulang"), ("tangan", "gerabah"), ("kaki", "kaca biru"),
         ("anggur", "kristal"), ("pinus", "faiens"), ("bes", "kaca hijau"), ("merkurius", "gerabah")]
CORD = (96, 984, 700, 300)  # the cord: from x 96 to 984 at y 700, sagging 300 px in the middle


def cord_pts(n=200):
    x0, x1, y, sag = CORD
    xs = np.linspace(x0, x1, n)
    return np.stack([xs, y + sag * (1 - ((xs - (x0 + x1) / 2) / ((x1 - x0) / 2)) ** 2)], 1)


def slots():
    """24 evenly spaced points along the cord, in landing order: from the middle outward, left and right in turn"""
    p = cord_pts(400)
    acc = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    at = [p[np.searchsorted(acc, acc[-1] * (0.07 + 0.86 * j / 23))] for j in range(24)]
    order = sorted(range(24), key=lambda j: (abs(j - 11.5), j))
    return [at[j] for j in order], [order.index(j) for j in range(24)]


# ---------- skema_kalung ----------
# the striped pouch's outline in 1281266, traced inside its edge (the cloth around it is other sachets)
POUCH = [(653, 257), (700, 257), (760, 277), (837, 281), (906, 289), (941, 299), (946, 307), (944, 318), (941, 340), (932, 356),
         (920, 371), (910, 386), (900, 402), (888, 426), (874, 446), (865, 466), (854, 483), (844, 503), (837, 522), (831, 538),
         (825, 558), (818, 580), (810, 602), (800, 632), (792, 662), (782, 690), (771, 714), (757, 740), (741, 762), (726, 780),
         (705, 789), (660, 791), (620, 789), (590, 784), (560, 777), (532, 765), (511, 746), (498, 724), (489, 700), (486, 673),
         (491, 646), (509, 611), (526, 573), (549, 535), (566, 500), (584, 450), (603, 400), (619, 350), (627, 325), (643, 290),
         (650, 270)]


def pouch_sprite():
    """the striped pouch cut out of 1281266, worn sepia, turned so its tied end points up"""
    im = Image.open("img/1281266.jpg").convert("RGB")
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).polygon(POUCH, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(2.5))
    a = np.asarray(im, np.float32)
    a = sepia(a, 0.8)
    a = (a - 128) * 0.85 + 128 - 6  # worn: flatter and a little darker
    rng = np.random.default_rng(36)
    a += rng.normal(0, 6, a.shape[:2])[..., None]
    rgba = np.dstack([a.clip(0, 255), np.asarray(m, np.float32)])
    x0, y0, x1, y1 = 470, 240, 975, 805
    return Image.fromarray(rgba[y0:y1, x0:x1].astype(np.uint8), "RGBA").rotate(180)  # the gathered end now on top


def dark_ground():
    v = (YY / H)[..., None]
    g = np.array([34, 25, 17], np.float32) * (1 - v) + np.array([16, 11, 8], np.float32) * v
    g *= (1 - 0.45 * (((XX - W / 2) / (W / 2)) ** 2 + ((YY - 1150) / (H / 2)) ** 2) / 2)[..., None]
    return g


def necklace_layer(t, landed_at, pts, sprites, glow=0.0):
    """the cord and the amulets that have landed by time t, at 1x"""
    L = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    c = cord_pts()
    d.line([(x * S, y * S) for x, y in c], fill=(176, 136, 78, 255), width=3 * S, joint="curve")
    L = L.resize((W, H), Image.LANCZOS)
    for j, (sp, tl) in enumerate(zip(sprites, landed_at)):
        if t >= tl:
            x, y = pts[j]
            sw = 3.0 * math.exp(-(t - tl) / 0.35) * math.sin(2 * math.pi * 2.2 * (t - tl))  # a small swing after landing
            r = sp.rotate(sw, resample=Image.BICUBIC, center=(sp.width / 2, 0))
            L.alpha_composite(r, (round(x - r.width / 2), round(y - 4)))
    if glow > 0:
        g = L.getchannel("A").filter(ImageFilter.GaussianBlur(14))
        halo = Image.new("RGBA", (W, H), (255, 214, 140, 0))
        halo.putalpha(g.point(lambda v: int(min(255, v * 1.6 * glow))))
        halo.alpha_composite(L)
        L = halo
    return L


def kalung_parts():
    pts, rank = slots()
    sprites = [amulet(k, m, 56).resize((round(56 * 56 / 64), round(70 * 56 / 64)), Image.LANCZOS) for k, m in ORDER]
    return pts, rank, sprites


def skema_kalung(times=None):
    ground = dark_ground()
    psp = pouch_sprite()
    pts, rank, sprites = kalung_parts()
    MOUTH = (540, 1046)
    t_cord, t_first, gap, fly = 1.45, 1.48, 0.04, 0.30
    launch = [t_first + gap * rank[j] for j in range(24)]
    landed = [x + fly for x in launch]
    f_cnt, f_lbl = ImageFont.truetype(XB, 66), ImageFont.truetype(MED, 26)
    frames = []
    for i in range(N["kalung"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        im = Image.fromarray(ground.astype(np.uint8)).convert("RGBA")
        sc_ = 1.05 + 0.05 * t / (N["kalung"] / FPS)  # the pouch pushes in slowly
        sp = psp.resize((round(psp.width * sc_), round(psp.height * sc_)), Image.LANCZOS)
        shadow = Image.new("RGBA", sp.size, (0, 0, 0, 0))
        shadow.putalpha(sp.getchannel("A").filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.6)))
        cy = MOUTH[1] + sp.height / 2 - 10
        paste_center(im, shadow, 556, cy + 18)
        dim = 1 - 0.25 * ramp(t, 2.6, 3.4)
        paste_center(im, sp, 540, cy)
        if dim < 0.99:
            veil = Image.new("RGBA", (W, H), (0, 0, 0, round(255 * (1 - dim))))
            im.alpha_composite(veil)
        mg = ramp(t, 1.25, 1.5) * (1 - 0.5 * ramp(t, 2.8, 3.6))  # the mouth glows as the amulets come out
        if mg > 0:
            r2 = (XX - MOUTH[0]) ** 2 + (YY - MOUTH[1]) ** 2
            glow = (np.exp(-r2 / (2 * 60.0 ** 2)) * 0.9 + np.exp(-r2 / (2 * 170.0 ** 2)) * 0.35) * mg
            a = np.asarray(im.convert("RGB"), np.float32) + glow[..., None] * np.array([255, 200, 120], np.float32)
            im = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
        if t >= t_cord:
            nk = necklace_layer(t, landed, pts, sprites, glow=0.8 * ramp(t, 2.8, 3.4))
            nk.putalpha(nk.getchannel("A").point(lambda v: int(v * ramp(t, t_cord, t_cord + 0.2))))
            im.alpha_composite(nk)
            for j in range(24):  # the amulets in flight: out of the mouth, up over an arc, onto the cord
                if launch[j] <= t < landed[j]:
                    u = (t - launch[j]) / fly
                    e = 1 - (1 - u) ** 2
                    x1, y1 = pts[j]
                    cx, cy2 = (MOUTH[0] + x1) / 2, min(MOUTH[1], y1) - 160
                    x = (1 - e) ** 2 * MOUTH[0] + 2 * (1 - e) * e * cx + e * e * x1
                    y = (1 - e) ** 2 * MOUTH[1] + 2 * (1 - e) * e * cy2 + e * e * y1
                    s_ = 0.35 + 0.65 * e
                    sp_ = sprites[j].resize((max(1, round(sprites[j].width * s_)), max(1, round(sprites[j].height * s_))), Image.LANCZOS)
                    im.alpha_composite(sp_, (round(x - sp_.width / 2), round(y - 4)))
            n = sum(1 for x in landed if t >= x)
            if n:
                d = ImageDraw.Draw(im)
                p = pop(t, max(x for x in landed if t >= x), 0.16)
                fs = ImageFont.truetype(XB, max(8, round(66 * (0.8 + 0.2 * p))))
                d.text((952, 1118), str(n), font=fs, fill=YELLOW + (255,), anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0, 255))
                d.text((952, 1166), "jimat", font=f_lbl, fill=(255, 255, 255, 230), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0, 200))
        frames.append(im.convert("RGB"))
    return frames


# ---------- skema_tumbuh ----------
def cover_pos(src, pos):
    im = Image.open(src).convert("RGB")
    k = max(W / im.width, H / im.height)
    big = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x = round((big.width - W) * pos)
    return np.asarray(big.crop((x, (big.height - H) // 2, x + W, (big.height - H) // 2 + H)), np.float32)


def zoomed(a, z):
    """centre zoom of a float frame by z >= 1"""
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    w, h = W / z, H / z
    return np.asarray(im.resize((W, H), Image.LANCZOS, box=((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2)), np.float32)


def skema_tumbuh(times=None):
    child = cover_pos("img/1344300.jpg", 0.276) * 0.86  # shot 7 ends dim; this carries on from it
    adult = cover_pos("img/922764.jpg", 0.51)
    pts, rank, sprites = kalung_parts()
    big = necklace_layer(99, [0] * 24, pts, sprites, glow=1.0)
    nk = big.resize((round(W * 0.62), round(H * 0.62)), Image.LANCZOS)
    t0, t1 = 2.0, 3.4  # the dissolve, from "pemiliknya" to "disimpan"
    t_nk = 2.5  # the necklace fades in once the painting shows through: on the statue it would sit across the chin
    T = N["tumbuh"] / FPS
    frames = []
    for i in range(N["tumbuh"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        u = ramp(t, t0, t1)
        z = 1.08 + 0.07 * t / T  # shot 7 ended at a 1,08 push: carry on from there
        a = zoomed(child, z) * (1 - u) + zoomed(adult, 1.0 + 0.05 * t / T) * u
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
        na = ramp(t, t_nk, t_nk + 0.8)
        if na > 0:
            breathe = 0.85 + 0.15 * math.sin(2 * math.pi * 0.7 * (t - t_nk))
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            layer.alpha_composite(nk, ((W - nk.width) // 2, round(1105 - 0.62 * 850)))
            layer.putalpha(layer.getchannel("A").point(lambda v: int(v * na * breathe)))
            im.alpha_composite(layer)
        frames.append(im.convert("RGB"))
    return frames


if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or ["stills", "lemari", "kalung", "tumbuh"]
    if "stills" in todo:
        stills()
    for name, fn in [("lemari", skema_lemari), ("kalung", skema_kalung), ("tumbuh", skema_tumbuh)]:
        if name in todo:
            fr = fn(times)
            if times is not None:
                sheet(fr, name, out)
            else:
                encode(fr, f"clips/skema_{name}.mp4")
