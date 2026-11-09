"""Stills and schematic animations for Titik Heran #48 (run in the episode work dir after `dl.py i:11012 i:11604 i:11607 i:11613`;
writes img/mars48v.jpg, clips/skema_tgo.mp4, clips/retak48.mp4 and clips/skema_magma.mp4).
Pixabay has no image of Alba Mons, the Trace Gas Orbiter or the fresh fissures, so the orbit and the ground section are drawn
("skema"), and the cracks are drawn over a real Mars surface photo (Pathfinder, 11604) ("ilustrasi: permukaan Mars + skema").
usage: python3 skema48.py [prep|tgo|retak|magma ...] [--sheet out.jpg t1,t2,...]
prep: img/mars48v.jpg, the NASA Mars globe 11012 (~1000 px across) low on a starry black vertical canvas, under the hook titles.
tgo: Mars' limb low in the frame with an orange haze; sunlight from the left grazes the haze to the orbiter at the right edge
  (solar occultation, how the orbiter "sniffs" gas); from "hidrogen" yellow HCl dots rise from a fissure and flare where they
  cross the beam ("HCl" pill).
retak: the Pathfinder surface with glowing cracks drawn in at once and yellow gas wisps rising from them.
magma: a ground section: a white ice plug in a crack sublimates, gas escapes upward, and from "di" a dim magma pocket below
  glows with a "?" on "sana" (it is a guess, so the pocket stays dim and gets a question mark, never a label "magma").
Event times are seconds from the start of each clip, read off `render.py 48 plan`: tgo starts at 9,90 ("hidrogen" 1,28),
retak at 13,10, magma at 16,73 ("di" 1,12, "sana" 1,46). Text stays out of the watermark band (y 935-985) and the captions (y >= 1210).
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, encode
from skema35 import blur, sheet
from skema37 import noise, to_img, put1
from skema39 import cover, title_shade
from skema46 import pill, ease, wanted

N = {"tgo": 108, "retak": 54, "magma": 78}
OUT = {"tgo": "clips/skema_tgo.mp4", "retak": "clips/retak48.mp4", "magma": "clips/skema_magma.mp4"}
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def stars(seed=48, n=260):
    rng = np.random.default_rng(seed)
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for _ in range(n):
        x, y, r = rng.random() * W, rng.random() * H, rng.choice([0.6, 0.9, 1.3, 1.8], p=[0.5, 0.3, 0.15, 0.05])
        v = int(90 + 165 * rng.random() ** 2)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(v, v, min(255, v + 15)))
    return np.asarray(im, np.float32)


def globe(diam):
    """the 11012 globe as RGBA, its dark corners cut away by a circular mask"""
    im = Image.open("img/11012.jpg").convert("RGB")
    # the planet fills ~ (10..1270) of the 1280 frame
    im = im.crop((8, 8, 1272, 1272)).resize((diam, diam), Image.LANCZOS)
    m = Image.new("L", (diam * 2, diam * 2), 0)
    ImageDraw.Draw(m).ellipse([6, 6, diam * 2 - 6, diam * 2 - 6], fill=255)
    im.putalpha(m.resize((diam, diam), Image.LANCZOS))
    return im


# ---------- prep ----------
def prep():
    base = to_img(stars()).convert("RGBA")
    d = 1020
    g = globe(d)
    cx, cy = 540, 1270
    halo = Image.new("RGBA", (W, H))
    ImageDraw.Draw(halo).ellipse([cx - d / 2 - 14, cy - d / 2 - 14, cx + d / 2 + 14, cy + d / 2 + 14], fill=(255, 140, 90, 90))
    base.alpha_composite(halo.filter(ImageFilter.GaussianBlur(22)))
    base.alpha_composite(g, (cx - d // 2, cy - d // 2))
    base.convert("RGB").save("img/mars48v.jpg", quality=95)
    print("img/mars48v.jpg")


# ---------- tgo ----------
LIMB_R, LIMB_TOP = 1500, 1125
ORB = (968, 1072)
SUN = (36, 1068)
VENT = 520


def limb_y(x):
    cx, cy = 540, LIMB_TOP + LIMB_R
    return cy - math.sqrt(max(LIMB_R ** 2 - (x - cx) ** 2, 0))


def tgo_base():
    base = to_img(stars(7, 200)).convert("RGBA")
    d = 2 * LIMB_R
    g = globe(d)
    halo = Image.new("RGBA", (W, H))
    ImageDraw.Draw(halo).ellipse([540 - LIMB_R - 40, LIMB_TOP - 40, 540 + LIMB_R + 40, LIMB_TOP + d + 40], fill=(255, 150, 90, 150))
    base.alpha_composite(halo.filter(ImageFilter.GaussianBlur(26)))
    base.alpha_composite(g, (540 - LIMB_R, LIMB_TOP))
    # the fissure: a dark jagged line at the vent with a faint glow
    lay = Image.new("RGBA", (W, H))
    dr = ImageDraw.Draw(lay)
    pts = [(VENT - 70, limb_y(VENT - 70) + 26), (VENT - 30, limb_y(VENT - 30) + 18), (VENT + 5, limb_y(VENT) + 24),
           (VENT + 40, limb_y(VENT + 40) + 15), (VENT + 80, limb_y(VENT + 80) + 22)]
    dr.line(pts, fill=(255, 200, 60, 150), width=14, joint="curve")
    lay = lay.filter(ImageFilter.GaussianBlur(7))
    ImageDraw.Draw(lay).line(pts, fill=(40, 16, 8, 255), width=5, joint="curve")
    base.alpha_composite(lay)
    # the sun just behind the left limb
    s = Image.new("RGBA", (W, H))
    ImageDraw.Draw(s).ellipse([SUN[0] - 60, SUN[1] - 60, SUN[0] + 60, SUN[1] + 60], fill=(255, 245, 210, 255))
    base.alpha_composite(s.filter(ImageFilter.GaussianBlur(30)))
    ImageDraw.Draw(base).ellipse([SUN[0] - 18, SUN[1] - 18, SUN[0] + 18, SUN[1] + 18], fill=(255, 252, 235))
    return base


def orbiter(t):
    """a small gold box with two blue solar panels, 2x sprite"""
    sp = Image.new("RGBA", (260 * S, 120 * S))
    d = ImageDraw.Draw(sp)
    c = (130 * S, 60 * S)
    for sx in (-1, 1):
        x0 = c[0] + sx * 34 * S
        x1 = c[0] + sx * 122 * S
        d.rectangle([min(x0, x1), c[1] - 16 * S, max(x0, x1), c[1] + 16 * S], fill=(38, 70, 150, 255), outline=(150, 180, 230, 255), width=2 * S)
        for k in range(1, 4):
            xx = x0 + (x1 - x0) * k / 4
            d.line([(xx, c[1] - 16 * S), (xx, c[1] + 16 * S)], fill=(150, 180, 230, 200), width=S)
    d.rectangle([c[0] - 26 * S, c[1] - 30 * S, c[0] + 26 * S, c[1] + 30 * S], fill=(212, 170, 60, 255), outline=(255, 225, 140, 255), width=2 * S)
    d.ellipse([c[0] - 34 * S - 10 * S, c[1] - 10 * S, c[0] - 34 * S + 10 * S, c[1] + 10 * S], fill=(230, 230, 230, 255))  # the sensor, facing the sun
    return sp


def dots_tgo(n=40, seed=3):
    rng = np.random.default_rng(seed)
    return [(rng.random() * 1.9, VENT + rng.normal(0, 22), rng.normal(0, 18), 6 + rng.random() * 6) for _ in range(n)]


def skema_tgo(times=None):
    base = tgo_base()
    orb = orbiter(0)
    lab = pill("HCl", 40, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200))
    t_h = 1.28
    dots = dots_tgo()
    frames = []
    for i in range(N["tgo"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        # the sunbeam, wiping in from the sun during the first 0,6 s, pulsing faintly
        u = ease(t / 0.6)
        x1 = SUN[0] + (ORB[0] - 40 - SUN[0]) * u
        bm = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(bm)
        a = 0.85 + 0.15 * math.sin(2 * math.pi * t / 1.1)
        d.line([SUN, (x1, ORB[1])], fill=(255, 235, 170, int(150 * a)), width=26)
        im.alpha_composite(bm.filter(ImageFilter.GaussianBlur(10)))
        ImageDraw.Draw(im).line([SUN, (x1, ORB[1])], fill=(255, 250, 225, int(230 * a)), width=4)
        bob = 4 * math.sin(2 * math.pi * t / 2.4)
        put1(im, orb, ORB[0], ORB[1] + bob)
        # HCl dots rising from the fissure from "hidrogen"
        if t >= t_h:
            dl = Image.new("RGBA", (W, H))
            dd = ImageDraw.Draw(dl)
            hits = 0
            for t0, x, drift, r in dots:
                age = t - t_h - t0 * 0.9
                if age < 0:
                    continue
                y = limb_y(VENT) + 10 - 95 * age
                if y < 820:
                    continue
                xx = x + drift * age + 10 * math.sin(age * 3 + t0 * 7)
                near = math.exp(-((y - ORB[1]) / 22) ** 2)
                hits += near
                rr = r * (1 + 0.8 * near)
                al = int(255 * min(1, age * 4) * min(1, (y - 820) / 80))
                dd.ellipse([xx - rr, y - rr, xx + rr, y + rr], fill=(255, 225 + int(30 * near), int(200 * near), al))
            g = dl.filter(ImageFilter.GaussianBlur(5))
            im.alpha_composite(g)
            im.alpha_composite(dl)
            # the orbiter's sensor blinks when gas crosses the beam
            if hits > 0.2:
                fl = Image.new("RGBA", (W, H))
                ImageDraw.Draw(fl).ellipse([ORB[0] - 80, ORB[1] - 60, ORB[0] + 80, ORB[1] + 60], fill=(255, 230, 120, int(min(1, hits) * 110)))
                im.alpha_composite(fl.filter(ImageFilter.GaussianBlur(22)))
            put1(im, lab, VENT, 1150, a=ramp(t, t_h + 0.15, t_h + 0.35), scale=min(pop(t, t_h + 0.15, 0.35), 1.1) if t > t_h + 0.15 else 0)
        frames.append(im.convert("RGB"))
    return frames


# ---------- retak ----------
def jag(p0, p1, n, amp, rng):
    pts = []
    for k in range(n + 1):
        u = k / n
        x = p0[0] + (p1[0] - p0[0]) * u
        y = p0[1] + (p1[1] - p0[1]) * u
        if 0 < k < n:
            x += rng.normal(0, amp)
            y += rng.normal(0, amp * 0.5)
        pts.append((x, y))
    return pts


CRACKS = [((60, 1180), (1020, 1060)), ((320, 1120), (420, 1520)), ((700, 1085), (900, 1460)), ((150, 1640), (980, 1560))]


def skema_retak(times=None):
    a = cover("img/11604.jpg", 0.5)
    a = title_shade(a, 0.45, 820) * 0.82
    base = to_img(a).convert("RGBA")
    rng = np.random.default_rng(48)
    lines = [jag(p, q, 14, 14, rng) for p, q in CRACKS]
    vents = [l[k] for l in lines for k in (4, 9)]
    wisps = [(v, rng.random() * 1.2, rng.normal(0, 14)) for v in vents for _ in range(3)]
    frames = []
    for i in range(N["retak"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        u = ease(t / 0.45)
        lay = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(lay)
        for l in lines:
            m = max(2, round(len(l) * u))
            d.line(l[:m], fill=(255, 140, 30, 255), width=40, joint="curve")
        lay = lay.filter(ImageFilter.GaussianBlur(14))
        im.alpha_composite(lay)
        lay = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(lay)
        for l in lines:
            m = max(2, round(len(l) * u))
            d.line(l[:m], fill=(255, 190, 70, 255), width=12, joint="curve")
        lay = lay.filter(ImageFilter.GaussianBlur(4))
        d = ImageDraw.Draw(lay)
        for l in lines:
            m = max(2, round(len(l) * u))
            d.line(l[:m], fill=(40, 14, 6, 255), width=5, joint="curve")
            d.line(l[:m], fill=(255, 235, 170, 230), width=2, joint="curve")
        im.alpha_composite(lay)
        # gas wisps
        wl = Image.new("RGBA", (W, H))
        wd = ImageDraw.Draw(wl)
        for (vx, vy), t0, dr in wisps:
            age = (t - 0.3 - t0 * 0.6) % 1.4
            if t < 0.3 + t0 * 0.6:
                continue
            y = vy - 160 * age
            x = vx + dr * age * 3 + 12 * math.sin(age * 4)
            r = 16 + 30 * age
            al = int(150 * math.sin(math.pi * min(age / 1.4, 1)))
            wd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 230, 90, int(al * 0.75)))
        im.alpha_composite(wl.filter(ImageFilter.GaussianBlur(20)))
        frames.append(im.convert("RGB"))
    return frames


# ---------- magma ----------
SURF = 800
CRX = 540
POCKET = (540, 1095, 250, 80)


def magma_base():
    sky = np.zeros((H, W, 3), np.float32)
    v = np.clip(YY / SURF, 0, 1)[..., None]
    sky += np.array([10, 8, 14], np.float32) * (1 - v) + np.array([70, 38, 30], np.float32) * v
    nz = noise((H, W), [(120, 0.5), (30, 0.35), (8, 0.15)], 48)[..., None]
    depth = np.clip((YY - SURF) / (H - SURF), 0, 1)[..., None]
    rock = (np.array([150, 78, 46], np.float32) * (1 - depth) + np.array([50, 30, 28], np.float32) * depth) * (0.75 + 0.45 * nz)
    # bands (layers)
    band = (0.92 + 0.08 * np.sin((YY - SURF) / 34 + nz[..., 0] * 3))[..., None]
    rock *= band
    under = (YY > SURF + 6 * np.sin(XX / 90))[..., None]
    a = np.where(under, rock, sky)
    im = to_img(a).convert("RGBA")
    d = ImageDraw.Draw(im)
    # the surface edge and the crack down to the pocket
    d.line([(0, SURF), (W, SURF)], fill=(210, 130, 90, 255), width=3)
    rng = np.random.default_rng(5)
    crack = jag((CRX, SURF), (CRX + 10, POCKET[1] - POCKET[3] + 10), 10, 9, rng)
    poly_l = [(x - 14 + 10 * (1 - (y - SURF) / 300), y) for x, y in crack]
    poly_r = [(x + 14 - 10 * (y - SURF) / 300, y) for x, y in crack][::-1]
    d.polygon(poly_l + poly_r, fill=(20, 10, 8, 255))
    return im, crack


def skema_magma(times=None):
    base, crack = magma_base()
    q = pill("?", 70, col=(255, 230, 200), bg=(120, 30, 10, 0), edge=(0, 0, 0, 0), pad=(10, 4))
    lab_es = pill("es", 34)
    lab_gas = pill("gas HCl", 34, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200))
    t_di, t_sana = 1.12, 1.46
    rng = np.random.default_rng(9)
    puffs = [(rng.random() * 1.6, rng.normal(0, 16), 7 + rng.random() * 6) for _ in range(30)]
    frames = []
    for i in range(N["magma"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        # the ice plug sublimates from 0,15 to 0,9 s
        k = 1 - ease((t - 0.15) / 0.75)
        if k > 0.02:
            pl = Image.new("RGBA", (W, H))
            h = 70 * k
            ImageDraw.Draw(pl).rounded_rectangle([CRX - 26, SURF + 8, CRX + 26, SURF + 8 + h], radius=10, fill=(225, 240, 255, int(255 * min(1, k * 1.5))))
            im.alpha_composite(pl)
            put1(im, lab_es, CRX - 110, SURF + 45, a=min(1, k * 1.5))
        # gas escaping from the crack
        if t > 0.35:
            gl = Image.new("RGBA", (W, H))
            gd = ImageDraw.Draw(gl)
            for t0, dr, r in puffs:
                age = t - 0.35 - t0
                if age < 0:
                    continue
                age %= 1.6
                y = SURF + 30 - 150 * age
                x = CRX + dr * age * 2.5 + 8 * math.sin(age * 5 + t0 * 9)
                al = int(240 * min(1, age * 5) * max(0, 1 - age / 1.6))
                gd.ellipse([x - r, y - r, x + r, y + r], fill=YELLOW + (al,))
            im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(3)))
            im.alpha_composite(gl)
            put1(im, lab_gas, CRX + 190, SURF - 60, a=ramp(t, 0.5, 0.7))
        # the magma pocket: dim and blurred, it brightens from "di", "?" pops on "sana"
        g = ramp(t, t_di, t_di + 0.35)
        pulse = 0.85 + 0.15 * math.sin(2 * math.pi * max(0.0, t - t_di) / 0.9)
        cx, cy, rx, ry = POCKET
        ml = Image.new("RGBA", (W, H))
        ImageDraw.Draw(ml).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(255, 70, 20, int((70 + 150 * g) * pulse)))
        im.alpha_composite(ml.filter(ImageFilter.GaussianBlur(30)))
        if g > 0:
            ml2 = Image.new("RGBA", (W, H))
            ImageDraw.Draw(ml2).ellipse([cx - rx * 0.6, cy - ry * 0.5, cx + rx * 0.6, cy + ry * 0.5], fill=(255, 170, 60, int(140 * g * pulse)))
            im.alpha_composite(ml2.filter(ImageFilter.GaussianBlur(24)))
        if t > t_sana:
            put1(im, q, cx, cy, scale=min(pop(t, t_sana, 0.35), 1.1))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"tgo": skema_tgo, "retak": skema_retak, "magma": skema_magma}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    os.makedirs("clips", exist_ok=True)
    for name in args or ["prep"] + list(N):
        if name == "prep":
            prep()
            continue
        fr = FUN[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
