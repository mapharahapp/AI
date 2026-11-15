"""Schematic animations for Titik Heran #60 (run in the episode work dir; needs ../geo/ne_50m_land.geojson from Natural
Earth and clips/37997.mp4; writes clips/karnak60.mp4, skema_hitung.mp4, skema_peta.mp4).
karnak: Pixabay video 37997 (Karnak columns) without its letterbox bars (crop 3840:1632:0:264), scaled to 1080 high.
hitung: 131 small line-drawn cat-skull icons fill a grid, then 81 of them (62%) turn red one by one.
peta: Europe and Egypt (Natural Earth), Beni Hasan and Liverpool pulse, a dashed arc draws between them (a plain line,
  not the ship's route), then a red pill "19,5 ton · dilelang sebagai pupuk".
Event times are seconds from the start of each clip, read off `render.py 60 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 700) and the captions (y >= 1210).
usage: python3 skema60.py [karnak|hitung|peta ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema53 import land_layer, sea_base, pulse

N = {"hitung": 222, "peta": 210}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
T = {"fill0": 0.1, "fill1": 1.9, "red0": 4.35, "red1": 6.0, "line0": 0.5, "line1": 5.6, "ton": 3.4}   # from `render.py 60 plan`

# ---------- hitung ----------
COLS, ROWS, GX0, GY0, CW, CH = 14, 10, 92, 714, 64, 45
BONE, RED = (236, 228, 208), (235, 60, 50)


def icon(col):
    sp = Image.new("RGBA", (60 * S, 46 * S))
    d = ImageDraw.Draw(sp)
    c = col + (255,)
    d.polygon([(11 * S, 18 * S), (13 * S, 3 * S), (25 * S, 11 * S)], fill=c)       # ears
    d.polygon([(49 * S, 18 * S), (47 * S, 3 * S), (35 * S, 11 * S)], fill=c)
    d.ellipse([10 * S, 8 * S, 50 * S, 38 * S], fill=c)                           # skull
    d.rounded_rectangle([22 * S, 30 * S, 38 * S, 43 * S], radius=5 * S, fill=c)  # muzzle
    for x in (21, 39):                                                           # eye sockets
        d.ellipse([(x - 6) * S, 16 * S, (x + 6) * S, 28 * S], fill=(18, 16, 22, 255))
    d.polygon([(30 * S, 29 * S), (27 * S, 34 * S), (33 * S, 34 * S)], fill=(18, 16, 22, 255))
    return sp


def skema_hitung(times=None):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bg = np.array([20, 18, 26], np.float32) * (1 - 0.35 * np.clip(np.hypot((xx - 540) / 800, (yy - 960) / 1100), 0, 1))[..., None]
    bg = to_img(bg).convert("RGBA")
    ib, ir = icon(BONE), icon(RED)
    cells = [(GX0 + CW * (k % COLS) + CW / 2, GY0 + CH * (k // COLS) + CH / 2) for k in range(131)]
    order = np.random.default_rng(60).permutation(131)
    red_rank = {int(k): n for n, k in enumerate(order[:81])}
    lab = pill("81 dari 131 · sakit atau terluka", 30, col=(255, 255, 255), bg=(150, 30, 30, 225))
    frames = []
    for i in range(N["hitung"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        for k, (x, y) in enumerate(cells):
            t_in = T["fill0"] + (T["fill1"] - T["fill0"]) * k / 130
            if t < t_in:
                continue
            sc = min(pop(t, t_in, 0.22), 1.1)
            sp = ib
            if k in red_rank:
                t_r = T["red0"] + (T["red1"] - T["red0"]) * red_rank[k] / 80
                if t >= t_r:
                    sp, sc = ir, sc * (1 + 0.35 * max(0.0, 1 - (t - t_r) / 0.25))
            put1(im, sp, x, y, scale=sc * 0.92)
        put1(im, lab, 540, 1183, a=ramp(t, T["red1"] - 0.3, T["red1"]))
        frames.append(im.convert("RGB"))
    return frames


# ---------- peta ----------
P_LON0, P_LON1, P_LAT1 = -14.0, 42.0, 56.5
PK = W / (P_LON1 - P_LON0)
P_Y0 = 650
BENI, LIVERPOOL = (30.9, 27.9), (-3.0, 53.4)


def ppx(lon, lat):
    return ((lon - P_LON0) * PK, P_Y0 + (P_LAT1 - lat) * PK)


def skema_peta(times=None):
    base = sea_base()
    base.alpha_composite(land_layer(ppx, (P_LON0, P_LON1, 20, P_LAT1 + 6)))
    sh = Image.new("RGBA", (W, H))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H], fill=(0, 0, 0, 50))
    base.alpha_composite(sh)
    k0, k1 = ppx(*BENI), ppx(*LIVERPOOL)
    cx, cy = (k0[0] + k1[0]) / 2 - 150, (k0[1] + k1[1]) / 2 + 150      # bend the arc over the sea, south-west
    pts = [((1 - u) ** 2 * k0[0] + 2 * (1 - u) * u * cx + u * u * k1[0], (1 - u) ** 2 * k0[1] + 2 * (1 - u) * u * cy + u * u * k1[1])
           for u in np.linspace(0, 1, 140)]
    lab_b = pill("Beni Hasan, Mesir", 30, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220))
    lab_l = pill("Liverpool, Inggris", 30, col=(255, 255, 255), bg=(150, 30, 30, 225))
    lab_t = pill("19,5 ton · dilelang sebagai pupuk", 30, col=(255, 255, 255), bg=(150, 30, 30, 235), edge=(255, 255, 255, 220))
    note = pill("garis lurus, bukan rute kapal", 22, col=(210, 210, 215), bg=(10, 14, 24, 170))
    t0, t1 = T["line0"], T["line1"]
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        u = ease((t - t0) / (t1 - t0))
        if u > 0.01:
            dl = Image.new("RGBA", (W * S, H * S))
            dashed(ImageDraw.Draw(dl), pts[:max(2, int(len(pts) * u))], YELLOW + (255,), 5, dash=14, gap=9)
            im.alpha_composite(dl.resize((W, H), Image.LANCZOS))
        pulse(im, *k0, (255, 220, 60), t, 0.0)
        pulse(im, *k1, (255, 70, 50), t, t1 - 0.2)
        put1(im, lab_b, k0[0] - 120, k0[1] - 62, a=ramp(t, 0.05, 0.3))
        put1(im, lab_l, k1[0] + 150, k1[1] - 50, a=ramp(t, t1 - 0.4, t1 - 0.15))
        if t > T["ton"]:
            put1(im, lab_t, 400, 870, scale=min(pop(t, T["ton"], 0.35), 1.08))
        put1(im, note, 300, 1185, a=ramp(t, 0.3, 0.55))
        frames.append(im.convert("RGB"))
    return frames


def karnak():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "clips/37997.mp4", "-vf", "crop=3840:1632:0:264,scale=-2:1920",
                    "-an", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "clips/karnak60.mp4"], check=True)
    print("clips/karnak60.mp4")


FUN = {"hitung": skema_hitung, "peta": skema_peta}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    os.makedirs("clips", exist_ok=True)
    for name in args or ["karnak"] + list(N):
        if name == "karnak":
            karnak()
            continue
        fr = FUN[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
