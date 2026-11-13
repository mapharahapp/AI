"""Schematic animations for Titik Heran #55 (run in the episode work dir; needs ../geo/ne_50m_land.geojson from Natural
Earth; writes clips/skema_rute.mp4, skema_kutipan.mp4 and skema_gajah.mp4).
rute: Java from Natural Earth; Borobudur pulses and eight small cart icons roll to the north coast, then Singosari (Malang)
  pulses with a "±30 menit" pill.
kutipan: an old paper card; Theodoor van Erp's line "kekeliruan yang patut disesalkan dari 1896" appears phrase by phrase.
gajah: a bronze elephant statue on a stepped Javanese-style pedestal drawn as a silhouette with rim light, in front of a
  line drawing of a columned museum facade (no photo of the real statue on Pixabay); "Museum Gajah, Jakarta" pops.
Event times are seconds from the start of each clip, read off `render.py 55 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 660) and the captions (y >= 1210).
usage: python3 skema55.py [rute|kutipan|gajah ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, encode, dashed
from skema35 import sheet, blur
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema49 import path_upto
from skema53 import land_layer, sea_base, pulse, paper, XB, RG, XX, YY

N = {"rute": 100, "kutipan": 75, "gajah": 155}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
T_RUTE = {"t0": 1.6, "singosari": 0.2, "menit": 2.0}   # set from `render.py 55 plan`; t0 starts the map with the carts parked
T_GAJAH = {"museum": 1.6}


# ---------- rute ----------
R_LON0, R_LON1, R_LAT1 = 107.3, 114.3, -5.6
RK = W / (R_LON1 - R_LON0)
R_Y0 = 640


def rpx(lon, lat):
    return ((lon - R_LON0) * RK, R_Y0 + (R_LAT1 - lat) * RK)


BOROBUDUR, SINGOSARI = (110.20, -7.61), (112.66, -7.89)
CARTS = [BOROBUDUR, (110.32, -7.25), (110.42, -6.97)]           # overland to the north coast (Semarang)


def cart_icon():
    sp = Image.new("RGBA", (44 * S, 30 * S))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([4 * S, 4 * S, 34 * S, 18 * S], radius=3 * S, fill=(120, 80, 40, 255), outline=(255, 230, 160, 255), width=2 * S)
    d.line([(34 * S, 12 * S), (42 * S, 12 * S)], fill=(255, 230, 160, 255), width=2 * S)
    d.ellipse([10 * S, 15 * S, 22 * S, 27 * S], fill=(60, 40, 20, 255), outline=(255, 230, 160, 255), width=2 * S)
    return sp


def skema_rute(times=None):
    """Java: Borobudur glows and eight carts roll to the north coast; then Singosari (Malang) pulses with "±30 menit"."""
    base = sea_base()
    base.alpha_composite(land_layer(rpx, (R_LON0, R_LON1, -9.5, R_LAT1)))
    sh = Image.new("RGBA", (W, H))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H], fill=(0, 0, 0, 40))
    base.alpha_composite(sh)
    cart_pts = [rpx(*q) for q in CARTS]
    bx, by = rpx(*BOROBUDUR)
    sx, sy = rpx(*SINGOSARI)
    cart = cart_icon()
    lab_b = pill("Borobudur", 30, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220))
    lab_c = pill("8 gerobak arca", 26, col=(255, 255, 255), bg=(10, 14, 24, 200))
    lab_s = pill("Singosari, Malang", 32, col=(255, 255, 255), bg=(150, 30, 30, 230))
    lab_m = pill("±30 menit", 40, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(26, 12))
    lab_j = pill("Jawa, 1896", 28, col=(210, 210, 215), bg=(10, 14, 24, 170))
    t0 = T_RUTE["t0"]
    t_s, t_m = t0 + T_RUTE["singosari"], t0 + T_RUTE["menit"]
    frames = []
    for i in range(N["rute"]):
        t = i / FPS + t0
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        for k in range(8):                       # eight carts trickle north, then park at the coast
            v = ease((t - k * 0.08) / 0.8)
            if v > 0:
                x, y = path_upto(cart_pts, v)[-1]
                put1(im, cart, x - 14 * (k % 4) + 20, y - 16 * (k // 4), a=ramp(v, 0, 0.1) * (1 - 0.6 * ramp(t, t_s, t_s + 0.3)))
        pulse(im, bx, by, (255, 220, 60), t, 0.0)
        put1(im, lab_b, bx - 20, by + 58, a=ramp(t, 0.05, 0.3) * (1 - 0.5 * ramp(t, t_s, t_s + 0.3)))
        put1(im, lab_c, bx - 10, by - 160, a=ramp(t, 0.4, 0.65) * (1 - ramp(t, t_s, t_s + 0.3)))
        if t > t_s:
            pulse(im, sx, sy, (255, 90, 70), t, t_s)
            put1(im, lab_s, sx - 60, sy + 62, scale=min(pop(t, t_s, 0.3), 1.1))
        if t > t_m:
            put1(im, lab_m, sx - 40, sy - 90, scale=min(pop(t, t_m, 0.3), 1.1))
        put1(im, lab_j, 540, 1170, a=ramp(t, t0 + 0.0, t0 + 0.25) if t0 else ramp(t, 0.2, 0.45))
        frames.append(im.convert("RGB"))
    return frames


# ---------- kutipan ----------
QUOTE = [("“Kekeliruan", 800, 70, (40, 30, 20), 0.15),
         ("yang patut disesalkan", 885, 62, (170, 40, 30), 0.55),
         ("dari 1896.”", 1000, 62, (40, 30, 20), 0.95)]


def skema_kutipan(times=None):
    bg = to_img(np.array([30, 24, 18], np.float32) * np.ones((H, W, 1), np.float32)).convert("RGBA")
    pap = to_img(paper()).convert("RGBA")
    m = Image.new("L", (W, H))
    ImageDraw.Draw(m).rounded_rectangle([60, 690, 1020, 1195], radius=18, fill=255)
    card = Image.new("RGBA", (W, H))
    card.paste(pap, (0, 0), m)
    sh = Image.new("RGBA", (W, H))
    ImageDraw.Draw(sh).rounded_rectangle([74, 708, 1034, 1213], radius=18, fill=(0, 0, 0, 170))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    bg.alpha_composite(card)
    ImageDraw.Draw(bg).line([(110, 722), (970, 722)], fill=(120, 100, 76), width=2)
    sprites = []
    for (txt, y, size, col, t0) in QUOTE:
        f = ImageFont.truetype(XB, size * S)
        x0, y0, x1, y1 = f.getbbox(txt)
        sp = Image.new("RGBA", (x1 - x0 + 20 * S, y1 - y0 + 20 * S))
        ImageDraw.Draw(sp).text((10 * S - x0, 10 * S - y0), txt, font=f, fill=col + (255,))
        sprites.append((sp, y, t0))
    att = Image.new("RGBA", (900 * S, 60 * S))
    ImageDraw.Draw(att).text((450 * S, 30 * S), "— Theodoor van Erp, arkeolog Belanda", font=ImageFont.truetype(RG, 32 * S),
                             fill=(70, 56, 40, 255), anchor="mm")
    frames = []
    for i in range(N["kutipan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        for sp, y, t0 in sprites:
            if t > t0 - 0.05:
                u = ease((t - t0 + 0.05) / 0.25)
                put1(im, sp, 540, y + 14 * (1 - u), a=u)
        put1(im, att, 540, 1140, a=ramp(t, 0.1, 0.35))
        frames.append(im.convert("RGB"))
    return frames


# ---------- gajah ----------
def elephant_mask():
    """2x mask of a standing elephant facing left, about 560 x 470 px at 1x, feet at y=470"""
    m = Image.new("L", (600 * S, 500 * S))
    d = ImageDraw.Draw(m)
    s = S
    d.ellipse([150 * s, 90 * s, 560 * s, 340 * s], fill=255)              # body
    d.ellipse([60 * s, 40 * s, 250 * s, 230 * s], fill=255)               # head
    d.polygon([(110 * s, 150 * s), (175 * s, 160 * s), (150 * s, 260 * s), (128 * s, 360 * s), (118 * s, 420 * s),
               (82 * s, 428 * s), (70 * s, 410 * s), (92 * s, 392 * s), (96 * s, 330 * s), (100 * s, 240 * s)], fill=255)  # trunk
    for x0 in (175, 250, 420, 490):                                       # legs
        d.rounded_rectangle([x0 * s, 260 * s, (x0 + 62) * s, 470 * s], radius=12 * s, fill=255)
    d.polygon([(545 * s, 170 * s), (585 * s, 300 * s), (575 * s, 305 * s), (535 * s, 200 * s)], fill=255)   # tail
    return m.filter(ImageFilter.GaussianBlur(1.2 * S))


def ear_mask():
    m = Image.new("L", (600 * S, 500 * S))
    ImageDraw.Draw(m).polygon([(c[0] * S, c[1] * S) for c in [(205, 70), (290, 62), (330, 120), (320, 230), (270, 260), (230, 240), (210, 180)]], fill=255)
    return m.filter(ImageFilter.GaussianBlur(1.0 * S))


def bronze(mask2x, light=(-0.6, -0.8)):
    """shade a 2x mask as dark bronze with a warm rim light from the upper left"""
    a = np.asarray(mask2x, np.float32) / 255
    b = blur(a, 10 * S)
    gx = np.gradient(b, axis=1)
    gy = np.gradient(b, axis=0)
    nrm = np.hypot(gx, gy) + 1e-6
    rim = np.clip((gx * light[0] + gy * light[1]) / nrm, 0, 1) * np.clip(1 - b, 0, 1) * 2.2
    base = np.array([58, 46, 30], np.float32)
    hi = np.array([235, 190, 110], np.float32)
    rgb = base * (0.75 + 0.25 * b[..., None]) + hi * np.clip(rim, 0, 1)[..., None]
    out = np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def facade():
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    col = (150, 175, 215, 150)
    y0, y1 = 420, 1040
    d.polygon([(110 * S, (y0 + 10) * S), (540 * S, (y0 - 120) * S), (970 * S, (y0 + 10) * S)], outline=col, width=4 * S)   # pediment
    d.line([(90 * S, (y0 + 30) * S), (990 * S, (y0 + 30) * S)], fill=col, width=5 * S)
    for k in range(8):
        x = 140 + k * 114
        d.rectangle([x * S, (y0 + 50) * S, (x + 34) * S, y1 * S], outline=col, width=3 * S)
    d.line([(60 * S, y1 * S), (1020 * S, y1 * S)], fill=col, width=5 * S)
    return lay.resize((W, H), Image.LANCZOS)


def pedestal():
    sp = Image.new("RGBA", (520 * S, 330 * S))
    d = ImageDraw.Draw(sp)
    steps = [(60, 0, 460, 40), (40, 40, 480, 90), (80, 90, 440, 250), (30, 250, 490, 290), (0, 290, 520, 330)]
    for k, (x0, y0, x1, y1) in enumerate(steps):
        g = 92 + 10 * k
        d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=(g, g - 6, g - 14, 255), outline=(200, 190, 170, 255), width=2 * S)
    for x in range(110, 420, 62):                     # carved panels
        d.rounded_rectangle([x * S, 110 * S, (x + 44) * S, 230 * S], radius=6 * S, outline=(180, 170, 150, 255), width=2 * S)
    return sp


def skema_gajah(times=None):
    v = (YY / H)[..., None]
    sky = np.array([24, 34, 64], np.float32) * (1 - v) + np.array([10, 12, 22], np.float32) * v
    base = to_img(sky).convert("RGBA")
    base.alpha_composite(facade())
    fl = Image.new("RGBA", (W, H))
    ImageDraw.Draw(fl).rectangle([0, 1040, W, H], fill=(20, 22, 30, 255))
    base.alpha_composite(fl)
    ele = bronze(elephant_mask())
    ear = bronze(ear_mask(), light=(-0.2, -1.0))
    ele.alpha_composite(ear)
    dd = ImageDraw.Draw(ele)
    dd.polygon([(c[0] * S, c[1] * S) for c in [(150, 205), (118, 262), (98, 280), (112, 284), (138, 262), (165, 215)]], fill=(235, 225, 200, 255))
    dd.ellipse([140 * S, 118 * S, 152 * S, 130 * S], fill=(20, 14, 8, 255))
    ped = pedestal()
    lab_m = pill("Museum Nasional (Museum Gajah), Jakarta", 30)
    lab_h = pill("hadiah Raja Chulalongkorn · kunjungan 1871", 28, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220))
    glow = Image.new("RGBA", (W, H))
    ImageDraw.Draw(glow).ellipse([200, 620, 880, 1060], fill=(255, 200, 120, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    frames = []
    for i in range(N["gajah"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        z = 1.0 + 0.06 * min(t / 4.5, 1)
        im = base.copy()
        im.alpha_composite(glow)
        st = Image.new("RGBA", (W, H))
        put1(st, ped, 540, 1040 + 0 * 165 - 165 + 165, scale=1.0)          # pedestal top at y ~875
        put1(st, ele, 540, 875 - 235 + 5, scale=1.0)
        if z != 1.0:
            st = st.resize((round(W * z), round(H * z)), Image.LANCZOS).crop(
                (round((W * z - W) / 2), round((H * z - H) * 0.55), round((W * z - W) / 2) + W, round((H * z - H) * 0.55) + H))
        im.alpha_composite(st)
        tm = T_GAJAH["museum"]
        if t > tm:
            put1(im, lab_m, 540, 1110, scale=min(pop(t, tm, 0.3), 1.08))
        if t > tm + 1.6:
            put1(im, lab_h, 540, 1170, a=ramp(t, tm + 1.6, tm + 1.85))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"rute": skema_rute, "kutipan": skema_kutipan, "gajah": skema_gajah}

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
