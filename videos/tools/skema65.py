"""Schematic animations for Titik Heran #65 (run in the episode work dir; needs img/9294935.jpg and img/3602696.jpg;
writes clips/skema_catatan.mp4 and clips/skema_cula.mp4).
catatan: an old paper card over the dark sepia Venice photo: "CATATAN MARCO POLO · SUMATRA, ±1292" with the traits he
  listed (a summary of Yule's translation, not a quote): HAMPIR SEBESAR GAJAH and BULU SEPERTI KERBAU already ticked,
  1 CULA DI DAHI ticks on at "cula".
cula: a Sumatran rhino head in profile (line drawing, not to scale) over a dark blurred rhino photo: a big front horn and a
  small back horn get labels, then short hair strokes grow along the outline ("berbulu").
Event times are seconds from the start of each clip, read off `render.py 65 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 560: the cula title is two lines) and the captions (y >= 1210).
usage: python3 skema65.py [catatan|cula ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, chaikin
from skema23 import smooth
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema53 import XB
from skema61 import cover, paper_card

N = {"catatan": 50, "cula": 54}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 65 plan`: catatan "satu" 0.05, "cula" 0.42, "dahi" 0.83; cula "badak" 0.05, "paling" 0.52, "berbulu" 0.90
T = {"card": 0.0, "tick": 0.42, "head": 0.0, "horns": 0.3, "hair0": 0.8, "hair1": 1.25}
RED = (170, 40, 30, 255)
INK = (52, 38, 26, 255)
GREEN = (40, 120, 60, 255)


def graded(path, cx, cy, k, blur=0, sepia=False):
    im = cover(path, cx, cy)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im, np.float32)
    if sepia:
        a = a @ np.array([[.393, .349, .272], [.769, .686, .534], [.189, .168, .131]], np.float32)
    return to_img(a * k).convert("RGBA")


# ---------- catatan ----------
def skema_catatan(times=None):
    bg = graded("img/9294935.jpg", 0.5, 0.5, 0.42, blur=6, sepia=True)
    cw, ch = 860, 330
    rows = ["HAMPIR SEBESAR GAJAH", "BULU SEPERTI KERBAU", "1 CULA DI DAHI"]
    fr = ImageFont.truetype(XB, 46)

    def card(k3):
        c = paper_card(cw, ch)
        d = ImageDraw.Draw(c)
        ox, oy = 30, 30
        d.text((ox + 44, oy + 26), "CATATAN MARCO POLO · SUMATRA, ±1292", font=ImageFont.truetype(XB, 30), fill=RED)
        d.line([(ox + 44, oy + 72), (ox + cw - 44, oy + 72)], fill=(150, 120, 90, 255), width=2)
        for r, txt in enumerate(rows):
            y = oy + 92 + r * 72
            on = 1.0 if r < 2 else k3
            if r == 2 and k3 > 0:   # the new row gets a yellow marker behind it
                bb = d.textbbox((ox + 120, y), txt, font=fr)
                mk = Image.new("RGBA", c.size)
                ImageDraw.Draw(mk).rounded_rectangle([bb[0] - 12, bb[1] - 8, bb[0] - 12 + (bb[2] - bb[0] + 24) * k3, bb[3] + 10],
                                                    radius=8, fill=YELLOW + (int(200 * k3),))
                c.alpha_composite(mk)
                d = ImageDraw.Draw(c)
            col = INK if r < 2 else tuple(int(INK[i] * on + 150 * (1 - on)) for i in range(3)) + (255,)
            d.text((ox + 120, y), txt, font=fr, fill=col)
            if on >= 1:
                d.text((ox + 52, y - 4), "✓", font=ImageFont.truetype(XB, 54), fill=GREEN)
        return c
    c0, c1 = card(0.0), card(1.0)
    frames = []
    for i in range(N["catatan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        u = ease(t / 0.25)
        k3 = ramp(t, T["tick"], T["tick"] + 0.2)
        c = c1 if k3 >= 1 else (c0 if k3 <= 0 else card(k3))
        c = c.rotate(-2 * (1 - u) - 1.0, resample=Image.BICUBIC, expand=True)
        c.putalpha(c.getchannel("A").point(lambda v: int(v * min(1, u * 1.4))))
        im.alpha_composite(c, (540 - c.width // 2, round(590 + 30 * (1 - u))))
        frames.append(im.convert("RGB"))
    return frames


# ---------- cula ----------
OX, OY, K = 215, 585, 1.05   # the head's local frame: x 0-620, y 0-330 -> screen x 215-866, y 585-932

HEAD = [(20, 262), (40, 238), (70, 222), (100, 205), (140, 190), (178, 182), (200, 178), (226, 172), (276, 160),
        (300, 142), (336, 122), (350, 108), (336, 66), (344, 28), (366, 8), (392, 14), (408, 52), (416, 104),
        (440, 112), (520, 120), (620, 140), (622, 330), (520, 332), (420, 322), (330, 314), (200, 302), (90, 292),
        (60, 282), (32, 272)]
HORN_F = [(98, 207), (104, 150), (114, 98), (124, 66), (136, 62), (148, 100), (162, 150), (180, 184)]
HORN_B = [(226, 173), (236, 147), (248, 130), (258, 131), (267, 150), (278, 164)]
EYE = (285, 215)
FOLD = [(330, 142), (350, 230), (345, 312)]


def xy(p):
    return ((OX + K * p[0]) * S, (OY + K * p[1]) * S)


def outline_pts():
    return chaikin(HEAD, 3)


def hair_strokes():
    """short strokes standing out of the upper outline and the ear, as (base, tip) pairs in local units"""
    pts = smooth([(40, 238), (70, 222), (100, 205), (200, 178), (276, 160), (300, 142), (336, 122), (350, 108), (336, 66),
                  (344, 28), (366, 8), (392, 14), (408, 52), (416, 104), (440, 112), (520, 120), (620, 140)], 3)
    rng = np.random.default_rng(3)
    out = []
    acc = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        acc += L
        if acc < 9 or 95 < x0 < 185 or 222 < x0 < 282:   # leave the front horn's base clear
            continue
        acc = 0.0
        nx, ny = (y1 - y0) / L, -(x1 - x0) / L   # outward normal (outline runs left to right along the top)
        if ny > 0:
            nx, ny = -nx, -ny
        ln = rng.uniform(10, 20)
        tilt = rng.uniform(-0.5, 0.5)
        out.append(((x0, y0), (x0 + ln * (nx + tilt * 0.4), y0 + ln * (ny - 0.2))))
    # a few strokes on the cheek and jaw for the shaggy coat
    for _ in range(40):
        x, y = rng.uniform(200, 590), rng.uniform(150, 315)
        out.append(((x, y), (x + rng.uniform(-6, 6), y + rng.uniform(8, 14))))
    return out


def skema_cula(times=None):
    bg = graded("img/3602696.jpg", 0.5, 0.5, 0.3, blur=16)
    base = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(base)
    d.polygon([xy(p) for p in outline_pts()], fill=(70, 52, 40, 235))
    d.line([xy(p) for p in outline_pts()] + [xy(outline_pts()[0])], fill=(255, 255, 255, 255), width=6 * S, joint="curve")
    d.line([xy(p) for p in smooth(FOLD, 2)], fill=(255, 255, 255, 150), width=4 * S)
    ex, ey = xy(EYE)
    d.ellipse([ex - 9 * S, ey - 7 * S, ex + 9 * S, ey + 7 * S], fill=(255, 255, 255, 255))
    head = base.resize((W, H), Image.LANCZOS)

    def horn_layer(pts, col):
        lay = Image.new("RGBA", (W * S, H * S))
        dl = ImageDraw.Draw(lay)
        dl.polygon([xy(p) for p in pts], fill=col, outline=(255, 255, 255, 255))
        dl.line([xy(p) for p in pts] + [xy(pts[0])], fill=(255, 255, 255, 255), width=5 * S)
        return lay.resize((W, H), Image.LANCZOS)
    hf0, hf1 = horn_layer(HORN_F, (95, 80, 70, 255)), horn_layer(HORN_F, YELLOW + (255,))
    hb0, hb1 = horn_layer(HORN_B, (95, 80, 70, 255)), horn_layer(HORN_B, YELLOW + (255,))
    strokes = hair_strokes()
    lab_f = pill("cula depan", 34, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(20, 10))
    lab_b = pill("cula belakang kecil", 34, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(20, 10))
    lab_h = pill("bulu kasar menutupi tubuh", 34, col=(255, 255, 255), bg=(10, 14, 24, 215), pad=(20, 10))
    frames = []
    for i in range(N["cula"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        a = ramp(t, 0.0, 0.25)
        h = head.copy()
        h.putalpha(h.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(h)
        lit = ramp(t, T["horns"], T["horns"] + 0.15)
        for l0, l1 in ((hf0, hf1), (hb0, hb1)):
            l = Image.blend(l0, l1, lit) if 0 < lit < 1 else (l1 if lit >= 1 else l0)
            l = l.copy()
            l.putalpha(l.getchannel("A").point(lambda v: int(v * a)))
            im.alpha_composite(l)
        g = ramp(t, T["hair0"], T["hair1"])
        if g > 0:
            lay = Image.new("RGBA", (W * S, H * S))
            dl = ImageDraw.Draw(lay)
            for (b, tip) in strokes:
                p0, p1 = xy(b), xy(tip)
                dl.line([p0, (p0[0] + (p1[0] - p0[0]) * g, p0[1] + (p1[1] - p0[1]) * g)], fill=(235, 220, 200, 255), width=3 * S)
            im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        if t > T["horns"]:
            put1(im, lab_f, 260, 1030, scale=min(pop(t, T["horns"], 0.3), 1.06))
            put1(im, lab_b, 640, 1090, scale=min(pop(t, T["horns"] + 0.12, 0.3), 1.06))
            ln = Image.new("RGBA", (W, H))
            dln = ImageDraw.Draw(ln)
            k = ramp(t, T["horns"], T["horns"] + 0.25)
            dln.line([(260, 1005), (260 + (OX + K * 130 - 260) * k, 1005 + (OY + K * 120 - 1005) * k)], fill=YELLOW + (230,), width=4)
            dln.line([(640, 1065), (640 + (OX + K * 252 - 640) * k, 1065 + (OY + K * 150 - 1065) * k)], fill=YELLOW + (230,), width=4)
            im.alpha_composite(ln)
        if t > T["hair0"]:
            put1(im, lab_h, 540, 1150, a=ramp(t, T["hair0"], T["hair0"] + 0.2))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"catatan": skema_catatan, "cula": skema_cula}

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
