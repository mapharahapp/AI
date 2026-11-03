"""Schematic animations for Titik Heran #38 (run in the episode work dir after `dl.py i:935258 i:4496863`;
writes img/935258v.jpg, clips/skema_scan.mp4 and clips/skema_apotek.mp4).
usage: python3 skema38.py [face|scan|apotek ...] [--sheet out.jpg t1,t2,...]
No photo of the Marburg mummy head or of the 18th-century mumia preparation is free to use, so:
img/935258v.jpg: the museum mummy face (Pixabay 935258, a stand-in) set into the 9:16 frame at 1,55x with its edges continued,
  so the whole face reads at once (a plain cover crop shows only an eye socket and the nose).
skema_scan: a green scan line sweeps down that face and lights up spots where the aloe compounds turn up, two of them tagged
  "aloin" and "aloeresin". The study found the compounds by chemical analysis of samples, not by scanning a face: the sweep
  and the spots are a schematic.
skema_apotek: a slow pan along a black-and-white apothecary shelf (Pixabay 4496863, a stand-in, set lower so its ALOE jar ends
  up under the subtitles) that comes to rest on the ALOE jar, which a soft light picks out. Aloe was a common pharmacy drug;
  this jar is not the mumia that was tested.
Event times are seconds from the start of each clip, read off `render.py 38 plan`: skema_scan starts at 16,03 ("Jejaknya"
0,05, "muncul" 0,76, "kepala" 1,36, "mumi" 1,64, "itu..." 1,96), skema_apotek at 19,03 ("obat" 0,43, "bubuk" 0,67,
"mumi" 0,95, "abad" 1,39, "belas." 2,15).
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, ramp, pop, encode
from skema35 import blur, sheet
from skema36 import reframe

N = {"scan": 100, "apotek": 96}  # each clip runs ~0,3 s past its shot
BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
GREEN, MINT = np.array([60, 255, 140], np.float32), np.array([205, 255, 215], np.float32)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

# the face still: 1,55x, the scaled photo's column 374 on the left edge and its top at frame row 311
FS, FX, FY = 1.55, 374, 311


def face_still():
    reframe("img/935258.jpg", FS, FX, FY, "img/935258v.jpg")
    # the continued bands streak where the photo's edge is lit: let them fall off into shadow toward the frame edges
    a = np.asarray(Image.open("img/935258v.jpg"), np.float32)
    top, bot = FY, FY + round(853 * FS)
    g = np.ones(H, np.float32)
    g[:top] = 0.4 + 0.6 * np.linspace(0, 1, top) ** 1.5
    g[bot:] = 0.4 + 0.6 * np.linspace(1, 0, H - bot) ** 1.5
    Image.fromarray((a * g[:, None, None]).clip(0, 255).astype(np.uint8)).save("img/935258v.jpg", quality=95)


def fxy(ix, iy):
    """a point of the 1280x853 photo in the face still's frame"""
    return ix * FS - FX, iy * FS + FY


def wanted(i, times):
    return times is None or any(abs(i / FPS - x) < 0.5 / FPS for x in times)


def dim(a):
    """close to render.py's "dim" grade, so the scan reads as the same museum shot as the face before it"""
    y = a @ np.array([0.299, 0.587, 0.114], np.float32)
    return np.clip(((y - 128) * 1.05 + 128 - 22)[..., None] + (a - y[..., None]) * 0.85, 0, 255)


def zoomed(base, z, cx, cy):
    """base (float HxWx3) scaled by z about (cx, cy), as a PIL image"""
    if z == 1.0:
        return Image.fromarray(base.astype(np.uint8))
    w, h = W / z, H / z
    x0, y0 = cx - cx / z, cy - cy / z
    im = Image.fromarray(base.astype(np.uint8))
    return im.transform((W, H), Image.EXTENT, (x0, y0, x0 + w, y0 + h), Image.BICUBIC)


def chip(text, size=34):
    """a small dark tag with green text, 2x"""
    f = ImageFont.truetype(BOLD, size * S)
    b = f.getbbox(text)
    w, h = b[2] - b[0] + 36 * S, b[3] - b[1] + 22 * S
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=10 * S, fill=(6, 28, 16, 215), outline=(60, 255, 140, 255), width=3 * S)
    d.text((18 * S - b[0], 11 * S - b[1]), text, font=f, fill=(205, 255, 215, 255))
    return im.resize((w // S, h // S), Image.LANCZOS)


# ---------- skema_scan ----------
DOTS = [fxy(*p) for p in [(500, 120), (610, 150), (420, 300), (560, 280), (760, 330), (520, 400), (700, 470), (560, 560),
                          (860, 560), (700, 640), (480, 640), (620, 730), (380, 560), (800, 720)]]
TAGS = [("aloin", 4, (870, 735), 1.40), ("aloeresin", 7, (300, 1100), 1.68)]  # text, dot index, chip centre, pop time
Y0, Y1, T0, T1 = 300, 1680, 0.12, 1.45  # the line runs from Y0 to Y1 between T0 and T1


def line_y(t):
    return Y0 + (Y1 - Y0) * ramp(t, T0, T1)


def hit_time(y):
    """when the line passes row y (bisection on the eased sweep)"""
    lo, hi = T0, T1
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if line_y(mid) < y else (lo, mid)
    return lo


def skema_scan(times=None):
    base = dim(np.asarray(Image.open("img/935258v.jpg").convert("RGB"), np.float32))
    chips = [chip(t) for t, *_ in TAGS]
    hits = [hit_time(y) for _, y in DOTS]
    frames = []
    for i in range(N["scan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        a = base.copy()
        yl = line_y(t)
        on = ramp(t, T0 - 0.08, T0) * (1 - ramp(t, T1, T1 + 0.25))  # the line itself
        tint = ramp(t, T0, T0 + 0.2) * (1 - ramp(t, T1 + 0.1, T1 + 0.6))  # the green wash over the scanned part
        if on > 0 or tint > 0:
            d = YY - yl
            glow = on * (0.85 * np.exp(-(d / 4) ** 2) + 0.45 * np.exp(-(d / 22) ** 2) + 0.18 * np.exp(-(d / 90) ** 2))
            grid = ((np.abs((XX % 54) - 27) > 25.5) | (np.abs((YY % 54) - 27) > 25.5)).astype(np.float32)
            band = on * 0.16 * grid * np.exp(-(d / 160) ** 2)
            wash = tint * 0.10 / (1 + np.exp(np.clip(d / 24, -40, 40)))  # soft edge: no step left behind once the line fades
            k = np.clip(glow + band + wash, 0, 1)[..., None]
            a = a * (1 - 0.35 * k) + GREEN * k  # green over a slightly darkened face
            a = np.where((np.abs(d) < 1.5)[..., None] & (on > 0.5), MINT, a)
        for (x, y), th in zip(DOTS, hits):  # a ring opens where the line finds a trace, then the spot keeps glowing
            if t < th:
                continue
            u = t - th
            x0, x1, y0, y1 = int(max(0, x - 90)), int(min(W, x + 90)), int(max(0, y - 90)), int(min(H, y + 90))
            r = np.hypot(XX[y0:y1, x0:x1] - x, YY[y0:y1, x0:x1] - y)
            R = 12 + 70 * ramp(u, 0, 0.45)
            ring = (1 - ramp(u, 0.15, 0.5)) * np.exp(-((r - R) / 3.5) ** 2)
            pulse = 0.85 + 0.15 * np.sin(2 * np.pi * (t - th) * 1.6)
            core = ramp(u, 0, 0.12) * pulse * (np.clip(9 - r, 0, 1.5) / 1.5 * 0.9 + 0.55 * np.exp(-(r / 16) ** 2))
            k = np.clip(ring * 0.9 + core, 0, 1)[..., None]
            a[y0:y1, x0:x1] = a[y0:y1, x0:x1] * (1 - k) + np.where(r[..., None] < 6, MINT, GREEN) * k
        im = zoomed(a.clip(0, 255), 1 + 0.05 * t / (N["scan"] / FPS), 560, 950).convert("RGBA")
        z = 1 + 0.05 * t / (N["scan"] / FPS)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(ov)
        for (text, di, (cx, cy), tp), sp in zip(TAGS, chips):  # tags ride the zoom with their dots
            if t < tp:
                continue
            al = ramp(t, tp, tp + 0.15)
            dx, dy = DOTS[di]
            dx, dy = 560 + (dx - 560) * z, 950 + (dy - 950) * z
            cx, cy = 560 + (cx - 560) * z, 950 + (cy - 950) * z
            ex = cx - sp.width / 2 if cx > dx else cx + sp.width / 2  # the leader meets the chip's near side
            dr.line([(dx, dy), (ex, cy)], fill=(60, 255, 140, int(230 * al)), width=3)
            s = 0.8 + 0.2 * pop(t, tp, 0.3)
            c = sp.resize((max(1, round(sp.width * s)), max(1, round(sp.height * s))), Image.LANCZOS)
            c.putalpha(c.getchannel("A").point(lambda v: int(v * al)))
            ov.alpha_composite(c, (round(cx - c.width / 2), round(cy - c.height / 2)))
        im.alpha_composite(ov)
        frames.append(im.convert("RGB"))
    return frames


# ---------- skema_apotek ----------
JS = 1920 / 853  # the shelf photo at cover scale
JDY = 260  # set 260 rows lower: the ALOE label (photo 178, 609) lands at frame y ~1630, under the subtitles
ALOE = (178 * JS, 609 * JS + JDY)  # in the scaled photo, x before the pan offset
P0, P1, TP0, TP1 = 0.42, 0.02, 0.0, 2.2  # pan from 42 % to 2 % of the free width


def skema_apotek(times=None):
    im = Image.open("img/4496863.jpg").convert("RGB")
    big = np.asarray(im.resize((round(im.width * JS), round(im.height * JS)), Image.LANCZOS), np.float32)
    canvas = np.zeros((H, big.shape[1], 3), np.float32)
    canvas[JDY:] = big[:H - JDY]
    # the top rows continued upward over the photo's full width (as skema36.edge_fill, which is one frame wide), falling
    # off into shadow toward the frame's top edge
    edge = big[:6].mean(0)
    for k in range(JDY):
        d = (k + 1) / JDY
        r = max(1, int(4 + 60 * d))
        c = np.cumsum(np.pad(edge, ((r + 1, r), (0, 0)), mode="edge"), 0)
        canvas[JDY - 1 - k] = (c[2 * r + 1:] - c[:-2 * r - 1]) / (2 * r + 1) * (1 - 0.12 * d) * (0.4 + 0.6 * (1 - d) ** 1.5)
    canvas[JDY - 10:JDY + 10] = blur(canvas[JDY - 30:JDY + 30], 2)[20:40]
    free = big.shape[1] - W
    frames = []
    for i in range(N["apotek"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        p = P0 + (P1 - P0) * ramp(t, TP0, TP1)
        x = free * p
        xi = int(x)
        f = canvas[:, xi:xi + W + 1]
        fr = x - xi
        a = f[:, :W] * (1 - fr) + f[:, 1:W + 1] * fr  # sub-pixel pan
        lt = ramp(t, 1.7, 2.4)  # a soft light finds the ALOE jar as the pan settles
        if lt > 0:
            ax, ay = ALOE[0] - x, ALOE[1]
            g = np.exp(-(((XX - ax) / 330) ** 2 + ((YY - ay + 40) / 420) ** 2))
            a = a * (1 + lt * (0.22 * g - 0.18 * (1 - g)))[..., None]
        frames.append(Image.fromarray(a.clip(0, 255).astype(np.uint8)))
    return frames


if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or ["face", "scan", "apotek"]
    if "face" in todo:
        face_still()
    for name, fn in [("scan", skema_scan), ("apotek", skema_apotek)]:
        if name in todo:
            fr = fn(times)
            if times is not None:
                sheet(fr, name, out)
            else:
                encode(fr, f"clips/skema_{name}.mp4")
