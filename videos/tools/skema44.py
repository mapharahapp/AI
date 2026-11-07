"""Stills and schematic animations for Titik Heran #44 (run in the episode work dir after
`dl.py v:751 i:1502706 i:2644630 i:67581 v:216500 i:969104 i:5926938 v:28659`; writes clips/751c.mp4, img/dadu44.jpg,
img/jung44.jpg, clips/topan.mp4, clips/skema_bangkai.mp4 and clips/skema_kepingan.mp4).
Pixabay + skema only: the finds themselves (photos by Matsuura City) are not shown; the wreck and one tile are drawn from
the sizes in the news (tile 3 x 1,5 cm, dice ±1 cm, wreck ±18 m down under more than 1 m of mud), shapes approximate.
usage: python3 skema44.py [prep|topan|bangkai|kepingan ...] [--sheet out.jpg t1,t2,...]
prep: clips/751c.mp4 (diver clip 751 without its letterbox and fade-in), img/dadu44.jpg (Pixabay dice 1502706, framed
  1,45x so the dice sit under the title) and img/jung44.jpg (the red-sail junk 2644630, a modern replica in Hong Kong:
  everything light behind the dark boat - the skyline, the water - is blurred into haze, then framed 1,5x on the sails
  and the bow, and the hull's painted name "AQUALUNA", its Chinese name and the draft marks are painted out).
topan: typhoon photo 67581 ("ilustrasi: topan dari satelit") turning slowly anticlockwise about its eye while pushing in,
  darker at the top so the four-line title reads.
skema_bangkai: seabed cross-section: water ±18 m deep (dimension line), mud, the buried wooden hull with its bulkheads;
  on "alat", "dapur" and "tulang" a knife, a mortar-like bowl and fish bones appear with labels; on "penyelam" a diver
  swims in with a torch; on "lima" five dice pop in one by one, glowing.
skema_kepingan: old dominoes (969104, "ilustrasi") behind an inset card "skema, bentuk perkiraan": one 3 x 1,5 cm tile
  with two dice faces beside a 1 cm die over a centimetre ruler.
Event times are seconds from the start of each clip, read off `render.py 44 plan`: topan starts at 10,13, skema_bangkai at
15,77 ("alat" 0,42, "dapur" 0,80, "tulang" 1,27, "penyelam" 2,42, "lima" 3,27, "dadu" 3,58), skema_kepingan at 20,23
("dua" 0,19, "kepingan" 1,04, "domino" 1,89).
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, text_sprite, encode
from skema35 import blur, sheet
from skema36 import reframe
from skema37 import noise, to_img, put1
from skema39 import cover, push, title_shade

N = {"topan": 99, "bangkai": 143, "kepingan": 93}  # each clip runs ~0,3 s past its shot
OUT = {"topan": "clips/topan.mp4", "bangkai": "clips/skema_bangkai.mp4", "kepingan": "clips/skema_kepingan.mp4"}
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def wanted(i, times):
    return times is None or any(abs(i / FPS - x) < 0.5 / FPS for x in times)


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def label(text, size=30, col=WHITE, bold=True, bg=(8, 14, 24, 190), pad=(16, 8)):
    """a pill label, 2x sprite"""
    f = ImageFont.truetype(XB if bold else MED, size * S)
    x0, y0, x1, y1 = f.getbbox(text)
    w, h = x1 - x0 + 2 * pad[0] * S, y1 - y0 + 2 * pad[1] * S
    sp = Image.new("RGBA", (w + 20 * S, h + 20 * S))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([10 * S, 10 * S, 10 * S + w, 10 * S + h], radius=h // 2, fill=bg)
    d.text((10 * S + pad[0] * S - x0, 10 * S + pad[1] * S - y0), text, font=f, fill=col + (255,))
    return sp


# ---------- prep ----------
def haze_junk(src, out):
    """keep the dark boat sharp; blur everything light behind it (skyline, water, painted name) into a warm haze"""
    im = Image.open(src).convert("RGB")
    a = np.asarray(im, np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    m = (lum < 118).astype(np.float32)
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(3)),
                   np.float32)[..., None] / 255
    soft = np.asarray(im.filter(ImageFilter.GaussianBlur(9)), np.float32)
    haze = np.array([214, 206, 192], np.float32)
    bgd = soft * 0.55 + haze * 0.45
    Image.fromarray((a * m + bgd * (1 - m)).clip(0, 255).astype(np.uint8)).save(out, quality=95)


def erase_marks(path, items):
    """paint out the light lettering left on the dark planked hull (the modern boat's name in Latin and Chinese letters
    and its draft marks): every masked pixel takes the nearest clean pixels along the plank direction (slope dy/dx), so
    the plank lines run on through the filled area"""
    a = np.asarray(Image.open(path).convert("RGB"), np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    bg = np.asarray(Image.fromarray(lum.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(7)), np.float32)
    h, w = lum.shape
    regs, allm = [], np.zeros((h, w), bool)
    for poly, slope, thr in items:
        pm = Image.new("L", (w, h))
        ImageDraw.Draw(pm).polygon(poly, fill=255)
        reg = np.asarray(pm.filter(ImageFilter.MaxFilter(5))) > 0
        m = (np.asarray(pm) > 0) & (lum - bg > thr)
        allm |= (np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0) & reg
        regs.append((reg, slope))
    res = a.copy()
    for reg, slope in regs:
        for y, x in zip(*np.nonzero(allm & reg)):
            got = []
            for sgn in (-1, 1):
                for k in range(2, 260):
                    xx, yy = x + sgn * k, int(round(y + sgn * k * slope))
                    if not (0 <= xx < w and 0 <= yy < h):
                        break
                    if not allm[yy, xx]:
                        got.append((k, a[yy, xx]))
                        break
            if got:
                res[y, x] = sum(v / k for k, v in got) / sum(1 / k for k, _ in got)
    sm = np.asarray(Image.fromarray(res.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32)
    mm = np.asarray(Image.fromarray((allm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)),
                    np.float32)[..., None] / 255 * 0.6
    Image.fromarray((res * (1 - mm) + sm * mm).clip(0, 255).astype(np.uint8)).save(path, quality=95)


JUNG_MARKS = [  # polygons in img/jung44.jpg, plank slope, brightness over the local mean
    ([(484, 1322), (484, 1284), (694, 1226), (694, 1266)], -0.29, 28),  # "AQUALUNA" and the number after it
    ([(506, 1358), (506, 1310), (614, 1286), (614, 1336)], -0.29, 28),  # the Chinese name
    ([(598, 1398), (642, 1394), (633, 1450), (598, 1450)], -0.22, 30),  # draft marks 2.4M / 2.2M
    ([(530, 1534), (574, 1534), (574, 1602), (530, 1602)], -0.22, 30),  # lower draft marks
]


def prep():
    # the wreck-diver clip 751 is 2.35:1 letterboxed inside 16:9 and fades in from black over its first 0,37 s:
    # drop the bars and the fade, lift the gamma (hook YAVG ~55 -> ~72)
    import subprocess
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "0.45", "-i", "clips/751.mp4", "-t", "7", "-vf",
                    "crop=1920:816:0:132,eq=gamma=1.22:saturation=1.05", "-c:v", "libx264", "-crf", "14", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-an", "clips/751c.mp4"], check=True)
    reframe("img/1502706.jpg", 1.45, 304, 185, "img/dadu44.jpg")  # the dice cluster centred at x 540, y ~900
    haze_junk("img/2644630.jpg", "img/2644630h.jpg")
    reframe("img/2644630h.jpg", 1.5, 640, 420, "img/jung44.jpg")  # foremast to bow in frame, the sail top under the title
    erase_marks("img/jung44.jpg", JUNG_MARKS)  # the boat's name and draft marks still read through the haze


# ---------- topan ----------
def skema_topan(times=None):
    im = Image.open("img/67581.jpg").convert("RGB")
    EYE = (895, 440)        # the big typhoon's eye in the 1280x954 photo
    FX, FY = 540, 1010      # where the eye sits in the frame
    frames = []
    n = N["topan"]
    for i in range(n):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        u = t / (n / FPS)
        s = 2.55 * (1 + 0.12 * ease(u))
        ang = math.radians(9 * u)  # anticlockwise on screen, like a northern typhoon
        c, sn = math.cos(ang), math.sin(ang)
        # output (x, y) -> source: eye + R(-ang) (out - F) / s ; image y points down, so anticlockwise is +ang here
        a_ = c / s
        b_ = -sn / s
        d_ = sn / s
        e_ = c / s
        cx = EYE[0] - a_ * FX - b_ * FY
        cy = EYE[1] - d_ * FX - e_ * FY
        f = im.transform((W, H), Image.AFFINE, (a_, b_, cx, d_, e_, cy), resample=Image.BICUBIC)
        arr = title_shade(np.asarray(f, np.float32), 0.5, 900)
        frames.append(to_img(arr))
    return frames


# ---------- skema_bangkai ----------
SURF, SEA = 236, 806   # water surface and seabed rows (±18 m)


def water_bg(t):
    v = np.clip((YY - SURF) / (SEA - SURF), 0, 1)[..., None]
    a = np.array([22, 84, 112], np.float32) * (1 - v) + np.array([6, 30, 46], np.float32) * v
    a[YY < SURF] = np.array([74, 112, 132], np.float32)
    # god rays from the surface, drifting slowly
    ray = np.zeros((H, W), np.float32)
    for k, (x0, wdt, sp) in enumerate([(160, 70, 9), (420, 110, -6), (700, 80, 7), (900, 60, -8)]):
        xc = x0 + sp * t + (YY - SURF) * 0.32
        ray += np.exp(-((XX - xc) / wdt) ** 2) * np.clip(1 - (YY - SURF) / 700, 0, 1) * (YY > SURF)
    a += ray[..., None] * np.array([60, 90, 90], np.float32) * 0.35
    return a


def mud_layer():
    """mud from the seabed down, its top gently wavy, grainy"""
    top = SEA + 8 * np.sin(XX[0] / 70.0) + 5 * np.sin(XX[0] / 23.0 + 1.3)
    m = np.clip(YY - top[None, :], 0, 1)
    n = noise((H, W), [(40, 0.5), (9, 0.5)], 21)
    v = np.clip((YY - SEA) / 900, 0, 1)
    col = np.stack([88 - 40 * v, 66 - 32 * v, 44 - 22 * v], -1) * (0.85 + 0.3 * n[..., None])
    return m, col, top


def hull_poly():
    """side view of the buried stern section: a broken, jagged end on the left, the gunwale just under the mud, the hull
    bottom curving up into a raised stern on the right"""
    from skema23 import smooth
    top = 838
    broken = [(112, 980), (126, top + 22), (148, top - 4), (170, top + 18), (192, top + 2)]
    stern = smooth([(860, top - 2), (930, top - 22), (978, top - 44), (990, top - 30), (984, 900), (962, 990), (920, 1068),
                    (850, 1120), (740, 1150), (560, 1158)])
    bottom = smooth([(560, 1158), (380, 1156), (240, 1138), (160, 1100), (122, 1040), (112, 980)])
    return broken + stern + bottom[1:]


def knife_sprite():
    sp = Image.new("RGBA", (200 * S, 80 * S))
    d = ImageDraw.Draw(sp)
    d.polygon([(20 * S, 40 * S), (120 * S, 28 * S), (124 * S, 52 * S), (30 * S, 50 * S)], fill=(176, 172, 160, 255))  # rusty blade
    d.line([(24 * S, 46 * S), (120 * S, 46 * S)], fill=(120, 96, 74, 255), width=3 * S)
    d.rounded_rectangle([122 * S, 30 * S, 186 * S, 50 * S], radius=8 * S, fill=(120, 78, 40, 255))
    return sp


def bowl_sprite():
    """a mortar-like bowl (suribachi / cobek): terracotta, combed grooves inside"""
    sp = Image.new("RGBA", (190 * S, 110 * S))
    d = ImageDraw.Draw(sp)
    d.polygon([(10 * S, 24 * S), (180 * S, 24 * S), (138 * S, 96 * S), (52 * S, 96 * S)], fill=(176, 92, 52, 255))
    d.ellipse([10 * S, 10 * S, 180 * S, 40 * S], fill=(120, 58, 32, 255))
    for k in range(-5, 6):
        d.line([((95 + 13 * k) * S, 16 * S), ((95 + 9 * k) * S, 36 * S)], fill=(204, 120, 74, 255), width=2 * S)
    return sp


def bones_sprite():
    sp = Image.new("RGBA", (200 * S, 90 * S))
    d = ImageDraw.Draw(sp)
    d.line([(20 * S, 45 * S), (170 * S, 45 * S)], fill=(236, 232, 218, 255), width=5 * S)  # spine
    for x in range(40, 160, 14):
        d.line([(x * S, 45 * S), ((x - 10) * S, 18 * S)], fill=(236, 232, 218, 255), width=3 * S)
        d.line([(x * S, 45 * S), ((x - 10) * S, 72 * S)], fill=(236, 232, 218, 255), width=3 * S)
    d.polygon([(170 * S, 45 * S), (192 * S, 24 * S), (192 * S, 66 * S)], outline=(236, 232, 218, 255), width=4 * S)  # tail
    d.ellipse([4 * S, 33 * S, 30 * S, 57 * S], outline=(236, 232, 218, 255), width=4 * S)  # skull ring
    return sp


def die_sprite(size=40, face=5, glow=True):
    """a small white die seen face on, with pips; optional yellow glow; 2x sprite"""
    m = size // 2
    sp = Image.new("RGBA", ((size + 2 * m) * S, (size + 2 * m) * S))
    if glow:
        g = Image.new("RGBA", sp.size)
        ImageDraw.Draw(g).rounded_rectangle([m * S - 8 * S, m * S - 8 * S, (m + size + 8) * S, (m + size + 8) * S], radius=12 * S,
                                            fill=YELLOW + (230,))
        sp.alpha_composite(g.filter(ImageFilter.GaussianBlur(9 * S)))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([m * S, m * S, (m + size) * S, (m + size) * S], radius=size * S // 6, fill=(246, 242, 228, 255),
                        outline=(120, 110, 90, 255), width=2 * S)
    pip = {1: [(0.5, 0.5)], 2: [(0.27, 0.27), (0.73, 0.73)], 3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
           4: [(0.27, 0.27), (0.73, 0.27), (0.27, 0.73), (0.73, 0.73)],
           5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
           6: [(0.27, 0.22), (0.27, 0.5), (0.27, 0.78), (0.73, 0.22), (0.73, 0.5), (0.73, 0.78)]}[face]
    r = size * 0.09
    for px, py in pip:
        cx, cy = (m + size * px) * S, (m + size * py) * S
        d.ellipse([cx - r * S, cy - r * S, cx + r * S, cy + r * S], fill=(30, 26, 22, 255))
    return sp


def diver_sprite():
    """a dark diver silhouette swimming right with a torch held forward; 2x sprite, ~260 px long at 1x"""
    sp = Image.new("RGBA", (300 * S, 140 * S))
    d = ImageDraw.Draw(sp)
    col = (30, 46, 58, 250)
    P = lambda pts: [(x * S, y * S) for x, y in pts]
    d.polygon(P([(70, 64), (180, 52), (196, 64), (182, 80), (70, 84)]), fill=col)          # torso
    d.ellipse(P([(196, 46), (228, 76)]), fill=col)                                        # head
    d.rounded_rectangle(P([(96, 38), (170, 56)]), radius=8 * S, fill=(26, 40, 48, 245))  # tank
    d.line(P([(76, 70), (20, 60)]), fill=col, width=14 * S)                               # legs
    d.line(P([(76, 78), (24, 90)]), fill=col, width=14 * S)
    d.polygon(P([(24, 54), (0, 40), (8, 66)]), fill=col)                                  # fins
    d.polygon(P([(28, 84), (2, 98), (14, 104)]), fill=col)
    d.line(P([(180, 78), (236, 96)]), fill=col, width=10 * S)                             # arm
    d.rounded_rectangle(P([(232, 90), (256, 104)]), radius=4 * S, fill=(60, 66, 70, 255))  # torch
    d.ellipse(P([(252, 90), (262, 104)]), fill=(255, 250, 220, 255))
    return sp


def skema_bangkai(times=None):
    t_alat, t_dapur, t_tulang, t_selam, t_lima = 0.42, 0.80, 1.27, 2.42, 3.27
    mud_m, mud_c, mud_top = mud_layer()
    hull = hull_poly()
    hm = Image.new("L", (W, H), 0)
    ImageDraw.Draw(hm).polygon(hull, fill=255)
    hmask = np.asarray(hm.filter(ImageFilter.GaussianBlur(1)), np.float32)[..., None] / 255
    # inside the hull: the dug-out dark cavity with plank lines
    cav = np.zeros((H, W, 3), np.float32) + np.array([22, 16, 12], np.float32)
    cav += (np.sin((YY - 840) / 9.0) > 0.85)[..., None] * np.array([18, 12, 8], np.float32)
    items = [(t_alat, knife_sprite(), 282, 1046, "diduga pisau dapur"), (t_dapur, bowl_sprite(), 560, 1040, "wadah mirip cobek"),
             (t_tulang, bones_sprite(), 826, 1046, "tulang ikan")]
    item_labels = [label(txt, 24, WHITE, False, (8, 14, 24, 200), (12, 6)) for *_, txt in items]
    dice = [die_sprite(34, f) for f in (5, 3, 6, 2, 4)]
    dice_xy = [(372, 1006), (470, 1020), (650, 1014), (712, 996), (520, 994)]
    diver = diver_sprite()
    depth = label("±18 m", 34, YELLOW)
    rng = np.random.default_rng(5)
    motes = [(rng.uniform(0, W), rng.uniform(SURF, SEA), rng.uniform(1, 2.4), rng.uniform(-8, 8)) for _ in range(90)]
    frames = []
    for i in range(N["bangkai"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        a = water_bg(t)
        a = a * (1 - mud_m[..., None]) + mud_c * mud_m[..., None]
        a = a * (1 - hmask) + cav * hmask
        im = to_img(a).convert("RGBA")
        lay = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(lay)
        # the hull's timbers: outline, bulkheads, a few planks
        d.line(hull + hull[:1], fill=(132, 92, 56, 255), width=10, joint="curve")
        for x in (425, 695):  # bulkheads
            d.line([(x, 834), (x, 1154)], fill=(124, 86, 52, 255), width=10)
        # mud fill still lying in the cavity's lower part
        d.polygon([(124, 1084), (300, 1128), (540, 1120), (760, 1126), (900, 1090), (842, 1124), (740, 1146), (262, 1142), (160, 1098)],
                  fill=(70, 52, 34, 255))
        # the water surface
        d.line([(x, SURF + 5 * math.sin(x / 40 + 3 * t)) for x in range(0, W + 1, 12)], fill=(190, 230, 240, 200), width=4)
        # suspended sediment drifting
        for x, y, r, vx in motes:
            xx = (x + vx * t) % W
            d.ellipse([xx - r, y - r, xx + r, y + r], fill=(200, 220, 210, 70))
        # depth: surface to seabed
        x = 1022
        d.line([(x, SURF + 6), (x, SEA - 4)], fill=(255, 225, 0, 230), width=4)
        for y in (SURF + 6, SEA - 4):
            d.line([(x - 16, y), (x + 16, y)], fill=(255, 225, 0, 230), width=4)
        im.alpha_composite(lay)
        put1(im, depth, 952, 742)
        # the diver comes in with a torch on "penyelam"
        kd = ramp(t, t_selam - 0.1, t_selam + 0.3)
        if kd > 0:
            dx = -300 + 520 * ease((t - t_selam + 0.1) / 1.4)
            dy = 720 + 6 * math.sin(3 * t)
            beam = Image.new("RGBA", (W, H))
            ImageDraw.Draw(beam).polygon([(dx + 168, dy + 34), (dx + 560, dy + 320), (dx + 360, dy + 390)],
                                         fill=(255, 246, 200, int(90 * kd)))
            im.alpha_composite(beam.filter(ImageFilter.GaussianBlur(18)))
            put1(im, diver, dx, dy, a=kd, scale=1.15)
        # the kitchen things, one per word, then the dice
        for k, (tk, sp, x, y, txt) in enumerate(items):
            kk = pop(t, tk, 0.3)
            if kk > 0:
                put1(im, sp, x, y, a=min(1, kk), scale=0.8 * kk)
                put1(im, item_labels[k], x, 1108, a=min(1, kk))
        for k, ((x, y), sp) in enumerate(zip(dice_xy, dice)):
            kk = pop(t, t_lima + 0.09 * k, 0.28)
            if kk > 0:
                put1(im, sp, x, y, a=min(1, kk), scale=kk)
        frames.append(im.convert("RGB"))
    return frames


# ---------- skema_kepingan ----------
PX_CM = 80


def tile_sprite():
    """one tile, 3 x 1,5 cm at 80 px/cm: ivory, a centre line, a dice face on each half (pips generic, shape approximate)"""
    w, h = 3 * PX_CM, int(1.5 * PX_CM)
    m = 12
    sp = Image.new("RGBA", ((w + 2 * m) * S, (h + 2 * m) * S))
    sh = Image.new("RGBA", sp.size)
    ImageDraw.Draw(sh).rounded_rectangle([(m + 4) * S, (m + 6) * S, (m + w + 4) * S, (m + h + 6) * S], radius=10 * S, fill=(0, 0, 0, 140))
    sp.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5 * S)))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([m * S, m * S, (m + w) * S, (m + h) * S], radius=10 * S, fill=(236, 226, 200, 255), outline=(150, 132, 100, 255),
                        width=2 * S)
    d.line([((m + w / 2) * S, (m + 10) * S), ((m + w / 2) * S, (m + h - 10) * S)], fill=(120, 104, 80, 255), width=3 * S)
    r = 7
    for x0, pips in [(m, [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)]), (m + w / 2, [(0.27, 0.27), (0.73, 0.73)])]:
        for px, py in pips:
            cx, cy = (x0 + 10 + (w / 2 - 20) * px) * S, (m + 10 + (h - 20) * py) * S
            d.ellipse([cx - r * S, cy - r * S, cx + r * S, cy + r * S], fill=(40, 34, 28, 255))
    return sp


def ruler_sprite(cm=6):
    w, h = cm * PX_CM, 40
    m = 10
    sp = Image.new("RGBA", ((w + 2 * m) * S, (h + 2 * m) * S))
    d = ImageDraw.Draw(sp)
    d.rectangle([m * S, m * S, (m + w) * S, (m + h) * S], fill=(232, 200, 120, 255))
    f = ImageFont.truetype(XB, 16 * S)
    for k in range(cm * 10 + 1):
        x = (m + k * PX_CM / 10) * S
        L = 18 if k % 10 == 0 else 11 if k % 5 == 0 else 6
        d.line([(x, m * S), (x, (m + L) * S)], fill=(40, 34, 28, 255), width=2 * S)
        if k % 10 == 0:
            d.text((x, (m + 32) * S), str(k // 10), font=f, fill=(40, 34, 28, 255), anchor="mm")
    return sp


def skema_kepingan(times=None):
    t_card, t_tile, t_die = 0.15, 0.35, 1.04
    bg0 = cover("img/969104.jpg", 0.3)
    tile, ruler = tile_sprite(), ruler_sprite()
    die = die_sprite(PX_CM, 3, glow=False)
    f_small = ImageFont.truetype(MED, 24)
    f_dim = ImageFont.truetype(XB, 28)
    CX, CY, CW, CH = 540, 1132, 640, 270   # the inset card, under the watermark band
    frames = []
    for i in range(N["kepingan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        a = push(bg0, 1 + 0.05 * i / N["kepingan"]) * 0.82
        im = to_img(a).convert("RGBA")
        kc = pop(t, t_card, 0.3)
        if kc > 0:
            card = Image.new("RGBA", (W, H))
            d = ImageDraw.Draw(card)
            s = min(1, kc)
            x0, y0 = CX - CW / 2 * kc, CY - CH / 2 * kc
            x1, y1 = CX + CW / 2 * kc, CY + CH / 2 * kc
            d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=(10, 22, 44, int(225 * s)), outline=(255, 255, 255, int(200 * s)), width=3)
            if kc >= 0.98:
                d.text((CX - CW / 2 + 22, CY - CH / 2 + 32), "skema, bentuk perkiraan", font=f_small, fill=(255, 255, 255, 200), anchor="ls")
            im.alpha_composite(card)
        kt = pop(t, t_tile, 0.3)
        if kt > 0:
            put1(im, tile, CX - 110, CY + 4, a=min(1, kt), scale=kt)
        kd = pop(t, t_die, 0.3)
        if kd > 0:
            put1(im, die, CX + 170, CY + 4, a=min(1, kd), scale=kd)
        kr = ramp(t, t_tile + 0.2, t_tile + 0.6)
        if kr > 0:
            put1(im, ruler, CX - 2, CY + 88, a=kr)
            lay = Image.new("RGBA", (W, H))
            d = ImageDraw.Draw(lay)
            d.text((CX - 110, CY - 78), "3 × 1,5 cm", font=f_dim, fill=YELLOW + (int(255 * kr),), anchor="ms")
            if kd > 0.9:
                d.text((CX + 170, CY - 78), "1 cm", font=f_dim, fill=YELLOW + (int(255 * min(1, kd)),), anchor="ms")
            im.alpha_composite(lay)
        frames.append(im.convert("RGB"))
    return frames


FUN = {"topan": skema_topan, "bangkai": skema_bangkai, "kepingan": skema_kepingan}

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
