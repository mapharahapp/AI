"""Schematic animations for Titik Heran #19 (run in the episode work dir; writes clips/skema_biru.mp4, skema_asap.mp4 and skema_pm25.mp4).
usage: python3 skema19.py [biru|asap|pm25 ...] [--sheet out.jpg t1,t2,...]   (--sheet saves those frames as a contact sheet)
skema_biru: sunlight carries every colour; the air molecules scatter the blue part all over the sky, so the sky looks blue.
skema_asap: a thick smoke layer from the forest fires scatters and absorbs the blue (BMKG: smoke particles scatter and absorb light),
so only yellow, orange and red get through and the sky turns orange. Simplified: real smoke dims every colour, blue the most.
skema_pm25: a human hair (±70 µm, US EPA) next to a PM2.5 particle (≤2,5 µm): about 30 of them fit across the hair; then the
particles go down the windpipe deep into the lungs. The card shows the BMKG reading for Palangka Raya on 23 Oct 2026, 10.00 WIB
(1.512,7 µg/m³, via Prokalteng) and the WHO 2021 guideline (15 µg/m³ as a 24-hour mean).
Event times are seconds from the start of each shot, read off `render.py 19 plan`.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, chaikin, encode, glow_sprite
from skema13 import navy
from skema17 import label, sun

PALE, ORANGE, RED = (200, 214, 235), (255, 150, 40), (255, 80, 64)
# the sunbeam's colours, blue side first
BEAM = [(80, 120, 255), (60, 200, 255), (90, 220, 120), YELLOW, ORANGE, RED]
SUN, HIT, GROUND = (190, 700), (640, 1235), 1235
PERSON = (862, GROUND)


# ---------- the sky diagram shared by skema_biru and skema_asap ----------
def skies():
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    v = np.clip((yy - 250) / (GROUND - 250), 0, 1)[..., None]
    space = np.array([10, 20, 46]) * (1 - v) + np.array([22, 40, 80]) * v
    haze = np.array([70, 66, 70]) * (1 - v) + np.array([150, 136, 120]) * v
    blue = np.array([34, 96, 196]) * (1 - v) + np.array([150, 200, 245]) * v
    orange = np.array([120, 52, 22]) * (1 - v) + np.array([250, 156, 60]) * v
    return space, haze, blue, orange


def sky(base, blue, orange, b, o):
    """the sky as a mix of a base colour, blue and orange (b + o <= 1)"""
    rgb = base * (1 - b - o) + blue * b + orange * o
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert("RGBA")


def ground():
    """a dark skyline of forest and roofs along the bottom, with a small person looking up at the sky"""
    lay = layer()
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(19)
    pts = [(-10, GROUND)]
    for x in range(0, W + 40, 30):  # tree tops
        pts.append((x, GROUND - 18 - 22 * abs(math.sin(x * 0.037)) - rng.uniform(0, 12)))
    pts += [(W + 10, GROUND), (W + 10, H + 10), (-10, H + 10)]
    d.polygon(sc(chaikin(pts[:-3], 2)[: -2] + pts[-3:]), fill=(16, 24, 22, 255))
    d.rectangle(sc([(-10, GROUND), (W + 10, H + 10)]), fill=(16, 24, 22, 255))
    for x0, w, h in ((80, 90, 46), (300, 110, 58), (980, 80, 40)):  # roofs
        d.polygon(sc([(x0, GROUND - h * 0.55), (x0 + w / 2, GROUND - h), (x0 + w, GROUND - h * 0.55), (x0 + w, GROUND + 4), (x0, GROUND + 4)]),
                  fill=(12, 18, 18, 255))
    px, py = PERSON  # the person, face turned up and to the left
    d.ellipse(sc([(px - 13, py - 112), (px + 13, py - 86)]), fill=(232, 236, 240, 255))
    d.rounded_rectangle(sc([(px - 18, py - 84), (px + 18, py - 30)]), radius=10 * S, fill=(232, 236, 240, 255))
    d.line(sc([(px - 9, py - 32), (px - 11, py)]), fill=(232, 236, 240, 255), width=11 * S)
    d.line(sc([(px + 9, py - 32), (px + 11, py)]), fill=(232, 236, 240, 255), width=11 * S)
    d.line(sc([(px - 16, py - 74), (px - 40, py - 104)]), fill=(232, 236, 240, 255), width=9 * S)  # pointing at the sky
    return down(lay)


def beam_lines(cut=None, fade_below=0.0, pulse=None):
    """the six parallel colour lines from the sun to the ground: [(points, colour, alpha, width)]
    cut: {colour index: y where the line stops in the smoke}; fade_below dims those lines below the cut; pulse: {index: boost}"""
    (x0, y0), (x1, y1) = SUN, HIT
    L = math.dist(SUN, HIT)
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    out = []
    for k, col in enumerate(BEAM):
        off = (k - 2.5) * 8
        a, b = (x0 + nx * off, y0 + ny * off), (x1 + nx * off, y1 + ny * off)
        boost = (pulse or {}).get(k, 0)
        if cut and k in cut:
            yc = cut[k]
            f = (yc - a[1]) / (b[1] - a[1])
            mid = (a[0] + (b[0] - a[0]) * f, yc)
            out.append(([a, mid], col, 1.0, 5 + 4 * boost))
            if fade_below < 1:
                out.append(([mid, b], col, 1 - fade_below, 5))
        else:
            out.append(([a, b], col, 1.0, 5 + 4 * boost))
    return out


def draw_beam(d, dg, lines, upto=1.0):
    for (a, b), col, al, w in lines:
        if al <= 0.01:
            continue
        e = (a[0] + (b[0] - a[0]) * min(1, upto / max(1e-6, (b[1] - SUN[1]) / (HIT[1] - SUN[1]))), a[1] + (b[1] - a[1]) * min(1, upto / max(1e-6, (b[1] - SUN[1]) / (HIT[1] - SUN[1]))))
        if a[1] - SUN[1] > upto * (HIT[1] - SUN[1]):
            continue
        d.line(sc([a, e]), fill=col + (round(255 * al),), width=round(w) * S)
        dg.line(sc([a, e]), fill=col + (round(120 * al),), width=round(w * 3) * S)


def molecules():
    rng = np.random.default_rng(7)
    pts = []
    while len(pts) < 24:
        x, y = rng.uniform(110, 990), rng.uniform(790, 1170)
        if abs(x - (SUN[0] + (y - SUN[1]) / 1.19)) < 70 or math.dist((x, y), (PERSON[0], PERSON[1] - 140)) < 110:
            continue  # keep clear of the beam and the person's label
        if all(math.dist((x, y), p) > 80 for p in pts):
            pts.append((x, y))
    return pts


def scatter(d, mols, t, t0, a):
    """each molecule throws short blue strokes out in all directions, again and again"""
    if a <= 0:
        return
    for k, (x, y) in enumerate(mols):
        ph = ((t - t0) * 1.3 + k * 0.37) % 1.0
        if t < t0:
            continue
        for j in range(6):
            ang = 2 * math.pi * j / 6 + k
            r0, r1 = 12 + 40 * ph, 30 + 46 * ph
            d.line(sc([(x + math.cos(ang) * r0, y + math.sin(ang) * r0), (x + math.cos(ang) * r1, y + math.sin(ang) * r1)]),
                   fill=(110, 170, 255, round(230 * a * (1 - ph))), width=4 * S)


def mol_dots(d, mols, t, t0):
    for k, (x, y) in enumerate(mols):
        p = pop(t, t0 + 0.012 * k, 0.25)
        if p > 0:
            r = 8 * p
            d.ellipse(sc([(x - r, y - r), (x + r, y + r)]), fill=(236, 242, 255, 255), outline=(120, 150, 200, 255), width=2 * S)


def sun_sprites():
    return sun(46), glow_sprite(90, (255, 226, 120))


def biru(times):
    space, _, blue, orange = skies()
    gr, mols = ground(), molecules()
    sunsp, sunglow = sun_sprites()
    lab_sun = text_sprite([("sinar matahari = campuran semua warna", 30, WHITE, False)])
    lab_mol = text_sprite([("molekul udara", 30, WHITE, True)])
    seen = label([("langit tampak", 28, WHITE, False), ("BIRU", 44, (120, 180, 255), True)])
    # Normalnya 0.04, udara 0.94, menyebarkan 1.32, cahaya 1.85, biru 2.22, ke 2.56, seluruh 2.67, langit 2.97
    t_mol, t_sc, t_biru, t_seen = 0.94, 1.32, 2.22, 2.97
    frames = []
    for t in times:
        im = sky(space, blue, orange, 0.95 * ramp(t, t_sc + 0.1, t_seen), 0.0)
        glow = layer()
        dg = ImageDraw.Draw(glow)
        top = layer()
        d = ImageDraw.Draw(top)
        put(top, sunglow, *SUN, a=0.8)
        put(top, sunsp, *SUN)
        pul = {0: math.exp(-((t - t_biru - 0.12) / 0.22) ** 2)}
        draw_beam(d, dg, beam_lines(pulse=pul), upto=ramp(t, 0.05, 0.6))
        put(top, lab_sun, 590, 690, a=ramp(t, 0.35, 0.6))
        scatter(d, mols, t, t_sc, ramp(t, t_sc, t_sc + 0.3))
        mol_dots(d, mols, t, t_mol)
        x, y = mols[0]
        put(top, lab_mol, x, y - 46, a=ramp(t, t_mol + 0.15, t_mol + 0.35) * (1 - ramp(t, t_sc + 0.9, t_sc + 1.2)))
        put(top, seen, PERSON[0], PERSON[1] - 200, scale=pop(t, t_seen))
        im.alpha_composite(down(glow).filter(ImageFilter.GaussianBlur(6)))
        im.alpha_composite(gr)
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


def smoke_sprite():
    """a wide band of soft grey-brown puffs, as a 1x RGBA image"""
    w, h = 1700, 300
    rng = np.random.default_rng(23)
    sm = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(sm)
    for _ in range(200):
        x, y, r = rng.uniform(60, w - 160), rng.uniform(115, 185), rng.uniform(40, 90)
        g = int(rng.uniform(92, 140))
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(g, int(g * 0.9), int(g * 0.78), 130))
    sm = sm.filter(ImageFilter.GaussianBlur(14))
    a = np.array(sm.getchannel("A"), np.float32) * np.clip((w - np.arange(w)) / 220, 0, 1)[None, :]  # a soft leading edge
    sm.putalpha(Image.fromarray(a.astype(np.uint8)))
    return sm


def asap(times):
    _, haze, blue, orange = skies()
    gr, mols = ground(), molecules()
    sunsp, sunglow = sun_sprites()
    sm = smoke_sprite()
    lab_smoke = text_sprite([("ASAP", 40, WHITE, True)])
    lab_stop = label([("biru tertahan", 32, (140, 190, 255), True)])
    seen_b = label([("langit tampak", 28, WHITE, False), ("BIRU", 44, (120, 180, 255), True)])
    seen_o = label([("langit tampak", 28, WHITE, False), ("ORANYE", 44, ORANGE, True)], edge=ORANGE + (230,))
    # menghalangi 0.03, cahaya 0.74, biru 1.04, itu 1.35, Yang 1.87, lolos 2.10, tinggal 2.55, kuning 2.92, oranye 3.60, sampai 4.42, merah 4.80
    t_in0, t_in1, t_cut0, t_cut1, t_warm = 0.0, 0.9, 0.6, 1.5, 1.87
    t_col = {3: 2.92, 4: 3.60, 5: 4.80}
    sm_y = 968  # the middle of the smoke band
    cuts = {0: 905, 1: 935, 2: 968}  # where blue, cyan and green die out in the smoke
    frames = []
    for t in times:
        b = 0.95 * (1 - ramp(t, 0.5, 2.0))  # the blue goes, the sky turns hazy, then orange
        o = 0.92 * ramp(t, 1.4, 3.8)
        im = sky(haze, blue, orange, min(b, 1 - o), o)
        glow = layer()
        dg = ImageDraw.Draw(glow)
        top = layer()
        d = ImageDraw.Draw(top)
        put(top, sunglow, *SUN, a=0.8)
        put(top, sunsp, *SUN)
        c = ramp(t, t_cut0, t_cut1)
        pul = {k: math.exp(-((t - tc - 0.15) / 0.25) ** 2) + 0.3 * ramp(t, t_warm, t_warm + 0.4) for k, tc in t_col.items()}
        draw_beam(d, dg, beam_lines(cut=cuts, fade_below=c, pulse=pul))
        scatter(d, mols, t, -1.0, 1 - ramp(t, 0.5, 1.4))
        mol_dots(d, mols, t, -1.0)
        im.alpha_composite(down(glow).filter(ImageFilter.GaussianBlur(6)))
        im.alpha_composite(down(top))
        # the smoke slides in over the beam, then drifts
        sx = -1700 + (1700 - 300) * ramp(t, t_in0, t_in1) + 14 * t
        if sx > -1700:
            im.alpha_composite(fade(sm, 0.95), (round(sx), sm_y - 150))
        top2 = layer()
        d2 = ImageDraw.Draw(top2)
        if c > 0:  # sparks where the blue lines die
            for k, yc in cuts.items():
                xc = SUN[0] + (yc - SUN[1]) / 1.19 + (k - 2.5) * 8 * 0.77
                for j in range(5):
                    ph = ((t - t_cut0) * 2.2 + j * 0.2 + k * 0.13) % 1.0
                    ang = 2 * math.pi * j / 5 + k
                    r = 6 + 26 * ph
                    d2.ellipse(sc([(xc + math.cos(ang) * r - 3, yc + math.sin(ang) * r - 3), (xc + math.cos(ang) * r + 3, yc + math.sin(ang) * r + 3)]),
                               fill=BEAM[k] + (round(230 * (1 - ph) * min(1, c * 2)),))
        put(top2, lab_smoke, 150, sm_y - 4, a=ramp(t, 0.5, 0.8))
        put(top2, lab_stop, 610, sm_y + 2, a=ramp(t, 1.0, 1.2), scale=pop(t, 1.0))
        sw = ramp(t, 3.8, 4.1)
        put(top2, seen_b, PERSON[0], PERSON[1] - 200, a=1 - sw)
        put(top2, seen_o, PERSON[0], PERSON[1] - 200, a=sw, scale=1 + 0.1 * math.exp(-((t - 4.0) / 0.15) ** 2))
        im.alpha_composite(gr)
        im.alpha_composite(down(top2))
        frames.append(im)
    return frames


# ---------- skema_pm25 ----------
def hair_sprite(r=230):
    s = Image.new("RGBA", (round(2.4 * r * S), round(2.4 * r * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    c = 1.2 * r * S
    for k in range(10, 0, -1):  # cuticle layers, darker inward
        rr = r * (0.55 + 0.045 * k) * S
        g = 0.6 + 0.04 * k
        d.ellipse([c - rr, c - rr, c + rr, c + rr], fill=(round(120 * g), round(78 * g), round(44 * g), 255))
    for k in range(36):  # scales on the outer edge
        a = 2 * math.pi * k / 36
        d.arc([c - r * S, c - r * S, c + r * S, c + r * S], math.degrees(a), math.degrees(a) + 7, fill=(200, 150, 100, 255), width=4 * S)
    d.ellipse([c - r * S, c - r * S, c + r * S, c + r * S], outline=(214, 170, 120, 255), width=5 * S)
    return s


def lungs_layer():
    lay = layer()
    d = ImageDraw.Draw(lay)
    left = chaikin([(510, 900), (470, 870), (400, 880), (330, 950), (290, 1060), (280, 1170), (300, 1240), (380, 1250),
                    (470, 1215), (515, 1150), (520, 1000)], 3)
    right = [(1080 - x, y) for x, y in left]
    for lobe in (left, right):
        d.polygon(sc(lobe), fill=(226, 118, 128, 255), outline=(255, 190, 196, 255), width=4 * S)
    d.rounded_rectangle(sc([(520, 760), (560, 905)]), radius=16 * S, fill=(236, 170, 176, 255), outline=(255, 210, 214, 255), width=3 * S)
    for k in range(5):  # rings of the windpipe
        y = 780 + 25 * k
        d.line(sc([(522, y), (558, y)]), fill=(200, 120, 128, 255), width=3 * S)
    tree = []
    for sx in (-1, 1):
        a = (540, 900)
        b = (540 + sx * 110, 965)
        tree.append([a, b])
        for k, (dx, dy) in enumerate(((60, 70), (20, 150), (90, 180), (130, 100))):
            c = (b[0] + sx * dx, b[1] + dy)
            tree.append([b, c])
            for e in (-1, 1):
                tree.append([c, (c[0] + sx * 30 + e * 26, c[1] + 50)])
    for seg in tree:
        d.line(sc(seg), fill=(160, 60, 76, 255), width=6 * S, joint="curve")
    return down(lay), tree


def pm25(times):
    bg = navy(540, 1000)
    hair = hair_sprite()
    lungs, tree = lungs_layer()
    card = label([("PM2.5 PALANGKA RAYA", 30, WHITE, True), ("1.512,7 µg/m³", 48, (255, 120, 90), True),
                  ("23 Okt 2026, 10.00 WIB (BMKG) · pedoman WHO: 15 µg/m³ per 24 jam", 24, PALE, False)])
    lab_h = text_sprite([("RAMBUT", 46, WHITE, True), ("±70 µm", 36, WHITE, False)], gap=2)
    lab_p = text_sprite([("PM2.5", 36, YELLOW, True)])
    lab_p2 = text_sprite([("≤2,5 µm", 30, WHITE, False)])
    HC, R = (540, 1010), 230
    dia = 2 * R * 2.5 / 70  # a PM2.5 particle at the same scale as the hair
    n_row = round(2 * R / dia)
    rng = np.random.default_rng(25)
    # particles down the windpipe into the bronchi: (delay, side, branch, end jitter)
    parts = [(rng.uniform(0, 1.0), int(rng.integers(0, 2)), int(rng.integers(0, 4)), rng.uniform(-20, 20, 2)) for _ in range(46)]
    # Masalahnya 0.05, partikel 0.98, asapnya 1.32, tiga 1.85, puluh 2.22, kali 2.52, lebih 2.75, kecil 2.97, dari 3.35, rambut 3.57,
    # bisa 4.25, masuk 4.48, ke 4.81, paru-paru 4.93
    t_card, t_p, t_row0, t_row1, t_x0, t_x1 = 0.2, 0.98, 1.85, 2.55, 4.05, 4.4
    frames = []
    for t in times:
        im = bg.copy()
        top = layer()
        d = ImageDraw.Draw(top)
        hv = 1 - ramp(t, t_x0, t_x1)
        if hv > 0:
            hs = layer()
            dh = ImageDraw.Draw(hs)
            put(hs, hair, *HC, scale=pop(t, 0.0, 0.35) * (1 + 0.03 * math.exp(-((t - 3.0) / 0.3) ** 2)))
            put(hs, lab_h, HC[0], HC[1] - 110, a=ramp(t, 0.25, 0.45))
            for k in range(n_row):  # about 30 particles across one hair
                tk = t_row0 + (t_row1 - t_row0) * k / n_row
                p = pop(t, tk, 0.2)
                if p > 0:
                    x = HC[0] - R + dia * (k + 0.5)
                    r = dia / 2 * p
                    dh.ellipse(sc([(x - r, HC[1] - r), (x + r, HC[1] + r)]), fill=(240, 240, 240, 255), outline=(40, 40, 40, 255), width=1 * S)
            pp = pop(t, t_p)
            if pp > 0:
                x, r = 872, dia / 2 * pp
                dh.ellipse(sc([(x - r, HC[1] - r), (x + r, HC[1] + r)]), fill=(240, 240, 240, 255), outline=(40, 40, 40, 255), width=1 * S)
                put(hs, lab_p, x, HC[1] - 52, a=ramp(t, t_p, t_p + 0.15))
                put(hs, lab_p2, x, HC[1] + 50, a=ramp(t, t_p + 0.1, t_p + 0.25))
            im.alpha_composite(fade(down(hs), hv))
        lv = ramp(t, t_x0 + 0.1, t_x1 + 0.1)
        if lv > 0:
            im.alpha_composite(fade(lungs, lv))
            for dl, side, br, jit in parts:  # windpipe -> main bronchus -> one branch
                u = ramp(t, t_x1 + dl, t_x1 + dl + 0.75)
                if u <= 0:
                    continue
                path = [(540, 700), (540, 900)] + tree[side * 13 + 0][1:] + [tree[side * 13 + 1 + 3 * br][1]]
                path = path[:-1] + [(path[-1][0] + jit[0], path[-1][1] + jit[1])]
                seg = [math.dist(a, b) for a, b in zip(path, path[1:])]
                g = u * sum(seg)
                for (a, b), L in zip(zip(path, path[1:]), seg):
                    if g <= L:
                        x, y = a[0] + (b[0] - a[0]) * g / L, a[1] + (b[1] - a[1]) * g / L
                        break
                    g -= L
                else:
                    x, y = path[-1]
                d.ellipse(sc([(x - 6, y - 6), (x + 6, y + 6)]), fill=(60, 60, 60, round(255 * lv)), outline=(255, 255, 255, round(220 * lv)), width=2 * S)
        put(top, card, 540, 652, a=ramp(t, t_card, t_card + 0.2), scale=pop(t, t_card))
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


N = {"biru": 117, "asap": 171, "pm25": 180}
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
