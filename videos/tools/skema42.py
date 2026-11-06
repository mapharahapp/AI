"""Stills and schematic animations for Titik Heran #42 (run in the episode work dir after
`dl.py i:2503865 v:89527 v:197525 i:3895160 v:145647`; writes img/hook42v.jpg, img/hook42c.jpg, clips/skema_cincin.mp4
and clips/skema_kode.mp4).
Pixabay + skema only (Arif, 2026-11-06, "supaya lebih aman"): the first cut (commit 274ca6f) showed the museum's collection
photos of the real lock; this version draws the lock instead. The hook stills use Pixabay photo 2503865, an antique brass
padlock the photographer cut out (labelled "ilustrasi"). The drawn lock follows the museum record of the Ann Francis lock
(Amgueddfa Cymru - Museum Wales, object 2025.17H/2.6): a cylinder of four turning letter rings between two lettered end
plates, the letters of each ring as the record lists them (D H B A X M / F V T Q X N / C O Z L R F with Z = ezh /
I G K O E S), so A N C E really sit on rings 1-4; 31,8 mm from the shackle top to the cylinder bottom.
usage: python3 skema42.py [prep|cincin|kode ...] [--sheet out.jpg t1,t2,...]
prep: img/hook42v.jpg (the brass padlock on a dark ground under the hook title, with a soft reflection) and
  img/hook42c.jpg (closer, the keyhole near the frame centre, for "dipecahkan").
skema_cincin: the drawn brass lock; the rings are outlined and numbered one by one ("cincin"), spun ("diputar") and stop
  on wrong letters while the camera pulls back ("tapi"); on "gagal" the shackle tugs but stays, the frame shakes, a red
  TETAP TERKUNCI stamp lands and a 3,2 cm dimension line appears.
skema_kode: the same lock turned into a cyan X-ray look by a sweeping line, with the notch inside each ring and the gate
  line; on each spelled letter its ring turns from the wrong letter to the code letter, the notch meets the gate line and
  the letter lights gold (A N C E on rings 1-4); after "E" the shackle lifts.
Event times are seconds from the start of each clip, read off `render.py 42 plan`: skema_cincin starts at 12,93 ("cincin"
0,37, "diputar" 1,80, "tapi" 2,97, "gagal" 4,49), skema_kode at 21,47 ("dan" 0,05, "A" 1,51, "En" 2,36, "Ce" 2,94,
"E" 3,51).
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, text_sprite, encode
from skema27 import stamp_sprite
from skema35 import sheet
from skema37 import to_img, put1
from skema39 import title_shade

N = {"cincin": 179, "kode": 131}  # each clip runs ~0,3 s past its shot
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
SERIF = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"  # has the ezh (U+01B7) inside the cap height
GOLD = (255, 205, 70)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

EZH = "Ʒ"
RINGS = ["DHBAXM", "FVTQXN", "CO" + EZH + "LRF", "IGKOES"]  # museum record, ring 1 (left) to ring 4
PLATES = ["PE" + EZH + "DA", "ROGCB"]                          # the two fixed end plates
CODE = "ANCE"
START = "BF" + EZH + "G"  # front letters when the clip opens
TRIED = "XTRO"            # where the rings stop after the failed try (any wrong letters)


def wanted(i, times):
    return times is None or any(abs(i / FPS - x) < 0.5 / FPS for x in times)


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


# ---------- prep: the two hook stills (Pixabay 2503865) ----------
def dark_ground(cy=930, warm=True):
    base = np.array([13, 10, 8] if warm else [8, 12, 22], np.float32)
    spot = np.array([62, 44, 26] if warm else [26, 40, 70], np.float32)
    g = np.exp(-((XX - 540) ** 2 + (YY - cy) ** 2) / (2 * 430.0 ** 2))
    v = 1 - 0.35 * np.clip((np.hypot(XX - 540, YY - 960) - 520) / 900, 0, 1)
    return (base + spot * g[..., None]) * v[..., None]


def place_lock(bg, scale, x0, y0, reflect=True):
    lk = Image.open("img/2503865.jpg").convert("RGBA")
    lk = lk.resize((round(lk.width * scale), round(lk.height * scale)), Image.LANCZOS)
    im = to_img(bg).convert("RGBA")
    a = lk.getchannel("A")
    sh = Image.new("RGBA", lk.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * 0.6)))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    im.paste(sh, (x0 + 12, y0 + 18), sh)
    if reflect:  # a dim reflection on the shelf below
        rf = lk.transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(2))
        fade = np.clip(1 - np.arange(rf.height) / 230.0, 0, 1) ** 1.6 * 0.22
        ra = np.asarray(rf.getchannel("A"), np.float32) * fade[:, None]
        rf.putalpha(Image.fromarray(ra.astype(np.uint8)))
        im.paste(rf, (x0, y0 + lk.height - 6), rf)
    im.paste(lk, (x0, y0), lk)
    return im.convert("RGB")


def prep():
    s = 0.53  # 449 x 678: the lock from y 612 (under the two-line title and the KARAM 1583 label) to 1290
    out = place_lock(dark_ground(930), s, 540 - round(848 * s / 2), 612)
    out.save("img/hook42v.jpg", quality=95)
    print("img/hook42v.jpg")
    s = 1.22  # closer: the keyhole (photo ~412,880) near the frame centre, the body under the three-line title
    out = place_lock(dark_ground(1000), s, 540 - round(412 * s), 1000 - round(880 * s), reflect=False)
    out.save("img/hook42c.jpg", quality=95)
    print("img/hook42c.jpg")


# ---------- the drawn lock, on its own canvas ----------
# proportions of the real lock (museum photo, front view): the cylinder is ~1,6x as long as it is thick, and the shackle
# rises ~1,2 cylinder diameters above it
CW, CH = 800, 1120          # canvas, drawn at the "close" size
OX, OY = 400, 820           # the cylinder axis centre on the canvas
R, RP, RC = 210.0, 220.0, 182.0   # ring radius, end-plate radius (a small flange), the core seen in the grooves
SEG = [(-356, -244, "p"), (-236, -124, "r"), (-116, -4, "r"), (4, 116, "r"), (124, 236, "r"), (244, 356, "p")]
RING_X = [((x0 + x1) / 2, x0, x1) for x0, x1, k in SEG if k == "r"]
HW, YT, RCORN, TH, YB = 300.0, -678.0, 150.0, 32.0, -150.0  # shackle: legs at x +-300, top centreline, corner, half thickness
R_IN = 130.0                # the bore: notches and the gate line sit at y = -R_IN
FS, FSP, LW = 122, 104, 96  # ring and plate letter sizes, the widest a ring letter may be
LV = np.array([-0.35, -0.65, 0.68], np.float32)
LV /= np.linalg.norm(LV)
HV = LV + np.array([0, 0, 1], np.float32)
HV /= np.linalg.norm(HV)
BRASS = np.array([206, 150, 64], np.float32) / 255
SPEC = np.array([255, 242, 205], np.float32)
CY, CX = np.mgrid[0:CH, 0:CW].astype(np.float32)
YC, XC = CY - OY, CX - OX
_LOCK = {}


def noise(shape, cell, seed):
    rng = np.random.default_rng(seed)
    g = rng.random((shape[0] // cell + 2, shape[1] // cell + 2))
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((shape[1] + 2 * cell, shape[0] + 2 * cell), Image.BICUBIC)
    return np.asarray(im, np.float32)[cell:cell + shape[0], cell:cell + shape[1]] / 255


def rrect_alpha(x0, x1, r, rr=10.0):
    """anti-aliased rounded rectangle [x0, x1] x [-r, r] around the axis"""
    xm, hw = (x0 + x1) / 2, (x1 - x0) / 2
    qx, qy = np.abs(XC - xm) - (hw - rr), np.abs(YC) - (r - rr)
    d = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - rr
    return np.clip(0.5 - d, 0, 1)


def cyl_shade(r):
    s = np.clip(YC / r, -1, 1)
    c = np.sqrt(1 - s * s)
    diff = np.clip(LV[1] * s + LV[2] * c, 0, None)
    spec = np.clip(HV[1] * s + HV[2] * c, 0, None) ** 40
    return 0.2 + 0.95 * diff, spec


def letter_mask(ch, size):
    key = (ch, size)
    if key not in _LOCK:
        f = ImageFont.truetype(SERIF, size)
        x0, y0, x1, y1 = f.getbbox(ch)
        im = Image.new("L", (x1 - x0 + 8, y1 - y0 + 8), 0)
        ImageDraw.Draw(im).text((4 - x0, 4 - y0), ch, font=f, fill=255)
        _LOCK[key] = np.asarray(im, np.float32) / 255
    return _LOCK[key]


def stamp_letter(L, ch, size, xc, yc, q, maxw=LW):
    """a letter mask squashed to q of its height (and to maxw px wide), centred at canvas-axis (xc, yc), max-ed into L"""
    if q < 0.06:
        return
    m = letter_mask(ch, size)
    h = max(1, round(m.shape[0] * q))
    w = min(m.shape[1], maxw + 8)
    mm = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32) / 255
    m = mm
    x0, y0 = round(OX + xc - m.shape[1] / 2), round(OY + yc - h / 2)
    ys, xs = max(0, -y0), max(0, -x0)
    y1, x1 = min(CH, y0 + h), min(CW, x0 + m.shape[1])
    if y1 <= y0 + ys or x1 <= x0 + xs:
        return
    sub = L[y0 + ys:y1, x0 + xs:x1]
    np.maximum(sub, mm[ys:ys + sub.shape[0], xs:xs + sub.shape[1]], out=sub)


def ring_letters(L, k, theta, size=FS, clip=None):
    """the letters of ring k turned by theta degrees (0 = its first letter at the front line)"""
    xm, x0, x1 = RING_X[k]
    n = len(RINGS[k])
    for j, ch in enumerate(RINGS[k]):
        ph = math.radians(theta + j * 360 / n)
        ph = (ph + math.pi) % (2 * math.pi) - math.pi
        if abs(ph) < math.radians(84):
            stamp_letter(L, ch, size, xm, R * math.sin(ph), math.cos(ph))
    if clip is not None:  # keep the letters on their own ring
        L[:, :OX + int(x0) + 3] *= clip[0]
        L[:, OX + int(x1) - 3:] *= clip[1]


def build_lock():
    """static parts: the cylinder albedo/shading/alpha with the end-plate letters, the shackle layer, the shadow"""
    if "base" in _LOCK:
        return _LOCK
    nz = 1 + 0.07 * (noise((CH, CW), 24, 7) - 0.5) + 0.05 * (noise((CH, CW), 5, 8) - 0.5)
    alb = np.zeros((CH, CW, 3), np.float32)
    shade = np.zeros((CH, CW), np.float32)
    spec = np.zeros((CH, CW), np.float32)
    alpha = np.zeros((CH, CW), np.float32)
    # the core seen through the grooves
    a_core = rrect_alpha(-430, 430, RC, 8)
    sh_c, sp_c = cyl_shade(RC)
    alb += (BRASS * 0.38)[None, None, :] * a_core[..., None]
    shade += sh_c * a_core
    spec += sp_c * 0.3 * a_core
    alpha = np.maximum(alpha, a_core)
    sh_r, sp_r = cyl_shade(R)
    sh_p, sp_p = cyl_shade(RP)
    for x0, x1, kind in SEG:
        r = RP if kind == "p" else R
        a = rrect_alpha(x0, x1, r)
        edge = np.clip(np.minimum(XC - x0, x1 - XC) / 7, 0, 1) ** 0.6  # the rim of each ring catches less light
        lit = np.where(XC - x0 < 3, 1.18, 1.0)                           # a thin highlight on its left edge
        sh = (sh_p if kind == "p" else sh_r) * (0.72 + 0.28 * edge) * lit
        sp = (sp_p if kind == "p" else sp_r) * edge
        tone = BRASS * (0.94 if kind == "p" else 1.0)
        alb = alb * (1 - a[..., None]) + tone[None, None, :] * a[..., None]
        shade = shade * (1 - a) + sh * a
        spec = spec * (1 - a) + sp * a
        alpha = np.maximum(alpha, a)
    alb *= nz[..., None]
    # the fixed letters of the end plates, engraved
    L = np.zeros((CH, CW), np.float32)
    for (x0, x1, kind), letters in zip([SEG[0], SEG[-1]], PLATES):
        xm = (x0 + x1) / 2
        for j, ch in enumerate(letters):
            ph = math.radians(j * 72 - 8)
            if abs(ph) < math.radians(84):
                stamp_letter(L, ch, FSP, xm, RP * math.sin(ph), math.cos(ph))
    alb, spec = engrave(alb, spec, L)
    # the shackle: a round bar bent like a rounded rectangle, its legs running into the end plates
    ax = np.abs(XC)
    cx, cy = HW - RCORN, YT + RCORN
    d = np.zeros_like(XC)
    nx = np.zeros_like(XC)
    ny = np.zeros_like(XC)
    leg = YC >= cy
    top = (~leg) & (ax <= cx)
    cor = (~leg) & (ax > cx)
    d[leg], nx[leg] = ax[leg] - HW, np.sign(XC[leg])
    d[top], ny[top] = YT - YC[top], -1
    vx, vy = ax[cor] - cx, YC[cor] - cy
    ln = np.hypot(vx, vy) + 1e-6
    d[cor], nx[cor], ny[cor] = ln - RCORN, np.sign(XC[cor]) * vx / ln, vy / ln
    sa = np.clip(TH + 0.5 - np.abs(d), 0, 1) * (YC <= YB)
    p = np.clip(d / TH, -1, 1)
    nz3 = np.sqrt(np.clip(1 - p * p, 0, 1))
    ndl = p * nx * LV[0] + p * ny * LV[1] + nz3 * LV[2]
    ndh = p * nx * HV[0] + p * ny * HV[1] + nz3 * HV[2]
    s_rgb = (BRASS * 0.92)[None, None, :] * nz[..., None] * (0.2 + 0.95 * np.clip(ndl, 0, None))[..., None] * 255
    s_rgb = s_rgb + np.clip(ndh, 0, None)[..., None] ** 40 * SPEC * 0.6
    # the shadow on the ground under the cylinder
    shad = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(shad).ellipse([OX - 390, OY + RP + 24, OX + 390, OY + RP + 84], fill=150)
    shad = np.asarray(shad.filter(ImageFilter.GaussianBlur(24)), np.float32) / 255
    _LOCK.update(base=(alb, shade, spec, alpha), shackle=(s_rgb, sa), shadow=shad)
    return _LOCK


def engrave(alb, spec, L):
    """letters cut into the brass: dark inside, a thin lit lip under each stroke, no shine"""
    lip = np.clip(np.roll(L, 2, axis=0) - L, 0, 1)
    alb = alb * (1 - 0.74 * L[..., None]) + 0.16 * lip[..., None]
    return alb, spec * (1 - 0.85 * L)


def vblur(a, r):
    """vertical box blur of a 2-D array by radius r (as if the ring spins)"""
    r = int(r)
    if r < 1:
        return a
    p = np.pad(a, ((r + 1, r), (0, 0)), mode="edge")
    cs = np.cumsum(p, axis=0)
    return (cs[2 * r + 1:] - cs[:-2 * r - 1]) / (2 * r + 1)


def lock_canvas(thetas, blurs, lift=0.0, gold=None):
    """the lock as RGBA float arrays (rgb 0-255, alpha 0-1) on the canvas; thetas = ring angles in degrees"""
    lk = build_lock()
    alb, shade, spec, alpha = lk["base"]
    L = np.zeros((CH, CW), np.float32)
    for k in range(4):
        Lk = np.zeros((CH, CW), np.float32)
        ring_letters(Lk, k, thetas[k])
        xm, x0, x1 = RING_X[k]
        c0, c1 = OX + int(x0), OX + int(x1)
        strip = Lk[:, c0:c1]
        if blurs[k] >= 1:
            strip = vblur(strip, blurs[k]) * 1.0
        ry0, ry1 = int(OY - R + 4), int(OY + R - 4)
        L[ry0:ry1, c0:c1] = np.maximum(L[ry0:ry1, c0:c1], strip[ry0:ry1])
    a2, sp2 = engrave(alb, spec, L)
    rgb = a2 * shade[..., None] * 255 + sp2[..., None] * SPEC * 0.55
    # the shackle behind the cylinder, lifted by `lift` px
    s_rgb, sa = lk["shackle"]
    dy = int(round(lift))
    if dy:
        s_rgb = np.roll(s_rgb, -dy, axis=0)
        sa = np.roll(sa, -dy, axis=0)
    out = s_rgb * sa[..., None] * (1 - alpha[..., None]) + rgb * alpha[..., None]
    al = np.maximum(alpha, sa)
    out = out / np.maximum(al, 1e-4)[..., None]
    if gold is not None:  # front letters that found the code glow gold
        g = np.zeros((CH, CW), np.float32)
        for k in gold:
            stamp_letter(g, CODE[k], FS, RING_X[k][0], 0.0, 1.0)
        gb = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)), np.float32) / 255
        out = out * (1 - g[..., None]) + np.array(GOLD, np.float32) * g[..., None]
        out = out + gb[..., None] * np.array([255, 190, 60], np.float32) * 0.55
    return out, al, L


def place(frame, rgb, al, sc, fx, fy, shadow=True):
    """composite a canvas (rgb, alpha) scaled by sc with its axis centre at frame (fx, fy)"""
    w, h = round(CW * sc), round(CH * sc)
    x0, y0 = round(fx - OX * sc), round(fy - OY * sc)
    if shadow:
        sh = Image.fromarray((build_lock()["shadow"] * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
        frame = paste_alpha(frame, np.zeros((h, w, 3), np.float32), np.asarray(sh, np.float32) / 255 * 0.8, x0, y0)
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    am = Image.fromarray((np.clip(al, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    return paste_alpha(frame, np.asarray(im, np.float32), np.asarray(am, np.float32) / 255, x0, y0)


def paste_alpha(frame, rgb, a, x0, y0):
    h, w = a.shape
    fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0:
        return frame
    sub = frame[fy0:fy1, fx0:fx1]
    aa = a[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0, None]
    sub[:] = sub * (1 - aa) + rgb[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] * aa
    return frame


def navy_ground():
    g = np.exp(-((XX - 540) ** 2 + (YY - 1020) ** 2) / (2 * 520.0 ** 2))
    a = np.array([8, 14, 30], np.float32) + np.array([26, 42, 74], np.float32) * g[..., None]
    grid = ((XX % 60 < 1.5) | (YY % 60 < 1.5)).astype(np.float32) * 0.06
    return a + grid[..., None] * np.array([150, 190, 255], np.float32)


def to_frame(x, y, sc, fx, fy):
    """canvas-axis coordinates (relative to the cylinder centre) to frame coordinates"""
    return fx + x * sc, fy + y * sc


def number_badge(n):
    f = ImageFont.truetype(XB, 40 * S)
    sp = Image.new("RGBA", (84 * S, 84 * S))
    d = ImageDraw.Draw(sp)
    d.ellipse([4 * S, 4 * S, 80 * S, 80 * S], fill=(16, 22, 40, 225), outline=YELLOW + (255,), width=4 * S)
    d.text((42 * S, 43 * S), str(n), font=f, fill=YELLOW + (255,), anchor="mm")
    return sp


# ring angles: theta puts letter j at the front when theta = -60 j
def front(k, ch):
    return -RINGS[k].index(ch) * 360 / len(RINGS[k])


_U = np.linspace(0, 1, 2001)
_SPD = np.minimum(_U / 0.12, 1.0) ** 2 * (1 - _U) ** 1.4  # a hand spin: quick start, long slow-down
_E = np.concatenate([[0.0], np.cumsum((_SPD[1:] + _SPD[:-1]) / 2)])
_E /= _E[-1]


def spin_angle(k, t):
    """skema_cincin: ring k spun from its START letter to its TRIED letter, staggered"""
    a0, a1 = front(k, START[k]), front(k, TRIED[k])
    turns = [2, -2, 3, -2][k]  # full turns, and the direction each ring is spun
    if turns > 0:
        total = (a1 - a0) % 360 + 360 * turns
    else:
        total = -((a0 - a1) % 360) - 360 * (-turns)
    t0, t1 = 1.80 + 0.1 * k, 3.60 + 0.1 * k
    u = (t - t0) / (t1 - t0)
    return a0 + total * float(np.interp(min(max(u, 0), 1), _U, _E))


def code_angle(k, t, t_let):
    """skema_kode: ring k turns from its TRIED letter to its code letter, landing on the spoken letter, with a small click"""
    a0, a1 = front(k, TRIED[k]), front(k, CODE[k])
    delta = (a1 - a0 + 180) % 360 - 180  # the short way
    if abs(delta) < 60:
        delta += 360 if delta >= 0 else -360  # always at least one letter's worth of turning plus a full turn
    t1 = t_let + 0.04
    t0 = t1 - 0.42
    a = a0 + delta * ease((t - t0) / (t1 - t0))
    if t > t1:
        v = t - t1
        a += 4.0 * math.exp(-v * 12) * math.sin(2 * math.pi * 6 * v) * (1 if delta > 0 else -1)
    return a


def blur_px(a_now, a_prev):
    return abs(a_now - a_prev) * math.pi / 180 * R * 0.5


# ---------- the rings, spun in vain ----------
CLOSE = (1.0, 540.0, 1060.0)    # scale, frame point of the cylinder centre: the rings large, the shackle under the title
WIDE = (0.58, 500.0, 1030.0)     # the whole lock (y ~618-1158) with room for the dimension line on the right
KODE = (0.9, 540.0, 1072.0)


def camera(u, push=0.0):
    s = math.exp(math.log(CLOSE[0]) + (math.log(WIDE[0]) - math.log(CLOSE[0])) * u) * (1 + push)
    return s, CLOSE[1] + (WIDE[1] - CLOSE[1]) * u, CLOSE[2] + (WIDE[2] - CLOSE[2]) * u


def skema_cincin(times=None):
    t_ring, t_spin, t_pull, t_fail = 0.37, 1.80, 2.97, 4.49
    badges = [number_badge(k + 1) for k in range(4)]
    stamp = stamp_sprite("TETAP TERKUNCI", size=64, angle=-7)
    dim_lab = text_sprite([("3,2 cm", 46, YELLOW, True), ("tinggi gemboknya", 26, WHITE, False)], gap=2)
    ground = navy_ground()
    frames = []
    for i in range(N["cincin"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        th = [spin_angle(k, t) for k in range(4)]
        th0 = [spin_angle(k, t - 1 / FPS) for k in range(4)]
        lift = 0.0
        if t_fail <= t < t_fail + 0.24:  # the shackle tugs up and drops back: still locked
            lift = 16 * math.sin(math.pi * (t - t_fail) / 0.24)
        rgb, al, _ = lock_canvas(th, [blur_px(a, b) for a, b in zip(th, th0)], lift)
        u = ease((t - t_pull) / 1.2)
        sc, fx, fy = camera(u, 0.03 * min(t / t_pull, 1.0) * (1 - u))
        dx = 0.0
        if t >= t_fail:
            v = t - t_fail
            dx = 13 * math.exp(-v * 6.5) * math.sin(2 * math.pi * 8 * v)
        a = place(ground.copy(), rgb, al, sc, fx + dx, fy)
        a = title_shade(a, k=0.35, y1=700)
        im = to_img(a).convert("RGBA")
        out_a = 1 - ramp(t, t_pull, t_pull + 0.4)
        if out_a > 0:  # ring outlines and numbers
            lay = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(lay)
            for k, (xm, x0, x1) in enumerate(RING_X):
                ka = ramp(t, t_ring + 0.12 * k, t_ring + 0.12 * k + 0.2) * out_a
                if ka <= 0:
                    continue
                p0 = to_frame(x0 - 3, -R - 6, sc, fx + dx, fy)
                p1 = to_frame(x1 + 3, R + 6, sc, fx + dx, fy)
                d.rounded_rectangle([p0[0] * S, p0[1] * S, p1[0] * S, p1[1] * S], radius=14 * S,
                                    outline=YELLOW + (int(235 * ka),), width=5 * S)
            im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
            for k, (xm, x0, x1) in enumerate(RING_X):
                kb = pop(t, t_ring + 0.12 * k, 0.3)
                if kb > 0:
                    bx, by = to_frame(xm, -R - 50, sc, fx + dx, fy)
                    put1(im, badges[k], bx, by, a=min(1.0, kb) * out_a, scale=max(kb, 0.01))
        if t >= t_fail:  # dimension line beside the whole lock (shackle top to cylinder bottom = 31,8 mm)
            kd = ramp(t, t_fail + 0.05, t_fail + 0.4)
            x = to_frame(SEG[-1][1], 0, sc, fx, fy)[0] + 40
            ya, yb = to_frame(0, YT - TH, sc, fx, fy)[1], to_frame(0, RP, sc, fx, fy)[1]
            ym = (ya + yb) / 2
            lay = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(lay)
            col = YELLOW + (int(255 * kd),)
            y0, y1 = ym - (ym - ya) * kd, ym + (yb - ym) * kd
            d.line([(x * S, y0 * S), (x * S, y1 * S)], fill=col, width=5 * S)
            for y in (y0, y1):
                d.line([((x - 18) * S, y * S), ((x + 18) * S, y * S)], fill=col, width=5 * S)
            im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
            put1(im, dim_lab, min(x + 100, W - 92), ym, a=kd)
            ks = ramp(t, t_fail, t_fail + 0.12)
            put1(im, stamp, to_frame(0, 0, sc, fx + dx, fy)[0], to_frame(0, 0, sc, fx, fy)[1], a=ks, scale=1.5 - 0.5 * ks)
        frames.append(im.convert("RGB"))
    return frames


# ---------- the code, read off an X-ray ----------
def xray(rgb, al, lift, notches, gold_notch):
    """the lock canvas as a cyan X-ray: thin metal (engraving, grooves) bright, the inner bar, notches and gate line drawn"""
    y = np.clip((rgb @ np.array([0.299, 0.587, 0.114], np.float32)) / 255, 0, 1)
    v = 0.22 + 0.78 * np.clip(1.12 - 1.3 * y, 0, 1) ** 1.25
    ab = np.asarray(Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
    edge = np.clip(np.abs(al - ab) * 5, 0, 1)
    v = np.clip(v + 0.7 * edge, 0, 1)
    out = np.array([10, 40, 56], np.float32) * (1 - v)[..., None] + np.array([150, 245, 255], np.float32) * v[..., None]
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (CW * 2, CH * 2))
    d = ImageDraw.Draw(lay)
    c2 = lambda x, y: ((OX + x) * 2, (OY + y) * 2)
    dy = -lift
    cyan = (170, 250, 255)
    # the shackle legs inside the end plates and the bar they hold along the bore
    for xl, yb in ((-HW, -R + 90), (HW, -R_IN - 12)):
        d.rectangle([*c2(xl - TH + 6, -RP + dy), *c2(xl + TH - 6, yb + dy)], fill=cyan + (70,), outline=cyan + (200,), width=4)
    d.rectangle([*c2(-250, -R_IN - 36 + dy), *c2(HW, -R_IN - 12 + dy)], fill=cyan + (90,), outline=cyan + (220,), width=4)
    for xm, x0, x1 in RING_X:  # a stud on the bar over each ring
        d.rectangle([*c2(xm - 16, -R_IN - 12 + dy), *c2(xm + 16, -R_IN - 2 + dy)], fill=cyan + (200,))
    # the bore and the gate line
    for yy in (-R_IN, R_IN):
        d.line([c2(SEG[0][0], yy), c2(SEG[-1][1], yy)], fill=cyan + (60,), width=2)
    x = SEG[1][0]
    while x < SEG[4][1]:  # dashed gate line across the four rings
        d.line([c2(x, -R_IN), c2(min(x + 18, SEG[4][1]), -R_IN)], fill=GOLD + (230,), width=4)
        x += 30
    for k, (xm, x0, x1) in enumerate(RING_X):  # each ring's notch, wherever its turn has carried it
        yn = notches[k]
        col = GOLD + (255,) if gold_notch[k] else cyan + (150,)
        d.rounded_rectangle([*c2(xm - 28, yn - 7), *c2(xm + 28, yn + 7)], radius=8, fill=col)
    lay = lay.resize((CW, CH), Image.LANCZOS)
    img.alpha_composite(lay)
    a = np.asarray(img.convert("RGB"), np.float32)
    return a


def xray_ground():
    g = np.exp(-((XX - 540) ** 2 + (YY - 1020) ** 2) / (2 * 560.0 ** 2))
    a = np.array([6, 22, 32], np.float32) + np.array([10, 40, 56], np.float32) * g[..., None]
    grid = ((XX % 48 < 1.5) | (YY % 48 < 1.5)).astype(np.float32)
    a = a + grid[..., None] * np.array([10, 44, 58], np.float32)
    return a * (1 - 0.07 * ((np.arange(H) % 4) < 1)[:, None, None])


def skema_kode(times=None):
    t0, t1 = 0.05, 1.35                  # the scan line sweeps the frame
    t_let = [1.51, 2.36, 2.94, 3.51]     # "A", "En", "Ce", "E"
    t_open = t_let[3] + 0.28
    ground, xground = navy_ground(), xray_ground()
    sc, fx, fy = KODE
    ya, yb = -20, H + 20
    frames = []
    for i in range(N["kode"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        th = [code_angle(k, t, t_let[k]) for k in range(4)]
        th0 = [code_angle(k, t - 1 / FPS, t_let[k]) for k in range(4)]
        lift = 70 * ease((t - t_open) / 0.32)
        done = [t >= t_let[k] + 0.02 for k in range(4)]
        z = 1 + 0.03 * t / (N["kode"] / FPS)
        rgb, al, _ = lock_canvas(th, [blur_px(a, b) for a, b in zip(th, th0)], lift)
        notches = []
        for k in range(4):  # the notch sits 90 degrees before the code letter: on the gate line when the code is in front
            ph = math.radians(th[k] - front(k, CODE[k]) - 90)
            notches.append(R_IN * math.sin(ph))
        brass = place(ground.copy(), rgb, al, sc * z, fx, fy)
        ys = ya + (yb - ya) * ramp(t, t0, t1) if t < t1 + 0.4 else H + 100
        if ys > 0:
            gl = [k for k in range(4) if done[k]]
            xr = xray(rgb, al, lift, notches, done)
            if gl:  # the code letters glow gold on the X-ray
                g = np.zeros((CH, CW), np.float32)
                for k in gl:
                    stamp_letter(g, CODE[k], FS, RING_X[k][0], R * math.sin(math.radians(th[k] - front(k, CODE[k]))),
                                 math.cos(math.radians(th[k] - front(k, CODE[k]))))
                gb = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)),
                                np.float32) / 255
                xr = xr * (1 - g[..., None]) + np.array(GOLD, np.float32) * g[..., None]
                xr = xr + gb[..., None] * np.array([255, 190, 60], np.float32) * 0.6
            if t >= t_open - 0.02:  # a short flash on the shackle as it springs open
                fl = math.exp(-max(t - t_open, 0) * 10) * 0.45
                xr = xr + fl * 255 * (al * (YC < -R))[..., None]
            scan = place(xground.copy(), xr, al, sc * z, fx, fy, shadow=False)
            m = np.clip((ys - YY) / 10, 0, 1)[..., None]
            a = brass * (1 - m) + scan * m
        else:
            a = brass
        if t < t1 + 0.4:  # the scan line itself, with a soft glow
            gline = np.exp(-((YY - ys) / 9) ** 2) * 0.95 + np.exp(-((YY - ys) / 40) ** 2) * 0.35
            gline *= 1 - ramp(t, t1, t1 + 0.4)
            a = a + gline[..., None] * np.array([120, 255, 255], np.float32)
        a = title_shade(a, k=0.42, y1=700)
        im = to_img(a).convert("RGBA")
        lay = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(lay)
        for k, (xm, x0, x1) in enumerate(RING_X):  # the ring that found its letter gets a gold frame
            kl = ramp(t, t_let[k] - 0.02, t_let[k] + 0.15)
            if kl > 0:
                p0 = to_frame(x0 - 3, -R - 6, sc * z, fx, fy)
                p1 = to_frame(x1 + 3, R + 6, sc * z, fx, fy)
                d.rounded_rectangle([p0[0] * S, p0[1] * S, p1[0] * S, p1[1] * S], radius=14 * S,
                                    outline=GOLD + (int(240 * kl),), width=5 * S)
        im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        frames.append(im.convert("RGB"))
    return frames


OUT = {"cincin": "clips/skema_cincin.mp4", "kode": "clips/skema_kode.mp4"}
FUN = {"cincin": skema_cincin, "kode": skema_kode}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    for name in args or ["prep", "cincin", "kode"]:
        if name == "prep":
            prep()
            continue
        fr = FUN[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
