"""Schematic and reconstruction animations for Titik Heran #39 (run in the episode work dir after
`dl.py i:10518742 i:10518757 i:3680171 i:1822636 i:5438620`; writes img/10518742v.jpg, img/10518757v.jpg, clips/skema_ukur.mp4,
skema_dugaan.mp4, skema_gua.mp4, skema_stegodon.mp4 and skema_punah.mp4).
usage: python3 skema39.py [foto|ukur|dugaan|gua|stegodon|punah ...] [--sheet out.jpg t1,t2,...]
Pixabay has no real photo of Homo floresiensis, Liang Bua or a Stegodon (its "homo floresiensis" results are AI images), so:
img/10518742v.jpg, img/10518757v.jpg: the two Rinca komodo photos set lower in the 9:16 frame (the sand continued above), so
  the heads sit under the titles instead of behind them.
skema_ukur: the Padar landscape (3680171, a stand-in for NTT) dims; a ruler (0-1,5 m) stands on a ground line and a white
  hobbit silhouette (1,06 m, the LB1 skeleton) rises beside a faint present-day adult; the 1 m line lights up on "satu".
skema_dugaan: the elephant photo (1822636, an Asian elephant standing in for the extinct Stegodon), a red "DUGAAN LAMA"
  stamp slammed on "dikira".
skema_gua: the cave photo (5438620, a stand-in for Liang Bua) dims; line-art bone fragments land on the floor in step with
  the title's counter (0 to 3.155) and blink yellow on "bercerita lain". 150 fragments stand for the 3.155.
skema_stegodon: a Stegodon diagram (an outline with a simplified skeleton): red zones pulse on the meatiest parts (shoulder and
  thigh: "bekas gigitan komodo") and yellow dots light up on ribs, toes and skull ("goresan alat batu"); a small hobbit
  silhouette (a reconstruction) comes in toward the leftovers. The zones follow the study's summary (bite marks on meat-rich
  bones, cut marks mostly on low-value parts), not a bone-by-bone map.
skema_punah: the cave at dusk; a backlit hobbit silhouette in the opening crumbles into drifting dust.
Event times are seconds from the start of each clip, read off `render.py 39 plan`: skema_ukur starts at 4,40 ("tingginya" 2,36,
"satu" 3,20, "meter" 3,43), skema_dugaan at 8,57 ("dikira" 0,72), skema_gua at 11,03 (counter 0,05-0,96, "bercerita" 2,82),
skema_stegodon at 16,37 ("paling" 0,49, "Goresan" 1,68, "hobit?" 2,57, "Kebanyakan" 3,14, "sisa" 4,05), skema_punah at 21,10
("sudah" 1,44, "punah" 1,74).
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, text_sprite, dashed, chaikin, encode
from skema27 import stamp_sprite
from skema35 import blur, sheet
from skema36 import reframe
from skema37 import ADULT, draw_figure, mask_of, noise, to_img, light_up, put1

N = {"ukur": 134, "dugaan": 83, "gua": 123, "stegodon": 151, "punah": 86}  # each clip runs ~0,3 s past its shot
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
RED = (232, 44, 40)
BONE = (238, 231, 214)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

# Homo floresiensis: the adult silhouette with longer arms and bigger feet
HOBBIT = dict(ADULT, armR=[(-0.13, 0.812), (-0.174, 0.63), (-0.17, 0.445)], handR=[(-0.17, 0.425), 0.027],
              armL=[(0.13, 0.812), (0.172, 0.63), (0.164, 0.445)], handL=[(0.164, 0.425), 0.027],
              footR=[(-0.097, 0.017), 0.06, 0.02], footL=[(0.089, 0.017), 0.06, 0.02])


def wanted(i, times):
    return times is None or any(abs(i / FPS - x) < 0.5 / FPS for x in times)


def cover(path, pos=0.5):
    im = Image.open(path).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0, y0 = round((im.width - W) * pos), (im.height - H) // 2
    return np.asarray(im.crop((x0, y0, x0 + W, y0 + H)), np.float32)


def push(a, z):
    """an HxWx3 float frame zoomed by z about its centre, sub-pixel smooth"""
    if z <= 1.0005:
        return a
    w, h = W / z, H / z
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return np.asarray(im.resize((W, H), Image.BICUBIC, box=((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2)), np.float32)


def lum(a):
    return a @ np.array([0.299, 0.587, 0.114], np.float32)


def sat(a, k):
    y = lum(a)[..., None]
    return y + (a - y) * k


def warm(a):  # render.py's "warm" by hand (render adds its base grade and vignette on top of a skema clip)
    a = sat((a - 128) * 1.04 + 128, 1.05)
    return a * np.array([1.04, 1.0, 0.94], np.float32) + np.array([5, 2, -3], np.float32)


def cold(a):
    a = sat((a - 128) * 1.08 + 128, 0.35) - 4
    y = np.clip(lum(a) / 255, 0, 1)[..., None]
    return a + (1 - y) * np.array([-9, -3, 14], np.float32) + y * np.array([-5, -1, 8], np.float32)


def dusk(a):
    a = (a - 128) * 1.08 + 128
    y = np.clip(lum(a) / 255, 0, 1)[..., None]
    return (a + (1 - y) * np.array([-8, -3, 16], np.float32) + y * np.array([16, 6, -10], np.float32)) * 0.9


def title_shade(a, k=0.42, y1=760):
    """darker towards the top, so the titles read over bright rock or light"""
    return a * (1 - k * np.clip((y1 - YY) / (y1 - 300), 0, 1) ** 1.2)[..., None]


def figure_mask(pose, x, ground, h):
    lay = Image.new("L", (W * S, H * S), 0)
    draw_figure(ImageDraw.Draw(lay), pose, x, ground, h)
    return mask_of(lay)


# ---------- the two komodo photos, set lower ----------
def foto():
    reframe("img/10518742.jpg", 2.4, 632, 186, "img/10518742v.jpg")   # the snout's top at y ~530, clear of the 2-line title through the push
    reframe("img/10518757.jpg", 2.1, 1202, 128, "img/10518757v.jpg")  # the head (photo ~820,320) at frame ~520,800


# ---------- 1 metre ----------
def skema_ukur(times=None):
    bg0 = warm(cover("img/3680171.jpg", 0.6))
    G, PX = 1190, 300            # ground line, pixels per metre
    HX, AX, RX = 410, 690, 935   # hobbit, adult, ruler
    t_in, t_one = 2.36, 3.20     # "tingginya", "satu"
    hob = figure_mask(HOBBIT, HX, G, 1.06 * PX)
    adu = figure_mask(ADULT, AX, G, 1.65 * PX)
    hob_glow = blur(hob, 7)
    lab_h = text_sprite([("hobbit", 30, WHITE, False)])
    lab_a = text_sprite([("orang dewasa masa kini", 30, WHITE, False)])
    tick_f = ImageFont.truetype(MED, 30 * S)
    dark = np.clip((YY - 640) / 300, 0, 1)
    frames = []
    for i in range(N["ukur"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        a = push(bg0, 1 + 0.05 * i / N["ukur"])
        k = ramp(t, t_in - 0.1, t_in + 0.35)
        if k > 0:  # the lower frame dims so the white figures read
            a = a * (1 - 0.55 * k * dark)[..., None]
        ka = ramp(t, t_in, t_in + 0.45)
        if ka > 0:  # a faint present-day adult for scale
            ma = (adu * 0.3 * ka)[..., None]
            a = a * (1 - ma) + 255 * ma
        kh = ramp(t, t_in, t_one - 0.15)
        if kh > 0:  # the hobbit rises: revealed from the ground up
            rev = np.clip((YY - (G - kh * (1.06 * PX + 24))) / 6, 0, 1)
            m = (hob * rev)[..., None]
            a = a + (hob_glow * rev * 0.32)[..., None] * 255
            a = a * (1 - 0.93 * m) + 0.93 * m * np.array([252, 248, 238], np.float32)
        im = to_img(a).convert("RGBA")
        lay = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(lay)
        kg = ramp(t, t_in, t_in + 0.35)
        if kg > 0:
            x0, x1 = 250, 1010
            xm = (x0 + x1) / 2
            d.line([((xm - (xm - x0) * kg) * S, G * S), ((xm + (x1 - xm) * kg) * S, G * S)], fill=(255, 255, 255, 200), width=4 * S)
            ytop = G - 1.5 * PX * kg
            d.line([(RX * S, G * S), (RX * S, ytop * S)], fill=(255, 255, 255, 235), width=5 * S)
            for mm, txt in ((0.5, "0,5 m"), (1.0, "1 m"), (1.5, "1,5 m")):
                y = G - mm * PX
                if y >= ytop - 1:
                    col = YELLOW + (255,) if mm == 1.0 and t >= t_one else (255, 255, 255, 235)
                    d.line([((RX - 22) * S, y * S), ((RX + 22) * S, y * S)], fill=col, width=5 * S)
                    d.text(((RX + 30) * S, y * S), txt, font=tick_f, fill=col, anchor="lm")
        if t >= t_one:  # the 1 m line runs from the hobbit's head to the ruler
            u = ramp(t, t_one, t_one + 0.3)
            xa, xb, y = HX - 70, RX - 24, G - PX
            dashed(d, [(xa, y), (xa + (xb - xa) * u, y)], YELLOW + (255,), 4, dash=18, gap=12)
        im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        if ka > 0:
            put1(im, lab_a, AX, G + 42, a=0.85 * ka)
        kl = ramp(t, t_in + 0.3, t_in + 0.6)
        if kl > 0:
            put1(im, lab_h, HX, G + 42, a=0.95 * kl)
        frames.append(im.convert("RGB"))
    return frames


# ---------- the old idea, stamped ----------
def skema_dugaan(times=None):
    bg0 = cold(cover("img/1822636.jpg", 0.47))
    st = stamp_sprite("DUGAAN LAMA", 84, 7)
    t_on = 0.72  # "dikira"
    frames = []
    for i in range(N["dugaan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = to_img(push(bg0, 1 + 0.06 * i / N["dugaan"])).convert("RGBA")
        if t >= t_on:
            u = min((t - t_on) / 0.12, 1.0)
            land = max(t - t_on - 0.12, 0)
            dx = 7 * math.exp(-land / 0.07) * math.sin(land * 70) if u >= 1 else 0
            put1(im, st, 560 + dx, 1110, a=u, scale=1.7 - 0.7 * u * u)
        frames.append(im.convert("RGB"))
    return frames


# ---------- bone fragments on the cave floor ----------
def floor_shards(seed=39, n=150):
    """irregular elongated shards in the floor's perspective (smaller and flatter further away), off the caption band"""
    rng = np.random.default_rng(seed)
    out = []
    while len(out) < n:
        y = rng.uniform(1115, 1720)
        if 1288 < y < 1418:
            continue
        half = 170 + (y - 1115) * 0.62
        x = rng.normal(560, half * 0.55)
        if abs(x - 560) > half or not 30 < x < 1050:
            continue
        L, ang, k = 17 + (y - 1100) * 0.085, rng.uniform(0, math.pi), int(rng.integers(6, 9))
        flat = rng.uniform(0.38, 0.62)  # chunky splinters, not slivers
        pts = []
        for j in range(k):
            th = 2 * math.pi * j / k + rng.uniform(-0.3, 0.3)
            r = rng.uniform(0.5, 1.0)
            px, py = math.cos(th) * L * r, math.sin(th) * L * r * flat
            pts.append((px * math.cos(ang) - py * math.sin(ang), (px * math.sin(ang) + py * math.cos(ang)) * 0.62))
        out.append([x, y, pts, 0.0])
    order = rng.permutation(n)
    for s, o in zip(out, order):
        s[3] = 0.05 + 0.91 * o / n  # lands in step with the counter (0,05-0,96)
    out.sort(key=lambda s: s[1])  # far ones first
    return out


def blink(t, t0):
    if t < t0:
        return 0.0
    u = t - t0
    return 1.0 if u < 0.16 or 0.28 <= u < 0.44 else 0.0 if u < 0.28 else 0.5


def skema_gua(times=None):
    bg0 = cover("img/5438620.jpg", 0.72)
    bg0 = title_shade(sat(bg0, 0.85) * np.array([0.8, 0.88, 0.8], np.float32), 0.45)
    shards = floor_shards()
    t_tell = 2.82  # "bercerita"
    frames = []
    for i in range(N["gua"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = to_img(push(bg0, 1 + 0.05 * i / N["gua"])).convert("RGBA")
        b = blink(t, t_tell)
        col = tuple(round(c0 * (1 - b) + c1 * b) for c0, c1 in zip(BONE, YELLOW))
        lay = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(lay)
        for x, y, pts, t0 in shards:
            if t < t0:
                continue
            k = pop(t, t0, 0.2)
            q = [((x + px * k) * S, (y + py * k) * S) for px, py in pts]
            d.polygon([(qx + 2 * S, qy + 3 * S) for qx, qy in q], fill=(0, 0, 0, 130))
            d.polygon(q, fill=col + (240,), outline=(96, 86, 66, 255))
            # a crack across the larger fragments, so they read as broken bone
            if len(q) > 6 and y > 1400:
                d.line([q[1], ((q[1][0] + q[4][0]) / 2 + S, (q[1][1] + q[4][1]) / 2), q[4]], fill=(140, 128, 104, 255), width=S)
        lay = lay.resize((W, H), Image.LANCZOS)
        if b > 0:  # a glow under the fragments while they blink
            g = Image.new("RGBA", (W, H), YELLOW + (0,))
            g.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.9 * b)))
            im.alpha_composite(g)
        im.alpha_composite(lay)
        frames.append(im.convert("RGB"))
    return frames


# ---------- the Stegodon diagram ----------
BODY = [(300, 720), (360, 700), (440, 690), (560, 700), (680, 712), (800, 740), (850, 790), (862, 860), (858, 900), (842, 980),
        (832, 1060), (828, 1150), (834, 1194), (752, 1196), (748, 1185), (752, 1100), (748, 1030), (735, 975), (690, 1000),
        (600, 1010), (510, 1000), (485, 1010), (478, 1100), (482, 1194), (398, 1196), (394, 1185), (392, 1100), (388, 1010),
        (380, 960), (360, 900), (330, 880), (300, 880), (270, 876), (262, 950), (266, 1040), (277, 1105), (262, 1114),
        (246, 1108), (240, 1040), (232, 950), (230, 860), (248, 790), (268, 745)]
EAR = [(330, 762), (396, 752), (412, 822), (398, 900), (352, 912), (326, 852)]
TUSK_NEAR = [(262, 878), (222, 958), (168, 1036), (124, 1068), (96, 1058)]
TUSK_FAR = [(272, 882), (236, 962), (186, 1042), (146, 1076), (122, 1070)]
MEAT = [(445, 860, 88, 122), (792, 905, 96, 132)]  # shoulder and upper fore leg; hip and thigh
CUTS = [(468, 905), (503, 918), (538, 928), (573, 932), (608, 926), (290, 762), (318, 822),
        (415, 1188), (455, 1188), (778, 1189), (812, 1189)]  # ribs, skull, toes
HOB_X, HOB_G, HOB_H = 962, 1196, 270


def tusk(d, pts, col, w0, w1):
    p = chaikin_open(pts)
    n = len(p)
    for k in range(n - 1):
        w = w0 + (w1 - w0) * k / (n - 1)
        d.line([(p[k][0] * S, p[k][1] * S), (p[k + 1][0] * S, p[k + 1][1] * S)], fill=col, width=max(1, round(w * S)))
        r = w * S / 2
        d.ellipse([p[k][0] * S - r, p[k][1] * S - r, p[k][0] * S + r, p[k][1] * S + r], fill=col)


def chaikin_open(pts, n=3):
    for _ in range(n):
        q = [pts[0]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            q += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        pts = q + [pts[-1]]
    return pts


def curve(d, pts, col, w):
    d.line([(x * S, y * S) for x, y in chaikin_open(pts)], fill=col, width=round(w * S), joint="curve")


def stegodon_layers():
    """(background with the body, the body mask, the skeleton as an RGBA layer)"""
    bg = blur(cover("img/5438620.jpg", 0.72), 16) * np.array([0.2, 0.24, 0.22], np.float32)
    bg = bg + (np.exp(-((XX - 520) ** 2 / 560 ** 2 + (YY - 960) ** 2 / 420 ** 2)) * 34)[..., None] * np.array([0.8, 1.0, 1.0], np.float32)
    body = chaikin(BODY, 2)
    m2 = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(m2).polygon([(x * S, y * S) for x, y in body], fill=255)
    M = mask_of(m2)
    shade = (np.array([30, 48, 54], np.float32) + np.clip(1 - (YY - 690) / 520, 0, 1)[..., None] * np.array([22, 30, 30], np.float32))
    sh = blur(np.clip(1 - ((XX - 600) / 380) ** 2 - ((YY - 1200) / 22) ** 2, 0, 1), 6)  # a contact shadow under the feet
    bg = bg * (1 - 0.6 * sh)[..., None]
    bg = bg * (1 - 0.93 * M[..., None]) + shade * 0.93 * M[..., None]
    im = to_img(bg).convert("RGBA")
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    tusk(d, TUSK_FAR, (150, 146, 132, 255), 22, 7)
    d.polygon([(x * S, y * S) for x, y in chaikin(EAR, 2)], fill=(44, 66, 72, 255), outline=(170, 205, 205, 150))
    d.line([(x * S, y * S) for x, y in body + body[:1]], fill=(190, 228, 226, 230), width=3 * S, joint="curve")
    tusk(d, TUSK_NEAR, (234, 226, 204, 255), 26, 8)
    d.ellipse([279 * S, 784 * S, 291 * S, 796 * S], fill=(10, 14, 16, 255))
    im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    sk = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(sk)
    c = (226, 232, 222, 150)
    curve(d, [(330, 765), (440, 730), (600, 734), (790, 768), (852, 822)], c, 4)            # spine
    for k in range(9):                                                                        # ribs
        x = 440 + k * 24
        ys = 732 + 4 * math.sin(k / 3)
        curve(d, [(x, ys + 4), (x - 18, ys + 90), (x - 6, ys + 170), (x + 16, 958 - abs(k - 4) * 6)], c, 3)
    d.polygon([(x * S, y * S) for x, y in [(412, 748), (472, 742), (460, 820), (436, 880), (420, 826)]], outline=c, width=3 * S)
    curve(d, [(436, 862), (424, 990)], c, 5)   # humerus
    curve(d, [(424, 992), (436, 1170)], c, 5)  # radius and ulna
    d.ellipse([752 * S, 760 * S, 842 * S, 862 * S], outline=c, width=3 * S)                  # pelvis
    curve(d, [(800, 858), (772, 1010)], c, 5)  # femur
    curve(d, [(772, 1012), (792, 1170)], c, 5)  # tibia
    d.polygon([(x * S, y * S) for x, y in [(258, 752), (320, 742), (342, 800), (318, 860), (268, 858), (250, 800)]], outline=c, width=3 * S)
    for x in (406, 424, 442, 460, 762, 780, 798, 816):                                       # toes
        d.ellipse([(x - 6) * S, 1183 * S, (x + 6) * S, 1193 * S], outline=c, width=2 * S)
    sk = sk.resize((W, H), Image.LANCZOS)
    a = np.asarray(sk, np.float32)
    a[..., 3] *= np.clip(M * 1.05, 0, 1)  # bones only inside the body
    return np.asarray(im.convert("RGB"), np.float32), M, Image.fromarray(a.astype(np.uint8))


def badge(sym):
    """a round red badge with a fang, or a grey stone flake, 2x sprite"""
    r = 30 * S
    sp = Image.new("RGBA", (4 * r, 4 * r))
    d = ImageDraw.Draw(sp)
    c = 2 * r
    if sym == "fang":
        d.ellipse([c - r, c - r, c + r, c + r], fill=RED + (255,), outline=(255, 255, 255, 255), width=3 * S)
        d.polygon([(c - 0.45 * r, c - 0.5 * r), (c + 0.45 * r, c - 0.5 * r), (c + 0.08 * r, c + 0.62 * r), (c - 0.08 * r, c + 0.62 * r)],
                  fill=(255, 255, 255, 255))
    else:
        d.ellipse([c - r, c - r, c + r, c + r], fill=(255, 205, 40, 255), outline=(255, 255, 255, 255), width=3 * S)
        d.polygon([(c - 0.55 * r, c + 0.35 * r), (c - 0.1 * r, c - 0.62 * r), (c + 0.6 * r, c - 0.2 * r), (c + 0.2 * r, c + 0.55 * r)],
                  fill=(92, 92, 96, 255), outline=(255, 255, 255, 255))
        d.line([(c - 0.1 * r, c - 0.62 * r), (c + 0.02 * r, c + 0.1 * r), (c + 0.6 * r, c - 0.2 * r)], fill=(200, 200, 205, 255), width=2 * S)
    sh = Image.new("RGBA", sp.size)
    ImageDraw.Draw(sh).ellipse([c - r - 6 * S, c - r - 4 * S, c + r + 6 * S, c + r + 8 * S], fill=(0, 0, 0, 140))
    sh = sh.filter(ImageFilter.GaussianBlur(6 * S))
    sh.alpha_composite(sp)
    return sh


def legend(text, col):
    f = ImageFont.truetype(MED, 32 * S)
    w = int(f.getlength(text)) + 60 * S
    sp = Image.new("RGBA", (w + 20 * S, 64 * S))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([0, 6 * S, w + 18 * S, 58 * S], radius=26 * S, fill=(0, 0, 0, 150))
    d.ellipse([14 * S, 20 * S, 38 * S, 44 * S], fill=col + (255,))
    d.text((50 * S, 32 * S), text, font=f, fill=(255, 255, 255, 255), anchor="lm")
    return sp


def skema_stegodon(times=None):
    base, M, sk = stegodon_layers()
    t_meat, t_cut0, t_hob, t_cut, t_left = 0.49, 1.68, 2.57, 3.14, 4.05  # "paling", "Goresan", "hobit?", "Kebanyakan", "sisa"
    blobs = [np.exp(-((XX - cx) / rx) ** 2 - ((YY - cy) / ry) ** 2) * M for cx, cy, rx, ry in MEAT]
    meat = np.clip(sum(blobs), 0, 1)
    hob = figure_mask(HOBBIT, HOB_X, HOB_G, HOB_H)
    hob_glow = blur(hob, 6)
    fang, flake = badge("fang"), badge("flake")
    lg_red, lg_yel = legend("gigitan komodo", RED), legend("goresan alat batu", YELLOW)
    dot = Image.new("RGBA", (64 * S, 64 * S))
    ImageDraw.Draw(dot).ellipse([22 * S, 22 * S, 42 * S, 42 * S], fill=YELLOW + (255,), outline=(255, 255, 255, 255), width=3 * S)
    dglow = Image.new("RGBA", (64 * S, 64 * S), YELLOW + (0,))
    ImageDraw.Draw(dglow).ellipse([14 * S, 14 * S, 50 * S, 50 * S], fill=YELLOW + (200,))
    dglow = dglow.filter(ImageFilter.GaussianBlur(7 * S))
    frames = []
    for i in range(N["stegodon"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        a = base.copy()
        km = ramp(t, t_meat - 0.05, t_meat + 0.3)
        if km > 0:  # the meaty zones glow red and pulse; they calm down once the cut marks take over
            lvl = km * (0.62 + 0.22 * math.sin(2 * math.pi * 2.0 * (t - t_meat))) * (1 - 0.4 * ramp(t, t_cut0, t_cut0 + 0.4))
            ma = (meat * lvl)[..., None]
            a = a * (1 - ma) + ma * np.array(RED, np.float32)
        im = to_img(a).convert("RGBA")
        im.alpha_composite(sk)
        kh = ramp(t, t_hob, t_hob + 0.7)
        if kh > 0:  # the hobbit comes in from the right toward the hind feet
            dx = round(70 * (1 - kh))
            m = np.roll(hob, dx, 1) * kh
            g = np.roll(hob_glow, dx, 1) * kh
            f = np.asarray(im.convert("RGB"), np.float32) + (g * 0.3)[..., None] * 255
            f = f * (1 - 0.9 * m[..., None]) + 0.9 * m[..., None] * np.array([250, 246, 236], np.float32)
            im = to_img(f).convert("RGBA")
        if km > 0:
            for cx, cy, _, _ in MEAT:
                k = pop(t, t_meat + 0.08, 0.3)
                put1(im, fang, cx + 10, cy - 20, a=min(1, k), scale=max(0.01, k))
            put1(im, lg_red, 270, 1248, a=km)
        for j, (x, y) in enumerate(CUTS):
            t0 = t_cut + 0.045 * j
            if t >= t0:
                k = pop(t, t0, 0.25)
                put1(im, dglow, x, y, a=0.8 * min(1, k) * (0.75 + 0.25 * math.sin(9 * (t - t0))))
                put1(im, dot, x, y, scale=max(0.01, k))
        if t >= t_cut0:
            k = pop(t, t_cut0 + 0.05, 0.3)
            put1(im, flake, 600, 1080, a=min(1, k), scale=max(0.01, k))
        if t >= t_cut:
            put1(im, lg_yel, 765, 1248, a=ramp(t, t_cut, t_cut + 0.25))
        frames.append(to_img(push(np.asarray(im.convert("RGB"), np.float32), 1 + 0.035 * i / N["stegodon"])))
    return frames


# ---------- the hobbit crumbles ----------
def skema_punah(times=None):
    bg0 = title_shade(dusk(cover("img/5438620.jpg", 0.72)), 0.38)
    X0, G, HH = 560, 1150, 360
    m0 = figure_mask(HOBBIT, X0, G, HH)
    t0, t1 = 1.40, 2.50  # from "sudah" until well into "punah..."
    order = 0.55 * noise((H, W), [(38, 0.6), (9, 0.4)], 5) + 0.45 * np.clip((XX - (X0 - 70)) / 140, 0, 1)
    tt = np.linspace(0, 3, 601)
    th = np.array([ramp(x, t0, t1) * 1.15 - 0.07 for x in tt])
    rng = np.random.default_rng(39)
    ys, xs = np.nonzero(m0 > 0.5)
    pick = rng.choice(len(xs), 2600, replace=False)
    px, py = xs[pick].astype(np.float32), ys[pick].astype(np.float32)
    rel = np.interp(order[ys[pick], xs[pick]], th, tt)  # when the dissolve front reaches each mote
    size = rng.uniform(1.4, 3.4, len(pick))
    phase = rng.uniform(0, 6.3, len(pick))
    vx, vy = rng.uniform(110, 300, len(pick)), rng.uniform(30, 150, len(pick))  # each flake its own drift, so the cloud spreads
    frames = []
    for i in range(N["punah"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        z = 1 + 0.04 * i / N["punah"]
        bg = push(bg0, z)
        thr = ramp(t, t0, t1) * 1.15 - 0.07
        m = m0 * np.clip((order - thr) / 0.04, 0, 1)
        out = light_up(bg, m, beam_rim=1.1, halo=1.0, alpha=ramp(t, 0, 0.2))
        age = t - rel
        live = (age > 0) & (age < 1.1)
        if live.any():  # the silhouette breaks into dark flakes that drift off with the air from the cave mouth
            lay = Image.new("L", (W, H), 0)
            d = ImageDraw.Draw(lay)
            for x, y, s, ph, g, ux, uy in zip(px[live], py[live], size[live], phase[live], age[live], vx[live], vy[live]):
                xx = x + ux * g ** 1.25 + 22 * math.sin(4 * g + ph) * g
                yy = y - uy * g - 60 * g * g + 18 * math.cos(3 * g + ph) * g
                al = int(235 * max(0.0, 1 - g / 1.1) ** 1.6)
                ss = s * (1 - 0.5 * g / 1.1)
                d.ellipse([xx - ss, yy - ss, xx + ss, yy + ss], fill=al)
            mote = (np.asarray(lay.filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255)[..., None]
            out = out * (1 - mote) + mote * np.array([16, 14, 14], np.float32)
        frames.append(to_img(out))
    return frames


FUNCS = {"ukur": skema_ukur, "dugaan": skema_dugaan, "gua": skema_gua, "stegodon": skema_stegodon, "punah": skema_punah}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k]
    os.makedirs("clips", exist_ok=True)
    for name in args or ["foto"] + list(N):
        if name == "foto":
            foto()
            continue
        frames = FUNCS[name](times)
        if out:
            sheet(frames, name, out)
        else:
            encode(frames, OUT[name])
