"""Schematic animations for Titik Heran #69 (run in the episode work dir; writes clips/skema_peti.mp4, skema_sarko.mp4,
skema_ukuran.mp4, skema_lipat.mp4, skema_wajah.mp4). No photo of the Nongan find may be used, so the chest is drawn from
the news descriptions: a box-shaped, carved, brown stone (padas) chest, about 125 x 90 x 60 cm, broken in two, with a carving
that resembles a human face (Disbudpar Karangasem, 19 Nov 2026).
peti: the chest rises out of the soil (oblique view, lid seam, a band of spiral medallions, a knob on the end), then a crack
  runs down it on "berukir" and the two halves part a little.
sarko: the broken chest, slow push; pills "DIDUGA KUAT SARKOFAGUS" (on "sarkofagus"), the source line, and
  "±125 x 90 x 60 cm" (on "peti mati").
ukuran: side view: the chest with a 125 cm ruler; an adult silhouette (±165 cm) lies over it and sticks out (red part), a
  yellow "?" pops on "Kok".
lipat: cross-section of the chest; a soft line figure (no bones) lies straight and sticks out of both walls (red), then folds
  into a foetal position that fits, on "dilipat"; pill "sarkofagus kecil: jenazah terlipat" and the source.
wajah: the chest's end in the dark; a torch beam sweeps across, then a mask-like face carving on the knob lights up yellow
  on "mirip"; pill "ukiran mirip wajah manusia" and a small line that the real shape is not published.
Event times are seconds from the start of each clip, read off `render.py 69 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < ~640) and the captions (y >= 1210).
usage: python3 skema69.py [peti|sarko|ukuran|lipat|wajah ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode
from skema35 import sheet
from skema37 import to_img, put1, noise
from skema46 import pill, ease, wanted
from skema70 import push

WHITE, RED = (255, 255, 255), (232, 44, 40)
N = {"peti": 56, "sarko": 114, "ukuran": 128, "lipat": 158, "wajah": 92}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 69 plan`: peti "peti" 0.05, "batu" 0.42, "berukir" 0.83; sarko "Diduga" 0.04, "sarkofagus" 1.15,
# "peti" 2.10, "kuno" 3.14; ukuran "panjangnya" 0.54, "seratus" 1.35, "sentimeter" 2.32, "Kok" 3.21, "muat" 3.59;
# lipat "Di" 0.04, "jenazah" 1.60, "dilipat" 2.56, "seperti" 3.49, "bayi" 3.86; wajah "Ukirannya" 0.03, "ternyata" 1.07,
# "mirip" 1.51, "wajah" 1.92
T = {"rise": 0.0, "crack": 0.80, "part": 1.05,
     "sar": 1.12, "dim": 2.08,
     "ruler": 0.5, "r125": 1.33, "body": 2.3, "q": 3.18,
     "fig": 1.55, "fold0": 2.56, "fold1": 3.40, "pl": 3.46,
     "sweep0": 0.0, "sweep1": 1.05, "face": 1.48, "fp": 1.9}

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
STONE = noise((H, W), [(70, 0.35), (16, 0.35), (4, 0.3)], 5)[..., None]
PADAS = np.array([152, 110, 72], np.float32)
SOILN = noise((H, W), [(40, 0.5), (8, 0.5)], 9)[..., None]
TOPSHADE = np.clip((660 - YY) / 380, 0, 1)[..., None] * 0.55          # darker under the titles


def stone(shade):
    return PADAS * (0.68 + 0.52 * STONE) * shade


def poly_mask(pts):
    m = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in pts], fill=255)
    return np.asarray(m.resize((W, H), Image.LANCZOS), np.float32)[..., None] / 255


def line_layer(segs, col, width, k=S):
    """polylines in 1x coordinates on a transparent 1x layer"""
    lay = Image.new("RGBA", (W * k, H * k))
    d = ImageDraw.Draw(lay)
    for pts in segs:
        d.line([(x * k, y * k) for x, y in pts], fill=col, width=int(width * k), joint="curve")
    return lay.resize((W, H), Image.LANCZOS)


# ---------- oblique chest ----------
X0, X1, Y0, Y1, DX, DY = 210, 770, 800, 1040, 120, 92


def chest(face_a=0.25):
    """the whole (unbroken) chest as an RGBA layer; face_a = how much of the knob's face shows"""
    front = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
    top = [(X0, Y0), (X0 + DX, Y0 - DY), (X1 + DX, Y0 - DY), (X1, Y0)]
    side = [(X1, Y0), (X1 + DX, Y0 - DY), (X1 + DX, Y1 - DY), (X1, Y1)]
    mf, mt, ms = poly_mask(front), poly_mask(top), poly_mask(side)
    rgb = stone(1.0) * mf + stone(1.22) * mt + stone(0.74) * ms
    a = np.clip(mf + mt + ms, 0, 1)
    im = Image.fromarray(np.dstack([np.clip(rgb / np.maximum(a, 1e-3), 0, 255), a * 255]).astype(np.uint8), "RGBA")
    dark, hi = (52, 34, 22, 235), (214, 176, 134, 150)
    # lid seam and edges
    seam = Y0 + 62
    im.alpha_composite(line_layer([[(X0, seam), (X1, seam), (X1 + DX, seam - DY)]], dark, 5))
    im.alpha_composite(line_layer([[(X0, Y0), (X1, Y0), (X1 + DX, Y0 - DY)], [(X1, Y0), (X1, Y1)]], hi, 3))
    # carving band: border lines and spiral medallions
    b0, b1 = seam + 26, Y1 - 30
    im.alpha_composite(line_layer([[(X0 + 24, b0), (X1 - 24, b0)], [(X0 + 24, b1), (X1 - 24, b1)]], dark, 4))
    segs, his = [], []
    n = 5
    for k in range(n):
        cx, cy, r = X0 + 24 + (X1 - X0 - 48) * (k + 0.5) / n, (b0 + b1) / 2, (b1 - b0) * 0.36
        sp = [(cx + r * (0.15 + 0.85 * u) * math.cos(6.3 * 2.2 * u + k), cy + r * (0.15 + 0.85 * u) * math.sin(6.3 * 2.2 * u + k))
              for u in np.linspace(0, 1, 60)]
        segs.append(sp)
        his.append([(x - 2, y - 2) for x, y in sp])
        segs.append([(cx + r * 1.15 * math.cos(v), cy + r * 1.15 * math.sin(v)) for v in np.linspace(0, 6.3, 50)])
    im.alpha_composite(line_layer(his, hi, 3))
    im.alpha_composite(line_layer(segs, dark, 4))
    # knob (tonjolan) on the end face with a faint face
    kx, ky = X1 + DX / 2, (Y0 + Y1) / 2 - DY / 2 + 12
    kn = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(kn)
    d.ellipse([(kx - 40) * S, (ky - 56) * S, (kx + 40) * S, (ky + 56) * S], fill=(176, 130, 88, 255), outline=dark, width=4 * S)
    if face_a > 0:
        c = (60, 40, 26, int(255 * face_a))
        d.arc([(kx - 26) * S, (ky - 34) * S, (kx - 4) * S, (ky - 16) * S], 200, 340, fill=c, width=4 * S)
        d.arc([(kx + 4) * S, (ky - 34) * S, (kx + 26) * S, (ky - 16) * S], 200, 340, fill=c, width=4 * S)
        d.ellipse([(kx - 21) * S, (ky - 18) * S, (kx - 9) * S, (ky - 10) * S], outline=c, width=3 * S)
        d.ellipse([(kx + 9) * S, (ky - 18) * S, (kx + 21) * S, (ky - 10) * S], outline=c, width=3 * S)
        d.line([(kx * S, (ky - 8) * S), (kx * S, (ky + 12) * S)], fill=c, width=3 * S)
        d.arc([(kx - 18) * S, (ky + 10) * S, (kx + 18) * S, (ky + 34) * S], 20, 160, fill=c, width=4 * S)
    sh = Image.new("RGBA", kn.size)
    ImageDraw.Draw(sh).ellipse([(kx - 34) * S, (ky - 46) * S, (kx + 52) * S, (ky + 66) * S], fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8 * S)).resize((W, H), Image.LANCZOS))
    im.alpha_composite(kn.resize((W, H), Image.LANCZOS))
    return im


XC = X0 + 0.56 * (X1 - X0)
CRACK = [(XC + DX + 8, Y0 - DY), (XC + DX * 0.62 - 6, Y0 - DY * 0.62 + 4), (XC + DX * 0.3 + 7, Y0 - DY * 0.3), (XC, Y0),
         (XC - 14, Y0 + 40), (XC + 6, Y0 + 82), (XC - 10, Y0 + 128), (XC + 9, Y0 + 170), (XC - 6, Y0 + 210), (XC + 2, Y1)]
CLEN = np.r_[0, np.cumsum([math.dist(a, b) for a, b in zip(CRACK, CRACK[1:])])]
LEFT = poly_mask([(-20, -20), (CRACK[0][0], -20)] + CRACK + [(CRACK[-1][0], H + 20), (-20, H + 20)])


def crack_path(u):
    L = CLEN[-1] * u
    pts = [CRACK[0]]
    for (a, b), l0, l1 in zip(zip(CRACK, CRACK[1:]), CLEN, CLEN[1:]):
        if L >= l1:
            pts.append(b)
        elif L > l0:
            q = (L - l0) / (l1 - l0)
            pts.append((a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q))
            break
    return pts


def broken(base, u, gap):
    """the chest with the crack drawn to fraction u and the halves moved gap px apart"""
    a = np.asarray(base, np.float32)
    lft = Image.fromarray((a * np.concatenate([LEFT] * 4, -1)).astype(np.uint8), "RGBA")
    rgt = Image.fromarray((a * np.concatenate([1 - LEFT] * 4, -1)).astype(np.uint8), "RGBA")
    out = Image.new("RGBA", (W, H))
    g = round(gap)
    if gap > 0.5:
        filler = line_layer([CRACK], (22, 15, 10, 255), 4 + 2 * gap)
        out.alpha_composite(filler)
    out.alpha_composite(lft, (-g, 0))
    out.alpha_composite(rgt, (g, 2 if g else 0))
    if u > 0:
        out.alpha_composite(line_layer([crack_path(u)], (24, 16, 10, 255), 5))
    return out


def ground_bg():
    sky = np.array([20, 18, 20], np.float32) * (1 - YY / H)[..., None] + np.array([58, 42, 30], np.float32) * (YY / H)[..., None]
    soil = np.array([96, 66, 42], np.float32) * (0.55 + 0.6 * SOILN) * (1 - 0.25 * ((YY - Y1) % 46 < 4)[..., None])
    a = np.where((YY >= Y1 - 2)[..., None], soil, sky) * (1 - TOPSHADE)
    return to_img(a).convert("RGBA")


def soil_layer():
    bg = np.asarray(ground_bg(), np.float32)
    al = np.clip((YY - (Y1 - 3)) / 3, 0, 1) * 255
    return Image.fromarray(np.dstack([bg[..., :3], al]).astype(np.uint8), "RGBA")


def skema_peti(times=None):
    bg, soil, base = ground_bg(), soil_layer(), chest(0.0)
    frames = []
    for i in range(N["peti"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        oy = 300 * (1 - ease((t - T["rise"]) / 0.45))
        u = ramp(t, T["crack"], T["crack"] + 0.22)
        gap = 7 * ease((t - T["part"]) / 0.2)
        shake = 4 * math.sin(t * 70) * (1 - ramp(t, T["crack"] + 0.2, T["crack"] + 0.45)) if t > T["crack"] else 0
        im = bg.copy()
        im.alpha_composite(broken(base, u, gap), (round(shake), round(oy)))
        im.alpha_composite(soil)
        frames.append(im.convert("RGB"))
    return frames


def skema_sarko(times=None):
    bg, soil = ground_bg(), soil_layer()
    scene = bg.copy()
    scene.alpha_composite(broken(chest(0.0), 1.0, 7))
    scene.alpha_composite(soil)
    scene = scene.convert("RGB")
    p1 = pill("DIDUGA KUAT SARKOFAGUS", 40, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220), pad=(26, 14))
    src = pill("tinjauan Disbudpar Karangasem, 19 Nov 2026", 24, col=(235, 228, 215), bg=(0, 0, 0, 150), edge=(255, 255, 255, 60))
    p2 = pill("±125 × 90 × 60 cm · patah dua", 32, col=WHITE, bg=(20, 14, 10, 215), edge=(255, 255, 255, 140))
    frames = []
    for i in range(N["sarko"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = push(scene, t, N["sarko"] / FPS, 1.0, 1.05, cy=900).convert("RGBA")
        if t > T["sar"]:
            put1(im, p1, 540, 1104, scale=min(pop(t, T["sar"], 0.3), 1.06))
            put1(im, src, 540, 1172, a=ramp(t, T["sar"] + 0.25, T["sar"] + 0.45))
        if t > T["dim"]:
            put1(im, p2, 540, 676, scale=min(pop(t, T["dim"], 0.3), 1.06))
        frames.append(im.convert("RGB"))
    return frames


# ---------- side view: ruler and a lying adult ----------
PXCM = 4.0
SX0, SY1 = 190, 1040
SX1, SY0 = SX0 + 125 * PXCM, SY1 - 60 * PXCM


def side_chest():
    im = Image.new("RGBA", (W, H))
    m = poly_mask([(SX0, SY0), (SX1, SY0), (SX1, SY1), (SX0, SY1)])
    rgb = stone(1.0)
    im = Image.fromarray(np.dstack([rgb, m * 255]).astype(np.uint8), "RGBA")
    im.alpha_composite(line_layer([[(SX0, SY0 + 58), (SX1, SY0 + 58)]], (52, 34, 22, 235), 5))
    im.alpha_composite(line_layer([[(SX0, SY0), (SX1, SY0)]], (214, 176, 134, 150), 3))
    return im


def lying_body(x0, length, cy, fill, outline):
    """a person lying on the back, seen from the side, as a soft silhouette (2x layer -> 1x)"""
    k = length / 165.0
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    X = lambda cm: (x0 + cm * k) * S
    Y = lambda off: (cy + off * k) * S
    d.ellipse([X(0), Y(-11), X(22), Y(11)], fill=fill, outline=outline, width=3 * S)                  # head
    d.rounded_rectangle([X(19), Y(-5), X(30), Y(5)], radius=3 * S, fill=fill)                            # neck
    d.rounded_rectangle([X(27), Y(-15), X(90), Y(13)], radius=int(12 * k * S), fill=fill, outline=outline, width=3 * S)  # torso
    d.rounded_rectangle([X(86), Y(-9), X(161), Y(8)], radius=int(7 * k * S), fill=fill, outline=outline, width=3 * S)    # legs
    d.polygon([(X(156), Y(-9)), (X(165), Y(-20)), (X(168), Y(-15)), (X(162), Y(8))], fill=fill)                         # feet
    return lay.resize((W, H), Image.LANCZOS)


def skema_ukuran(times=None):
    bg = ground_bg()
    soil = soil_layer()
    base = bg.copy()
    base.alpha_composite(side_chest())
    base.alpha_composite(soil)
    body = lying_body(SX0 + 6, 165 * PXCM, SY0 + 120, (236, 226, 208, 210), (255, 255, 255, 255))
    ba = np.asarray(body, np.float32)
    over = (XX > SX1)[..., None]
    tint = np.where(over, np.array([232, 44, 40, 255], np.float32) * np.array([1, 1, 1, 0.0]) + ba * np.array([0, 0, 0, 1]), ba)
    body_red = Image.fromarray(tint.astype(np.uint8), "RGBA")
    r125 = pill("125 cm", 40, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220), pad=(24, 12))
    r165 = pill("orang dewasa ±165 cm", 30, col=WHITE, bg=(150, 26, 22, 235), edge=(255, 255, 255, 160))
    qf = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 190 * S)
    q = Image.new("RGBA", (220 * S, 260 * S))
    dq = ImageDraw.Draw(q)
    x0, y0, x1, y1 = qf.getbbox("?")
    for off, c in ((6 * S, (0, 0, 0, 160)), (0, YELLOW + (255,))):
        dq.text((110 * S - (x0 + x1) / 2 + off, 130 * S - (y0 + y1) / 2 + off), "?", font=qf, fill=c)
    frames = []
    for i in range(N["ukuran"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        u = ramp(t, T["ruler"], T["ruler"] + 0.5)
        if u > 0:
            ry = SY0 - 44
            xe = SX0 + (SX1 - SX0) * u
            segs = [[(SX0, ry), (xe, ry)], [(SX0, ry - 16), (SX0, ry + 16)]]
            if u >= 1:
                segs.append([(SX1, ry - 16), (SX1, ry + 16)])
            im.alpha_composite(line_layer(segs, YELLOW + (255,), 5))
        if t > T["r125"]:
            put1(im, r125, (SX0 + SX1) / 2, SY0 - 100, scale=min(pop(t, T["r125"], 0.3), 1.06))
        if t > T["body"]:
            kk = ease((t - T["body"]) / 0.35)
            bl = body_red if t > T["body"] + 0.35 else body
            lay = Image.new("RGBA", (W, H))
            lay.alpha_composite(bl, (round(-220 * (1 - kk)), 0))
            lay.putalpha(lay.getchannel("A").point(lambda v, q=ramp(t, T["body"], T["body"] + 0.2): int(v * q)))
            im.alpha_composite(lay)
            put1(im, r165, 540, 1120, a=ramp(t, T["body"] + 0.3, T["body"] + 0.5))
        if t > T["q"]:
            sc = min(pop(t, T["q"], 0.3), 1.08) * (1 + 0.05 * math.sin((t - T["q"]) * 9))
            put1(im, q, 905, SY0 - 120, scale=sc)
        frames.append(im.convert("RGB"))
    return frames


# ---------- cross-section and folding figure ----------
CX0, CX1, CY0, CY1, WALL = 200, 880, 735, 1050, 30
IX0, IX1, IY0, IY1 = CX0 + WALL, CX1 - WALL, CY0 + 52, CY1 - WALL
KP = 5.0  # px per body cm, straight pose
POSE_A = {"head": (118 + 11 * KP, 905), "sh": (118 + 26 * KP, 905), "hip": (118 + 85 * KP, 905), "knee": (118 + 125 * KP, 905),
          "ank": (118 + 158 * KP, 905), "toe": (118 + 165 * KP, 893), "elb": (118 + 55 * KP, 895), "hand": (118 + 84 * KP, 895)}
POSE_B = {"head": (362, 948), "sh": (432, 893), "hip": (700, 890), "knee": (522, 975), "ank": (696, 988), "toe": (736, 982),
          "elb": (500, 988), "hand": (604, 978)}   # crouched: back on top, knees drawn up under the chest, head bowed


def figure(u):
    p = {k: (POSE_A[k][0] + (POSE_B[k][0] - POSE_A[k][0]) * u, POSE_A[k][1] + (POSE_B[k][1] - POSE_A[k][1]) * u) for k in POSE_A}
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    col = (246, 232, 204, 225)
    P = lambda k: (p[k][0] * S, p[k][1] * S)

    edge = (150, 118, 84, 255)

    def limb(a, b, w):
        for c, ww in ((edge, w + 7), (col, w)):   # a thin darker rim keeps overlapping limbs apart
            d.line([P(a), P(b)], fill=c, width=int(ww * S))
            for q in (a, b):
                d.ellipse([P(q)[0] - ww * S / 2, P(q)[1] - ww * S / 2, P(q)[0] + ww * S / 2, P(q)[1] + ww * S / 2], fill=c)
    limb("ank", "toe", 22)
    limb("knee", "ank", 34)
    limb("hip", "knee", 44)
    limb("sh", "hip", 70)
    limb("head", "sh", 30)
    hx, hy = P("head")
    for c, r in ((edge, 58), (col, 54)):
        d.ellipse([hx - r * S, hy - r * S, hx + r * S, hy + r * S], fill=c)
    limb("sh", "elb", 28)
    limb("elb", "hand", 24)
    return lay.resize((W, H), Image.LANCZOS)


def skema_lipat(times=None):
    bgc = np.array([64, 44, 24], np.float32) * (1 - 0.5 * np.clip(np.hypot(XX - 540, YY - 900) / 900, 0, 1))[..., None]
    bg = to_img(bgc * (1 - TOPSHADE)).convert("RGBA")
    shell = Image.fromarray(np.dstack([stone(1.0), poly_mask([(CX0, CY0), (CX1, CY0), (CX1, CY1), (CX0, CY1)])[..., 0] * 255]).astype(np.uint8), "RGBA")
    inner = poly_mask([(IX0, IY0), (IX1, IY0), (IX1, IY1), (IX0, IY1)])
    sh = np.asarray(shell, np.float32)
    sh[..., :3] = sh[..., :3] * (1 - inner) + np.array([30, 21, 15], np.float32) * inner
    shell = Image.fromarray(sh.astype(np.uint8), "RGBA")
    shell.alpha_composite(line_layer([[(CX0, CY0 + 52), (CX1, CY0 + 52)]], (52, 34, 22, 235), 5))
    shell.alpha_composite(line_layer([[(CX0, CY0), (CX1, CY0)]], (214, 176, 134, 150), 3))
    glow = Image.new("RGBA", (W, H))
    ImageDraw.Draw(glow).ellipse([360, 760, 760, 1040], fill=(255, 200, 90, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    pl = pill("sarkofagus kecil: jenazah terlipat", 32, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220))
    src = pill("Soejono; Arisanti & Sunarya 2020 (BRIN)", 24, col=(235, 228, 215), bg=(0, 0, 0, 150), edge=(255, 255, 255, 60))
    lbl = pill("±125 cm", 28, col=WHITE, bg=(20, 14, 10, 200), edge=(255, 255, 255, 120))
    frames = []
    for i in range(N["lipat"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = push(bg.convert("RGB"), t, N["lipat"] / FPS, 1.0, 1.03).convert("RGBA")
        g = ramp(t, T["fold1"] - 0.2, T["fold1"] + 0.3)
        if g > 0:
            gl = glow.copy()
            gl.putalpha(gl.getchannel("A").point(lambda v, q=g: int(v * q)))
            im.alpha_composite(gl)
        im.alpha_composite(shell)
        put1(im, lbl, (CX0 + CX1) / 2, CY0 - 40, a=ramp(t, 0.1, 0.3) * (1 - ramp(t, T["fig"], T["fig"] + 0.2)))
        if t > T["fig"]:
            u = ease((t - T["fold0"]) / (T["fold1"] - T["fold0"]))
            fg = np.asarray(figure(u), np.float32)
            out = ((XX < IX0 - 4) | (XX > IX1 + 4))[..., None] * (1 - u)
            fg[..., :3] = fg[..., :3] * (1 - out) + np.array(RED, np.float32) * out
            fg[..., 3] *= ramp(t, T["fig"], T["fig"] + 0.25)
            im.alpha_composite(Image.fromarray(fg.astype(np.uint8), "RGBA"))
        if t > T["pl"]:
            put1(im, pl, 540, 1112, scale=min(pop(t, T["pl"], 0.3), 1.06))
            put1(im, src, 540, 1176, a=ramp(t, T["pl"] + 0.25, T["pl"] + 0.45))
        frames.append(im.convert("RGB"))
    return frames


# ---------- the face on the knob, by torchlight ----------
KX, KY, KW, KH = 540, 830, 230, 250


def face_layer(col, w):
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    B = lambda x0, y0, x1, y1: [(KX + x0) * S, (KY + y0) * S, (KX + x1) * S, (KY + y1) * S]
    d.arc(B(-160, -136, -26, -54), 200, 340, fill=col, width=w * S)                       # brows
    d.arc(B(26, -136, 160, -54), 200, 340, fill=col, width=w * S)
    for sx in (-1, 1):                                                                       # almond eyes with round pupils
        cx = 90 * sx
        d.arc(B(cx - 54, -84, cx + 54, -10), 195, 345, fill=col, width=w * S)
        d.arc(B(cx - 54, -64, cx + 54, 8), 15, 165, fill=col, width=w * S)
        d.ellipse(B(cx - 15, -52, cx + 15, -22), fill=col)
    d.line([((KX - 10) * S, (KY - 30) * S), ((KX - 26) * S, (KY + 44) * S)], fill=col, width=w * S)   # broad nose
    d.line([((KX + 10) * S, (KY - 30) * S), ((KX + 26) * S, (KY + 44) * S)], fill=col, width=w * S)
    d.arc(B(-44, 26, 44, 70), 10, 170, fill=col, width=w * S)
    d.arc(B(-86, 92, 86, 140), 195, 345, fill=col, width=w * S)                            # closed lips
    d.arc(B(-74, 106, 74, 162), 15, 165, fill=col, width=w * S)
    d.line([((KX - 84) * S, (KY + 122) * S), ((KX + 84) * S, (KY + 122) * S)], fill=col, width=max(2, w - 3) * S)
    d.arc(B(-206, -200, 206, 214), 150, 390, fill=col, width=max(2, w - 4) * S)           # face outline on the knob
    return lay.resize((W, H), Image.LANCZOS)


def skema_wajah(times=None):
    wall = stone(0.62)
    knob = poly_mask([(KX + KW * math.cos(v), KY + KH * math.sin(v)) for v in np.linspace(0, 6.283, 90)])
    sh = np.clip(1 - np.hypot((XX - KX - 26) / (KW + 40), (YY - KY - 34) / (KH + 40)), 0, 1)[..., None]
    rgb = wall * (1 - 0.55 * sh * (1 - knob)) * (1 - knob) + stone(1.05) * knob
    rim = np.clip(1 - np.abs(np.hypot((XX - KX) / KW, (YY - KY) / KH) - 0.97) / 0.03, 0, 1)[..., None]
    rgb = rgb * (1 - 0.5 * rim)
    groove = face_layer((40, 26, 16, 255), 9)
    hi = face_layer((226, 190, 146, 170), 4)
    base = to_img(rgb).convert("RGBA")
    base.alpha_composite(hi, (-3, -3))
    base.alpha_composite(groove)
    base = np.asarray(base.convert("RGB"), np.float32)
    glowf = face_layer(YELLOW + (255,), 9).filter(ImageFilter.GaussianBlur(6))
    linef = face_layer(YELLOW + (255,), 5)
    pl = pill("ukiran mirip wajah manusia", 36, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220))
    src = pill("tinjauan Disbudpar Karangasem, 19 Nov · bentuk asli belum dipublikasikan", 21, col=(235, 228, 215),
               bg=(0, 0, 0, 160), edge=(255, 255, 255, 60))
    frames = []
    for i in range(N["wajah"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        u = ease((t - T["sweep0"]) / (T["sweep1"] - T["sweep0"]))
        lx, ly = 120 + (KX - 120) * u, 640 + (KY - 640) * u
        rad = 250 + 120 * ramp(t, T["face"], T["face"] + 0.4)
        spot = np.exp(-((XX - lx) ** 2 + (YY - ly) ** 2) / (2 * rad ** 2))[..., None]
        amb = 0.10 + 0.35 * ramp(t, T["face"], T["face"] + 0.5)
        light = amb + 0.95 * spot
        a = base * light * np.array([1.0, 0.93, 0.8], np.float32) * (1 - TOPSHADE)
        im = to_img(a).convert("RGBA")
        f = ramp(t, T["face"], T["face"] + 0.3)
        if f > 0:
            for lay, q in ((glowf, 0.8 * f * (0.85 + 0.15 * math.sin((t - T["face"]) * 8))), (linef, f)):
                l2 = lay.copy()
                l2.putalpha(l2.getchannel("A").point(lambda v, q=q: int(v * q)))
                im.alpha_composite(l2)
        if t > T["fp"]:
            put1(im, pl, 540, 1112, scale=min(pop(t, T["fp"], 0.3), 1.06))
            put1(im, src, 540, 1176, a=ramp(t, T["fp"] + 0.25, T["fp"] + 0.45))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"peti": skema_peti, "sarko": skema_sarko, "ukuran": skema_ukuran, "lipat": skema_lipat, "wajah": skema_wajah}

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
