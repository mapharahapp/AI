"""Schematic animations for Titik Heran #14 (run in the episode work dir; writes clips/skema_*.mp4).
usage: python3 skema14.py [warna|spektrum|putih|titik|serap|duo ...]
skema_warna: star colours run from red (cool) to blue (hot); the green slot stays empty.
skema_spektrum: the Sun's light over the visible spectrum (Planck curve at 5.772 K), strongest near 500 nm.
skema_putih: the colours of the rainbow added together make white.
skema_titik: a flight into a star field to one star that turns green, WD J1330+6435.
skema_serap: sodium takes out the yellow, orange and red light; what is left looks green.
skema_duo: the green white dwarf next to a pink one, found in the same study.
The green and pink are estimates (Hollands et al. 2026 computed them from the spectra), hence the "warna perkiraan" tag.
Event times are seconds from the start of each shot, read off `render.py 14 plan`.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, put, dashed, encode

GREEN, PINK = (150, 236, 110), (255, 168, 190)
CX, CY = 540, 900  # centre of the drawings: below the title, above the captions


def space(seed=14):
    """deep navy sky with faint stars"""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = (yy / H)[..., None]
    col = np.array([11, 26, 56]) * (1 - v) + np.array([3, 8, 22]) * v
    col += np.exp(-((xx - CX) ** 2 + (yy - CY) ** 2) / 560 ** 2)[..., None] * np.array([12, 24, 46])
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")
    g = layer()
    d = ImageDraw.Draw(g)
    for _ in range(240):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.6, 1.7)
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(255, 255, 255, int(rng.uniform(40, 160))))
    im.alpha_composite(down(g))
    return im


def star(r, col, glow=0.85):
    """a star disc of radius r with a whiter centre and a soft glow of its own colour, as a 2x sprite"""
    n = int(r * 3.2 * S)
    yy, xx = np.mgrid[-n:n, -n:n].astype(np.float32)
    d = np.hypot(xx, yy) / S
    core = np.clip(r - d + 0.5, 0, 1)
    halo = glow * np.exp(-np.maximum(d - r, 0) ** 2 / (0.6 * r) ** 2)
    hot = (np.clip(1 - d / r, 0, 1) ** 1.6)[..., None]
    rgb = np.array(col, np.float32) * (1 - 0.5 * hot) + 255 * 0.5 * hot
    a = core + (1 - core) * halo
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8), "RGBA")


def ring(d, x, y, r, col, a, w=5):
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], outline=col + (round(a),), width=w * S)


def pulse(d, x, y, r0, t, t0, col=YELLOW, period=0.9, grow=60):
    if t >= t0:
        ph = ((t - t0) % period) / period
        ring(d, x, y, r0 + grow * ph, col, 230 * (1 - ph) ** 1.5)


def wl_rgb(nm):
    """visible wavelength -> sRGB (Bruton's approximation), dimmer toward both ends"""
    if nm < 440:
        c = ((440 - nm) / 60, 0, 1)
    elif nm < 490:
        c = (0, (nm - 440) / 50, 1)
    elif nm < 510:
        c = (0, 1, (510 - nm) / 20)
    elif nm < 580:
        c = ((nm - 510) / 70, 1, 0)
    elif nm < 645:
        c = (1, (645 - nm) / 65, 0)
    else:
        c = (1, 0, 0)
    f = 0.35 + 0.65 * (nm - 380) / 40 if nm < 420 else 0.35 + 0.65 * (780 - nm) / 80 if nm > 700 else 1.0
    return tuple(round(255 * (f * max(v, 0)) ** 0.8) for v in c)


def warna(n=70):
    cols = [(255, 96, 62), (255, 160, 72), (255, 222, 122), (255, 250, 242), (198, 218, 255), (128, 164, 255)]
    xs = [128 + 165 * k for k in range(6)]
    y0, gy, gr = 780, 1065, 112  # the row, the green slot and its radius
    bg = space()
    stars = [star(62, c, 0.7) for c in cols]
    cold, hot = text_sprite([("DINGIN", 40, (255, 150, 110), True)]), text_sprite([("PANAS", 40, (160, 190, 255), True)])
    q = text_sprite([("?", 140, GREEN, True)])
    lab = text_sprite([("HIJAU", 56, GREEN, True)])
    frames = []
    for i in range(n):
        t = i / FPS
        im = bg.copy()
        top = layer()
        d = ImageDraw.Draw(top)
        for k, (x, sp) in enumerate(zip(xs, stars)):
            put(top, sp, x, y0, scale=pop(t, 0.02 + 0.08 * k, 0.28))
        a = ramp(t, 0.45, 0.7)
        if a > 0:
            d.line(sc([(272, y0 + 118), (818, y0 + 118)]), fill=(255, 255, 255, round(170 * a)), width=4 * S)
            d.polygon(sc([(842, y0 + 118), (816, y0 + 104), (816, y0 + 132)]), fill=(255, 255, 255, round(170 * a)))
            put(top, cold, 160, y0 + 118, a=a)
            put(top, hot, 936, y0 + 118, a=a)
        dashed(d, [(540 + gr * math.cos(u), gy + gr * math.sin(u)) for u in np.linspace(-math.pi / 2, 1.5 * math.pi, 140)],
               GREEN + (230,), 6, dash=20, gap=13, upto=ramp(t, 0.72, 1.05) * 2 * math.pi * gr)
        put(top, q, 540, gy - 4, a=ramp(t, 0.85, 1.0), scale=pop(t, 0.85))
        put(top, lab, 540, gy + gr + 58, a=ramp(t, 0.9, 1.1))
        x = pop(t, 1.22, 0.25)
        if x > 0:
            L = 118 * x
            for s_ in (1, -1):
                d.line(sc([(540 - L, gy - L * s_), (540 + L, gy + L * s_)]), fill=(235, 45, 45, 255), width=20 * S)
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_warna.mp4")


def spektrum(n=66):
    x0, x1, base, hmax = 150, 930, 1150, 420
    lam = np.linspace(380, 750, x1 - x0)
    b = lam ** -5.0 / (np.exp(1.4388e7 / (lam * 5772)) - 1)  # Planck, wavelength in nm
    b = b / b.max()
    peak = float(lam[b.argmax()])
    xp, yp = x0 + (peak - 380) / 370 * (x1 - x0), base - hmax
    bg = space()
    g = layer()  # sprites are 2x: they go on a 2x layer, never straight on the 1x background
    d = ImageDraw.Draw(g)
    d.line(sc([(x0 - 10, base), (x1 + 10, base)]), fill=(255, 255, 255, 200), width=3 * S)
    for nm in (400, 500, 600, 700):
        put(g, text_sprite([(str(nm), 32, WHITE, False)]), x0 + (nm - 380) / 370 * (x1 - x0), base + 36, a=0.85)
    put(g, text_sprite([("nm", 28, WHITE, False)]), x1 + 4, base + 36, a=0.65)
    put(g, text_sprite([("cahaya Matahari", 38, WHITE, True)]), 540, 1250, a=0.9)
    bg.alpha_composite(down(g))
    cols = np.array([wl_rgb(v) for v in lam], np.uint8)
    fill = np.zeros((H, W, 4), np.uint8)
    for k in range(x1 - x0):
        top = int(base - b[k] * hmax)
        fill[top:base, x0 + k, :3] = cols[k]
        fill[top:base, x0 + k, 3] = 215
    fill = Image.fromarray(fill, "RGBA")
    curve = [(x0 + k, base - b[k] * hmax) for k in range(x1 - x0)]
    lab = text_sprite([("±500 nm", 50, YELLOW, True)])
    t_peak = 0.95  # "hijau!" lands at 1.00
    frames = []
    for i in range(n):
        t = i / FPS
        im = bg.copy()
        reveal = x0 + ramp(t, 0.0, 0.8) * (x1 - x0)
        if reveal > x0:
            cut = fill.crop((0, 0, int(reveal), H))
            im.alpha_composite(cut, (0, 0))
        top = layer()
        d = ImageDraw.Draw(top)
        pts = [p for p in curve if p[0] <= reveal]
        if len(pts) > 1:
            d.line(sc(pts), fill=(255, 255, 255, 255), width=5 * S, joint="curve")
        if t >= t_peak:
            fx = layer()  # ImageDraw replaces pixels instead of blending, so see-through rings get a layer of their own
            dashed(d, [(xp, yp - 6), (xp, base)], (255, 255, 255, 230), 4, dash=14, gap=10, upto=ramp(t, t_peak, t_peak + 0.25) * (base - yp))
            pulse(ImageDraw.Draw(fx), xp, yp, 18, t, t_peak + 0.1, period=0.8, grow=50)
            top.alpha_composite(fx)
            r = 13 * pop(t, t_peak, 0.25)
            d.ellipse([(xp - r) * S, (yp - r) * S, (xp + r) * S, (yp + r) * S], fill=YELLOW + (255,), outline=(60, 45, 0, 255), width=3 * S)
            put(top, lab, xp + 150, yp - 30, a=ramp(t, t_peak + 0.05, t_peak + 0.25), scale=pop(t, t_peak + 0.05))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_spektrum.mp4")


def putih(n=68):
    cols = [wl_rgb(v) for v in (650, 605, 575, 530, 470, 420)]
    cols[5] = (150, 60, 255)  # a brighter violet, so the sum reaches white
    bg = np.asarray(space(), np.float32)[..., :3]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    R, R0 = 150, 330
    lab = text_sprite([("PUTIH", 64, WHITE, True)])
    frames = []
    for i in range(n):
        t = i / FPS
        u = ramp(t, 0.0, 0.92)
        acc = np.zeros((H, W, 3), np.float32)
        for k, c in enumerate(cols):
            ang = -math.pi / 2 + k * math.pi / 3 + 0.6 * u
            cx, cy = CX + R0 * (1 - u) * math.cos(ang), CY + R0 * (1 - u) * math.sin(ang)
            m = np.clip(R - np.hypot(xx - cx, yy - cy) + 0.5, 0, 1)
            acc += m[..., None] * np.array(c, np.float32) * 0.92
        flash = math.exp(-((t - 1.0) / 0.25) ** 2) * (t > 0.85)
        glow = np.exp(-np.maximum(np.hypot(xx - CX, yy - CY) - R, 0) ** 2 / 70 ** 2)[..., None] * 160 * ramp(t, 0.8, 1.05)
        img = np.clip(bg + acc + glow * (1 + flash), 0, 255).astype(np.uint8)
        im = Image.fromarray(img).convert("RGBA")
        top = layer()
        put(top, lab, CX, CY + R + 90, a=ramp(t, 1.0, 1.2), scale=pop(t, 1.0))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_putih.mp4")


def titik(n=122):
    rng = np.random.default_rng(1330)
    f, DT = 900.0, 100.0  # focal length; depth of the target star
    N = 1400
    depth = rng.uniform(4, 420, N)
    u, v = rng.uniform(-1.25, 1.25, N), rng.uniform(-1.25, 1.25, N)
    wx, wy = u * 540 / f * depth, v * 960 / f * depth
    keep = np.hypot(wx, wy) > 2.5  # leave the line of sight to the target clear
    depth, wx, wy = depth[keep], wx[keep], wy[keep]
    tint = rng.choice([(255, 255, 255), (255, 240, 215), (215, 228, 255), (255, 214, 170)], len(depth))
    base_r = rng.uniform(0.7, 1.6, len(depth))
    bg = space(7)
    t_arrive, t_green, t_ring, t_lab = 2.25, 2.26, 2.62, 2.95
    lab = text_sprite([("WD J1330+6435", 46, WHITE, True), ("bintang mati (katai putih)", 32, WHITE, False)], gap=8)
    frames = []
    for i in range(n):
        t = i / FPS
        cam = 88 * (1 - (1 - min(t / t_arrive, 1)) ** 3)
        im = bg.copy()
        top = layer()
        d = ImageDraw.Draw(top)
        D = depth - cam
        vis = D > 1.5
        sx, sy = CX + wx[vis] * f / D[vis], CY + wy[vis] * f / D[vis]
        rr = np.clip(base_r[vis] * 150 / D[vis], 0.8, 6.5)
        aa = np.clip(130 / D[vis], 0.35, 1.0)
        for x, y, r, a, c in zip(sx, sy, rr, aa, tint[vis]):
            if -20 < x < W + 20 and -20 < y < H + 20:
                d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=tuple(int(k) for k in c) + (int(255 * a),))
        im.alpha_composite(down(top))
        g = ramp(t, t_green, t_green + 0.4)
        col = tuple(round(w_ * (1 - g) + c * g) for w_, c in zip((255, 248, 236), GREEN))
        r_t = 2.2 * DT / (DT - cam) + 52 * pop(t, t_green, 0.45)
        top = layer()
        put(top, star(max(r_t, 1.5), col, 0.6 + 0.3 * g), CX, CY)
        if t >= t_ring:
            fx = layer()
            d = ImageDraw.Draw(fx)
            ring(d, CX, CY, (r_t + 34) * pop(t, t_ring, 0.3), YELLOW, 240, 6)
            pulse(d, CX, CY, r_t + 34, t, t_ring + 0.3, period=0.9, grow=55)
            top.alpha_composite(fx)
        put(top, lab, CX, CY + r_t + 125, a=ramp(t, t_lab, t_lab + 0.2), scale=pop(t, t_lab))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_titik.mp4")


def serap(n=104):
    x0, x1, y0, y1 = 150, 930, 1015, 1085
    sy = 755  # the star
    lam = np.linspace(400, 700, x1 - x0)
    cols = np.array([wl_rgb(v) for v in lam], np.float32)
    cols *= (0.6 + 0.4 * np.clip((lam - 400) / 80, 0, 1))[:, None]  # a cool star (±4.000 °C) gives off little blue
    bar = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    bar[..., :3] = cols[None].astype(np.uint8)
    bar[..., 3] = 255
    bar = Image.fromarray(bar, "RGBA")
    bg = space(5)
    g = layer()
    for nm, txt in ((400, "400"), (500, "500"), (600, "600"), (700, "700 nm")):
        put(g, text_sprite([(txt, 32, WHITE, False)]), x0 + (nm - 400) / 300 * (x1 - x0) + (24 if nm == 700 else 0), y1 + 36, a=0.85)
    bg.alpha_composite(down(g))
    note = text_sprite([("warna dihitung dari cahayanya", 30, WHITE, False)])
    absorbed = text_sprite([("diserap natrium", 34, WHITE, True)])
    left = text_sprite([("sisanya", 34, GREEN, True)])

    def xw(nm):
        return x0 + (nm - 400) / 300 * (x1 - x0)

    def cut(t):  # the absorption creeps from yellow to the red end as the words land
        if t < 0.55:
            return 570 + 22 * ramp(t, 0.04, 0.45)
        if t < 0.82:
            return 592 + 30 * ramp(t, 0.55, 0.8)
        return 622 + 78 * ramp(t, 0.82, 1.3)
    t_left = 1.79  # "menyisakan"
    frames = []
    for i in range(n):
        t = i / FPS
        im = bg.copy()
        im.alpha_composite(bar, (x0, y0))
        top = layer()
        d = ImageDraw.Draw(top)
        c = cut(t)
        if c > 570.5:
            d.rectangle(sc([(xw(570), y0 - 1), (xw(c), y1 + 1)]), fill=(6, 10, 22, 225))
            d.line(sc([(xw(570), y0 - 26), (xw(570), y0 - 12), (xw(c), y0 - 12), (xw(c), y0 - 26)]), fill=(255, 255, 255, 220), width=4 * S)
            put(top, absorbed, (xw(570) + xw(c)) / 2, y0 - 58, a=ramp(t, 0.25, 0.45))
        if t >= t_left:
            a = ramp(t, t_left, t_left + 0.2)
            d.rectangle(sc([(xw(490), y0 - 6), (xw(570), y1 + 6)]), outline=YELLOW + (round(255 * a),), width=5 * S)
            put(top, left, xw(530), y1 + 82, a=a, scale=pop(t, t_left))
        g = ramp(t, 0.1, 1.5)
        col = tuple(round(w_ * (1 - g) + k * g) for w_, k in zip((255, 248, 236), GREEN))
        put(top, star(105, col, 0.75), CX, sy)
        if t >= 2.3:  # "hijau." lands at 2.35
            fx = layer()
            pulse(ImageDraw.Draw(fx), CX, sy, 128, t, 2.3, col=GREEN, period=1.0, grow=60)
            top.alpha_composite(fx)
        put(top, note, CX, 1215, a=0.85 * ramp(t, 0.3, 0.6))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_serap.mp4")


def duo(n=170):
    gx, px, y, r = 290, 790, 880, 128
    bg = space(9)
    gl = text_sprite([("HIJAU", 58, GREEN, True)])
    pl = text_sprite([("MERAH MUDA", 58, PINK, True)])
    t_pink, t_g, t_p = 1.72, 3.05, 4.22  # "merah", "hijau,", "pink?"
    frames = []
    for i in range(n):
        t = i / FPS
        im = bg.copy()
        top = layer()
        d = ImageDraw.Draw(top)
        wob = 1 + 0.02 * math.sin(2 * math.pi * t / 1.7)
        put(top, star(r * wob, GREEN, 0.75), gx, y, scale=pop(t, 0.0, 0.25) if t < 0.3 else 1.0)
        put(top, gl, gx, y + r + 105, a=ramp(t, 0.1, 0.35))
        if t >= t_pink:
            put(top, star(r / wob, PINK, 0.75), px, y, scale=pop(t, t_pink, 0.35))
            put(top, pl, px, y + r + 105, a=ramp(t, t_pink + 0.1, t_pink + 0.3))
        fx = layer()
        pulse(ImageDraw.Draw(fx), gx, y, r + 28, t, t_g, col=GREEN, period=0.95, grow=70)
        pulse(ImageDraw.Draw(fx), px, y, r + 28, t, t_p, col=PINK, period=0.95, grow=70)
        top.alpha_composite(fx)
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_duo.mp4")


for name in sys.argv[1:] or ["warna", "spektrum", "putih", "titik", "serap", "duo"]:
    globals()[name]()
