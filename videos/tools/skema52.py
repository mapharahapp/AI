"""Schematic animations for Titik Heran #52 (run in the episode work dir; needs ../geo/ne_50m_land.geojson from Natural Earth;
writes clips/skema_lidar.mp4, skema_glif.mp4, skema_peta.mp4 and skema_tawanan.mp4).
Pixabay has no image of Minanbé, its LiDAR scan, its glyphs or the Ocomtún captive, so all four are drawn ("skema").
lidar: jungle canopy seen from above; a scan line peels it off to a grey hillshade with a plaza and pyramids (made up, not
  the real plan); on "lima" (1,68 s) a yellow dashed trail runs in from the bottom edge, "±5 km jalur dibabat".
glif: two stone glyph blocks SAK and IL slide together on "Sakil" (0,87 s) and glow into SAKIL?; "sak = putih" pops on
  "putih" (2,39 s). The blocks are lettered, not real Maya glyphs.
peta: the Yucatán peninsula from Natural Earth (lon -92 to -87,5); Minanbé pulses, a dashed line runs north-west to Ocomtún on "Sakil"
  (0,72 s), "±40 km" pops on "kota" (1,75 s). Site positions are approximate ("posisi perkiraan").
tawanan: a plain white line drawing carved on stone: a figure lying face down, hands tied behind the back (no blood, no
  face detail), a glyph box "DARI SAKIL" under it; the rope lights up on "terikat" (1,48 s).
Event times are seconds from the start of each clip, read off `render.py 52 plan` (lidar starts at 6,83, glif at 12,17,
peta at 17,80, tawanan at 20,70). Text stays out of the watermark band (y 935-985), the title zone (y < 660) and the
captions (y >= 1210).
usage: python3 skema52.py [lidar|glif|peta|tawanan ...] [--sheet out.jpg t1,t2,...]
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, encode, dashed
from skema35 import sheet, blur
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema49 import path_upto

N = {"lidar": 92, "glif": 94, "peta": 92, "tawanan": 72}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
RNG = np.random.default_rng(52)


def noise(sig, seed):
    r = np.random.default_rng(seed).standard_normal((H // 4, W // 4)).astype(np.float32)
    a = blur(np.asarray(Image.fromarray(r).resize((W, H), Image.BICUBIC), np.float32), sig)
    return (a - a.mean()) / (a.std() + 1e-6)


# ---------- lidar ----------
def relief():
    h = 2.5 * noise(14, 1) + 0.6 * noise(4, 2)
    def box(x0, y0, x1, y1, z, steps=1):
        for k in range(steps):
            m = (min(x1 - x0, y1 - y0) / 2 - 10) * k / steps
            sel = (XX >= x0 + m) & (XX <= x1 - m) & (YY >= y0 + m) & (YY <= y1 - m)
            h[sel] = np.maximum(h[sel], z * (k + 1) / steps)
    box(230, 770, 850, 1150, 16)                 # the plaza platform
    box(420, 790, 660, 1010, 120, steps=6)       # the big pyramid
    box(270, 1020, 400, 1130, 60, steps=3)
    box(690, 1010, 820, 1130, 64, steps=3)
    box(260, 800, 380, 930, 40, steps=2)
    box(710, 810, 820, 920, 36, steps=2)
    h = blur(h, 2.5)
    gy, gx = np.gradient(h)
    shade = np.clip(0.6 + 0.06 * (-gx * 1.2 - gy * 0.9), 0, 1)
    g = 60 + 150 * shade
    return np.stack([g * 0.97, g * 0.98, g * 1.0], -1)


def canopy():
    n = noise(3, 3) * 0.6 + noise(9, 4) * 0.4
    crowns = np.clip(n, -2, 2)
    base = np.array([28, 70, 34], np.float32)
    hi = np.array([86, 150, 70], np.float32)
    u = ((crowns + 2) / 4)[..., None]
    return base * (1 - u) + hi * u


TRAIL = [(200, 1920), (260, 1600), (180, 1400), (240, 1250), (300, 1160), (330, 1140)]


def skema_lidar(times=None):
    rel, can = relief(), canopy()
    lab = pill("LiDAR · MINANBÉ", 34)
    lab5 = pill("±5 km jalur dibabat", 34, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200))
    t5 = 1.68
    frames = []
    for i in range(N["lidar"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        sy = -60 + (H + 120) * ease((t - 0.05) / 1.5)
        m = np.clip((sy - YY) / 60, 0, 1)[..., None]
        a = can * (1 - m) + rel * m
        a += np.exp(-((YY - sy) ** 2) / 14 ** 2)[..., None] * np.array([60, 230, 200], np.float32) * 0.8
        im = to_img(a).convert("RGBA")
        u = ease((t - t5 + 0.15) / 0.6)
        if u > 0.02:
            dl = Image.new("RGBA", (W * S, H * S))
            dashed(ImageDraw.Draw(dl), path_upto(TRAIL, u), YELLOW + (255,), 6, dash=22, gap=12)
            im.alpha_composite(dl.resize((W, H), Image.LANCZOS))
        put1(im, lab, 540, 700, a=ramp(t, 0.7, 1.0))
        if t > t5:
            put1(im, lab5, 640, 1180, scale=min(pop(t, t5, 0.35), 1.1))
        frames.append(im.convert("RGB"))
    return frames


# ---------- glif ----------
def stone(seed, tint=(118, 108, 92)):
    n = 0.6 * noise(2, seed) + 0.4 * noise(10, seed + 1)
    v = (YY / H)[..., None]
    a = np.array(tint, np.float32) * (0.85 + 0.12 * n[..., None]) * (1.05 - 0.45 * v)
    return a


def glyph_block(text, size=104):
    w = h = 300
    sp = Image.new("RGBA", ((w + 30) * S, (h + 30) * S))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([18 * S, 18 * S, (w + 18) * S, (h + 18) * S], radius=60 * S, fill=(40, 34, 26, 160))
    d.rounded_rectangle([10 * S, 10 * S, (w + 10) * S, (h + 10) * S], radius=60 * S, fill=(176, 162, 136, 255), outline=(232, 222, 196, 255), width=5 * S)
    d.rounded_rectangle([34 * S, 34 * S, (w - 14) * S, (h - 14) * S], radius=44 * S, outline=(120, 106, 84, 255), width=4 * S)
    f = ImageFont.truetype(XB, size * S)
    d.text(((w / 2 + 12) * S, (h / 2 + 14) * S), text, font=f, fill=(60, 48, 34, 255), anchor="mm")
    d.text(((w / 2 + 10) * S, (h / 2 + 10) * S), text, font=f, fill=(248, 240, 220, 255), anchor="mm")
    return sp


def skema_glif(times=None):
    base = to_img(stone(10)).convert("RGBA")
    a_s, a_i = glyph_block("SAK"), glyph_block("IL")
    word = pill("SAKIL?", 110, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(40, 22))
    lab = pill("sak = putih", 50, col=(20, 20, 20), bg=(250, 250, 245, 240), edge=(255, 255, 255, 220))
    t_s, t_p = 0.87, 2.39
    frames = []
    for i in range(N["glif"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        a = ramp(t, 0.0, 0.3)
        m = ease((t - t_s) / 0.35)
        off = 185 - 30 * m
        put1(im, a_s, 540 - off, 800, a=a * (1 - 0.6 * ramp(t, t_s + 0.3, t_s + 0.55)))
        put1(im, a_i, 540 + off, 800, a=a * (1 - 0.6 * ramp(t, t_s + 0.3, t_s + 0.55)))
        if t > t_s + 0.3:
            gl = Image.new("RGBA", (W, H))
            ImageDraw.Draw(gl).ellipse([180, 640, 900, 960], fill=YELLOW + (int(90 * ramp(t, t_s + 0.3, t_s + 0.6)),))
            im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(50)))
            put1(im, word, 540, 800, scale=min(pop(t, t_s + 0.3, 0.35), 1.08))
        if t > t_p:
            put1(im, lab, 540, 1110, scale=min(pop(t, t_p, 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


# ---------- peta ----------
LON0, LON1, LAT1 = -92.0, -87.5, 19.6
K = W / (LON1 - LON0)
Y0 = 680
MIN, OCO = (-89.62, 18.55), (-89.95, 18.75)  # Ocomtún lies 40 km north-west of Minanbé


def px(lon, lat):
    return ((lon - LON0) * K, Y0 + (LAT1 - lat) * K)


def land_layer():
    geo = json.load(open("../geo/ne_50m_land.geojson"))
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for f in geo["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for p in polys:
            ring = p[0]
            xs = [q[0] for q in ring]
            ys = [q[1] for q in ring]
            if max(xs) < LON0 - 3 or min(xs) > LON1 + 3 or max(ys) < 12 or min(ys) > 26:
                continue
            d.polygon([tuple(c * S for c in px(*q)) for q in ring], fill=(52, 108, 60, 255), outline=(150, 200, 150, 255))
    return lay.resize((W, H), Image.LANCZOS)


def skema_peta(times=None):
    v = (YY / H)[..., None]
    sea = np.array([16, 44, 86], np.float32) * (1 - v) + np.array([6, 18, 42], np.float32) * v
    base = to_img(sea).convert("RGBA")
    base.alpha_composite(land_layer())
    sh = Image.new("RGBA", (W, H))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H], fill=(0, 0, 0, 40))
    base.alpha_composite(sh)
    mx, my = px(*MIN)
    ox, oy = px(*OCO)
    lab_m = pill("Minanbé (Sakil?)", 32)
    lab_o = pill("Ocomtún", 32, col=(255, 255, 255), bg=(150, 30, 30, 220))
    lab_k = pill("±40 km", 40, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200))
    lab_c = pill("Campeche, Meksiko", 32)
    note = pill("posisi perkiraan", 24, col=(210, 210, 215), bg=(10, 14, 24, 170))
    t_s, t_k = 0.72, 1.75
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        d = ImageDraw.Draw(im)
        u = ease((t - t_s) / 0.6)
        if u > 0.02:
            dl = Image.new("RGBA", (W * S, H * S))
            dashed(ImageDraw.Draw(dl), path_upto([(mx, my), (ox, oy)], u), YELLOW + (255,), 5, dash=14, gap=9)
            im.alpha_composite(dl.resize((W, H), Image.LANCZOS))
        for (x, y, col, t0) in ((mx, my, (255, 220, 60), 0.0), (ox, oy, (255, 70, 50), t_s + 0.55)):
            a = ramp(t, t0, t0 + 0.2)
            if a <= 0:
                continue
            ph = (t - t0) % 0.9 / 0.9
            rl = Image.new("RGBA", (W, H))
            rd = ImageDraw.Draw(rl)
            r = 10 + 40 * ph
            rd.ellipse([x - r, y - r, x + r, y + r], outline=col + (int(220 * (1 - ph) * a),), width=4)
            rd.ellipse([x - 11, y - 11, x + 11, y + 11], fill=col + (int(255 * a),), outline=(255, 255, 255, int(255 * a)), width=3)
            im.alpha_composite(rl)
        put1(im, lab_m, mx + 120, my + 95, a=ramp(t, 0.15, 0.4))
        put1(im, lab_o, ox - 100, oy - 70, a=ramp(t, t_s + 0.55, t_s + 0.8))
        if t > t_k:
            put1(im, lab_k, mx + 150, oy - 20, scale=min(pop(t, t_k, 0.35), 1.1))
        put1(im, lab_c, 540, 1110, a=ramp(t, 0.2, 0.45))
        put1(im, note, 540, 1170, a=ramp(t, 0.2, 0.45))
        frames.append(im.convert("RGB"))
    return frames


# ---------- tawanan ----------
def figure_paths():
    """a figure lying face down, facing left, hands tied behind the back; 1x coordinates"""
    head = [(300 + 40 * math.cos(a), 850 + 40 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40)]
    back = [(340, 838), (420, 822), (520, 818), (620, 828), (700, 846)]
    belly = [(338, 878), (420, 892), (520, 896), (620, 892), (700, 884)]
    leg1 = [(700, 846), (800, 850), (900, 842)]
    leg2 = [(700, 884), (800, 888), (900, 880)]
    feet = [(900, 842), (918, 836), (930, 862), (900, 880)]
    arm1 = [(400, 830), (470, 790), (560, 794), (600, 810)]
    arm2 = [(420, 836), (490, 806), (570, 806), (602, 818)]
    return [scale_fig(p) for p in (head, back, belly, leg1, leg2, feet, arm1, arm2)]


def scale_fig(p):
    return [(540 + (x - 615) * 1.3, 830 + (y - 850) * 1.3) for x, y in p]


ROPE0 = [[(585 + 6 * math.cos(a), 812 + 22 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 30)],
        [(600 + 6 * math.cos(a), 812 + 22 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 30)],
        [(600, 812), (640, 830), (660, 852)]]
ROPE = [scale_fig(p) for p in ROPE0]


def skema_tawanan(times=None):
    base = to_img(stone(20, (140, 128, 108))).convert("RGBA")
    paths = figure_paths()
    box = Image.new("RGBA", (420 * S, 170 * S))
    bd = ImageDraw.Draw(box)
    bd.rounded_rectangle([0, 0, 420 * S - 1, 170 * S - 1], radius=36 * S, fill=(70, 60, 46, 200), outline=(250, 244, 226, 255), width=5 * S)
    bd.text((210 * S, 52 * S), "DARI", font=ImageFont.truetype(XB, 40 * S), fill=(250, 244, 226, 255), anchor="mm")
    bd.text((210 * S, 112 * S), "SAKIL", font=ImageFont.truetype(XB, 64 * S), fill=YELLOW + (255,), anchor="mm")
    t_t = 1.48
    frames = []
    for i in range(N["tawanan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        u = ease((t - 0.0) / 1.0)
        ln = Image.new("RGBA", (W * S, H * S))
        sd = Image.new("RGBA", (W * S, H * S))
        d, ds = ImageDraw.Draw(ln), ImageDraw.Draw(sd)
        for p in paths:
            q = path_upto(p, u)
            if len(q) > 1:
                ds.line([((x + 4) * S, (y + 5) * S) for x, y in q], fill=(40, 32, 24, 200), width=12 * S, joint="curve")
                d.line([(x * S, y * S) for x, y in q], fill=(248, 244, 232, 255), width=11 * S, joint="curve")
        im.alpha_composite(sd.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2)))
        im.alpha_composite(ln.resize((W, H), Image.LANCZOS))
        ra = ramp(t, 0.8, 1.0)
        hot = ramp(t, t_t, t_t + 0.25)
        if ra > 0:
            col = tuple(int(248 * (1 - hot) + c * hot) for c in YELLOW)
            if hot > 0:
                gl = Image.new("RGBA", (W, H))
                ImageDraw.Draw(gl).ellipse([480, 700, 680, 860], fill=YELLOW + (int(110 * hot),))
                im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(24)))
            rl = Image.new("RGBA", (W * S, H * S))
            rd = ImageDraw.Draw(rl)
            for p in ROPE:
                rd.line([(x * S, y * S) for x, y in p], fill=col + (int(255 * ra),), width=6 * S, joint="curve")
            im.alpha_composite(rl.resize((W, H), Image.LANCZOS))
        put1(im, box, 540, 1100, scale=min(pop(t, 0.34, 0.35), 1.08) if t > 0.34 else 0)
        frames.append(im.convert("RGB"))
    return frames


FUN = {"lidar": skema_lidar, "glif": skema_glif, "peta": skema_peta, "tawanan": skema_tawanan}

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
