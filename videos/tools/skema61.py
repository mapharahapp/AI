"""Schematic animations for Titik Heran #61 (run in the episode work dir; needs img/4930032.jpg, img/5966113.jpg and
clips/141636.mp4; writes clips/skema_jamur.mp4, skema_kesimpulan.mp4, skema_unesco.mp4).
jamur: six cooked soybean halves; white mould threads grow out of them and knit them together, then the real tempe photo
  fades in where the beans were. Pills "JAMUR RHIZOPUS" and "protein & lemak dipecah".
kesimpulan: an old paper card over the sepia barracks clip: "Banyak tawanan selamat berkat TEMPE", marked as a summary of
  A.G. van Veen's 1946 conclusion (not a quote).
unesco: a calendar card "DESEMBER 2026 / 1-3" over the blurred fried-tempe photo, pills "Sidang Warisan Budaya Takbenda
  UNESCO · Xiamen" and "nominasi: Budaya Tempe", and a pulsing "?" stamp. No UNESCO logo.
Event times are seconds from the start of each clip, read off `render.py 61 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 660) and the captions (y >= 1210).
usage: python3 skema61.py [jamur|kesimpulan|unesco ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode
from skema35 import sheet, SERIF_BI, SERIF_I
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema53 import XB

N = {"jamur": 76, "kesimpulan": 78, "unesco": 129}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# set from `render.py 61 plan`: jamur "mencerna" 0.74, "kedelai" 1.17; kesimpulan "selamat" 0.65, "tempe" 1.79;
# unesco "tempe" 1.62, "warisan" 2.25
T = {"rhizo": 0.7, "pecah": 1.15, "blok": 1.45, "card": 0.0, "tempe": 1.75, "cal": 0.05, "nom": 1.6, "q": 2.2}


def flat(rgb):
    return to_img(np.array(rgb, np.float32) * np.ones((H, W, 1), np.float32)).convert("RGBA")


def cover(path, cx=0.5, cy=0.5):
    im = Image.open(path).convert("RGB")
    k = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x, y = round((im.width - W) * cx), round((im.height - H) * cy)
    return im.crop((x, y, x + W, y + H))


# ---------- jamur ----------
BOX = (250, 700, 830, 1170)   # where the beans sit, and where the tempe block ends up
BEANS = [(360, 790), (540, 770), (720, 800), (380, 1060), (560, 1090), (730, 1050)]


def bean_layer():
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for k, (x, y) in enumerate(BEANS):
        rx, ry, rot = 92, 66, (k * 37) % 50 - 25
        sp = Image.new("RGBA", (2 * rx * S + 20, 2 * ry * S + 20))
        ds = ImageDraw.Draw(sp)
        ds.ellipse([10, 10, 10 + 2 * rx * S, 10 + 2 * ry * S], fill=(236, 206, 128, 255), outline=(176, 140, 70, 255), width=3 * S)
        ds.ellipse([10 + 30 * S, 10 + 16 * S, 10 + 2 * rx * S - 60 * S, 10 + ry * S], fill=(250, 228, 160, 255))  # highlight
        ds.line([(10 + rx * S, 10 + 8 * S), (10 + rx * S, 10 + 2 * ry * S - 8 * S)], fill=(200, 166, 92, 255), width=2 * S)  # the split
        sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
        lay.alpha_composite(sp, (x * S - sp.width // 2, y * S - sp.height // 2))
    return lay.resize((W, H), Image.LANCZOS)


def threads():
    """random-walk mould threads; each point carries the time it appears (0-1 of the growth)"""
    rng = np.random.default_rng(61)
    out = []
    for k in range(340):
        bx, by = BEANS[k % len(BEANS)]
        a = rng.uniform(0, 2 * math.pi)
        x, y = bx + 80 * math.cos(a), by + 58 * math.sin(a)
        heading = a + rng.normal(0, 0.6)
        n = rng.integers(10, 26)
        t0 = rng.uniform(0, 0.45)
        pts = [(x, y, t0)]
        for j in range(n):
            heading += rng.normal(0, 0.45)
            x += 9 * math.cos(heading)
            y += 9 * math.sin(heading)
            cx, cy = (BOX[0] + BOX[2]) / 2, (BOX[1] + BOX[3]) / 2
            if not (BOX[0] + 20 < x < BOX[2] - 20 and BOX[1] + 20 < y < BOX[3] - 20):  # near the edge: bend back inward
                heading += 0.5 * math.remainder(math.atan2(cy - y, cx - x) - heading, 2 * math.pi)
            pts.append((x, y, t0 + (1 - t0) * (j + 1) / n))
        out.append(pts)
    return out


def tempe_block():
    """the real tempe photo (4930032), cropped to the box with rounded corners"""
    im = Image.open("img/4930032.jpg").convert("RGB")
    bw, bh = BOX[2] - BOX[0], BOX[3] - BOX[1]
    # the middle slab, tight on the mould
    c = im.crop((360, 110, 360 + 720, 110 + round(720 * bh / bw)))
    c = c.resize((bw, bh), Image.LANCZOS)
    m = Image.new("L", (bw, bh))
    ImageDraw.Draw(m).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=40, fill=255)
    out = Image.new("RGBA", (bw, bh))
    out.paste(c, (0, 0), m)
    return out


def skema_jamur(times=None):
    bg = flat((34, 24, 16))
    beans = bean_layer()
    th = threads()
    blk = tempe_block()
    l1 = pill("JAMUR RHIZOPUS", 40, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(26, 12))
    l2 = pill("protein & lemak dipecah", 32, col=(255, 255, 255), bg=(10, 14, 24, 215))
    frames = []
    for i in range(N["jamur"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        im.alpha_composite(beans)
        g = ease((t - 0.1) / 1.35)   # growth 0 -> 1
        lay = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(lay)
        for pts in th:
            seg = [(x, y) for x, y, tp in pts if tp <= g]
            if len(seg) > 1:
                d.line(seg, fill=(255, 255, 255, 150), width=2, joint="curve")
        # a soft white felt that thickens as the threads close up
        felt = lay.filter(ImageFilter.GaussianBlur(10))
        felt.putalpha(felt.getchannel("A").point(lambda v: int(min(255, v * (0.6 + 1.6 * g)))))
        im.alpha_composite(felt)
        im.alpha_composite(lay)
        b = ramp(t, T["blok"], T["blok"] + 0.45)
        if b > 0:
            bb = blk.copy()
            bb.putalpha(bb.getchannel("A").point(lambda v: int(v * b)))
            im.alpha_composite(bb, (BOX[0], BOX[1]))
        if t > T["rhizo"]:
            put1(im, l1, 540, 1175, scale=min(pop(t, T["rhizo"], 0.3), 1.1))
        if t > T["pecah"]:
            put1(im, l2, 540, 690, scale=min(pop(t, T["pecah"], 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


# ---------- kesimpulan ----------
def barracks_still():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "2.5", "-i", "clips/141636.mp4", "-frames:v", "1",
                    "-vf", "scale=-2:1920", "clips/k61.png"], check=True)
    im = cover("clips/k61.png", 0.5, 0.5)
    a = np.asarray(im, np.float32)
    sep = a @ np.array([[.393, .349, .272], [.769, .686, .534], [.189, .168, .131]], np.float32)
    im = to_img(sep * 0.42).filter(ImageFilter.GaussianBlur(5))
    return im.convert("RGBA")


def paper_card(w, h):
    rng = np.random.default_rng(7)
    a = np.ones((h, w, 3), np.float32) * np.array([226, 210, 172], np.float32)
    a += rng.normal(0, 6, (h, w, 1))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    edge = np.clip(np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]) / 60, 0, 1)
    a *= (0.78 + 0.22 * edge)[..., None]
    im = to_img(a).convert("RGBA")
    m = Image.new("L", (w, h))
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=14, fill=255)
    im.putalpha(m)
    sh = Image.new("RGBA", (w + 60, h + 60))
    ImageDraw.Draw(sh).rounded_rectangle([30, 36, w + 30, h + 36], radius=18, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    sh.alpha_composite(im, (30, 30))
    return sh


def skema_kesimpulan(times=None):
    bg = barracks_still()
    cw, ch = 760, 500
    card = paper_card(cw, ch)
    d = ImageDraw.Draw(card)
    ink = (52, 38, 26, 255)
    ox, oy = 30, 30
    d.text((ox + 48, oy + 40), "KESIMPULAN", font=ImageFont.truetype(XB, 30), fill=(150, 40, 30, 255))
    d.line([(ox + 48, oy + 84), (ox + cw - 48, oy + 84)], fill=(150, 120, 90, 255), width=2)
    f = ImageFont.truetype(SERIF_BI, 58)
    d.text((ox + 48, oy + 104), "Banyak tawanan", font=f, fill=ink)
    d.text((ox + 48, oy + 170), "selamat berkat", font=f, fill=ink)
    # the card's top sits at y 680 on screen: rows 680+30+104 ... must end before the watermark band at 935
    fs = ImageFont.truetype(SERIF_I, 30)
    d.text((ox + 48, oy + 352), "ringkasan kesimpulan A.G. van Veen,", font=fs, fill=(90, 70, 50, 255))
    d.text((ox + 48, oy + 392), "ilmuwan pangan yang ikut ditawan (1946)", font=fs, fill=(90, 70, 50, 255))
    big = pill("TEMPE", 64, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230), pad=(30, 12))
    frames = []
    for i in range(N["kesimpulan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        u = ease(t / 0.35)
        c = card.rotate(-2.5 * (1 - u) - 1.0, resample=Image.BICUBIC, expand=True)
        c.putalpha(c.getchannel("A").point(lambda v: int(v * min(1, u * 1.4))))
        im.alpha_composite(c, (540 - c.width // 2, round(650 + 40 * (1 - u))))
        # "TEMPE" stamped at the end of the second line, clear of the watermark band
        if t > T["tempe"] - 0.6:
            put1(im, big, 760, 878, scale=min(pop(t, T["tempe"] - 0.6, 0.3), 1.1) * 0.9)
        frames.append(im.convert("RGB"))
    return frames


# ---------- unesco ----------
def skema_unesco(times=None):
    bg = cover("img/5966113.jpg", 0.5, 0.5).filter(ImageFilter.GaussianBlur(9))
    bg = to_img(np.asarray(bg, np.float32) * 0.42).convert("RGBA")
    cw, chh = 460, 250
    cal = Image.new("RGBA", (cw * S, chh * S))
    d = ImageDraw.Draw(cal)
    d.rounded_rectangle([0, 0, cw * S - 1, chh * S - 1], radius=22 * S, fill=(250, 248, 242, 255))
    d.rounded_rectangle([0, 0, cw * S - 1, 70 * S], radius=22 * S, fill=(200, 40, 40, 255))
    d.rectangle([0, 40 * S, cw * S - 1, 70 * S], fill=(200, 40, 40, 255))
    d.text((cw * S // 2, 36 * S), "DESEMBER 2026", font=ImageFont.truetype(XB, 36 * S), fill=(255, 255, 255, 255), anchor="mm")
    d.text((cw * S // 2, 160 * S), "1–3", font=ImageFont.truetype(XB, 130 * S), fill=(30, 30, 30, 255), anchor="mm")
    for k in (0.3, 0.7):  # two binder rings
        x = round(cw * S * k)
        d.rounded_rectangle([x - 8 * S, -2, x + 8 * S, 22 * S], radius=6 * S, fill=(70, 70, 70, 255))
    l1 = pill("Sidang Warisan Budaya Takbenda UNESCO", 30, col=(255, 255, 255), bg=(10, 14, 24, 215))
    l2 = pill("Xiamen, Tiongkok", 28, col=(225, 225, 230), bg=(10, 14, 24, 190))
    l3 = pill("nominasi: Budaya Tempe", 38, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(26, 12))
    q = Image.new("RGBA", (200 * S, 200 * S))
    dq = ImageDraw.Draw(q)
    dq.ellipse([8 * S, 8 * S, 192 * S, 192 * S], fill=YELLOW + (255,), outline=(20, 20, 20, 255), width=8 * S)
    dq.text((100 * S, 104 * S), "?", font=ImageFont.truetype(XB, 130 * S), fill=(20, 20, 20, 255), anchor="mm")
    frames = []
    for i in range(N["unesco"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        put1(im, cal, 470, 800, scale=min(pop(t, T["cal"], 0.35), 1.08))
        put1(im, l1, 540, 1030, a=ramp(t, 0.35, 0.6))
        put1(im, l2, 540, 1085, a=ramp(t, 0.5, 0.75))
        if t > T["nom"]:
            put1(im, l3, 540, 1160, scale=min(pop(t, T["nom"], 0.3), 1.1))
        if t > T["q"]:
            put1(im, q, 820, 735, scale=min(pop(t, T["q"], 0.35), 1.12) * (1 + 0.07 * math.sin((t - T["q"]) * 7)) * 0.8)
        frames.append(im.convert("RGB"))
    return frames


FUN = {"jamur": skema_jamur, "kesimpulan": skema_kesimpulan, "unesco": skema_unesco}

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
