"""Schematic animations and the cover for Titik Heran #86 (run in the episode work dir).
tinggi: height comparison: the Colossus of Rhodes (+-33 m, 70 cubits) beside the Statue of Liberty (46 m without its
  pedestal, dashed) and a 1,7 m person, as simple pictograms on a metre ruler (schematic, not the real shape).
mustahil: the harbour mouth from above: two breakwaters hundreds of metres apart, and the statue's feet, which could open
  only about 8 m (McDaniel 2019; Britannica: "technically impossible"), then a red cross.
unta: the real caravan clip (Pixabay 112040) darkened, with 900 small camel icons filling in (the 900+ camel loads of
  the chronicle of Theophanes, "supposedly" per Britannica).
cover: img/cover86.jpg from Higgsfield H1 (the legendary straddling version) with the title.
Event times are seconds from the start of each clip, read off `render.py 86 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < ~600) and the captions (y >= 1210).
usage: python3 skema86.py [tinggi|mustahil|unta|cover ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, pop, ramp, encode, text_sprite
from skema35 import sheet
from skema37 import to_img, put1, noise, wanted
from skema74 import backdrop

WHITE, GREY = (255, 255, 255), (200, 200, 200)
BRONZE, TEAL, RED = (196, 140, 72), (110, 190, 170), (235, 50, 45)
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
N = {"tinggi": 120, "mustahil": 80, "unta": 84}
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def statue(d, x, gy, h, fill, crown=True, torch=True, dash=False):
    """a pictogram of a robed statue with a raised torch, feet at (x, gy), h px from feet to flame tip, drawn at 2x"""
    def P(u, v):
        return ((x + u * h) * S, (gy - v * h) * S)
    parts = [
        [P(-0.045, 0), P(-0.012, 0), P(-0.010, 0.40), P(-0.040, 0.40)],            # legs
        [P(0.012, 0), P(0.045, 0), P(0.040, 0.40), P(0.010, 0.40)],
        [P(-0.085, 0.36), P(0.085, 0.36), P(0.065, 0.71), P(-0.065, 0.71)],         # tunic and chest
        [P(0.050, 0.69), P(0.075, 0.71), P(0.105, 0.92), P(0.080, 0.93)],           # raised right arm
        [P(-0.050, 0.69), P(-0.075, 0.69), P(-0.098, 0.47), P(-0.075, 0.46)],       # lowered left arm
        [P(-0.018, 0.70), P(0.018, 0.70), P(0.016, 0.74), P(-0.016, 0.74)],         # neck
    ]
    for p in parts:
        d.polygon(p, fill=fill)
    cx, cy = P(0, 0.79)
    r = 0.05 * h * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    if crown:
        for k in range(7):
            a = math.radians(-90 + (k - 3) * 26)
            b0 = (cx + r * 0.9 * math.cos(a - 0.2), cy + r * 0.9 * math.sin(a - 0.2))
            b1 = (cx + r * 0.9 * math.cos(a + 0.2), cy + r * 0.9 * math.sin(a + 0.2))
            tip = (cx + r * 1.9 * math.cos(a), cy + r * 1.9 * math.sin(a))
            d.polygon([b0, tip, b1], fill=fill)
    if torch:
        d.polygon([P(0.070, 0.925), P(0.115, 0.925), P(0.105, 0.955), P(0.080, 0.955)], fill=fill)
        d.polygon([P(0.078, 0.955), P(0.107, 0.955), P(0.092, 1.0)], fill=(255, 190, 60, 255))


def human(d, x, gy, h, fill):
    def P(u, v):
        return ((x + u * h) * S, (gy - v * h) * S)
    d.polygon([P(-0.10, 0), P(-0.02, 0), P(-0.02, 0.45), P(-0.10, 0.45)], fill=fill)
    d.polygon([P(0.02, 0), P(0.10, 0), P(0.10, 0.45), P(0.02, 0.45)], fill=fill)
    d.polygon([P(-0.14, 0.45), P(0.14, 0.45), P(0.12, 0.82), P(-0.12, 0.82)], fill=fill)
    cx, cy = P(0, 0.91)
    r = 0.09 * h * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


# ---------- tinggi ----------
GY, K = 1150, 11.0          # ground line, px per metre
T_COL, T_HUM, T_LIB = 0.15, 0.9, 1.6


def skema_tinggi(times=None):
    bg = backdrop((18, 30, 44), (6, 10, 16), glow=(30, 44, 56), gx=420, gy=900)
    a = np.asarray(bg, np.float32).copy()
    a[..., :3] *= (0.94 + 0.12 * noise((H, W), [(40, 0.6), (9, 0.4)], 86))[..., None]
    bg = to_img(a).convert("RGBA")
    L0 = Image.new("RGBA", (W * S, H * S))
    d0 = ImageDraw.Draw(L0)
    d0.line([(70 * S, GY * S), (1010 * S, GY * S)], fill=(230, 230, 230, 200), width=4 * S)
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 26 * S)
    for m in range(0, 51, 10):
        y = GY - m * K
        d0.line([(98 * S, y * S), (124 * S, y * S)], fill=(230, 230, 230, 200), width=3 * S)
        if m:
            d0.text((92 * S, y * S), f"{m} m", font=f, fill=(220, 220, 220, 220), anchor="rm")
    d0.line([(111 * S, GY * S), (111 * S, (GY - 50 * K) * S)], fill=(230, 230, 230, 120), width=2 * S)
    bg.alpha_composite(L0.resize((W, H), Image.LANCZOS))
    l_col = text_sprite([("COLOSSUS ±33 m", 40, YELLOW, True), ("70 hasta", 28, GREY, False)])
    l_hum = text_sprite([("manusia 1,7 m", 28, WHITE, False)])
    l_lib = text_sprite([("Patung Liberty 46 m", 34, TEAL, True), ("tanpa alas", 26, GREY, False)])
    frames = []
    for i in range(N["tinggi"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        # Liberty: a dashed outline-like ghost that rises after the Colossus
        kl = ramp(t, T_LIB, T_LIB + 0.6)
        if kl > 0:
            L = Image.new("RGBA", (W * S, H * S))
            statue(ImageDraw.Draw(L), 790, GY, 46 * K * kl, TEAL + (95,))
            im.alpha_composite(L.resize((W, H), Image.LANCZOS))
            d = ImageDraw.Draw(im)
            yl = GY - 46 * K * kl
            for x in range(150, 1000, 22):
                d.line([(x, yl), (x + 11, yl)], fill=TEAL + (200,), width=3)
            put1(im, l_lib, 790, 600 + 26 if kl >= 1 else yl - 40, a=min(1, kl * 1.5))
        kc = ramp(t, T_COL, T_COL + 0.75)
        if kc > 0:
            L = Image.new("RGBA", (W * S, H * S))
            statue(ImageDraw.Draw(L), 400, GY, 33 * K * kc, BRONZE + (255,))
            im.alpha_composite(L.resize((W, H), Image.LANCZOS))
            d = ImageDraw.Draw(im)
            yc = GY - 33 * K * kc
            for x in range(150, 640, 22):
                d.line([(x, yc), (x + 11, yc)], fill=YELLOW + (220,), width=3)
            put1(im, l_col, 400, yc - 52, a=min(1, kc * 1.6))
        kh = pop(t, T_HUM, 0.3)
        if kh > 0:
            L = Image.new("RGBA", (W * S, H * S))
            human(ImageDraw.Draw(L), 560, GY, 1.7 * K * max(kh, 0.01) * 1.0, WHITE + (255,))
            im.alpha_composite(L.resize((W, H), Image.LANCZOS))
            d = ImageDraw.Draw(im)
            d.line([(560, GY - 26), (560, GY - 70)], fill=(255, 255, 255, 180), width=2)
            put1(im, l_hum, 560, GY - 92, a=min(1, kh * 1.4))
        frames.append(im.convert("RGB"))
    return frames


# ---------- mustahil ----------
GAPL, GAPR, YB = 300, 780, 800     # inner ends of the two breakwaters, their centre line
T_GAP, T_FEET, T_X = 0.1, 0.5, 1.08


def skema_mustahil(times=None):
    v = (YY / H)[..., None]
    sea = np.array((18, 64, 96), np.float32) * (1 - v) + np.array((6, 28, 50), np.float32) * v
    sea *= (0.9 + 0.2 * noise((H, W), [(60, 0.5), (14, 0.5)], 860))[..., None]
    bg = to_img(sea).convert("RGBA")
    L = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(L)
    sand = (176, 160, 122, 255)
    d.rounded_rectangle([(-40 * S, (YB - 34) * S), (GAPL * S, (YB + 34) * S)], radius=30 * S, fill=sand)
    d.rounded_rectangle([(GAPR * S, (YB - 34) * S), ((W + 40) * S, (YB + 34) * S)], radius=30 * S, fill=sand)
    bg.alpha_composite(L.resize((W, H), Image.LANCZOS))
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 26)
    ImageDraw.Draw(bg).text((40, YB + 44), "pemecah ombak", font=f, fill=(230, 220, 190, 210))
    l_gap = text_sprite([("PINTU PELABUHAN", 40, WHITE, True), ("ratusan meter", 30, GREY, False)])
    l_feet = text_sprite([("kaki patung: ±8 m", 32, YELLOW, True)])
    l_src = text_sprite([("perkiraan: McDaniel (2019)", 24, GREY, False), ("Britannica: \"technically impossible\"", 24, GREY, False)])
    frames = []
    for i in range(N["mustahil"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        d = ImageDraw.Draw(im)
        kg = ramp(t, T_GAP, T_GAP + 0.35)
        if kg > 0:
            xa = 540 - (540 - GAPL) * kg
            xb = 540 + (GAPR - 540) * kg
            d.line([(xa, 700), (xb, 700)], fill=(255, 255, 255, 230), width=4)
            for xx in (xa, xb):
                d.line([(xx, 684), (xx, 716)], fill=(255, 255, 255, 230), width=4)
            put1(im, l_gap, 540, 646, a=min(1, kg * 1.5))
        kf = pop(t, T_FEET, 0.3)
        if kf > 0:
            r = 9 * min(kf, 1.15)
            for xx in (532, 548):
                d.ellipse([xx - r, YB - r, xx + r, YB + r], fill=BRONZE + (255,), outline=(40, 30, 20, 255), width=2)
            d.line([(540, YB + 14), (540, YB + 196)], fill=YELLOW + (200,), width=3)
            put1(im, l_feet, 540, YB + 226, a=min(1, kf * 1.4))
        kx = pop(t, T_X, 0.3)
        if kx > 0:
            Lx = Image.new("RGBA", (W * S, H * S))
            dx = ImageDraw.Draw(Lx)
            s = 120 * min(kx, 1.1)
            for p, q in (((540 - s, YB - s), (540 + s, YB + s)), ((540 - s, YB + s), (540 + s, YB - s))):
                dx.line([(p[0] * S, p[1] * S), (q[0] * S, q[1] * S)], fill=RED + (235,), width=22 * S)
            im.alpha_composite(Lx.resize((W, H), Image.LANCZOS))
            put1(im, l_src, 540, 1130, a=min(1, kx * 1.3))
        frames.append(im.convert("RGB"))
    return frames


# ---------- unta ----------
T_FILL0, T_FILL1 = 0.25, 1.45
COLS, ROWS, X0, Y0, CW, CH = 36, 25, 72, 640, 26, 21


def camel_icon(px):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (150, 150))
    ImageDraw.Draw(im).text((10, 10), "\U0001F42A", font=f, embedded_color=True)
    return im.crop(im.getbbox()).resize((px, round(px * 0.9)), Image.LANCZOS)


def caravan_frames(n, start=3.0):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(start), "-i", "clips/112040.mp4", "-frames:v", str(n),
                                   "-vf", f"fps={FPS},scale=-2:{H},crop={W}:{H}:(iw-{W})*0.45:0", "-f", "rawvideo",
                                   "-pix_fmt", "rgb24", "-"])
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    return fr


def skema_unta(times=None):
    vid = caravan_frames(N["unta"])
    icon = camel_icon(22)
    rng = np.random.default_rng(900)
    order = rng.permutation(COLS * ROWS)
    when = np.empty(COLS * ROWS)
    when[order] = T_FILL0 + (T_FILL1 - T_FILL0) * np.sqrt(np.arange(COLS * ROWS) / (COLS * ROWS - 1))
    frames = []
    for i in range(N["unta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        a = vid[min(i, len(vid) - 1)].astype(np.float32)
        a *= 1 - np.clip((620 - YY) / 400, 0, 1)[..., None] * 0.55
        im = to_img(a).convert("RGBA")
        kp = ramp(t, 0.0, 0.3)
        panel = Image.new("RGBA", (W, H))
        ImageDraw.Draw(panel).rounded_rectangle([X0 - 22, Y0 - 22, X0 + COLS * CW + 18, Y0 + ROWS * CH + 18], radius=28,
                                               fill=(10, 8, 6, int(175 * kp)))
        im.alpha_composite(panel)
        for k in np.flatnonzero(when <= t):
            r, c = divmod(int(k), COLS)
            im.alpha_composite(icon, (X0 + c * CW, Y0 + r * CH))
        frames.append(im.convert("RGB"))
    return frames


# ---------- cover ----------
def cover():
    im = Image.open("img/H1.jpg").convert("RGB")
    a = np.asarray(im, np.float32)
    a *= 1 - np.clip((800 - YY) / 560, 0, 1)[..., None] * 0.6
    im = to_img(a).convert("RGBA")
    t = text_sprite([("KAKAK PATUNG LIBERTY", 70, WHITE, True), ("KONON BERDIRI", 70, WHITE, True),
                     ("MENGANGKANG", 120, YELLOW, True)], gap=10)
    put1(im, t, 540, 400)
    im.convert("RGB").save("img/cover86.jpg", quality=93)
    print("img/cover86.jpg")


if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or ["tinggi", "mustahil", "unta", "cover"]
    fns = {"tinggi": skema_tinggi, "mustahil": skema_mustahil, "unta": skema_unta}
    for name in todo:
        if name == "cover":
            cover()
            continue
        fr = fns[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, f"clips/skema_{name}.mp4")
