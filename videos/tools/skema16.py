"""Size comparisons for Titik Heran #16 (run in the episode work dir; writes clips/skema_kepala.mp4 and clips/skema_patung.mp4).
usage: python3 skema16.py [kepala|patung ...]
skema_kepala: the Ramses II head from Behbeit el-Hagar, ±1,6 m with the double crown, comes up out of the soil next to a 1,7 m adult.
skema_patung: the same head on top of the whole statue, ±8,5 m with its base (the estimate of the Supreme Council of Antiquities);
the camera pulls back from the head until the adult shows up at the statue's feet. The body is dashed because only the head was found.
The head and the statue are drawn from the usual shape of a standing Ramses II colossus, not from the real pieces (their photos belong
to the ministry and the press). Event times are seconds from the start of each shot, read off `render.py 16 plan`.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, dashed, chaikin, encode
from skema13 import navy

HEAD_M, STATUE_M, ADULT_M = 1.6, 8.5, 1.7
GY0, K0, HX0, PX0 = 1250, 370, 400, 760  # kepala: ground line, px per metre, centre of the head, centre of the adult
K1, HX1, TOP1 = 76, 380, 634  # patung after the pull-back: px per metre, statue centre, top of the crown (ground at 1280)
LINE = (86, 48, 42, 255)


def half(pts):
    """the right half of a symmetric outline (x >= 0, top to bottom) -> the whole closed outline"""
    return pts + [(-x, y) for x, y in reversed(pts)]


# the head in units of its own height (x from the middle, y down from the top of the crown)
WHITE_CROWN = chaikin(half([(0.05, 0.045), (0.1, 0.1), (0.14, 0.17), (0.158, 0.25), (0.157, 0.33), (0.15, 0.4)]), 2)
RED_CROWN = half([(0.245, 0.36), (0.225, 0.53)])
FACE = chaikin(half([(0.2, 0.52), (0.206, 0.58), (0.2, 0.65), (0.182, 0.72), (0.142, 0.785), (0.078, 0.826), (0.0, 0.836)]), 2)
BEARD = half([(0.046, 0.8), (0.058, 1.0)])
_rng = np.random.default_rng(16)
NECK = [(-0.16, 0.72), (0.16, 0.72)] + [(0.165 - 0.33 * k / 10, 0.955 + 0.03 * _rng.uniform(-1, 1) * (0 < k < 10)) for k in range(11)]
TEX = None


def texture():
    """granite speckles in head units, made once and resized for every frame"""
    global TEX
    if TEX is None:
        rng = np.random.default_rng(7)
        tex = Image.new("RGBA", (720, 1200), (0, 0, 0, 0))
        d = ImageDraw.Draw(tex)
        for _ in range(5200):
            x, y, r = rng.uniform(0, 720), rng.uniform(0, 1200), rng.uniform(1.0, 3.2)
            col = (40, 22, 20, int(rng.uniform(40, 120))) if rng.uniform() < 0.62 else (255, 236, 228, int(rng.uniform(40, 110)))
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        TEX = tex
    return TEX


def head_sprite(hh):
    """front view of a pink-granite pharaoh head in the double crown, hh px tall at 1x, as a 2x sprite whose top edge is the crown"""
    s = hh * S
    w2, h2 = int(0.6 * s) + 2, int(1.0 * s) + 2
    cx = w2 / 2

    def P(pts):
        return [(cx + x * s, y * s) for x, y in pts]
    im = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon(P(WHITE_CROWN), fill=(198, 140, 128, 255))
    d.ellipse([cx - 0.036 * s, 0.004 * s, cx + 0.036 * s, 0.076 * s], fill=(198, 140, 128, 255))  # the knob on top
    d.polygon(P(RED_CROWN), fill=(160, 98, 88, 255))
    d.polygon(P(NECK), fill=(146, 92, 82, 255))
    for sx in (-1, 1):  # ears
        d.ellipse([cx + sx * 0.215 * s - 0.036 * s, 0.555 * s, cx + sx * 0.215 * s + 0.036 * s, 0.675 * s], fill=(170, 110, 98, 255))
    d.polygon(P(FACE), fill=(186, 124, 112, 255))
    d.polygon(P(BEARD), fill=(158, 100, 90, 255))
    d.ellipse([cx - 0.03 * s, 0.405 * s, cx + 0.03 * s, 0.5 * s], fill=(204, 148, 134, 255))  # uraeus: hood and head
    d.ellipse([cx - 0.016 * s, 0.375 * s, cx + 0.016 * s, 0.41 * s], fill=(204, 148, 134, 255))
    # light from the upper left, darker towards the outline, granite speckles
    a = np.asarray(im)[..., 3].astype(np.float32) / 255
    yy, xx = np.mgrid[0:h2, 0:w2].astype(np.float32)
    xn, yn = (xx - cx) / s, yy / s
    edge = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.02 * s))).astype(np.float32) / 255
    shade = (1.1 - 0.5 * xn - 0.14 * yn) * (0.8 + 0.2 * edge)
    rgb = np.clip(np.asarray(im)[..., :3].astype(np.float32) * shade[..., None], 0, 255)
    im = Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), "RGBA")
    spk = texture().resize((w2, h2), Image.BILINEAR)
    spk.putalpha(Image.fromarray((np.asarray(spk)[..., 3].astype(np.float32) * a).astype(np.uint8)))
    im.alpha_composite(spk)
    d = ImageDraw.Draw(im)
    lw = max(2, round(0.006 * s))
    d.line(P([(-0.245, 0.36), (0.245, 0.36)]), fill=(214, 160, 146, 255), width=lw)  # top edge of the red crown
    for sx in (-1, 1):
        f = lambda pts: P([(sx * x, y) for x, y in pts])
        d.line(f([(0.03, 0.586), (0.09, 0.574), (0.165, 0.588)]), fill=LINE, width=lw)  # brow
        d.polygon(f([(0.038, 0.617), (0.065, 0.603), (0.095, 0.6), (0.128, 0.61), (0.11, 0.625), (0.075, 0.629), (0.048, 0.624)]),
                  fill=(232, 196, 184, 255), outline=LINE, width=lw)  # eye
        d.ellipse([cx + sx * 0.085 * s - 0.014 * s, 0.6 * s, cx + sx * 0.085 * s + 0.014 * s, 0.628 * s], fill=LINE)
        d.line(f([(0.128, 0.61), (0.168, 0.606)]), fill=LINE, width=lw)  # the painted line out of the eye corner
        d.line(f([(0.012, 0.6), (0.022, 0.676), (0.042, 0.703), (0.018, 0.716), (0.0, 0.712)]), fill=LINE, width=lw)  # nose
        d.line(f([(0.0, 0.753), (0.022, 0.749), (0.062, 0.756)]), fill=LINE, width=lw)  # mouth
        d.line(f([(0.012, 0.772), (0.042, 0.77)]), fill=(120, 74, 64, 255), width=lw)
    for k in range(7):  # the plaited beard
        y = 0.83 + k * 0.025
        d.line(P([(-0.05 - 0.01 * (y - 0.8) / 0.2, y), (0.05 + 0.01 * (y - 0.8) / 0.2, y)]), fill=(110, 66, 58, 255), width=lw)
    d.line(P(NECK[2:]), fill=(70, 40, 36, 255), width=lw)  # where the neck broke off
    return im


def place(lay, sprite, cx, top):
    """composite a 2x sprite onto a 2x layer, centred on x = cx with its top edge at y = top (1x)"""
    lay.alpha_composite(sprite, (round(cx * S - sprite.width / 2), round(top * S)))


def adult_sprite(hp):
    """a plain adult figure, hp px tall at 1x, as a 2x sprite with its top edge at the top of the head"""
    s = hp * S
    w2, h2 = int(0.44 * s) + 2, int(s) + 2
    cx = w2 / 2
    im = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = (226, 234, 246, 240)
    d.ellipse([cx - 0.062 * s, 0.0, cx + 0.062 * s, 0.13 * s], fill=col)
    d.rounded_rectangle([cx - 0.035 * s, 0.11 * s, cx + 0.035 * s, 0.17 * s], radius=0.01 * s, fill=col)
    d.rounded_rectangle([cx - 0.13 * s, 0.155 * s, cx + 0.13 * s, 0.53 * s], radius=0.05 * s, fill=col)
    for sx in (-1, 1):  # arms, then legs
        for x0, x1, y0, y1, r in ((0.145, 0.2, 0.165, 0.5, 0.027), (0.015, 0.115, 0.48, 1.0, 0.04)):
            xa, xb = sorted([cx + sx * x0 * s, cx + sx * x1 * s])
            d.rounded_rectangle([xa, y0 * s, xb, y1 * s], radius=r * s, fill=col)
    return im


def soil(gy):
    """the ground from y = gy down: dark soil with a few layers and stones"""
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    v = np.clip((yy - gy) / (H - gy), 0, 1)[..., None]
    rgb = np.array([104, 76, 52]) * (1 - v) + np.array([46, 33, 24]) * v
    im = Image.fromarray(rgb.astype(np.uint8)).convert("RGBA")
    m = layer()
    dm = ImageDraw.Draw(m)
    xs = list(range(-10, W + 11, 8))
    dm.polygon(sc([(x, gy + 3 * math.sin(x / 37) + 2 * math.sin(x / 13)) for x in xs] + [(W + 10, H + 10), (-10, H + 10)]), fill=(255,) * 4)
    im.putalpha(down(m).getchannel("A"))
    top = layer()
    d = ImageDraw.Draw(top)
    for k, (y0, amp) in enumerate(((gy + 90, 10), (gy + 230, 14), (gy + 420, 12))):
        d.line(sc([(x, y0 + amp * math.sin(x / (70 + 20 * k) + k)) for x in xs]), fill=(150, 116, 82, 70), width=4 * S)
    rng = np.random.default_rng(3)
    for _ in range(46 if gy + 30 < H else 0):
        x, y, r = rng.uniform(0, W), rng.uniform(gy + 30, H), rng.uniform(5, 16)
        pts = [(x + r * rng.uniform(0.6, 1.1) * math.cos(a), y + r * rng.uniform(0.6, 1.1) * math.sin(a)) for a in sorted(rng.uniform(0, 2 * math.pi, 6))]
        g = int(rng.uniform(-10, 20))
        d.polygon(sc(pts), fill=(120 + g, 96 + g, 74 + g, 200))
    d.line(sc([(x, gy + 3 * math.sin(x / 37) + 2 * math.sin(x / 13)) for x in xs]), fill=(170, 134, 96, 255), width=4 * S)
    im.alpha_composite(down(top))
    return im


def dim_line(d, x, y_low, y_high, col, a, ticks=None):
    """a vertical measuring line with arrowheads, from y_low up to y_high (1x); ticks: y of the metre marks"""
    if a <= 0.01 or y_low - y_high < 4:
        return
    c = col + (round(255 * a),)
    d.line(sc([(x, y_low), (x, y_high)]), fill=c, width=4 * S)
    for y, s_ in ((y_low, -1), (y_high, 1)):
        d.line(sc([(x - 18, y), (x + 18, y)]), fill=c, width=4 * S)
        if y_low - y_high > 40:
            d.polygon(sc([(x, y), (x - 11, y - 20 * s_), (x + 11, y - 20 * s_)]), fill=c)
    for y in ticks or []:
        if y_high + 6 < y < y_low - 6:
            d.line(sc([(x - 12, y), (x, y)]), fill=c, width=3 * S)


def dust(d, t, gy, x0, x1, t0=0.0, t1=0.75, n=70):
    """bits of soil thrown up while the head comes out"""
    rng = np.random.default_rng(11)
    for _ in range(n):
        ts, x, vx, vy, r = rng.uniform(t0, t1 - 0.3), rng.uniform(x0, x1), rng.uniform(-260, 260), rng.uniform(-620, -260), rng.uniform(3, 8)
        dt = t - ts
        if not 0 <= dt <= 0.7:
            continue
        px, py = x + vx * dt, gy + vy * dt + 1400 * dt * dt
        if py > gy + 4:
            continue
        al = int(230 * (1 - dt / 0.7))
        d.ellipse([(px - r) * S, (py - r) * S, (px + r) * S, (py + r) * S], fill=(150, 112, 78, al))


def kepala(n=120):
    hh, hp = HEAD_M * K0, ADULT_M * K0
    bg = navy(540, 900)
    ground = soil(GY0)
    head, adult = head_sprite(hh), adult_sprite(hp)
    lab_head = text_sprite([("1,6 m", 64, YELLOW, True)])
    lab_adult = text_sprite([("1,7 m", 44, WHITE, True), ("orang", 30, WHITE, False)], gap=2)
    xd_head, xd_adult = HX0 - 0.25 * hh - 40, PX0 + 0.2 * hp + 34
    # kepala 0.02, raksasa 0.28, Ramses 0.73, Kedua 1.14, setinggi 1.74, satu 2.22, koma 2.60, enam 2.89, meter 3.12
    t_adult, t_dim, t_num, t_meter = 0.5, 1.74, 2.22, 3.12
    frames = []
    for i in range(n):
        t = i / FPS
        im = bg.copy()
        back = layer()
        u = 1 - (1 - ramp(t, 0.0, 0.75)) ** 2  # out of the soil, slowing down at the top
        place(back, head, HX0, GY0 - u * hh)
        a = ramp(t, t_adult, t_adult + 0.3)
        if a > 0:
            place(back, adult if a >= 1 else fade(adult, a), PX0 + 30 * (1 - a), GY0 - hp)
        im.alpha_composite(down(back))
        im.alpha_composite(ground)
        top = layer()
        d = ImageDraw.Draw(top)
        dust(d, t, GY0, HX0 - 0.25 * hh, HX0 + 0.25 * hh)
        dim_line(d, xd_adult, GY0, GY0 - ramp(t, t_adult + 0.4, t_adult + 0.8) * hp, WHITE, 0.75)
        put(top, lab_adult, xd_adult + 76, GY0 - hp / 2, a=0.85 * ramp(t, t_adult + 0.7, t_adult + 0.9))
        dim_line(d, xd_head, GY0, GY0 - ramp(t, t_dim, t_num + 0.1) * hh, YELLOW, 1.0)
        bump = 1 + 0.12 * math.exp(-((t - t_meter) / 0.12) ** 2)  # a small nudge on "meter"
        put(top, lab_head, xd_head - 92, GY0 - hh / 2, a=ramp(t, t_num, t_num + 0.12), scale=pop(t, t_num) * bump)
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_kepala.mp4")


# the standing statue below the head, in metres (x from the middle, y up from the ground): right half of the outline
BODY = [(0.17, 7.25), (0.2, 6.78), (0.7, 6.56), (0.95, 6.42), (1.0, 6.2), (0.97, 4.25), (0.96, 4.02), (0.86, 3.87), (0.7, 3.92), (0.74, 3.4),
        (0.56, 3.38), (0.57, 2.3), (0.52, 1.05), (0.64, 0.98), (0.64, 0.8), (1.1, 0.8), (1.1, 0.0)]
BODY_LINES = [[(-0.62, 4.55), (0.62, 4.55)], [(-0.74, 3.4), (0.74, 3.4)], [(0.68, 6.3), (0.7, 4.1)], [(-0.68, 6.3), (-0.7, 4.1)],
              [(0.15, 3.38), (0.15, 0.98)], [(-0.15, 3.38), (-0.15, 0.98)], [(0.12, 4.5), (0.12, 3.42)], [(-0.12, 4.5), (-0.12, 3.42)]]


def patung(n=100):
    bg = navy(540, 900)
    lab_tall = text_sprite([("±8,5 m", 66, YELLOW, True)])
    lab_head = text_sprite([("KEPALA", 36, YELLOW, True), ("yang ditemukan", 28, WHITE, False)], gap=2)
    lab_adult = text_sprite([("1,7 m", 34, WHITE, True)])
    lab_base = text_sprite([("alas", 26, WHITE, False)])
    outline = [(x, y) for x, y in BODY] + [(-x, y) for x, y in reversed(BODY)]
    soils = {}
    # Patung 0.04, utuhnya 0.36, diperkirakan 0.85, delapan 1.55, setengah 2.07, meter 2.44
    t_pull0, t_pull1, t_dim, t_num, t_meter = 0.15, 1.45, 1.5, 1.6, 2.44
    frames = []
    for i in range(n):
        t = i / FPS
        u = ramp(t, t_pull0, t_pull1)
        k = math.exp(math.log(K0) + (math.log(K1) - math.log(K0)) * u)  # an even pull-back: the scale changes by the same ratio per frame
        top_y = (GY0 - HEAD_M * K0) + (TOP1 - (GY0 - HEAD_M * K0)) * u
        cx = HX0 + (HX1 - HX0) * u
        gy = top_y + STATUE_M * k  # the camera keeps the crown in place, so the ground comes up from below

        def xy(x, y):
            return cx + x * k, gy - y * k
        im = bg.copy()
        if gy < H:
            g = round(gy)
            if g not in soils:
                soils[g] = soil(g)
            im.alpha_composite(soils[g])
        body = layer()
        d = ImageDraw.Draw(body)
        a = ramp(t, 0.0, 0.35)
        d.polygon(sc([xy(*p) for p in outline]), fill=(178, 116, 104, round(80 * a)))
        if a > 0:
            dashed(d, [xy(*p) for p in outline + outline[:1]], (255, 255, 255, round(220 * a)), 3, dash=18, gap=11)
            for ln in BODY_LINES:
                dashed(d, [xy(*p) for p in ln], (255, 255, 255, round(110 * a)), 2, dash=12, gap=10)
        place(body, head_sprite(HEAD_M * k), cx, top_y)
        hp = ADULT_M * k
        place(body, adult_sprite(hp), cx + 6.58 * k, gy - hp)
        im.alpha_composite(down(body))
        top = layer()
        d = ImageDraw.Draw(top)
        xd = cx + 1.58 * k
        ticks = [gy - m * k for m in range(1, 9)]
        dim_line(d, xd, gy, gy - ramp(t, t_dim, t_dim + 0.4) * STATUE_M * k, YELLOW, 1.0, ticks)
        bump = 1 + 0.12 * math.exp(-((t - t_meter) / 0.12) ** 2)
        put(top, lab_tall, xd + 128, gy - STATUE_M * k / 2, a=ramp(t, t_num, t_num + 0.12), scale=pop(t, t_num) * bump)
        f = ramp(t, t_pull1 - 0.1, t_pull1 + 0.15)
        if f > 0:
            hx, hy = xy(-0.42, STATUE_M - 0.62 * HEAD_M)
            d.line(sc([(hx - 12, hy), (hx - 78, hy)]), fill=YELLOW + (round(230 * f),), width=3 * S)
            put(top, lab_head, hx - 190, hy, a=f)
            put(top, lab_adult, cx + 6.58 * k, gy - hp - 26, a=f)
            put(top, lab_base, cx, gy - 0.4 * k, a=f * 0.9)
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_patung.mp4")


if __name__ == "__main__":
    for name in sys.argv[1:] or ["kepala", "patung"]:
        globals()[name]()
