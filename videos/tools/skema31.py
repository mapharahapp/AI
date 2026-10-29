"""Schematic animations for Titik Heran #31 (run in the episode work dir after `dl.py i:3636061 i:447578`;
writes clips/skema_rute.mp4, skema_lenyap.mp4 and skema_surat.mp4).
usage: python3 skema31.py GEO_DIR [rute|lenyap|surat ...] [--sheet out.jpg t1,t2,...]
       (GEO_DIR holds ne_10m_land.geojson from github.com/nvkelso/natural-earth-vector, folder geojson/;
       --sheet saves those frames as a contact sheet instead of encoding)
skema_rute: Java from the Natural Earth coastlines; a twin-engine plane flies from Bandung to Surabaya (24 June 1937), a red warning
pulses there (the long-distance flying instruments failed again) and it flies back to Bandung (25 June; This Day in Aviation).
skema_lenyap: a propeller airliner on a clear sky (Pixabay 3636061, a Lockheed Super Constellation, not Earhart's Electra; its tail
logos painted out), small enough to fit the frame on a sky extended from the photo. It fades away on "lenyap"; render.py adds the night grade.
skema_surat: a letter sheet over a stack of old letters (Pixabay 447578). The letterhead follows the Sotheby's lot of Fred Noonan's
letter ("Grand Hotel Preanger, Bandoeng, Java", 23 June 1937); the handwriting is made-up squiggles, not his words.
A highlighter marks the hotel on "ditulis" and Bandoeng on "Bandung".
Event times are seconds from the start of each shot, read off `render.py 31 plan`.
"""
import json, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, BOLD, YELLOW, WHITE, ramp, pop, layer, down, sc, fade, put, dashed, glow_sprite, encode
from skema13 import navy
from skema17 import ring, label
from skema18 import clip_ring
from skema27 import along, dot_sprite
from skema30 import photo

N = {"rute": 112, "lenyap": 80, "surat": 154}
GEO = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in N else "geo"
RED = (232, 44, 40)
SERIF, SERIF_BOLD = "/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf", "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
SERIF_IT = "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"


# ---------- skema_rute ----------
K, LON0, LAT0, CY = 110, 110.18, -7.3, 860  # all of Java across the frame
BANDUNG, SURABAYA = (107.61, -6.91), (112.75, -7.25)


def xy(lon, lat):
    return 540 + (lon - LON0) * K, CY + (LAT0 - lat) * K


def land():
    """the rings near Java, and Java itself (the biggest ring)"""
    rings = []
    for f in json.load(open(os.path.join(GEO, "ne_10m_land.geojson")))["features"]:
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            r = poly[0]
            lo, la = [p[0] for p in r], [p[1] for p in r]
            if max(lo) < 103 or min(lo) > 117 or max(la) < -12 or min(la) > 2:
                continue
            c = clip_ring(r, 103, -12, 117, 2)
            if len(c) > 2 and max(p[0] for p in c) > 106.2:  # not Sumatra, whose tip would poke in at the top left
                rings.append(c)
    java = max((r for r in rings if 105 < sum(p[0] for p in r) / len(r) < 115 and -8.5 < sum(p[1] for p in r) / len(r) < -6), key=len)
    return rings, java


def bezier(p0, c, p2, n=80):
    return [((1 - u) ** 2 * p0[0] + 2 * u * (1 - u) * c[0] + u * u * p2[0], (1 - u) ** 2 * p0[1] + 2 * u * (1 - u) * c[1] + u * u * p2[1])
            for u in (k / n for k in range(n + 1))]


def plane_sprite(L=70):
    """a twin-engine, twin-tail airliner seen from above, nose to the right, with a dark rim; 2x sprite centred on the plane"""
    n = round(1.6 * L * S)
    sp = Image.new("RGBA", (n, n))
    d = ImageDraw.Draw(sp)
    c = n / 2

    def P(x, y):
        return (c + x * L * S, c + y * L * S)
    body, dark = (246, 246, 240, 255), (70, 76, 92, 255)
    d.polygon([P(0.15, -0.07), P(0.07, -0.72), P(-0.01, -0.72), P(-0.07, -0.07), P(-0.07, 0.07), P(-0.01, 0.72), P(0.07, 0.72),
               P(0.15, 0.07)], fill=body)  # the wing
    d.polygon([P(-0.35, -0.04), P(-0.41, -0.25), P(-0.48, -0.25), P(-0.46, 0), P(-0.48, 0.25), P(-0.41, 0.25), P(-0.35, 0.04)], fill=body)
    d.ellipse([*P(-0.5, -0.07), *P(0.53, 0.07)], fill=body)  # the fuselage
    for s in (-1, 1):
        y = s * 0.25
        d.rounded_rectangle([*P(0.0, y - 0.045), *P(0.29, y + 0.045)], radius=0.04 * L * S, fill=body)  # engines
        d.line([P(0.31, y - 0.11), P(0.31, y + 0.11)], fill=dark, width=2 * S)  # the propeller disc, edge on
        d.rounded_rectangle([*P(-0.5, y - 0.025), *P(-0.39, y + 0.025)], radius=0.02 * L * S, fill=dark)  # the twin fins
    d.ellipse([*P(0.36, -0.035), *P(0.47, 0.035)], fill=(150, 190, 230, 255))  # cockpit glass
    rim = Image.new("RGBA", sp.size, (24, 30, 44, 0))
    rim.putalpha(sp.getchannel("A").filter(ImageFilter.MaxFilter(5)))
    rim.alpha_composite(sp)
    return rim


def warn_sprite(r=30):
    """a red disc with a white "!" on a red glow; 2x sprite"""
    sp = glow_sprite(r, RED)
    d = ImageDraw.Draw(sp)
    c = 2 * r * S
    d.ellipse([c - r * S, c - r * S, c + r * S, c + r * S], fill=RED + (255,), outline=(255, 255, 255, 255), width=4 * S)
    f = ImageFont.truetype(BOLD, round(1.4 * r) * S)
    b = f.getbbox("!")
    d.text((c - (b[0] + b[2]) / 2, c - (b[1] + b[3]) / 2), "!", font=f, fill=(255, 255, 255, 255))
    return sp


def heading(pts, s):
    a, b = along(pts, max(0.0, s - 2)), along(pts, s + 2)
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def rute(times):
    rings, java = land()
    bg = navy(540, CY, [xy(lon, 0)[0] for lon in range(106, 116)], [xy(0, lat)[1] for lat in (-6, -7, -8, -9, -10)])
    base = layer()
    d = ImageDraw.Draw(base)
    for r in rings:
        d.polygon(sc([xy(*p) for p in r]), fill=(222, 200, 150, 255) if r is java else (150, 134, 102, 255),
                  outline=(120, 100, 68, 255) if r is java else (96, 84, 62, 255))
    base = down(base)
    # Borneo and Sumatra fade out toward the top: the title sits there
    g = np.clip((np.arange(H, dtype=np.float32) - 540) / 160, 0, 1)
    base.putalpha(Image.fromarray((np.asarray(base.getchannel("A"), np.float32) * g[:, None]).astype(np.uint8)))
    pb, ps = xy(*BANDUNG), xy(*SURABAYA)
    mid = ((pb[0] + ps[0]) / 2, (pb[1] + ps[1]) / 2)
    out_pts = bezier(pb, (mid[0], mid[1] - 150), ps)  # there: an arc over the north
    back_pts = bezier(ps, (mid[0], mid[1] + 100), pb)  # and back: a flatter arc to the south, clear of the watermark
    L1 = sum(math.dist(a, b) for a, b in zip(out_pts, out_pts[1:]))
    L2 = sum(math.dist(a, b) for a, b in zip(back_pts, back_pts[1:]))
    plane, warn = plane_sprite(), warn_sprite()
    dot_b, dot_s = dot_sprite(11, (250, 250, 250)), dot_sprite(11, (250, 250, 250))
    lab_b = label([("BANDUNG", 34, WHITE, True)])
    lab_s = label([("SURABAYA", 34, WHITE, True)])
    h_out, h_back = heading(out_pts, L1 - 3), heading(back_pts, 3)
    # sempat 0.05, ke 0.32, Surabaya 0.43, bermasalah 1.43, lagi 1.90, balik 2.63, lagi. 3.01; the shot ends at 3.57
    t_go, t_there, t_bad, t_turn, t_back, t_home = 0.14, 1.3, 1.43, 2.3, 2.63, 3.38
    out = []
    for t in times:
        im = bg.copy()
        im.alpha_composite(fade(base, ramp(t, 0.0, 0.12)) if t < 0.12 else base)
        top = layer()
        d = ImageDraw.Draw(top)
        s1 = L1 * ramp(t, t_go, t_there)
        s2 = L2 * ramp(t, t_back, t_home)
        if s1 > 4:
            dashed(d, out_pts, fill=(255, 255, 255, 235), width=5, dash=18, gap=12, upto=s1 - 30 * (t < t_there + 0.1))
        if s2 > 4:
            dashed(d, back_pts, fill=YELLOW + (255,), width=5, dash=18, gap=12, upto=s2 - 30 * (t < t_home + 0.1))
        if t_bad <= t < 2.62:  # the trouble at Surabaya: red rings pulse out
            for k in range(2):
                u = ((t - t_bad) / 0.6 + k / 2) % 1
                ring(d, *ps, 16 + 50 * u, RED, 235 * (1 - u) ** 1.3 * (1 - ramp(t, 2.4, 2.62)), w=5)
        if t >= t_home:  # home again: yellow rings at Bandung
            for k in range(2):
                u = ((t - t_home) / 0.6 + k / 2) % 1
                if t - t_home > k * 0.3:
                    ring(d, *pb, 16 + 50 * u, YELLOW, 235 * (1 - u) ** 1.3, w=5)
        put(top, dot_b, *pb, scale=pop(t, 0.0))
        put(top, dot_s, *ps, scale=pop(t, 0.38))
        put(top, lab_b, pb[0] - 95, pb[1] - 62, a=ramp(t, 0.06, 0.18), scale=pop(t, 0.06))
        put(top, lab_s, ps[0] + 115, ps[1] + 50, a=ramp(t, 0.43, 0.55), scale=pop(t, 0.43))
        # where the plane is and where it points
        if t < t_back:
            x, y = along(out_pts, s1)
            hd = heading(out_pts, min(max(s1, 3), L1 - 3))
            if t > t_turn:  # turning round for the way back
                hd = h_out + (h_back - h_out) * ramp(t, t_turn, t_back)
            hd += 7 * math.sin(2 * math.pi * (t - t_bad) / 0.32) * (t_bad < t < t_turn) * (1 - ramp(t, 2.0, t_turn))  # shaking
        else:
            x, y = along(back_pts, s2)
            hd = heading(back_pts, min(max(s2, 3), L2 - 3))
        p = plane.rotate(-hd, resample=Image.BICUBIC)
        sh = Image.new("RGBA", p.size, (0, 0, 0, 0))
        sh.putalpha(p.getchannel("A").point(lambda v: v * 0.45).filter(ImageFilter.GaussianBlur(4 * S)))
        lift = 1 + 0.08 * (math.sin(math.pi * ramp(t, t_go, t_there)) + math.sin(math.pi * ramp(t, t_back, t_home)))  # bigger in the air
        sp = pop(t, 0.02) * lift
        put(top, sh, x + 9 * lift, y + 13 * lift, a=ramp(t, 0.02, 0.2), scale=sp)
        put(top, p, x, y, scale=sp)
        if t_bad <= t < 2.7:
            put(top, warn, ps[0], ps[1] - 76, a=1 - ramp(t, 2.5, 2.7), scale=pop(t, t_bad) * (1 + 0.07 * math.sin(2 * math.pi * (t - t_bad) / 0.5)))
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_lenyap ----------
PLANE_BOX = (230, 240, 1190, 600)  # the plane in 3636061 (x0, y0, x1, y1), with room for its soft edge
LOGOS = [((1126, 396, 1158, 442), 108), ((1010, 438, 1039, 470), 108), ((1113, 460, 1162, 484), 70)]  # the two "B" tail logos
# and the registration, with the brightness below which a pixel counts as paint (the fins are in shade, about 120-140)
KP, PLANE_AT = 0.9, (540, 860)  # the plane's scale in the frame and where the centre of PLANE_BOX goes


def heal(a, box, bad):
    """fill the `bad` pixels (a mask over box) of the float image a from the pixels around them (Laplace diffusion)"""
    x0, y0, x1, y1 = box
    m = np.asarray(Image.fromarray(bad.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(3))) > 0
    p = 2
    blk = a[y0 - p:y1 + p, x0 - p:x1 + p]
    hole = np.zeros(blk.shape[:2], bool)
    hole[p:-p, p:-p] = m
    v = blk.copy()
    v[hole] = blk[~hole].mean(0)
    for _ in range(400):
        avg = (np.roll(v, 1, 0) + np.roll(v, -1, 0) + np.roll(v, 1, 1) + np.roll(v, -1, 1)) / 4
        v[hole] = avg[hole]
    a[y0 - p:y1 + p, x0 - p:x1 + p] = v


def soft(v, lo, hi):
    """squeeze v into (lo, hi) without a kink: the identity in the middle, tanh toward the ends"""
    c, r = (lo + hi) / 2, (hi - lo) / 2
    return c + r * np.tanh((v - c) / r)


def sky_fit(a, sky):
    """per-channel quadratic surface fitted to the sky pixels; returns a function of (x, y) arrays"""
    ys, xs = np.nonzero(sky)
    pick = np.random.default_rng(31).choice(len(xs), min(len(xs), 60000), replace=False)
    xs, ys = xs[pick].astype(np.float64) / 1000, ys[pick].astype(np.float64) / 1000
    A = np.stack([np.ones_like(xs), xs, ys, xs * xs, xs * ys, ys * ys], 1)
    coef = [np.linalg.lstsq(A, a[(ys * 1000).round().astype(int), (xs * 1000).round().astype(int), c].astype(np.float64), rcond=None)[0]
            for c in range(3)]

    def f(x, y):
        x, y = x / 1000, y / 1000
        B = np.stack([np.ones_like(x), x, y, x * x, x * y, y * y], -1)
        return np.stack([B @ k for k in coef], -1)
    return f


def lenyap_layers():
    im = Image.open("img/3636061.jpg").convert("RGB")
    a = np.asarray(im, np.float32)
    sky = (a[..., 2] - a[..., 0] > 95) & (a[..., 2] > 150)
    model = sky_fit(a, sky)
    for (x0, y0, x1, y1), dark in LOGOS:  # paint the tail logos out with the fin around them
        heal(a, (x0, y0, x1, y1), a[y0:y1, x0:x1].mean(-1) < dark)
    x0, y0, x1, y1 = PLANE_BOX
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float64)
    m = model(xx, yy)
    crop = a[y0:y1, x0:x1]
    diff = np.abs(crop - m).max(-1)
    alpha = np.clip((diff - 14) / 22, 0, 1)
    al = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3))
    pl = Image.fromarray(crop.astype(np.uint8)).convert("RGBA")
    pl.putalpha(al)
    pl = pl.resize((round(pl.width * KP * S), round(pl.height * KP * S)), Image.LANCZOS)  # a 2x sprite
    # the sky of the whole frame from the fitted surface: frame (X, Y) -> photo (x, y), rows clamped to the photo
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    Y, X = np.mgrid[0:H, 0:W].astype(np.float64)
    px, py = cx + (X - PLANE_AT[0]) / KP, cy + (Y - PLANE_AT[1]) / KP
    sky_im = model(soft(px, 0, im.width - 1), soft(py, 0, im.height - 1))  # beyond the photo the sky levels off smoothly
    sky_im = Image.fromarray(np.clip(sky_im, 0, 255).astype(np.uint8)).convert("RGBA")
    return sky_im, pl


def lenyap(times):
    sky, pl = lenyap_layers()
    # Lalu 0.05, ia 0.49, lenyap 0.72, di 1.22, atas 1.33, Pasifik. 1.57; the shot ends at 2.53
    out = []
    for t in times:
        im = sky.copy()
        a = 1 - ramp(t, 0.74, 1.62)
        if a > 0.01:
            top = layer()
            p = pl
            blur = 5 * ramp(t, 0.74, 1.62)
            if blur > 0.2:
                p = pl.filter(ImageFilter.GaussianBlur(blur * S))
            k = 1 - 0.05 * t / 2.6  # it draws away, nose first (to the left)
            put(top, p, PLANE_AT[0] - 46 * t / 2.6, PLANE_AT[1] - 8 * t / 2.6, a=a, scale=k)
            im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_surat ----------
SHEET = (800, 480)  # the letter (1x); its top-left corner sits at SHEET_AT before the tilt
SHEET_AT, TILT = (140, 682), -1.5
INK, PRINT = (34, 40, 86), (26, 50, 98)


def spaced(d, xy0, text, font, fill, track, anchor_mid=True):
    """text with extra letter spacing (`track` px at 2x), centred on xy0 when anchor_mid; returns its (x0, x1)"""
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    x = xy0[0] - total / 2 if anchor_mid else xy0[0]
    x0 = x
    for ch, w in zip(text, widths):
        d.text((x, xy0[1]), ch, font=font, fill=fill, anchor="ls")
        x += w + track
    return x0, x0 + total


def scribble_line(d, x0, base, width, rng):
    """a line of made-up cursive at 2x: words of looped strokes with a slant"""
    adv, xh = 11.0 * S, 8.5 * S
    x = x0
    while True:
        n = rng.randint(2, 8)
        if x + n * adv > x0 + width:
            break
        kinds = [rng.choices((1.0, 2.3, -1.5), (0.72, 0.18, 0.1))[0] for _ in range(n)]
        jit = rng.uniform(-1.2, 1.2) * S
        pts = []
        for i in range(n * 14 + 1):
            u = i / 14
            k = min(int(u), n - 1)
            f = u - k
            amp = kinds[k] * xh
            r = (0.42 if kinds[k] != 1.0 else 0.22) * adv
            y = base + jit - amp * (1 - math.cos(2 * math.pi * f)) / 2
            px = x + adv * u - r * math.sin(2 * math.pi * f) + 0.32 * (base - y)
            pts.append((px, y))
        d.line(pts, fill=INK + (225,), width=round(2.3 * S), joint="curve")
        x += n * adv + rng.uniform(0.9, 1.4) * adv
        if rng.random() < 0.12:  # a dotted i or a crossed t now and then
            d.ellipse([x - 1.3 * adv - 2 * S, base - 2.2 * xh - 2 * S, x - 1.3 * adv + 2 * S, base - 2.2 * xh + 2 * S], fill=INK + (225,))


def sheet_image(hl1, hl2):
    """the letter at 2x, unrotated; hl1 and hl2 (0-1) are how far the highlighter has run over the hotel name and over BANDOENG"""
    w, h = SHEET[0] * S, SHEET[1] * S
    rng = np.random.default_rng(5)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    edge = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)) / (40 * S)
    age = 1 - 0.13 * np.clip(1 - edge, 0, 1) ** 2  # darker, older edges
    grain = rng.normal(0, 4.5, (h // 4, w // 4)).astype(np.float32)
    grain = np.asarray(Image.fromarray(grain).resize((w, h), Image.BILINEAR))
    paper = (np.array([240, 229, 202], np.float32) * age[..., None] + grain[..., None]).clip(0, 255).astype(np.uint8)
    sh = Image.fromarray(paper).convert("RGBA")
    d = ImageDraw.Draw(sh)
    crease = Image.new("RGBA", sh.size)
    dc = ImageDraw.Draw(crease)
    for fy in (h / 3, 2 * h / 3):  # folded in three: a soft shadow and a light edge
        dc.line([(0, fy), (w, fy)], fill=(120, 100, 70, 40), width=3 * S)
        dc.line([(0, fy + 3 * S), (w, fy + 3 * S)], fill=(255, 252, 240, 45), width=2 * S)
    sh.alpha_composite(crease.filter(ImageFilter.GaussianBlur(1.5 * S)))
    f1, f2, f3 = ImageFont.truetype(SERIF_BOLD, 45 * S), ImageFont.truetype(SERIF, 25 * S), ImageFont.truetype(SERIF_IT, 29 * S)
    mx = w / 2
    hl = Image.new("RGBA", sh.size)
    dh = ImageDraw.Draw(hl)
    t1 = Image.new("RGBA", sh.size)
    dt = ImageDraw.Draw(t1)
    a0, a1 = spaced(dt, (mx, 74 * S), "GRAND HOTEL PREANGER", f1, PRINT + (255,), 3 * S)
    b0, b1 = spaced(dt, (mx, 113 * S), "BANDOENG, JAVA", f2, PRINT + (255,), 7 * S)
    bw = f2.getlength("BANDOENG") + 7 * S * 7  # BANDOENG alone, with its tracking
    for yl, wd in ((131, 3), (137, 1)):
        dt.line([(mx - 250 * S, yl * S), (mx + 250 * S, yl * S)], fill=PRINT + (255,), width=wd * S)
    dt.text((w - 64 * S, 188 * S), "23 June 1937", font=f3, fill=INK + (235,), anchor="rs")
    if hl1 > 0.01:
        dh.rounded_rectangle([a0 - 10 * S, 34 * S, a0 - 10 * S + (a1 - a0 + 20 * S) * hl1, 86 * S], radius=6 * S, fill=YELLOW + (150,))
    if hl2 > 0.01:
        dh.rounded_rectangle([b0 - 8 * S, 90 * S, b0 - 8 * S + (bw + 16 * S) * hl2, 121 * S], radius=5 * S, fill=YELLOW + (165,))
    r = random.Random(1937)
    for k, yb in enumerate((214, 248, 324, 358, 392, 426)):  # a paragraph break where the watermark crosses the sheet
        lead = 92 if k in (0, 2) else 64
        width = (600 if k in (1, 5) else 672 - (lead - 64)) * r.uniform(0.82, 1.0)
        scribble_line(dt, lead * S, yb * S, width * S, r)
    # the highlighter goes on the paper under the ink: multiply it in
    if hl1 > 0.01 or hl2 > 0.01:
        p = np.asarray(sh.convert("RGB"), np.float32)
        ha = np.asarray(hl, np.float32)
        k = ha[..., 3:] / 255
        p = p * (1 - k) + p * ha[..., :3] / 255 * k
        sh = Image.fromarray(p.clip(0, 255).astype(np.uint8)).convert("RGBA")
    sh.alpha_composite(t1)
    return sh


def surat(times):
    base = photo("img/447578.jpg", 0.5)
    base = Image.fromarray((np.asarray(base.convert("RGB"), np.float32) * 0.62).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5)).convert("RGBA")
    cache = {}

    def sheet_at(h1, h2):
        key = (round(h1, 2), round(h2, 2))
        if key not in cache:
            sh = sheet_image(*key)
            pad = 40 * S  # room for the shadow
            sp = Image.new("RGBA", (sh.width + 2 * pad, sh.height + 2 * pad))
            shadow = Image.new("RGBA", sp.size)
            ImageDraw.Draw(shadow).rectangle([pad + 8 * S, pad + 14 * S, pad + sh.width + 8 * S, pad + sh.height + 14 * S], fill=(0, 0, 0, 150))
            sp.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14 * S)))
            sp.alpha_composite(sh, (pad, pad))
            cache[key] = sp
        return cache[key]
    cx, cy = SHEET_AT[0] + SHEET[0] / 2, SHEET_AT[1] + SHEET[1] / 2
    # Dan 0.04, salah 0.29, satu 0.60, surat 0.90, terakhir 1.14, navigatornya... 1.52, ditulis 2.87, di 3.29, sebuah 3.37,
    # hotel 3.87, di 4.14, Bandung. 4.37; the shot ends at 5.0
    out = []
    for t in times:
        im = base.copy()
        u = ramp(t, 0.22, 0.86)
        if u > 0:
            sp = sheet_at(ramp(t, 2.87, 3.2), ramp(t, 4.35, 4.62))
            ang = TILT - 7 * (1 - u)
            sp = sp.rotate(-ang, resample=Image.BICUBIC, expand=True)
            k = 1 + 0.035 * ramp(t, 0.86, 5.0)  # a slow push toward the letterhead
            top = layer()
            put(top, sp, cx, cy + 520 * (1 - u) - 6 * ramp(t, 0.86, 5.0), scale=k)
            im.alpha_composite(down(top))
        out.append(im)
    return out


OUT = {k: f"clips/skema_{k}.mp4" for k in N}

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
            encode(globals()[name]([i / FPS for i in range(N[name])]), OUT[name])
