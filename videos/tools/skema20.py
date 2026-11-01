"""Schematic animations for Titik Heran #20 (run in the episode work dir; writes clips/skema_sengat.mp4, skema_gerigi.mp4, skema_kabur.mp4,
skema_pompa.mp4, skema_menit.mp4 and skema_kerok.mp4).
usage: python3 skema20.py [sengat|gerigi|kabur|pompa|menit|kerok ...] [--sheet out.jpg t1,t2,...]   (--sheet saves those frames as a contact sheet)
skema_sengat: a cross-section of human skin with a honeybee sting left behind: the bee is gone, the venom sac pulses and venom spreads.
skema_gerigi: the stinger close up: its lancets carry barbs that point back, so they catch in elastic skin when the bee pulls.
skema_kabur: the bee flies off, the sting stays in the skin with its venom sac (torn from the abdomen), and the bee dies.
skema_pompa: the sting as a pump (Ramirez-Esquivel et al. 2026, PNAS): the valve on each lancet opens like a parachute on the down stroke
and pushes venom down the canal, then folds to slide back up; the two work in turn, like a double piston.
skema_menit: a stopwatch runs to 1:00; the strong pumping lasts 15-70 s (UNSW).
skema_kerok: a fingernail scrapes the sting sideways out of the skin (Visscher et al. 1996: speed matters more than the method).
Simplified and not to scale. Event times are seconds from the start of each shot, read off `render.py 20 plan`.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, BOLD, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, chaikin, encode, glow_sprite
from skema13 import navy
from skema17 import label, arrow

SURF, EPI, DER, FAT = 830, 910, 1150, 1280  # skin surface and the layer boundaries, 1x
SX = 540  # where the sting goes in
VENOM, RED, GREEN, CYAN, ORANGE = (196, 240, 70), (255, 84, 64), (110, 225, 120), (120, 220, 255), (255, 150, 40)
SHAFT, PLATE, SAC = (64, 40, 22), (178, 114, 48), (244, 236, 172)


def rot(pts, ang, cx=0.0, cy=0.0):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def ell(rx, ry, n=48):
    return [(rx * math.cos(2 * math.pi * k / n), ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def ell_slice(rx, ry, u0, u1, n=12):
    """the part of an ellipse between u0 and u1 along its long axis, as a polygon"""
    us = [u0 + (u1 - u0) * k / n for k in range(n + 1)]
    top = [(u, -ry * math.sqrt(max(0.0, 1 - (u / rx) ** 2))) for u in us]
    return top + [(u, -y) for u, y in reversed(top)]


# ---------- the skin cross-section ----------
def skin_rgba(surf_fn=None):
    """epidermis, dermis and fat under the surface, fading out below FAT, as a 1x RGBA layer;
    surf_fn(x) can lift the surface (a tent where the sting pulls)"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    surf = SURF - (surf_fn(xx) if surf_fn else 0)
    lift = SURF - surf  # the layers below follow the tent, less with depth
    y = yy + lift * np.clip(1 - (yy - SURF) / 260, 0, 1)
    epi = EPI + 9 * np.sin(xx / 44.0) + 4 * np.sin(xx / 13.0 + 1)
    der = DER + 12 * np.sin(xx / 92.0 + 2)
    depth = np.clip((y - EPI) / (DER - EPI), 0, 1)[..., None]
    col = np.where((y < epi)[..., None], np.array([240, 202, 176]) - 14 * np.clip((y - SURF) / 70, 0, 1)[..., None],
                   np.where((y < der)[..., None], np.array([224, 142, 132]) * (1 - depth) + np.array([206, 120, 114]) * depth,
                            np.array([242, 216, 150])))
    a = np.where(yy >= surf, 1.0, 0.0) * np.clip(1 - (yy - FAT) / 60, 0, 1)
    im = Image.fromarray(np.dstack([np.clip(col, 0, 255), a * 255]).astype(np.uint8), "RGBA")
    tex = layer()
    d = ImageDraw.Draw(tex)
    rng = np.random.default_rng(20)
    for _ in range(46):  # fat cells
        x, yc, r = rng.uniform(20, W - 20), rng.uniform(DER + 26, FAT + 30), rng.uniform(17, 27)
        d.ellipse(sc([(x - r, yc - r), (x + r, yc + r)]), outline=(222, 188, 114, 150), width=3 * S)
    for k in range(9):  # collagen fibres in the dermis
        y0 = EPI + 40 + k * 19
        pts = [(x, y0 + 7 * math.sin(x / 61 + k)) for x in range(-20, W + 40, 20)]
        d.line(sc(pts), fill=(196, 110, 104, 90), width=3 * S, joint="curve")
    pts = [(x, EPI + 9 * math.sin(x / 44.0) + 4 * math.sin(x / 13.0 + 1)) for x in range(0, W + 8, 6)]
    d.line(sc(pts), fill=(206, 150, 136, 200), width=3 * S)
    tex = down(tex)
    tex.putalpha(Image.fromarray(np.minimum(np.array(tex.getchannel("A"), np.float32), a * 255).astype(np.uint8)))
    im.alpha_composite(tex)
    top = layer()
    xs = list(range(0, W + 8, 6))
    ys = [SURF - (float(surf_fn(np.float32(x))) if surf_fn else 0) for x in xs]
    ImageDraw.Draw(top).line(sc(list(zip(xs, ys))), fill=(196, 140, 112, 255), width=5 * S)
    im.alpha_composite(down(top))
    return im


def backdrop(lab=True):
    bg = navy(540, 760)
    bg.alpha_composite(skin_rgba())
    if lab:
        put_1x(bg, text_sprite([("kulit", 30, WHITE, True)]), 105, SURF + 44)
    return bg


def put_1x(base, sprite, cx, cy, a=1.0):
    """put() for a 1x base: the 2x sprite is scaled down first"""
    sp = sprite.resize((sprite.width // S, sprite.height // S), Image.LANCZOS)
    if a < 1:
        sp = fade(sp, a)
    base.alpha_composite(sp, (round(cx - sp.width / 2), round(cy - sp.height / 2)))


# ---------- the sting apparatus, in its own frame: origin where it enters the skin, +y down the shaft ----------
K = 1.3  # drawn this much bigger than its frame units


def hw(y, top=7.0, tip=212.0):
    return top * max(0.0, (tip - y) / (tip + 40)) ** 0.8


def sting(d, x0, y0, ang=0.0, pulse=0.0, a=255, up=1.0, drops=(), cut=False, k=K):
    """draw the sting at (x0, y0) on a 2x layer, turned by ang; pulse swells the venom sac; up: opacity of the parts above the
    skin (sac, muscle plates); drops are positions along the shaft (0 = bulb, 1 = tip) of venom drops; cut: torn tissue on the sac"""
    def tr(pts):
        return sc(rot([(x * k, y * k) for x, y in pts], ang, x0, y0))

    def oval(cx, cy, rx, ry, n=28):
        return tr([(cx + rx * math.cos(2 * math.pi * j / n), cy + ry * math.sin(2 * math.pi * j / n)) for j in range(n)])
    au = round(a * up)
    ys = [-40, 0, 40, 80, 120, 160, 190, 212]
    shaft = [(-hw(y), y) for y in ys] + [(hw(y), y) for y in reversed(ys)]
    if au > 0:
        for sgn in (-1, 1):  # muscle plates either side of the bulb
            d.polygon(tr([(sgn * 8, -34), (sgn * 40, -50), (sgn * 44, -72), (sgn * 14, -64)]), fill=PLATE + (au,), outline=(120, 70, 30, au))
    d.polygon(tr(shaft), fill=SHAFT + (a,))
    d.line(tr([(-1.5, -36), (-1, 150)]), fill=(140, 100, 60, a), width=2 * S)
    for y in range(42, 200, 22):  # barbs pointing back up the shaft
        for sgn in (-1, 1):
            e = sgn * hw(y)
            d.polygon(tr([(e, y), (e + sgn * 6, y - 12), (sgn * hw(y - 7), y - 7)]), fill=SHAFT + (a,))
    if au > 0:
        d.polygon(oval(0, -52, 12, 18), fill=(96, 60, 30, au))  # the bulb
        r = 1 + pulse
        d.line(tr([(4, -64), (6, -80)]), fill=(200, 190, 120, au), width=round(6 * k) * S)
        d.polygon(oval(6, -126, 34 * r, 46 * (1 + 0.5 * pulse), 40), fill=SAC + (round(au * 0.86),), outline=(214, 200, 120, au))
        d.polygon(oval(-6, -140, 9, 16, 16), fill=(255, 255, 240, round(au * 0.7)))
        d.polygon(oval(-22, -96, 8, 8, 16), fill=(250, 244, 232, au))  # ganglion
        if cut:
            for j, dx in enumerate((-10, 2, 14)):
                d.line(tr([(dx, -168), (dx + 4 * math.sin(j + 1), -182), (dx - 3, -194 + 3 * j)]), fill=(240, 186, 186, au), width=3 * S)
    for p in drops:
        y = -40 + p * 248
        d.polygon(oval(0, y, 5, 5, 12), fill=VENOM + (a,))


def venom_cloud(base, r, a, x=SX, y=SURF + 196 * K, red=0.0):
    """venom spreading round the tip and redness round the wound, clipped to the skin (base is 1x)"""
    lay = layer()
    if red > 0:
        put(lay, glow_sprite(int(70 + 90 * red), RED), x, SURF + 70, a=0.5 * red)
    if a > 0:
        put(lay, glow_sprite(max(8, int(r)), VENOM), x, y, a=a)
    ImageDraw.Draw(lay).rectangle([0, 0, W * S, (SURF + 3) * S], fill=(0, 0, 0, 0))
    base.alpha_composite(down(lay))


# ---------- the bee, side view, facing left, sting point at the origin ----------
def bee_sprite(wing=0.0, grey=False, legs=True):
    R = 300
    im = Image.new("RGBA", (2 * R * S, 2 * R * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def tr(pts):
        return [((R + x) * S, (R + y) * S) for x, y in pts]
    if legs:
        for p in ([(-104, -150), (-150, -88), (-166, 0)], [(-82, -144), (-110, -70), (-110, 0)], [(-62, -146), (-46, -66), (-70, 0)]):
            d.line(tr(p), fill=(54, 36, 22, 255), width=6 * S, joint="curve")
    ang = math.atan2(150, 50)  # abdomen axis: petiole (-50, -150) to the tip (0, 0)
    ab = ell(79, 46)
    d.polygon(tr(rot(ab, ang, -25, -75)), fill=(220, 154, 42, 255))
    for u0, u1 in ((-38, -22), (-4, 12), (30, 46), (60, 79)):
        d.polygon(tr(rot(ell_slice(79, 46, u0, u1), ang, -25, -75)), fill=(66, 42, 22, 255))
    d.polygon(tr(rot(ab, ang, -25, -75)), outline=(70, 46, 24, 255), width=3 * S)
    th = [(-78 + 44 * math.cos(k * math.pi / 18) * (1 + 0.06 * math.sin(5 * k)), -182 + 44 * math.sin(k * math.pi / 18) * (1 + 0.06 * math.sin(5 * k)))
          for k in range(36)]
    d.polygon(tr(th), fill=(132, 90, 44, 255), outline=(196, 156, 92, 255), width=4 * S)
    d.polygon(tr(rot(ell(30, 34), 0, -138, -186)), fill=(58, 40, 26, 255))
    d.polygon(tr(rot(ell(13, 21), 0.2, -132, -192)), fill=(24, 20, 18, 255))
    d.ellipse(tr([(-136, -206), (-128, -198)]), fill=(200, 200, 210, 255))
    for p in ([(-150, -212), (-176, -246), (-200, -252)], [(-142, -214), (-160, -254), (-178, -268)]):
        d.line(tr(p), fill=(44, 30, 20, 255), width=4 * S, joint="curve")
    for (cx, cy, rx, ry, a0) in ((-6, -250, 78, 26, -0.35), (-20, -234, 54, 18, -0.2)):  # wings, hinged at (-70, -222)
        pts = rot(rot(ell(rx, ry), a0, cx + 70, cy + 222), wing, -70, -222)
        d.polygon(tr(pts), fill=(226, 238, 255, 120), outline=(255, 255, 255, 190), width=2 * S)
    if grey:
        g = ImageOps.grayscale(im.convert("RGB")).point(lambda v: int(v * 0.8 + 30))
        im = Image.merge("RGBA", (g, g, g, im.getchannel("A")))
    return im


def put_bee(lay, sp, x, y, a=1.0, ang=0.0):
    """the bee sprite with its sting point at (x, y), turned by ang (radians, clockwise)"""
    if a <= 0.01:
        return
    if ang:
        sp = sp.rotate(-math.degrees(ang), resample=Image.BICUBIC)
    put(lay, sp, x, y, a=a)


# ---------- skema_sengat ----------
def sengat(times):
    bg = backdrop()
    ghost = fade(bee_sprite(), 0.5)
    lab = label([("sengat", 30, WHITE, True)])
    lab_v = label([("racun", 30, VENOM, True)])
    # tapi 0.03, sengatnya 0.38, masih 1.22, menyerangmu 1.61
    t_lab, t_pump, t_v = 0.38, 1.22, 1.61
    frames = []
    for t in times:
        im = bg.copy()
        pump = ramp(t, t_pump, t_pump + 0.2)
        venom_cloud(im, 30 + 90 * ramp(t, t_pump, 2.6), 0.85 * ramp(t, t_pump + 0.1, t_pump + 0.5), red=ramp(t, t_v, 2.6))
        top = layer()
        d = ImageDraw.Draw(top)
        u = ramp(t, 0.0, 0.9)
        put_bee(top, ghost, SX + 330 * u, SURF - 210 * u, a=0.6 * (1 - u), ang=-0.25 * u)
        drops = [((t - t_pump) * 1.6 + k / 4) % 1 for k in range(4)] if t > t_pump else []
        sting(d, SX, SURF, pulse=0.1 * pump * (0.5 + 0.5 * math.sin(2 * math.pi * 2.6 * (t - t_pump))), drops=drops, cut=True)
        d.line(sc([(SX - 190, 1000), (SX - 14, 1000)]), fill=(255, 255, 255, round(200 * ramp(t, t_lab, t_lab + 0.15))), width=3 * S)
        put(top, lab, SX - 270, 1000, a=ramp(t, t_lab, t_lab + 0.15), scale=pop(t, t_lab))
        put(top, lab_v, SX + 250, SURF + 196, a=ramp(t, t_v + 0.1, t_v + 0.3), scale=pop(t, t_v + 0.1))
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


# ---------- skema_gerigi: the stinger close up ----------
GT, GB, GW = 560, 1236, 66  # top and tip of the big shaft, half-width at the top


def ghw(y):
    return GW * max(0.0, (GB - y) / (GB - GT)) ** 0.85


def barbs():
    """(y, side) of the barbs on the big shaft, from the tip up"""
    return [(y, s) for y in range(1190, 740, -50) for s in (-1, 1)]


def big_shaft(dy, glow_t=None, hook=0.0):
    """the magnified shaft as a 2x layer, fading out towards the title; glow_t runs a highlight up the barbs, hook reddens
    the barbs inside the skin"""
    lay = layer()
    d = ImageDraw.Draw(lay)
    ys = list(range(GT, GB + 1, 12))
    d.polygon(sc([(540 - ghw(y), y + dy) for y in ys] + [(540 + ghw(y), y + dy) for y in reversed(ys)]), fill=(86, 56, 30, 255),
              outline=(150, 110, 70, 255), width=3 * S)
    d.polygon(sc([(540 - 0.28 * ghw(y), y + dy) for y in ys] + [(540 + 0.28 * ghw(y), y + dy) for y in reversed(ys)]), fill=(58, 36, 20, 255))
    d.line(sc([(540 - 0.62 * ghw(y), y + dy) for y in ys[:-6]]), fill=(150, 108, 66, 255), width=3 * S)
    for k, (y, s) in enumerate(barbs()):
        e = 540 + s * ghw(y)
        pts = [(e, y + dy), (e + s * 32, y - 44 + dy), (540 + s * ghw(y - 18), y - 18 + dy)]
        d.polygon(sc(pts), fill=(86, 56, 30, 255), outline=(150, 110, 70, 255), width=3 * S)
        g = 0.0 if glow_t is None else math.exp(-((glow_t - 0.06 * (k // 2)) / 0.16) ** 2)
        col = YELLOW
        if hook > 0 and y + dy > SURF + 20:
            g, col = max(g, hook), RED
        if g > 0.02:
            d.line(sc(pts + pts[:1]), fill=col + (round(255 * g),), width=5 * S, joint="curve")
    m = np.clip((np.arange(H * S, dtype=np.float32) / S - GT - 10) / 90, 0, 1)
    a = np.array(lay.getchannel("A"), np.float32) * m[:, None]
    lay.putalpha(Image.fromarray(a.astype(np.uint8)))
    return lay


def gerigi(times):
    bg = navy(540, 900)
    lab = label([("gerigi", 32, YELLOW, True), ("mengarah ke belakang", 26, WHITE, False)])
    lab_z = text_sprite([("diperbesar", 30, WHITE, False)])
    pull = label([("ditarik", 30, WHITE, True)])
    # Sengat 0.02, bergerigi 0.86, jadi 1.79, tersangkut 2.02, di 2.48, kulit 2.60
    t_b, t_skin, t_pull = 0.86, 1.79, 2.02
    frames = []
    for t in times:
        im = bg.copy()
        tug = ramp(t, t_pull, t_pull + 0.3) - 0.6 * ramp(t, t_pull + 0.62, t_pull + 0.85)
        dy = -30 * tug
        sv = ramp(t, t_skin, t_skin + 0.35)
        if sv > 0:
            sk = skin_rgba(lambda x: 34 * tug * np.exp(-((x - 540) / 100.0) ** 2))
            im.alpha_composite(fade(sk, sv))
        top = layer()
        d = ImageDraw.Draw(top)
        reveal = ramp(t, 0.0, 0.5)
        top.alpha_composite(big_shaft(dy + 700 * (1 - reveal) ** 2, glow_t=t - t_b if t > t_b - 0.3 else None,
                                      hook=ramp(t, t_pull + 0.2, t_pull + 0.3) * (1 - 0.5 * ramp(t, t_pull + 0.7, t_pull + 0.9))))
        y, s = barbs()[7]
        la = ramp(t, t_b + 0.2, t_b + 0.4) * (1 - ramp(t, t_skin - 0.1, t_skin + 0.1))
        if la > 0:
            d.line(sc([(540 + ghw(y) + 36, y - 30), (780, y - 30)]), fill=(255, 255, 255, round(210 * la)), width=3 * S)
            put(top, lab, 860, y - 30, a=la, scale=pop(t, t_b + 0.2))
        put(top, lab_z, 150, 640, a=ramp(t, 0.2, 0.5) * (1 - ramp(t, t_skin, t_skin + 0.2)))
        pa = ramp(t, t_pull - 0.05, t_pull + 0.1) * (1 - ramp(t, 2.95, 3.1))
        if pa > 0:
            arrow(d, [(720, 810 + dy), (720, 680 + dy)], (255, 255, 255, round(240 * pa)), 9, upto=ramp(t, t_pull - 0.05, t_pull + 0.25), head=34)
            put(top, pull, 840, 745 + dy, a=pa)
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


# ---------- skema_kabur ----------
def kabur(times):
    bg = backdrop()
    def small(sp, k=0.85):  # a little smaller than in skema_sengat, so it can hover below the title
        return sp.resize((round(sp.width * k), round(sp.height * k)), Image.LANCZOS)
    bees = [small(bee_sprite(w)) for w in (0.0, -0.5, 0.35)]
    dead = small(bee_sprite(0.0, grey=True))
    lab_s = label([("sengat", 30, WHITE, True)])
    lab_k = label([("kantong racun", 30, WHITE, True)])
    # sengatnya 0.05, tercabut 0.55, bersama 1.17, kantong 1.48, racun 1.75, Lebahnya 2.43, pun 2.97, mati 3.21
    t_go, t_snap, t_s, t_k, t_dead, t_fall = 0.5, 1.05, 1.17, 1.48, 2.43, 2.97
    hover = (SX + 340, SURF - 80)  # kept low and to the right, clear of the two-line title above
    frames = []
    for i, t in enumerate(times):
        im = bg.copy()
        venom_cloud(im, 30 + 50 * ramp(t, 1.0, 3.9), 0.7 * ramp(t, 1.2, 1.8), red=0.6 * ramp(t, 1.4, 3.9))
        top = layer()
        d = ImageDraw.Draw(top)
        u = ramp(t, t_go, t_go + 0.9)
        bx, by = SX + (hover[0] - SX) * u, SURF + (hover[1] - SURF) * u
        if t > t_go + 0.9:
            by += 8 * math.sin(2 * math.pi * 1.4 * (t - t_go - 0.9)) * (1 - ramp(t, t_dead, t_dead + 0.2))
        tip = rot([(0, 0)], -0.3 * u, bx, by)[0]
        sting(d, SX, SURF, pulse=0.06 * math.sin(2 * math.pi * 2.6 * t) * ramp(t, 1.2, 1.5), cut=t > t_snap, up=ramp(t, t_go, t_go + 0.3),
              drops=[((t - 1.2) * 1.6 + k / 4) % 1 for k in range(4)] if t > 1.2 else [])
        if t_go < t <= t_snap + 0.15:  # the torn tissue stretches between the sac and the leaving abdomen, then snaps
            stretch = ramp(t, t_go, t_snap)
            back = ramp(t, t_snap, t_snap + 0.15)
            for k, dx in enumerate((-12, 2, 16)):
                p0 = (SX + (6 + dx * 0.6) * K, SURF - 168 * K)
                p1 = (tip[0] + dx * 0.4, tip[1] - 6)
                end = (p0[0] + (p1[0] - p0[0]) * (1 - back) * 0.5, p0[1] + (p1[1] - p0[1]) * (1 - back) * 0.5) if t > t_snap else p1
                mid = ((p0[0] + end[0]) / 2 + 10 * math.sin(k + 3 * stretch), (p0[1] + end[1]) / 2)
                d.line(sc([p0, mid, end]), fill=(240, 186, 186, 230), width=(4 - k % 2) * S, joint="curve")
        if t < t_dead:
            sp = bees[0] if u == 0 else bees[1 + i % 2]
            put_bee(top, sp, bx, by, ang=-0.3 * u)
        else:  # it stops, turns grey and drops away
            g = ramp(t, t_dead, t_dead + 0.3)
            fall = ramp(t, t_fall, t_fall + 0.8)
            fx, fy = bx + 90 * fall, by + 150 * fall * fall
            put_bee(top, bees[0], fx, fy, a=1 - g, ang=-0.3 + 2.4 * fall)
            put_bee(top, dead, fx, fy, a=g * (1 - ramp(t, t_fall + 0.4, t_fall + 0.8)), ang=-0.3 + 2.4 * fall)
        for t0, lab, (lx, ly), (ax, ay) in ((t_s, lab_s, (SX - 270, 1000), (SX - 14, 1000)), (t_k, lab_k, (SX - 310, SURF - 164), (SX - 40, SURF - 164))):
            a = ramp(t, t0, t0 + 0.15)
            if a > 0:
                d.line(sc([(lx + 90, ly), (ax, ay)]), fill=(255, 255, 255, round(200 * a)), width=3 * S)
                put(top, lab, lx, ly, a=a, scale=pop(t, t0))
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


# ---------- skema_pompa: the sting as a double-piston pump ----------
PT, PJ, PTIP = 612, 905, 1258  # top of the bulb, where it narrows into the canal, the tip
P_SURF = 1085  # the skin surface in this close-up


def pw(y):
    """inner half-width of the bulb and canal at y"""
    if y <= PJ:
        u = min(max((y - PT) / (PJ - PT), 0.0), 1.0)
        return 170 - 124 * u ** 1.5
    return 46 - 38 * ((y - PJ) / (PTIP - PJ)) ** 0.9


def rod_x(y):
    """distance of each lancet from the middle: along the bulb wall, then side by side down the canal"""
    return max(pw(y) - 22, 0.45 * pw(y))


def valve(d, side, yv, opened, col):
    """a valve hinged on the lancet at yv: open, it spans the chamber like a parachute (concave side down);
    folded, it hangs along the lancet as a narrow leaf"""
    xr = 540 + side * rod_x(yv)
    span = 2 * pw(yv) - 50
    fs = [k / 18 for k in range(19)]
    op = [(xr - side * span * f, yv - 46 * math.sin(math.pi * f) + 4 * f) for f in fs] + \
         [(xr - side * span * f, yv + 6 - 18 * math.sin(math.pi * f) + 4 * f) for f in reversed(fs)]
    fo = [(xr - side * 26 * math.sin(math.pi * f), yv + 96 * f) for f in fs] + \
         [(xr - side * 3 * math.sin(math.pi * f), yv + 96 * f) for f in reversed(fs)]
    pts = [(x1 + (x0 - x1) * opened, y1 + (y0 - y1) * opened) for (x0, y0), (x1, y1) in zip(op, fo)]
    d.polygon(sc(pts), fill=col + (255,), outline=(16, 24, 44, 255), width=3 * S)
    d.ellipse(sc([(xr - 12, yv - 12), (xr + 12, yv + 12)]), fill=(40, 28, 18, 255), outline=(16, 24, 44, 255), width=2 * S)


def badge_sprite(n, col):
    b = Image.new("RGBA", (72 * S, 72 * S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(b)
    bd.ellipse([3 * S, 3 * S, 69 * S, 69 * S], fill=(10, 22, 48, 235), outline=col + (255,), width=4 * S)
    bd.text((36 * S, 37 * S), str(n), font=ImageFont.truetype(BOLD, 40 * S), fill=col + (255,), anchor="mm")
    return b


def pompa(times):
    bg = navy(540, 860)
    sk = skin_rgba()
    sk = sk.transform(sk.size, Image.AFFINE, (1, 0, 0, 0, 1, SURF - P_SURF), resample=Image.BICUBIC)  # the skin, moved down to P_SURF
    bg.alpha_composite(sk)
    lab_v = label([("racun", 32, VENOM, True)])
    lab_p = label([("2 katup bergantian", 30, WHITE, True), ("= 2 piston", 34, YELLOW, True)])
    badge = {-1: badge_sprite(1, CYAN), 1: badge_sprite(2, ORANGE)}
    ys = list(range(PT, PTIP + 1, 6))
    inner = [(540 - pw(y), y) for y in ys] + [(540 + pw(y), y) for y in reversed(ys)]
    outer = [(540 - pw(y) - 16, y) for y in ys] + [(540 + pw(y) + 16, y) for y in reversed(ys)]
    rng = np.random.default_rng(7)
    parts = [(rng.uniform(0, 1), rng.uniform(-0.8, 0.8)) for _ in range(54)]
    P = 0.9  # seconds per pump cycle: one down stroke for each valve
    # sengat 0.03, terus 0.65, memompa 1.04, racun 1.42, sendiri 1.66, seperti 2.35, mesin 2.66, dua 2.93, piston 3.13
    t_v, t_badge, t_lab = 1.42, 2.35, 2.93
    frames = []
    for t in times:
        im = bg.copy()
        venom_cloud(im, 50 + 90 * ramp(t, 0.0, 3.9), 0.8, x=540, y=PTIP + 14, red=0)
        top = layer()
        d = ImageDraw.Draw(top)
        sq = 1 + 0.05 * math.sin(4 * math.pi * t / P)
        d.polygon(sc([(540 - 196 * math.cos(k * math.pi / 30), PT + 6 - 62 * sq * math.sin(k * math.pi / 30)) for k in range(61)]),
                  fill=SAC + (220,), outline=(214, 200, 120, 255))  # the venom sac on top of the bulb
        d.polygon(sc(outer), fill=SHAFT + (255,))
        d.polygon(sc(inner), fill=(168, 190, 72, 255))
        # venom flowing down in pulses, one per down stroke
        flow = 0.16 * t + 0.22 * (t / 2 - math.sin(4 * math.pi * t / P) * P / (8 * math.pi))
        for s0, lat in parts:
            s = (s0 + flow) % 1
            y = PT + 30 + s * (PTIP - PT - 40)
            x = 540 + lat * pw(y) * 0.8
            r = 7 if y < PJ else 6
            d.ellipse(sc([(x - r, y - r), (x + r, y + r)]), fill=VENOM + (255,), outline=(90, 110, 30, 255), width=S)
        for k in range(6):  # drops leaving the tip into the skin
            f = (t * 1.3 + k / 6) % 1
            ang = math.pi / 2 + (k - 2.5) * 0.45
            x, y = 540 + math.cos(ang) * 110 * f, PTIP + 6 + math.sin(ang) * 110 * f
            d.ellipse(sc([(x - 7, y - 7), (x + 7, y + 7)]), fill=VENOM + (round(240 * (1 - f)),))
        for side, ph, col in ((-1, 0.0, CYAN), (1, math.pi, ORANGE)):
            phi = 2 * math.pi * t / P + ph
            yv = 760 - 70 * math.cos(phi)  # the lancet slides up and down
            opened = min(max(math.sin(phi) * 2.5 + 0.5, 0.0), 1.0)  # open on the way down
            rod = [(540 + side * rod_x(y), y) for y in range(max(PT + 8, int(yv) - 120), PTIP - 30, 8)]
            d.line(sc(rod), fill=(52, 32, 18, 255), width=10 * S, joint="curve")
            valve(d, side, yv, opened, col)
            ba = ramp(t, t_badge, t_badge + 0.15)
            if ba > 0:
                put(top, badge[side], 540 + side * (pw(yv) + 64), yv, a=ba, scale=pop(t, t_badge))
        a = ramp(t, t_v, t_v + 0.15)
        if a > 0:
            d.line(sc([(580, 1000), (790, 1000)]), fill=(255, 255, 255, round(200 * a)), width=3 * S)
            put(top, lab_v, 870, 1000, a=a, scale=pop(t, t_v))
        put(top, lab_p, 196, 990, a=ramp(t, t_lab, t_lab + 0.15), scale=pop(t, t_lab))
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


# ---------- skema_menit: the stopwatch ----------
def menit(times):
    cx, cy, R = 540, 905, 225
    bg = navy(cx, cy)
    face = layer()
    d = ImageDraw.Draw(face)
    d.rounded_rectangle(sc([(cx - 34, cy - R - 64), (cx + 34, cy - R - 30)]), radius=10 * S, fill=(220, 226, 236, 255))
    d.rectangle(sc([(cx - 12, cy - R - 32), (cx + 12, cy - R + 4)]), fill=(200, 206, 216, 255))
    bx, by = cx + (R + 16) * math.cos(-math.pi / 4), cy + (R + 16) * math.sin(-math.pi / 4)
    d.polygon(sc(rot([(-12, -26), (12, -26), (12, 4), (-12, 4)], math.pi / 4, bx, by)), fill=(200, 206, 216, 255))
    d.ellipse(sc([(cx - R - 16, cy - R - 16), (cx + R + 16, cy + R + 16)]), fill=(232, 236, 244, 255))
    d.ellipse(sc([(cx - R, cy - R), (cx + R, cy + R)]), fill=(10, 26, 56, 255))
    f = ImageFont.truetype(BOLD, 30 * S)
    for k in range(60):
        a = 2 * math.pi * k / 60 - math.pi / 2
        r0 = R - (30 if k % 5 == 0 else 16)
        d.line(sc([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + (R - 6) * math.cos(a), cy + (R - 6) * math.sin(a))]),
               fill=(255, 255, 255, 230 if k % 5 == 0 else 120), width=(4 if k % 5 == 0 else 2) * S)
        if k % 15 == 0:
            n = 60 if k == 0 else k
            d.text(((cx + (R - 62) * math.cos(a)) * S, (cy + (R - 62) * math.sin(a)) * S), str(n), font=f, fill=(255, 255, 255, 230), anchor="mm")
    bg.alpha_composite(down(face))
    # Bisa 0.04, sampai 0.46, satu 0.73, menit 1.12
    t0, t1 = 0.08, 1.12
    frames = []
    for t in times:
        im = bg.copy()
        u = ramp(t, t0, t1)
        sec = 60 * u
        top = layer()
        d = ImageDraw.Draw(top)
        if sec > 0.2:  # the elapsed time as a thick arc inside the ticks
            d.arc(sc([(cx - R + 44, cy - R + 44), (cx + R - 44, cy + R - 44)]), -90, -90 + 6 * sec, fill=YELLOW + (150,), width=22 * S)
        a = 2 * math.pi * sec / 60 - math.pi / 2
        d.line(sc([(cx - 30 * math.cos(a), cy - 30 * math.sin(a)), (cx + (R - 40) * math.cos(a), cy + (R - 40) * math.sin(a))]),
               fill=YELLOW + (255,), width=8 * S)
        d.ellipse(sc([(cx - 16, cy - 16), (cx + 16, cy + 16)]), fill=YELLOW + (255,))
        txt = "1:00" if u >= 1 else f"0:{int(sec):02d}"
        put(top, text_sprite([(txt, 64, YELLOW if u >= 1 else WHITE, True)]), cx, cy + 80, scale=pop(t, t1) if u >= 1 else 1.0)
        if t > t1:
            ph = ramp(t, t1, t1 + 0.5)
            r = R + 20 + 80 * ph
            d.ellipse(sc([(cx - r, cy - r), (cx + r, cy + r)]), outline=YELLOW + (round(220 * (1 - ph)),), width=8 * S)
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


# ---------- skema_kerok: scraping it out with a fingernail ----------
def finger_sprite():
    """a fingertip from the side, pointing right and leaning down 10 degrees, the nail on top; (0, 0) in the sprite's middle
    is the lowest point of the fingertip, where it rides on the skin"""
    R = 520
    im = Image.new("RGBA", (2 * R * S, 2 * R * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ang = math.radians(10)

    def tr(pts):  # fingertip frame (x along the finger, y down) -> sprite pixels
        return [((R + x) * S, (R + y) * S) for x, y in rot(pts, ang, -40, -70)]
    body = [(-520, -62), (-60, -62)] + [(-60 + 62 * math.cos(a), 62 * math.sin(a)) for a in np.linspace(-math.pi / 2, math.pi / 2, 16)] + [(-520, 62)]
    d.polygon(tr(body), fill=(234, 180, 150, 255), outline=(176, 120, 96, 255), width=4 * S)
    nail = [(-170, -62), (-56, -62), (-12, -50), (8, -30), (-10, -36), (-60, -46), (-170, -48)]
    d.polygon(tr(nail), fill=(250, 228, 222, 255), outline=(200, 150, 140, 255), width=3 * S)
    d.line(tr([(-230, -20), (-180, -16)]), fill=(200, 140, 116, 255), width=3 * S)
    return im


def kerok(times):
    bg = backdrop()
    fing = finger_sprite()
    check = Image.new("RGBA", (120 * S, 120 * S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(check)
    cd.ellipse([4 * S, 4 * S, 116 * S, 116 * S], fill=GREEN + (255,), outline=(255, 255, 255, 255), width=5 * S)
    cd.line([(32 * S, 62 * S), (52 * S, 82 * S), (88 * S, 42 * S)], fill=(255, 255, 255, 255), width=11 * S, joint="curve")
    # Jadi 0.04, kerok 0.73, pakai 1.04, kuku 1.28, secepatnya 1.77
    t_move, t_hit, t_out, t_ok = 0.55, 1.08, 1.32, 1.77
    frames = []
    for t in times:
        im = bg.copy()
        venom_cloud(im, 80, 0.7 * (1 - 0.6 * ramp(t, t_out, 2.6)), red=0.6 * (1 - 0.5 * ramp(t, t_out, 2.6)))
        top = layer()
        d = ImageDraw.Draw(top)
        # the fingertip rides along the skin from the left and pushes the sting over with its nail
        nx = 150 + (SX + 300 - 150) * ramp(t, t_move, t_move + 1.15)
        ny = SURF - 2 - 120 * ramp(t, 1.55, 1.95)
        tilt = math.radians(62) * ramp(t, t_hit, t_out)
        if t < t_out:
            sting(d, SX, SURF, ang=tilt, pulse=0.05 * math.sin(2 * math.pi * 2.6 * t), cut=True)
        else:  # flicked out: up and away, turning
            f = ramp(t, t_out, t_out + 0.6)
            sl = layer()
            sting(ImageDraw.Draw(sl), SX + 280 * f, SURF - 20 - 260 * f + 170 * f * f, ang=tilt + 2.2 * f, cut=True)
            top.alpha_composite(fade(sl, 1 - ramp(t, t_out + 0.35, t_out + 0.6)))
        fa = ramp(t, 0.2, 0.45) * (1 - ramp(t, 1.6, 1.9))
        if t_move <= t < t_out + 0.3:
            for k in range(3):  # speed lines behind the fingertip
                y = SURF - 34 - 26 * k
                d.line(sc([(nx - 330 - 30 * k, y), (nx - 230 - 30 * k, y)]), fill=(255, 255, 255, round(110 * fa)), width=3 * S)
        if fa > 0:
            put(top, fing, nx, ny, a=fa)
        put(top, check, SX, SURF - 110, a=ramp(t, t_ok, t_ok + 0.12), scale=pop(t, t_ok))
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


N = {"sengat": 86, "gerigi": 104, "kabur": 132, "pompa": 128, "menit": 62, "kerok": 90}
if __name__ == "__main__":
    args = sys.argv[1:]
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
            encode(globals()[name]([i / FPS for i in range(N[name])]), f"clips/skema_{name}.mp4")
