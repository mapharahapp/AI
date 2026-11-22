"""Schematic animations for Titik Heran #74 (run in the episode work dir; writes clips/skema_garis.mp4, skema_kontak.mp4,
skema_buku.mp4, skema_kartu.mp4, skema_mantel.mp4, skema_kikis.mp4).
garis: Pixabay photo 7924473 (Grand Canyon, eastern inner gorge), right part, slow push; a glowing yellow line is drawn
  along the base of the pale Tapeats cliff, over the dark inner-gorge rock (the Great Unconformity; position approximate,
  tagged "skema"); pill "THE GREAT UNCONFORMITY". The first GARIS_OFF seconds have no line and run as the photo.
kontak: Higgsfield H1 close-up (tagged "ilustrasi"), the sandstone/schist contact glows, a bracket on the dark rock and
  pill "1,7 MILIAR TAHUN".
buku: a book of Earth's history seen from the page edges: sandstone pages on top (±500 JUTA TAHUN), dark schist pages
  at the bottom (1,7 MILIAR TAHUN); the cream pages between are torn out and fly away, a red dashed outline marks the
  hole, pill "±1,2 MILIAR TAHUN" and "HILANG!".
kartu: journal-style card, no logo: "jurnal Nature · Nov 2026", Univ. of Wollongong (Australia), Great Unconformity,
  highlight "dalangnya: ???" (Dhungana & Flament, Nature 659, 2026).
mantel: cross-section (sediment layers, old crust, hot mantle); red arrows rise in the mantle and the crust bulges up
  into a dome (Live Science: heat-driven mantle circulation pushed the regions upward).
kikis: the same dome under rain; everything above a falling level washes away grain by grain until the land is flat
  and the old crust shows at the centre.
Event times are seconds from the start of each clip, read off `render.py 74 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < ~640) and the captions (y >= 1210).
usage: python3 skema74.py [garis|kontak|buku|kartu|mantel|kikis ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed, text_sprite
from skema35 import sheet
from skema37 import to_img, put1, noise
from skema46 import pill, ease, wanted, path_upto

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
WHITE, RED = (255, 255, 255), (232, 44, 40)
GARIS_OFF = 16 / FPS          # frames of shot 02 ("yang" -> "lebih") in `render.py 74 plan`
N = {"garis": 108, "kontak": 124, "buku": 84, "kartu": 80, "mantel": 62, "kikis": 46}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 74 plan`: garis = shot 02 (0.53 s) + shot 03 ("lebih" 0.05, "satu" 0.74, "miliar" 1.12, "tahun" 1.50,
# cut 2.93); kontak "bawahnya" 0.17, "batu" 1.08, "satu" 1.62, "tahun" 3.14, cut 3.97; buku "atasnya" 0.17, "cuma" 0.90,
# "lima" 1.21, "tahun" 1.97, cut 2.67; kartu "studi" 0.46, "jurnal" 1.29, "Nature" 1.60, "menunjuk" 2.09, cut 2.57;
# mantel "Panasnya" 0.04, "mengangkat" 0.59, "benua" 1.24, cut 2.00; kikis "mengikisnya" 0.04, "habis" 0.84, cut 1.47
T = {"line0": GARIS_OFF + 0.06, "line1": GARIS_OFF + 0.80, "gpill": GARIS_OFF + 1.05,
     "k_line0": 0.12, "k_line1": 0.75, "k_brk": 1.05, "k_pill": 1.55,
     "b_bot": 0.0, "b_top": 0.16, "tear0": 0.80, "tear1": 1.45, "hole": 1.45, "b_pill": 1.70, "b_hil": 1.95,
     "l1": 0.30, "l2": 0.50, "l3": 0.85, "l4": 2.00,
     "arrows": 0.05, "up0": 0.45, "up1": 1.55,
     "e0": 0.04, "e1": 1.00}

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def backdrop(top, bot, glow=None, gx=540, gy=900):
    v = (YY / H)[..., None]
    a = np.array(top, np.float32) * (1 - v) + np.array(bot, np.float32) * v
    if glow:
        a = a + np.exp(-((XX - gx) ** 2 + (YY - gy) ** 2) / (2 * 430 ** 2))[..., None] * np.array(glow, np.float32)
    return to_img(a).convert("RGBA")


def strokes(paths, u=1.0, col=WHITE + (255,), width=5.0):
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for pts in paths:
        p = pts if u >= 1 else path_upto(pts, max(u, 0.0))
        if len(p) > 1:
            d.line([(x * S, y * S) for x, y in p], fill=col, width=max(1, int(width * S)), joint="curve")
    return lay.resize((W, H), Image.LANCZOS)


def glowing(base, paths, u, col, width, glow=0.8, blur=8):
    if u <= 0:
        return
    ln = strokes(paths, u, col + (255,), width)
    if glow > 0:
        g = ln.filter(ImageFilter.GaussianBlur(blur))
        g.putalpha(g.getchannel("A").point(lambda v: int(min(255, v * 1.8 * glow))))
        base.alpha_composite(g)
    base.alpha_composite(ln)


def zoom_pt(p, z, c):
    return (c[0] + (p[0] - c[0]) * z, c[1] + (p[1] - c[1]) * z)


def push(bg, z, c):
    w, h = W / z, H / z
    x0, y0 = c[0] - w * c[0] / W, c[1] - h * c[1] / H
    return bg.transform((W, H), Image.EXTENT, (x0, y0, x0 + w, y0 + h), Image.BICUBIC)


def resample_line(pts, n=120):
    """densify a polyline so path_upto draws it smoothly"""
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        k = max(2, int(math.hypot(x1 - x0, y1 - y0) / 6))
        out += [(x0 + (x1 - x0) * i / k, y0 + (y1 - y0) * i / k) for i in range(k)]
    return out + [pts[-1]]


# ---------- garis: the line on the canyon photo ----------
GX0 = 790                                     # left edge of the 9:16 window in the 1280x851 photo
GK = H / 851                                  # photo px -> video px
G_SRC = [(790, 430), (830, 428), (875, 429), (905, 433), (922, 444), (936, 460), (975, 468), (1020, 476), (1060, 484),
         (1105, 495), (1150, 507), (1185, 520), (1215, 528), (1270, 526)]


def garis_bg():
    im = Image.open("img/7924473.jpg").convert("RGB")
    crop = im.crop((GX0, 0, GX0 + 851 * 9 / 16, 851))
    return crop.resize((W, H), Image.LANCZOS).convert("RGBA")


def skema_garis(times=None):
    bg = garis_bg()
    line = resample_line([((x - GX0) * GK, y * GK) for x, y in G_SRC])
    C = (540, 1080)
    gp = pill("THE GREAT UNCONFORMITY", 36, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220))
    frames = []
    dur = N["garis"] / FPS
    for i in range(N["garis"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        z = 1.0 + 0.08 * t / dur
        im = push(bg, z, C)
        u = ease((t - T["line0"]) / (T["line1"] - T["line0"]))
        if u > 0:
            pts = [zoom_pt(p, z, C) for p in line]
            puls = 1.0 if t < T["line1"] else 0.8 + 0.25 * math.sin((t - T["line1"]) * 9)
            glowing(im, [pts], u, YELLOW, 7, glow=puls, blur=9)
        k = pop(t, T["gpill"], 0.3)
        if k > 0:
            lead = Image.new("RGBA", (W, H))
            ly = zoom_pt((540, 900), z, C)[1]
            y_line = zoom_pt((0, 1075), z, C)[1]
            ImageDraw.Draw(lead).line([(540, 896), (540, 896 + (y_line - 900) * ramp(t, T["gpill"], T["gpill"] + 0.2))],
                                      fill=YELLOW + (230,), width=4)
            im.alpha_composite(lead)
            put1(im, gp, 540, 862, scale=min(k, 1.06))
        frames.append(im.convert("RGB"))
    return frames


# ---------- kontak: H1 close-up ----------
KZ, KY = 1.12, 0.364                          # H1 zoom (width 1080 * KZ) and the contact's height in H1


def kontak_bg():
    im = Image.open("img/H1.jpg").convert("RGB")
    w = round(W * KZ)
    h = round(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    x0 = (w - W) // 2
    return im.crop((x0, 0, x0 + W, H)).convert("RGBA"), KY * h


def skema_kontak(times=None):
    bg, cy = kontak_bg()
    C = (540, cy)
    line = resample_line([(0, cy + 2), (W, cy - 2)])
    p17 = pill("1,7 MILIAR TAHUN", 42, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220))
    frames = []
    dur = N["kontak"] / FPS
    for i in range(N["kontak"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        z = 1.0 + 0.07 * t / dur
        im = push(bg, z, C)
        u = ease((t - T["k_line0"]) / (T["k_line1"] - T["k_line0"]))
        puls = 1.0 if t < T["k_line1"] else 0.8 + 0.25 * math.sin((t - T["k_line1"]) * 8)
        glowing(im, [line], u, YELLOW, 6, glow=puls, blur=9)
        b = ramp(t, T["k_brk"], T["k_brk"] + 0.3)
        if b > 0:                                 # bracket down the right side of the dark rock
            x = 930
            y0, y1 = cy + 30, cy + 30 + 470 * b
            br = Image.new("RGBA", (W, H))
            d = ImageDraw.Draw(br)
            d.line([(x - 26, y0), (x, y0), (x, y1), (x - 26, y1)], fill=WHITE + (230,), width=5, joint="curve")
            im.alpha_composite(br)
        put1(im, p17, 560, 1100, scale=min(pop(t, T["k_pill"], 0.3), 1.06))
        frames.append(im.convert("RGB"))
    return frames


# ---------- buku: the book with missing pages ----------
BX0, BX1 = 215, 880
TOP0, TOP1, MID1, BOT1 = 676, 786, 1062, 1182
PAGE = 9


def page_texture(y0, y1, base, line, seed, veins=None):
    h = y1 - y0
    n = noise((h, BX1 - BX0), [(18, 0.6), (5, 0.4)], seed)
    a = np.array(base, np.float32)[None, None, :] * (0.86 + 0.24 * n[..., None])
    for yy in range(0, h, PAGE):
        a[yy:yy + 2] = np.array(line, np.float32)
    if veins:
        v = noise((h, BX1 - BX0), [(40, 0.7), (12, 0.3)], seed + 1)
        m = (np.abs(v - 0.5) < 0.018)[..., None]
        a = np.where(m, np.array(veins, np.float32), a)
    img = to_img(a).convert("RGBA")
    return img


def skema_buku(times=None):
    bg = backdrop((40, 30, 22), (10, 8, 6), glow=(30, 20, 10), gy=930)
    top = page_texture(TOP0, TOP1, (214, 150, 100), (150, 96, 60), 3)
    mid = page_texture(TOP1, MID1, (236, 226, 200), (196, 184, 156), 5)
    bot = page_texture(MID1, BOT1, (72, 70, 78), (40, 38, 44), 7, veins=(206, 150, 150))
    spine = Image.new("RGBA", (W * S, H * S))
    ImageDraw.Draw(spine).rounded_rectangle([168 * S, (TOP0 - 10) * S, 222 * S, (BOT1 + 10) * S], radius=22 * S,
                                            fill=(92, 46, 30, 255), outline=(150, 90, 60, 255), width=3 * S)
    spine = spine.resize((W, H), Image.LANCZOS)
    rng = np.random.default_rng(11)
    strips = []
    CH_ = 46                                               # the torn pages leave in six bundles
    nb = math.ceil((MID1 - TOP1) / CH_)
    for k in range(nb):
        y = TOP1 + k * CH_
        strips.append({"y": y, "h": min(CH_, MID1 - y),
                       "t0": T["tear0"] + (T["tear1"] - T["tear0"]) * k / (nb - 1) + rng.uniform(-0.04, 0.04),
                       "vx": rng.uniform(700, 1100) * (1 if k % 2 == 0 else 0.8), "vy": rng.uniform(-520, -160),
                       "rot": rng.uniform(25, 80) * (1 if k % 2 else -1),
                       "img": mid.crop((0, y - TOP1, BX1 - BX0, min(y - TOP1 + CH_, MID1 - TOP1)))})
    p500 = pill("±500 JUTA TAHUN", 34, col=WHITE, bg=(30, 16, 8, 215), edge=(255, 255, 255, 150))
    p17 = pill("1,7 MILIAR TAHUN", 34, col=WHITE, bg=(10, 10, 14, 215), edge=(255, 255, 255, 150))
    p12 = pill("±1,2 MILIAR TAHUN", 52, col=(20, 20, 20), bg=YELLOW + (248,), edge=(255, 255, 255, 230))
    hil = text_sprite([("HILANG!", 60, RED, True)])
    frames = []
    for i in range(N["buku"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        sh = Image.new("RGBA", (W, H))
        ImageDraw.Draw(sh).rectangle([BX0 + 14, TOP0 + 18, BX1 + 14, BOT1 + 18], fill=(0, 0, 0, 150))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
        im.alpha_composite(spine)
        im.alpha_composite(top, (BX0, TOP0))
        im.alpha_composite(bot, (BX0, MID1))
        flying = Image.new("RGBA", (W, H))
        for s_ in strips:
            dt = t - s_["t0"]
            if dt <= 0:
                im.alpha_composite(s_["img"], (BX0, s_["y"]))
                continue
            if dt > 0.75:
                continue
            sp = s_["img"].rotate(s_["rot"] * dt, expand=True, resample=Image.BICUBIC)
            a = 1 - ramp(dt, 0.3, 0.75)
            sp.putalpha(sp.getchannel("A").point(lambda q, a=a: int(q * a)))
            cx = BX0 + (BX1 - BX0) / 2 + s_["vx"] * dt
            cy = s_["y"] + s_["h"] / 2 + s_["vy"] * dt + 900 * dt * dt
            flying.alpha_composite(sp, (round(cx - sp.width / 2), round(cy - sp.height / 2)))
        stub = Image.new("RGBA", (W, H))                       # torn stubs at the spine
        ds = ImageDraw.Draw(stub)
        for s_ in strips:
            if t > s_["t0"]:
                for yy in range(s_["y"], s_["y"] + s_["h"], PAGE):
                    jag = 8 + 14 * abs(math.sin(yy * 1.7))
                    ds.polygon([(BX0, yy), (BX0 + jag, yy + 2), (BX0 + jag * 0.6, yy + PAGE - 1), (BX0, yy + PAGE - 1)],
                               fill=(236, 226, 200, 255))
        im.alpha_composite(stub)
        h = ramp(t, T["hole"], T["hole"] + 0.2)
        if h > 0:
            lay = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(lay)
            dashed(d, [(BX0 + 26, TOP1 + 6), (BX1 - 4, TOP1 + 6), (BX1 - 4, MID1 - 6), (BX0 + 26, MID1 - 6), (BX0 + 26, TOP1 + 6)],
                   RED + (int(235 * h),), 5, dash=22, gap=14)
            im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        im.alpha_composite(flying)
        put1(im, p17, (BX0 + BX1) / 2, (MID1 + BOT1) / 2, scale=min(pop(t, T["b_bot"], 0.25), 1.05))
        put1(im, p500, (BX0 + BX1) / 2, (TOP0 + TOP1) / 2, scale=min(pop(t, T["b_top"], 0.25), 1.05))
        put1(im, p12, (BX0 + BX1) / 2 + 10, 872, scale=min(pop(t, T["b_pill"], 0.3), 1.06))
        put1(im, hil, (BX0 + BX1) / 2 + 10, 1018, a=ramp(t, T["b_hil"], T["b_hil"] + 0.1),
             scale=min(pop(t, T["b_hil"], 0.25), 1.08))
        frames.append(im.convert("RGB"))
    return frames


# ---------- kartu: the journal card ----------
def skema_kartu(times=None):
    bg = backdrop((52, 20, 12), (12, 5, 3))
    CW, CH, CX0, CY0 = 860, 520, 110, 668
    card = Image.new("RGBA", (CW * S, CH * S))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, CW * S - 1, CH * S - 1], radius=22 * S, fill=(250, 248, 242, 255))
    d.rectangle([0, 0, CW * S, 14 * S], fill=(150, 36, 24, 255))
    F = lambda f, s: ImageFont.truetype(f, s * S)
    lines = [("jurnal Nature · Nov 2026", F(XB, 46), (150, 36, 24), 62, "l1"),
             ("Univ. of Wollongong (Australia)", F(MED, 38), (40, 40, 40), 146, "l2"),
             ("Great Unconformity", F(XB, 64), (20, 20, 20), 212, "l3"),
             ("dalangnya: ???", F(XB, 50), (20, 20, 20), 394, "l4")]
    sprites = []
    for text, font, col, y, key in lines:
        lay = Image.new("RGBA", (CW * S, CH * S))
        ImageDraw.Draw(lay).text((54 * S, y * S), text, font=font, fill=col + (255,))
        sprites.append((lay, key))
    hl = Image.new("RGBA", (CW * S, CH * S))
    ImageDraw.Draw(hl).rounded_rectangle([38 * S, 380 * S, 470 * S, 466 * S], radius=14 * S, fill=YELLOW + (255,))
    rule = Image.new("RGBA", (CW * S, CH * S))
    ImageDraw.Draw(rule).line([(54 * S, 330 * S), ((CW - 54) * S, 330 * S)], fill=(200, 196, 186, 255), width=3 * S)
    frames = []
    for i in range(N["kartu"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        c = card.copy()
        c.alpha_composite(rule)
        if t > T["l4"]:
            h2 = hl.copy()
            h2.putalpha(h2.getchannel("A").point(lambda q, a=ramp(t, T["l4"], T["l4"] + 0.15): int(q * a)))
            c.alpha_composite(h2)
        for lay, key in sprites:
            a = ramp(t, T[key], T[key] + 0.18)
            if a > 0:
                l2 = lay.copy()
                l2.putalpha(l2.getchannel("A").point(lambda q, a=a: int(q * a)))
                c.alpha_composite(l2)
        c = c.resize((CW, CH), Image.LANCZOS)
        im = bg.copy()
        sh = Image.new("RGBA", (W, H))
        y = CY0 + 700 * (1 - ease(t / 0.35))
        ImageDraw.Draw(sh).rounded_rectangle([CX0 + 10, y + 18, CX0 + CW + 10, y + CH + 18], radius=22, fill=(0, 0, 0, 120))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
        im.alpha_composite(c, (CX0, round(y)))
        frames.append(im.convert("RGB"))
    return frames


# ---------- mantel / kikis: the cross-section ----------
SURF, SED1, CRUST1, BOTTOM = 860, 948, 1080, 1200     # flat surface, sediment base, crust base, bottom of the section
AMAX, SIG = 150, 250


def section_base():
    """the flat cross-section as an array (rows SURF..BOTTOM); the mantle is drawn per frame"""
    h = BOTTOM - SURF
    a = np.zeros((h, W, 3), np.float32)
    n = noise((h, W), [(30, 0.5), (8, 0.5)], 21)
    cols = [(198, 112, 72), (222, 176, 124), (176, 96, 62), (226, 196, 146)]
    for k, c in enumerate(cols):                           # four sediment layers of 22 px
        y0, y1 = k * 22, (k + 1) * 22
        a[y0:y1] = np.array(c, np.float32) * (0.85 + 0.25 * n[y0:y1, :, None])
        a[y1 - 2:y1] *= 0.75
    c0 = SED1 - SURF
    v = noise((CRUST1 - SED1, W), [(46, 0.7), (14, 0.3)], 23)
    crust = np.array((66, 64, 72), np.float32) * (0.8 + 0.4 * n[c0:CRUST1 - SURF, :, None])
    crust = np.where((np.abs(v - 0.5) < 0.02)[..., None], np.array((196, 140, 140), np.float32), crust)
    a[c0:CRUST1 - SURF] = crust
    return a


def mantle_rgb(t, ys):
    """hot mantle colour for rows ys (absolute y), flickering a little"""
    k = np.clip((ys - CRUST1 + 60) / 180, 0, 1)[:, None]
    base = np.array((255, 120, 30), np.float32) * (1 - k) + np.array((170, 30, 10), np.float32) * k
    fl = 0.9 + 0.1 * np.sin(XX[0][None, :] / 37 + t * 5 + ys[:, None] / 23)
    return base[:, None, :] * fl[..., None]


SKY = None


def sky():
    global SKY
    if SKY is None:
        SKY = np.asarray(backdrop((24, 30, 40), (8, 10, 14)).convert("RGB"), np.float32)
    return SKY


def lifted(base, D, t, level=None):
    """the section with column x pushed up by D[x]; material above `level` (if given) is gone"""
    out = sky().copy()
    ys = np.arange(SURF - AMAX - 10, BOTTOM, dtype=np.float32)
    src = ys[:, None] + D[None, :] - SURF                  # row in the flat section
    rows = np.clip(src, 0, BOTTOM - SURF - 1).astype(int)
    cols = np.broadcast_to(np.arange(W), rows.shape)
    sec = base[rows, cols]
    m = mantle_rgb(t, ys)
    sec = np.where((src >= CRUST1 - SURF)[..., None], m, sec)
    keep = src >= 0
    if level is not None:
        keep &= ys[:, None] >= level
    y0 = int(ys[0])
    region = out[y0:BOTTOM]
    out[y0:BOTTOM] = np.where(keep[..., None], sec, region)
    out[BOTTOM:BOTTOM + 3] = 40
    return out


def arrows(im, t, a):
    if a <= 0:
        return
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for k, x in enumerate((380, 540, 700)):
        ph = ((t * 1.3 + k * 0.33) % 1.0)
        y = 1190 - 70 * ph
        s_ = 1.25 if x == 540 else 0.9
        al = int(255 * a * (1 - abs(ph - 0.5) * 0.8))
        pts = [(x - 16 * s_, y), (x - 16 * s_, y - 40 * s_), (x - 34 * s_, y - 40 * s_), (x, y - 80 * s_),
               (x + 34 * s_, y - 40 * s_), (x + 16 * s_, y - 40 * s_), (x + 16 * s_, y)]
        d.polygon([(px * S, py * S) for px, py in pts], fill=(255, 236, 160, al), outline=(150, 20, 10, al))
    lay = lay.resize((W, H), Image.LANCZOS)
    g = lay.filter(ImageFilter.GaussianBlur(8))
    im.alpha_composite(g)
    im.alpha_composite(lay)


def dome(A):
    return A * np.exp(-((np.arange(W, dtype=np.float32) - 540) / SIG) ** 2)


def section_labels():
    lm = text_sprite([("mantel panas", 34, WHITE, True)])
    lk = text_sprite([("kerak benua", 32, WHITE, True)])
    return lm, lk


def skema_mantel(times=None):
    base = section_base()
    lm, lk = section_labels()
    frames = []
    for i in range(N["mantel"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        A = AMAX * ease((t - T["up0"]) / (T["up1"] - T["up0"]))
        D = dome(A)
        im = to_img(lifted(base, D, t)).convert("RGBA")
        arrows(im, t, ramp(t, T["arrows"], T["arrows"] + 0.2))
        put1(im, lm, 190, 1160, a=ramp(t, 0.1, 0.3))
        put1(im, lk, 190, 1030 - D[190], a=ramp(t, 0.2, 0.4))
        frames.append(im.convert("RGB"))
    return frames


def rain(im, t):
    lay = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(5)
    for _ in range(90):
        x0, y0, sp = rng.uniform(-200, W), rng.uniform(0, 1), rng.uniform(1300, 1800)
        y = 640 + ((y0 * 520 + sp * t) % 520)
        x = x0 + (y - 640) * 0.25
        d.line([(x, y), (x + 9, y + 36)], fill=(190, 215, 255, 120), width=2)
    im.alpha_composite(lay)


def skema_kikis(times=None):
    base = section_base()
    lm, lk = section_labels()
    D = dome(AMAX)
    top0 = SURF - AMAX
    rng = np.random.default_rng(9)
    grains = [{"x": rng.uniform(300, 780), "t0": rng.uniform(T["e0"], T["e1"]), "vx": rng.uniform(60, 260),
               "c": (int(rng.uniform(170, 230)), int(rng.uniform(100, 170)), int(rng.uniform(60, 110)))} for _ in range(160)]
    frames = []
    for i in range(N["kikis"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        L = top0 + (SURF - top0) * ease((t - T["e0"]) / (T["e1"] - T["e0"]))
        im = to_img(lifted(base, D, t, level=L)).convert("RGBA")
        rain(im, t)
        lay = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(lay)
        for g in grains:
            dt = t - g["t0"]
            if dt <= 0 or dt > 0.6:
                continue
            y_s = SURF - D[int(g["x"])]
            ys = top0 + (SURF - top0) * ease((g["t0"] - T["e0"]) / (T["e1"] - T["e0"]))
            if ys < y_s:                                   # this column had nothing to erode at that time
                continue
            sgn = 1 if g["x"] >= 540 else -1
            x = g["x"] + sgn * g["vx"] * dt
            y = ys + 260 * dt * dt + 40 * dt
            a = int(255 * (1 - dt / 0.6))
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=g["c"] + (a,))
        im.alpha_composite(lay)
        arrows(im, t, 1 - ramp(t, 0.2, 0.6))
        put1(im, lm, 190, 1160, a=1 - ramp(t, 0.2, 0.5))
        put1(im, lk, 190, 1030 - D[190])
        frames.append(im.convert("RGB"))
    return frames


FUN = {"garis": skema_garis, "kontak": skema_kontak, "buku": skema_buku, "kartu": skema_kartu, "mantel": skema_mantel,
       "kikis": skema_kikis}

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
