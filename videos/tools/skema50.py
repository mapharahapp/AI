"""Stills and schematic animations for Titik Heran #50 (run in the episode work dir; writes img/cta50.jpg,
clips/skema_jalur.mp4 and clips/skema_kiri.mp4).
Pixabay has no footage of the gut-brain signal, so it is drawn ("skema"); the study (Nature, Nov 2026, UCSF) was in mice
and people and did not test coffee, so the drawing shows "minuman" in general.
prep: img/cta50.jpg, black coffee 2619216 (left half) and cappuccino 8342636 (right half) side by side for the CTA.
jalur: a body outline; the stomach lights on "perut!" (0,37 s), a drop of drink runs down to it from 1,08 s ("saat") and
  lands on "perut," (2,37 s), signal dots climb to the brain, and from "dopamin" (3,89 s) the brain fills slowly with
  yellow sparks (slow on purpose: the release builds over minutes).
kiri: the brain seen from above (front at the top), the left half lights and flares on "kiri" (2,70 s); on "peneliti"
  (3,41 s) it dims and a "?" rises.
Event times are seconds from the start of each clip, read off `render.py 50 plan` (jalur starts at 8,90, kiri at 19,50).
Text stays out of the watermark band (y 935-985), the title zone (y < 660) and the captions (y >= 1210).
usage: python3 skema50.py [prep|jalur|kiri ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, encode, dashed, chaikin
from skema35 import sheet
from skema37 import to_img, put1, noise
from skema39 import cover
from skema46 import pill, ease, wanted

N = {"jalur": 170, "kiri": 186}
OUT = {"jalur": "clips/skema_jalur.mp4", "kiri": "clips/skema_kiri.mp4"}
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def prep():
    l = Image.open("img/2619216.jpg").convert("RGB")
    r = Image.open("img/8342636.jpg").convert("RGB")
    out = Image.new("RGB", (W, H))
    for k, (im, fx) in enumerate([(l, 0.5), (r, 0.35)]):
        s = max(540 / im.width, H / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        x0 = round((im.width - 540) * fx)
        out.paste(im.crop((x0, 0, x0 + 540, H)), (k * 540, 0))
    ImageDraw.Draw(out).rectangle([536, 0, 544, H], fill=(10, 30, 64))
    out.save("img/cta50.jpg", quality=95)
    print("img/cta50.jpg")


def navy():
    v = (YY / H)[..., None]
    a = np.array([18, 40, 80], np.float32) * (1 - v) + np.array([6, 14, 34], np.float32) * v
    a += np.exp(-((XX - 540) ** 2 + (YY - 950) ** 2) / 520 ** 2)[..., None] * np.array([16, 30, 56], np.float32)
    return a


# ---------- jalur ----------
HEAD = (540, 790, 125)
STOM = (600, 1150)
BRAIN = (540, 770)


def body_base():
    im = to_img(navy()).convert("RGBA")
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    c = (170, 200, 240, 255)
    cx, cy, r = HEAD
    d.ellipse([(cx - r) * S, (cy - r * 1.12) * S, (cx + r) * S, (cy + r) * S], fill=(30, 52, 92, 255), outline=c, width=5 * S)
    torso = [(470, 905), (470, 940), (300, 990), (250, 1060), (240, 1400), (840, 1400), (830, 1060), (780, 990), (610, 940), (610, 905)]
    d.polygon([(x * S, y * S) for x, y in torso], fill=(30, 52, 92, 255))
    d.line([(x * S, y * S) for x, y in torso], fill=c, width=5 * S)
    # brain
    bx, by = BRAIN
    d.ellipse([(bx - 90) * S, (by - 78) * S, (bx + 90) * S, (by + 50) * S], fill=(200, 140, 160, 255))
    rng = np.random.default_rng(4)
    for _ in range(9):
        x, y = bx + rng.normal(0, 40), by - 14 + rng.normal(0, 22)
        pts = [(x + 26 * math.cos(a), y + 10 * math.sin(3 * a)) for a in np.linspace(0, math.pi, 9)]
        d.line([(px * S, py * S) for px, py in pts], fill=(150, 90, 115, 255), width=4 * S, joint="curve")
    # gullet and stomach
    d.line([(540 * S, 860 * S), (540 * S, 1080 * S), (575 * S, 1105 * S)], fill=(120, 150, 200, 255), width=10 * S, joint="curve")
    return im, lay.resize((W, H), Image.LANCZOS)


def stomach_sprite(col):
    sp = Image.new("RGBA", (300 * S, 260 * S))
    d = ImageDraw.Draw(sp)
    pts = [(60, 40), (110, 45), (130, 90), (200, 80), (250, 120), (250, 180), (200, 225), (120, 220), (70, 180), (75, 120), (50, 70)]
    d.polygon([(x * S, y * S) for x, y in chaikin(pts, 4)], fill=col, outline=(255, 255, 255, 220), width=3 * S)
    return sp


def skema_jalur(times=None):
    bg, body = body_base()
    base = bg.copy()
    base.alpha_composite(body)
    st_dim, st_on = stomach_sprite((150, 110, 120, 255)), stomach_sprite((255, 170, 60, 255))
    lab_p = pill("perut", 34)
    lab_o = pill("otak", 34)
    lab_d = pill("dopamin", 36, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200))
    t_p, t_s, t_land, t_d = 0.37, 1.08, 2.37, 3.89
    up = [(STOM[0] + 10, STOM[1] - 40), (640, 1040), (640, 900), (600, 830), (BRAIN[0] + 30, BRAIN[1] + 20)]
    rng = np.random.default_rng(50)
    sparks = [(BRAIN[0] + rng.normal(0, 45), BRAIN[1] - 14 + rng.normal(0, 22), rng.random() * 1.4) for _ in range(30)]
    frames = []
    for i in range(N["jalur"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        on = ramp(t, t_p, t_p + 0.25) * (0.75 + 0.25 * math.sin(2 * math.pi * t / 1.2))
        if t > t_land:
            on = max(on, 1.0)
        gl = Image.new("RGBA", (W, H))
        ImageDraw.Draw(gl).ellipse([STOM[0] - 170, STOM[1] - 140, STOM[0] + 170, STOM[1] + 140], fill=(255, 160, 50, int(120 * on)))
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40)))
        put1(im, st_dim, STOM[0], STOM[1])
        put1(im, st_on, STOM[0], STOM[1], a=on, scale=1 + 0.08 * pop(t, t_p, 0.35) * (1 - ramp(t, t_p + 0.35, t_p + 0.6)))
        put1(im, lab_p, 840, 1150, a=ramp(t, t_p, t_p + 0.2))
        # a drop runs down the gullet
        if t_s < t < t_land + 0.1:
            u = ease((t - t_s) / (t_land - t_s))
            y = 860 + (1100 - 860) * u
            x = 540 + (35 * max(0, (y - 1080) / 25))
            d = ImageDraw.Draw(im)
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(120, 70, 40), outline=(255, 220, 160), width=3)
        # signal dots climb to the brain
        if t > t_land:
            dl = Image.new("RGBA", (W, H))
            dd = ImageDraw.Draw(dl)
            for k in range(6):
                u = ((t - t_land) * 0.55 + k / 6) % 1.0
                p = path_at(up, u)
                dd.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=YELLOW + (int(255 * ramp(t, t_land, t_land + 0.3)),))
            im.alpha_composite(dl.filter(ImageFilter.GaussianBlur(4)))
            im.alpha_composite(dl)
        put1(im, lab_o, 830, 700, a=ramp(t, t_land, t_land + 0.3) * (1 - ramp(t, t_d - 0.1, t_d)))
        # dopamine fills the brain slowly
        if t > t_d:
            g = ramp(t, t_d, t_d + 1.4)
            bl = Image.new("RGBA", (W, H))
            bd = ImageDraw.Draw(bl)
            bd.ellipse([BRAIN[0] - 110, BRAIN[1] - 95, BRAIN[0] + 110, BRAIN[1] + 70], fill=YELLOW + (int(120 * g),))
            im.alpha_composite(bl.filter(ImageFilter.GaussianBlur(30)))
            sl = Image.new("RGBA", (W, H))
            sd = ImageDraw.Draw(sl)
            for x, y, t0 in sparks:
                if t - t_d < t0:
                    continue
                a = 0.5 + 0.5 * math.sin((t - t0) * 5)
                sd.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 245, 160, int(230 * a)))
            im.alpha_composite(sl)
            put1(im, lab_d, 840, 700, scale=min(pop(t, t_d, 0.35), 1.1))
        frames.append(im.convert("RGB"))
    return frames


def path_at(pts, u):
    seg = [math.dist(pts[k], pts[k + 1]) for k in range(len(pts) - 1)]
    L, acc = sum(seg) * u, 0.0
    for k, s in enumerate(seg):
        if acc + s >= L:
            f = (L - acc) / s
            return (pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f)
        acc += s
    return pts[-1]


# ---------- kiri ----------
BC = (540, 880)


def hemi(side, col, gyri):
    """one hemisphere from above as a 2x sprite; side -1 left, 1 right"""
    w, h = 240, 380
    sp = Image.new("RGBA", ((w + 40) * S, (h + 40) * S))
    d = ImageDraw.Draw(sp)
    pts = []
    for a in np.linspace(0, 2 * math.pi, 80):
        x = math.cos(a) * w / 2 * (1.0 if math.cos(a) * side > 0 else 0.92)
        y = math.sin(a) * h / 2 * (0.95 if math.sin(a) < 0 else 1.0)
        pts.append(((x + w / 2 + 20) * S, (y + h / 2 + 20) * S))
    d.polygon(pts, fill=col)
    gl = Image.new("RGBA", sp.size)
    gd = ImageDraw.Draw(gl)
    rng = np.random.default_rng(1 if side < 0 else 2)
    for _ in range(22):
        x, y = rng.uniform(20, w + 20), rng.uniform(20, h + 20)
        q = [(x + 34 * math.cos(a) * side, y + 14 * math.sin(3 * a)) for a in np.linspace(0, math.pi, 9)]
        gd.line([(px * S, py * S) for px, py in q], fill=gyri, width=5 * S, joint="curve")
    m = Image.new("L", sp.size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    gl.putalpha(Image.fromarray(np.minimum(np.asarray(gl.getchannel("A")), np.asarray(m))))
    sp.alpha_composite(gl)
    ImageDraw.Draw(sp).line(pts + [pts[0]], fill=(255, 255, 255, 200), width=3 * S)
    return sp


def skema_kiri(times=None):
    base = to_img(navy()).convert("RGBA")
    dimL, dimR = hemi(-1, (150, 110, 130, 255), (110, 75, 95, 255)), hemi(1, (150, 110, 130, 255), (110, 75, 95, 255))
    onL = hemi(-1, (255, 200, 70, 255), (220, 140, 30, 255))
    lab_l, lab_r = pill("KIRI", 36, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200)), pill("KANAN", 36)
    q = Image.new("RGBA", (260 * S, 300 * S))
    ImageDraw.Draw(q).text((130 * S, 150 * S), "?", font=ImageFont.truetype(XB, 230 * S), fill=(255, 255, 255, 255), anchor="mm")
    t_k, t_p = 2.70, 3.41
    lx, rx = BC[0] - 127, BC[0] + 127
    frames = []
    for i in range(N["kiri"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        g = 0.55 * ramp(t, 0.9, 2.0) + 0.45 * ramp(t, t_k, t_k + 0.2)
        g *= 1 - 0.65 * ramp(t, t_p, t_p + 0.5)
        if g > 0:
            gl = Image.new("RGBA", (W, H))
            ImageDraw.Draw(gl).ellipse([lx - 170, BC[1] - 230, lx + 150, BC[1] + 230], fill=(255, 190, 50, int(150 * g)))
            im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(45)))
        put1(im, dimL, lx, BC[1])
        put1(im, dimR, rx, BC[1])
        put1(im, onL, lx, BC[1], a=g, scale=1 + 0.05 * pop(t, t_k, 0.3) * (1 - ramp(t, t_k + 0.3, t_k + 0.6)))
        put1(im, lab_l, lx, 1165, a=ramp(t, 0.2, 0.4))
        put1(im, lab_r, rx, 1165, a=ramp(t, 0.2, 0.4) * (1 - 0.5 * ramp(t, t_p, t_p + 0.5)))
        dim = ramp(t, t_p, t_p + 0.5)
        if dim > 0:
            dk = Image.new("RGBA", (W, H), (0, 0, 0, int(120 * dim)))
            im.alpha_composite(dk)
            put1(im, q, BC[0], BC[1] - 10 - 30 * ease((t - t_p) / 0.6), a=dim, scale=min(pop(t, t_p, 0.4), 1.1))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"jalur": skema_jalur, "kiri": skema_kiri}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    os.makedirs("clips", exist_ok=True)
    for name in args or ["prep"] + list(N):
        if name == "prep":
            prep()
            continue
        fr = FUN[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
