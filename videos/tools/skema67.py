"""Schematic animations for Titik Heran #67 (run in the episode work dir; needs img/1129156.jpg and img/flagframe.jpg, a frame
of Pixabay video 24671 grabbed with ffmpeg at 4 s; writes clips/skema_call.mp4, skema_pidato.mp4, skema_unesco.mp4).
call: a video-call mock-up, not a screenshot (no real frame of the 16 Nov stream is used): a dark "IShowSpeed · LIVE" tile with
  a plain avatar (no look-alike), an Obama tile cut from his official portrait, the bubble "Apa kabar?" under Speed, then
  "Baik-baik!" under Obama when the VO says it; the speaking tile gets a green edge.
pidato: a stage spotlight and a mic; two quote cards with the first and last lines of Speed's Indonesian speech at the
  Streamer Awards, Los Angeles, 12 Nov 2026 (as GNFI quoted them).
unesco: the official languages of the UNESCO General Conference one by one (the six UN languages, then Hindi, Italian and
  Portuguese), then "10 · BAHASA INDONESIA" in yellow, and a pill "disetujui bulat · 20 Nov 2023" (Badan Bahasa press
  release 649). No UNESCO logo.
Event times are seconds from the start of each clip, read off `render.py 67 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 705) and the captions (y >= 1210).
usage: python3 skema67.py [call|pidato|unesco ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode
from skema35 import sheet, SERIF_BI
from skema37 import to_img, put1
from skema46 import pill, wanted
from skema53 import XB

N = {"call": 122, "pidato": 54, "unesco": 124}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 67 plan`: call "dan" 0.03, "Obama" 0.27, "ternyata" 0.91, "bahasa" 1.98, "Baik-baik!" 3.05;
# pidato "juga" 0.04, "pakai" 0.40, "bahasa" 0.64, "Indonesia!" 0.96; unesco "bahasa" 0.03, "Indonesia" 0.35, "resmi" 1.07,
# "kesepuluh" 2.18, "Sidang" 2.74, "Unesko!" 3.30
T = {"obama": 0.27, "baik": 3.0,
     "q1": 0.05, "q2": 0.75,
     "list0": 0.1, "list1": 1.9, "ten": 2.15, "ok": 2.75}
WHITE = (255, 255, 255)
GREEN = (60, 220, 120)


def dark_bg(top=(16, 20, 30), bottom=(6, 8, 14)):
    v = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    return to_img(np.array(top, np.float32) * (1 - v) + np.array(bottom, np.float32) * v + np.zeros((H, W, 3), np.float32)).convert("RGBA")


def rounded(im, r):
    m = Image.new("L", (im.width * S, im.height * S), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width * S - 1, im.height * S - 1], radius=r * S, fill=255)
    im = im.convert("RGBA")
    im.putalpha(m.resize(im.size, Image.LANCZOS))
    return im


def bubble(text, size=44, col=(20, 20, 20), bg=WHITE, tail="left"):
    f = ImageFont.truetype(XB, size * S)
    x0, y0, x1, y1 = f.getbbox(text)
    pw, ph = 30 * S, 18 * S
    w, h = x1 - x0 + 2 * pw, y1 - y0 + 2 * ph
    sp = Image.new("RGBA", (w + 40 * S, h + 60 * S))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([20 * S, 36 * S, 20 * S + w, 36 * S + h], radius=26 * S, fill=bg + (255,))
    tx = 20 * S + (60 * S if tail == "left" else w - 60 * S)
    d.polygon([(tx - 18 * S, 38 * S), (tx + 18 * S, 38 * S), (tx, 6 * S)], fill=bg + (255,))
    d.text((20 * S + pw - x0, 36 * S + ph - y0), text, font=f, fill=col + (255,))
    return sp


# ---------- call ----------
TL, TR, TY0, TY1 = (40, 530), (550, 1040), 720, 1100


def speed_tile():
    w, h = TL[1] - TL[0], TY1 - TY0
    t = Image.new("RGBA", (w * S, h * S), (34, 38, 48, 255))
    d = ImageDraw.Draw(t)
    cx, cy = w * S // 2, int(h * S * 0.46)
    d.ellipse([cx - 70 * S, cy - 120 * S, cx + 70 * S, cy + 20 * S], fill=(120, 128, 146, 255))          # plain avatar head
    d.pieslice([cx - 150 * S, cy + 40 * S, cx + 150 * S, cy + 330 * S], 180, 360, fill=(120, 128, 146, 255))
    return rounded(t.resize((w, h), Image.LANCZOS), 22)


def obama_tile():
    w, h = TR[1] - TR[0], TY1 - TY0
    im = Image.open("img/1129156.jpg").convert("RGB")
    # the official portrait is 853x1067 at 1280: his face sits around x 0.5, y 0.25
    k = w / (im.width * 0.62)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x0 = round(im.width * 0.5 - w / 2)
    y0 = round(im.height * 0.06)
    return rounded(im.crop((x0, y0, x0 + w, y0 + h)), 22)


def name_tag(text, live=False):
    sp = pill(text, 26, col=WHITE, bg=(0, 0, 0, 170), edge=(255, 255, 255, 60), pad=(16, 7))
    if not live:
        return sp
    lv = pill("LIVE", 24, col=WHITE, bg=(220, 30, 40, 255), edge=(255, 255, 255, 0), pad=(12, 6))
    out = Image.new("RGBA", (sp.width + lv.width, max(sp.height, lv.height)))
    out.alpha_composite(lv, (0, (out.height - lv.height) // 2))
    out.alpha_composite(sp, (lv.width - 10 * S, (out.height - sp.height) // 2))
    return out


def skema_call(times=None):
    bg = dark_bg()
    st, ot = speed_tile(), obama_tile()
    n1, n2 = name_tag("IShowSpeed", live=True), name_tag("Barack Obama")
    b1 = bubble("Apa kabar?", tail="left")
    b2 = bubble("Baik-baik!", col=(20, 20, 20), bg=YELLOW, tail="right")
    date = pill("siaran langsung · 16 Nov 2026", 24, col=(225, 225, 230), bg=(10, 14, 24, 200))
    frames = []
    for i in range(N["call"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        im.alpha_composite(st, (TL[0], TY0))
        im.alpha_composite(ot, (TR[0], TY0))
        d = ImageDraw.Draw(im)
        a1 = 1 - ramp(t, 0.2, 0.5)                   # Speed just spoke: his edge fades
        if a1 > 0:
            d.rounded_rectangle([TL[0] - 3, TY0 - 3, TL[1] + 3, TY1 + 3], radius=24, outline=GREEN + (int(255 * a1),), width=6)
        a2 = ramp(t, T["baik"] - 0.2, T["baik"])
        if a2 > 0:
            d.rounded_rectangle([TR[0] - 3, TY0 - 3, TR[1] + 3, TY1 + 3], radius=24, outline=GREEN + (int(255 * a2),), width=6)
        put1(im, n1, TL[0] + 20 + n1.width / (2 * S), TY1 - 34)
        put1(im, n2, TR[0] + 20 + n2.width / (2 * S), TY1 - 34)
        put1(im, date, (TL[0] + TL[1]) / 2, TY0 + 40)
        put1(im, b1, 250, 1160)
        if t > T["baik"]:
            put1(im, b2, 800, 1160, scale=min(pop(t, T["baik"], 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


# ---------- pidato ----------
def quote_card(text, w=900):
    f = ImageFont.truetype(SERIF_BI, 56 * S)
    x0, y0, x1, y1 = f.getbbox(text)
    h = (y1 - y0) + 60 * S
    sp = Image.new("RGBA", (w * S, h))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([0, 0, w * S - 1, h - 1], radius=18 * S, fill=(250, 246, 236, 245))
    d.rectangle([0, 0, 12 * S, h - 1], fill=YELLOW + (255,))
    d.text((w * S // 2, h // 2), text, font=f, fill=(30, 26, 22, 255), anchor="mm")
    return sp


def skema_pidato(times=None):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.array([10, 10, 18], np.float32) * np.ones((H, W, 1), np.float32)
    cone = np.clip(1 - np.abs(xx - 540) / (120 + (yy - 200) * 0.32).clip(60), 0, 1) * (yy > 200)   # spotlight from the top
    pool = np.exp(-(((xx - 540) / 380) ** 2 + ((yy - 1180) / 90) ** 2))
    img = base + (np.array([255, 236, 190], np.float32) * (0.16 * cone + 0.35 * pool)[..., None])
    bg = to_img(img).convert("RGBA").filter(ImageFilter.GaussianBlur(6))
    d = ImageDraw.Draw(bg)
    d.line([(540, 900), (540, 1180)], fill=(30, 30, 34, 255), width=10)                  # mic stand
    d.line([(470, 1180), (610, 1180)], fill=(30, 30, 34, 255), width=10)
    d.rounded_rectangle([522, 850, 558, 912], radius=18, fill=(40, 40, 46, 255), outline=(120, 120, 130, 255), width=3)
    q1 = quote_card("“Terima kasih banyak semuanya.”")
    q2 = quote_card("“Aku cinta kalian semuanya.”")
    src = pill("pidato IShowSpeed · The Streamer Awards, 12 Nov", 24, col=(225, 225, 230), bg=(10, 14, 24, 200))
    frames = []
    for i in range(N["pidato"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        if t > T["q1"]:
            put1(im, q1, 540, 780, scale=min(pop(t, T["q1"], 0.3), 1.06))
        if t > T["q2"]:
            put1(im, q2, 540, 1050, scale=min(pop(t, T["q2"], 0.3), 1.06))
        put1(im, src, 540, 1160, a=ramp(t, 0.2, 0.4))
        frames.append(im.convert("RGB"))
    return frames


# ---------- unesco ----------
LANGS = ["Inggris", "Prancis", "Arab", "China", "Rusia", "Spanyol", "Hindi", "Italia", "Portugis"]
GRID = [(200, 735), (540, 735), (880, 735), (200, 830), (540, 830), (880, 830), (200, 1040), (540, 1040), (880, 1040)]


def skema_unesco(times=None):
    flag = Image.open("img/flagframe.jpg").convert("RGB")
    k = max(W / flag.width, H / flag.height)
    flag = flag.resize((round(flag.width * k), round(flag.height * k)), Image.LANCZOS)
    x0 = (flag.width - W) // 2
    flag = flag.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(14))
    bg = to_img(np.asarray(flag, np.float32) * 0.32).convert("RGBA")
    chips = [pill(name, 34, col=WHITE, bg=(10, 14, 24, 215)) for n, name in enumerate(LANGS)]
    ten = pill("10  BAHASA INDONESIA", 52, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230), pad=(30, 14))
    ok = pill("disetujui bulat · 20 Nov 2023", 28, col=WHITE, bg=(10, 14, 24, 220))
    un = pill("6 bahasa PBB", 22, col=(200, 205, 215), bg=(10, 14, 24, 160), pad=(14, 6))
    frames = []
    for i in range(N["unesco"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        for n, (c, (x, y)) in enumerate(zip(chips, GRID)):
            t0 = T["list0"] + n * (T["list1"] - T["list0"]) / len(LANGS)
            if t > t0:
                put1(im, c, x, y, scale=min(pop(t, t0, 0.25), 1.05) * (0.92 if t > T["ten"] else 1.0),
                     a=1.0 if t < T["ten"] else 1 - 0.45 * ramp(t, T["ten"], T["ten"] + 0.3))
        put1(im, un, 540, 900, a=ramp(t, T["list0"] + 0.9, T["list0"] + 1.1) * (1 - ramp(t, T["ten"], T["ten"] + 0.3)))
        if t > T["ten"]:
            put1(im, ten, 540, 1140, scale=min(pop(t, T["ten"], 0.35), 1.1) * (1 + 0.03 * math.sin((t - T["ten"]) * 6)))
        if t > T["ok"]:
            put1(im, ok, 540, 900, a=ramp(t, T["ok"], T["ok"] + 0.25))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"call": skema_call, "pidato": skema_pidato, "unesco": skema_unesco}

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
