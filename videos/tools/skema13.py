"""Schematic animations for Titik Heran #13 (run in the episode work dir; writes clips/skema_papua.mp4, skema_es.mp4, skema_bor.mp4).
usage: python3 skema13.py GEO_DIR [papua|es|bor ...]   (GEO_DIR holds ne_10m_land.geojson and ne_50m_admin_0_boundary_lines_land.geojson from
       github.com/nvkelso/natural-earth-vector, folder geojson/)
skema_papua: New Guinea from the Natural Earth coastlines, the equator, and Puncak Jaya (4°05'S 137°11'E), ±450 km south of it.
skema_es: the ice shrinking from ±4,3 km² (1988) to ±0,09 km² (2025), the BMKG figures; the shape is schematic, the areas are to scale.
skema_bor: a cross-section of the ice, ±32 m thick in 2010, drilled down to the bedrock; the ice core comes up.
Event times are seconds from the start of each shot, read off the word times of `render.py 13 subs`.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, BOLD, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, dashed, chaikin, encode

GEO = sys.argv[1] if len(sys.argv) > 1 else "geo"


def navy(cx, cy, xs=(), ys=()):
    """the navy backdrop of the other skema clips, lighter around (cx, cy), with faint lines at xs and ys"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = (yy / H)[..., None]
    col = np.array([13, 38, 78]) * (1 - v) + np.array([5, 17, 40]) * v
    col += np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / 520 ** 2)[..., None] * np.array([16, 38, 66])
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")
    g = layer()
    d = ImageDraw.Draw(g)
    for x in xs:
        d.line([(x * S, 0), (x * S, H * S)], fill=(255, 255, 255, 18), width=2 * S)
    for y in ys:
        d.line([(0, y * S), (W * S, y * S)], fill=(255, 255, 255, 18), width=2 * S)
    im.alpha_composite(down(g))
    return im


def marker():
    dot = Image.new("RGBA", (80 * S, 80 * S), (0, 0, 0, 0))
    ImageDraw.Draw(dot).polygon(sc(chaikin([(40 + 22 * math.cos(a) * (1 + 0.18 * math.sin(3 * a + 1)), 40 + 19 * math.sin(a))
                                             for a in (2 * math.pi * k / 9 for k in range(9))])),
                                fill=YELLOW + (255,), outline=(70, 50, 0, 255), width=3 * S)
    return dot


def papua(n=90):
    K, LON0, YEQ = 50, 138.5, 760  # pixels per degree, centre longitude, y of the equator

    def xy(lon, lat):
        return 540 + (lon - LON0) * K, YEQ - lat * K
    rings = []
    for f in json.load(open(os.path.join(GEO, "ne_10m_land.geojson")))["features"]:
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            lon = [p[0] for p in poly[0]]
            lat = [p[1] for p in poly[0]]
            if max(lon) > LON0 - 13 and min(lon) < LON0 + 13 and max(lat) > -26 and min(lat) < 17:
                rings.append([xy(*p) for p in poly[0]])
    border = []
    for f in json.load(open(os.path.join(GEO, "ne_50m_admin_0_boundary_lines_land.geojson")))["features"]:
        g = f["geometry"]
        for ln in g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]:
            if all(139 < x < 143 and -11 < y < 0 for x, y in ln):
                border = [xy(*p) for p in ln]
    border.sort(key=lambda p: p[1])
    px, py = xy(137.1833, -4.0833)  # Puncak Jaya
    land = Image.new("L", (W * S, H * S), 0)
    dl = ImageDraw.Draw(land)
    for r in rings:
        dl.polygon(sc(r), fill=255)
    east = Image.new("L", (W * S, H * S), 0)  # Papua New Guinea: east of the border, drawn a little darker
    cut = [(border[-1][0], 1240), (800, 1240), (800, 1360), (W + 10, 1360), (W + 10, 0)]  # stop above Cape York
    ImageDraw.Draw(east).polygon(sc([(border[0][0], 0)] + border + cut), fill=255)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = np.clip(np.hypot(xx - px, yy - py) / 760, 0, 1)[..., None]
    shade = np.array([214, 194, 150]) * (1 - u) + np.array([140, 122, 88]) * u
    shade *= 1 - 0.22 * (np.asarray(east.resize((W, H), Image.LANCZOS), np.float32) / 255)[..., None]
    terrain = Image.fromarray(shade.astype(np.uint8)).convert("RGBA")
    terrain.putalpha(land.resize((W, H), Image.LANCZOS))
    lines = [540 + (lon - LON0) * K for lon in (130, 135, 140, 145)], [YEQ - lat * K for lat in (15, 10, 5, -5, -10, -15, -20)]
    bg = navy(px, py, *lines)
    bg.alpha_composite(terrain)
    top = layer()
    d = ImageDraw.Draw(top)
    for r in rings:
        d.line(sc(r + r[:1]), fill=(116, 96, 66, 255), width=2 * S)
    dashed(d, border, (255, 255, 255, 150), 3, dash=12, gap=9)
    ax, ay = 985 * S, 1585 * S  # north arrow, out in the Coral Sea
    d.polygon([(ax, ay - 46 * S), (ax + 20 * S, ay + 12 * S), (ax, ay), (ax - 20 * S, ay + 12 * S)], fill=(255, 255, 255, 210))
    d.text((ax, ay - 58 * S), "U", font=ImageFont.truetype(BOLD, 40 * S), fill=(255, 255, 255, 225), anchor="ms")
    for name, lon, lat, size, a in (("PAPUA NUGINI", 144.4, -5.9, 30, 0.75), ("AUSTRALIA", 134.0, -19.0, 34, 0.6)):
        put(top, text_sprite([(name, size, WHITE, True)]), *xy(lon, lat), a=a)
    bg.alpha_composite(down(top))
    papua_lab = text_sprite([("PAPUA", 46, WHITE, True)])
    eq_lab = text_sprite([("KHATULISTIWA 0°", 40, YELLOW, True)])
    pj_lab = text_sprite([("PUNCAK JAYA", 40, WHITE, True)])
    km_lab = text_sprite([("±450 km", 50, WHITE, True)])
    dot = marker()
    t_pj, t_km = 0.25, 0.7  # "Puncak" is said 0.31 s into the shot
    frames = []
    for i in range(n):
        t = i / FPS
        im = bg.copy()
        top = layer()
        d = ImageDraw.Draw(top)
        dashed(d, [(0, YEQ), (W, YEQ)], YELLOW + (225,), 5, dash=26, gap=14, upto=ramp(t, 0.0, 0.45) * W)
        put(top, eq_lab, 822, YEQ - 42, a=ramp(t, 0.2, 0.45))
        put(top, papua_lab, *xy(139.4, -6.7), a=ramp(t, 0.05, 0.35))
        if t >= t_km:
            dashed(d, [(px, py - 26), (px, YEQ + 4)], (255, 255, 255, 230), 4, dash=14, gap=10, upto=ramp(t, t_km, t_km + 0.35) * (py - 30 - YEQ))
            put(top, km_lab, px - 118, (py + YEQ) / 2, a=ramp(t, t_km + 0.25, t_km + 0.4), scale=pop(t, t_km + 0.25))
        if t >= t_pj:
            ph = ((t - t_pj) % 1.0) / 1.0
            r = (22 + 44 * ph) * S
            d.ellipse([px * S - r, py * S - r, px * S + r, py * S + r], outline=YELLOW + (round(210 * (1 - ph) ** 1.5),), width=4 * S)
            put(top, dot, px, py, scale=pop(t, t_pj))
            put(top, pj_lab, px + 178, py + 4, a=ramp(t, t_pj + 0.1, t_pj + 0.3))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_papua.mp4")


def es(n=96):
    rng = np.random.default_rng(13)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = 540, 1000
    # a smooth height field; the ice is where it lies above a threshold, so raising the threshold shrinks the ice
    # the way a glacier retreats: unevenly, to the highest spots (here two patches, as on Puncak Jaya today)
    field = np.zeros((H, W), np.float32)
    bumps = [(-330 + 55 * k, 18 * math.sin(k / 2.2), rng.uniform(0.45, 0.65), rng.uniform(70, 130), rng.uniform(55, 95)) for k in range(13)]
    bumps += [(-250, 130, 0.42, 70, 120), (-60, 150, 0.4, 60, 130), (170, 120, 0.38, 80, 110), (300, -110, 0.36, 70, 90),
              (-180, -120, 0.36, 90, 80), (60, -130, 0.34, 70, 80)]  # tongues running down from the crest
    bumps += [(70, -5, 0.5, 45, 32), (-150, 20, 0.44, 40, 30)]  # the two highest spots, where the last ice holds on
    for dx, dy, a, sx, sy in bumps:
        field += a * np.exp(-(((xx - cx - dx) / sx) ** 2 + ((yy - cy - dy) / sy) ** 2) / 2)
    for cell, amp in ((40, 0.26), (12, 0.07)):
        nz = Image.fromarray((rng.random((H // cell + 2, W // cell + 2)) * 255).astype(np.uint8))
        field += amp * (np.asarray(nz.resize((W + 2 * cell, H + 2 * cell), Image.BICUBIC), np.float32)[cell:cell + H, cell:cell + W] / 255 - 0.5)
    ranked = np.sort(field.ravel())
    A0 = 250_000
    A1 = A0 * 0.09 / 4.3
    thr0 = ranked[-A0]
    edge = 0.006

    def ice_alpha(thr):
        return np.clip((field - thr) / edge, 0, 1)
    ghost = Image.fromarray((ice_alpha(thr0) * 255).astype(np.uint8))
    grow = np.asarray(ghost.filter(ImageFilter.MaxFilter(5)), np.int16)
    shrink = np.asarray(ghost.filter(ImageFilter.MinFilter(3)), np.int16)
    ring = Image.fromarray((grow - shrink).clip(0, 255).astype(np.uint8))  # the 1988 outline
    bg = navy(cx, cy)
    fill = Image.new("RGBA", (W, H), (122, 112, 104, 0))  # bare rock where the ice was in 1988
    fill.putalpha(ghost.point(lambda v: v * 0.45))
    bg.alpha_composite(fill)
    line = Image.new("RGBA", (W, H), (176, 214, 255, 0))
    line.putalpha(ring.point(lambda v: min(255, v * 0.85)))
    bg.alpha_composite(line)
    note = layer()
    put(note, text_sprite([("luas es · data BMKG", 30, WHITE, False)]), cx, 1262, a=0.75)
    bg.alpha_composite(down(note))
    lab0 = text_sprite([("4,3 km²", 58, WHITE, True)])
    lab1 = text_sprite([("0,09 km²", 58, WHITE, True)])
    st = Image.fromarray((rng.random((H // 3, W // 30)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    streak = 1 - 0.07 * (np.asarray(st, np.float32) / 255)[..., None]  # faint crevasses
    t0, t1 = 0.25, 1.75  # "esnya kini tinggal" ... "dua persen" lands at 1.84
    frames = []
    for i in range(n):
        t = i / FPS
        u = ramp(t, t0, t1)
        thr = ranked[-max(1, round(A0 * (A1 / A0) ** u))]
        a = ice_alpha(thr)
        lift = np.clip((field - thr) / 0.12, 0, 1)[..., None]
        rgb = (np.array([168, 208, 244]) * (1 - lift) + np.array([248, 252, 255]) * lift) * streak
        ice = Image.fromarray(rgb.astype(np.uint8)).convert("RGBA")
        ice.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        im = bg.copy()
        im.alpha_composite(ice)
        top = layer()
        d = ImageDraw.Draw(top)
        if t > t1:  # pulse around what is left
            ys, xs = np.nonzero(a > 0.5)
            mx, my = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
            ph = ((t - t1) % 0.9) / 0.9
            r = (math.hypot(xs.max() - xs.min(), ys.max() - ys.min()) / 2 + 30 + 60 * ph) * S
            d.ellipse([mx * S - r, my * S - r, mx * S + r, my * S + r], outline=YELLOW + (round(220 * (1 - ph) ** 1.5),), width=5 * S)
        put(top, text_sprite([(str(1988 + round(37 * u)), 112, YELLOW, True)]), cx, 640)
        put(top, lab0, cx, 742, a=1 - ramp(t, t0 - 0.1, t0 + 0.15))
        put(top, lab1, cx, 742, a=ramp(t, t1, t1 + 0.2), scale=pop(t, t1))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_es.mp4")


def bor(n=120):
    x0 = 600  # where the drill stands

    def surf(x):  # top of the ice
        return 900 + 9 * math.sin(x / 170 + 0.5) + (x - 540) * 0.035

    def bed(x):  # bedrock under it, ±32 m down
        return 1232 + 16 * math.sin(x / 130 + 1.2) + 7 * math.sin(x / 47)
    xs = list(range(-10, W + 11, 6))
    y0, yb = surf(x0), bed(x0)
    bg = navy(540, 700)
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    ice_m = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(ice_m).polygon(sc([(x, surf(x)) for x in xs] + [(x, bed(x) + 2) for x in xs[::-1]]), fill=255)
    rock_m = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(rock_m).polygon(sc([(x, bed(x)) for x in xs] + [(W + 10, H + 10), (-10, H + 10)]), fill=255)
    v = np.clip((yy - 880) / 380, 0, 1)[..., None]
    ice = Image.fromarray((np.array([228, 242, 252]) * (1 - v) + np.array([160, 202, 238]) * v).astype(np.uint8)).convert("RGBA")
    ice.putalpha(ice_m.resize((W, H), Image.LANCZOS))
    v = np.clip((yy - 1230) / 690, 0, 1)[..., None]
    rock = Image.fromarray((np.array([86, 74, 66]) * (1 - v) + np.array([46, 40, 38]) * v).astype(np.uint8)).convert("RGBA")
    rock.putalpha(rock_m.resize((W, H), Image.LANCZOS))
    ridges = layer()
    dg = ImageDraw.Draw(ridges)
    for base, amp, f, ph, col in ((820, 120, 260, 0.4, (34, 58, 96, 255)), (860, 80, 170, 2.1, (26, 44, 76, 255))):
        dg.polygon(sc([(x, base - amp * abs(math.sin(x / f + ph)) - 0.4 * amp * math.sin(x / 61 + ph)) for x in xs] + [(W + 10, H), (-10, H)]), fill=col)
    bg.alpha_composite(down(ridges))
    bg.alpha_composite(rock)
    bg.alpha_composite(ice)
    top = layer()
    d = ImageDraw.Draw(top)
    rng = np.random.default_rng(5)
    for _ in range(150):  # broken stone in the bedrock
        cx, cy, r = rng.uniform(0, W), rng.uniform(1260, H), rng.uniform(8, 26)
        if cy < bed(cx) + r + 6:
            continue
        pts = [(cx + r * rng.uniform(0.6, 1.1) * math.cos(a), cy + r * rng.uniform(0.6, 1.1) * math.sin(a))
               for a in sorted(rng.uniform(0, 2 * math.pi, 6))]
        g = int(rng.uniform(-14, 18))
        d.polygon(sc(pts), fill=(92 + g, 80 + g, 72 + g, 255))
    for k in range(1, 14):  # yearly layers in the ice
        f = k / 14
        d.line(sc([(x, surf(x) + f * (bed(x) - surf(x)) + 3 * math.sin(x / 60 + k)) for x in xs]),
               fill=(110, 160, 210, 70), width=2 * S)
    d.line(sc([(x, surf(x)) for x in xs]), fill=(255, 255, 255, 255), width=3 * S)
    d.line(sc([(x, bed(x)) for x in xs]), fill=(40, 34, 32, 255), width=3 * S)
    put(top, text_sprite([("ES", 46, (24, 64, 118), True)]), 900, (surf(900) + bed(900)) / 2)
    put(top, text_sprite([("BATUAN DASAR", 40, WHITE, True)]), 770, 1490, a=0.85)
    bg.alpha_composite(down(top))
    # the rig: a tripod with a winch on top, drawn once and dropped into place
    rig = Image.new("RGBA", (260 * S, 240 * S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(rig)
    for a, b in (((30, 230), (130, 30)), ((230, 230), (130, 30)), ((70, 150), (190, 150))):
        dr.line(sc([a, b]), fill=(30, 30, 36, 255), width=12 * S)
        dr.line(sc([a, b]), fill=(236, 236, 240, 255), width=7 * S)
    dr.rounded_rectangle(sc([(104, 12), (156, 46)]), radius=6 * S, fill=YELLOW + (255,), outline=(60, 45, 0, 255), width=3 * S)
    arrow_lab = text_sprite([("±32 m", 56, YELLOW, True), ("(2010)", 34, WHITE, False)])
    core_lab = text_sprite([("INTI ES", 52, YELLOW, True)])
    ax = 110
    a0, a1 = surf(ax), bed(ax)
    t_rig, t_drill, t_done, t_up = 0.9, 1.6, 2.55, 3.1  # "ilmuwan" 1.1, "sempat" 1.62, "mengebor" 2.05, "es ini" 2.54-2.84
    frames = []
    for i in range(n):
        t = i / FPS
        im = bg.copy()
        top = layer()
        d = ImageDraw.Draw(top)
        u = ramp(t, 0.15, 0.5)  # thickness arrow, drawn from both ends
        if u > 0:
            mid = (a0 + a1) / 2
            d.line(sc([(ax, mid - u * (mid - a0 - 6)), (ax, mid + u * (a1 - 6 - mid))]), fill=(255, 255, 255, 240), width=4 * S)
            for yv, s_ in ((a0 + 2, 1), (a1 - 2, -1)):
                if u > 0.95:
                    d.polygon(sc([(ax, yv), (ax - 13, yv + 22 * s_), (ax + 13, yv + 22 * s_)]), fill=(255, 255, 255, 240))
            put(top, arrow_lab, ax + 118, mid, a=ramp(t, 0.35, 0.55))
        drop = ramp(t, t_rig, t_rig + 0.3)
        if drop > 0:
            put(top, rig, x0, y0 - 120 - 60 * (1 - drop), a=drop)
        depth = ramp(t, t_drill, t_done)
        lift = ramp(t, t_done + 0.08, t_up)
        if depth > 0:  # the borehole and the core inside it
            hole = y0 + depth * (yb - y0)
            d.rectangle(sc([(x0 - 15, y0), (x0 + 15, hole)]), fill=(92, 132, 176, 255))
            if lift > 0:
                rise = lift * (yb - y0 + 14)
                top_y, bot_y = y0 - rise, yb - rise
                d.rectangle(sc([(x0 - 13, top_y), (x0 + 13, bot_y)]), fill=(222, 238, 250, 255), outline=(90, 140, 190, 255), width=2 * S)
                for k in range(1, 14):
                    yk = top_y + k / 14 * (bot_y - top_y)
                    d.line(sc([(x0 - 12, yk), (x0 + 12, yk)]), fill=(110, 160, 210, 160), width=2 * S)
            else:
                d.rectangle(sc([(x0 - 5, y0 - 150), (x0 + 5, hole)]), fill=(205, 205, 212, 255), outline=(40, 40, 46, 255), width=2 * S)
                d.polygon(sc([(x0 - 11, hole - 8), (x0 + 11, hole - 8), (x0, hole + 10)]), fill=YELLOW + (255,), outline=(60, 45, 0, 255))
        put(top, core_lab, x0 + 140, y0 - 210, a=ramp(t, t_up - 0.1, t_up + 0.1), scale=pop(t, t_up - 0.1))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_bor.mp4")


if __name__ == "__main__":  # skema15.py imports navy() and marker()
    for name in sys.argv[2:] or ["papua", "es", "bor"]:
        globals()[name]()
