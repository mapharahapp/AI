"""Schematic animations for Titik Heran #59 (run in the episode work dir; needs img/1583098.jpg and img/4264846.jpg;
writes clips/skema_nobel.mp4, skema_beras.mp4, skema_versus.mp4).
nobel: a self-drawn gold medal (not the real Nobel medal) with turning rays, then two pills "HADIAH NOBEL KEDOKTERAN" and
  "Christiaan Eijkman · 1929". Used twice: a short flash in the hook and the full clip at "Tahun 1929".
beras: one rice grain in section: white core, brown bran layer (kulit ari) that lights up yellow, pills "kulit ari" and
  "VITAMIN B1", then a note that white rice has had it polished off.
versus: nasi putih (left) and nasi merah (right) slide in with a pulsing VS badge; runs under the CTA labels.
Event times are seconds from the start of each clip, read off `render.py 59 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 660) and the captions (y >= 1210).
usage: python3 skema59.py [nobel|beras|versus ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema53 import XB

N = {"nobel": 138, "beras": 86, "versus": 108}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
T = {"kulit": 0.25, "vit": 1.35, "note": 1.75, "vs": 0.9}   # set from `render.py 59 plan`
GOLD, GOLD_D = (232, 186, 70), (150, 108, 28)


def flat(rgb):
    return to_img(np.array(rgb, np.float32) * np.ones((H, W, 1), np.float32)).convert("RGBA")


# ---------- nobel ----------
MC, MR = (540, 842), 118


def medal():
    sp = Image.new("RGBA", (320 * S, 320 * S))
    d = ImageDraw.Draw(sp)
    c = 160 * S
    d.ellipse([c - MR * S, c - MR * S, c + MR * S, c + MR * S], fill=GOLD + (255,), outline=GOLD_D + (255,), width=6 * S)
    d.ellipse([c - 96 * S, c - 96 * S, c + 96 * S, c + 96 * S], outline=GOLD_D + (255,), width=3 * S)
    for k in range(24):                      # a ring of leaves
        a = 2 * math.pi * k / 24
        x, y = c + 84 * S * math.cos(a), c + 84 * S * math.sin(a)
        d.ellipse([x - 7 * S, y - 7 * S, x + 7 * S, y + 7 * S], fill=GOLD_D + (255,))
    star = []
    for k in range(10):
        a = -math.pi / 2 + math.pi * k / 5
        r = (58 if k % 2 == 0 else 24) * S
        star.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(star, fill=(255, 240, 190, 255), outline=GOLD_D + (255,))
    return sp


def rays(t):
    lay = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(lay)
    for k in range(12):
        a = 2 * math.pi * k / 12 + t * 0.35
        p = [MC, (MC[0] + 900 * math.cos(a - 0.07), MC[1] + 900 * math.sin(a - 0.07)),
             (MC[0] + 900 * math.cos(a + 0.07), MC[1] + 900 * math.sin(a + 0.07))]
        d.polygon(p, fill=(255, 210, 90, 16))
    return lay.filter(ImageFilter.GaussianBlur(6))


def skema_nobel(times=None):
    bg = flat((14, 18, 40))
    md = medal()
    l1 = pill("HADIAH NOBEL KEDOKTERAN", 44, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(28, 14))
    l2 = pill("Christiaan Eijkman · 1929", 36, col=(255, 255, 255), bg=(10, 14, 24, 215))
    note = pill("medali digambar sendiri, bukan medali asli", 24, col=(210, 210, 215), bg=(10, 14, 24, 170))
    frames = []
    for i in range(N["nobel"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        im.alpha_composite(rays(t))
        put1(im, md, MC[0], MC[1], scale=1.3 * min(pop(t, 0.0, 0.3), 1.1) * (1 + 0.02 * math.sin(t * 3)))
        if t > 0.25:
            put1(im, l1, 540, 1050, scale=min(pop(t, 0.25, 0.3), 1.1))
        put1(im, l2, 540, 1125, a=ramp(t, 0.5, 0.75))
        put1(im, note, 540, 1183, a=ramp(t, 0.7, 0.95))
        frames.append(im.convert("RGB"))
    return frames


# ---------- beras ----------
GC, GRX, GRY = (540, 860), 330, 128


def grain_mask(rx, ry):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # a rice grain: an ellipse, a little pointed at both ends
    u = (xx - GC[0]) / rx
    v = (yy - GC[1]) / (ry * (1 - 0.18 * u * u))
    return np.clip((1 - np.hypot(u, v)) * 60, 0, 1)


def skema_beras(times=None):
    outer, inner = grain_mask(GRX, GRY), grain_mask(GRX - 26, GRY - 24)
    bran = np.clip(outer - inner, 0, 1)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    shade = 1 - 0.18 * np.clip((yy - GC[1]) / GRY, -1, 1)
    core = (np.array([246, 242, 228], np.float32) * shade[..., None])
    bg = np.array([36, 26, 18], np.float32) * np.ones((H, W, 1), np.float32)
    bg *= (1 - 0.3 * np.clip(np.hypot((xx - 540) / 700, (yy - 900) / 900), 0, 1))[..., None]
    glow_m = np.asarray(Image.fromarray((bran * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18)), np.float32) / 255
    lk = pill("kulit ari", 36, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220))
    lv = pill("VITAMIN B1", 60, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230), pad=(32, 16))
    ln = pill("nasi putih: kulit ari sudah digosok habis", 26, col=(225, 225, 228), bg=(10, 14, 24, 190))
    li = pill("isi beras (pati)", 26, col=(60, 50, 40), bg=(255, 255, 255, 0), edge=(0, 0, 0, 0))
    frames = []
    for i in range(N["beras"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        g = ramp(t, T["kulit"], T["kulit"] + 0.3) * (0.75 + 0.25 * math.sin((t - T["kulit"]) * 7))
        bcol = np.array([150, 98, 46], np.float32) * (1 - g) + np.array([255, 214, 40], np.float32) * g
        a = bg + glow_m[..., None] * np.array([255, 200, 40], np.float32) * 0.55 * g
        a = a * (1 - outer[..., None]) + (core * inner[..., None] + bcol * (1 - inner[..., None])) * outer[..., None]
        im = to_img(a).convert("RGBA")
        d = ImageDraw.Draw(im)
        if t > T["kulit"]:
            u = ramp(t, T["kulit"], T["kulit"] + 0.25)
            d.line([(700, 712), (700 - 0 * u, 712 + (GC[1] - GRY * 0.93 - 712) * u + 2)], fill=YELLOW + (255,), width=5)
            put1(im, lk, 700, 690, scale=min(pop(t, T["kulit"], 0.3), 1.1))
        put1(im, li, 540, GC[1] - 46, a=ramp(t, 0.1, 0.4))
        if t > T["vit"]:
            put1(im, lv, 540, 1075, scale=min(pop(t, T["vit"], 0.32), 1.1))
        put1(im, ln, 540, 1168, a=ramp(t, T["note"], T["note"] + 0.25))
        frames.append(im.convert("RGB"))
    return frames


# ---------- versus ----------
PW, PH, PY = 490, 580, 610


def panel(path, box):
    im = Image.open(path).convert("RGB").crop(box).resize((PW, PH), Image.LANCZOS)
    m = Image.new("L", (PW, PH))
    ImageDraw.Draw(m).rounded_rectangle([0, 0, PW - 1, PH - 1], radius=26, fill=255)
    out = Image.new("RGBA", (PW, PH))
    out.paste(im, (0, 0), m)
    return out


def skema_versus(times=None):
    # nasi putih 1583098 (1280x960): bowl near (640, 560); nasi merah 4264846 (1280x853): left bowl near (360, 290)
    put = panel("img/1583098.jpg", (330, 190, 950, 924))
    mer = panel("img/4264846.jpg", (40, 0, 720, 805))
    bg = flat((22, 16, 14))
    vs = Image.new("RGBA", (260 * S, 260 * S))
    dv = ImageDraw.Draw(vs)
    dv.ellipse([10 * S, 10 * S, 250 * S, 250 * S], fill=YELLOW + (255,), outline=(20, 20, 20, 255), width=8 * S)
    dv.text((130 * S, 132 * S), "VS", font=ImageFont.truetype(XB, 110 * S), fill=(20, 20, 20, 255), anchor="mm")
    frames = []
    for i in range(N["versus"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        u = ease(t / 0.4)
        im.alpha_composite(put, (round(35 - 600 * (1 - u)), PY))
        im.alpha_composite(mer, (round(555 + 600 * (1 - u)), PY))
        if t > T["vs"]:
            sc = min(pop(t, T["vs"], 0.35), 1.12) * (1 + 0.05 * math.sin((t - T["vs"]) * 6))
            put1(im, vs, 540, PY + PH // 2 - 40, scale=sc)
        frames.append(im.convert("RGB"))
    return frames


FUN = {"nobel": skema_nobel, "beras": skema_beras, "versus": skema_versus}

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
