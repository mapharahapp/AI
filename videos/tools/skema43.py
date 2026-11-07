"""Stills and schematic animations for Titik Heran #43 (run in the episode work dir after
`dl.py i:1715020 i:559641 i:11612 i:11180 i:693224 i:5862911`; writes img/hook43.jpg, img/hook43c.jpg, clips/skema_swift.mp4,
clips/skema_orbit.mp4 and clips/skema_link.mp4).
Pixabay + skema only: Pixabay has no photo of NASA's Swift observatory or of Katalyst's LINK robot, so both are drawn from
NASA's descriptions (shapes approximate, labelled "skema" by render.py). Numbers drawn here are only the checked ones:
launch 2004, end 2026, the planned 2 years, 275 km (20 Oct 2026), 12-15 km (how close LINK got), 25 Sep and 4 Nov 2026.
usage: python3 skema43.py [prep|swift|orbit|link ...] [--sheet out.jpg t1,t2,...]
prep: img/hook43.jpg and img/hook43c.jpg frame Pixabay 1715020 (a fiery streak over a riverside town at night, "ilustrasi")
  bigger than kind b would: the whole streak entering from the top left, then closer on its bright head; edges continued,
  midtones lifted. img/11180v.jpg sets Cassiopeia A (11180) on a black frame with feathered edges.
skema_swift: Swift (BAT box with its coded mask, XRT and UVOT tubes, gold body, two solar wings) drifting above the Earth's
  rim on a faint dashed orbit; a 2004-2026 bar whose first 2 years are marked "RENCANA: 2 TAHUN", filled to 2026 by a year
  counter.
skema_orbit: the Earth with Swift spiralling lower; the active Sun pulses and throws arcs, the glow of upper air thickens,
  an engine icon gets a red cross on "pendorong" and the last orbit is labelled 275 km (20 Okt 2026).
skema_link: LINK comes in from the right and stops at the 12-15 km mark, tumbles with question marks on "hilang", dives into
  the air with a tail of fire on "jatuh"; calendar cards LINK 25 SEP 2026 / SWIFT 4 NOV 2026.
Event times are seconds from the start of each clip, read off `render.py 43 plan`: skema_swift starts at 10,30 ("bertahan"
0,38, "dua puluh dua" 1,41-2,28), skema_orbit at 16,23 ("ia" 1,18, "mesin" 1,81, "pendorong" 2,05), skema_link at 23,00
("robotnya" 0,58, "hilang" 1,06, "dan" 2,16, "jatuh" 2,56, "duluan" 2,84).
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, text_sprite, encode
from skema35 import sheet
from skema36 import reframe
from skema37 import noise, to_img, put1

N = {"swift": 101, "orbit": 101, "link": 121}  # each clip runs ~0,3 s past its shot
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
RED, ORANGE, SKY = (232, 44, 40), (255, 138, 28), (120, 190, 255)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def wanted(i, times):
    return times is None or any(abs(i / FPS - x) < 0.5 / FPS for x in times)


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


# ---------- prep: the hook stills ----------
def lift(path, gamma=1.3):
    """a night photo's midtones lifted (YAVG ~51 -> ~65), so the hook does not read as a black frame"""
    a = np.asarray(Image.open(path).convert("RGB"), np.float32) / 255
    Image.fromarray((255 * a ** (1 / gamma)).clip(0, 255).astype(np.uint8)).save(path, quality=95)


def on_black(src, out, cy=880, feather=70):
    """a photo shot on black (Cassiopeia A) set 1080 wide on a black frame, its edges feathered into the black: kind b would
    put it on a blurred copy of itself and show the band's edges"""
    im = Image.open(src).convert("RGB")
    im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    a = np.asarray(im, np.float32)
    h = a.shape[0]
    yy, xx = np.mgrid[0:h, 0:W].astype(np.float32)
    m = np.clip(np.minimum.reduce([xx, W - 1 - xx, yy, h - 1 - yy]) / feather, 0, 1)
    m = m * m * (3 - 2 * m)
    f = np.zeros((H, W, 3), np.float32)
    y0 = cy - h // 2
    f[y0:y0 + h] = a * m[..., None]
    Image.fromarray(f.clip(0, 255).astype(np.uint8)).save(out, quality=95)
    print(out)


def prep():
    # the streak's head (795, 430 in the 1280x720 photo) lands right of centre at y ~1000, the streak enters top left
    reframe("img/1715020.jpg", 1.45, 380, 377, "img/hook43.jpg")
    # closer: the head near the frame centre (y ~900)
    reframe("img/1715020.jpg", 2.0, 1050, 40, "img/hook43c.jpg")
    for p in ("img/hook43.jpg", "img/hook43c.jpg"):
        lift(p)
    on_black("img/11180.jpg", "img/11180v.jpg")


# ---------- shared drawing ----------
def space_bg(seed=3):
    """deep navy with the faint skema grid and a sprinkle of stars"""
    v = (YY / H)[..., None]
    a = np.array([12, 30, 64], np.float32) * (1 - v) + np.array([4, 11, 28], np.float32) * v
    im = to_img(a).convert("RGBA")
    lay = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(lay)
    for x in range(0, W + 1, 135):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 13), width=2)
    for y in range(-45, H + 1, 135):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 13), width=2)
    rng = np.random.default_rng(seed)
    for _ in range(240):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.choice([0.8, 1.0, 1.2, 1.8])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(rng.uniform(50, 190))))
    im.alpha_composite(lay)
    return im


class Earth:
    """a shaded ocean-blue disc lit from the upper left, cloud bands that drift sideways (the planet turning) and a glow of
    air on the rim whose thickness can grow"""

    def __init__(self, cx, cy, R, seed=5, dark_below=None):
        self.cx, self.cy, self.R = cx, cy, R
        y0, y1 = max(0, int(cy - R - 300)), min(H, int(cy + R + 300))
        self.y0, self.y1 = y0, y1
        yy, xx = YY[y0:y1] - cy, XX[y0:y1] - cx
        r = np.sqrt(xx ** 2 + yy ** 2)
        self.r = r
        self.inside = np.clip((R - r) / 1.5 + 0.5, 0, 1)
        nz = np.sqrt(np.clip(1 - (r / R) ** 2, 0, 1))
        lit = np.clip(0.18 + 0.82 * np.clip((-xx / R) * 0.30 + (-yy / R) * 0.45 + nz * 0.80, 0, 1), 0, 1)
        if dark_below is not None:  # a big rim: the planet falls into shade further down the frame
            lit = lit * np.clip(1.15 - (YY[y0:y1] - dark_below) / 800, 0.42, 1)
        deep, shallow = np.array([10, 38, 96], np.float32), np.array([38, 112, 196], np.float32)
        self.ocean = deep + (shallow - deep) * lit[..., None]
        self.lit = lit
        h, w = y1 - y0, W + 600
        n = noise((h, w // 3 + 2), [(150, 0.45), (60, 0.35), (24, 0.2)], seed)
        n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
        band = 0.5 + 0.5 * np.sin(np.arange(h)[:, None] / 41.0 + n * 5.0)  # streaky, like cloud bands seen from orbit
        c = np.clip((n * 0.72 + band * 0.28 - 0.53) * 2.6, 0, 1)
        c = np.asarray(Image.fromarray((c * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
        self.cloud = c * 0.8

    def draw(self, im, shift=0.0, air=18.0, air_a=1.0):
        a = np.asarray(im, np.float32).copy()
        y0, y1 = self.y0, self.y1
        sh = int(shift) % 600
        cl = self.cloud[:, sh:sh + W] * self.lit
        body = self.ocean * (1 - cl[..., None]) + np.array([235, 240, 248], np.float32) * cl[..., None] * (0.35 + 0.65 * self.lit[..., None])
        ins = self.inside[..., None]
        reg = a[y0:y1, :, :3] * (1 - ins) + body * ins
        # air: a soft light-blue rim, thicker and brighter when `air` grows, inside a little and mostly outside
        d = self.r - self.R
        g = np.exp(-np.clip(d, 0, None) / max(air, 1.0)) * np.clip((d + 6) / 6, 0, 1) * np.clip(3 - d / max(air, 1.0), 0, 1)
        g = g * (0.55 + 0.45 * np.clip(self.lit * 1.6, 0, 1)) * air_a
        reg = reg * (1 - 0.85 * g[..., None]) + np.array(SKY, np.float32) * 0.85 * g[..., None] * 1.15
        a[y0:y1, :, :3] = reg
        return to_img(a[..., :3]).convert("RGBA")


def cylinder(d, k, ox, oy, x0, x1, y0, y1, base=(232, 234, 238), hood=(44, 47, 56)):
    """a vertical tube with cylinder shading, a few darker rings and a dark sun hood on top"""
    n = max(2, int((x1 - x0) * k))
    for j in range(n):
        u = j / (n - 1)
        f = 0.62 + 0.5 * math.sin(math.pi * (0.15 + 0.7 * u)) - 0.12 * u
        c = tuple(int(min(255, ch * f)) for ch in base)
        x = (ox + x0) * k + j
        d.line([(x, (oy + y0) * k), (x, (oy + y1) * k)], fill=c + (255,), width=1)
    for yr in np.linspace(y0 + 40, y1 - 30, 4):
        d.rectangle([(ox + x0) * k, (oy + yr) * k, (ox + x1) * k, (oy + yr + 4) * k], fill=(150, 154, 162, 255))
    d.rectangle([(ox + x0 - 3) * k, (oy + y0) * k, (ox + x1 + 3) * k, (oy + y0 + 22) * k], fill=hood + (255,))


def solar_wing(d, k, ox, oy, x0, x1, y0, y1):
    d.rectangle([(ox + x0) * k, (oy + y0) * k, (ox + x1) * k, (oy + y1) * k], fill=(26, 50, 122, 255))
    for gx in np.arange(x0 + 22, x1 - 4, 22):
        d.line([((ox + gx) * k, (oy + y0) * k), ((ox + gx) * k, (oy + y1) * k)], fill=(92, 132, 214, 255), width=max(1, int(1.5 * k)))
    for gy in np.linspace(y0, y1, 5)[1:-1]:
        d.line([((ox + x0) * k, (oy + gy) * k), ((ox + x1) * k, (oy + gy) * k)], fill=(92, 132, 214, 255), width=max(1, int(1.5 * k)))
    d.rectangle([(ox + x0) * k, (oy + y0) * k, (ox + x1) * k, (oy + y1) * k], outline=(206, 210, 220, 255), width=int(4 * k))


def soft_edge(sp, r=10, a=0.35):
    """a faint glow round a sprite, so the drawing separates from the dark sky"""
    g = Image.new("RGBA", sp.size, (200, 225, 255, 0))
    g.putalpha(sp.getchannel("A").filter(ImageFilter.GaussianBlur(r * S)).point(lambda v: int(v * a)))
    g.alpha_composite(sp)
    return g


def swift_sprite():
    """Swift, side view (shape approximate): the wide BAT box with its coded mask on top, the long XRT and the shorter UVOT
    tube beside it, the gold-foil body and two solar wings; 2x sprite at its natural size (~690 px wide at 1x)"""
    k, w, h = S, 760, 420
    ox, oy = w / 2, 255
    sp = Image.new("RGBA", (w * k, h * k))
    d = ImageDraw.Draw(sp)
    P = lambda pts: [((ox + x) * k, (oy + y) * k) for x, y in pts]
    for sg in (-1, 1):  # booms and wings
        a, b = sorted((sg * 70, sg * 128))
        d.rectangle([(ox + a) * k, (oy + 14) * k, (ox + b) * k, (oy + 26) * k], fill=(176, 180, 190, 255))
        a, b = sorted((sg * 125, sg * 345))
        solar_wing(d, k, ox, oy, a, b, -38, 78)
    # gold-foil body with wrinkle lines and a silver base
    d.rectangle(P([(-78, -22), (78, 92)]), fill=(198, 150, 56, 255))
    rng = np.random.default_rng(4)
    for x in np.arange(-70, 74, 13):
        d.line(P([(x + rng.uniform(-3, 3), -18), (x + rng.uniform(-4, 4), 72)]), fill=(150, 108, 34, 255), width=2 * k)
    d.rectangle(P([(-78, 72), (78, 92)]), fill=(196, 200, 208, 255))
    # BAT: the wide box, darker on its left face, the coded mask (random black and white cells) on its rim
    d.polygon(P([(-104, -22), (104, -22), (166, -118), (-166, -118)]), fill=(66, 70, 82, 255))
    d.polygon(P([(-104, -22), (-40, -22), (-60, -118), (-166, -118)]), fill=(54, 57, 68, 255))
    d.line(P([(-166, -118), (166, -118)]), fill=(150, 156, 170, 255), width=3 * k)
    d.polygon(P([(-166, -118), (166, -118), (154, -138), (-154, -138)]), fill=(214, 214, 218, 255))
    for yy in np.arange(-136, -119, 6):
        span = 154 + (yy + 138) / 20 * 12
        for xx in np.arange(-span, span - 5, 7):
            if rng.random() < 0.5:
                d.rectangle(P([(xx, yy), (xx + 6, yy + 5)]), fill=(22, 22, 26, 255))
    # the narrow-field telescopes beside the box
    cylinder(d, k, ox, oy, 112, 152, -226, 88)            # XRT, the long one
    cylinder(d, k, ox, oy, -156, -122, -176, 88)          # UVOT
    return soft_edge(sp)


def link_sprite():
    """LINK, the rescue robot (shape approximate): a small gold box with one solar wing and three capture arms in front;
    2x sprite (~250 px wide at 1x), the arms pointing left"""
    k, w, h = S, 300, 170
    ox, oy = 150, 85
    sp = Image.new("RGBA", (w * k, h * k))
    d = ImageDraw.Draw(sp)
    P = lambda pts: [((ox + x) * k, (oy + y) * k) for x, y in pts]
    d.rectangle(P([(32, -4), (58, 4)]), fill=(176, 180, 190, 255))
    solar_wing(d, k, ox, oy, 56, 140, -30, 30)
    d.rectangle(P([(-34, -34), (34, 34)]), fill=(204, 156, 60, 255))
    for x in np.arange(-28, 30, 11):
        d.line(P([(x, -30), (x + 2, 30)]), fill=(150, 108, 34, 255), width=2 * k)
    d.rectangle(P([(-34, 26), (34, 34)]), fill=(196, 200, 208, 255))
    for yo in (-24, 0, 24):  # three arms with claws
        d.line(P([(-34, yo * 0.6), (-92, yo)]), fill=(214, 218, 226, 255), width=5 * k)
        d.line(P([(-92, yo), (-110, yo - 9)]), fill=(214, 218, 226, 255), width=4 * k)
        d.line(P([(-92, yo), (-110, yo + 9)]), fill=(214, 218, 226, 255), width=4 * k)
    return soft_edge(sp, 8)


def rotated(sp, ang):
    return sp if abs(ang) < 0.05 else sp.rotate(ang, resample=Image.BICUBIC, expand=True)


def label(text, size=34, col=WHITE, bold=True, bg=(8, 18, 40, 200), pad=(18, 10)):
    """a pill label, 2x sprite"""
    f = ImageFont.truetype(XB if bold else MED, size * S)
    x0, y0, x1, y1 = f.getbbox(text)
    w, h = x1 - x0 + 2 * pad[0] * S, y1 - y0 + 2 * pad[1] * S
    sp = Image.new("RGBA", (w + 20 * S, h + 20 * S))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([10 * S, 10 * S, 10 * S + w, 10 * S + h], radius=h // 2, fill=bg)
    d.text((10 * S + pad[0] * S - x0, 10 * S + pad[1] * S - y0), text, font=f, fill=col + (255,))
    return sp


def dashed_arc(d, cx, cy, r, a0, a1, fill, width=3, dash=14, gap=12):
    """dashes along a circle arc (degrees, image coordinates), 1x"""
    L = math.radians(a1 - a0) * r
    n = int(L / (dash + gap)) + 1
    for i in range(n):
        s0 = a0 + (a1 - a0) * (i * (dash + gap)) / L
        s1 = a0 + (a1 - a0) * min(L, i * (dash + gap) + dash) / L
        d.arc([cx - r, cy - r, cx + r, cy + r], s0, s1, fill=fill, width=width)


# ---------- skema_swift ----------
def skema_swift(times=None):
    bg = space_bg(3)
    earth = Earth(540, 2700, 1480, seed=5, dark_below=1220)
    sw = swift_sprite()
    BX0, BX1, BY = 140, 940, 1112   # the 2004-2026 bar
    name_swift = label("SWIFT", 28, WHITE, True, (8, 18, 40, 190), (14, 6))
    plan_w = (BX1 - BX0) * 2 / 21.96
    f_lab = ImageFont.truetype(XB, 30)
    f_yr = ImageFont.truetype(XB, 40)
    frames = []
    for i in range(N["swift"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        u = t / (N["swift"] / FPS)
        im = earth.draw(bg, shift=60 * t, air=16)
        lay = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(lay)
        dashed_arc(d, 540, 2700, 1960, 250, 290, (255, 255, 255, 70), width=3)  # the orbit, through Swift
        im.alpha_composite(lay)
        x, y = 505 + 70 * u, 760 + 8 * math.sin(2 * math.pi * t / 3.2)
        put1(im, rotated(sw, 4 - 7 * u), x, y, scale=0.74)
        put1(im, name_swift, x, y + 128, a=ramp(t, 0.1, 0.4))
        # the bar: planned 2 years (white) and the real run filling to 2026 (yellow)
        lay = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(lay)
        ka = ramp(t, 0.0, 0.25)
        d.rounded_rectangle([BX0, BY - 18, BX1, BY + 18], radius=18, fill=(6, 14, 34, int(200 * ka)),
                            outline=(255, 255, 255, int(230 * ka)), width=3)
        fill = ease((t - 0.45) / 1.95)
        if fill > 0:
            d.rounded_rectangle([BX0 + 5, BY - 13, BX0 + 5 + max(26, (BX1 - BX0 - 10) * fill), BY + 13], radius=13, fill=YELLOW + (255,))
        kp = pop(t, 0.12, 0.3)
        if kp > 0:
            d.rounded_rectangle([BX0 + 5, BY - 13, BX0 + 5 + plan_w, BY + 13], radius=13, fill=(255, 255, 255, int(255 * min(1, kp))))
            d.line([(BX0 + 5 + plan_w, BY - 30), (BX0 + 5 + plan_w, BY + 30)], fill=(255, 255, 255, int(255 * min(1, kp))), width=4)
            d.text((BX0, BY - 40), "RENCANA: 2 TAHUN", font=f_lab, fill=(255, 255, 255, int(255 * min(1, kp))), anchor="ls")
        d.text((BX0 + 4, BY + 52), "2004", font=f_lab, fill=(255, 255, 255, int(230 * ka)), anchor="ls")
        im.alpha_composite(lay)
        if fill > 0.12:  # the year rides the end of the yellow fill
            yr = 2004 + min(22, int(21.96 * fill + 0.4))
            hx = BX0 + 5 + (BX1 - BX0 - 10) * fill
            sp = label(str(yr), 40, (20, 20, 22), True, YELLOW + (255,), (14, 6))
            put1(im, sp, min(hx, BX1 - 50), BY + 52, a=ramp(fill, 0.12, 0.2))
        frames.append(im.convert("RGB"))
    return frames


# ---------- skema_orbit ----------
def sun_sprite(r=54):
    sp = Image.new("RGBA", (8 * r * S, 8 * r * S))
    c = 4 * r * S
    d = ImageDraw.Draw(sp)
    d.ellipse([c - 2.2 * r * S, c - 2.2 * r * S, c + 2.2 * r * S, c + 2.2 * r * S], fill=(255, 150, 40, 120))
    g = sp.filter(ImageFilter.GaussianBlur(r * S * 0.9))
    d = ImageDraw.Draw(g)
    for k in range(12):
        a = 2 * math.pi * k / 12
        d.line([(c + math.cos(a) * 1.15 * r * S, c + math.sin(a) * 1.15 * r * S), (c + math.cos(a) * 1.7 * r * S, c + math.sin(a) * 1.7 * r * S)],
               fill=(255, 205, 80, 220), width=6 * S)
    d.ellipse([c - r * S, c - r * S, c + r * S, c + r * S], fill=(255, 226, 110, 255))
    d.ellipse([c - 0.6 * r * S, c - 0.6 * r * S, c + 0.3 * r * S, c + 0.3 * r * S], fill=(255, 246, 200, 255))
    return g


def engine_sprite():
    """a rocket engine: chamber and bell nozzle with a small flame, 2x"""
    sp = Image.new("RGBA", (220 * S, 260 * S))
    d = ImageDraw.Draw(sp)
    c = 110 * S
    d.rounded_rectangle([c - 34 * S, 30 * S, c + 34 * S, 100 * S], radius=10 * S, fill=(214, 218, 226, 255))
    d.polygon([(c - 22 * S, 100 * S), (c + 22 * S, 100 * S), (c + 62 * S, 190 * S), (c - 62 * S, 190 * S)], fill=(170, 174, 184, 255))
    d.polygon([(c - 62 * S, 190 * S), (c + 62 * S, 190 * S), (c + 54 * S, 198 * S), (c - 54 * S, 198 * S)], fill=(120, 124, 134, 255))
    d.polygon([(c - 40 * S, 200 * S), (c + 40 * S, 200 * S), (c, 250 * S)], fill=ORANGE + (230,))
    d.polygon([(c - 20 * S, 200 * S), (c + 20 * S, 200 * S), (c, 232 * S)], fill=YELLOW + (255,))
    return soft_edge(sp, 6, 0.3)


def red_x(size=150):
    sp = Image.new("RGBA", (size * S, size * S))
    d = ImageDraw.Draw(sp)
    m = 18 * S
    for (a, b) in [((m, m), (size * S - m, size * S - m)), ((size * S - m, m), (m, size * S - m))]:
        d.line([a, b], fill=(0, 0, 0, 160), width=26 * S)
    sh = sp.filter(ImageFilter.GaussianBlur(5 * S))
    d = ImageDraw.Draw(sh)
    for (a, b) in [((m, m), (size * S - m, size * S - m)), ((size * S - m, m), (m, size * S - m))]:
        d.line([a, b], fill=RED + (255,), width=18 * S)
    return sh


def skema_orbit(times=None):
    t_mesin, t_dorong = 1.81, 2.05
    bg = space_bg(8)
    CX, CY, R = 540, 1030, 232
    earth = Earth(CX, CY, R, seed=9)
    sw = swift_sprite()
    sun = sun_sprite()
    eng, cross = engine_sprite(), red_x()
    SUN = (128, 652)
    th0, turns = math.radians(160), 1.5          # anticlockwise on screen, from the left to just above the right side
    r0, r1 = 420, 268
    frames = []
    total = N["orbit"] / FPS
    for i in range(N["orbit"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        u = ease(t / (total - 0.25))
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t / 0.85)
        im = earth.draw(bg, shift=90 * t, air=12 + 46 * ramp(t, 0.2, 2.6) + 6 * pulse, air_a=0.75 + 0.35 * ramp(t, 0.2, 2.6))
        # the Sun: pulsing, throwing arcs towards the Earth
        put1(im, sun, *SUN, scale=0.5 * (1 + 0.16 * pulse))
        lay = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(lay)
        for k in range(6):
            g = (t - 0.42 * k) % 2.5
            if 0 <= g < 1.4:
                rr = 70 + 330 * g
                al = int(170 * min(1, g / 0.15) * max(0, 1 - g / 1.4))
                d.arc([SUN[0] - rr, SUN[1] - rr, SUN[0] + rr, SUN[1] + rr], 15, 75, fill=ORANGE + (al,), width=6)
        im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3)))
        im.alpha_composite(lay)
        # the spiral already flown (dashed, fading) and Swift on it
        lay = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(lay)
        steps = 160
        pts = []
        for j in range(steps + 1):
            v = u * j / steps
            th = th0 - 2 * math.pi * turns * v
            r = r0 + (r1 - r0) * v
            pts.append((CX + r * math.cos(th), CY + r * math.sin(th)))
        for j in range(0, steps, 2):
            a = int(60 + 150 * j / steps)
            d.line([pts[j], pts[j + 1]], fill=(255, 255, 255, a), width=4)
        im.alpha_composite(lay)
        th = th0 - 2 * math.pi * turns * u
        r = r0 + (r1 - r0) * u
        sx, sy = CX + r * math.cos(th), CY + r * math.sin(th)
        heading = math.degrees(-(th - math.pi / 2))
        put1(im, rotated(sw, heading), sx, sy, scale=0.2)
        # no engine: the icon pops on "mesin", the red cross lands on "pendorong"
        ke = pop(t, t_mesin, 0.3)
        if ke > 0:
            put1(im, eng, 924, 660, a=min(1, ke), scale=0.8 * ke)
        kx = pop(t, t_dorong, 0.25)
        if kx > 0:
            put1(im, cross, 924, 670, a=min(1, kx), scale=1.05 * (1.6 - 0.6 * min(kx, 1.2)))
        # where it ended up
        kl = pop(t, 2.45, 0.3)
        if kl > 0:
            put1(im, label("275 km", 44, YELLOW), 868, 826, a=min(1, kl), scale=kl)
            put1(im, label("20 Okt 2026", 28, WHITE, False, (8, 18, 40, 180), (14, 6)), 868, 888, a=min(1, kl))
        frames.append(im.convert("RGB"))
    return frames


# ---------- skema_link ----------
def card(day, year, hl=False):
    """a tear-off calendar page: red header with rings, the day big and the year under it; 2x sprite"""
    w, h, hd = 300 * S, 196 * S, 46 * S
    sp = Image.new("RGBA", (w + 60 * S, h + 60 * S))
    sh = Image.new("RGBA", sp.size)
    ImageDraw.Draw(sh).rounded_rectangle([26 * S, 36 * S, 34 * S + w, 42 * S + h], radius=22 * S, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(10 * S))
    d = ImageDraw.Draw(sp)
    x0, y0 = 30 * S, 30 * S
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=20 * S, fill=YELLOW + (255,) if hl else (250, 250, 248, 255))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + hd], radius=20 * S, fill=(205, 38, 38, 255))
    d.rectangle([x0, y0 + hd - 20 * S, x0 + w, y0 + hd], fill=(205, 38, 38, 255))
    for rx in (x0 + 80 * S, x0 + w - 80 * S):
        d.ellipse([rx - 9 * S, y0 + 14 * S, rx + 9 * S, y0 + 32 * S], fill=(120, 20, 20, 255))
    d.text((x0 + w / 2, y0 + hd + 58 * S), day, font=ImageFont.truetype(XB, 60 * S), fill=(28, 28, 30, 255), anchor="mm")
    d.text((x0 + w / 2, y0 + hd + 118 * S), year, font=ImageFont.truetype(XB, 36 * S), fill=(70, 70, 76, 255), anchor="mm")
    sh.alpha_composite(sp)
    return sh


def fire_tail(im, pts, heat):
    """a tapered glowing tail along pts (newest first), orange to yellow, `heat` 0-1"""
    if heat <= 0.01 or len(pts) < 2:
        return
    lay = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(lay)
    n = len(pts)
    for j in range(n - 1):
        f = 1 - j / (n - 1)
        wdt = max(2, int(46 * f * heat))
        col = tuple(int(a * f + b * (1 - f)) for a, b in zip(YELLOW, ORANGE))
        d.line([pts[j], pts[j + 1]], fill=col + (int(235 * f * heat),), width=wdt)
    glow = lay.filter(ImageFilter.GaussianBlur(14))
    im.alpha_composite(glow)
    im.alpha_composite(glow)
    im.alpha_composite(lay)


def skema_link(times=None):
    t_rob, t_hil, t_dan, t_jat, t_dul = 0.58, 1.06, 2.16, 2.56, 2.84
    bg = space_bg(11)
    earth = Earth(540, 2700, 1480, seed=13, dark_below=1220)
    sw, lk = swift_sprite(), link_sprite()
    q = text_sprite([("?", 64, YELLOW, True)])
    cards = {("25 SEP", True): card("25 SEP", "2026", True), ("4 NOV", False): card("4 NOV", "2026", False)}
    name_swift = label("SWIFT", 28, WHITE, True, (8, 18, 40, 190), (14, 6))
    name_link = label("LINK", 28, YELLOW, True, (8, 18, 40, 190), (14, 6))
    SW = (300, 772)
    STOP = (668, 806)
    rng = np.random.default_rng(2)
    qs = [(t_hil + 0.12 + 0.3 * k, rng.uniform(-110, 110), rng.uniform(-100, -40)) for k in range(4)]
    path = []
    frames = []
    for i in range(N["link"]):
        t = i / FPS
        # LINK: in from the right, stops at the 12-15 km mark, tumbles, then dives into the air
        if t < 1.0:
            v = ease(t / 1.0)
            lx, ly, ang = 1240 + (STOP[0] - 1240) * v, STOP[1], 0.0
        elif t < t_dan:
            w = t - t_hil
            spin = 0.0 if w < 0 else 160 * w + 380 * w * w
            lx, ly, ang = STOP[0] + (25 * max(0, w)) ** 1.1, STOP[1] + 30 * max(0, w) ** 1.5, spin
        else:
            w = t - t_dan
            x1, y1 = STOP[0] + (25 * (t_dan - t_hil)) ** 1.1, STOP[1] + 30 * (t_dan - t_hil) ** 1.5
            g = min(1.0, (w / 1.25) ** 1.7)
            lx, ly = x1 + (890 - x1) * g, y1 + (1300 - y1) * g
            ang = 160 * (t - t_hil) + 380 * (t - t_hil) ** 2
        path.insert(0, (lx, ly))
        if not wanted(i, times):
            frames.append(None)
            continue
        im = earth.draw(bg, shift=60 * t, air=18)
        put1(im, rotated(sw, -6 + 3 * math.sin(t)), SW[0], SW[1] + 6 * math.sin(2 * math.pi * t / 3.4), scale=0.4)
        put1(im, name_swift, SW[0], SW[1] + 84)
        put1(im, name_link, lx, ly + 66, a=ramp(t, 0.5, 0.8) * (1 - ramp(t, t_hil, t_hil + 0.25)))
        # the gap that never closed
        kd = ramp(t, 0.85, 1.1) * (1 - ramp(t, 1.9, 2.15))
        if kd > 0.01:
            lay = Image.new("RGBA", (W, H))
            d = ImageDraw.Draw(lay)
            xa, xb = SW[0] + 150, lx - 120
            for x in np.arange(xa, xb - 10, 26):
                d.line([(x, SW[1] + 30), (min(x + 14, xb), SW[1] + 30)], fill=(255, 255, 255, int(220 * kd)), width=4)
            for x in (xa, xb):
                d.line([(x, SW[1] + 14), (x, SW[1] + 46)], fill=(255, 255, 255, int(220 * kd)), width=4)
            im.alpha_composite(lay)
            put1(im, label("12–15 km", 38, YELLOW), (xa + xb) / 2, SW[1] - 30, a=kd)
        # the fall: heat grows as it sinks into the air
        heat = ramp(t, t_dan + 0.25, t_dan + 0.9)
        fire_tail(im, path[:16], heat)
        glow_a = ramp(t, t_dan + 0.4, t_dan + 1.0)
        sp = rotated(lk, ang)
        if glow_a > 0:  # red-hot
            tint = Image.new("RGBA", sp.size, ORANGE + (0,))
            tint.putalpha(sp.getchannel("A").point(lambda v: int(v * 0.8 * glow_a)))
            sp = sp.copy()
            sp.alpha_composite(tint)
        fade = 1 - ramp(t, t_dan + 1.25, t_dan + 1.6)
        put1(im, sp, lx, ly, a=fade, scale=0.62 * (1 - 0.35 * ramp(t, t_dan, t_dan + 1.4)))
        if t > t_dan + 1.1:  # it burns up at the rim
            kf = ramp(t, t_dan + 1.1, t_dan + 1.3) * (1 - ramp(t, t_dan + 1.35, t_dan + 1.85))
            lay = Image.new("RGBA", (W, H))
            ImageDraw.Draw(lay).ellipse([lx - 70, ly - 70, lx + 70, ly + 70], fill=(255, 220, 140, int(230 * kf)))
            im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(22)))
        for tq, dx, dy in qs:  # question marks while it tumbles
            k = pop(t, tq, 0.25)
            if k > 0 and t < t_dan + 0.2:
                put1(im, q, lx + dx, ly + dy, a=min(1, k) * (1 - ramp(t, tq + 0.6, tq + 0.9)), scale=k)
        # calendar cards: LINK fell on 25 Sep, Swift on 4 Nov
        for tc, day, hl, cx, name in [(t_jat, "25 SEP", True, 220, "LINK"), (t_dul, "4 NOV", False, 520, "SWIFT")]:
            k = pop(t, tc, 0.3)
            if k > 0:
                put1(im, cards[(day, hl)], cx, 1122, a=min(1, k), scale=0.8 * k)
                put1(im, label(name, 30, WHITE, True, (8, 18, 40, 190), (14, 6)), cx, 1022, a=min(1, k))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"swift": skema_swift, "orbit": skema_orbit, "link": skema_link}

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
