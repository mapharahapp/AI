"""Schematic animations for Titik Heran #56 (run in the episode work dir; needs ../geo/ne_50m_land.geojson from Natural
Earth; writes clips/skema_logo.mp4, skema_pausanias.mp4, skema_denah.mp4).
logo: a blue six-armed Star of Life drawn by hand (no real logo), the rod with one snake wound round it in white; the star
  fades and the rod stays, "tongkat Asclepius" pops; used for the CTA (BERANI / NGGAK buttons come from render.py titles).
pausanias: an old scroll card "Pausanias, ±160 M" with his line about the sanctuary; then a map of the Peloponnese from
  Natural Earth with Epidaurus pulsing and a "?" bobbing over it.
denah: a plain site plan: the Small Theatre (half circle) and a box "tempat suci Asclepius" with a dimension line "±20 m",
  then a sherd shape with the letters ΑΣΚΛΗΠΙ scratched in.
Event times are seconds from the start of each clip, read off `render.py 56 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 660) and the captions (y >= 1210).
usage: python3 skema56.py [logo|pausanias|denah ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, encode, dashed
from skema35 import sheet, blur
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema53 import land_layer, sea_base, pulse, paper, XB, RG, XX, YY

N = {"logo": 60, "pausanias": 130, "denah": 120}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
T = {"map": 2.14, "sherd": 0.9, "letters": 1.3}   # set from `render.py 56 plan`


def navy_bg():
    v = (YY / H)[..., None]
    a = np.array([20, 30, 58], np.float32) * (1 - v) + np.array([8, 10, 20], np.float32) * v
    return to_img(a).convert("RGBA")


# ---------- logo ----------
def star_layer(cx, cy, r, w):
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for k in range(3):
        a = math.radians(90 + 60 * k)
        dx, dy = math.cos(a), math.sin(a)
        px, py = -dy, dx
        pts = [(cx + dx * r + px * w, cy + dy * r + py * w), (cx - dx * r + px * w, cy - dy * r + py * w),
               (cx - dx * r - px * w, cy - dy * r - py * w), (cx + dx * r - px * w, cy + dy * r - py * w)]
        d.polygon([(x * S, y * S) for x, y in pts], fill=(30, 70, 170, 255))
    lay = lay.resize((W, H), Image.LANCZOS)
    return lay


def rod_layer(cx, cy, h):
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    top, bot = cy - h / 2, cy + h / 2
    d.rounded_rectangle([(cx - 11) * S, top * S, (cx + 11) * S, bot * S], radius=10 * S, fill=(255, 255, 255, 255))
    pts = []
    for k in range(200):                 # the snake: a sine wound round the rod, rising
        u = k / 199
        y = bot - 30 - u * (h - 110)
        x = cx + 46 * math.sin(u * 2.6 * 2 * math.pi)
        pts.append((x * S, y * S))
    for k in range(len(pts) - 1):
        wd = (8 + 10 * math.sin(math.pi * min(k / 199 * 1.2, 1))) * S
        d.line([pts[k], pts[k + 1]], fill=(255, 255, 255, 255), width=int(wd))
    hx, hy = pts[-1]
    d.ellipse([hx - 22 * S, hy - 30 * S, hx + 26 * S, hy + 8 * S], fill=(255, 255, 255, 255))
    out = lay.resize((W, H), Image.LANCZOS)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(out.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: v // 2))
    res = Image.new("RGBA", (W, H))
    res.alpha_composite(sh, (4, 6))
    res.alpha_composite(out)
    return res


def skema_logo(times=None):
    base = navy_bg()
    star = star_layer(540, 800, 330, 105)
    rod = rod_layer(540, 800, 520)
    lab = pill("tongkat Asclepius", 40, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(28, 14))
    frames = []
    for i in range(N["logo"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        a = 1 - ramp(t, 0.6, 1.2)
        if a > 0.01:
            s = star.copy()
            s.putalpha(s.getchannel("A").point(lambda v: int(v * a)))
            im.alpha_composite(s)
        z = 1 + 0.05 * min(t / 4, 1)
        r = rod.resize((round(W * z), round(H * z)), Image.LANCZOS).crop(
            (round((W * z - W) / 2), round(800 * z - 800), round((W * z - W) / 2) + W, round(800 * z - 800) + H))
        im.alpha_composite(r)
        if t > 1.0:
            put1(im, lab, 540, 1120, scale=min(pop(t, 1.0, 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


# ---------- pausanias ----------
G_LON0, G_LON1, G_LAT1 = 20.6, 25.4, 39.4
GK = W / (G_LON1 - G_LON0)
G_Y0 = 650
EPIDAURUS, ATHENS = (23.15, 37.63), (23.73, 37.98)


def gpx(lon, lat):
    return ((lon - G_LON0) * GK, G_Y0 + (G_LAT1 - lat) * GK)


def scroll_card():
    pap = to_img(paper()).convert("RGBA")
    m = Image.new("L", (W, H))
    ImageDraw.Draw(m).rounded_rectangle([90, 690, 990, 1190], radius=14, fill=255)
    card = Image.new("RGBA", (W, H))
    card.paste(pap, (0, 0), m)
    d = ImageDraw.Draw(card)
    for y in (690, 1190):        # scroll rods
        d.rounded_rectangle([60, y - 18, 1020, y + 18], radius=18, fill=(110, 74, 40, 255), outline=(60, 40, 20, 255), width=3)
    f1 = ImageFont.truetype(XB, 54)
    f2 = ImageFont.truetype(RG, 38)
    d.text((540, 790), "Pausanias, ±160 M", font=f1, fill=(60, 40, 20), anchor="mm")
    for k, ln in enumerate(["“Di kota Epidaurus ada", "pelataran suci Asclepius...”"]):
        d.text((540, 880 + 62 * k), ln, font=f2, fill=(70, 56, 40), anchor="mm")
    d.text((540, 1090), "Description of Greece, buku 2", font=ImageFont.truetype(RG, 28), fill=(110, 90, 66), anchor="mm")
    return card


def qmark(sz):
    sp = Image.new("RGBA", (120 * S, 160 * S))
    ImageDraw.Draw(sp).text((60 * S, 80 * S), "?", font=ImageFont.truetype(XB, sz * S), fill=YELLOW + (255,), anchor="mm",
                            stroke_width=4 * S, stroke_fill=(20, 20, 20, 255))
    return sp


def skema_pausanias(times=None):
    bg = navy_bg()
    card = scroll_card()
    mp = sea_base()
    mp.alpha_composite(land_layer(gpx, (G_LON0, G_LON1, 35.5, G_LAT1)))
    sh = Image.new("RGBA", (W, H))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H], fill=(0, 0, 0, 40))
    mp.alpha_composite(sh)
    ex, ey = gpx(*EPIDAURUS)
    lab_e = pill("Epidaurus", 34, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220))
    lab_a = pill("Athena", 26, col=(210, 210, 215), bg=(10, 14, 24, 170))
    lab_g = pill("Yunani", 28, col=(210, 210, 215), bg=(10, 14, 24, 170))
    q = qmark(120)
    tm = T["map"]
    frames = []
    for i in range(N["pausanias"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        if t < tm:
            im = bg.copy()
            u = ease(t / 0.3)
            c = card.copy()
            c.putalpha(c.getchannel("A").point(lambda v: int(v * u)))
            im.alpha_composite(c, (0, round(20 * (1 - u))))
        else:
            im = mp.copy()
            ax, ay = gpx(*ATHENS)
            put1(im, lab_a, ax + 40, ay - 40, a=ramp(t, tm, tm + 0.3))
            put1(im, lab_g, 200, 1160, a=ramp(t, tm, tm + 0.3))
            pulse(im, ex, ey, (255, 220, 60), t, tm)
            put1(im, lab_e, ex - 40, ey + 60, scale=min(pop(t, tm + 0.1, 0.3), 1.1) if t > tm + 0.1 else 0)
            if t > tm + 0.5:
                put1(im, q, ex + 10, ey - 110 + 10 * math.sin((t - tm) * 5), scale=min(pop(t, tm + 0.5, 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


# ---------- denah ----------
GREEK = "ΑΣΚΛΗΠΙ"


def sherd_sprite():
    sp = Image.new("RGBA", (640 * S, 420 * S))
    d = ImageDraw.Draw(sp)
    poly = [(40, 120), (180, 30), (420, 20), (600, 110), (560, 300), (380, 400), (150, 380), (60, 260)]
    d.polygon([(x * S, y * S) for x, y in poly], fill=(176, 92, 52, 255), outline=(90, 46, 24, 255))
    a = np.asarray(sp, np.float32)
    n = blur(np.random.default_rng(56).standard_normal(a.shape[:2]).astype(np.float32), 2.0 * S)
    a[..., :3] *= (1 + 0.08 * np.clip(n, -3, 3))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def skema_denah(times=None):
    base = navy_bg()
    plan = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(plan)
    col = (190, 210, 240, 255)
    # Small Theatre: a half circle of seats, left
    cx, cy = 300, 960
    for r in range(70, 200, 22):
        d.arc([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], 180, 360, fill=col, width=3 * S)
    d.line([((cx - 200) * S, cy * S), ((cx + 200) * S, cy * S)], fill=col, width=4 * S)
    # the sanctuary box, right
    d.rectangle([640 * S, 740 * S, 960 * S, 1060 * S], outline=YELLOW + (255,), width=6 * S)
    d.rectangle([700 * S, 800 * S, 790 * S, 880 * S], outline=YELLOW + (200,), width=3 * S)       # fountain
    d.rectangle([820 * S, 900 * S, 930 * S, 1030 * S], outline=YELLOW + (200,), width=3 * S)      # reservoir
    plan = plan.resize((W, H), Image.LANCZOS)
    lab_t = pill("Teater Kecil", 28, col=(210, 210, 215), bg=(10, 14, 24, 190))
    lab_s = pill("tempat suci Asclepius", 30, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220))
    lab_d = pill("±20 m", 40, col=(255, 255, 255), bg=(150, 30, 30, 230), pad=(24, 12))
    sherd = sherd_sprite()
    f = ImageFont.truetype(XB, 74 * S)
    ts = T["sherd"]
    frames = []
    for i in range(N["denah"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        a = ramp(t, 0.0, 0.3) * (1 - 0.75 * ramp(t, ts, ts + 0.3))
        p = plan.copy()
        p.putalpha(p.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(p)
        put1(im, lab_t, 300, 1060, a=a)
        put1(im, lab_s, 800, 700, a=a)
        u = ease((t - 0.35) / 0.4)
        if u > 0 and a > 0.3:
            dl = Image.new("RGBA", (W * S, H * S))
            dashed(ImageDraw.Draw(dl), [(500, 900), (500 + 140 * u, 900)], (255, 120, 100, 255), 5, dash=12, gap=8)
            im.alpha_composite(dl.resize((W, H), Image.LANCZOS))
            if u > 0.95:
                put1(im, lab_d, 570, 850, scale=min(pop(t, 0.75, 0.3), 1.1) if t > 0.75 else 0)
        if t > ts:
            sp = sherd.copy()
            dd = ImageDraw.Draw(sp)
            k = min(len(GREEK), int((t - ts - T["letters"]) / 0.1) + 1) if t > ts + T["letters"] else 0
            dd.text((320 * S, 215 * S), GREEK[:k], font=f, fill=(250, 230, 200, 255), anchor="mm", stroke_width=2 * S, stroke_fill=(70, 30, 10, 255))
            put1(im, sp, 540, 900, scale=min(pop(t, ts, 0.35), 1.08))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"logo": skema_logo, "pausanias": skema_pausanias, "denah": skema_denah}

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
