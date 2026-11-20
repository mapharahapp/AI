"""Animations for Titik Heran #70 (run in the episode work dir; needs Arif's Higgsfield images img/H1.jpg-H5.jpg, 1536x2752;
writes img/H2v.jpg and clips/skema_sakit.mp4, skema_detak.mp4, skema_chip.mp4, skema_kalender.mp4).
stills: H2 (Empire State lit gold) moved down 330 px so the crown sits under the title zone; the sky above is the top rows
  mirrored (the spire starts at y 190, so rows 0-189 are sky only).
sakit: H1 (Voyager, Higgsfield) moved down 320 px so the probe sits below the title; slow push; small glitches at "dia" and
  "sedang", a heavy red glitch (row shifts, RGB split, scanlines, red tint) on "sakit".
detak: H3 (radio dish at night) moved up 380 px so the dish sits above the captions; a green heartbeat line (the carrier
  signal, an image) draws across under the title on "antena", pill "SINYAL: ADA" on "detak", a red "DATA: —" pill blinks
  on "tanpa data".
chip: H4 (circuit board, the red chip at ~(556, 950)); push in; the red chip pulses; on "memindahkan" eight small code
  blocks hop one by one to the healthy chip at ~(870, 775), which gets a green outline; pills "2024: KODE DIPINDAH", then
  "SEMBUH · JUNI 2024" (science data back 13 Jun 2024).
kalender: H5 sky dimmed and softened; on "sakit yang dulu" a calendar sheet NOVEMBER 14 2023 pops in on the left, on "juga"
  one for 2026 on the right; red rings are drawn round both 14s on "empat belas".
Event times are seconds from the start of each clip, read off `render.py 70 plan`. Text stays out of the watermark band
(y 935-985) where it can, the title zone (y < ~600) and the captions (y >= 1210).
usage: python3 skema70.py [stills|sakit|detak|chip|kalender ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
WHITE, GREEN, RED = (255, 255, 255), (70, 255, 150), (235, 40, 40)
N = {"sakit": 84, "detak": 200, "chip": 222, "kalender": 136}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 70 plan`: sakit "tapi" 0.03, "dia" 0.59, "sedang" 1.34, "sakit" 1.71; detak "Masalahnya" 0.05, "antena" 2.65,
# "detak" 4.12, "tanpa" 5.54, "data" 5.77; chip "Kabar" 0.05, "menyembuhkannya" 1.96, "memindahkan" 3.24, "dua" 4.97,
# "kilometer" 6.32; kalender "Anehnya" 0.03, "sakit" 1.11, "dulu" 1.57, "juga" 2.05, "empat" 3.03, "belas" 3.25, "November" 3.48
T = {"g1": 0.59, "g2": 1.34, "g3": 1.66,
     "line0": 2.6, "line1": 3.9, "sig": 4.12, "nodata": 5.5,
     "hop0": 3.24, "hopdt": 0.27, "hopd": 0.5, "p1": 3.3, "heal": 6.2,
     "cal1": 1.08, "cal2": 2.02, "ring1": 3.0, "ring2": 3.22}


def load(k):
    return Image.open(f"img/{k}.jpg").convert("RGB").resize((W, H), Image.LANCZOS)


def shifted(im, dy, edge=None):
    """move the picture down (dy > 0) or up (dy < 0); the uncovered strip is filled with the `edge` rows nearest that side
    (default |dy|), mirrored back and forth"""
    a = np.asarray(im)
    out = np.empty_like(a)
    n = abs(dy)
    m = edge or n
    if dy > 0:
        out[dy:] = a[:H - dy]
        src = a[:m]                         # rows 0..m-1, row 0 at the seam
        for k in range(n):
            j = k % (2 * m)
            out[dy - 1 - k] = src[j] if j < m else src[2 * m - 1 - j]
    else:
        out[:H - n] = a[n:]
        src = a[H - m:][::-1]               # last rows, the bottom row at the seam
        for k in range(n):
            j = k % (2 * m)
            out[H - n + k] = src[j] if j < m else src[2 * m - 1 - j]
    return Image.fromarray(out)


def push(bg, t, dur, z0=1.0, z1=1.06, cx=W / 2, cy=H / 2):
    """slow zoom about (cx, cy)"""
    z = z0 + (z1 - z0) * min(t / dur, 1)
    w, h = W / z, H / z
    x0, y0 = cx - w * cx / W, cy - h * cy / H
    return bg.transform((W, H), Image.EXTENT, (x0, y0, x0 + w, y0 + h), Image.BICUBIC)


def stills():
    im = shifted(load("H2"), 330, edge=185)
    im.save("img/H2v.jpg", quality=94)
    print("img/H2v.jpg")


# ---------- sakit ----------
def glitch(im, amt, seed):
    """row-band shifts, an RGB split and scanlines; amt 0-1"""
    if amt <= 0.01:
        return im
    rng = np.random.default_rng(seed)
    a = np.asarray(im, np.float32).copy()
    for _ in range(int(3 + 9 * amt)):
        y0 = int(rng.uniform(0, H - 40))
        h = int(rng.uniform(6, 30 + 80 * amt))
        dx = int(rng.uniform(-1, 1) * 70 * amt)
        a[y0:y0 + h] = np.roll(a[y0:y0 + h], dx, axis=1)
    sh = int(4 + 18 * amt)
    a[..., 0] = np.roll(a[..., 0], sh, axis=1)
    a[..., 2] = np.roll(a[..., 2], -sh, axis=1)
    a[::4] *= 1 - 0.35 * amt                          # scanlines
    tint = amt ** 1.5
    a[..., 0] = a[..., 0] * (1 + 0.4 * tint) + 30 * tint   # red tint, strong only in the big burst
    a[..., 1:] *= 1 - 0.3 * tint
    return to_img(a)


def skema_sakit(times=None):
    bg = shifted(load("H1"), 320, edge=230)
    frames = []
    for i in range(N["sakit"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = push(bg, t, N["sakit"] / FPS, 1.0, 1.05, 620, 1000)
        amt = 0.0
        for g, d, a in ((T["g1"], 0.12, 0.35), (T["g2"], 0.1, 0.4)):
            if g <= t < g + d:
                amt = a
        if t >= T["g3"]:
            u = t - T["g3"]
            amt = max(amt, (0.95 if u < 0.35 else 0.35 + 0.25 * (math.sin(u * 23) > 0.3)) * (1 if u < 0.7 else 0.6))
        frames.append(glitch(im, amt, i))
    return frames


# ---------- detak ----------
BASE_Y = 690


def ecg_points():
    """a heartbeat trace across the frame: flat, P bump, QRS spike, T bump, every 240 px"""
    pts = []
    for x in range(40, W - 39, 3):
        u = ((x - 40) % 240) / 240
        y = 0.0
        if 0.18 < u < 0.28:
            y = -14 * math.sin((u - 0.18) / 0.10 * math.pi)
        elif 0.36 < u < 0.40:
            y = 18 * (u - 0.36) / 0.04
        elif 0.40 <= u < 0.44:
            y = 18 - 110 * (u - 0.40) / 0.04
        elif 0.44 <= u < 0.49:
            y = -92 + 132 * (u - 0.44) / 0.05
        elif 0.49 <= u < 0.52:
            y = 40 - 40 * (u - 0.49) / 0.03
        elif 0.62 < u < 0.78:
            y = -24 * math.sin((u - 0.62) / 0.16 * math.pi)
        pts.append((x, BASE_Y + y))
    return pts


def skema_detak(times=None):
    bg = shifted(load("H3"), -380, edge=200)
    pts = ecg_points()
    sig = pill("SINYAL: ADA", 34, col=(10, 30, 16), bg=GREEN + (235,), edge=(255, 255, 255, 200))
    nod = pill("DATA: —", 40, col=WHITE, bg=RED + (240,), edge=(255, 255, 255, 220), pad=(26, 12))
    frames = []
    for i in range(N["detak"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = push(bg, t, N["detak"] / FPS, 1.0, 1.05, 540, 950).convert("RGBA")
        if t > T["line0"]:
            u = ease((t - T["line0"]) / (T["line1"] - T["line0"]))
            n = max(2, int(len(pts) * u))
            lay = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(lay)
            band = Image.new("RGBA", (W, H))
            ImageDraw.Draw(band).rectangle([0, BASE_Y - 120, W, BASE_Y + 70], fill=(0, 10, 20, 110))
            im.alpha_composite(band)
            d.line([(x * S, y * S) for x, y in pts[:n]], fill=GREEN + (255,), width=6 * S, joint="curve")
            line = lay.resize((W, H), Image.LANCZOS)
            glow = line.filter(ImageFilter.GaussianBlur(10))
            im.alpha_composite(glow)
            im.alpha_composite(glow)
            im.alpha_composite(line)
            # a bright head that keeps sweeping once the trace is drawn
            hx = pts[n - 1][0] if u < 1 else 40 + ((t - T["line1"]) * 420) % (W - 80)
            hy = min(pts, key=lambda p: abs(p[0] - hx))[1]
            dot = Image.new("RGBA", (W, H))
            ImageDraw.Draw(dot).ellipse([hx - 12, hy - 12, hx + 12, hy + 12], fill=(220, 255, 230, 255))
            im.alpha_composite(dot.filter(ImageFilter.GaussianBlur(4)))
        if t > T["sig"]:
            put1(im, sig, 230, 1140, scale=min(pop(t, T["sig"], 0.3), 1.08))
        if t > T["nodata"]:
            blink = 1.0 if t < T["nodata"] + 0.5 else (0.25 if int((t - T["nodata"]) * 4) % 2 else 1.0)
            put1(im, nod, 840, 1140, a=blink, scale=min(pop(t, T["nodata"], 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


# ---------- chip ----------
SRC, DST = (556, 950), (850, 772)


def skema_chip(times=None):
    bg = load("H4")
    rng = np.random.default_rng(7)
    blocks = [((SRC[0] + rng.uniform(-70, 70), SRC[1] + rng.uniform(-28, 28)),
               (DST[0] + rng.uniform(-70, 70), DST[1] + rng.uniform(-30, 30))) for _ in range(8)]
    blk = Image.new("RGBA", (34 * S, 20 * S))
    ImageDraw.Draw(blk).rounded_rectangle([0, 0, 34 * S - 1, 20 * S - 1], radius=5 * S, fill=(120, 230, 255, 255),
                                           outline=(255, 255, 255, 255), width=2 * S)
    p1 = pill("2024: KODE DIPINDAH", 34)
    p2 = pill("SEMBUH · JUNI 2024", 34, col=(10, 30, 16), bg=GREEN + (235,), edge=(255, 255, 255, 200))
    last = T["hop0"] + 7 * T["hopdt"] + T["hopd"]
    frames = []
    for i in range(N["chip"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = push(bg, t, N["chip"] / FPS, 1.0, 1.07, 700, 860).convert("RGBA")
        z = 1.0 + 0.07 * min(t / (N["chip"] / FPS), 1)

        def sc(p):   # a point on the photo after the push
            return (700 + (p[0] - 700) * z, 860 + (p[1] - 860) * z)
        # the red chip pulses until its code has left
        red = (0.55 + 0.45 * math.sin(t * 6)) * (1 - ramp(t, last - 0.3, last + 0.4))
        if red > 0.02:
            g = Image.new("RGBA", (W, H))
            cx, cy = sc(SRC)
            ImageDraw.Draw(g).ellipse([cx - 170, cy - 95, cx + 170, cy + 95], fill=(255, 40, 30, int(120 * red)))
            im.alpha_composite(g.filter(ImageFilter.GaussianBlur(28)))
        if t > last - 0.2:   # the healthy chip lights up green
            a = ramp(t, last - 0.2, last + 0.3)
            g = Image.new("RGBA", (W, H))
            cx, cy = sc(DST)
            ImageDraw.Draw(g).rounded_rectangle([cx - 145, cy - 105, cx + 145, cy + 105], radius=18, outline=GREEN + (int(255 * a),), width=7)
            im.alpha_composite(g.filter(ImageFilter.GaussianBlur(6)))
            im.alpha_composite(g)
        for k, (a0, a1) in enumerate(blocks):
            t0 = T["hop0"] + k * T["hopdt"]
            if t < t0 - 0.15:
                continue
            u = ease((t - t0) / T["hopd"])
            p0, q = sc(a0), sc(a1)
            x = p0[0] + (q[0] - p0[0]) * u
            y = p0[1] + (q[1] - p0[1]) * u - 150 * math.sin(math.pi * u)
            put1(im, blk, x, y, a=ramp(t, t0 - 0.15, t0))
        if T["p1"] < t < T["heal"] + 0.15:
            put1(im, p1, 540, 1150, a=1 - ramp(t, T["heal"], T["heal"] + 0.15), scale=min(pop(t, T["p1"], 0.3), 1.08))
        if t > T["heal"]:
            put1(im, p2, 540, 1150, scale=min(pop(t, T["heal"], 0.3), 1.08))
        frames.append(im.convert("RGB"))
    return frames


# ---------- kalender ----------
def cal_sheet(year):
    w, h = 400, 470
    sp = Image.new("RGBA", ((w + 30) * S, (h + 30) * S))
    d = ImageDraw.Draw(sp)
    o = 15 * S
    d.rounded_rectangle([o + 8 * S, o + 10 * S, o + w * S + 8 * S, o + h * S + 10 * S], radius=26 * S, fill=(0, 0, 0, 120))
    d.rounded_rectangle([o, o, o + w * S, o + h * S], radius=26 * S, fill=(248, 246, 240, 255))
    d.rounded_rectangle([o, o, o + w * S, o + 110 * S], radius=26 * S, fill=(210, 36, 36, 255))
    d.rectangle([o, o + 70 * S, o + w * S, o + 110 * S], fill=(210, 36, 36, 255))
    for x in (110, 290):  # rings at the top
        d.ellipse([o + (x - 14) * S, o - 12 * S, o + (x + 14) * S, o + 16 * S], fill=(60, 60, 66, 255))
    f1 = ImageFont.truetype(XB, 52 * S)
    f2 = ImageFont.truetype(XB, 200 * S)
    f3 = ImageFont.truetype(XB, 66 * S)
    for txt, f, y, col in (("NOVEMBER", f1, 56, WHITE + (255,)), ("14", f2, 228, (24, 24, 28, 255)), (year, f3, 400, (210, 36, 36, 255))):
        b = f.getbbox(txt)
        d.text((o + w * S / 2 - (b[0] + b[2]) / 2, o + y * S - (b[1] + b[3]) / 2), txt, font=f, fill=col)
    return sp


def ring_sprite(u):
    sp = Image.new("RGBA", (320 * S, 260 * S))
    if u > 0:
        ImageDraw.Draw(sp).arc([12 * S, 12 * S, 308 * S, 248 * S], -100, -100 + 360 * u, fill=RED + (255,), width=12 * S)
    return sp


def skema_kalender(times=None):
    bg = load("H5").filter(ImageFilter.GaussianBlur(3))
    bg = to_img(np.asarray(bg, np.float32) * 0.5)
    c23, c26 = cal_sheet("2023"), cal_sheet("2026")
    L, R, CY = (290, 885), (790, 885), 885
    frames = []
    for i in range(N["kalender"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = push(bg, t, N["kalender"] / FPS, 1.0, 1.05).convert("RGBA")
        for sp, (x, y), t0, rt in ((c23, L, T["cal1"], T["ring1"]), (c26, R, T["cal2"], T["ring2"])):
            if t < t0:
                continue
            k = pop(t, t0, 0.35)
            put1(im, sp, x, y + 60 * (1 - min(k, 1)), a=ramp(t, t0, t0 + 0.15), scale=0.85 + 0.15 * k)
            if t > rt:
                put1(im, ring_sprite(ease((t - rt) / 0.35)), x, y - 12)
        frames.append(im.convert("RGB"))
    return frames


FUN = {"sakit": skema_sakit, "detak": skema_detak, "chip": skema_chip, "kalender": skema_kalender}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    os.makedirs("clips", exist_ok=True)
    todo = args or ["stills"] + list(N)
    if "stills" in todo:
        stills()
    for name in todo:
        if name == "stills":
            continue
        fr = FUN[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
