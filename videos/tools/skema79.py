"""Schematic animations for Titik Heran #79 (run in the episode work dir; writes clips/skema_jam.mp4, skema_buku.mp4,
skema_kbbi.mp4, and img/H2c.jpg).
jam: Arif's Higgsfield H1 (tub in a VOC house in Ambon) dimmed, slow push to the tub; an hourglass with falling sand,
  4 sun icons pop in one by one ("hari") and a pill "+7 jam"; on "menolak makan" three food icons (ikan, kerang,
  rumput) are struck out (Fallours: it refused fish, shellfish, moss and grass); on "lalu mati" the light dies.
buku: aged paper title card in the style of the book (no facsimile): POISSONS, ECREVISSES ET CRABES, an empty plate
  frame with a fish-tail outline, "Amsterdam +-1719 · Louis Renard · lukisan Samuel Fallours"; pill "menurut
  peneliti (Pietsch)"; a red stamp "DIKARANG?" drops on "dikarang".
kbbi: H3 (dugong, blurred and dimmed) behind a white dictionary card "du·yung (n) binatang laut yang menyusui", KBBI;
  a yellow pill "= DUGONG" pops on "disebut".
h2crop: H2 cropped to x 523-1536, y 800-2601 so the modern car outside the window is out of frame; the pseudo-Latin
  caption under the engraving is softened.
Event times are seconds from the start of each clip, read off `render.py 79 plan`. Text stays out of the watermark
band (y 935-985 around the centre), the title zone (y < ~640) and the captions (y >= 1210).
usage: python3 skema79.py [jam|buku|kbbi|h2crop ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, text_sprite
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
SERB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERI = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SER = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
WHITE, RED, INK = (255, 255, 255), (214, 38, 34), (58, 40, 22)
N = {"jam": 130, "buku": 100, "kbbi": 54}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 79 plan`: jam = shot 06 ("Empat" 0.04, "hari" 0.48, "tujuh" 0.85, "jam" 1.23, "ia" 1.98, "menolak"
# 2.13, "makan" 2.55, "lalu" 3.41, "mati" 3.79, cut 4.23); buku = shot 09 ("Kini" 0.03, "peneliti" 0.73, "menduga"
# 1.22, "dikarang" 2.50, cut 3.23); kbbi = shot 12 ("yang" 0.04, "sini" 0.48, "disebut" 0.93, cut 1.70)
T = {"glass": 0.0, "day0": 0.45, "jam7": 0.88, "food": 2.10, "x0": 2.55, "dark0": 3.40, "dark1": 4.0,
     "card": 0.0, "piet": 0.75, "stamp": 2.45,
     "kcard": 0.0, "kdef": 0.25, "kdug": 0.93}

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def vignette(r0, soft):
    d = np.sqrt(((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2)
    return np.clip(1 - (d - r0) / soft, 0, 1)[..., None]


def push_frame(im, z, cx, cy):
    """crop of a W x H-shaped image zoomed by z around (cx, cy) in its own pixels"""
    w_, h_ = im.width / z, im.width / z * H / W
    x0 = min(max(cx - w_ / 2, 0), im.width - w_)
    y0 = min(max(cy - h_ / 2, 0), im.height - h_)
    return im.transform((W, H), Image.EXTENT, (x0, y0, x0 + w_, y0 + h_), Image.BICUBIC)


# ---------- jam ----------
def hourglass(t):
    sp = Image.new("RGBA", (220 * S, 300 * S))
    d = ImageDraw.Draw(sp)
    c = 110 * S
    gl = (235, 245, 255, 235)
    top, mid, bot = 30 * S, 150 * S, 270 * S
    d.rectangle([20 * S, 10 * S, 200 * S, 30 * S], fill=(150, 104, 52, 255))
    d.rectangle([20 * S, 270 * S, 200 * S, 290 * S], fill=(150, 104, 52, 255))
    d.line([(40 * S, top), (c - 8 * S, mid), (40 * S, bot)], fill=gl, width=5 * S, joint="curve")
    d.line([(180 * S, top), (c + 8 * S, mid), (180 * S, bot)], fill=gl, width=5 * S, joint="curve")
    u = min(max(t / 4.0, 0), 1)                       # sand runs from the top bulb to the bottom one
    sand = (236, 196, 110, 255)
    ht = (1 - u) * 90 * S
    if ht > 2:
        y = mid - 12 * S - ht
        k = (mid - y) / (mid - top)
        d.polygon([(c - 62 * S * k, y), (c + 62 * S * k, y), (c, mid - 6 * S)], fill=sand)
    hb = u * 80 * S + 6 * S
    d.polygon([(48 * S, bot - 4 * S), (172 * S, bot - 4 * S), (c + 20 * S, bot - hb), (c - 20 * S, bot - hb)], fill=sand)
    if u < 1:
        d.line([(c, mid - 4 * S), (c, bot - hb)], fill=sand, width=3 * S)
    return sp


def sun_icon(col=YELLOW):
    sp = Image.new("RGBA", (90 * S, 90 * S))
    d = ImageDraw.Draw(sp)
    c = 45 * S
    for k in range(8):
        a = math.pi * k / 4
        d.line([(c + 24 * S * math.cos(a), c + 24 * S * math.sin(a)), (c + 40 * S * math.cos(a), c + 40 * S * math.sin(a))], fill=col + (255,), width=6 * S)
    d.ellipse([c - 18 * S, c - 18 * S, c + 18 * S, c + 18 * S], fill=col + (255,))
    return sp


def food_icon(kind):
    sp = Image.new("RGBA", (130 * S, 130 * S))
    d = ImageDraw.Draw(sp)
    d.ellipse([4 * S, 4 * S, 126 * S, 126 * S], fill=(20, 24, 30, 200), outline=(255, 255, 255, 200), width=3 * S)
    col = (255, 255, 255, 240)
    if kind == "ikan":
        d.ellipse([28 * S, 46 * S, 88 * S, 84 * S], fill=col)
        d.polygon([(84 * S, 65 * S), (106 * S, 46 * S), (106 * S, 84 * S)], fill=col)
        d.ellipse([38 * S, 58 * S, 46 * S, 66 * S], fill=(20, 24, 30, 255))
    elif kind == "kerang":
        cx, cy = 65 * S, 88 * S
        d.pieslice([25 * S, 40 * S, 105 * S, 120 * S], 180, 360, fill=col)
        for k in range(1, 6):
            a = math.pi + math.pi * k / 6
            d.line([(cx, cy - 8 * S), (cx + 40 * S * math.cos(a), 80 * S + 40 * S * math.sin(a))], fill=(20, 24, 30, 255), width=3 * S)
        d.rectangle([52 * S, 80 * S, 78 * S, 94 * S], fill=col)
    else:  # rumput laut: three wavy blades
        for k, x0 in enumerate((45, 65, 85)):
            pts = [((x0 + 9 * math.sin(y / 11 + k)) * S, y * S) for y in range(30, 106, 3)]
            d.line(pts, fill=(150, 230, 150, 245), width=7 * S, joint="curve")
    return sp


def skema_jam(times=None):
    src = Image.open("img/H1.jpg").convert("RGB")
    vig = vignette(0.6, 0.7)
    suns = sun_icon()
    j7 = pill("+7 jam", 44, col=(30, 22, 0), bg=YELLOW + (245,), edge=(255, 255, 255, 230))
    foods = [(food_icon(k), k) for k in ("ikan", "kerang", "rumput")]
    labs = {k: text_sprite([(k, 28, WHITE, True)]) for _, k in foods}
    frames = []
    for i in range(N["jam"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        z = 1.0 + 0.16 * ease(t / (N["jam"] / FPS))
        f = push_frame(src, z, 0.47 * src.width, 0.72 * src.height)
        dark = 0.5 - 0.32 * ramp(t, T["dark0"], T["dark1"])
        a = np.asarray(f, np.float32) * dark * (0.55 + 0.45 * vig)
        im = to_img(a).convert("RGBA")
        g = hourglass(t)
        put1(im, g, 540, 800, scale=min(pop(t, T["glass"], 0.3), 1.03) * 0.9, a=1 - 0.6 * ramp(t, T["dark0"], T["dark1"]))
        # 4 days: suns pop one by one on either side of the hourglass, then "+7 jam"
        fade = 1 - 0.7 * ramp(t, T["dark0"], T["dark1"])
        for k, (x, y) in enumerate([(190, 700), (890, 700), (190, 880), (890, 880)]):
            put1(im, suns, x, y, scale=min(pop(t, T["day0"] + 0.1 * k, 0.25), 1.05) * 0.9, a=fade)
        put1(im, j7, 890, 975, scale=min(pop(t, T["jam7"], 0.3), 1.05), a=fade)
        # menolak makan: the food icons, struck out
        for k, (sp, name) in enumerate(foods):
            x = 300 + 240 * k
            s_ = min(pop(t, T["food"] + 0.08 * k, 0.25), 1.05)
            put1(im, sp, x, 1080, scale=s_, a=fade)
            put1(im, labs[name], x, 1170, a=fade * ramp(t, T["food"] + 0.1, T["food"] + 0.25))
            v = ease((t - T["x0"] - 0.07 * k) / 0.15)
            if v > 0:
                lay = Image.new("RGBA", (W * S, H * S))
                dl = ImageDraw.Draw(lay)
                r = 58
                dl.line([((x - r) * S, (1080 - r) * S), ((x - r + 2 * r * v) * S, (1080 - r + 2 * r * v) * S)], fill=RED + (int(255 * fade),), width=12 * S)
                dl.line([((x + r) * S, (1080 - r) * S), ((x + r - 2 * r * v) * S, (1080 - r + 2 * r * v) * S)], fill=RED + (int(255 * fade),), width=12 * S)
                im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        frames.append(im.convert("RGB"))
    return frames


# ---------- buku ----------
def paper(w, h, seed=3):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base = np.array([232, 214, 178], np.float32)
    n = rng.normal(0, 1, (h // 6 + 1, w // 6 + 1)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3)), np.float32)[..., None] / 255
    edge = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))[..., None]
    burn = np.clip(1 - edge / 60, 0, 1) ** 1.6
    a = base * (0.9 + 0.12 * n) - burn * np.array([70, 80, 90], np.float32)
    return to_img(a).convert("RGBA")


def tail_outline(d, cx, cy, s, col, width):
    """a fish tail rising from water: two lobes and a tapering body (no torso)"""
    pts = [(cx - 22 * s, cy + 90 * s), (cx - 16 * s, cy + 20 * s), (cx - 6 * s, cy - 30 * s), (cx - 60 * s, cy - 80 * s),
           (cx - 20 * s, cy - 70 * s), (cx, cy - 48 * s), (cx + 20 * s, cy - 70 * s), (cx + 60 * s, cy - 80 * s),
           (cx + 6 * s, cy - 30 * s), (cx + 16 * s, cy + 20 * s), (cx + 22 * s, cy + 90 * s)]
    d.line(pts, fill=col, width=width, joint="curve")
    for k in range(4):
        y = cy - 10 * s + k * 24 * s
        d.arc([cx - 18 * s, y - 8 * s, cx + 18 * s, y + 8 * s], 20, 160, fill=col, width=max(1, width // 2))
    for k in range(3):
        y = cy + 92 * s + k * 10 * s
        d.arc([cx - 80 * s + k * 8 * s, y - 6 * s, cx + 80 * s - k * 8 * s, y + 6 * s], 200, 340, fill=col, width=max(1, width // 2))


def card_sprite():
    cw, ch = 820, 480
    sp = paper(cw * S, ch * S)
    d = ImageDraw.Draw(sp)
    d.rectangle([22 * S, 22 * S, (cw - 22) * S, (ch - 22) * S], outline=INK + (200,), width=3 * S)
    f1 = ImageFont.truetype(SERB, 46 * S)
    f2 = ImageFont.truetype(SERI, 28 * S)
    f3 = ImageFont.truetype(SER, 26 * S)
    d.text((cw / 2 * S, 66 * S), "POISSONS, ÉCREVISSES", font=f1, fill=INK + (255,), anchor="mm")
    d.text((cw / 2 * S, 116 * S), "ET CRABES", font=f1, fill=INK + (255,), anchor="mm")
    d.line([(cw / 2 * S - 120 * S, 148 * S), (cw / 2 * S + 120 * S, 148 * S)], fill=INK + (200,), width=2 * S)
    # the plate: an empty frame with a tail outline (the painting itself is not reproduced)
    d.rectangle([260 * S, 164 * S, 560 * S, 364 * S], outline=INK + (220,), width=3 * S, fill=(222, 202, 162, 255))
    tail_outline(d, 410 * S, 252 * S, 0.8 * S, (70, 100, 96, 255), 4 * S)
    d.text((cw / 2 * S, 398 * S), "Amsterdam ±1719 · Louis Renard", font=f2, fill=INK + (255,), anchor="mm")
    d.text((cw / 2 * S, 432 * S), "lukisan: Samuel Fallours (pelukis VOC di Ambon)", font=f3, fill=INK + (230,), anchor="mm")
    return sp


def stamp_sprite():
    f = ImageFont.truetype(XB, 92 * S)
    x0, y0, x1, y1 = f.getbbox("DIKARANG?")
    w, h = x1 - x0 + 70 * S, y1 - y0 + 50 * S
    sp = Image.new("RGBA", (w + 20 * S, h + 20 * S))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([10 * S, 10 * S, 10 * S + w, 10 * S + h], radius=18 * S, outline=RED + (240,), width=9 * S)
    d.text((10 * S + w / 2, 10 * S + h / 2), "DIKARANG?", font=f, fill=RED + (240,), anchor="mm")
    rng = np.random.default_rng(4)                    # worn ink
    a = np.asarray(sp.getchannel("A"), np.float32)
    holes = rng.random(a.shape) < 0.06
    a[holes] *= 0.35
    sp.putalpha(Image.fromarray(a.astype(np.uint8)))
    return sp.rotate(-10, resample=Image.BICUBIC, expand=True)


def skema_buku(times=None):
    v = (YY / H)[..., None]
    bg = to_img(np.array([46, 32, 20], np.float32) * (1 - v) + np.array([16, 10, 6], np.float32) * v
                + np.exp(-((XX - 540) ** 2 + (YY - 880) ** 2) / (2 * 420 ** 2))[..., None] * np.array([60, 40, 18], np.float32)).convert("RGBA")
    card = card_sprite()
    st = stamp_sprite()
    pp = pill("menurut peneliti (Pietsch)", 34, col=WHITE, bg=(30, 18, 10, 225), edge=(255, 230, 190, 180))
    frames = []
    for i in range(N["buku"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        s = 1.0 + 0.04 * t / (N["buku"] / FPS)
        put1(im, card, 540, 870, scale=s * min(pop(t, T["card"], 0.3), 1.02))
        put1(im, pp, 540, 1160, scale=min(pop(t, T["piet"], 0.3), 1.04))
        u = ramp(t, T["stamp"], T["stamp"] + 0.12)
        if u > 0:
            sc = 1.7 - 0.7 * u
            put1(im, st, 560, 820, scale=sc * 0.95, a=min(1.0, 0.3 + u))
        frames.append(im.convert("RGB"))
    return frames


# ---------- kbbi ----------
def skema_kbbi(times=None):
    h3 = Image.open("img/H3.jpg").convert("RGB")
    bgi = h3.resize((W, round(W * h3.height / h3.width)), Image.LANCZOS).crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(14))
    bg = to_img(np.asarray(bgi, np.float32) * 0.45).convert("RGBA")
    cw, ch = 860, 250
    card = Image.new("RGBA", (cw * S, ch * S))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, cw * S - 1, ch * S - 1], radius=26 * S, fill=(250, 250, 246, 248))
    d.text((48 * S, 72 * S), "du·yung", font=ImageFont.truetype(XB, 74 * S), fill=(20, 24, 30, 255), anchor="lm")
    d.text((372 * S, 82 * S), "n", font=ImageFont.truetype(SERI, 44 * S), fill=(200, 40, 40, 255), anchor="lm")
    d.text((cw * S - 40 * S, 52 * S), "KBBI", font=ImageFont.truetype(XB, 30 * S), fill=(30, 90, 170, 255), anchor="rm")
    defin = Image.new("RGBA", (cw * S, ch * S))
    ImageDraw.Draw(defin).text((48 * S, 168 * S), "binatang laut yang menyusui", font=ImageFont.truetype(MED, 44 * S), fill=(40, 44, 50, 255), anchor="lm")
    dg = pill("= DUGONG", 76, col=(30, 22, 0), bg=YELLOW + (250,), edge=(255, 255, 255, 240), pad=(34, 16))
    frames = []
    for i in range(N["kbbi"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        c = card.copy()
        c.alpha_composite(defin if t >= T["kdef"] else Image.new("RGBA", defin.size))
        if T["kdef"] <= t < T["kdef"] + 0.15:
            c = card.copy()
            dd = defin.copy()
            dd.putalpha(dd.getchannel("A").point(lambda q: int(q * ramp(t, T["kdef"], T["kdef"] + 0.15))))
            c.alpha_composite(dd)
        put1(im, c, 540, 790, scale=min(pop(t, T["kcard"], 0.3), 1.02))
        put1(im, dg, 540, 1085, scale=min(pop(t, T["kdug"], 0.3), 1.06))
        frames.append(im.convert("RGB"))
    return frames


# ---------- h2crop ----------
def h2crop(times=None):
    im = Image.open("img/H2.jpg").convert("RGB")
    c = im.crop((523, 800, 1536, 2601))
    box = (960 - 523, 2096 - 800, 1130 - 523, 2132 - 800)
    c.paste(c.crop(box).filter(ImageFilter.GaussianBlur(4)), box[:2])
    c.save("img/H2c.jpg", quality=93)
    print("img/H2c.jpg")
    return None


FUN = {"jam": skema_jam, "buku": skema_buku, "kbbi": skema_kbbi, "h2crop": h2crop}

if __name__ == "__main__":
    args = sys.argv[1:]
    out, TIMES = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, TIMES = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    os.makedirs("clips", exist_ok=True)
    for name in args or ["h2crop"] + list(N):
        fr = FUN[name](TIMES)
        if fr is None:
            continue
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
