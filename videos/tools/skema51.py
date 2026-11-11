"""Schematic animations for Titik Heran #51 (run in the episode work dir; needs ../geo/ne_50m_land.geojson from Natural Earth;
writes clips/skema_peta.mp4, clips/skema_cangkir.mp4 and clips/skema_label.mp4).
Pixabay has no image of the Belitung wreck, its gold cup or the museum card, so all three are drawn ("skema").
peta: Sumatra-Borneo-Java from Natural Earth land (lon 99-117, lat 3 at y 680); a yellow dashed route comes down from China
  past Vietnam to the Gelasa Strait, where Belitung pulses red; "±830 M" pops on "seribu" (0,75 s); a faint grey route goes on
  through the Sunda Strait, "menuju Teluk Persia" (schematic course: where the ship meant to sail is not recorded).
cangkir: an eight-sided gold cup with a ring handle, outlined in gold and turning slowly (not drawn to scale).
label: a neutral museum name card over the blurred Singapore photo: BELITUNG is struck out on "bukan" (1,37 s) and
  TANG SHIPWRECK comes in on "Belitung" (1,93 s).
Event times are seconds from the start of each clip, read off `render.py 51 plan` (peta starts at 7,00, cangkir at 14,73,
label at 22,37). Text stays out of the watermark band (y 935-985), the title zone (y < 660) and the captions (y >= 1210).
usage: python3 skema51.py [peta|cangkir|label ...] [--sheet out.jpg t1,t2,...]
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, encode, dashed
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema49 import path_upto

N = {"peta": 84, "cangkir": 72, "label": 92}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
RG = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
GOLD = (236, 190, 70)

# ---------- peta ----------
LON0, LON1, LAT1 = 99.0, 117.0, 3.0
K = W / (LON1 - LON0)
Y0 = 680


def px(lon, lat):
    return ((lon - LON0) * K, Y0 + (LAT1 - lat) * K)


def sea():
    v = (YY / H)[..., None]
    a = np.array([16, 44, 86], np.float32) * (1 - v) + np.array([6, 18, 42], np.float32) * v
    a += np.exp(-((XX - 540) ** 2 + (YY - 1030) ** 2) / 520 ** 2)[..., None] * np.array([14, 34, 60], np.float32)
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
            if max(xs) < LON0 - 3 or min(xs) > LON1 + 3 or max(ys) < -20 or min(ys) > 30:
                continue
            d.polygon([tuple(c * S for c in px(*q)) for q in ring], fill=(58, 104, 72, 255), outline=(150, 200, 150, 255))
    return lay.resize((W, H), Image.LANCZOS)


ROUTE = [(110.6, 16.0), (109.4, 12.0), (108.4, 8.0), (107.4, 4.0), (106.9, 1.0), (107.2, -1.6), (107.55, -2.55)]
ONWARD = [(107.55, -2.55), (106.6, -4.2), (105.8, -6.0), (104.0, -7.4), (98.0, -8.6)]
WRECK = (107.55, -2.55)


def glow_line(im, pts, col, w, blur):
    gl = Image.new("RGBA", (W * S, H * S))
    ImageDraw.Draw(gl).line([(x * S, y * S) for x, y in pts], fill=col, width=w * S, joint="curve")
    im.alpha_composite(gl.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(blur)))


def skema_peta(times=None):
    base = to_img(sea()).convert("RGBA")
    base.alpha_composite(land_layer())
    route, onward = [px(*p) for p in ROUTE], [px(*p) for p in ONWARD]
    wx, wy = px(*WRECK)
    lab_b = pill("BELITUNG", 36)
    lab_y = pill("±830 M", 40, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200))
    lab_c = pill("dari Cina", 32)
    lab_p = pill("menuju Teluk Persia", 30, col=(225, 225, 230), bg=(10, 14, 24, 190))
    t_y = 0.75
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        u = ease((t - 0.05) / 1.05)
        pts = path_upto(route, u)
        if len(pts) > 1:
            glow_line(im, pts, YELLOW + (110,), 16, 7)
            dl = Image.new("RGBA", (W * S, H * S))
            dashed(ImageDraw.Draw(dl), pts, YELLOW + (255,), 6, dash=24, gap=14)
            im.alpha_composite(dl.resize((W, H), Image.LANCZOS))
        v = ease((t - 1.25) / 0.9)
        if v > 0.02:
            dl = Image.new("RGBA", (W * S, H * S))
            dashed(ImageDraw.Draw(dl), path_upto(onward, v), (200, 200, 210, 150), 4, dash=16, gap=14)
            im.alpha_composite(dl.resize((W, H), Image.LANCZOS))
        put1(im, lab_c, 700, 700, a=ramp(t, 0.1, 0.35))
        a = ramp(t, 0.9, 1.1)
        if a > 0:  # the wreck pulses where the route stops
            ph = (t - 0.9) % 0.9 / 0.9
            rl = Image.new("RGBA", (W, H))
            rd = ImageDraw.Draw(rl)
            r = 14 + 52 * ph
            rd.ellipse([wx - r, wy - r, wx + r, wy + r], outline=(255, 90, 60, int(220 * (1 - ph) * a)), width=5)
            rd.ellipse([wx - 13, wy - 13, wx + 13, wy + 13], fill=(255, 80, 50, int(255 * a)), outline=(255, 255, 255, int(255 * a)), width=3)
            im.alpha_composite(rl)
        put1(im, lab_b, 660, 1095, a=ramp(t, 0.3, 0.55))
        if t > t_y:
            put1(im, lab_y, 880, 1030, scale=min(pop(t, t_y, 0.35), 1.1))
        put1(im, lab_p, 250, 1165, a=ramp(t, 1.5, 1.8))
        frames.append(im.convert("RGB"))
    return frames


# ---------- cangkir ----------
def cup_frame(t):
    """an eight-sided cup: top ring, bottom ring and a foot, turned by angle th; returns a 2x RGBA layer"""
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    th = 0.35 + 0.55 * t
    cx, tilt = 540, 0.28

    def ring(y, r):
        return [(cx + r * math.cos(th + k * math.pi / 4), y + r * tilt * math.sin(th + k * math.pi / 4),
                 math.sin(th + k * math.pi / 4)) for k in range(8)]
    top, bot = ring(760, 230), ring(1060, 165)
    foot_t, foot_b = ring(1085, 95), ring(1130, 120)
    c = lambda p: (p[0] * S, p[1] * S)
    # body faces, back first so the front ones cover them
    order = sorted(range(8), key=lambda k: top[k][2] + top[(k + 1) % 8][2])
    for k in order:
        j = (k + 1) % 8
        front = top[k][2] + top[j][2]
        shade = 0.55 + 0.45 * (front + 2) / 4
        nx = math.cos(th + (k + 0.5) * math.pi / 4)
        lit = 0.75 + 0.25 * nx
        fill = tuple(int(v * shade * lit) for v in GOLD) + (255,)
        d.polygon([c(top[k]), c(top[j]), c(bot[j]), c(bot[k])], fill=fill, outline=(255, 236, 170, 255), width=3 * S)
        if front > 0:  # a band of chased decoration on the front faces
            m0 = [(top[k][0] * 0.55 + bot[k][0] * 0.45) * S, (top[k][1] * 0.55 + bot[k][1] * 0.45) * S]
            m1 = [(top[j][0] * 0.55 + bot[j][0] * 0.45) * S, (top[j][1] * 0.55 + bot[j][1] * 0.45) * S]
            d.line([tuple(m0), tuple(m1)], fill=(255, 240, 190, 200), width=2 * S)
    d.polygon([c(p) for p in top], fill=(120, 84, 24, 255), outline=(255, 236, 170, 255), width=3 * S)
    d.polygon([c(p) for p in foot_b], fill=(150, 108, 34, 255), outline=(255, 236, 170, 255), width=3 * S)
    d.polygon([c(p) for p in foot_t], fill=(190, 140, 50, 255), outline=(255, 236, 170, 255), width=3 * S)
    # ring handle with a thumb plate, on the face at angle 0
    hx = math.cos(th) * 200
    hz = math.sin(th)
    if abs(hx) > 20:
        x0 = cx + hx + (35 if hx > 0 else -35)
        r = 46
        col = (255, 226, 140, 255 if hz > -0.2 else 150)
        d.ellipse([(x0 - r) * S, (880 - r) * S, (x0 + r) * S, (880 + r) * S], outline=col, width=12 * S)
        d.rectangle([(x0 - 52) * S, 820 * S, (x0 + 52) * S, 836 * S], fill=col)
    return lay.resize((W, H), Image.LANCZOS)


def skema_cangkir(times=None):
    v = (YY / H)[..., None]
    bg = np.array([34, 24, 12], np.float32) * (1 - v) + np.array([10, 7, 4], np.float32) * v
    bg += np.exp(-((XX - 540) ** 2 + (YY - 930) ** 2) / 420 ** 2)[..., None] * np.array([70, 48, 16], np.float32)
    base = to_img(bg).convert("RGBA")
    lab = pill("cangkir emas · bersegi 8", 32, col=(20, 20, 20), bg=YELLOW + (235,), edge=(255, 255, 255, 200))
    frames = []
    for i in range(N["cangkir"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        cup = cup_frame(t)
        a = ramp(t, 0.0, 0.25)
        glow = cup.filter(ImageFilter.GaussianBlur(30))
        glow.putalpha(glow.getchannel("A").point(lambda q: int(q * 0.6 * a)))
        im.alpha_composite(glow)
        if a < 1:
            cup.putalpha(cup.getchannel("A").point(lambda q: int(q * a)))
        im.alpha_composite(cup)
        # a glint runs across the rim
        gx = 300 + 480 * ((t * 0.7) % 1.0)
        gl = Image.new("RGBA", (W, H))
        ImageDraw.Draw(gl).ellipse([gx - 26, 735, gx + 26, 785], fill=(255, 255, 230, 150))
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(10)))
        put1(im, lab, 540, 1175, a=ramp(t, 0.35, 0.6))
        frames.append(im.convert("RGB"))
    return frames


# ---------- label ----------
def skema_label(times=None):
    ph = Image.open("img/430643.jpg").convert("RGB")
    s = max(W / ph.width, H / ph.height)
    ph = ph.resize((round(ph.width * s), round(ph.height * s)), Image.LANCZOS)
    ph = ph.crop(((ph.width - W) // 2, (ph.height - H) // 2, (ph.width - W) // 2 + W, (ph.height - H) // 2 + H))
    base = Image.blend(ph.filter(ImageFilter.GaussianBlur(18)), Image.new("RGB", (W, H), (8, 10, 16)), 0.55).convert("RGBA")
    card = Image.new("RGBA", (860 * S, 520 * S))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, 860 * S - 1, 520 * S - 1], radius=18 * S, fill=(244, 241, 234, 250), outline=(180, 170, 150, 255), width=3 * S)
    cd.text((430 * S, 52 * S), "ASIAN CIVILISATIONS MUSEUM", font=ImageFont.truetype(XB, 30 * S), fill=(90, 80, 70, 255), anchor="mm")
    cd.line([(60 * S, 92 * S), (800 * S, 92 * S)], fill=(190, 180, 160, 255), width=2 * S)
    cd.text((430 * S, 482 * S), "Singapura", font=ImageFont.truetype(RG, 30 * S), fill=(110, 100, 90, 255), anchor="mm")
    old = Image.new("RGBA", (860 * S, 160 * S))
    ImageDraw.Draw(old).text((430 * S, 80 * S), "BELITUNG", font=ImageFont.truetype(XB, 104 * S), fill=(40, 40, 46, 255), anchor="mm")
    new = Image.new("RGBA", (860 * S, 130 * S))
    ImageDraw.Draw(new).text((430 * S, 65 * S), "TANG SHIPWRECK", font=ImageFont.truetype(XB, 76 * S), fill=(150, 30, 30, 255), anchor="mm")
    CX, CY = 540, 935  # card centre; its middle (y 905-1010) holds no text
    t_x, t_n = 1.37, 1.93
    frames = []
    for i in range(N["label"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        a = ramp(t, 0.0, 0.3)
        put1(im, card, CX, CY + 30 * (1 - a), a=a)
        put1(im, old, CX, 850, a=a * (1 - 0.55 * ramp(t, t_x + 0.25, t_x + 0.5)))
        u = ease((t - t_x) / 0.3)
        if u > 0:
            d = ImageDraw.Draw(im)
            d.line([(290, 862), (290 + 500 * u, 848)], fill=(200, 30, 30), width=12)
        if t > t_n:
            put1(im, new, CX, 1065, scale=min(pop(t, t_n, 0.35), 1.08))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"peta": skema_peta, "cangkir": skema_cangkir, "label": skema_label}

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
