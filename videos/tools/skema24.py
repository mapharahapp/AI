"""Schematic animations for Titik Heran #24 (run in the episode work dir after `dl.py i:3940781 i:347262 i:1057155`;
writes clips/skema_peta.mp4, skema_scan.mp4, skema_coret.mp4, skema_moncong.mp4 and clips/1057155c.mp4).
usage: python3 skema24.py GEO_DIR [peta|scan|coret|moncong|hidung ...] [--sheet out.jpg t1,t2,...]
       (GEO_DIR holds ne_10m_land.geojson and ne_50m_admin_0_boundary_lines_land.geojson from github.com/nvkelso/natural-earth-vector,
       folder geojson/; --sheet saves those frames as a contact sheet instead of encoding)
skema_peta: Sumatra and Borneo from the Natural Earth coastlines light up as Akram names them: the lowland rivers there are home to
the senyulong (Tomistoma schlegelii), the long-snouted crocodile whose genus the Egyptian skull was put in, in 1927.
skema_scan: a modern crocodile skull (Pixabay 3940781, an illustration, not the fossil) swept by a CT scan line; a card gives the
size of the comparison (152 species, 331 anatomical characters; Burke et al. 2026, Royal Society Open Science).
skema_coret: the senyulong photo (Pixabay 347262) laid out like render.py's kind b, crossed out in red on "bukan".
skema_moncong: a long-snouted crocodile skull drawn in side view; the tip of the snout is ringed on "ujung" and turns into a dashed
outline on "hilang" (the fossil skull of Herugavialis lacks the tip of its snout).
hidung (clips/1057155c.mp4): the Sphinx face (Pixabay 1057155) with a yellow ring drawn round the missing nose on "hidung".
Event times are seconds from the start of each shot, read off `render.py 24 plan`.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, dashed, encode
from skema13 import navy
from skema17 import ring, label
from skema18 import clip_ring, check

N = {"peta": 102, "scan": 63, "coret": 60, "moncong": 72, "hidung": 57}
GEO = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in N else "geo"
RED = (226, 40, 36)


def inside(pt, ring_):
    x, y, hit = pt[0], pt[1], False
    for (x0, y0), (x1, y1) in zip(ring_, ring_[1:] + ring_[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (x1 - x0) * (y - y0) / (y1 - y0):
            hit = not hit
    return hit


def kind_b(src):
    """render.py's kind b at 1x: the photo across the frame, sharp, over its own blurred and darkened copy"""
    im = Image.open(src).convert("RGB")
    k = max(W / im.width, H / im.height)
    bg = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(30))
    bg = Image.fromarray(np.clip(np.asarray(bg, np.float32) * 0.8 - 8, 0, 255).astype(np.uint8))
    fg = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    bg.paste(fg, (0, (H - fg.height) // 2))
    return bg.convert("RGBA"), (H - fg.height) // 2, fg.height


# ---------- skema_peta ----------
K, LON0, LAT0, CY = 42, 107.3, 0.5, 905
SUMATRA, BORNEO = (101.5, -0.5), (114.0, 1.0)


def xy(lon, lat):
    return 540 + (lon - LON0) * K, CY - (lat - LAT0) * K


def sea_land():
    rings = []
    for f in json.load(open(os.path.join(GEO, "ne_10m_land.geojson")))["features"]:
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            r = poly[0]
            lo, la = [p[0] for p in r], [p[1] for p in r]
            if max(lo) < 88 or min(lo) > 128 or max(la) < -16 or min(la) > 16:
                continue
            c = clip_ring(r, 88, -16, 128, 16)
            if len(c) > 2:
                rings.append(c)
    hot = {}
    for name, pt in (("sumatra", SUMATRA), ("kalimantan", BORNEO)):
        hot[name] = next(r for r in rings if max(p[0] for p in r) - min(p[0] for p in r) < 14 and inside(pt, r))
    borders = []
    for f in json.load(open(os.path.join(GEO, "ne_50m_admin_0_boundary_lines_land.geojson")))["features"]:
        g = f["geometry"]
        for ln in g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]:
            if all(95 < p[0] < 125 and -11 < p[1] < 12 for p in ln):
                borders.append(ln)
    return rings, hot, borders


def peta(times):
    rings, hot, borders = sea_land()
    bg = navy(540, 900)
    base = layer()
    d = ImageDraw.Draw(base)
    for r in rings:
        d.polygon(sc([xy(*q) for q in r]), fill=(150, 134, 102, 255), outline=(96, 84, 62, 255), width=2 * S)
    for ln in borders:
        dashed(d, [xy(*q) for q in ln], fill=(96, 84, 62, 220), width=3, dash=12, gap=9)
    base = down(base)
    lit, glow = {}, {}
    for name, r in hot.items():
        p = sc([xy(*q) for q in r])
        a = layer()
        ImageDraw.Draw(a).polygon(p, fill=(232, 206, 140, 255), outline=(120, 96, 50, 255), width=2 * S)
        lit[name] = down(a)
        g = layer()
        ImageDraw.Draw(g).line(p + p[:1], fill=YELLOW + (255,), width=9 * S, joint="curve")
        glow[name] = down(g).filter(ImageFilter.GaussianBlur(7))
    labs = {"sumatra": (text_sprite([("SUMATRA", 46, WHITE, True)]), xy(99.6, -1.2)),
            "kalimantan": (text_sprite([("KALIMANTAN", 46, WHITE, True)]), xy(114.1, 0.4))}
    habitat = label([("habitat senyulong", 42, YELLOW, True)], edge=YELLOW + (220,))
    # buaya 0.04, moncong 0.33, panjang 0.63, dari 1.12, Sumatra 1.31, dan 1.91, Kalimantan 2.06
    on = {"sumatra": 1.27, "kalimantan": 2.02}
    out = []
    for t in times:
        im = bg.copy()
        im.alpha_composite(fade(base, ramp(t, 0.0, 0.22)))
        for name, t0 in on.items():
            a = ramp(t, t0, t0 + 0.2)
            if a > 0:
                im.alpha_composite(fade(lit[name], a))
                pulse = 0.65 + 0.35 * math.cos(2 * math.pi * max(0.0, t - t0) / 1.1)
                im.alpha_composite(fade(glow[name], a * pulse))
        top = layer()
        for name, (sp, (x, y)) in labs.items():
            put(top, sp, x, y, a=ramp(t, on[name] + 0.04, on[name] + 0.16), scale=pop(t, on[name] + 0.04))
        put(top, habitat, 540, 1190, a=ramp(t, 2.3, 2.45), scale=pop(t, 2.3))
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_scan ----------
def ct_look(im):
    """the photo as a CT slice would show it: grey bone, contrast up, a cool tint, faint scan rows"""
    a = np.asarray(im.convert("L"), np.float32) / 255
    a = np.clip((a - 0.08) * 1.35, 0, 1) ** 0.9
    rows = 1 - 0.12 * (np.arange(a.shape[0]) % 4 == 0)[:, None]
    rgb = np.stack([a * 200, a * 238, a * 255], -1) * rows[..., None]
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert("RGBA")


def scan(times):
    photo = Image.open("img/3940781.jpg").convert("RGB")
    photo = photo.resize((W, round(photo.height * W / photo.width)), Image.LANCZOS)
    y0 = 540
    plain = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    plain.paste(photo, (0, y0))
    ct = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    ct.paste(ct_look(photo), (0, y0))
    grid = layer()
    d = ImageDraw.Draw(grid)
    for x in range(30, W, 60):
        d.line([(x * S, y0 * S), (x * S, (y0 + photo.height) * S)], fill=(90, 255, 200, 34), width=2 * S)
    grid = down(grid)
    beam = Image.new("RGBA", (120, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    for i in range(60):  # a soft trail behind the line
        bd.line([(i, y0 - 30), (i, y0 + photo.height + 30)], fill=(90, 255, 200, round(150 * (i / 60) ** 2)))
    bd.rectangle([58, y0 - 30, 63, y0 + photo.height + 30], fill=(210, 255, 240, 255))
    beam = beam.filter(ImageFilter.GaussianBlur(1.2))
    card = label([("dibandingkan dengan 152 spesies", 38, WHITE, True), ("331 ciri anatomi", 34, YELLOW, False)], edge=YELLOW + (230,))
    # membongkar 0.03, tengkoraknya: 0.63
    t0, t1, t_card = 0.05, 1.15, 0.6
    out = []
    for t in times:
        sx = round(-60 + (W + 120) * ramp(t, t0, t1))
        im = plain.copy()
        if sx > 0:
            done = ct.crop((0, 0, min(sx, W), H))
            im.paste(done, (0, 0))
            g = grid.crop((0, 0, min(sx, W), H))
            im.alpha_composite(g, (0, 0))
        if -60 < sx < W + 60:
            im.alpha_composite(beam, (sx - 60, 0))
        top = layer()
        put(top, card, 540, 1190, a=ramp(t, t_card, t_card + 0.15), scale=pop(t, t_card))
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_coret ----------
def stroke(d, a, b, u, width, col, wob=0.0):
    """a marker stroke from a to b drawn up to fraction u"""
    if u <= 0:
        return
    n = 24
    pts = [(a[0] + (b[0] - a[0]) * i / n * u + wob * math.sin(i * 0.7), a[1] + (b[1] - a[1]) * i / n * u) for i in range(n + 1)]
    d.line(sc(pts), fill=col, width=width * S, joint="curve")
    for x, y in (pts[0], pts[-1]):
        r = width / 2
        d.ellipse(sc([(x - r, y - r), (x + r, y + r)]), fill=col)


def coret(times):
    base, py, ph = kind_b("img/347262.jpg")
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    # ia 0.04, bukan 0.19, golongan 0.42, senyulong... 0.72
    out = []
    for t in times:
        im = base.copy()
        im.alpha_composite(fade(dark, 0.35 * ramp(t, 0.17, 0.4)))
        top = layer()
        d = ImageDraw.Draw(top)
        x0, x1, y0, y1 = 170, 910, py + 70, py + ph - 70
        stroke(d, (x0, y0), (x1, y1), ramp(t, 0.17, 0.33), 30, RED + (240,), wob=3)
        stroke(d, (x1, y0), (x0, y1), ramp(t, 0.33, 0.49), 30, RED + (240,), wob=-3)
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_moncong ----------
BONE, BONE_D, EDGE, HOLE = (234, 220, 188), (204, 186, 150), (112, 92, 62), (12, 26, 52)
TIP0 = 300  # the snout ahead of this x (before T) is the part the fossil lacks


def T(p):  # the skull is drawn on a 1080-wide grid, then enlarged about its middle
    return 560 + (p[0] - 560) * 1.12, 915 + (p[1] - 915) * 1.12


TIP = T((TIP0, 0))[0]


def at_x(edge, x):
    """y of a polyline at x (linear between its points)"""
    for (x0, y0), (x1, y1) in zip(edge, edge[1:]):
        if min(x0, x1) <= x <= max(x0, x1) and x0 != x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


def skull_parts():
    """a long-snouted crocodile skull in side view, facing left: the skull and the lower jaw, each as a top and bottom edge"""
    top = [(150, 902), (176, 889), (260, 884), (360, 880), (460, 874), (560, 866), (640, 851), (700, 822), (762, 795),
           (840, 783), (902, 792), (944, 822), (956, 872), (948, 930), (930, 972)]
    bot = [(900, 978), (820, 980), (720, 974), (620, 965), (520, 958), (420, 951), (320, 945), (230, 939), (172, 931), (152, 918)]
    jaw_top = [(166, 951), (240, 957), (340, 963), (440, 969), (540, 975), (640, 982), (740, 988), (850, 992), (930, 990), (972, 1008)]
    jaw_bot = [(962, 1036), (900, 1046), (780, 1040), (640, 1026), (520, 1012), (400, 1000), (290, 989), (210, 979), (170, 970)]
    holes = [(735, 852, 34, 27), (858, 902, 42, 22), (806, 1013, 42, 11)]
    teeth = []
    for i, x in enumerate(range(184, 900, 30)):
        teeth.append(("up", x, at_x(bot[::-1], x) if x <= 900 else 978, 14 + 8 * (i % 3 == 1)))
    for i, x in enumerate(range(198, 880, 30)):
        teeth.append(("down", x, at_x(jaw_top, x), 12 + 8 * (i % 3 == 2)))
    return top, bot, jaw_top, jaw_bot, holes, teeth


def tip_outline():
    """the outline of the missing tip (before T): the front of the skull and of the lower jaw, each from the cut round to the cut"""
    top, bot, jaw_top, jaw_bot, _, _ = skull_parts()
    upper = [(TIP0, at_x(top, TIP0))] + [p for p in top if p[0] < TIP0][::-1] + [p for p in bot if p[0] < TIP0] + [(TIP0, at_x(bot, TIP0))]
    lower = [(TIP0, at_x(jaw_top, TIP0))] + [p for p in jaw_top if p[0] < TIP0][::-1] + [p for p in jaw_bot if p[0] < TIP0] + \
            [(TIP0, at_x(jaw_bot, TIP0))]
    return [T(p) for p in upper], [T(p) for p in lower]


def skull_layer():
    top, bot, jaw_top, jaw_bot, holes, teeth = skull_parts()
    im = layer()
    d = ImageDraw.Draw(im)

    def poly(pts, **kw):
        d.polygon(sc([T(p) for p in pts]), **kw)
    for kind, x, y, h in teeth:
        poly([(x - 7, y), (x + 7, y), (x, y + h)] if kind == "up" else [(x - 7, y), (x + 7, y), (x, y - h)],
             fill=(246, 240, 222, 255), outline=EDGE + (255,), width=S)
    poly(jaw_top + jaw_bot, fill=BONE_D + (255,), outline=EDGE + (255,), width=3 * S)
    poly(top + bot, fill=BONE + (255,), outline=EDGE + (255,), width=3 * S)
    for x, y, rx, ry in holes:
        (x0, y0), (x1, y1) = T((x - rx, y - ry)), T((x + rx, y + ry))
        d.ellipse(sc([(x0, y0), (x1, y1)]), fill=HOLE + (255,), outline=EDGE + (255,), width=2 * S)
    (x0, y0), (x1, y1) = T((164, 893)), T((178, 903))
    d.ellipse(sc([(x0, y0), (x1, y1)]), fill=HOLE + (255,))  # nostril at the tip
    for x in range(330, 700, 46):  # pitted bone along the snout
        d.line(sc([T((x, 900 - (x - 300) * 0.045)), T((x + 20, 903 - (x - 300) * 0.045))]), fill=BONE_D + (255,), width=2 * S)
    return down(im)


def split_at_tip(im):
    """(front, rest): the part of a layer ahead of TIP and the part behind it"""
    a = np.asarray(im.getchannel("A")).copy()
    front, rest = im.copy(), im.copy()
    fa, ra = a.copy(), a.copy()
    fa[:, round(TIP):] = 0
    ra[:, :round(TIP)] = 0
    front.putalpha(Image.fromarray(fa))
    rest.putalpha(Image.fromarray(ra))
    return front, rest


def moncong(times):
    bg = navy(540, 930)
    front, rest = split_at_tip(skull_layer())
    up, lo = tip_outline()
    cx, cy = T((222, 930))
    lab_ujung = label([("ujung moncong", 38, YELLOW, True)], edge=YELLOW + (220,))
    lab_hilang = text_sprite([("HILANG!", 70, RED, True)])
    # Sebab 0.03, ujung 0.55, moncongnya 0.81, hilang... 1.23
    t_in, t_ring, t_gone = 0.0, 0.5, 1.2
    out = []
    for t in times:
        im = bg.copy()
        a = ramp(t, t_in, t_in + 0.25)
        g = ramp(t, t_gone, t_gone + 0.3)
        im.alpha_composite(fade(rest, a))
        if g < 1:
            im.alpha_composite(fade(front, a * (1 - g)))
        top = layer()
        d = ImageDraw.Draw(top)
        if g > 0:
            for seg in (up, lo):
                dashed(d, seg, fill=YELLOW + (round(255 * g),), width=5, dash=14, gap=10)
        if t >= t_ring and g < 1:
            ring(d, cx, cy, 128 * pop(t, t_ring), YELLOW, 235 * (1 - g), w=7)
        put(top, lab_ujung, cx + 20, cy + 178, a=ramp(t, t_ring, t_ring + 0.15) * (1 - g), scale=pop(t, t_ring))
        put(top, lab_hilang, cx + 30, cy + 170, a=ramp(t, t_gone + 0.1, t_gone + 0.25), scale=pop(t, t_gone + 0.1))
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- hidung (clips/1057155c.mp4) ----------
def hidung(times):
    src = Image.open("img/1057155.jpg").convert("RGB")
    k, x0, dy = 2.0, 470, 120  # 2x, crop from x 470, the photo moved down 120 px so the nose sits mid-frame
    ph = src.resize((round(src.width * k), round(src.height * k)), Image.LANCZOS).crop((round(x0 * k), 0, round(x0 * k) + W, round(src.height * k)))
    sky = np.asarray(ph.crop((0, 0, W, 8)), np.float32).mean((0, 1))
    base = Image.new("RGB", (W, H), tuple(int(v) for v in sky))
    base.paste(ph, (0, dy))
    base = base.convert("RGBA")
    c = ((828 - x0) * k, 392 * k + dy)
    rng = np.random.default_rng(24)
    wob = rng.normal(0, 0.03, 8)
    # persis 0.05, hidung 0.43, Sfinks! 0.69
    t0, t1 = 0.4, 0.68
    out = []
    for t in times:
        im = base.copy()
        u = ramp(t, t0, t1)
        if u > 0:
            top = layer()
            d = ImageDraw.Draw(top)
            pts = []
            for i in range(int(72 * u) + 1):
                a = -2.0 + 2 * math.pi * 1.1 * i / 72
                rr = 1 + sum(wob[j] * math.sin((j + 1) * a + j) for j in range(8))
                pts.append(((c[0] + 118 * rr * math.cos(a)) * S, (c[1] + 150 * rr * math.sin(a)) * S))
            if len(pts) > 1:
                d.line(pts, fill=(0, 0, 0, 120), width=16 * S, joint="curve")
                d.line(pts, fill=YELLOW + (255,), width=11 * S, joint="curve")
            im.alpha_composite(down(top))
        out.append(im)
    return out


OUT = {"peta": "clips/skema_peta.mp4", "scan": "clips/skema_scan.mp4", "coret": "clips/skema_coret.mp4",
       "moncong": "clips/skema_moncong.mp4", "hidung": "clips/1057155c.mp4"}

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
