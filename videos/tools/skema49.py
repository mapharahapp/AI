"""Schematic animations for Titik Heran #49 (run in the episode work dir; needs ../geo/ne_50m_land.geojson from Natural Earth;
writes clips/skema_garis.mp4 and clips/skema_rute.mp4).
Pixabay has no map of the Wallace Line and no image of the 1858 letter, so both are drawn ("skema").
garis: Indonesia from Natural Earth land (lon 110-132, from lat 6,5), the Wallace Line (Bali-Lombok, Makassar Strait, east of
  Borneo; schematic course) draws in as a yellow dashed line, "Garis Wallace" pops on "Garis" (1,13 s), Ternate pulses from 0,3 s.
rute: an envelope flies from Ternate (bottom right) to London (top), two papers marked WALLACE and DARWIN slide together there
  (on "London", 2,04 s), and on "tanpa" (2,79 s) two empty dashed seats for the authors fade in on either side.
Event times are seconds from the start of each clip, read off `render.py 49 plan` (garis starts at 4,73, rute at 13,67).
Text stays out of the watermark band (y 935-985), the title zone (y < 660) and the captions (y >= 1210).
usage: python3 skema49.py [garis|rute ...] [--sheet out.jpg t1,t2,...]
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, encode, dashed
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted

N = {"garis": 70, "rute": 128}
OUT = {"garis": "clips/skema_garis.mp4", "rute": "clips/skema_rute.mp4"}
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

LON0, LON1, LAT1 = 110.0, 132.0, 6.5
K = W / (LON1 - LON0)          # px per degree
Y0 = 690                       # map top (lat 6,5)


def px(lon, lat):
    return ((lon - LON0) * K, Y0 + (LAT1 - lat) * K)


def sea():
    v = (YY / H)[..., None]
    a = np.array([16, 44, 86], np.float32) * (1 - v) + np.array([6, 18, 42], np.float32) * v
    a += np.exp(-((XX - 600) ** 2 + (YY - 950) ** 2) / 560 ** 2)[..., None] * np.array([14, 34, 60], np.float32)
    return a


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
            if max(xs) < LON0 - 2 or min(xs) > LON1 + 2 or max(ys) < -14 or min(ys) > 12:
                continue
            pts = [tuple(c * S for c in px(*q)) for q in ring]
            d.polygon(pts, fill=(58, 104, 72, 255), outline=(150, 200, 150, 255))
    return lay.resize((W, H), Image.LANCZOS)


WALLACE = [(115.75, -10.2), (115.8, -8.5), (116.7, -6.8), (117.6, -4.6), (118.4, -2.2), (119.0, 0.4), (119.6, 2.6), (120.4, 4.6), (121.2, 6.5)]
TERNATE = (127.38, 0.79)


def path_upto(pts, u):
    seg = [math.dist(pts[k], pts[k + 1]) for k in range(len(pts) - 1)]
    L, out, acc = sum(seg) * u, [pts[0]], 0.0
    for k, s in enumerate(seg):
        if acc + s >= L:
            f = (L - acc) / s if s else 0
            out.append((pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f))
            return out
        acc += s
        out.append(pts[k + 1])
    return out


def skema_garis(times=None):
    base = to_img(sea()).convert("RGBA")
    base.alpha_composite(land_layer())
    line = [px(*p) for p in WALLACE]
    lab = pill("Garis Wallace", 36, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200))
    lab_t = pill("TERNATE", 34)
    tx, ty = px(*TERNATE)
    t_g = 1.13
    frames = []
    for i in range(N["garis"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        pts = path_upto(line, ease((t - 0.1) / 1.1))
        if len(pts) > 1:
            gl = Image.new("RGBA", (W * S, H * S))
            sp = [(x * S, y * S) for x, y in pts]
            ImageDraw.Draw(gl).line(sp, fill=YELLOW + (120,), width=18 * S, joint="curve")
            im.alpha_composite(gl.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(8)))
            dl = Image.new("RGBA", (W * S, H * S))
            dashed(ImageDraw.Draw(dl), pts, YELLOW + (255,), 7, dash=26, gap=14)
            im.alpha_composite(dl.resize((W, H), Image.LANCZOS))
        # Ternate pulses
        a = ramp(t, 0.3, 0.5)
        if a > 0:
            ph = ((t - 0.3) % 1.0)
            rl = Image.new("RGBA", (W, H))
            rd = ImageDraw.Draw(rl)
            r = 14 + 50 * ph
            rd.ellipse([tx - r, ty - r, tx + r, ty + r], outline=(255, 90, 60, int(220 * (1 - ph) * a)), width=5)
            rd.ellipse([tx - 13, ty - 13, tx + 13, ty + 13], fill=(255, 80, 50, int(255 * a)), outline=(255, 255, 255, int(255 * a)), width=3)
            im.alpha_composite(rl)
            put1(im, lab_t, tx, ty - 58, a=a)
        if t > t_g:
            put1(im, lab, 185, 1150, scale=min(pop(t, t_g, 0.35), 1.1))
        frames.append(im.convert("RGB"))
    return frames


# ---------- rute ----------
TER = (880, 1115)
LON = (540, 790)


def paper(name, w=170, h=210):
    sp = Image.new("RGBA", ((w + 20) * S, (h + 20) * S))
    d = ImageDraw.Draw(sp)
    d.rectangle([10 * S, 10 * S, (10 + w) * S, (10 + h) * S], fill=(242, 232, 205, 255), outline=(120, 100, 70, 255), width=2 * S)
    f = ImageFont.truetype(XB, 24 * S)
    d.text(((10 + w / 2) * S, 36 * S), name, font=f, fill=(60, 40, 20, 255), anchor="mm")
    rng = np.random.default_rng(len(name))
    for k in range(7):
        y = (64 + k * 21) * S
        x1 = (10 + w - 20 - rng.random() * 40) * S
        d.line([(30 * S, y), (x1, y)], fill=(90, 80, 70, 200), width=3 * S)
    return sp


def envelope():
    w, h = 120, 80
    sp = Image.new("RGBA", ((w + 20) * S, (h + 20) * S))
    d = ImageDraw.Draw(sp)
    box = [10 * S, 10 * S, (10 + w) * S, (10 + h) * S]
    d.rectangle(box, fill=(240, 228, 196, 255), outline=(110, 90, 60, 255), width=2 * S)
    d.line([(10 * S, 10 * S), ((10 + w / 2) * S, (10 + h * 0.6) * S), ((10 + w) * S, 10 * S)], fill=(110, 90, 60, 255), width=2 * S)
    d.ellipse([(10 + w / 2 - 11) * S, (10 + h * 0.6 - 11) * S, (10 + w / 2 + 11) * S, (10 + h * 0.6 + 11) * S], fill=(190, 40, 40, 255))
    return sp


def seat():
    """an empty place: a dashed outline of a person"""
    sp = Image.new("RGBA", (180 * S, 230 * S))
    d = ImageDraw.Draw(sp)
    c = (180, 180, 190, 230)
    head = [(90 + 34 * math.cos(a) , 60 + 34 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40)]
    body = [(20 + 140 * (k / 30), 220 - 110 * math.sin(math.pi * k / 30) ** 0.6) for k in range(31)]
    for pts in (head, body):
        dashed(d, pts, c, 5, dash=14, gap=10)
    return sp


def skema_rute(times=None):
    bg = sea()
    base = to_img(bg).convert("RGBA")
    g = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(g)
    for x in range(0, W + 1, 135):
        gd.line([(x, 0), (x, H)], fill=(255, 255, 255, 14), width=2)
    for y in range(-45, H + 1, 135):
        gd.line([(0, y), (W, y)], fill=(255, 255, 255, 14), width=2)
    base.alpha_composite(g)
    env = envelope()
    pw, pd = paper("WALLACE"), paper("DARWIN")
    st = seat()
    lab_t, lab_l = pill("Ternate", 34), pill("London", 34, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200))
    ctrl = (960, 760)
    arc = [((1 - u) ** 2 * TER[0] + 2 * (1 - u) * u * ctrl[0] + u * u * LON[0],
            (1 - u) ** 2 * TER[1] + 2 * (1 - u) * u * ctrl[1] + u * u * LON[1]) for u in np.linspace(0, 1, 60)]
    t_l, t_t = 2.04, 2.79
    frames = []
    for i in range(N["rute"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        u = ease((t - 0.15) / 1.3)
        dl = Image.new("RGBA", (W * S, H * S))
        dashed(ImageDraw.Draw(dl), arc, (255, 255, 255, 110), 4, dash=18, gap=14)
        if u > 0.02:
            dashed(ImageDraw.Draw(dl), path_upto(arc, u), YELLOW + (255,), 5, dash=18, gap=14)
        im.alpha_composite(dl.resize((W, H), Image.LANCZOS))
        # dots at both ends
        d = ImageDraw.Draw(im)
        for (x, y) in (TER, LON):
            d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(255, 80, 50), outline=WHITE, width=3)
        put1(im, lab_t, TER[0], TER[1] + 44)
        # the envelope flies until 1,45 s, then fades as the papers come
        if t < 1.7:
            k = min(int(u * (len(arc) - 1)), len(arc) - 1)
            ex, ey = arc[k]
            put1(im, env, ex, ey, a=1 - ramp(t, 1.45, 1.7), scale=0.9 + 0.1 * math.sin(t * 6))
        # papers slide together on "London"
        a = ramp(t, 1.45, 1.7)
        if a > 0:
            m = ease((t - 1.6) / (t_l + 0.25 - 1.6))
            off = 260 - 112 * m
            put1(im, pw, LON[0] - off, LON[1] + 10, a=a, scale=1.2)
            put1(im, pd, LON[0] + off, LON[1] + 10, a=a, scale=1.2)
            if t > t_l:
                gl = Image.new("RGBA", (W, H))
                ImageDraw.Draw(gl).ellipse([LON[0] - 260, LON[1] - 150, LON[0] + 260, LON[1] + 170], fill=YELLOW + (int(70 * ramp(t, t_l, t_l + 0.3)),))
                im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40)))
                put1(im, pw, LON[0] - off, LON[1] + 10, scale=1.2)
                put1(im, pd, LON[0] + off, LON[1] + 10, scale=1.2)
        put1(im, lab_l, LON[0], 1050, a=ramp(t, 1.3, 1.5))
        # the authors' empty places
        if t > t_t:
            sa = ramp(t, t_t, t_t + 0.35)
            put1(im, st, 95, 830, a=sa)
            put1(im, st, 985, 830, a=sa)
        frames.append(im.convert("RGB"))
    return frames


FUN = {"garis": skema_garis, "rute": skema_rute}

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
