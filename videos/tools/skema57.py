"""Schematic animations for Titik Heran #57 (run in the episode work dir; needs ../geo/ne_50m_land.geojson from Natural
Earth, img/10532631.jpg and img/gorila128698.png, a frame of Pixabay video 128698 at 3 s; writes clips/skema_peta.mp4,
skema_koran.mp4, skema_versus.mp4).
peta: a world map (Natural Earth), Pulau Komodo and New York pulse, a dashed arc draws from one to the other (a plain line,
  not the 1926 route) and a "1926" pill pops.
koran: an old paper card typed by us: "New York Times, 1926" and the headline "DRAGONS OF LEGEND COME TO BRONX ZOO",
  then a red pill "38.000 pengunjung" pops.
versus: komodo (left) and gorila (right) slide in, a yellow seam, a "VS" badge pops and pulses; runs under the CTA labels.
Event times are seconds from the start of each clip, read off `render.py 57 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 660) and the captions (y >= 1210).
usage: python3 skema57.py [peta|koran|versus ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema53 import land_layer, sea_base, pulse, paper, XB, RG

N = {"peta": 120, "koran": 108, "versus": 225}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
T = {"line0": 0.3, "line1": 3.3, "year": 1.0, "pill": 2.0, "vs": 1.15}   # set from `render.py 57 plan`

# ---------- peta ----------
P_LON0, P_LON1, P_LAT1 = -100.0, 150.0, 62.0
PK = W / (P_LON1 - P_LON0)
P_Y0 = 680
KOMODO, NEWYORK = (119.5, -8.6), (-74.0, 40.7)


def ppx(lon, lat):
    return ((lon - P_LON0) * PK, P_Y0 + (P_LAT1 - lat) * PK)


def arc_pts(a, b, lift=230, n=120):
    (x0, y0), (x1, y1) = a, b
    cx, cy = (x0 + x1) / 2, min(y0, y1) - lift
    return [((1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1, (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1)
            for u in np.linspace(0, 1, n)]


def skema_peta(times=None):
    base = sea_base()
    base.alpha_composite(land_layer(ppx, (P_LON0, P_LON1, -40, P_LAT1)))
    sh = Image.new("RGBA", (W, H))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H], fill=(0, 0, 0, 50))
    base.alpha_composite(sh)
    k0, k1 = ppx(*KOMODO), ppx(*NEWYORK)
    pts = arc_pts(k0, k1)
    lab_k = pill("Pulau Komodo", 32, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220))
    lab_n = pill("New York", 32, col=(255, 255, 255), bg=(150, 30, 30, 220))
    lab_y = pill("1926", 60, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(30, 14))
    note = pill("garis lurus, bukan rute kapal", 24, col=(210, 210, 215), bg=(10, 14, 24, 170))
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
        pulse(im, *k1, (255, 70, 50), t, t1 - 0.1)
        put1(im, lab_k, k0[0] - 70, k0[1] + 70, a=ramp(t, 0.05, 0.3))
        put1(im, lab_n, k1[0] + 70, k1[1] + 66, a=ramp(t, t1 - 0.1, t1 + 0.15))
        if t > T["year"]:
            put1(im, lab_y, 540, 720, scale=min(pop(t, T["year"], 0.35), 1.1))
        put1(im, note, 540, 1170, a=ramp(t, 0.2, 0.45))
        frames.append(im.convert("RGB"))
    return frames


# ---------- koran ----------
def skema_koran(times=None):
    bg = to_img(np.array([30, 24, 18], np.float32) * np.ones((H, W, 1), np.float32)).convert("RGBA")
    pap = to_img(paper()).convert("RGBA")
    m = Image.new("L", (W, H))
    ImageDraw.Draw(m).rounded_rectangle([70, 660, 1010, 1190], radius=10, fill=255)
    card = Image.new("RGBA", (W, H))
    card.paste(pap, (0, 0), m)
    d = ImageDraw.Draw(card)
    ink = (40, 32, 24)
    d.text((540, 712), "NEW YORK TIMES · 1926", font=ImageFont.truetype(XB, 34), fill=ink, anchor="mm")
    d.line([(110, 745), (970, 745)], fill=ink, width=3)
    d.line([(110, 753), (970, 753)], fill=ink, width=1)
    for k, ln in enumerate(["DRAGONS OF LEGEND", "COME TO BRONX ZOO"]):
        d.text((540, 815 + 78 * k), ln, font=ImageFont.truetype(XB, 66), fill=ink, anchor="mm")
    for k in range(5):          # grey "text" columns
        y = 1010 + 26 * k
        for x0 in (110, 400, 690):
            d.line([(x0, y), (x0 + 260 - 40 * (k == 4), y)], fill=(120, 110, 95), width=7)
    d.text((540, 1165), "judul berita asli, diketik ulang", font=ImageFont.truetype(RG, 24), fill=(110, 90, 66), anchor="mm")
    lab = pill("38.000 pengunjung", 46, col=(255, 255, 255), bg=(160, 30, 30, 235), edge=(255, 255, 255, 220), pad=(28, 14))
    frames = []
    for i in range(N["koran"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        u = ease(t / 0.35)
        z = 1 + 0.04 * t / 3.6
        c = card.resize((round(W * z), round(H * z)), Image.LANCZOS).crop(
            (round((W * z - W) / 2), round(925 * z - 925), round((W * z - W) / 2) + W, round(925 * z - 925) + H))
        c.putalpha(c.getchannel("A").point(lambda v: int(v * u)))
        im.alpha_composite(c, (0, round(30 * (1 - u))))
        if t > T["pill"]:
            put1(im, lab, 720, 1060, scale=min(pop(t, T["pill"], 0.35), 1.1))
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
    # komodo 10532631 (1280x769): head near (660, 400); gorilla frame (3840x2160, video 128698 at 3 s): face near (1590, 1000)
    kom = panel("img/10532631.jpg", (350, 0, 970, 769))
    gor = panel("img/gorila128698.png", (890, 130, 2290, 1866))
    bg = to_img(np.array([16, 14, 22], np.float32) * np.ones((H, W, 1), np.float32)).convert("RGBA")
    vs = Image.new("RGBA", (260 * S, 260 * S))
    dv = ImageDraw.Draw(vs)
    dv.ellipse([10 * S, 10 * S, 250 * S, 250 * S], fill=YELLOW + (255,), outline=(20, 20, 20, 255), width=8 * S)
    dv.text((130 * S, 132 * S), "VS", font=ImageFont.truetype(XB, 110 * S), fill=(20, 20, 20, 255), anchor="mm")
    lk = pill("komodo, kini", 24, col=(230, 230, 230), bg=(10, 14, 24, 190))
    lg = pill("gorila, ilustrasi", 24, col=(230, 230, 230), bg=(10, 14, 24, 190))
    frames = []
    for i in range(N["versus"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        u = ease(t / 0.45)
        im.alpha_composite(kom, (round(35 - 600 * (1 - u)), PY))
        im.alpha_composite(gor, (round(555 + 600 * (1 - u)), PY))
        put1(im, lk, 280, PY + 36, a=ramp(t, 0.4, 0.7))
        put1(im, lg, 800, PY + 36, a=ramp(t, 0.4, 0.7))
        if t > T["vs"]:
            sc = min(pop(t, T["vs"], 0.35), 1.12) * (1 + 0.05 * math.sin((t - T["vs"]) * 6))
            put1(im, vs, 540, PY + PH // 2, scale=sc)
        frames.append(im.convert("RGB"))
    return frames


FUN = {"peta": skema_peta, "koran": skema_koran, "versus": skema_versus}

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
