"""Schematic animations and image prep for Titik Heran #80 (run in the episode work dir).
prep: img/H5c.jpg (Arif's Higgsfield H5, the marble head with the chipped nose; the shadow of a person on the wall at
  the lower left is painted out with the wall colour of each row), img/H2k.jpg (H2 cropped on the hand on the wrapped
  head and the gold wreath, below the emperor's face: used on "krek"), img/H3c.jpg (H3 cropped past the burning torch:
  a lit torch in a sealed tunnel makes no sense).
lini: timeline on dark parchment: 323 SM Alexander wafat -> 30 SM dikunjungi Augustus -> +-400 M terakhir disebut ->
  red marks for the searches, counter "140+ PENCARIAN GAGAL" (La Brujula Verde: more than 140 official excavations).
penampang: cross-section at one scale (22 px per metre): the park (palms, lawn) on the surface, limestone foundations
  +-10 m down (2016 season), >=36 m long (2017 season), walls around them, a tunnel running north beneath them
  (Egyptian Gazette, Greek City Times, La Brujula Verde, 24-25 Nov 2026).
peta: schematic map of Alexandria (north up): the sea, Qaitbay fort (site of the Pharos) at the west tip of the Eastern
  Harbour, the ancient royal quarter on its south-east shore, a pulsing dot for Taman Shallalat and the pill
  "makam raja-raja Ptolemaios (Sema)?"; the shot tag says "perkiraan".
cover: img/cover80.jpg from H4 (the title sits on H4's own grey band) with a small "ilustrasi" tag.
Event times are seconds from the start of each clip, read off `render.py 80 plan`. Text stays out of the watermark
band (y 935-985), the title zone (y < ~600) and the captions (y >= 1210).
usage: python3 skema80.py [prep|lini|penampang|peta|cover ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, text_sprite
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema74 import backdrop

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
WHITE, RED = (255, 255, 255), (232, 44, 40)
N = {"lini": 78, "penampang": 72, "peta": 50}
# from `render.py 80 plan`: lini = shot 08 ("berabad-abad" 0.04, "dicari" 0.80, "tak" 1.48, "ketemu" 1.63, cut 2.37);
# penampang = shot 10 ("fondasi" 0.04, "raksasa" 0.42, "di" 0.99, "bawah" 1.10, "taman" 1.29, "kota" 1.55, cut 2.20);
# peta = shot 11 ("diduga" 0.04, "makam" 0.57, "raja" 0.87, cut 1.40)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def font(path, size):
    return ImageFont.truetype(path, size * S)


def label(lines):
    return text_sprite(lines, gap=6)


# ---------- prep ----------
def prep():
    a = np.asarray(Image.open("img/H5.jpg").convert("RGB"), np.float32).copy()
    y0, y1, xr = 1700, 2330, 262
    ref = a[y0:y1, xr:xr + 40].mean(1)                      # wall colour of each row, right of the shadow
    xs = np.arange(xr)[None, :, None]
    fill = ref[:, None, :] * (0.88 + 0.12 * xs / xr)        # the wall darkens a little toward the left edge
    w = np.ones((y1 - y0, xr, 1), np.float32)
    f = 40.0
    yy = np.arange(y1 - y0)[:, None, None]
    w *= np.clip(np.minimum(yy, (y1 - y0 - 1) - yy) / f, 0, 1)   # feather top and bottom
    w *= np.clip((xr - 1 - xs) / 24.0, 0, 1)                      # and toward the sampled column
    a[y0:y1, :xr] = a[y0:y1, :xr] * (1 - w) + fill * w
    to_img(a).save("img/H5c.jpg", quality=95)
    Image.open("img/H2.jpg").crop((614, 980, 1478, 2516)).resize((1080, 1920), Image.LANCZOS).save("img/H2k.jpg", quality=95)
    Image.open("img/H3.jpg").crop((430, 380, 1536, 2346)).resize((1080, 1920), Image.LANCZOS).save("img/H3c.jpg", quality=95)
    print("img/H5c.jpg img/H2k.jpg img/H3c.jpg")


# ---------- lini ----------
def x_mark(r=16, col=RED + (255,)):
    sp = Image.new("RGBA", ((2 * r + 8) * S, (2 * r + 8) * S))
    d = ImageDraw.Draw(sp)
    c = (r + 4) * S
    for s in (1, -1):
        d.line([(c - r * S, c - s * r * S), (c + r * S, c + s * r * S)], fill=col, width=6 * S)
    return sp


def skema_lini(times=None):
    bg = backdrop((52, 40, 28), (14, 10, 8), glow=(30, 22, 10), gy=960)
    AX0, AX1, AY = 90, 990, 960
    ms = [  # x, above?, year, text, t
        (170, True, "323 SM", "Alexander wafat", 0.10),
        (400, False, "30 SM", "dikunjungi Augustus", 0.35),
        (640, True, "±400 M", "terakhir disebut", 0.60),
    ]
    sprites = [label([(y, 46, YELLOW, True), (t, 30, WHITE, False)]) for _, _, y, t, _ in ms]
    end = label([("2026", 46, YELLOW, True), ("?", 34, WHITE, True)])
    xm = x_mark()
    marks = [690 + k * 28 for k in range(8)]
    frames = []
    for i in range(N["lini"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        d = ImageDraw.Draw(im)
        u = ease(t / 0.45)
        d.line([(AX0, AY), (AX0 + (AX1 - AX0) * u, AY)], fill=(235, 220, 190), width=6)
        for (x, up, *_ , t0), sp in zip(ms, sprites):
            k = pop(t, t0)
            if k > 0:
                d.ellipse([x - 13, AY - 13, x + 13, AY + 13], fill=YELLOW + (255,))
                put1(im, sp, x, 850 if up else 1075, a=min(1, k), scale=k)
        ke = pop(t, 1.60)
        if ke > 0:
            d.ellipse([930 - 13, AY - 13, 930 + 13, AY + 13], outline=YELLOW + (255,), width=5)
            put1(im, end, 930, 850, a=min(1, ke), scale=ke)
        for k, x in enumerate(marks):
            km = pop(t, 0.78 + 0.085 * k, 0.2)
            if km > 0:
                put1(im, xm, x, AY, a=min(1, km), scale=km)
        n = int(round(140 * ease((t - 0.78) / 0.68))) if t > 0.78 else 0
        if t >= 0.78:
            done = t >= 1.46
            txt = "140+ PENCARIAN GAGAL" if done else f"PENCARIAN: {n}"
            sp = pill(txt, 40 if done else 34, WHITE, bg=(190, 30, 28, 235) if done else (10, 14, 24, 215))
            put1(im, sp, 790, 1150, scale=pop(t, 1.46, 0.25) if done else 1.0)
        frames.append(im)
    encode([f for f in frames if f is not None] if times is None else [], "clips/skema_lini.mp4") if times is None else None
    return frames


# ---------- penampang ----------
PX = 22                    # px per metre
GY = 700                   # ground surface
FY0 = GY + 10 * PX         # top of the foundations, +-10 m down
FX0, FX1 = 140, 140 + 36 * PX


def palm(d, x, y, h, col=(40, 70, 40, 255)):
    d.line([(x, y), (x + 6, y - h)], fill=(90, 70, 50, 255), width=7)
    for ang in (-160, -130, -100, -70, -40, -15):
        a = math.radians(ang)
        d.line([(x + 6, y - h), (x + 6 + 46 * math.cos(a), y - h + 46 * math.sin(a) + 12)], fill=col, width=7)


def penampang_bg():
    a = np.zeros((H, W, 3), np.float32)
    sky = backdrop((120, 160, 200), (180, 205, 225))
    a[:] = np.asarray(sky.convert("RGB"), np.float32)
    v = np.clip((YY - GY) / 520, 0, 1)[..., None]
    earth = np.array([118, 88, 60], np.float32) * (1 - v) + np.array([62, 44, 30], np.float32) * v
    a = np.where((YY >= GY)[..., None], earth, a)
    rng = np.random.default_rng(80)
    grain = rng.normal(0, 6, (H, W, 1)).astype(np.float32)
    a = np.where((YY >= GY)[..., None], a + grain, a)
    im = to_img(a).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle([0, GY - 14, W, GY], fill=(70, 130, 60, 255))             # lawn
    for x, h in ((80, 92), (230, 76), (470, 98), (700, 80), (880, 94), (1010, 70)):
        palm(d, x, GY - 12, h)
    return im


def blocks(d, x0, x1, y0, y1, col=(226, 214, 186, 255), line=(150, 136, 110, 255)):
    d.rectangle([x0, y0, x1, y1], fill=col)
    bh = (y1 - y0) / 2
    for r in range(2):
        yy = y0 + r * bh
        d.line([(x0, yy), (x1, yy)], fill=line, width=2)
        off = 0 if r == 0 else 36
        for x in range(int(x0 + off), int(x1), 72):
            d.line([(x, yy), (x, yy + bh)], fill=line, width=2)
    d.rectangle([x0, y0, x1, y1], outline=line, width=3)


def skema_penampang(times=None):
    bg = penampang_bg()
    taman = pill("TAMAN SHALLALAT", 32, YELLOW)
    tw = label([("terowongan", 30, WHITE, True), ("→ ke utara", 28, YELLOW, True)])
    dep = label([("±10 m", 40, YELLOW, True), ("di bawah tanah", 26, WHITE, False)])
    lng = label([("≥36 m", 40, YELLOW, True)])
    fnd = label([("FONDASI BATU KAPUR", 32, WHITE, True)])
    frames = []
    for i in range(N["penampang"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        d = ImageDraw.Draw(im, "RGBA")
        u = ease((t - 0.0) / 0.55)                       # the foundations come out of the earth, left to right
        if u > 0:
            xe = FX0 + (FX1 - FX0) * u
            blocks(d, FX0, xe, FY0, FY0 + 64)
            wall_h = 120
            d.rectangle([FX0, FY0 - wall_h, FX0 + 26, FY0], fill=(214, 200, 170, 255))
            if u > 0.97:
                d.rectangle([FX1 - 26, FY0 - wall_h, FX1, FY0], fill=(214, 200, 170, 255))
            put1(im, fnd, (FX0 + FX1) / 2, FY0 - 60, a=ramp(t, 0.15, 0.4))
        kl = ease((t - 0.42) / 0.4)                      # >=36 m
        if kl > 0:
            y = FY0 + 150
            xm = (FX0 + FX1) / 2
            d.line([(xm - (xm - FX0) * kl, y), (xm + (FX1 - xm) * kl, y)], fill=YELLOW + (255,), width=5)
            for x in (xm - (xm - FX0) * kl, xm + (FX1 - xm) * kl):
                d.line([(x, y - 14), (x, y + 14)], fill=YELLOW + (255,), width=5)
            put1(im, lng, xm, y + 52, a=min(1, kl * 1.5))
        kd = ease((t - 0.99) / 0.35)                     # +-10 m
        if kd > 0:
            x = 70
            d.line([(x, GY), (x, GY + (FY0 - GY) * kd)], fill=YELLOW + (255,), width=5)
            d.line([(x - 14, GY), (x + 14, GY)], fill=YELLOW + (255,), width=5)
            if kd > 0.95:
                d.line([(x - 14, FY0), (x + 14, FY0)], fill=YELLOW + (255,), width=5)
            put1(im, dep, 200, (GY + FY0) / 2 - 40, a=min(1, kd * 1.5))
        kt = pop(t, 1.29)
        if kt > 0:
            put1(im, taman, 540, GY - 150 + 0 * kt, a=min(1, kt), scale=kt)
        ku = ease((t - 1.55) / 0.45)                     # the tunnel runs north under the building
        if ku > 0:
            ty = FY0 + 64 + 34
            x1 = 560 + (1040 - 560) * ku
            d.rounded_rectangle([560, ty - 22, x1, ty + 22], radius=20, fill=(20, 14, 10, 255))
            put1(im, tw, 965, 1160, a=min(1, ku * 1.5))
        frames.append(im)
    if times is None:
        encode(frames, "clips/skema_penampang.mp4")
    return frames


# ---------- peta ----------
def peta_bg():
    im = backdrop((22, 60, 96), (14, 40, 70)).copy()
    d = ImageDraw.Draw(im, "RGBA")
    # land: everything under the coast line (north up; the Eastern Harbour is the bay in the middle)
    coast = [(0, 860), (120, 850), (200, 800), (250, 760), (300, 790), (330, 860), (420, 905), (540, 915),
             (650, 895), (730, 850), (780, 800), (820, 820), (860, 880), (960, 900), (1080, 890)]
    d.polygon(coast + [(1080, 1920), (0, 1920)], fill=(196, 178, 140, 255))
    d.line(coast, fill=(240, 230, 200, 255), width=4)
    # royal quarter (Brucheion), south-east shore of the harbour
    d.polygon([(600, 905), (700, 885), (780, 830), (840, 870), (880, 1000), (900, 1100), (660, 1100), (620, 1010)], fill=(232, 200, 80, 90))
    return im


def skema_peta(times=None):
    bg = peta_bg()
    sea = label([("LAUT TENGAH", 34, (200, 225, 245), True)])
    qb = label([("Benteng Qaitbay", 26, WHITE, True), ("(bekas Mercusuar)", 22, WHITE, False)])
    rq = label([("kawasan istana kuno", 24, WHITE, True)])
    sh = pill("TAMAN SHALLALAT", 30, YELLOW)
    sema = pill("makam raja-raja Ptolemaios (Sema)?", 30, WHITE, bg=(150, 30, 28, 230))
    DX, DY = 740, 1000
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        put1(im, sea, 540, 680, a=ramp(t, 0.0, 0.2))
        put1(im, qb, 250, 690, a=ramp(t, 0.05, 0.25))
        put1(im, rq, 780, 1078, a=ramp(t, 0.1, 0.3))
        k = pop(t, 0.04)
        if k > 0:
            d = ImageDraw.Draw(im, "RGBA")
            ph = (t * 2.2) % 1.0
            r = 18 + 40 * ph
            d.ellipse([DX - r, DY - r, DX + r, DY + r], outline=YELLOW + (int(255 * (1 - ph)),), width=5)
            d.line([(585, 1040), (DX - 18, DY + 6)], fill=YELLOW + (int(255 * min(1, k)),), width=4)
            d.ellipse([DX - 16, DY - 16, DX + 16, DY + 16], fill=YELLOW + (255,), outline=(40, 30, 0, 255), width=3)
            put1(im, sh, 450, 1040, a=min(1, k), scale=k)
        ks = pop(t, 0.57)
        if ks > 0:
            put1(im, sema, 540, 1162, a=min(1, ks), scale=ks)
        frames.append(im)
    if times is None:
        encode(frames, "clips/skema_peta.mp4")
    return frames


# ---------- cover ----------
def cover():
    im = Image.open("img/H4.jpg").convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")
    t = text_sprite([("MAKAM", 80, WHITE, True), ("ALEXANDER AGUNG", 92, YELLOW, True), ("DITEMUKAN?", 80, WHITE, True)], gap=8)
    put1(im, t, 540, 315)
    tag = pill("ilustrasi", 24, WHITE)
    put1(im, tag, 960, 1860)
    im.convert("RGB").save("img/cover80.jpg", quality=93)
    print("img/cover80.jpg")


if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or ["prep", "lini", "penampang", "peta", "cover"]
    fns = {"lini": skema_lini, "penampang": skema_penampang, "peta": skema_peta}
    for name in todo:
        if name == "prep":
            prep()
        elif name == "cover":
            cover()
        else:
            fr = fns[name](times)
            if out:
                sheet(fr, name, out)
