"""Night grade, reconstructions and schematic animations for Titik Heran #22 (run in the episode work dir; writes clips/142647n.mp4,
clips/skema_1989.mp4, skema_tinggi.mp4, skema_korsika.mp4 and skema_peta.mp4).
usage: python3 skema22.py GEO_DIR [malam|tape|tinggi|korsika|peta ...] [--sheet out.jpg t1,t2,...]
       (GEO_DIR holds ne_10m_land.geojson from github.com/nvkelso/natural-earth-vector, folder geojson/; --sheet saves those frames
       as a contact sheet instead of encoding)
malam -> clips/142647n.mp4: Pixabay 142647 (wing and a towering storm cloud, daylight) graded to moonlit night under a taller sky,
with a faint red flash above the cloud top on "aneh" and "badai": what the pilots reported (ilustrasi).
tape -> clips/skema_1989.mp4: static, then a grainy black-and-white low-light camera picture of a distant storm; a double column
flashes above the cloud tops and is circled. Winckler's team at the University of Minnesota caught the first sprite this way in
July 1989 (rekonstruksi, not their tape).
tinggi: an altitude column from the ground to 100 km: the storm cloud (tops ±15 km) and an airliner (±10 km), then the camera rises
and pulls back to a red sprite at 50-90 km, just under the dashed edge of space (±100 km). Heights to scale.
korsika: Pixabay 10333236 (Calvi, Corsica, at blue hour) graded to night; a camera frames the sky, the shutter fires and a red
sprite cluster hangs over the town, as in Florian Riou's photo of 16 Sep 2026 from nearby Montemaggiore (rekonstruksi; his photo
is not shown).
peta: the western Mediterranean from the Natural Earth coastlines: a pin at Montemaggiore, the storm in Catalonia, and the
distance between them counting up to 500+ km.
Event times are seconds from the start of each shot, read off `render.py 22 plan`.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, BOLD, MED, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, dashed, chaikin, encode
from skema13 import navy, marker
from skema17 import ring, label
from skema18 import clip_ring

NAMES = ("malam", "tape", "tinggi", "korsika", "peta")
GEO = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in NAMES else "geo"
NIGHT = "curves=all='0/0 0.35/0.11 0.7/0.32 1/0.56',eq=saturation=0.5,colorbalance=bs=0.16:bm=0.1:bh=0.05:rs=-0.06:rm=-0.05:gs=-0.02"


# ---------- the red sprite, as light ----------
def sprite_light(h, seed=22, wide=0.62, tendrils=34):
    """a jellyfish-type red sprite h px tall, as an additive light map (float32 h x w x 3, 0..1): faint red wisps above,
    a bright red crown at 30 % of the height, hair-like tendrils hanging to the bottom that turn violet-blue at the tips"""
    w = max(8, int(h * wide))
    k = 2  # drawn at 2x
    hw, hh = w * k, h * k
    rng = np.random.default_rng(seed)
    crown, hair, wisp = (Image.new("L", (hw, hh), 0) for _ in range(3))
    dc, dh, dw = ImageDraw.Draw(crown), ImageDraw.Draw(hair), ImageDraw.Draw(wisp)
    cx = hw / 2
    dc.ellipse([cx - 0.3 * hw, 0.21 * hh, cx + 0.3 * hw, 0.39 * hh], fill=125)
    dc.ellipse([cx - 0.19 * hw, 0.25 * hh, cx + 0.19 * hw, 0.35 * hh], fill=215)
    for _ in range(tendrils):
        u = rng.normal(0, 0.12)
        u = max(-0.27, min(0.27, u))
        x, y = cx + u * hw, (0.33 + rng.uniform(0, 0.04)) * hh
        end = rng.uniform(0.62, 0.95) * hh
        width = rng.uniform(0.004, 0.008) * hh
        val = int(rng.uniform(140, 255))
        pts = [(x, y)]
        drift = rng.normal(0, 0.05) * hw / hh
        while y < end:
            y += 0.02 * hh
            x += drift * 0.02 * hh + rng.normal(0, 0.004) * hw
            pts.append((x, y))
        dh.line(pts, fill=val, width=max(1, round(width)), joint="curve")
        for _ in range(rng.integers(1, 3)):  # forks near the tip
            j = rng.integers(len(pts) // 2, len(pts))
            fx, fy = pts[j]
            fork = [(fx, fy)]
            ang = rng.choice([-1, 1]) * rng.uniform(0.15, 0.4)
            for _ in range(rng.integers(3, 7)):
                fx += math.sin(ang) * 0.02 * hh
                fy += math.cos(ang) * 0.02 * hh
                fork.append((fx, fy))
            dh.line(fork, fill=int(val * 0.7), width=max(1, round(width * 0.6)), joint="curve")
    for _ in range(7):
        u = rng.uniform(-0.17, 0.17)
        x, y = cx + u * hw, 0.24 * hh
        top = rng.uniform(0.02, 0.12) * hh
        pts = [(x, y)]
        while y > top:
            y -= 0.02 * hh
            x += rng.normal(0, 0.003) * hw
            pts.append((x, y))
        dw.line(pts, fill=int(rng.uniform(90, 160)), width=max(1, round(0.006 * hh)), joint="curve")
    crown = crown.filter(ImageFilter.GaussianBlur(0.035 * hh))
    hair = hair.filter(ImageFilter.GaussianBlur(0.0025 * hh))
    wisp = wisp.filter(ImageFilter.GaussianBlur(0.006 * hh))
    v = np.linspace(0, 1, hh, dtype=np.float32)[:, None, None]
    # tendrils: red at the crown, magenta in the middle, violet-blue at the tips
    t = np.clip((v - 0.33) / 0.6, 0, 1)
    hair_col = (np.array([1.0, 0.2, 0.25]) * (1 - t) + np.array([0.45, 0.3, 1.0]) * t).astype(np.float32)
    light = (np.asarray(crown, np.float32)[..., None] / 255 * np.array([1.0, 0.32, 0.24], np.float32)
             + np.asarray(hair, np.float32)[..., None] / 255 * hair_col
             + np.asarray(wisp, np.float32)[..., None] / 255 * np.array([0.9, 0.22, 0.3], np.float32))
    light = np.clip(light, 0, 1)
    img = Image.fromarray((light * 255).astype(np.uint8))
    bloom = np.asarray(img.filter(ImageFilter.GaussianBlur(0.03 * hh)), np.float32) / 255
    out = np.clip(light + 0.9 * bloom, 0, 1)
    return np.asarray(Image.fromarray((out * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS), np.float32) / 255


def screen(base, light, x, y, k=1.0):
    """screen-blend a light map (float, 0..1) into base (float H x W x 3) with its top-left corner at (x, y)"""
    if k <= 0.003:
        return
    lh, lw = light.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(base.shape[1], x + lw), min(base.shape[0], y + lh)
    if x1 <= x0 or y1 <= y0:
        return
    sub = light[y0 - y:y1 - y, x0 - x:x1 - x] * k
    base[y0:y1, x0:x1] = 1 - (1 - base[y0:y1, x0:x1]) * (1 - np.clip(sub, 0, 1))


def tint(base, light, x, y, k=1.0):
    """paint a light map over a bright background, where screen would wash out: its hue at full value, alpha from its brightness"""
    if k <= 0.003:
        return
    lh, lw = light.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(base.shape[1], x + lw), min(base.shape[0], y + lh)
    if x1 <= x0 or y1 <= y0:
        return
    sub = np.clip(light[y0 - y:y1 - y, x0 - x:x1 - x], 0, 1)
    peak = sub.max(axis=2, keepdims=True)
    a = np.clip(peak * 1.6, 0, 1) * k
    base[y0:y1, x0:x1] = base[y0:y1, x0:x1] * (1 - a) + 0.85 * sub / np.maximum(peak, 1e-3) * a


def scaled(light, h):
    h = max(4, int(h))
    w = max(4, int(light.shape[1] * h / light.shape[0]))
    return np.asarray(Image.fromarray((light * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS), np.float32) / 255


def to_im(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")


def frames_of(src, start, n, vf):
    """n frames of a clip from `start` seconds through an ffmpeg filter that ends in a 1080 px wide picture, as float arrays"""
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", src, "-frames:v", str(n), "-vf", vf + ",format=rgb24",
                        "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    hh = len(p) // (n * W * 3)
    return [np.frombuffer(p[i * W * hh * 3:(i + 1) * W * hh * 3], np.uint8).reshape(hh, W, 3).astype(np.float32) / 255
            for i in range(n)]


def stars(n, seed, y0=0, y1=H, faint=0.35):
    rng = np.random.default_rng(seed)
    return np.c_[rng.uniform(0, W, n), rng.uniform(y0, y1, n), rng.uniform(faint, 1.0, n) ** 2]


def draw_stars(a, st, k=1.0, dy=0.0, scale=1.0, cx=W / 2, cy=H / 2):
    xs = np.round(cx + (st[:, 0] - cx) * scale).astype(int)
    ys = np.round(cy + (st[:, 1] - cy) * scale + dy).astype(int)
    ok = (xs >= 1) & (xs < W - 1) & (ys >= 1) & (ys < H - 1)
    for x, y, b in zip(xs[ok], ys[ok], st[ok, 2]):
        v = 0.85 * b * k
        a[y, x] = np.maximum(a[y, x], v)
        if b > 0.7:
            for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a[y + ddy, x + ddx] = np.maximum(a[y + ddy, x + ddx], v * 0.35)


# ---------- malam: the wing and storm cloud at night, with the strange flash ----------
def malam(times):
    n = round(max(times) * FPS) + 1
    top = 520  # the clip is scaled to 1500 px high and its top 1400 px go under a taller night sky
    src = frames_of("clips/142647.mp4", 3.0, n, f"scale=-2:1500:flags=lanczos,crop={W}:1400:(iw-{W})*0.43:0,{NIGHT}")
    sky0 = src[0][:12].mean((0, 1))
    g = np.linspace(0, 1, top + 120, dtype=np.float32)[:, None, None]
    sky = (sky0 * 0.55) * (1 - g) + sky0 * g  # darker towards the top
    st = stars(160, 4, 0, top + 60, faint=0.3)
    sp = sprite_light(270, seed=7, wide=0.55, tendrils=26)
    # the cloud top sits at ±y 760 under the new sky; the flash hangs just above it
    fx, fy = 470, 760 - 262
    # kilatan 0.04, aneh 0.51, di 0.97, atas 1.17, badai 1.36
    def flash(t):
        k = 0.0
        for t0, a in ((0.52, 0.95), (0.62, 0.55), (1.38, 0.7)):
            k = max(k, a * math.exp(-max(0.0, t - t0) / 0.05) if t >= t0 else 0.0)
        return k
    out = []
    for t in times:
        f = src[min(round(t * FPS), n - 1)]
        a = np.zeros((H, W, 3), np.float32)
        a[top:top + 1400] = f
        blend = np.clip((np.arange(top + 120) - top) / 120, 0, 1)[:, None, None]
        a[:top + 120] = sky * (1 - blend) + a[:top + 120] * blend
        draw_stars(a, st, 0.6)
        k = flash(t)
        if k > 0:
            glow = np.zeros((360, 520, 3), np.float32)
            yy, xx = np.mgrid[0:360, 0:520]
            glow[...] = (np.exp(-(((xx - 260) / 105) ** 2 + ((yy - 230) / 60) ** 2))[..., None] * np.array([0.35, 0.05, 0.08]))
            screen(a, glow, fx + sp.shape[1] // 2 - 260, 760 - 230, k)  # the cloud top catches a little red
            screen(a, sp, fx, fy, k)
        out.append(to_im(a))
    return out


# ---------- tape: the 1989 low-light camera ----------
def tape(times):
    lw, lh = W // 4, H // 4  # drawn small, then blown up like analog video
    rng = np.random.default_rng(1989)
    xs = np.arange(lw)
    ridge = 318 + 10 * np.sin(xs / 23) + 7 * np.sin(xs / 9 + 1) + 4 * np.sin(xs / 4.3)
    bank = (np.arange(lh)[:, None] > ridge[None, :]).astype(np.float32)
    bank_im = Image.fromarray((bank * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5))
    bank = np.asarray(bank_im, np.float32) / 255
    puff = Image.fromarray((rng.uniform(0, 1, (lh // 6, lw // 6)) * 255).astype(np.uint8)).resize((lw, lh), Image.BICUBIC)
    bank = bank * (0.75 + 0.5 * np.asarray(puff.filter(ImageFilter.GaussianBlur(3)), np.float32) / 255)  # lumpy cloud tops
    sky = np.linspace(0.08, 0.17, lh, dtype=np.float32)[:, None] * np.ones((1, lw), np.float32)
    col = Image.new("L", (lw, lh), 0)
    d = ImageDraw.Draw(col)
    for x0, y0, y1, w0 in ((128, 214, 306, 7), (147, 230, 300, 5)):  # the double column, as on the first tape
        d.ellipse([x0 - w0, y0, x0 + w0, y1], fill=230)
        d.line([(x0, y0 + 10), (x0, y1 + 8)], fill=255, width=3)
    col = np.asarray(col.filter(ImageFilter.GaussianBlur(3.0)), np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = np.clip(1.15 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2), 0, 1)
    # tak 0.04, sengaja 0.23, merekamnya 0.82
    t_snow, t_flash, t_ring = 0.2, 0.8, 0.98
    out = []
    for i, t in enumerate(times):
        if t < t_snow:
            g = rng.uniform(0, 1, (lh, lw)).astype(np.float32) ** 1.5
            roll = int((t / t_snow) * lh * 1.5) % lh
            g[max(0, roll - 30):roll] *= 0.5
        else:
            frozen = t >= t_flash + 0.12
            g = sky + bank * 0.2
            if not frozen and rng.uniform() < 0.25:  # lightning inside the distant clouds
                g = g + bank * rng.uniform(0.05, 0.18)
            k = 0.0
            if t >= t_flash:
                k = 0.95 if t < t_flash + 0.1 else 0.55
            g = g + col * k
            grain = rng.normal(0, 0.055 if not frozen else 0.035, (lh, lw)).astype(np.float32)
            if frozen:  # a paused tape: a band of noise holds still
                g[402:411] += rng.uniform(0.0, 0.35, (9, lw)).astype(np.float32)
            g = g + grain
            g[::2] *= 0.82  # scanlines
        big = np.asarray(Image.fromarray((np.clip(g, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
        a = np.repeat((big * vig)[..., None], 3, 2) * np.array([0.92, 0.97, 1.0], np.float32)
        im = to_im(a)
        if t >= t_ring:
            top = layer()
            d = ImageDraw.Draw(top)
            u = ramp(t, t_ring, t_ring + 0.3)
            cxr, cyr, r = 552, 1000, 175
            d.arc([(cxr - r) * S, (cyr - r) * S, (cxr + r) * S, (cyr + r) * S], -90, -90 + 360 * u, fill=YELLOW + (255,), width=9 * S)
            im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- tinggi: the altitude column ----------
CX = 650  # the storm and the sprite stand on this x


def cloud_mask(s, gy):
    """a cumulonimbus (2x mask) for s px per km with the ground at gy: a lumpy tower from a 2 km base, an anvil spreading at
    12-15 km with an overshooting top"""
    m = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(m)

    def P(x, y):
        return ((CX + x * s) * S, (gy - y * s) * S)
    d.polygon([P(-4.6, 2.0), P(4.8, 2.0), P(5.1, 8.0), P(4.2, 12.6), P(-4.0, 12.6), P(-4.9, 8.0)], fill=255)
    d.polygon([P(-9.0, 13.4), P(-6.5, 14.9), P(13.0, 15.1), P(15.6, 13.7), P(12.0, 12.5), P(-6.0, 12.3)], fill=255)
    puffs = [(-4.7, 3.4, 1.3), (-5.1, 5.4, 1.6), (-4.8, 7.5, 1.5), (-4.5, 9.6, 1.6), (-3.7, 11.4, 1.5), (4.9, 3.2, 1.3),
             (5.4, 5.3, 1.7), (5.1, 7.4, 1.5), (4.7, 9.4, 1.6), (3.9, 11.3, 1.6), (0.0, 15.5, 1.4), (-1.6, 14.9, 1.2),
             (1.7, 15.0, 1.2), (-7.5, 13.6, 1.1), (14.4, 13.9, 1.0), (8.0, 14.6, 0.9), (-2.4, 12.6, 1.3), (2.6, 12.7, 1.3)]
    for x, y, r in puffs:
        (x0, y0), (x1, y1) = P(x - r, y + r), P(x + r, y - r)
        d.ellipse([x0, y0, x1, y1], fill=255)
    return m.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(max(1.0, 0.12 * s)))


def plane_sprite(L=90):
    """an airliner in side view, nose to the right, L px long (2x sprite)"""
    im = Image.new("RGBA", (int(L * 1.2) * S, int(L * 0.6) * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    oy = L * 0.3

    def P(pts):
        return [((x + 0.1) * L * S, (y * L + oy) * S) for x, y in pts]
    d.polygon(P([(0.0, -0.02), (0.88, -0.03), (1.0, 0.0), (0.88, 0.035), (0.05, 0.03), (-0.02, -0.2), (0.07, -0.2)]),
              fill=(220, 228, 245, 255))
    d.polygon(P([(0.38, 0.02), (0.55, 0.02), (0.42, 0.16), (0.35, 0.16)]), fill=(190, 200, 225, 255))
    return im


def tinggi(times):
    light = sprite_light(1000, seed=22)
    st = np.c_[np.random.default_rng(3).uniform(0, W, 420), np.random.default_rng(4).uniform(18, 120, 420),
               np.random.default_rng(5).uniform(0.25, 1.0, 420) ** 2]  # stars at x px and height km
    plane = plane_sprite()
    f_tick = ImageFont.truetype(MED, 28 * S)
    f_tick_b = ImageFont.truetype(BOLD, 30 * S)
    lab_plane = text_sprite([("pesawat ±10 km", 30, WHITE, False)])
    lab_cloud = text_sprite([("awan badai", 30, WHITE, False), ("±15 km", 34, YELLOW, True)])
    lab_jelly = text_sprite([("bentuknya", 28, WHITE, False), ("mirip ubur-ubur", 30, WHITE, True)])
    lab_edge = text_sprite([("±100 km", 40, YELLOW, True)])
    # Namanya 0.05, red 0.68, sprait 0.95, kilat 1.73, merah 2.00, raksasa 2.24, nyaris 3.17, di 3.59, tepi 3.71, luar 3.91, angkasa 4.18
    t_bolt, t_sprite, t_band, t_jelly, t_edge = 0.82, 0.95, 1.75, 2.3, 3.2

    def cam(t):
        u = ramp(t, 0.5, 1.8)
        if t <= 1.8:
            s = 26 + (11 - 26) * u
            gy = 1240 + (1660 - 1240) * u
        else:
            s = 11 - 0.8 * ramp(t, 1.8, 4.93)
            gy = 560 + 100 * s
        return s, gy
    out = []
    rows = np.arange(H, dtype=np.float32)
    for t in times:
        s, gy = cam(t)
        km = (gy - rows) / s
        c0, c1, c2, c3 = np.array([26, 38, 74]), np.array([13, 20, 46]), np.array([5, 8, 22]), np.array([2, 3, 10])
        kk = km[:, None]
        col = np.where(kk < 15, c0 + (c1 - c0) * np.clip(kk / 15, 0, 1),
                       np.where(kk < 45, c1 + (c2 - c1) * np.clip((kk - 15) / 30, 0, 1), c2 + (c3 - c2) * np.clip((kk - 45) / 55, 0, 1)))
        a = np.repeat((col / 255).astype(np.float32)[:, None, :], W, 1)
        sy = gy - st[:, 1] * s
        ok = (sy > 1) & (sy < H - 1)
        for x, y, b, h_km in zip(st[ok, 0], sy[ok], st[ok, 2], st[ok, 1]):
            v = 0.8 * b * min(1.0, (h_km - 18) / 20)
            a[int(y), int(x)] = np.maximum(a[int(y), int(x)], v)
        # the sprite, from 92 km (wisp tops) down to 46 km
        if t >= t_sprite:
            k = 1.0 if t < t_sprite + 0.08 else 0.82 + 0.1 * math.sin(t * 23) * math.sin(t * 7.3)
            k *= ramp(t, t_sprite, t_sprite + 0.04)
            lit = scaled(light, 46 * s)
            screen(a, lit, int(CX - lit.shape[1] / 2), int(gy - 92 * s), k)
        im = to_im(a)
        lay = layer()
        d = ImageDraw.Draw(lay)
        # ground
        hills = [(x, gy + 6 + 10 * math.sin(x / 140) + 6 * math.sin(x / 47)) for x in range(-20, W + 40, 20)]
        d.polygon(sc(hills + [(W + 40, H + 10), (-20, H + 10)]), fill=(9, 12, 18, 255))
        im.alpha_composite(down(lay))
        # storm cloud, lit from above, with a flicker inside; then the strong strike that sets off the sprite
        flick = 0.0
        for t0 in (0.15, 0.38, t_bolt, 2.6, 3.9):
            if t0 <= t < t0 + 0.12:
                flick = max(flick, 1 - (t - t0) / 0.12)
        cm = cloud_mask(s, gy)
        v = np.clip((gy - rows - 2 * s) / (14 * s), 0, 1)[:, None, None]
        shade = (np.array([58, 66, 92]) * (1 - v) + np.array([150, 160, 190]) * v)
        yy = rows[:, None]
        xx = np.arange(W, dtype=np.float32)[None, :]
        core = np.exp(-(((xx - CX) / (4.5 * s)) ** 2 + ((yy - (gy - 8 * s)) / (5 * s)) ** 2))[..., None]
        cl = np.clip(shade + core * (25 + 200 * flick), 0, 255).astype(np.uint8)
        cloud = Image.fromarray(np.broadcast_to(cl, (H, W, 3)).copy()).convert("RGBA")
        cloud.putalpha(cm)
        im.alpha_composite(cloud)
        top = layer()
        d = ImageDraw.Draw(top)
        if t_bolt <= t < t_bolt + 0.16:
            bx = CX + 1.5 * s
            bolt = [(bx, gy - 2 * s)]
            rng = np.random.default_rng(int(t_bolt * 100))
            while bolt[-1][1] < gy:
                bolt.append((bolt[-1][0] + rng.normal(0, 0.35) * s, min(gy, bolt[-1][1] + 0.5 * s)))
            d.line(sc(bolt), fill=(255, 250, 220, 255), width=max(2, round(0.12 * s)) * S, joint="curve")
        # airliner at 10 km
        pa = 1 - ramp(t, 2.0, 2.5)
        put(top, plane, CX - 11.5 * s, gy - 10 * s, scale=max(0.25, s / 26), a=1.0)
        put(top, lab_plane, CX - 11.5 * s, gy - 10 * s - 44, a=pa * (1 - ramp(t, 0.9, 1.3)))
        put(top, lab_cloud, CX + 9.5 * s, gy - 18.6 * s, a=1 - ramp(t, 0.9, 1.3))
        # height axis
        ax = 86
        d.line(sc([(ax, min(H, gy)), (ax, max(0, gy - 104 * s))]), fill=(200, 210, 235, 170), width=3 * S)
        band = ramp(t, t_band, t_band + 0.3)
        if band > 0:
            d.line(sc([(ax, gy - 50 * s), (ax, gy - 50 * s - (40 * s) * band)]), fill=YELLOW + (255,), width=9 * S)
        for v in range(10, 101, 10):
            y = gy - v * s
            if y < -20 or y > H + 20:
                continue
            hot = band > 0 and v in (50, 90)
            d.line(sc([(ax - 10, y), (ax + 10, y)]), fill=(YELLOW + (255,)) if hot else (200, 210, 235, 200), width=3 * S)
            d.text(((ax + 18) * S, y * S), f"{v} km", font=f_tick_b if hot else f_tick,
                   fill=(YELLOW + (255,)) if hot else (200, 210, 235, 210), anchor="lm")
        if t >= t_jelly:
            put(top, lab_jelly, CX + 0.26 * 46 * s + 130, gy - 74 * s, a=ramp(t, t_jelly, t_jelly + 0.2), scale=pop(t, t_jelly))
        ue = ramp(t, t_edge, t_edge + 0.55)
        if ue > 0:
            y = gy - 100 * s
            dashed(d, [(ax, y), (ax + (1040 - ax) * ue, y)], fill=(255, 255, 255, 235), width=4, dash=26, gap=16)
            put(top, lab_edge, 930, y - 34, a=ramp(t, t_edge + 0.3, t_edge + 0.5), scale=pop(t, t_edge + 0.3))
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- korsika: Calvi at night and the sprite cluster ----------
def korsika(times):
    src = Image.open("img/10333236.jpg").convert("RGB")
    x0, x1, scl, ytop = 440, 1115, 1.6, 555  # the crop around the citadel and where its top edge lands
    ph = src.crop((x0, 0, x1, src.height)).resize((W, round(src.height * scl)), Image.LANCZOS)
    p = np.asarray(ph, np.float32) / 255
    p = p ** 2.0 * np.array([0.78, 0.86, 1.08], np.float32)  # night: the sky drops away, the lights stay
    base = np.zeros((H, W, 3), np.float32)
    hgt = min(H - ytop, p.shape[0])
    base[ytop:ytop + hgt] = p[:hgt]
    sky0 = p[:10].mean((0, 1))
    g = np.linspace(0, 1, ytop + 140, dtype=np.float32)[:, None, None]
    sky = sky0 * 0.35 * (1 - g) + sky0 * g
    blend = np.clip((np.arange(ytop + 140) - ytop) / 140, 0, 1)[:, None, None]
    base[:ytop + 140] = sky * (1 - blend) + base[:ytop + 140] * blend
    draw_stars(base, stars(260, 9, 0, 900, faint=0.3), 0.55)
    big = sprite_light(430, seed=31)
    small = sprite_light(300, seed=5, wide=0.5, tendrils=20)
    # September 0.05, lalu 0.53, fotografer 1.16, Prancis 1.73, memotretnya 2.20, seolah 3.28, melayang 3.63, di 4.25, atas 4.37,
    # desa 4.72, di 4.99, Korsika 5.15
    t_frame, t_shot = 1.75, 2.22
    zc = (560, 840)
    out = []
    for t in times:
        a = base.copy()
        if t >= t_shot:
            k = 1.0 if t < t_shot + 0.07 else 0.78
            for t0 in (3.3, 4.7):
                if t0 <= t < t0 + 0.25:
                    k = max(k, 1.0 - 0.22 * (t - t0) / 0.25)
            k *= 0.94 + 0.06 * math.sin(t * 17)
            screen(a, big, 560 - big.shape[1] // 2, 935 - big.shape[0], k)
            screen(a, small, 760 - small.shape[1] // 2, 905 - small.shape[0], k * 0.8)
            halo = np.zeros((420, 700, 3), np.float32)
            yy, xx = np.mgrid[0:420, 0:700]
            halo[...] = np.exp(-(((xx - 350) / 300) ** 2 + ((yy - 210) / 170) ** 2))[..., None] * np.array([0.16, 0.03, 0.05])
            screen(a, halo, 640 - 350, 760 - 210, k)
        z = 1 + 0.12 * ramp(t, 0, max(times)) if max(times) > 0 else 1
        im = to_im(a)
        if z > 1.001:
            cw, ch = W / z, H / z
            l, u = zc[0] - cw * zc[0] / W, zc[1] - ch * zc[1] / H
            im = im.crop((round(l), round(u), round(l + cw), round(u + ch))).resize((W, H), Image.BICUBIC)
        top = layer()
        d = ImageDraw.Draw(top)
        fa = ramp(t, t_frame, t_frame + 0.15) * (1 - ramp(t, t_shot, t_shot + 0.02))
        if fa > 0:  # a camera frames the sky over the town
            bx0, by0, bx1, by1, L = 250, 560, 830, 1120, 70
            for (x, y, sx, sy) in ((bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx0, by1, 1, -1), (bx1, by1, -1, -1)):
                d.line(sc([(x, y + sy * L), (x, y), (x + sx * L, y)]), fill=(255, 255, 255, round(235 * fa)), width=6 * S)
            d.rectangle(sc([(540 - 26, 840 - 26), (540 + 26, 840 + 26)]), outline=(120, 255, 120, round(220 * fa)), width=4 * S)
        im.alpha_composite(down(top))
        if t_shot <= t < t_shot + 0.16:  # the shutter
            im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, round(200 * (1 - (t - t_shot) / 0.16)))))
        out.append(im)
    return out


# ---------- peta: Corsica to Catalonia ----------
COS42 = math.cos(math.radians(42))
MONTE, STORM = (8.89, 42.53), (2.2, 41.75)  # Montemaggiore; the storm over Catalonia, just north of Barcelona


def west_med():
    rings = []
    for f in json.load(open(os.path.join(GEO, "ne_10m_land.geojson")))["features"]:
        geo = f["geometry"]
        for poly in geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]:
            r = poly[0]
            lo, la = [q[0] for q in r], [q[1] for q in r]
            if max(lo) < -6 or min(lo) > 18 or max(la) < 34 or min(la) > 50:
                continue
            c = clip_ring(r, -6, 34, 18, 50)
            if len(c) > 2:
                rings.append(c)
    return rings


def km_between(a, b):
    la1, la2 = math.radians(a[1]), math.radians(b[1])
    dl = math.radians(b[0] - a[0])
    return 6371 * math.acos(math.sin(la1) * math.sin(la2) + math.cos(la1) * math.cos(la2) * math.cos(dl))


def storm_icon(r=46):
    im = Image.new("RGBA", (int(4 * r) * S, int(4 * r) * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = 2 * r * S
    for dx, dy, rr in ((-0.55, 0.1, 0.55), (0.0, -0.2, 0.75), (0.6, 0.12, 0.55), (0.0, 0.25, 0.6)):
        d.ellipse([c + (dx - rr) * r * S, c + (dy - rr) * r * S, c + (dx + rr) * r * S, c + (dy + rr) * r * S], fill=(70, 78, 100, 255))
    return im


def bolt_icon(r=46):
    im = Image.new("RGBA", (int(4 * r) * S, int(4 * r) * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = 2 * r * S
    pts = [(0.1, 0.35), (-0.25, 1.05), (0.05, 1.05), (-0.2, 1.65), (0.42, 0.8), (0.1, 0.8), (0.35, 0.35)]
    d.polygon([(c + x * r * S, c + y * r * S) for x, y in pts], fill=YELLOW + (255,))
    return im


def peta(times):
    rings = west_med()
    bg = navy(540, 900)
    dist = km_between(MONTE, STORM)
    print(f"Montemaggiore - storm: {dist:.0f} km")
    lab_fr = text_sprite([("PRANCIS", 50, (70, 56, 34), True)])
    lab_es = text_sprite([("SPANYOL", 50, (70, 56, 34), True)])
    lab_sea = text_sprite([("L A U T   T E N G A H", 26, (190, 214, 240), True)])
    lab_monte = label([("Montemaggiore", 34, WHITE, True), ("Korsika · lokasi foto", 26, WHITE, False)], edge=YELLOW + (230,))
    lab_storm = label([("badai petir", 34, WHITE, True), ("Katalonia, Spanyol", 26, WHITE, False)], edge=(255, 110, 90, 230))
    cloud, bolt = storm_icon(), bolt_icon()
    tiny = sprite_light(90, seed=12, wide=0.55, tendrils=14)
    dot = marker()
    f_num = ImageFont.truetype(BOLD, 96 * S)
    # Padahal 0.02, badainya 0.61, di 0.96, Spanyol 1.08, lebih 1.93, dari 2.16, lima 2.40, ratus 2.63, kilometer 3.02, jauhnya 3.52
    t_z0, t_z1, t_storm, t_line0, t_line1, t_done = 0.0, 1.0, 0.75, 1.9, 2.95, 3.02
    v0, v1 = (MONTE[0], MONTE[1], 520, 900), (4.8, 42.3, 150, 900)
    out = []
    for t in times:
        z = ramp(t, t_z0, t_z1)
        clon, clat = v0[0] + (v1[0] - v0[0]) * z, v0[1] + (v1[1] - v0[1]) * z
        kpx = math.exp(math.log(v0[2]) + (math.log(v1[2]) - math.log(v0[2])) * z)

        def xy(lon, lat):
            return 540 + (lon - clon) * kpx * COS42, 900 - (lat - clat) * kpx
        im = bg.copy()
        lay = layer()
        d = ImageDraw.Draw(lay)
        for r in rings:
            pts = [xy(*q) for q in r]
            xs, ys = [x for x, _ in pts], [y for _, y in pts]
            if max(xs) < -50 or min(xs) > W + 50 or max(ys) < -50 or min(ys) > H + 50:
                continue
            hot = 8.4 < sum(q[0] for q in r) / len(r) < 9.7 and 41.3 < sum(q[1] for q in r) / len(r) < 43.1  # Corsica
            d.polygon(sc(pts), fill=((232, 208, 150, 255) if hot else (222, 200, 150, 255)), outline=(120, 100, 68, 255))
        im.alpha_composite(down(lay))
        top = layer()
        d = ImageDraw.Draw(top)
        put(top, lab_fr, *xy(3.9, 44.0), a=ramp(t, 0.5, 0.9))
        put(top, lab_es, *xy(1.15, 41.2), a=ramp(t, 0.7, 1.1))
        put(top, lab_sea, *xy(5.6, 40.4), a=0.8 * ramp(t, 0.6, 1.0))
        mx, my = xy(*MONTE)
        sx_, sy_ = xy(*STORM)
        ul = ramp(t, t_line0, t_line1)
        if ul > 0:
            dashed(d, [(mx, my), (mx + (sx_ - mx) * ul, my + (sy_ - my) * ul)], fill=YELLOW + (255,), width=6, dash=24, gap=14)
        for ph0 in (0.0, 0.5):
            ph = ((t + ph0) % 1.0) / 1.0
            ring(d, mx, my, 16 + 56 * ph, YELLOW, 220 * (1 - ph) ** 1.5, w=4)
        put(top, dot, mx, my, scale=0.8 * pop(t, 0.05))
        put(top, lab_monte, mx - 165, my + 96, a=ramp(t, 0.1, 0.3), scale=pop(t, 0.1))
        if t >= t_storm:
            put(top, cloud, sx_, sy_ - 8, scale=pop(t, t_storm))
            fl = (t - t_storm) % 0.7 < 0.12
            if fl:
                put(top, bolt, sx_, sy_ - 8)
            put(top, lab_storm, sx_ + 190, sy_ + 78, a=ramp(t, t_storm + 0.1, t_storm + 0.3), scale=pop(t, t_storm + 0.1))
        if ul > 0:
            n = int(round(dist * min(1.0, ul)))
            txt = "500+ km" if t >= t_done else f"{min(n, 500)} km"
            num = Image.new("RGBA", (700 * S, 170 * S), (0, 0, 0, 0))
            nd = ImageDraw.Draw(num)
            nd.text((353 * S, 91 * S), txt, font=f_num, fill=(0, 0, 0, 180), anchor="mm")
            nd.text((350 * S, 85 * S), txt, font=f_num, fill=YELLOW + (255,), anchor="mm")
            put(top, num, (mx + sx_) / 2 + 10, (my + sy_) / 2 - 120, scale=pop(t, t_done) if t >= t_done else 1.0)
        im.alpha_composite(down(top))
        if t >= t_storm:  # the sprite over the storm, flashing (tinted: it sits on pale land)
            k = 0.0
            for t0 in (t_storm + 0.15, 2.1, t_done + 0.05, 3.7):
                if t0 <= t < t0 + 0.3:
                    k = max(k, 1 - (t - t0) / 0.3)
            if k > 0:
                a = np.asarray(im.convert("RGB"), np.float32) / 255
                tint(a, tiny, int(sx_ - tiny.shape[1] / 2), int(sy_ - 52 - tiny.shape[0]), k)
                im = to_im(a)
        out.append(im)
    return out


N = {"malam": 72, "tape": 54, "tinggi": 149, "korsika": 179, "peta": 128}
OUT = {"malam": "clips/142647n.mp4", "tape": "clips/skema_1989.mp4"}
if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != GEO]
    sheet = None
    if "--sheet" in args:
        i = args.index("--sheet")
        sheet, ts = args[i + 1], [float(v) for v in args[i + 2].split(",")]
        args = args[:i]
    for name in args or list(N):
        if sheet:
            fr = [f.convert("RGB").resize((W // 3, H // 3)) for f in globals()[name](ts)]
            sh = Image.new("RGB", (len(fr) * W // 3, H // 3))
            for k, f in enumerate(fr):
                sh.paste(f, (k * W // 3, 0))
            sh.save(sheet.replace(".jpg", f"_{name}.jpg"), quality=85)
        else:
            encode(globals()[name]([i / FPS for i in range(N[name])]), OUT.get(name, f"clips/skema_{name}.mp4"))
