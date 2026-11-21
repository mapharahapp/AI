"""Schematic animations for Titik Heran #72 (run in the episode work dir; writes clips/skema_tbabun.mp4,
skema_timbangan.mp4, skema_batas.mp4, skema_taung.mp4, skema_mata.mp4). Skulls are line drawings only (no fossil photos,
no wounds, rule from #29); the study's own photos are not used.
tbabun: side view of an adult male baboon skull (long muzzle, big canine) drawn on in white on a warm dark ground; two red
  puncture marks pulse in the eye socket on "berlubang" (Hobaiter et al., Am. J. Biol. Anthropol., 18 Nov 2026: talon
  punctures in the skull, two of them in the orbits); pill "Dataran Tinggi Ennedi, CHAD · studi 18 Nov 2026".
timbangan: a seesaw, baboon silhouette "26 KG" left, eagle silhouette "±4 KG" right; it tips to the baboon's side.
batas: a dashed line "batas lama: 13 kg" (no primate above 13 kg had been recorded as raptor prey) is drawn, then a
  yellow bar counts up to 26 kg and breaks through it; the line turns red and its label is struck through.
taung: front view of a child hominin skull (round braincase, big round orbits, short face) drawn on in cool white; card
  "ANAK TAUNG · Afrika Selatan · ditemukan 1924" and, on "juta", "±2,8 juta tahun".
mata: the same skull close on the orbits; red arcs pulse along the orbit floors with small talon marks (Berger 2006,
  Am. J. Phys. Anthropol. 131:166-168); pill "bekas cakar di rongga mata · Berger, 2006".
Event times are seconds from the start of each clip, read off `render.py 72 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < ~640) and the captions (y >= 1210).
usage: python3 skema72.py [tbabun|timbangan|batas|taung|mata ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, chaikin, dashed, text_sprite
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted, path_upto

WHITE, RED = (255, 255, 255), (232, 44, 40)
N = {"tbabun": 60, "timbangan": 40, "batas": 64, "taung": 134, "mata": 42}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 72 plan` (tbabun starts at "babun+0.1"): tbabun "berlubang" 0.97, "bekas" 1.45, cut at 1.70;
# timbangan "empat" 0.05, "kilo" 0.37, cut 1.13; batas "primata" 0.04, "tiga" 0.79, "belas" 0.99, "kilo" 1.27, cut 1.93;
# taung "tengkorak" 0.54, "anak" 0.98, "purba" 1.61, "hampir" 2.57, "tiga" 3.04, "juta" 3.24, "tahun" 3.52, cut 4.27;
# mata "rongga" 0.03, "matanya" 0.27, cut 1.17
T = {"holes": 0.92,
     "tilt0": 0.04, "tilt1": 0.50,
     "line0": 0.08, "line1": 0.62, "lpill": 0.76, "bar0": 0.95, "bar1": 1.50, "cross": 1.22,
     "skull0": 0.04, "skull1": 1.10, "c1": 0.96, "c2": 1.58, "c3": 2.10, "age": 3.22,
     "ring": 0.06, "scr": 0.24, "mpill": 0.34}

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
WARM = ((44, 31, 22), (12, 9, 7), (34, 22, 10))
COOL = ((20, 27, 38), (6, 8, 12), (16, 26, 40))
TOPFADE = np.clip((660 - YY) / 300, 0, 1)[..., None] * 0.72          # the close-up skull dims under the titles


def backdrop(tint, gx=540, gy=900):
    v = (YY / H)[..., None]
    a = np.array(tint[0], np.float32) * (1 - v) + np.array(tint[1], np.float32) * v
    a = a + np.exp(-((XX - gx) ** 2 + (YY - gy) ** 2) / (2 * 430 ** 2))[..., None] * np.array(tint[2], np.float32)
    im = to_img(a).convert("RGBA")
    g = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(g)
    for x in range(0, W + 1, 90):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 9), width=1)
    for y in range(30, H + 1, 90):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 9), width=1)
    im.alpha_composite(g)
    return im


def closed(pts, n=3):
    p = chaikin(pts, n)
    return p + [p[0]]


def ell(cx, cy, rx, ry, a0=0, a1=360, n=72):
    return [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]


def strokes(paths, u=1.0, col=WHITE + (255,), width=5.0):
    """polylines (1x coords) drawn at 2x, the first fraction u of each, returned as a 1x RGBA layer"""
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for pts in paths:
        p = pts if u >= 1 else path_upto(pts, max(u, 0.0))
        if len(p) > 1:
            d.line([(x * S, y * S) for x, y in p], fill=col, width=max(1, int(width * S)), joint="curve")
    return lay.resize((W, H), Image.LANCZOS)


def glowing(base, paths, u, col, width, glow=0.7):
    if u <= 0:
        return
    ln = strokes(paths, u, col + (255,), width)
    if glow > 0:
        g = ln.filter(ImageFilter.GaussianBlur(7))
        g.putalpha(g.getchannel("A").point(lambda v: int(min(255, v * 1.6 * glow))))
        base.alpha_composite(g)
    base.alpha_composite(ln)


def alpha(lay, a):
    if a >= 0.999:
        return lay
    l2 = lay.copy()
    l2.putalpha(l2.getchannel("A").point(lambda v: int(v * a)))
    return l2


# ---------- baboon skull, side view, muzzle to the left ----------
def baboon_skull():
    main = [closed([(880, 880), (892, 818), (862, 758), (802, 714), (722, 692), (642, 700), (582, 725), (546, 750),
                    (516, 762), (494, 778), (470, 792), (380, 808), (290, 830), (222, 850), (196, 866), (186, 890),
                    (192, 922), (206, 952), (262, 960), (400, 963), (560, 962), (622, 952), (702, 948), (792, 952),
                    (852, 930)], 2),
            closed([(212, 972), (400, 976), (560, 976), (640, 966), (690, 935), (712, 930), (714, 975), (690, 1030),
                    (612, 1064), (470, 1068), (340, 1052), (262, 1028), (224, 1004)], 2),
            ell(535, 815, 40, 44)]
    detail = [chaikin([(470, 778), (505, 762), (548, 766), (580, 790)], 1)[:-1],                 # brow ridge
              [(232, 892), (320, 878), (400, 870), (476, 866)],                                    # maxillary ridge
              [(250, 922), (340, 914), (430, 908)],
              [(560, 870), (632, 874), (706, 886), (760, 904)], [(568, 902), (636, 906), (708, 914), (760, 920)],
              ell(204, 900, 9, 7), ell(782, 908, 13, 13),
              [(610, 752), (690, 734), (770, 748), (840, 792)],                                    # temporal line
              [(288, 960), (322, 960), (318, 996), (306, 1034), (296, 996), (288, 960)],           # upper canine
              [(640, 1000), (612, 1040)]]                                                          # jaw angle line
    detail += [[(x, 962), (x, 976)] for x in range(360, 600, 34)]
    return main, detail


def puncture(base, x, y, t, t0):
    k = pop(t, t0, 0.25)
    if k <= 0:
        return
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for j in range(2):                                    # two expanding rings
        ph = ((t - t0) * 1.6 + j * 0.5) % 1.0
        r = 12 + 46 * ph
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], outline=RED + (int(220 * (1 - ph)),), width=4 * S)
    r = 11 * k
    d.ellipse([(x - r - 4) * S, (y - r - 4) * S, (x + r + 4) * S, (y + r + 4) * S], fill=RED + (255,))
    d.ellipse([(x - r * 0.55) * S, (y - r * 0.55) * S, (x + r * 0.55) * S, (y + r * 0.55) * S], fill=(40, 6, 6, 255))
    lay = lay.resize((W, H), Image.LANCZOS)
    g = lay.filter(ImageFilter.GaussianBlur(9))
    base.alpha_composite(g)
    base.alpha_composite(lay)


def skema_tbabun(times=None):
    bg = backdrop(WARM, 540, 880)
    main, detail = baboon_skull()
    src = pill("Dataran Tinggi Ennedi, CHAD · studi 18 Nov 2026", 28, col=(240, 232, 220), bg=(0, 0, 0, 170),
               edge=(255, 255, 255, 70))
    frames = []
    for i in range(N["tbabun"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        u = 0.3 + 0.7 * ease(t / 0.55)
        glowing(im, main, u, (250, 244, 232), 5.5)
        glowing(im, detail, ease((t - 0.2) / 0.5), (250, 244, 232), 3.5, glow=0.4)
        puncture(im, 500, 812, t, T["holes"])
        puncture(im, 532, 838, t, T["holes"] + 0.12)
        put1(im, src, 540, 1122, a=ramp(t, 0.25, 0.45))
        frames.append(im.convert("RGB"))
    return frames


# ---------- silhouettes (feet on the line y = cy) ----------
def silhouette(kind, cx, cy, s=1.0, col=(232, 226, 214)):
    m = Image.new("L", (W * S, H * S))
    d = ImageDraw.Draw(m)
    P = lambda x, y: ((cx + x * s) * S, (cy + y * s) * S)
    B = lambda x0, y0, x1, y1: [*P(x0, y0), *P(x1, y1)]
    if kind == "baboon":                                  # walking baboon facing left
        d.ellipse(B(-100, -130, 105, -52), fill=255)
        d.ellipse(B(-122, -152, -8, -62), fill=255)       # shoulder mane
        d.ellipse(B(-165, -162, -95, -96), fill=255)      # head
        d.polygon([P(-150, -142), P(-204, -122), P(-208, -102), P(-148, -98)], fill=255)  # muzzle
        for x0 in (-96, -62, 52, 84):
            d.polygon([P(x0, -84), P(x0 + 24, -84), P(x0 + 20, 0), P(x0 + 2, 0)], fill=255)
        d.line([P(98, -104), P(138, -124), P(162, -98), P(168, -50)], fill=255, width=int(17 * s * S), joint="curve")
    else:                                                 # perched eagle facing left
        d.ellipse(B(-40, -150, 50, 2), fill=255)
        d.ellipse(B(-38, -198, 14, -146), fill=255)       # head
        d.polygon([P(-34, -182), P(-60, -170), P(-54, -156), P(-34, -158)], fill=255)    # hooked beak
        d.polygon([P(-8, -150), P(58, -124), P(72, -24), P(44, 12), P(10, -40)], fill=255)  # folded wing
        d.polygon([P(18, -22), P(72, 44), P(42, 54), P(2, -4)], fill=255)                 # tail
        for x0 in (-14, 10):
            d.line([P(x0, -12), P(x0 - 2, 0)], fill=255, width=int(9 * s * S))
    m = m.resize((W, H), Image.LANCZOS)
    lay = Image.new("RGBA", (W, H), col + (0,))
    lay.putalpha(m)
    return lay


def skema_timbangan(times=None):
    bg = backdrop(WARM, 540, 980)
    PX, PY, L = 540, 1040, 340
    ground = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(ground)
    gd.polygon([(PX, PY + 6), (PX - 62, 1140), (PX + 62, 1140)], fill=(120, 104, 86, 255))
    gd.line([(130, 1140), (950, 1140)], fill=(255, 255, 255, 60), width=3)
    p26 = pill("26 KG", 56, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220))
    p4 = pill("±4 KG", 46, col=WHITE, bg=(10, 14, 24, 215), edge=(255, 255, 255, 140))
    frames = []
    for i in range(N["timbangan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        th = 0.21 * pop(t, T["tilt0"], T["tilt1"] - T["tilt0"])
        c, s_ = math.cos(th), math.sin(th)
        pos = lambda dd: (PX + dd * c, PY - dd * s_)
        im = bg.copy()
        im.alpha_composite(ground)
        bx, by = pos(-262)
        ex, ey = pos(262)
        im.alpha_composite(silhouette("baboon", bx + 20, by - 8, 0.95))
        im.alpha_composite(silhouette("eagle", ex, ey - 8, 0.95))
        beam = Image.new("RGBA", (W * S, H * S))
        bd = ImageDraw.Draw(beam)
        (x0, y0), (x1, y1) = pos(-L), pos(L)
        bd.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=(214, 190, 150, 255), width=16 * S)
        bd.ellipse([(PX - 13) * S, (PY - 13) * S, (PX + 13) * S, (PY + 13) * S], fill=(60, 50, 40, 255))
        im.alpha_composite(beam.resize((W, H), Image.LANCZOS))
        put1(im, p26, bx, by - 232, scale=min(pop(t, 0.0, 0.25), 1.06))
        put1(im, p4, ex, ey - 262, scale=min(pop(t, 0.06, 0.25), 1.06))
        frames.append(im.convert("RGB"))
    return frames


def skema_batas(times=None):
    bg = backdrop(WARM, 540, 980)
    BASE, X0, X1, BX0, BX1, K, LY = 1180, 160, 920, 600, 790, 20, 920   # LY = BASE - 13 kg * K
    ground = Image.new("RGBA", (W, H))
    ImageDraw.Draw(ground).line([(X0, BASE), (X1, BASE)], fill=(255, 255, 255, 150), width=4)
    ground.alpha_composite(silhouette("eagle", 300, BASE - 2, 0.9))
    lp = pill("batas lama: 13 kg", 38, col=WHITE, bg=(10, 14, 24, 215), edge=(255, 255, 255, 140))
    bp = pill("babun Ennedi", 34, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220))
    frames = []
    for i in range(N["batas"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        im.alpha_composite(ground)
        kg = 26 * ease((t - T["bar0"]) / (T["bar1"] - T["bar0"]))
        broke = ramp(t, T["cross"], T["cross"] + 0.12)
        lay = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(lay)
        if kg > 0.2:
            top = BASE - kg * K
            d.rectangle([BX0 * S, top * S, BX1 * S, BASE * S], fill=YELLOW + (235,))
            d.rectangle([BX0 * S, top * S, BX1 * S, (top + 8) * S], fill=(255, 250, 200, 255))
        lc = tuple(int(a + (b - a) * broke) for a, b in zip(WHITE, RED))
        dashed(d, [(X0, LY), (X1, LY)], lc + (255,), 5, dash=30, gap=18,
               upto=(X1 - X0) * ease((t - T["line0"]) / (T["line1"] - T["line0"])))
        im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        if kg > 3:
            num = text_sprite([(f"{round(kg)} KG", 46, (20, 20, 20), True)])
            put1(im, num, (BX0 + BX1) / 2, BASE - kg * K + 46)
        lx, ly = 340, 876
        put1(im, lp, lx, ly, scale=min(pop(t, T["lpill"], 0.3), 1.06))
        if broke > 0:
            st = Image.new("RGBA", (W * S, H * S))
            w2 = lp.width / S / 2 - 14
            ImageDraw.Draw(st).line([((lx - w2) * S, ly * S), ((lx - w2 + 2 * w2 * broke) * S, ly * S)],
                                    fill=RED + (255,), width=7 * S)
            im.alpha_composite(st.resize((W, H), Image.LANCZOS))
        put1(im, bp, 380, 704, scale=min(pop(t, T["bar1"] - 0.1, 0.3), 1.06))
        frames.append(im.convert("RGB"))
    return frames


# ---------- child hominin skull, front view (local coords, centre origin) ----------
def taung_paths(cx, cy, s):
    f = lambda pts: [(cx + x * s, cy + y * s) for x, y in pts]
    main = [f(closed([(-150, 20), (-166, -50), (-145, -130), (-90, -185), (0, -205), (90, -185), (145, -130),
                      (166, -50), (150, 20), (174, 70), (160, 110), (128, 130), (118, 175), (112, 228), (70, 262),
                      (0, 274), (-70, 262), (-112, 228), (-118, 175), (-128, 130), (-160, 110), (-174, 70)], 3)),
            f(ell(-62, 32, 50, 46)), f(ell(62, 32, 50, 46)),
            f(closed([(0, 76), (18, 90), (28, 120), (24, 148), (0, 154), (-24, 148), (-28, 120), (-18, 90)], 2))]
    detail = []
    for sx in (-1, 1):
        detail.append(f(chaikin([(sx * 12, -8), (sx * 62, -24), (sx * 120, -4)], 1)[:-1]))        # brow
        detail.append(f(chaikin([(sx * 100, 64), (sx * 118, 100), (sx * 128, 128)], 1)[:-1]))     # cheekbone
        detail.append(f([(sx * 118, 176), (sx * 100, 214)]))                                       # jaw line
    arc = lambda y: [(x, y - 0.005 * x * x) for x in range(-74, 75, 6)]
    for y0, y1 in ((180, 202), (206, 226)):                                                        # teeth rows
        detail += [f(arc(y0)), f(arc(y1))]
        detail += [f([(x, y0 - 0.005 * x * x), (x, y1 - 0.005 * x * x)]) for x in range(-66, 67, 19)]
    return main, detail, []


SKULL_C = (220, 234, 255)


def draw_taung(im, cx, cy, s, u=1.0, ud=1.0):
    main, detail, suture = taung_paths(cx, cy, s)
    glowing(im, main, u, SKULL_C, 5.5 * max(1, s * 0.8))
    glowing(im, detail, ud, SKULL_C, 3.5 * max(1, s * 0.8), glow=0.35)
    glowing(im, suture, ud, (150, 168, 190), 2.5 * max(1, s * 0.8), glow=0)


def skema_taung(times=None):
    bg = backdrop(COOL, 420, 900)
    SX, SY, SC = 400, 902, 0.85
    c1 = text_sprite([("ANAK TAUNG", 46, YELLOW, True)])
    c2 = text_sprite([("Afrika Selatan", 34, WHITE, False)])
    c3 = text_sprite([("ditemukan 1924", 34, WHITE, False)])
    age = pill("±2,8 juta tahun", 36, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220))
    frames = []
    for i in range(N["taung"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        z = 1.0 + 0.05 * t / 4.4
        draw_taung(im, SX, SY, SC * z, ease((t - T["skull0"]) / (T["skull1"] - T["skull0"])),
                   ease((t - 0.7) / 0.6))
        rule = Image.new("RGBA", (W, H))
        ImageDraw.Draw(rule).line([(652, 726), (652, 726 + 190 * ramp(t, T["c1"] - 0.1, T["c1"] + 0.2))],
                                  fill=YELLOW + (200,), width=4)
        im.alpha_composite(rule)
        put1(im, c1, 846, 754, a=ramp(t, T["c1"], T["c1"] + 0.15), scale=min(pop(t, T["c1"], 0.3), 1.05))
        put1(im, c2, 846, 820, a=ramp(t, T["c2"], T["c2"] + 0.2))
        put1(im, c3, 846, 878, a=ramp(t, T["c3"], T["c3"] + 0.2))
        put1(im, age, 846, 1062, scale=min(pop(t, T["age"], 0.3), 1.06))
        frames.append(im.convert("RGB"))
    return frames


def skema_mata(times=None):
    bg = backdrop(COOL, 540, 860)
    src = pill("bekas cakar di rongga mata · Berger, 2006", 28, col=(240, 236, 228), bg=(0, 0, 0, 185),
               edge=(255, 255, 255, 70))
    frames = []
    for i in range(N["mata"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        s = 1.75 + 0.3 * ease(t / 0.4)
        cx, cy = 540, 870 - 40 * s
        im = bg.copy()
        draw_taung(im, cx, cy, s)
        for j, sx in enumerate((-1, 1)):
            k = ramp(t, T["ring"] + 0.08 * j, T["ring"] + 0.08 * j + 0.15)
            if k <= 0:
                continue
            ox, oy = cx + sx * 70 * s, cy + 40 * s
            puls = 0.75 + 0.25 * math.sin((t - T["ring"]) * 11)
            arc = [ell(ox, oy, 54 * s + 2, 50 * s + 2, 15, 165, 40)]
            glowing(im, arc, k, RED, 10, glow=1.2 * puls)
            m = ramp(t, T["scr"] + 0.06 * j, T["scr"] + 0.06 * j + 0.12)
            if m > 0:
                marks = [[(ox + dx * s, oy + 34 * s), (ox + (dx + 7) * s, oy + 46 * s)] for dx in (-24, -6, 12)]
                glowing(im, marks, m, RED, 7, glow=0.8)
        put1(im, src, 540, 1150, scale=min(pop(t, T["mpill"], 0.3), 1.05))
        frames.append(to_img(np.asarray(im.convert("RGB"), np.float32) * (1 - TOPFADE)))
    return frames


FUN = {"tbabun": skema_tbabun, "timbangan": skema_timbangan, "batas": skema_batas, "taung": skema_taung,
       "mata": skema_mata}

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
