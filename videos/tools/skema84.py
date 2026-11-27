"""Image prep, schematic animations and the cover for Titik Heran #84 (run in the episode work dir).
prep: img/H5k.jpg (Arif's Higgsfield H5 cropped on the water falling from the clay pipe, used on "sampai sekarang").
peta: simplified Sultanahmet map (north up, 0,7 px per metre; the shoreline is drawn by hand from approximate
  coordinates, so the shot is tagged "disederhanakan"): Hagia Sophia (41.0083 N, 28.9800 E), the Basilica Cistern
  (41.0081 N, 28.9778 E) with a solid orange line between them (Prof. Gulec: the tunnel running south "leads directly
  to" the cistern), and a dashed line to Topkapi Palace (41.0128 N, 28.9839 E) with a "KONON" pill, drawn on with the
  VO "tembus ke istana sultan" (only a legend; no such tunnel has been found).
kartu: number card from the ministry's 20 Nov 2026 statement: 420 m of tunnels cleared, 9 passages, 6 underground
  rooms (the +-3.000 tons are in the title of the shot before).
penampang: cross-section: Hagia Sophia on the ground, the brick-vaulted tunnels below it; on "got" rain runs off the
  roof down two shafts into the tunnels and flows along them; on "kuno" a pill "saluran air · got air hujan ·
  ventilasi" (the minister via CNN: "water distribution and the drainage of rainwater"; ventilation per Prof. Diker).
cover: img/cover84.jpg from H2 with the title "TEROWONGAN RAHASIA / HAGIA SOPHIA / AKHIRNYA DIBUKA" and a small
  "ilustrasi" tag.
Event times are seconds from the start of each clip, read off `render.py 84 plan`. Text stays out of the watermark
band (y 935-985), the title zone (y < ~600) and the captions (y >= 1210).
usage: python3 skema84.py [prep|peta|kartu|penampang|cover ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed, text_sprite
from skema35 import sheet
from skema37 import to_img, put1, noise
from skema46 import pill, ease, wanted
from skema68 import pulse
from skema74 import backdrop

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
WHITE, ORANGE, BLUE, BRICK = (255, 255, 255), (255, 140, 40), (90, 190, 255), (176, 92, 58)
N = {"peta": 51, "kartu": 53, "penampang": 86}
# from `render.py 84 plan`: see the shot list in the naskah
T_ISTANA, T_SULTAN = 0.64, 1.00                    # peta: "istana sultan,"
T_ROWS = (0.10, 0.45, 0.80)                        # kartu: rows pop through "lumpur untuk membukanya."
T_CUMA, T_GOT, T_KUNO = 1.53, 1.85, 2.09           # penampang
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


# ---------- prep ----------
def prep():
    Image.open("img/H5.jpg").crop((150, 850, 1050, 2450)).resize((1080, 1920), Image.LANCZOS).save("img/H5k.jpg", quality=95)
    print("img/H5k.jpg")


# ---------- map ----------
K, LON0, LAT0, X0, Y0 = 0.7, 28.9800, 41.0083, 560, 1075   # Hagia Sophia at (560, 1075)
HAGIA, CISTERN, TOPKAPI = (28.9800, 41.0083), (28.9778, 41.0081), (28.9839, 41.0128)
# the tip of the historic peninsula, by hand (Golden Horn shore west to east, Sarayburnu, Bosphorus shore south,
# Ahirkapi, Marmara shore west), then closed off-screen
SHORE = [(28.955, 41.0235), (28.962, 41.0226), (28.968, 41.0201), (28.9725, 41.0180), (28.977, 41.0169),
         (28.981, 41.0166), (28.9845, 41.0171), (28.9872, 41.0166), (28.9881, 41.0150), (28.9874, 41.0128),
         (28.9862, 41.0100), (28.9851, 41.0068), (28.9840, 41.0042), (28.9805, 41.0030), (28.9750, 41.0026),
         (28.9700, 41.0021), (28.9650, 41.0023), (28.9580, 41.0031), (28.9500, 41.0040), (28.9400, 41.0040),
         (28.9400, 41.0300), (28.9550, 41.0300)]


def xy(lon, lat):
    return (X0 + (lon - LON0) * 84015 * K, Y0 - (lat - LAT0) * 111000 * K)


def finish(im, top=600):
    a = np.asarray(im, np.float32)
    tex = noise((H, W), [(40, 0.6), (9, 0.4)], 84)[..., None]
    a[..., :3] *= 0.92 + 0.16 * tex
    shade = np.clip(np.maximum((top - YY) / 380, (YY - 1190) / 260), 0, 1)[..., None] * 0.8
    a[..., :3] *= 1 - shade
    return to_img(a).convert("RGBA")


def label(lines):
    return text_sprite(lines, gap=4)


def dot(d, x, y, col, r=13):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,), outline=WHITE + (255,), width=3)


def map_base():
    v = (YY / H)[..., None]
    sea = np.array((12, 44, 72), np.float32) * (1 - v) + np.array((8, 30, 54), np.float32) * v
    base = Image.fromarray(sea.astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    d.polygon([(xy(*q)[0] * S, xy(*q)[1] * S) for q in SHORE], fill=(92, 84, 66, 255), outline=(176, 160, 120, 255))
    base.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    base = finish(base)
    put1(base, label([("Selat", 30, (150, 190, 220), False), ("Bosporus", 30, (150, 190, 220), False)]), 1000, 1150)
    # the tunnel toward the cistern: south from Hagia Sophia, then west (Prof. Gulec), solid orange
    hx, hy = xy(*HAGIA)
    cx, cy = xy(*CISTERN)
    L = Image.new("RGBA", (W * S, H * S))
    dl = ImageDraw.Draw(L)
    path = [(hx, hy), (hx - 8, hy + 40), (hx - 52, hy + 60), (cx + 40, cy + 38), (cx, cy)]
    dl.line([(x * S, y * S) for x, y in path], fill=ORANGE + (255,), width=8 * S, joint="curve")
    base.alpha_composite(L.resize((W, H), Image.LANCZOS))
    d = ImageDraw.Draw(base)
    dot(d, cx, cy, ORANGE, 15)
    dot(d, hx, hy, YELLOW, 18)
    put1(base, label([("HAGIA SOPHIA", 42, WHITE, True)]), hx + 150, hy + 62)
    put1(base, label([("BASILICA CISTERN", 36, ORANGE, True), ("istana Medusa", 30, WHITE, False)]), cx - 150, cy + 80)
    return base


def skema_peta(times=None):
    base = map_base()
    hx, hy = xy(*HAGIA)
    tx, ty = xy(*TOPKAPI)
    konon = pill("KONON", 42, WHITE, (90, 90, 96, 230), (255, 255, 255, 170))
    tk = label([("ISTANA TOPKAPI", 42, WHITE, True), ("istana sultan", 32, YELLOW, False)])
    route = [(hx + 8, hy - 14), (hx + 60, hy - 110), (tx - 20, ty + 60), (tx - 4, ty + 12)]
    rlen = sum(math.dist(a, b) for a, b in zip(route, route[1:]))
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        L = Image.new("RGBA", (W * S, H * S))
        dashed(ImageDraw.Draw(L), route, (235, 235, 235, 230), 6, dash=18, gap=13, upto=ease((t - 0.05) / 0.6) * rlen)
        im.alpha_composite(L.resize((W, H), Image.LANCZOS))
        k = pop(t, 0.15)
        if k > 0:
            put1(im, konon, hx - 60, hy - 200, a=min(1, k), scale=min(k, 1.05))
        if t >= T_ISTANA - 0.05:
            pulse(im, tx, ty, (255, 225, 0), t, T_ISTANA - 0.05)
        kt = pop(t, T_ISTANA)
        if kt > 0:
            s = min(kt, 1.05) * (1 + 0.06 * math.sin(math.pi * min(max((t - T_SULTAN) / 0.3, 0), 1)))
            put1(im, tk, tx - 150, ty - 62, a=min(1, kt), scale=s)
        frames.append(im.convert("RGB"))
    return frames


# ---------- kartu ----------
def skema_kartu(times=None):
    bg = backdrop((40, 26, 18), (10, 8, 6), glow=(40, 24, 10), gy=930)
    panel = Image.new("RGBA", (W * S, H * S))
    ImageDraw.Draw(panel).rounded_rectangle([110 * S, 650 * S, 970 * S, 1185 * S], radius=34 * S,
                                            fill=(14, 12, 10, 215), outline=(255, 225, 0, 150), width=3 * S)
    bg.alpha_composite(panel.resize((W, H), Image.LANCZOS))
    rows = [("420 m", "terowongan dibersihkan", 735), ("9", "lorong", 855), ("6", "ruang bawah tanah", 1045)]
    big = ImageFont.truetype(XB, 88 * S)
    small = ImageFont.truetype(MED, 36 * S)

    def row_sprite(num, txt):
        sp = Image.new("RGBA", (840 * S, 130 * S))
        d = ImageDraw.Draw(sp)
        b = big.getbbox(num)
        d.text((10 * S - b[0], 65 * S - (b[3] + b[1]) / 2), num, font=big, fill=YELLOW + (255,))
        bs = small.getbbox(txt)
        d.text((10 * S + b[2] - b[0] + 30 * S - bs[0], 65 * S - (bs[3] + bs[1]) / 2), txt, font=small, fill=WHITE + (255,))
        return sp
    sprites = [row_sprite(n, t) for n, t, _ in rows]
    foot = label([("Kementerian Kebudayaan & Pariwisata Turki", 26, (200, 190, 170), False), ("20 November 2026", 26, (200, 190, 170), False)])
    frames = []
    for i in range(N["kartu"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        for sp, (_, _, y), t0 in zip(sprites, rows, T_ROWS):
            k = pop(t, t0, 0.28)
            if k > 0:
                put1(im, sp, 540 + 40 * (1 - min(k, 1)), y, a=min(1, k * 1.4), scale=min(k, 1.04))
        kf = ramp(t, 0.9, 1.2)
        if kf > 0:
            put1(im, foot, 540, 1135, a=kf)
        frames.append(im.convert("RGB"))
    return frames


# ---------- penampang ----------
GROUND = 880
TUN_Y0, TUN_Y1 = 1000, 1080            # main tunnel, arched top
SHAFTS = (330, 750)                    # x of the two drain shafts from the roof edges down to the tunnel


def building_layer():
    """Hagia Sophia in profile: main dome, two half domes, the body and buttresses, four thin minarets"""
    L = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(L)
    col, edge = (214, 156, 120, 255), (255, 220, 190, 255)
    for mx in (205, 280, 800, 875):                      # minarets (Ottoman additions, but they make the outline)
        d.rectangle([(mx - 9) * S, 600 * S, (mx + 9) * S, GROUND * S], fill=(230, 210, 190, 255))
        d.polygon([((mx - 11) * S, 602 * S), ((mx + 11) * S, 602 * S), (mx * S, 540 * S)], fill=(150, 150, 160, 255))
        d.rectangle([(mx - 13) * S, 690 * S, (mx + 13) * S, 698 * S], fill=(200, 180, 160, 255))
    d.rectangle([330 * S, 770 * S, 750 * S, GROUND * S], fill=col, outline=edge, width=3 * S)              # body
    d.rectangle([300 * S, 815 * S, 780 * S, GROUND * S], fill=(196, 138, 104, 255), outline=edge, width=3 * S)  # aisles
    for x0, x1 in ((330, 420), (660, 750)):                                                         # half domes
        d.pieslice([x0 * S, 720 * S, x1 * S, 820 * S], 180, 360, fill=(170, 170, 180, 255), outline=edge, width=3 * S)
    d.rectangle([430 * S, 745 * S, 650 * S, 772 * S], fill=col, outline=edge, width=3 * S)              # drum
    d.pieslice([430 * S, 640 * S, 650 * S, 850 * S], 180, 360, fill=(180, 184, 196, 255), outline=edge, width=3 * S)  # dome
    for k in range(9):                                                                              # drum windows
        x = 446 + k * 24
        d.rectangle([x * S, 752 * S, (x + 10) * S, 766 * S], fill=(60, 48, 40, 255))
    f = ImageFont.truetype(XB, 30 * S)
    b = f.getbbox("HAGIA SOPHIA")
    d.text(((540 * S - (b[2] - b[0]) / 2 - b[0]), (846 * S - (b[3] + b[1]) / 2)), "HAGIA SOPHIA", font=f, fill=(60, 36, 24, 255))
    return L.resize((W, H), Image.LANCZOS)


def tunnel_layer():
    """brick-vaulted tunnels in the soil: one long tunnel, two shafts up to the roof edges, two side rooms"""
    L = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(L)
    inside, rim = (26, 16, 12, 255), BRICK + (255,)

    def vault(x0, y0, x1, y1):
        r = (y1 - y0) * 0.55
        d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=int(r * S), fill=inside, outline=rim, width=7 * S)
        d.rectangle([(x0 + 4) * S, (y0 + r) * S, (x1 - 4) * S, (y1 - 4) * S], fill=inside)
        d.line([(x0 * S, y1 * S), (x1 * S, y1 * S)], fill=rim, width=7 * S)
    vault(90, TUN_Y0, 990, TUN_Y1)
    vault(150, 950, 260, TUN_Y0 + 10)
    vault(830, 950, 940, TUN_Y0 + 10)
    for x in SHAFTS:
        d.rectangle([(x - 13) * S, (GROUND - 2) * S, (x + 13) * S, (TUN_Y0 + 8) * S], fill=inside, outline=rim, width=5 * S)
    # brick joints on the rim
    for x in range(100, 990, 26):
        d.line([(x * S, (TUN_Y0 - 3) * S), (x * S, (TUN_Y0 + 4) * S)], fill=(90, 46, 30, 255), width=2 * S)
    return L.resize((W, H), Image.LANCZOS)


def section_base():
    sky = backdrop((18, 26, 44), (30, 36, 52))
    a = np.asarray(sky, np.float32).copy()
    soil = np.array((92, 64, 42), np.float32) * (0.85 + 0.25 * noise((H, W), [(30, 0.5), (7, 0.5)], 41))[..., None]
    deep = np.clip((YY - GROUND) / 500, 0, 1)[..., None]
    soil = soil * (1 - 0.45 * deep)
    m = (YY >= GROUND)[..., None]
    a[..., :3] = np.where(m, soil, a[..., :3])
    im = to_img(a).convert("RGBA")
    ImageDraw.Draw(im).line([(0, GROUND), (W, GROUND)], fill=(150, 120, 80, 255), width=4)
    return im


def skema_penampang(times=None):
    base = section_base()
    bld = building_layer()
    tun = tunnel_layer()
    rng = np.random.default_rng(84)
    drops = [(rng.uniform(250, 830), rng.uniform(0, 1)) for _ in range(40)]
    tag = pill("saluran air · got air hujan · ventilasi", 30, (20, 20, 20), YELLOW + (245,), (255, 255, 255, 220))
    frames = []
    for i in range(N["penampang"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        kb = ramp(t, 0.0, 0.45)
        if kb > 0:
            b = bld.copy()
            b.putalpha(b.getchannel("A").point(lambda v: int(v * kb)))
            im.alpha_composite(b, (0, int(20 * (1 - kb))))
        u = ramp(t, 0.35, 1.3)                       # the tunnels are dug out from left to right
        if u > 0:
            tl = tun.copy()
            a = np.asarray(tl.getchannel("A"), np.float32) * np.clip((80 + u * 1000 - XX) / 80, 0, 1)
            tl.putalpha(Image.fromarray(a.astype(np.uint8)))
            im.alpha_composite(tl)
        if t >= T_GOT - 0.15:                         # rain, run-off down the shafts, flow along the tunnel
            tw = t - (T_GOT - 0.15)
            L = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(L)
            for x, ph in drops:
                y = 610 + ((tw * 1.6 + ph) % 1.0) * 230
                if y < 735 or abs(x - 540) > 110 or y < 690:
                    d.line([(x * S, y * S), ((x - 3) * S, (y + 18) * S)], fill=(160, 210, 255, 200), width=3 * S)
            fill = ease(tw / 0.35)
            for x in SHAFTS:
                y1 = GROUND + (TUN_Y0 + 40 - GROUND) * fill
                d.line([(x * S, (GROUND - 30) * S), (x * S, y1 * S)], fill=BLUE + (235,), width=10 * S)
            if fill >= 1:
                for k in range(16):                  # dashes running left along the tunnel floor
                    x = 980 - ((tw * 260 + k * 60) % 900)
                    d.line([(x * S, 1060 * S), ((x - 34) * S, 1060 * S)], fill=BLUE + (240,), width=9 * S)
                d.line([(100 * S, 1066 * S), (980 * S, 1066 * S)], fill=BLUE + (110,), width=12 * S)
            im.alpha_composite(L.resize((W, H), Image.LANCZOS))
        k = pop(t, T_KUNO, 0.3)
        if k > 0:
            put1(im, tag, 540, 1140, a=min(1, k), scale=min(k, 1.05))
        frames.append(im.convert("RGB"))
    return frames


# ---------- cover ----------
def cover():
    im = Image.open("img/H2.jpg").convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")
    a = np.asarray(im, np.float32)
    a[..., :3] *= 1 - np.clip((820 - YY) / 560, 0, 1)[..., None] * 0.55
    im = to_img(a).convert("RGBA")
    t = text_sprite([("TEROWONGAN RAHASIA", 70, WHITE, True), ("HAGIA SOPHIA", 112, YELLOW, True),
                     ("AKHIRNYA DIBUKA", 70, WHITE, True)], gap=10)
    put1(im, t, 540, 430)
    put1(im, pill("ilustrasi", 24, WHITE), 960, 1860)
    im.convert("RGB").save("img/cover84.jpg", quality=93)
    print("img/cover84.jpg")


if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or ["prep", "peta", "kartu", "penampang", "cover"]
    fns = {"peta": skema_peta, "kartu": skema_kartu, "penampang": skema_penampang}
    for name in todo:
        if name in ("prep", "cover"):
            {"prep": prep, "cover": cover}[name]()
            continue
        fr = fns[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, f"clips/skema_{name}.mp4")
