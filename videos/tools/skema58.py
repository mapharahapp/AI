"""Schematic animations for Titik Heran #58 (run in the episode work dir; needs ../geo/ne_50m_land.geojson from Natural
Earth; writes clips/skema_cincin.mp4, skema_magnet.mp4, skema_batu.mp4 and clips/trex58.mp4).
cincin: Yucatán from Natural Earth; blue cenote dots pop one by one along the southern half circle round Chicxulub
  (radius ~90 km), "Chicxulub" pin.
magnet: the same map dimmed; a small survey plane crosses leaving dashed track lines (1978), concentric anomaly rings
  grow from the centre, then the full dashed 180 km ring and a diameter line with a "180 km" pill.
batu: a drill core (grey, cracked) on a card "sampel sumur bor Pemex", then a red stamp "BUKTI HANTAMAN · 1990".
trex: Pixabay video 140144 (green screen T. rex) keyed over a dark orange sky (ffmpeg chromakey), labelled ilustrasi.
Event times are seconds from the start of each clip, read off `render.py 58 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 660) and the captions (y >= 1210).
usage: python3 skema58.py [cincin|magnet|batu|trex ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed
from skema35 import sheet, blur
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema53 import land_layer, sea_base, pulse, paper, XB, RG

N = {"cincin": 40, "magnet": 110, "batu": 115}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
T = {"ring": 0.8, "full": 1.7, "stamp": 2.78}   # set from `render.py 58 plan`

LON0, LON1, LAT1 = -91.6, -87.4, 23.0
K = W / (LON1 - LON0)
Y0 = 340
CHX = (-89.5, 21.3)
R_DEG = 0.81   # ~90 km in latitude degrees


def px(lon, lat):
    return ((lon - LON0) * K, Y0 + (LAT1 - lat) * K)


def yucatan(dim=0):
    base = sea_base()
    base.alpha_composite(land_layer(px, (LON0, LON1, 17.0, LAT1)))
    sh = Image.new("RGBA", (W, H))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H], fill=(0, 0, 0, 50 + dim))
    base.alpha_composite(sh)
    return base


def ring_xy(a, r=R_DEG):
    lon = CHX[0] + r * math.cos(a) / math.cos(math.radians(CHX[1]))
    lat = CHX[1] + r * math.sin(a)
    return px(lon, lat)


def dot(r=16):
    sp = Image.new("RGBA", (4 * r * S, 4 * r * S))
    d = ImageDraw.Draw(sp)
    c = 2 * r * S
    d.ellipse([c - r * S, c - r * S, c + r * S, c + r * S], fill=(60, 200, 255, 255), outline=(255, 255, 255, 255), width=3 * S)
    return sp


def skema_cincin(times=None):
    base = yucatan()
    cx, cy = px(*CHX)
    ds = dot()
    lab = pill("Chicxulub", 30, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220))
    lab2 = pill("Semenanjung Yucatán", 26, col=(210, 210, 215), bg=(10, 14, 24, 170))
    angs = np.linspace(math.radians(195), math.radians(345), 22)   # the southern, on-land half
    frames = []
    for i in range(N["cincin"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        for k, a in enumerate(angs):
            t0 = 0.05 + k * 0.035
            if t > t0:
                x, y = ring_xy(a)
                put1(im, ds, x, y, scale=min(pop(t, t0, 0.25), 1.1))
        pulse(im, cx, cy, (255, 220, 60), t, 0.0)
        put1(im, lab, cx, cy - 55, a=ramp(t, 0.0, 0.2))
        put1(im, lab2, 540, 1170, a=ramp(t, 0.0, 0.2))
        frames.append(im.convert("RGB"))
    return frames


def plane(sz=46):
    sp = Image.new("RGBA", (sz * 2 * S, sz * 2 * S))
    d = ImageDraw.Draw(sp)
    c = sz * S
    pts = [(c + sz * S * 0.9, c), (c - sz * S * 0.6, c - sz * S * 0.18), (c - sz * S * 0.5, c), (c - sz * S * 0.6, c + sz * S * 0.18)]
    d.polygon(pts, fill=(255, 255, 255, 255))
    d.polygon([(c + 6 * S, c), (c - 10 * S, c - sz * S * 0.75), (c - 22 * S, c - sz * S * 0.75), (c - 14 * S, c)], fill=(255, 255, 255, 255))
    d.polygon([(c + 6 * S, c), (c - 10 * S, c + sz * S * 0.75), (c - 22 * S, c + sz * S * 0.75), (c - 14 * S, c)], fill=(255, 255, 255, 255))
    return sp


def skema_magnet(times=None):
    base = yucatan(dim=60)
    cx, cy = px(*CHX)
    pl = plane()
    lab_y = pill("survei magnet · 1978", 30, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220))
    lab_k = pill("180 km", 54, col=(255, 255, 255), bg=(160, 30, 30, 235), edge=(255, 255, 255, 220), pad=(28, 14))
    rr = abs(ring_xy(0)[0] - cx)
    tracks = [cy - 240, cy - 80, cy + 80, cy + 240]
    frames = []
    for i in range(N["magnet"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        dl = Image.new("RGBA", (W * S, H * S))
        dd = ImageDraw.Draw(dl)
        for k, ty in enumerate(tracks):          # survey tracks, drawn by the plane one after another
            u = np.clip((t - k * 0.18) / 0.5, 0, 1)
            if u > 0.01:
                x0, x1 = (60, 60 + 960 * u) if k % 2 == 0 else (1020, 1020 - 960 * u)
                dashed(dd, [(x0, ty), (x1, ty)], (255, 255, 255, 120), 2, dash=10, gap=8)
        rl = Image.new("RGBA", (W * S, H * S))
        rd = ImageDraw.Draw(rl)
        for k, f in enumerate((0.35, 0.55, 0.75, 1.0)):   # anomaly rings
            a = ramp(t, T["ring"] + k * 0.15, T["ring"] + k * 0.15 + 0.3)
            if a > 0:
                r = rr * f * (0.85 + 0.15 * a)
                col = ((255, 150, 60) if k % 2 else (120, 200, 255)) + (int(200 * a),)
                rd.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], outline=col, width=5 * S)
        im.alpha_composite(dl.resize((W, H), Image.LANCZOS))
        im.alpha_composite(rl.resize((W, H), Image.LANCZOS))
        k = min(int(t / 0.18), 3)
        u = np.clip((t - k * 0.18) / 0.5, 0, 1)
        if t < 1.2:
            x = 60 + 960 * u if k % 2 == 0 else 1020 - 960 * u
            s = pl if k % 2 == 0 else pl.transpose(Image.FLIP_LEFT_RIGHT)
            put1(im, s, x, tracks[k], a=1 - ramp(t, 1.0, 1.2))
        put1(im, lab_y, 540, 690, a=ramp(t, 0.0, 0.25) * (1 - ramp(t, T["full"] - 0.2, T["full"])))
        if t > T["full"]:
            u = ease((t - T["full"]) / 0.4)
            ol = Image.new("RGBA", (W * S, H * S))
            od = ImageDraw.Draw(ol)
            pts = [ring_xy(a) for a in np.linspace(0, 2 * math.pi * u, max(3, int(90 * u)))]
            dashed(od, pts, YELLOW + (255,), 5, dash=14, gap=9)
            if u > 0.95:
                dashed(od, [(cx - rr, cy), (cx + rr, cy)], (255, 120, 100, 255), 4, dash=12, gap=8)
            im.alpha_composite(ol.resize((W, H), Image.LANCZOS))
            if u > 0.95:
                put1(im, lab_k, cx, cy + rr + 70, scale=min(pop(t, T["full"] + 0.4, 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


def core_sprite():
    w, h = 170, 430
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    shade = 0.55 + 0.45 * np.sin(np.pi * xx / w)
    n = blur(np.random.default_rng(58).standard_normal((h, w)).astype(np.float32), 2.5)
    g = (120 + 30 * np.clip(n, -3, 3)) * shade
    rgb = np.stack([g * 1.02, g, g * 0.95], -1)
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(5)
    for y in (140, 300):                       # breaks in the core
        d.line([(0, y), (w * 0.4, y + 8), (w, y - 6)], fill=(40, 38, 36, 255), width=4)
    for _ in range(26):                        # breccia fragments
        x, y, r = rng.uniform(15, w - 15), rng.uniform(15, h - 15), rng.uniform(5, 13)
        c = int(rng.uniform(150, 215))
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(c, c - 8, c - 18, 255))
    m = Image.new("L", (w, h))
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=18, fill=255)
    im.putalpha(m)
    return im


def skema_batu(times=None):
    bg = to_img(np.array([24, 22, 26], np.float32) * np.ones((H, W, 1), np.float32)).convert("RGBA")
    pap = to_img(paper()).convert("RGBA")
    m = Image.new("L", (W, H))
    ImageDraw.Draw(m).rounded_rectangle([110, 660, 970, 1190], radius=14, fill=255)
    card = Image.new("RGBA", (W, H))
    card.paste(pap, (0, 0), m)
    d = ImageDraw.Draw(card)
    d.text((540, 710), "sampel batu dari sumur bor Pemex", font=ImageFont.truetype(XB, 34), fill=(50, 40, 30), anchor="mm")
    d.text((540, 1160), "skema, bukan foto sampel asli", font=ImageFont.truetype(RG, 22), fill=(110, 90, 66), anchor="mm")
    core = core_sprite().rotate(90, expand=True)
    core = core.resize((round(core.width * 1.65), round(core.height * 1.65)), Image.LANCZOS)
    stamp = Image.new("RGBA", (760 * S, 200 * S))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle([8 * S, 8 * S, 752 * S, 192 * S], radius=16 * S, outline=(190, 30, 30, 255), width=10 * S)
    sd.text((380 * S, 78 * S), "BUKTI HANTAMAN", font=ImageFont.truetype(XB, 74 * S), fill=(190, 30, 30, 255), anchor="mm")
    sd.text((380 * S, 152 * S), "1990", font=ImageFont.truetype(XB, 44 * S), fill=(190, 30, 30, 255), anchor="mm")
    stamp = stamp.rotate(-8, expand=True, resample=Image.BICUBIC)
    frames = []
    for i in range(N["batu"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        u = ease(t / 0.35)
        c = card.copy()
        c.putalpha(c.getchannel("A").point(lambda v: int(v * u)))
        im.alpha_composite(c, (0, round(30 * (1 - u))))
        cu = ease((t - 0.3) / 0.6)
        if cu > 0:
            im.alpha_composite(core, (round(540 - core.width / 2 - 600 * (1 - cu)), 880 - core.height // 2))
        if t > T["stamp"]:
            s = 1.0 + 0.5 * (1 - ease((t - T["stamp"]) / 0.18))
            put1(im, stamp, 560, 1075, scale=s, a=ramp(t, T["stamp"], T["stamp"] + 0.08))
        frames.append(im.convert("RGB"))
    return frames


def make_trex():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x2a1408:s=1920x1080:d=5",
                    "-i", "clips/140144.mp4", "-filter_complex",
                    "[0]geq=r='42+90*(1-Y/H)':g='20+40*(1-Y/H)':b='8+10*(1-Y/H)'[bg];"
                    "[1]scale=1920:1080,chromakey=0x00d000:0.18:0.08,despill=green[fg];[bg][fg]overlay=shortest=1,format=yuv420p",
                    "-c:v", "libx264", "-crf", "18", "-an", "clips/trex58.mp4"], check=True)


FUN = {"cincin": skema_cincin, "magnet": skema_magnet, "batu": skema_batu}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    os.makedirs("clips", exist_ok=True)
    for name in args or list(N) + ["trex"]:
        if name == "trex":
            make_trex()
            continue
        fr = FUN[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
