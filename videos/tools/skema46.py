"""Stills, hook push and schematic animations for Titik Heran #46 (run in the episode work dir after
`dl.py i:376989 i:1700918 i:60588 i:1757353 i:241962 v:6583 v:224206 v:8625`; writes img/allo46.jpg, img/tengkorak46.jpg,
clips/trex46.mp4, clips/kaki46.mp4, clips/skema_tulang.mp4, clips/skema_heme.mp4 and clips/api46.mp4).
Pixabay has no photo of Aratasaurus, its bone or the Museu Nacional fire: the skeletons and bones are T. rex and Allosaurus
stand-ins ("ilustrasi"), the fire is another building ("ilustrasi: kebakaran gedung lain"), and the bone section and the heme
molecule are drawn ("skema", shapes simplified; no cell size is shown because it is disputed).
usage: python3 skema46.py [prep|trex|kaki|tulang|heme|api ...] [--sheet out.jpg t1,t2,...]
prep: img/allo46.jpg (the Allosaurus skull 60588, shot on black, 1,3x on a black frame under the title, edges feathered) and
  img/tengkorak46.jpg (the dark museum skull 241962 1180 wide over its own blurred copy, set low so the CTA title clears it).
trex: the T. rex skeleton 376989 pushing in toward its skull, which stays put at (403, 806), darker at the top for the title.
kaki: the T. rex foot 1700918 (a cutout PNG: its transparent pixels hold junk colour, so it is used through its alpha) on a dark
  warm ground; from "tulang" a glowing red line runs down the middle toe like a blood vessel, then beats softly.
tulang: a cross-section of a leg bone (cortex with osteons and their canals, the marrow cavity) with one canal ringed in red
  on "saluran" ("saluran" label); it zooms through into that canal, where reddish ovals light up one by one from "ada", label
  "bulatan mirip sel darah merah" on "bulatan".
heme: a heme molecule drawn as a skeletal formula (porphyrin ring of four pyrroles, four N around an iron atom) wiped in
  clockwise; Fe pops on "heme" ("Fe = besi"), an O2 molecule flies in from "pembawa" and docks on the iron on "oksigen".
api: the burning building 224206 (4K drone, cropped vertical on the smoke column); on "selamat" the foot bone fades in over
  it, glowing white, while the fire behind it dims.
Event times are seconds from the start of each clip, read off `render.py 46 plan`: tulang starts at 12,23 ("di" 0,46,
"saluran" 0,62, "ada" 1,69, "bulatan" 1,92), heme at 15,93 ("jejak" 0,36, "heme" 0,62, "pembawa" 1,05, "oksigen" 1,47),
api at 18,17 ("ini" 0,57, "selamat" 1,37), kaki at 2,17 ("tulang" 0,17, "seratus" 1,50).
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, encode
from skema35 import blur, sheet
from skema37 import noise, to_img, put1
from skema39 import cover, lum, sat, title_shade

N = {"trex": 75, "kaki": 117, "tulang": 78, "heme": 78, "api": 111}  # each clip runs ~0,3 s past its shot
OUT = {"trex": "clips/trex46.mp4", "kaki": "clips/kaki46.mp4", "tulang": "clips/skema_tulang.mp4",
       "heme": "clips/skema_heme.mp4", "api": "clips/api46.mp4"}
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def wanted(i, times):
    return times is None or any(abs(i / FPS - x) < 0.5 / FPS for x in times)


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def pill(text, size=34, col=WHITE, bg=(10, 14, 24, 205), edge=(255, 255, 255, 120), pad=(22, 12)):
    """a rounded label, 2x sprite"""
    f = ImageFont.truetype(XB, size * S)
    x0, y0, x1, y1 = f.getbbox(text)
    w, h = x1 - x0 + 2 * pad[0] * S, y1 - y0 + 2 * pad[1] * S
    sp = Image.new("RGBA", (w + 20 * S, h + 20 * S))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([10 * S, 10 * S, 10 * S + w, 10 * S + h], radius=h // 2, fill=bg, outline=edge, width=3 * S)
    d.text((10 * S + pad[0] * S - x0, 10 * S + pad[1] * S - y0), text, font=f, fill=col + (255,))
    return sp


def foot():
    """the T. rex foot cutout (808x1280 RGBA); its transparent pixels carry junk colour, so zero them"""
    im = Image.open("img/1700918.jpg").convert("RGBA")
    a = np.asarray(im, np.float32)
    a[..., :3] *= (a[..., 3:] > 0)
    return Image.fromarray(a.astype(np.uint8))


# ---------- prep ----------
def feathered(a, f):
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    m = np.clip(np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]) / f, 0, 1)
    return m * m * (3 - 2 * m)


def prep():
    # the Allosaurus skull on black: 1,3x, the skull (orig ~500, 450) at frame (520, 990), under the three-line title
    im = Image.open("img/60588.jpg").convert("RGB")
    s = 1.3
    a = np.asarray(im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS), np.float32)
    a *= feathered(a, 60)[..., None]
    f = np.zeros((H, W, 3), np.float32)
    x0, y0 = round(520 - 500 * s), round(990 - 450 * s)
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    w, h = min(a.shape[1] - sx0, W - dx0), min(a.shape[0] - sy0, H - dy0)
    f[dy0:dy0 + h, dx0:dx0 + w] = a[sy0:sy0 + h, sx0:sx0 + w]
    Image.fromarray(f.clip(0, 255).astype(np.uint8)).save("img/allo46.jpg", quality=95)
    print("img/allo46.jpg")
    # the dark museum skull: 1180 wide, skull (orig ~687, 500) at frame (560, 1060), over its blurred, darkened copy
    im = Image.open("img/241962.jpg").convert("RGB")
    bg = blur(cover("img/241962.jpg", 0.55), 26) * 0.55
    k = 1180 / im.width
    a = np.asarray(im.resize((1180, round(im.height * k)), Image.LANCZOS), np.float32)
    x0, y0 = round(560 - 687 * k), round(1060 - 500 * k)
    m = feathered(a, 45)[..., None]
    sx0 = max(0, -x0)
    w = min(a.shape[1] - sx0, W - max(0, x0))
    region = bg[y0:y0 + a.shape[0], max(0, x0):max(0, x0) + w]
    bg[y0:y0 + a.shape[0], max(0, x0):max(0, x0) + w] = a[:, sx0:sx0 + w] * m[:, sx0:sx0 + w] + region * (1 - m[:, sx0:sx0 + w])
    Image.fromarray(bg.clip(0, 255).astype(np.uint8)).save("img/tengkorak46.jpg", quality=95)
    print("img/tengkorak46.jpg")


# ---------- trex (hook) ----------
def skema_trex(times=None):
    im = Image.open("img/376989.jpg").convert("RGB")  # 853x1280, skull ~ (260, 520)
    SK, FP = (260, 520), (420, 850)
    frames = []
    n = N["trex"]
    for i in range(n):
        if not wanted(i, times):
            frames.append(None)
            continue
        u = i / (n - 1)
        s = 1.55 + 0.30 * (1 - (1 - u) ** 1.6)
        x0, y0 = SK[0] - FP[0] / s, SK[1] - FP[1] / s
        x0 = min(max(x0, 0), im.width - W / s)
        y0 = min(max(y0, 0), im.height - H / s)
        f = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + W / s, y0 + H / s))
        frames.append(to_img(title_shade(np.asarray(f, np.float32), 0.45, 700)))
    return frames


# ---------- kaki ----------
FOOT_S, FOOT_X, FOOT_Y = 1.05, 116, 560
VESSEL = [(550, 70), (540, 250), (520, 450), (482, 650), (440, 780), (390, 900), (330, 1010), (262, 1120), (195, 1225)]


def warm_ground():
    r = np.sqrt(((XX - 540) / 1.1) ** 2 + (YY - 1150) ** 2)
    v = np.clip(r / 1150, 0, 1)[..., None]
    a = np.array([52, 34, 28], np.float32) * (1 - v) + np.array([8, 6, 8], np.float32) * v
    return a * (0.94 + 0.08 * noise((H, W), [(80, 0.6), (20, 0.4)], 46))[..., None]


def path_upto(pts, u):
    """the first fraction u of a polyline (by length)"""
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    L, out, acc = sum(seg) * u, [pts[0]], 0.0
    for (a, b), d in zip(zip(pts, pts[1:]), seg):
        if acc + d >= L:
            k = (L - acc) / d if d else 0
            out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
            return out
        out.append(b)
        acc += d
    return out


def skema_kaki(times=None):
    base = to_img(warm_ground()).convert("RGBA")
    ft = foot()
    ft = ft.resize((round(ft.width * FOOT_S), round(ft.height * FOOT_S)), Image.LANCZOS)
    base.alpha_composite(ft, (FOOT_X, FOOT_Y))
    pts = [(FOOT_X + x * FOOT_S, FOOT_Y + y * FOOT_S) for x, y in VESSEL]
    pts = smooth_open(pts)
    t0, t1 = 0.17, 1.45  # "tulang" -> just before "seratus"
    frames = []
    for i in range(N["kaki"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        u = ease((t - t0) / (t1 - t0))
        if u > 0:
            beat = 1.0 if t < t1 else 0.75 + 0.25 * math.cos(2 * math.pi * (t - t1) / 0.85)
            seg = path_upto(pts, u)
            lay = Image.new("RGBA", (W, H))
            d = ImageDraw.Draw(lay)
            if len(seg) > 1:
                d.line(seg, fill=(255, 30, 20, int(190 * beat)), width=46, joint="curve")
            lay = lay.filter(ImageFilter.GaussianBlur(16))
            d = ImageDraw.Draw(lay)
            if len(seg) > 1:
                d.line(seg, fill=(235, 40, 30, int(240 * beat)), width=14, joint="curve")
                d.line(seg, fill=(255, 205, 175, int(235 * beat)), width=5, joint="curve")
            im.alpha_composite(lay)
            if u < 1:  # the bright head of the line
                hx, hy = seg[-1]
                g = Image.new("RGBA", (W, H))
                ImageDraw.Draw(g).ellipse([hx - 24, hy - 24, hx + 24, hy + 24], fill=(255, 130, 100, 240))
                im.alpha_composite(g.filter(ImageFilter.GaussianBlur(9)))
        frames.append(im.convert("RGB"))
    return frames


def smooth_open(pts, n=3):
    for _ in range(n):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        pts = out + [pts[-1]]
    return pts


# ---------- skema_tulang ----------
BC = (540, 960)          # the bone section's centre
CANAL = (742, 808)       # the canal we zoom into
CL = (540, 880)          # the canal's centre in the close-up
R_CL = 230               # the canal's radius in the close-up


def blob(cx, cy, rx, ry, seed, amp=0.06, n=160):
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 2 * math.pi, 4)
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        r = 1 + amp * (math.sin(2 * a + ph[0]) * 0.6 + math.sin(3 * a + ph[1]) * 0.3 + math.sin(5 * a + ph[2]) * 0.1)
        out.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    return out


def section_image():
    """the bone cross-section at 1x on its dark ground (RGB array) and the osteon centres"""
    g = np.array([14, 10, 11], np.float32) + np.exp(-((XX - BC[0]) ** 2 + (YY - BC[1]) ** 2) / 520 ** 2)[..., None] * np.array([26, 18, 16], np.float32)
    big = Image.new("L", (W * S, H * S))
    outer = blob(BC[0], BC[1], 340, 305, 1)
    inner = blob(BC[0] - 18, BC[1] + 10, 150, 128, 2, 0.1)
    ImageDraw.Draw(big).polygon([(x * S, y * S) for x, y in outer], fill=255)
    mo = np.asarray(big.resize((W, H), Image.LANCZOS), np.float32) / 255
    big = Image.new("L", (W * S, H * S))
    ImageDraw.Draw(big).polygon([(x * S, y * S) for x, y in inner], fill=255)
    mi = np.asarray(big.resize((W, H), Image.LANCZOS), np.float32) / 255
    nz = noise((H, W), [(30, 0.5), (8, 0.3), (3, 0.2)], 461)
    # cortex: ivory with faint concentric lamellae round the centre
    r = np.sqrt(((XX - BC[0]) / 340) ** 2 + ((YY - BC[1]) / 305) ** 2)
    lam = 0.5 + 0.5 * np.sin(r * 2 * math.pi * 9)
    ivory = np.array([214, 196, 164], np.float32) * (0.9 + 0.08 * nz[..., None] + 0.04 * lam[..., None])
    marrow = np.array([58, 32, 26], np.float32) * (0.8 + 0.4 * nz[..., None])
    a = g * (1 - mo[..., None]) + (ivory * (1 - mi[..., None]) + marrow * mi[..., None]) * mo[..., None]
    im = to_img(a).convert("RGBA")
    # osteons: a ring of lamellae round a dark canal, scattered through the cortex
    rng = np.random.default_rng(46)
    pts = [CANAL]
    for _ in range(4000):  # random placement with a minimum gap (the band holds ~45)
        ang, rad = rng.uniform(0, 2 * math.pi), rng.uniform(0.54, 0.92)
        p = (BC[0] + 340 * rad * math.cos(ang), BC[1] + 305 * rad * math.sin(ang))
        if all(math.dist(p, q) > 46 for q in pts):
            pts.append(p)
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for k, (x, y) in enumerate(pts):
        R = 22 if k == 0 else rng.uniform(15, 22)
        for rr, col, wd in [(R, (170, 150, 120, 150), 2), (R * 0.7, (160, 140, 112, 120), 2)]:
            d.ellipse([(x - rr) * S, (y - rr) * S, (x + rr) * S, (y + rr) * S], outline=col, width=wd * S)
        c = R * 0.34
        d.ellipse([(x - c) * S, (y - c) * S, (x + c) * S, (y + c) * S], fill=(46, 24, 20, 255))
    im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    return im.convert("RGB")


def closeup_image(seed=7):
    """the close-up: bone matrix with lamellae concentric to the canal, the dark canal, cell spaces (lacunae)"""
    r = np.sqrt((XX - CL[0]) ** 2 + (YY - CL[1]) ** 2)
    nz = noise((H, W), [(60, 0.5), (14, 0.3), (4, 0.2)], 4612)
    lam = 0.5 + 0.5 * np.sin((r - R_CL) / 22 * 2 * math.pi + 0.8 * nz)
    a = np.array([206, 186, 152], np.float32) * (0.86 + 0.08 * nz[..., None] + 0.07 * lam[..., None])
    a *= np.clip(1.05 - (r / 1100) ** 1.5, 0.45, 1)[..., None]
    rim = np.exp(-((r - R_CL) / 9) ** 2)
    a = a * (1 - 0.45 * rim[..., None])
    inside = np.clip((R_CL - r) / 3, 0, 1)[..., None]
    lumen = np.array([40, 20, 17], np.float32) * (0.75 + 0.5 * nz[..., None]) * (0.7 + 0.3 * np.clip(r / R_CL, 0, 1))[..., None]
    a = a * (1 - inside) + lumen * inside
    im = to_img(a).convert("RGBA")
    rng = np.random.default_rng(seed)
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for _ in range(90):  # lacunae: small dark lens shapes along the lamellae
        ang, rad = rng.uniform(0, 2 * math.pi), rng.uniform(R_CL + 40, 820)
        x, y = CL[0] + rad * math.cos(ang), CL[1] + rad * math.sin(ang)
        if not (0 < x < W and 0 < y < H):
            continue
        t = ang + math.pi / 2
        pts = [(x + 9 * math.cos(t) * math.cos(q) - 3.5 * math.sin(t) * math.sin(q),
                y + 9 * math.sin(t) * math.cos(q) + 3.5 * math.cos(t) * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 16)]
        d.polygon([(px * S, py * S) for px, py in pts], fill=(96, 70, 52, 170))
    im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    return im


def cell_sprite(rx, ry, ang, k):
    """a reddish oval (a mineralised 'cell'): dim brown at k=0, glowing red at k=1, a paler dimple in the middle; 2x sprite"""
    m = 30
    w, h = int((rx + m) * 2 * S), int((rx + m) * 2 * S)
    sp = Image.new("RGBA", (w, h))
    gl = Image.new("RGBA", (w, h))
    cx, cy = w / 2, h / 2
    lit = (int(96 + 140 * k), int(42 - 6 * k), int(34 - 4 * k))
    ImageDraw.Draw(gl).ellipse([cx - (rx + 10) * S, cy - (ry + 10) * S, cx + (rx + 10) * S, cy + (ry + 10) * S],
                               fill=(255, 40, 30, int(170 * k)))
    sp.alpha_composite(gl.filter(ImageFilter.GaussianBlur(12 * S)))
    d = ImageDraw.Draw(sp)
    d.ellipse([cx - rx * S, cy - ry * S, cx + rx * S, cy + ry * S], fill=lit + (255,), outline=(40, 12, 10, 200), width=2 * S)
    d.ellipse([cx - rx * 0.5 * S, cy - ry * 0.45 * S, cx + rx * 0.5 * S, cy + ry * 0.45 * S],
              fill=(int(lit[0] * 0.78), int(lit[1] * 0.8), int(lit[2] * 0.8), 255))
    d.ellipse([cx - rx * 0.55 * S, cy - ry * 0.75 * S, cx - rx * 0.05 * S, cy - ry * 0.35 * S], fill=(255, 210, 190, int(70 + 80 * k)))
    return sp.rotate(ang, resample=Image.BICUBIC)


CELLS = [(-92, -70, 20), (18, -110, -30), (110, -40, 60), (-120, 40, -50), (-10, 0, 10), (95, 75, -20), (-40, 115, 40),
         (60, 150, 80), (-150, -10, 75)]


def skema_tulang(times=None):
    sec = section_image()
    cl = closeup_image()
    lab_s = pill("saluran", 40, YELLOW)
    lab_c = pill("bulatan mirip sel darah merah", 38, YELLOW)
    t_ring, t_z0, t_z1, t_cells, t_lab = 0.62, 1.0, 1.5, 1.66, 1.92
    Zend = R_CL / 7.5  # the canal's radius in the overview is ~7,5 px
    frames = []
    for i in range(N["tulang"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        uz = ease((t - t_z0) / (t_z1 - t_z0))
        Z = (1.0 + 0.06 * min(t, t_z0) / t_z0) * (Zend / 1.06) ** uz if uz > 0 else 1.0 + 0.06 * t / t_z0
        # the canal moves from where it is to the close-up centre as the zoom goes in
        cx, cy = CANAL[0] + (CL[0] - CANAL[0]) * uz, CANAL[1] + (CL[1] - CANAL[1]) * uz
        if uz < 1:
            box = (CANAL[0] - cx / Z, CANAL[1] - cy / Z, CANAL[0] + (W - cx) / Z, CANAL[1] + (H - cy) / Z)
            im = sec.resize((W, H), Image.BICUBIC, box=box).convert("RGBA")
        else:
            im = Image.new("RGBA", (W, H))
        ka = ramp(t, t_z0 + 0.15, t_z1)
        if ka > 0:
            k = Z / Zend
            c2 = cl.resize((max(1, round(W * k)), max(1, round(H * k))), Image.BICUBIC)
            c2.putalpha(Image.fromarray((np.asarray(c2.getchannel("A"), np.float32) * ka).astype(np.uint8)))
            lay = Image.new("RGBA", (W, H))
            ox, oy = round(cx - CL[0] * k), round(cy - CL[1] * k)
            lay.paste(c2, (ox, oy))
            im.alpha_composite(lay)
        kr = ramp(t, t_ring, t_ring + 0.2) * (1 - ramp(t, t_z0 + 0.1, t_z0 + 0.3))
        if kr > 0:  # the red ring round the canal and its label
            pulse = 1 + 0.25 * math.sin(2 * math.pi * (t - t_ring) / 0.45)
            rr = 24 * Z * pulse
            lay = Image.new("RGBA", (W * S, H * S))
            ImageDraw.Draw(lay).ellipse([(cx - rr) * S, (cy - rr) * S, (cx + rr) * S, (cy + rr) * S], outline=(255, 50, 40, int(255 * kr)), width=6 * S)
            im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
            put1(im, lab_s, cx + 20, cy - 78, a=kr)
        if t >= t_z1 - 0.1:
            for k, (dx, dy, ang) in enumerate(CELLS):
                kk = ramp(t, t_cells + 0.05 * k, t_cells + 0.05 * k + 0.18)
                sp = cell_sprite(38, 25, ang, kk)
                put1(im, sp, CL[0] + dx, CL[1] + dy, a=min(1.0, 3 * ramp(t, t_z1 - 0.1, t_z1 + 0.1)))
        kl = pop(t, t_lab, 0.3)
        if kl > 0:
            put1(im, lab_c, 540, CL[1] + R_CL + 66, a=min(1.0, kl), scale=kl)
        frames.append(im.convert("RGB"))
    return frames


# ---------- skema_heme ----------
M = (540, 880)  # the iron atom


def heme_layout():
    """atoms and bonds of a heme skeleton (top view): four pyrroles round Fe, their N inward, meso carbons between them"""
    atoms, bonds = {}, []
    for q in range(4):
        th = -math.pi / 2 + q * math.pi / 2  # the pyrrole's direction from Fe
        c = (M[0] + 193 * math.cos(th), M[1] + 193 * math.sin(th))
        ring = []
        for k in range(5):  # vertex 0 (N) points to Fe
            a = th + math.pi + k * 2 * math.pi / 5
            ring.append((c[0] + 70 * math.cos(a), c[1] + 70 * math.sin(a)))
        for k in range(5):
            atoms[f"p{q}_{k}"] = ring[k]
            bonds.append((f"p{q}_{k}", f"p{q}_{(k + 1) % 5}", 2 if k in (2,) else 1))
        # side groups on the two outer (beta) carbons
        for k in (2, 3):
            v = (ring[k][0] - c[0], ring[k][1] - c[1])
            L = math.hypot(*v)
            atoms[f"s{q}_{k}"] = (ring[k][0] + v[0] / L * 64, ring[k][1] + v[1] / L * 64)
            bonds.append((f"p{q}_{k}", f"s{q}_{k}", 1))
    for q in range(4):  # meso carbons on the diagonals, joining alpha carbons of neighbouring pyrroles
        th = -math.pi / 2 + q * math.pi / 2 + math.pi / 4
        atoms[f"m{q}"] = (M[0] + 230 * math.cos(th), M[1] + 230 * math.sin(th))
        bonds.append((f"p{q}_4", f"m{q}", 1))
        bonds.append((f"m{q}", f"p{(q + 1) % 4}_1", 2))
    return atoms, bonds


def skema_heme(times=None):
    atoms, bonds = heme_layout()
    ground = np.array([10, 16, 30], np.float32) + np.exp(-((XX - M[0]) ** 2 + (YY - M[1]) ** 2) / 560 ** 2)[..., None] * np.array([18, 30, 50], np.float32)
    base = to_img(ground).convert("RGBA")
    # the ring skeleton on its own layer (2x), wiped in clockwise from the top
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for a, b, order in bonds:
        (x0, y0), (x1, y1) = atoms[a], atoms[b]
        d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=(235, 245, 255, 255), width=7 * S)
        if order == 2:  # a second, inner line for a double bond
            nx, ny = -(y1 - y0), x1 - x0
            L = math.hypot(nx, ny)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            if (M[0] - mx) * nx + (M[1] - my) * ny < 0:
                nx, ny = -nx, -ny
            ox, oy = nx / L * 13, ny / L * 13
            d.line([((x0 + ox + (x1 - x0) * 0.15) * S, (y0 + oy + (y1 - y0) * 0.15) * S),
                    ((x1 + ox - (x1 - x0) * 0.15) * S, (y1 + oy - (y1 - y0) * 0.15) * S)], fill=(235, 245, 255, 255), width=5 * S)
    fN = ImageFont.truetype(XB, 34 * S)
    for q in range(4):
        x, y = atoms[f"p{q}_0"]
        d.ellipse([(x - 25) * S, (y - 25) * S, (x + 25) * S, (y + 25) * S], fill=(60, 110, 230, 255), outline=(235, 245, 255, 255), width=3 * S)
        d.text((x * S, y * S), "N", font=fN, fill=(255, 255, 255, 255), anchor="mm")
    ring = lay.resize((W, H), Image.LANCZOS)
    glow = ring.filter(ImageFilter.GaussianBlur(10))
    g = np.asarray(glow, np.float32)
    g[..., :3] = np.array([120, 220, 255], np.float32)
    g[..., 3] *= 0.8
    glow = Image.fromarray(g.astype(np.uint8))
    # the N-Fe bonds (dashed) and the iron atom
    fe = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(fe)
    for q in range(4):
        x, y = atoms[f"p{q}_0"]
        for k in range(5):
            u0, u1 = 0.2 + k * 0.13, 0.2 + k * 0.13 + 0.07
            d.line([((M[0] + (x - M[0]) * u0) * S, (M[1] + (y - M[1]) * u0) * S), ((M[0] + (x - M[0]) * u1) * S, (M[1] + (y - M[1]) * u1) * S)],
                   fill=(255, 200, 120, 230), width=4 * S)
    d.ellipse([(M[0] - 52) * S, (M[1] - 52) * S, (M[0] + 52) * S, (M[1] + 52) * S], fill=(222, 112, 40, 255), outline=(255, 230, 190, 255), width=4 * S)
    d.text((M[0] * S, M[1] * S), "Fe", font=ImageFont.truetype(XB, 50 * S), fill=(255, 255, 255, 255), anchor="mm")
    fe = fe.resize((W, H), Image.LANCZOS)
    feg = Image.new("RGBA", (W, H))
    ImageDraw.Draw(feg).ellipse([M[0] - 90, M[1] - 90, M[0] + 90, M[1] + 90], fill=(255, 150, 60, 200))
    feg = feg.filter(ImageFilter.GaussianBlur(30))
    # O2: two red atoms with a double bond, 2x sprite
    o2 = Image.new("RGBA", (260 * S, 140 * S))
    d = ImageDraw.Draw(o2)
    for dy in (-7, 7):
        d.line([(84 * S, (70 + dy) * S), (176 * S, (70 + dy) * S)], fill=(255, 235, 235, 255), width=5 * S)
    fO = ImageFont.truetype(XB, 36 * S)
    for x in (80, 180):
        d.ellipse([(x - 34) * S, 36 * S, (x + 34) * S, 104 * S], fill=(222, 40, 46, 255), outline=(255, 220, 220, 255), width=3 * S)
        d.text((x * S, 70 * S), "O", font=fO, fill=(255, 255, 255, 255), anchor="mm")
    o2 = o2.rotate(-28, resample=Image.BICUBIC, expand=True)
    lab_fe = pill("Fe = besi", 36)
    lab_o2 = pill("O₂ = oksigen", 36, YELLOW)
    ang = (np.degrees(np.arctan2(XX - M[0], -(YY - M[1]))) + 360) % 360  # clockwise from the top
    t_fe, t_o0, t_o1 = 0.62, 1.05, 1.47
    frames = []
    for i in range(N["heme"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        w = ramp(t, 0.0, 0.55) * 380 - 10
        mk = np.clip((w - ang) / 12, 0, 1)
        for L in (glow, ring):
            a = np.asarray(L, np.float32).copy()
            a[..., 3] *= mk
            im.alpha_composite(Image.fromarray(a.astype(np.uint8)))
        kf = pop(t, t_fe, 0.32)
        if kf > 0:
            fl = 1 + 0.6 * math.exp(-max(0.0, t - t_fe - 0.15) / 0.25)
            g2 = feg.copy()
            g2.putalpha(g2.getchannel("A").point(lambda v: int(min(255, v * min(1.0, kf) * fl))))
            im.alpha_composite(g2)
            f2 = fe if abs(kf - 1) < 1e-3 else fe.resize((W, H))
            sc = kf
            if sc != 1:
                f2 = fe.resize((round(W * sc), round(H * sc)), Image.BICUBIC)
                tmp = Image.new("RGBA", (W, H))
                tmp.paste(f2, (round(M[0] - M[0] * sc), round(M[1] - M[1] * sc)))
                f2 = tmp
            im.alpha_composite(f2)
            put1(im, lab_fe, M[0], M[1] + 348, a=ramp(t, t_fe + 0.1, t_fe + 0.3))
        uo = ease((t - t_o0) / (t_o1 - t_o0))
        if t >= t_o0:
            # from the top right down to dock on the iron, a little up and right of it (it sits above the ring's plane)
            x = 980 + (M[0] + 62 - 980) * uo
            y = 440 + (M[1] - 74 - 440) * uo
            if t > t_o1:
                y += 4 * math.sin(2 * math.pi * (t - t_o1) / 0.6)
                fl = math.exp(-(t - t_o1) / 0.22)
                if fl > 0.02:
                    b = Image.new("RGBA", (W, H))
                    ImageDraw.Draw(b).ellipse([M[0] - 150, M[1] - 150, M[0] + 150, M[1] + 150], fill=(255, 240, 220, int(160 * fl)))
                    im.alpha_composite(b.filter(ImageFilter.GaussianBlur(40)))
            put1(im, o2, x, y, a=min(1.0, 4 * (t - t_o0)))
            put1(im, lab_o2, x + 150, y - 104, a=ramp(t, t_o0 + 0.15, t_o0 + 0.35))
        frames.append(im.convert("RGB"))
    return frames


# ---------- api ----------
FIRE_OFF, FIRE_POS = 4.0, 0.47


def fire_reader(n):
    w = round(3840 * H / 2160)
    x0 = round((w - W) * FIRE_POS)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(FIRE_OFF), "-i", "clips/224206.mp4", "-frames:v", str(n), "-vf",
                          f"fps={FPS},scale={w}:{H}:flags=lanczos,crop={W}:{H}:{x0}:0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    for _ in range(n):
        yield np.frombuffer(p.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3)
    p.stdout.close()
    p.wait()


def skema_api(times=None):
    ft = foot()
    s = 0.62
    ft = ft.resize((round(ft.width * s), round(ft.height * s)), Image.LANCZOS)
    al = np.asarray(ft.getchannel("A"), np.float32) / 255
    pad = 60
    halo = np.zeros((ft.height + 2 * pad, ft.width + 2 * pad), np.float32)
    halo[pad:pad + ft.height, pad:pad + ft.width] = al
    halo = np.clip(blur(halo[..., None], 16)[..., 0] * 1.9, 0, 1)
    halo_im = Image.fromarray(np.dstack([np.full(halo.shape, 255, np.float32)] * 3 + [halo * 205]).astype(np.uint8))
    a = np.asarray(ft, np.float32)
    a[..., :3] = a[..., :3] * 0.85 + 255 * 0.15  # paler, as if lit from within
    ft = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    BX, BY = 540, 1080
    t_on = 1.37  # "selamat"
    frames = []
    reader = fire_reader(N["api"])
    for i in range(N["api"]):
        t = i / FPS
        fr = next(reader)
        if not wanted(i, times):
            frames.append(None)
            continue
        k = ramp(t, t_on, t_on + 0.4)
        a = fr.astype(np.float32)
        a = title_shade(a, 0.35, 760)
        if k > 0:
            a = sat(a, 1 - 0.4 * k) * (1 - 0.45 * k)
        im = to_img(a).convert("RGBA")
        if k > 0:
            kp = pop(t, t_on, 0.45)
            sc = 0.9 + 0.1 * min(kp, 1.08)
            breathe = 1 + 0.15 * math.sin(2 * math.pi * max(0.0, t - t_on - 0.4) / 1.2)
            h2 = halo_im.resize((round(halo_im.width * sc), round(halo_im.height * sc)), Image.BICUBIC)
            h2.putalpha(h2.getchannel("A").point(lambda v: int(min(255, v * k * breathe))))
            im.alpha_composite(h2, (round(BX - h2.width / 2), round(BY - h2.height / 2)))
            f2 = ft.resize((round(ft.width * sc), round(ft.height * sc)), Image.BICUBIC)
            f2.putalpha(f2.getchannel("A").point(lambda v: int(v * k)))
            im.alpha_composite(f2, (round(BX - f2.width / 2), round(BY - f2.height / 2)))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"trex": skema_trex, "kaki": skema_kaki, "tulang": skema_tulang, "heme": skema_heme, "api": skema_api}

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
