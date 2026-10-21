"""Schematic map animations for Titik Heran #11 (run in the episode work dir; writes clips/skema1883.mp4 and clips/skema2026.mp4).
skema1883: Krakatau before 1883, then its northern two-thirds vanish and only the southern end (Rakata) is left.
skema2026: Anak Krakatau and the two land masses seen in Sep 2026, ±760 m north-west and ±495 m south-east of its coast,
in line with the crater (Badan Geologi via Antara and Kompas). Coastlines are schematic; the distances follow the reported numbers.
Event times are seconds from the start of each shot, read off the word anchors of `render.py 11 plan`.
"""
import math, subprocess
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H, FPS, S = 1080, 1920, 30, 2  # S: lines and text are drawn at 2x and scaled down for clean edges
BOLD, MED = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
YELLOW, WHITE = (255, 225, 0), (255, 255, 255)


def ramp(t, t0, t1):  # smoothstep from 0 at t0 to 1 at t1
    u = min(max((t - t0) / (t1 - t0), 0.0), 1.0)
    return u * u * (3 - 2 * u)


def pop(t, t0, d=0.3):  # 0 -> overshoot -> 1 (ease-out-back)
    u = min(max((t - t0) / d, 0.0), 1.0)
    return 0.0 if u <= 0 else 1 + 2.9 * (u - 1) ** 3 + 1.9 * (u - 1) ** 2


def layer():
    return Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))


def down(im):
    return im.resize((W, H), Image.LANCZOS)


def sc(pts):
    return [(x * S, y * S) for x, y in pts]


def background(cx, cy):
    """navy sea, lighter around the island, a faint map grid and a north arrow"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = (yy / H)[..., None]
    sea = np.array([13, 38, 78]) * (1 - v) + np.array([5, 17, 40]) * v
    sea += np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / 520 ** 2)[..., None] * np.array([16, 38, 66])
    im = Image.fromarray(np.clip(sea, 0, 255).astype(np.uint8)).convert("RGBA")
    g = layer()
    d = ImageDraw.Draw(g)
    for x in range(0, W + 1, 135):
        d.line([(x * S, 0), (x * S, H * S)], fill=(255, 255, 255, 16), width=2 * S)
    for y in range(-45, H + 1, 135):
        d.line([(0, y * S), (W * S, y * S)], fill=(255, 255, 255, 16), width=2 * S)
    ax, ay = 960 * S, 745 * S
    d.polygon([(ax, ay - 46 * S), (ax + 20 * S, ay + 12 * S), (ax, ay), (ax - 20 * S, ay + 12 * S)], fill=(255, 255, 255, 210))
    d.text((ax, ay - 58 * S), "U", font=ImageFont.truetype(BOLD, 40 * S), fill=(255, 255, 255, 225), anchor="ms")
    im.alpha_composite(down(g))
    return im


def text_sprite(lines, gap=4):
    """centred lines of (text, size, colour, bold) with a soft shadow, as an RGBA sprite at 2x"""
    fonts = [ImageFont.truetype(BOLD if b else MED, size * S) for _, size, _, b in lines]
    boxes = [f.getbbox(t) for f, (t, *_) in zip(fonts, lines)]
    m = 24 * S
    w = max(b[2] - b[0] for b in boxes) + 2 * m
    h = sum(b[3] - b[1] for b in boxes) + gap * S * (len(lines) - 1) + 2 * m
    sh, tx = Image.new("RGBA", (w, h), (0, 0, 0, 0)), Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ds, dt = ImageDraw.Draw(sh), ImageDraw.Draw(tx)
    y = m
    for f, b, (t, _, col, _) in zip(fonts, boxes, lines):
        x = (w - (b[2] - b[0])) // 2 - b[0]
        ds.text((x + 2 * S, y - b[1] + 3 * S), t, font=f, fill=(0, 0, 0, 200))
        dt.text((x, y - b[1]), t, font=f, fill=col + (255,))
        y += b[3] - b[1] + gap * S
    sh = sh.filter(ImageFilter.GaussianBlur(5 * S))
    sh.alpha_composite(tx)
    return sh


def fade(im, a):
    im = im.copy()
    im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return im


def put(base, sprite, cx, cy, a=1.0, scale=1.0):
    """composite a 2x sprite centred on (cx, cy) in 1x coordinates"""
    if a <= 0.01 or scale <= 0.01:
        return
    sp = sprite if scale == 1.0 else sprite.resize((max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))), Image.LANCZOS)
    base.alpha_composite(sp if a >= 1 else fade(sp, a), (round(cx * S - sp.width / 2), round(cy * S - sp.height / 2)))


def glow_sprite(r, col):
    g = Image.new("RGBA", (4 * r * S, 4 * r * S), col + (0,))
    ImageDraw.Draw(g).ellipse([r * S, r * S, 3 * r * S, 3 * r * S], fill=col + (255,))
    return g.filter(ImageFilter.GaussianBlur(r * S * 0.45))


def resample(pts, step=2.0):
    out, acc = [pts[0]], [0.0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(seg / step))
        for i in range(1, n + 1):
            out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
            acc.append(acc[-1] + seg / n)
    return out, acc


def dashed(d, pts, fill, width, dash=24, gap=16, upto=None):
    """dashes along a polyline in 1x coordinates; `upto` stops it at that length (to draw it on)"""
    p, acc = resample(pts)
    end = acc[-1] if upto is None else min(upto, acc[-1])
    k = 0
    while k * (dash + gap) < end:
        a, b = k * (dash + gap), min(k * (dash + gap) + dash, end)
        seg = [(x * S, y * S) for (x, y), L in zip(p, acc) if a <= L <= b]
        if len(seg) > 1:
            d.line(seg, fill=fill, width=width * S, joint="curve")
        k += 1


def chaikin(pts, n=3):
    for _ in range(n):
        q = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            q += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        pts = q
    return pts


def mask(pts):
    m = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(m).polygon(sc(pts), fill=255)
    return m


def shaded(m, cx, cy, r, inner, outer):
    """land coloured from `inner` at (cx, cy) to `outer` at distance r, cut out by mask m (2x)"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = np.clip(np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r, 0, 1)[..., None]
    im = Image.fromarray((np.array(inner) * (1 - u) + np.array(outer) * u).astype(np.uint8)).convert("RGBA")
    im.putalpha(m.resize((W, H), Image.LANCZOS))
    return im


def encode(frames, out):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.convert("RGB").tobytes())
    p.stdin.close()
    if p.wait():
        raise SystemExit(f"ffmpeg failed on {out}")
    print(out)


def krakatau_1883(n=80):
    cx, cy, km = 540, 935, 72  # island centre and pixels per km
    raw = [(-0.8, -4.5), (0.4, -4.25), (1.3, -3.3), (1.65, -1.9), (1.95, -0.55), (2.25, 0.75), (2.6, 1.95), (2.7, 3.15),
           (2.05, 4.25), (0.85, 4.6), (-0.45, 4.25), (-1.35, 3.35), (-1.6, 2.1), (-1.5, 0.8), (-1.8, -0.6), (-2.0, -2.0), (-1.8, -3.4)]
    coast = chaikin([(cx + x * km, cy + y * km) for x, y in raw])
    (ax, ay), (bx, by) = (cx - 2.2 * km, cy + 1.62 * km), (cx + 3.0 * km, cy + 1.0 * km)  # the 1883 collapse edge, south of it stays

    def ycut(x):
        return ay + (by - ay) * (x - ax) / (bx - ax)
    isl = mask(coast)
    half = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(half).polygon([(0, 0), (W * S, 0), (W * S, ycut(W) * S), (0, ycut(0) * S)], fill=255)
    north_m = ImageChops.multiply(isl, half)
    land = shaded(isl, cx, cy - 40, 360, (214, 194, 150), (164, 144, 104))
    north = land.copy()
    north.putalpha(north_m.resize((W, H), Image.LANCZOS))
    south = land.copy()
    south.putalpha(ImageChops.subtract(isl, north_m).resize((W, H), Image.LANCZOS))
    # coastline split into the part that vanishes and the part that stays
    side = [y < ycut(x) for x, y in coast]
    k = side.index(False)
    ring = coast[k:] + coast[:k]
    sring = [s for s in side[k:] + side[:k]]
    j0 = sring.index(True)
    j1 = len(sring) - sring[::-1].index(True)
    north_line = ring[j0 - 1:j1 + 1]
    south_line = ring[j1:] + ring[:j0]
    cliff = [north_line[0], north_line[-1]]
    bg = background(cx, cy)
    label = text_sprite([("KRAKATAU", 46, WHITE, True)])
    gone = text_sprite([("±2/3", 70, YELLOW, True), ("LENYAP", 46, YELLOW, True)])
    flash = glow_sprite(170, (255, 120, 20))
    fx, fy = cx + 0.1 * km, cy - 1.7 * km
    frames = []
    for i in range(n):
        t = i / FPS
        im = bg.copy()
        im.alpha_composite(south)
        na = 1 - ramp(t, 0.3, 0.8)
        if na > 0.01:
            im.alpha_composite(fade(north, na))
        top = layer()
        d = ImageDraw.Draw(top)
        d.line(sc(south_line), fill=(120, 100, 70, 255), width=4 * S, joint="curve")
        if na > 0.01:
            d.line(sc(north_line), fill=(120, 100, 70, round(255 * na)), width=4 * S, joint="curve")
        da = ramp(t, 0.55, 0.85)
        if da > 0.01:
            dashed(d, north_line, (255, 255, 255, round(200 * da)), 4)
            d.line(sc(cliff), fill=(92, 66, 40, round(255 * da)), width=7 * S)
        put(top, flash, fx, fy, a=ramp(t, 0.1, 0.28) * (1 - ramp(t, 0.28, 0.85)) * 0.95)
        ra = ramp(t, 0.2, 0.9)
        if 0 < ra < 1:
            r = (40 + 480 * ra) * S
            d.ellipse([fx * S - r, fy * S - r, fx * S + r, fy * S + r], outline=(255, 236, 200, round(170 * (1 - ra))), width=7 * S)
        put(top, label, cx - 10, cy - 30, a=1 - ramp(t, 0.2, 0.4))
        put(top, gone, cx - 5, cy - 1.25 * km, a=ramp(t, 0.9, 1.1), scale=pop(t, 0.9))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema1883.mp4")


def anak_krakatau_2026(n=72):
    (cx, cy), R, m_px = (560, 985), 190, 0.19  # island radius ~1 km, so 0.19 px per metre
    terms = [(0.05, 3, 0.7), (0.035, 5, 2.1), (0.02, 11, 0.3), (0.012, 17, 1.3)]

    def rad(t):
        return R * (1 + sum(a * math.sin(f * t + p) for a, f, p in terms))
    coast = [(cx + rad(t) * math.cos(t), cy + rad(t) * math.sin(t)) for t in (2 * math.pi * k / 240 for k in range(240))]
    nw_t, se_t = math.radians(225), math.radians(45)  # image angles: north-west and south-east of the crater
    nw = (cx + (rad(nw_t) + 760 * m_px) * math.cos(nw_t), cy + (rad(nw_t) + 760 * m_px) * math.sin(nw_t))
    se = (cx + (rad(se_t) + 495 * m_px) * math.cos(se_t), cy + (rad(se_t) + 495 * m_px) * math.sin(se_t))
    bg = background(cx, cy)
    halo = layer()
    ImageDraw.Draw(halo).polygon(sc([(cx + (x - cx) * 1.3, cy + (y - cy) * 1.3) for x, y in coast]), fill=(70, 130, 180, 110))
    bg.alpha_composite(down(halo.filter(ImageFilter.GaussianBlur(26 * S))))
    bg.alpha_composite(shaded(mask(coast), cx, cy, R, (52, 45, 42), (122, 106, 90)))
    top = layer()
    d = ImageDraw.Draw(top)
    d.line(sc(coast + coast[:1]), fill=(176, 158, 130, 255), width=5 * S, joint="curve")
    d.ellipse([(cx - 58) * S, (cy - 50) * S, (cx + 58) * S, (cy + 50) * S], fill=(34, 28, 26, 255))
    d.ellipse([(cx - 40) * S, (cy - 33) * S, (cx + 40) * S, (cy + 33) * S], fill=(150, 44, 12, 255))
    put(top, text_sprite([("ANAK", 40, WHITE, True), ("KRAKATAU", 40, WHITE, True)]), cx - 25, cy + 105)
    bg.alpha_composite(down(top))
    glow = glow_sprite(48, (255, 110, 20))
    dot = Image.new("RGBA", (80 * S, 80 * S), (0, 0, 0, 0))
    ImageDraw.Draw(dot).polygon(sc(chaikin([(40 + 22 * math.cos(a) * (1 + 0.18 * math.sin(3 * a + 1)), 40 + 19 * math.sin(a))
                                             for a in (2 * math.pi * k / 9 for k in range(9))])),
                                fill=YELLOW + (255,), outline=(70, 50, 0, 255), width=3 * S)
    lab_nw = text_sprite([("±760 m", 54, YELLOW, True), ("dari pantai", 36, WHITE, False)])
    lab_se = text_sprite([("±495 m", 54, YELLOW, True), ("dari pantai", 36, WHITE, False)])
    t_nw, t_se, t_line = 0.35, 0.82, 0.97  # "muncul", "dua", "daratan"
    frames = []
    for i in range(n):
        t = i / FPS
        im = bg.copy()
        top = layer()
        d = ImageDraw.Draw(top)
        put(top, glow, cx, cy, a=0.75 + 0.15 * math.sin(2 * math.pi * 2.3 * t) + 0.08 * math.sin(2 * math.pi * 5.1 * t + 1))
        u = ramp(t, t_line, t_line + 0.35)
        if u > 0:
            dashed(d, [nw, se], YELLOW + (190,), 5, dash=22, gap=14, upto=u * math.dist(nw, se))
        for (px, py), t0, lab, (lx, ly) in ((nw, t_nw, lab_nw, (nw[0] - 85, nw[1] - 105)), (se, t_se, lab_se, (se[0] + 140, se[1] - 70))):
            if t < t0:
                continue
            ph = ((t - t0) % 1.0) / 1.0
            r = (24 + 62 * ph) * S
            d.ellipse([px * S - r, py * S - r, px * S + r, py * S + r], outline=YELLOW + (round(200 * (1 - ph) ** 1.5),), width=4 * S)
            put(top, dot, px, py, scale=pop(t, t0))
            put(top, lab, lx, ly, a=ramp(t, t0 + 0.05, t0 + 0.25))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema2026.mp4")


if __name__ == "__main__":  # skema13.py imports the drawing helpers above
    krakatau_1883()
    anak_krakatau_2026()
