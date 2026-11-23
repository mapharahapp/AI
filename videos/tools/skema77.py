"""Schematic animations for Titik Heran #77 (run in the episode work dir; writes clips/skema_penggaris.mp4,
skema_makin.mp4, skema_suara.mp4).
penggaris: Pixabay photo 212825 (male proboscis monkey in profile on a rail, Labuk Bay) framed so the nose sits under
  the title zone; a yellow ruler grows down beside the nose, pill "10+ cm"; on "melewati" a dashed line marks the mouth
  and an arrow runs from the mouth line to the nose tip, pill "melewati mulut". Schematic, not a measurement.
makin: three rows on a dark mangrove-green backdrop, bars rise in turn: HIDUNG, BADAN (note "jantan +-20 kg, betina
  +-separuhnya", EurekAlert / Wikipedia), BETINA with female icons popping in 1 -> 4; pill "Science Advances, 2018"
  (Koda dkk.). The study found a correlation; the bars only say "more goes with more". The clip runs in two parts in
  the video (shots 09 and 11 of `render.py 77 plan`), the group photo 10376925 sits between them.
suara: photo 10547221 (male calling) dimmed; two waves: "hidung kecil" thin and fast, "hidung besar" wide and slow
  (lower pitch = "suara lebih berat", EurekAlert: "making their voices lower when attracting a female").
Event times are seconds from the start of each clip, read off `render.py 77 plan`. Text stays out of the watermark
band (y 935-985), the title zone (y < ~650) and the captions (y >= 1210).
usage: python3 skema77.py [penggaris|makin|suara ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, text_sprite
from skema35 import sheet
from skema37 import put1
from skema46 import pill, ease, wanted
from skema74 import backdrop

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
WHITE = (255, 255, 255)
N = {"penggaris": 54, "makin": 129, "suara": 69}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 77 plan`: penggaris = shot 06 ("menggantung" 0.02, "melewati" 0.58, "mulut" 0.99, cut 1.63);
# makin = shot 09 ("makin" 0.03, "besar" 0.32, "badannya" 0.77, cut 1.63) + group photo 1.03 s + shot 11 at 2.67
# ("betina" 2.71, "kelompoknya" 3.12, cut 3.97); suara = shot 13 ("suara" 0.04, "lebih" 0.34, "berat" 0.64,
# "saat" 1.01, "merayu" 1.24, cut 2.03)
T = {"ruler": 0.04, "cm": 0.30, "mouth": 0.55, "arrow": 0.62, "mpill": 0.85,
     "hidung": 0.0, "badan": 0.30, "kg": 0.70, "betina": 2.69, "icons": 2.76, "sci": 2.95,
     "wa": 0.02, "wb": 0.30, "wlab": 0.62}


# ---------- penggaris ----------
PZ, PX, PY = 3.1, -1327, 0          # photo scale and offset: the nose (600-655, 195-305 in 1280x848) lands at x 533-703, y 605-945


def profile_bg():
    im = Image.open("img/212825.jpg").convert("RGB")
    big = im.resize((round(im.width * PZ), round(im.height * PZ)), Image.LANCZOS)
    big = big.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
    can = Image.new("RGB", (W, H))
    can.paste(big, (PX, PY))
    return can.convert("RGBA")


def P(x, y):
    return x * PZ + PX, y * PZ + PY


def ruler_sprite(h):
    w = 56
    sp = Image.new("RGBA", ((w + 20) * S, (h + 20) * S))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([10 * S, 10 * S, (10 + w) * S, (10 + h) * S], radius=8 * S, fill=YELLOW + (240,), outline=(40, 30, 0, 255), width=3 * S)
    for k in range(0, h - 4, 17):
        L = 26 if k % 85 == 0 else 14
        d.line([(10 * S, (10 + k + 8) * S), ((10 + L) * S, (10 + k + 8) * S)], fill=(40, 30, 0, 255), width=3 * S)
    return sp


def skema_penggaris(times=None):
    bg = profile_bg()
    nx0, ny0 = P(600, 195)
    nx1, ny1 = P(655, 305)
    mx, my = P(585, 266)                        # corner of the mouth
    rx, rh = nx1 + 70, round(ny1 - ny0)
    rul = ruler_sprite(rh)
    cm = pill("10+ cm", 46, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230))
    mp = pill("melewati mulut", 36, col=WHITE, bg=(10, 14, 24, 215), edge=(255, 255, 255, 160))
    ml = text_sprite([("mulut", 30, WHITE, True)])
    frames = []
    for i in range(N["penggaris"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        z = 1.0 + 0.035 * t / (N["penggaris"] / FPS)
        cx, cy = (nx0 + nx1) / 2, (ny0 + ny1) / 2
        w_, h_ = W / z, H / z
        x0, y0 = cx - w_ * cx / W, cy - h_ * cy / H
        im = bg.transform((W, H), Image.EXTENT, (x0, y0, x0 + w_, y0 + h_), Image.BICUBIC)
        zp = lambda x, y: (cx + (x - cx) * z, cy + (y - cy) * z)
        d = ImageDraw.Draw(im)
        # ruler: grows down from the top of the nose
        u = ease((t - T["ruler"]) / 0.4)
        if u > 0:
            r = rul.crop((0, 0, rul.width, max(1, round((20 + rh * u) * S))))
            rx_, ry_ = zp(rx, ny0)
            im.alpha_composite(r.resize((max(1, r.width // S), max(1, r.height // S)), Image.LANCZOS), (round(rx_ - 38), round(ry_ - 10)))
        tx, ty = zp(rx + 175, (ny0 + ny1) / 2)
        put1(im, cm, tx, ty, scale=min(pop(t, T["cm"], 0.3), 1.05))
        # mouth line, dashed, and the arrow down to the nose tip
        a = ramp(t, T["mouth"], T["mouth"] + 0.12)
        if a > 0:
            lay = Image.new("RGBA", (W, H))
            dl = ImageDraw.Draw(lay)
            y = zp(mx, my)[1]
            xa, xb = zp(mx - 150, my)[0], zp(rx + 20, my)[0]
            x = xa
            while x < xb:
                dl.line([(x, y), (min(x + 22, xb), y)], fill=(255, 255, 255, int(235 * a)), width=5)
                x += 36
            im.alpha_composite(lay)
            put1(im, ml, zp(mx - 225, my)[0], y, a=a)
        v = ease((t - T["arrow"]) / 0.3)
        if v > 0:
            lay = Image.new("RGBA", (W * S, H * S))
            dl = ImageDraw.Draw(lay)
            ax, ay0 = zp(nx1 + 22, my)
            ay1 = zp(nx1, ny1 - 8)[1]
            ay = ay0 + (ay1 - ay0) * v
            dl.line([(ax * S, ay0 * S), (ax * S, ay * S)], fill=YELLOW + (255,), width=7 * S)
            if v > 0.6:
                dl.polygon([((ax - 16) * S, (ay - 18) * S), ((ax + 16) * S, (ay - 18) * S), (ax * S, (ay + 6) * S)], fill=YELLOW + (255,))
            im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        put1(im, mp, 540, 1075, scale=min(pop(t, T["mpill"], 0.3), 1.05))
        frames.append(im.convert("RGB"))
    return frames


# ---------- makin ----------
ROWS = [("HIDUNG", 705, "hidung"), ("BADAN", 805, "badan"), ("BETINA", 900, "betina")]
BX0, BX1, BH = 360, 990, 62


def female_icon(r=18, col=(40, 30, 0, 255)):
    sp = Image.new("RGBA", ((2 * r + 12) * S, (3 * r + 22) * S))
    d = ImageDraw.Draw(sp)
    c = (r + 6) * S
    d.ellipse([c - r * S, 6 * S, c + r * S, (6 + 2 * r) * S], outline=col, width=5 * S)
    d.line([(c, (6 + 2 * r) * S), (c, (6 + 3 * r + 10) * S)], fill=col, width=5 * S)
    d.line([(c - 11 * S, (6 + 2 * r + 12) * S), (c + 11 * S, (6 + 2 * r + 12) * S)], fill=col, width=5 * S)
    return sp


def up_arrow(col=YELLOW + (255,)):
    sp = Image.new("RGBA", (60 * S, 60 * S))
    ImageDraw.Draw(sp).polygon([(30 * S, 6 * S), (54 * S, 40 * S), (38 * S, 40 * S), (38 * S, 56 * S), (22 * S, 56 * S), (22 * S, 40 * S), (6 * S, 40 * S)], fill=col)
    return sp


def skema_makin(times=None):
    bg = backdrop((16, 46, 34), (4, 12, 9), glow=(14, 40, 26), gy=820)
    f = ImageFont.truetype(XB, 46)
    labels = []
    for name, y, _ in ROWS:
        lay = Image.new("RGBA", (W, H))
        dl = ImageDraw.Draw(lay)
        dl.text((84 + 2, y + 3), name, font=f, fill=(0, 0, 0, 170), anchor="lm")
        dl.text((84, y), name, font=f, fill=WHITE + (255,), anchor="lm")
        labels.append(lay)
    track = Image.new("RGBA", (W, H))
    dt = ImageDraw.Draw(track)
    for _, y, _ in ROWS:
        dt.rounded_rectangle([BX0, y - BH // 2, BX1, y + BH // 2], radius=BH // 2, fill=(255, 255, 255, 34))
    kg = text_sprite([("jantan ±20 kg · betina ±separuhnya", 34, (225, 235, 228), False)])
    sci = pill("Science Advances, 2018", 32, col=WHITE, bg=(10, 14, 24, 215), edge=(255, 255, 255, 150))
    icon, arrow = female_icon(), up_arrow()
    frames = []
    for i in range(N["makin"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        im.alpha_composite(track)
        for (name, y, key), lab in zip(ROWS, labels):
            a = ramp(t, T[key] - 0.05, T[key] + 0.1) if key != "hidung" else 1.0
            if a <= 0:
                continue
            u = 0.92 * ease((t - T[key]) / 0.5) if key != "hidung" else 0.92 * (0.55 + 0.45 * ease(t / 0.3))
            lay = Image.new("RGBA", (W * S, H * S))
            dl = ImageDraw.Draw(lay)
            xe = BX0 + (BX1 - BX0) * max(u, 0.1)
            dl.rounded_rectangle([BX0 * S, (y - BH // 2) * S, xe * S, (y + BH // 2) * S], radius=BH // 2 * S, fill=YELLOW + (int(255 * a),))
            im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
            if a < 1:
                lab = lab.copy()
                lab.putalpha(lab.getchannel("A").point(lambda q, a=a: int(q * a)))
            im.alpha_composite(lab)
            put1(im, arrow, xe + 32, y, a=a * ramp(u, 0.3, 0.6), scale=0.9)
        for k in range(4):                         # female icons inside the BETINA bar, 1 -> 4
            put1(im, icon, BX0 + 60 + 130 * k, 900, scale=min(pop(t, T["icons"] + 0.15 * k, 0.25), 1.05))
        put1(im, kg, 540, 1040, a=ramp(t, T["kg"], T["kg"] + 0.15))
        put1(im, sci, 540, 1130, scale=min(pop(t, T["sci"], 0.3), 1.05))
        frames.append(im.convert("RGB"))
    return frames


# ---------- suara ----------
def calling_bg():
    im = Image.open("img/10547221.jpg").convert("RGB")
    s_ = H / im.height
    big = im.resize((round(im.width * s_), H), Image.LANCZOS)
    x0 = round((big.width - W) * 0.6)
    im = big.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(3))
    im = Image.blend(im, Image.new("RGB", (W, H)), 0.58)
    return im.convert("RGBA")


def wave(im, y, amp, lam, phase, upto, col, width):
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    x0, x1 = 90, 990
    xe = x0 + (x1 - x0) * upto
    pts = []
    x = x0
    while x <= xe:
        env = math.sin(math.pi * (x - x0) / (x1 - x0)) ** 0.6
        pts.append((x * S, (y + amp * env * math.sin(2 * math.pi * (x - x0) / lam + phase)) * S))
        x += 3
    if len(pts) > 1:
        d.line(pts, fill=col, width=width * S, joint="curve")
    im.alpha_composite(lay.resize((W, H), Image.LANCZOS))


def skema_suara(times=None):
    bg = calling_bg()
    la = text_sprite([("hidung kecil", 36, (230, 230, 230), False)])
    lb = text_sprite([("hidung besar", 40, YELLOW, True)])
    lc = pill("suara lebih berat", 38, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230))
    frames = []
    for i in range(N["suara"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        ua, ub = ease((t - T["wa"]) / 0.3), ease((t - T["wb"]) / 0.35)
        put1(im, la, 540, 690, a=ramp(t, T["wa"], T["wa"] + 0.1))
        if ua > 0:
            wave(im, 775, 42, 46, -t * 26, ua, (255, 255, 255, 230), 5)
        put1(im, lb, 300, 1025, a=ramp(t, T["wb"], T["wb"] + 0.1))
        if ub > 0:
            wave(im, 1115, 62, 190, -t * 9, ub, YELLOW + (255,), 8)
        put1(im, lc, 730, 1025, scale=min(pop(t, T["wlab"], 0.3), 1.05))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"penggaris": skema_penggaris, "makin": skema_makin, "suara": skema_suara}

if __name__ == "__main__":
    args = sys.argv[1:]
    out, TIMES = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, TIMES = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    os.makedirs("clips", exist_ok=True)
    for name in args or list(N):
        fr = FUN[name](TIMES)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
