"""Schematic animations for Titik Heran #54 (run in the episode work dir; writes clips/skema_siluet.mp4, skema_rahang.mp4
and skema_kunyah.mp4). There is no photo or honest reconstruction of Infernogallus on Pixabay (and we use no AI dinosaurs),
so all three are plain line drawings labelled "skema".
siluet: a faint T. rex outline behind a small yellow beaked dinosaur, "skala perkiraan"; red berries pop by its beak on
  "buah" (1,36 s), "±12 kg" on "yang" (2,17 s). The small one is a generic toothless beaked theropod, not a reconstruction.
rahang: a toothless beaked skull in side view; from "bergeser" (0,91 s) the lower jaw slides front-back under a yellow
  double arrow; a berry with a seed appears in front of the beak on "melumat" (2,68 s).
kunyah: a parrot head and a human head in profile; both lower jaws slide front-back with the same arrow; "manusia" pops
  on "manusia" (1,27 s), the parrot side shows from the start.
Event times are seconds from the start of each clip, read off `render.py 54 plan` after prep54.py (siluet starts at 8,20,
rahang at 12,57, kunyah at 22,60). Text stays out of the watermark band (y 935-985), the title zone (y < 660) and the
captions (y >= 1210).
usage: python3 skema54.py [siluet|rahang|kunyah ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, encode, dashed
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema49 import path_upto

N = {"siluet": 100, "rahang": 124, "kunyah": 72}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
RED = (226, 60, 50)


def smooth(pts, closed=False, n=3):
    for _ in range(n):
        q = [pts[0]] if not closed else []
        pairs = list(zip(pts, pts[1:] + pts[:1])) if closed else list(zip(pts, pts[1:]))
        for (x0, y0), (x1, y1) in pairs:
            q += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        if not closed:
            q.append(pts[-1])
        pts = q
    return pts


def place(pts, x0, y0, s, flip=False):
    return [(x0 + (s * (1 - x) if flip else s * x), y0 + s * y) for x, y in pts]


def backdrop(top=(22, 30, 40), bot=(8, 12, 18)):
    v = (YY / H)[..., None]
    a = np.array(top, np.float32) * (1 - v) + np.array(bot, np.float32) * v
    im = to_img(a).convert("RGBA")
    d = ImageDraw.Draw(im)
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 10))
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 10))
    return im


def stroke(im, paths, col, width, u=1.0, fill=None, glow=False):
    """draw 1x paths at 2x; u draws them on by length"""
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for p, closed in paths:
        if fill and closed and u >= 1:
            d.polygon([(x * S, y * S) for x, y in p], fill=fill)
        q = path_upto(p + ([p[0]] if closed else []), u)
        if len(q) > 1:
            d.line([(x * S, y * S) for x, y in q], fill=col, width=width * S, joint="curve")
    lay = lay.resize((W, H), Image.LANCZOS)
    if glow:
        im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(8)))
    im.alpha_composite(lay)


def arrow2(im, x0, x1, y, col=YELLOW, a=1.0, w=8):
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    c = col + (int(255 * a),)
    d.line([(x0 * S, y * S), (x1 * S, y * S)], fill=c, width=w * S)
    for xe, sgn in ((x0, 1), (x1, -1)):
        d.polygon([(xe * S - sgn * 4 * S, y * S), ((xe + sgn * 30) * S, (y - 20) * S), ((xe + sgn * 30) * S, (y + 20) * S)], fill=c)
    im.alpha_composite(lay.resize((W, H), Image.LANCZOS))


def berry(im, x, y, r, seed=False, a=1.0):
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=RED + (int(255 * a),), outline=(255, 230, 220, int(255 * a)), width=3 * S)
    d.ellipse([(x - r * 0.45) * S, (y - r * 0.6) * S, (x - r * 0.15) * S, (y - r * 0.3) * S], fill=(255, 200, 190, int(200 * a)))
    if seed:
        d.ellipse([(x - r * 0.35) * S, (y - r * 0.2) * S, (x + r * 0.35) * S, (y + r * 0.45) * S], fill=(110, 70, 40, int(255 * a)))
    im.alpha_composite(lay.resize((W, H), Image.LANCZOS))


# ---------- siluet ----------
TREX = [(0.00, 0.10), (0.00, 0.14), (0.01, 0.17), (0.12, 0.21), (0.17, 0.20), (0.22, 0.22), (0.28, 0.27), (0.29, 0.30),
        (0.27, 0.33), (0.30, 0.32), (0.32, 0.29), (0.38, 0.32), (0.44, 0.34), (0.42, 0.46), (0.40, 0.55), (0.35, 0.58),
        (0.46, 0.58), (0.47, 0.48), (0.50, 0.38), (0.53, 0.37), (0.55, 0.43), (0.54, 0.54), (0.50, 0.58), (0.60, 0.58),
        (0.61, 0.46), (0.62, 0.34), (0.75, 0.27), (1.00, 0.20), (1.00, 0.18), (0.75, 0.19), (0.58, 0.15), (0.40, 0.14),
        (0.25, 0.11), (0.20, 0.05), (0.15, 0.03), (0.06, 0.05)]
SMALL = [(0.00, 0.14), (0.06, 0.18), (0.12, 0.20), (0.18, 0.35), (0.25, 0.50), (0.30, 0.58), (0.40, 0.60), (0.50, 0.62),
         (0.52, 0.70), (0.50, 0.90), (0.46, 0.98), (0.56, 0.98), (0.58, 0.88), (0.60, 0.66), (0.80, 0.55), (1.00, 0.48),
         (0.98, 0.42), (0.75, 0.42), (0.55, 0.38), (0.35, 0.36), (0.20, 0.20), (0.17, 0.08), (0.12, 0.03), (0.06, 0.05)]


def skema_siluet(times=None):
    base = backdrop()
    d = ImageDraw.Draw(base)
    d.line([(0, 1185), (W, 1185)], fill=(200, 200, 200, 90), width=3)
    trex = smooth(place(TREX, 330, 1185 - 0.58 * 1000, 1000), closed=True, n=2)
    small = smooth(place(SMALL, 90, 1185 - 0.98 * 230, 230), closed=True)
    eye = (90 + 0.11 * 230, 1185 - 0.98 * 230 + 0.10 * 230)
    lab_t = pill("T. rex", 34, col=(220, 220, 225), bg=(10, 14, 24, 190))
    lab_s = pill("si \"ayam neraka\"", 34, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200))
    lab_kg = pill("±12 kg", 44, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220))
    note = pill("skala perkiraan", 24, col=(210, 210, 215), bg=(10, 14, 24, 170))
    t_b, t_k = 1.36, 2.17
    frames = []
    for i in range(N["siluet"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        stroke(im, [(trex, True)], (200, 205, 215, 170), 4, u=ease(t / 0.8), fill=(120, 130, 145, 40))
        stroke(im, [(small, True)], YELLOW + (255,), 6, u=ease((t - 0.1) / 0.6), fill=YELLOW + (70,), glow=True)
        if t > 0.6:
            ImageDraw.Draw(im).ellipse([eye[0] - 5, eye[1] - 5, eye[0] + 5, eye[1] + 5], fill=(20, 20, 20, 255))
        put1(im, lab_t, 870, 830, a=ramp(t, 0.5, 0.8))
        put1(im, lab_s, 220, 880, a=ramp(t, 0.4, 0.7))
        if t > t_b:
            for k, (bx, by) in enumerate(((60, 1000), (34, 1036), (78, 1046))):
                berry(im, bx, by, 16, a=min(pop(t, t_b + 0.06 * k, 0.3), 1.0))
        if t > t_k:
            put1(im, lab_kg, 420, 1080, scale=min(pop(t, t_k, 0.35), 1.1))
        put1(im, note, 880, 1150, a=ramp(t, 0.3, 0.6))
        frames.append(im.convert("RGB"))
    return frames


# ---------- rahang ----------
SKULL = [(0.00, 0.62), (0.03, 0.50), (0.10, 0.35), (0.25, 0.18), (0.45, 0.08), (0.65, 0.05), (0.85, 0.12), (0.98, 0.30),
         (1.00, 0.50), (0.92, 0.60), (0.70, 0.58), (0.40, 0.60), (0.15, 0.61), (0.04, 0.62)]
JAW = [(0.03, 0.645), (0.20, 0.68), (0.45, 0.70), (0.72, 0.66), (0.80, 0.72), (0.70, 0.82), (0.40, 0.84), (0.15, 0.76),
       (0.06, 0.68)]


def ring(cx, cy, r, n=40):
    return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def skema_rahang(times=None):
    base = backdrop()
    s, x0, y0 = 640, 250, 600
    skull = smooth(place(SKULL, x0, y0, s), closed=True, n=2)
    jaw0 = smooth(place(JAW, x0, y0, s), closed=True, n=2)
    orbit = place(ring(0.62, 0.28, 0.10), x0, y0, s)
    nost = place(ring(0.24, 0.33, 0.035), x0, y0, s)
    lab = pill("paruh tanpa gigi", 34, col=(220, 220, 225), bg=(10, 14, 24, 190))
    lab_b = pill("buah berbiji", 34, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200))
    t_g, t_m = 0.91, 2.68
    frames = []
    for i in range(N["rahang"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        u = ease(t / 0.7)
        dx = 34 * math.sin(2 * math.pi * 1.3 * (t - t_g)) * ramp(t, t_g, t_g + 0.25) if t > t_g else 0.0
        jaw = [(x + dx, y) for x, y in jaw0]
        stroke(im, [(skull, True), (orbit, True), (nost, True)], (245, 240, 228, 255), 6, u=u, fill=(245, 240, 228, 40))
        stroke(im, [(jaw, True)], YELLOW + (255,), 6, u=u, fill=YELLOW + (60,), glow=t > t_g)
        put1(im, lab, 540, 690, a=ramp(t, 0.5, 0.8) * (1 - ramp(t, t_m - 0.2, t_m)))
        if t > t_g:
            a = ramp(t, t_g, t_g + 0.2)
            arrow2(im, 330 + dx, 650 + dx, 1150, a=a)
        if t > t_m:
            sq = 1 - 0.25 * ramp(t, t_m + 0.4, t_m + 0.9)
            berry(im, 185, 1000, 40 * sq, seed=True, a=min(pop(t, t_m, 0.3), 1.0))
            put1(im, lab_b, 540, 690, scale=min(pop(t, t_m, 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


# ---------- kunyah ----------
PARROT_HEAD = [(0.30, 0.47), (0.16, 0.38), (0.06, 0.44), (0.00, 0.30), (0.08, 0.15), (0.25, 0.08), (0.45, 0.00),
               (0.75, 0.05), (0.95, 0.30), (0.95, 0.60), (0.80, 0.90)]
PARROT_THROAT = [(0.32, 0.64), (0.40, 0.80), (0.50, 0.92)]
PARROT_JAW = [(0.12, 0.48), (0.30, 0.50), (0.33, 0.62), (0.16, 0.60)]
HUMAN_HEAD = [(0.24, 0.62), (0.22, 0.60), (0.24, 0.53), (0.14, 0.48), (0.24, 0.36), (0.22, 0.28), (0.30, 0.10),
              (0.55, 0.00), (0.85, 0.10), (0.95, 0.35), (0.90, 0.60), (0.86, 0.95)]
HUMAN_JAW = [(0.22, 0.64), (0.25, 0.76), (0.40, 0.83), (0.60, 0.73), (0.58, 0.56)]
HUMAN_NECK = [(0.45, 0.86), (0.46, 1.00)]


def skema_kunyah(times=None):
    base = backdrop()
    s = 380
    px0, hx0, y0 = 70, 600, 640
    ph = smooth(place(PARROT_HEAD, px0, y0, s))
    pt = smooth(place(PARROT_THROAT, px0, y0, s))
    pj0 = smooth(place(PARROT_JAW, px0, y0, s), closed=True)
    pe = place(ring(0.55, 0.30, 0.05), px0, y0, s)
    hh = smooth(place(HUMAN_HEAD, hx0, y0, s))
    hj0 = smooth(place(HUMAN_JAW, hx0, y0, s))
    hn = place(HUMAN_NECK, hx0, y0, s)
    he = place(ring(0.62, 0.45, 0.06), hx0, y0, s)
    lab_p = pill("nuri", 40, col=(220, 220, 225), bg=(10, 14, 24, 190))
    lab_h = pill("manusia", 40, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220))
    t_h = 1.27
    frames = []
    for i in range(N["kunyah"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        dx = 16 * math.sin(2 * math.pi * 1.5 * t) * ramp(t, 0.1, 0.3)
        stroke(im, [(ph, False), (pt, False), (pe, True)], (245, 240, 228, 255), 6, u=ease(t / 0.5))
        stroke(im, [([(x + dx, y) for x, y in pj0], True)], YELLOW + (255,), 6, u=ease(t / 0.5), fill=YELLOW + (60,), glow=True)
        arrow2(im, px0 + 20 + dx, px0 + 200 + dx, 1110, a=ramp(t, 0.2, 0.4))
        put1(im, lab_p, px0 + 190, 1170, a=ramp(t, 0.1, 0.35))
        th = ramp(t, t_h - 0.35, t_h)
        if th > 0:
            hdx = dx * ramp(t, t_h, t_h + 0.2)
            stroke(im, [(hh, False), (hn, False), (he, True)], (245, 240, 228, int(255 * th)), 6, u=ease((t - t_h + 0.35) / 0.5))
            stroke(im, [([(x + hdx, y) for x, y in hj0], False)], YELLOW + (int(255 * th),), 6, u=ease((t - t_h + 0.35) / 0.5), glow=True)
            arrow2(im, hx0 + 60 + hdx, hx0 + 240 + hdx, 1110, a=ramp(t, t_h, t_h + 0.2))
            put1(im, lab_h, hx0 + 190, 1170, scale=min(pop(t, t_h, 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"siluet": skema_siluet, "rahang": skema_rahang, "kunyah": skema_kunyah}

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
