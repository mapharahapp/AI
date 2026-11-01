"""Schematic animations for Titik Heran #26 (run in the episode work dir after `dl.py i:2659622 i:3624193`;
writes clips/skema_panas.mp4, skema_sentuh.mp4, skema_uji.mp4 and skema_tolak.mp4).
usage: python3 skema26.py [panas|sentuh|uji|tolak ...] [--sheet out.jpg t1,t2,...]
skema_panas: the Acropora close-up (Pixabay 2659622) as the sea heats up: a thermometer rises, the green algae (zooxanthellae)
leave the coral and it pales toward white.
skema_sentuh ("rekonstruksi"): the accident in the Stanford tank (Collins, Palumbi et al., Science Advances, 14 Oct 2026): a healthy
fragment tips over onto its bleached clone, a ring marks the contact point and the colour spreads back from there while algae cross over.
The fragments are drawn (Pocillopora-like), over the blurred reef tank of Pixabay 3624193.
skema_uji: the test of 10 clone pairs: the 5 touching pairs regain their colour over 7 weeks, the 5 kept a few millimetres apart stay white.
skema_tolak: a clone pair heals; a bleached fragment touching a coral of another genotype is rejected (a red spark, they pull apart).
Event times are seconds from the start of each shot, read off `render.py 26 plan`.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, encode, glow_sprite
from skema13 import navy
from skema17 import ring, label
from skema18 import check

N = {"panas": 106, "sentuh": 186, "uji": 124, "tolak": 98}
RED, GREEN, ALGA = (226, 40, 36), (60, 200, 100), (120, 236, 90)
# base, tip and polyp colours of a fragment
HEALTHY = ((122, 70, 30), (232, 174, 98), (92, 50, 20))
BLEACHED = ((204, 211, 218), (248, 250, 252), (176, 184, 194))
FOREIGN = ((84, 44, 100), (206, 120, 196), (64, 28, 74))  # a coral of another genotype, in another colour
DEAD = ((96, 100, 104), (156, 160, 164), (82, 86, 90))


def cover(path, pos=0.5):
    """the photo filling the 1080x1920 frame (render.py's cover crop) at 1x"""
    im = Image.open(path).convert("RGB")
    k = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x0 = round((im.width - W) * pos)
    return im.crop((x0, (im.height - H) // 2, x0 + W, (im.height - H) // 2 + H))


# ---------- the coral fragments ----------
def silhouette(seed, w, h, depth=4):
    """a bushy, knobbly branching fragment (Pocillopora-like) as an L mask at 2x, about w x h px at 1x, standing on the middle of
    its bottom edge; the canvas is cropped symmetrically round the trunk, so it is as wide as the branches spread"""
    rng = np.random.default_rng(seed)
    cw = 2 * w
    m = Image.new("L", (cw * S, h * S), 0)
    d = ImageDraw.Draw(m)

    def dot(x, y, r):
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=255)

    def branch(x, y, ang, L, t, k):
        x1, y1 = x + L * math.sin(ang), y - L * math.cos(ang)
        d.line([(x * S, y * S), (x1 * S, y1 * S)], fill=255, width=max(1, round(t * S)))
        dot(x1, y1, t / 2)
        for _ in range(int(L / 7)):  # the knobs (verrucae) along the branch
            u, side = rng.uniform(0.1, 1.0), rng.choice([-1, 1])
            dot(x + (x1 - x) * u + side * t * 0.42 * math.cos(ang), y + (y1 - y) * u + side * t * 0.42 * math.sin(ang),
                t * rng.uniform(0.16, 0.26))
        if k == 0:
            dot(x1, y1, t * 0.6)
            return
        n = 3 if rng.random() < 0.45 else 2
        spread = rng.uniform(0.3, 0.44)
        for i in range(n):
            a = ang + spread * (i - (n - 1) / 2) * (1.8 if n == 2 else 1.0) + rng.normal(0, 0.07)
            branch(x1, y1, max(-1.0, min(1.0, a)), L * rng.uniform(0.7, 0.86), t * rng.uniform(0.76, 0.84), k - 1)
    branch(cw / 2, h - 2, rng.normal(0, 0.04), h * 0.26, w * 0.12, depth)
    x0, _, x1, _ = m.getbbox()
    e = max(cw * S / 2 - x0, x1 - cw * S / 2) + 4 * S
    m = m.crop((round(cw * S / 2 - e), 0, round(cw * S / 2 + e), h * S))
    return m.filter(ImageFilter.GaussianBlur(0.8 * S))


def paint(m, pal, seed):
    """a fragment in one palette: darker at the base, light at the tips, dotted with polyps, shaded round its edges (RGBA at 2x)"""
    w2, h2 = m.size
    base, tip, pol = (np.array(c, np.float32) for c in pal)
    v = np.linspace(1, 0, h2, dtype=np.float32)[:, None, None] ** 0.8
    rgb = base * (1 - v) + tip * v + np.zeros((h2, w2, 3), np.float32)
    rng = np.random.default_rng(seed + 100)  # the same polyps on every palette of one fragment
    pm = Image.new("L", m.size, 0)
    pd = ImageDraw.Draw(pm)
    for _ in range(int(w2 * h2 / (90 * S * S))):
        x, y, r = rng.uniform(0, w2), rng.uniform(0, h2), rng.uniform(1.8, 2.8) * S
        pd.ellipse([x - r, y - r, x + r, y + r], fill=255)
    p = (np.asarray(pm.filter(ImageFilter.GaussianBlur(0.6 * S)), np.float32) / 255)[..., None]
    rgb = rgb * (1 - 0.7 * p) + pol * 0.7 * p
    blur = m.filter(ImageFilter.GaussianBlur(5 * S))
    edge = np.asarray(blur, np.float32) / 255
    lit = np.clip(edge - np.asarray(blur.transform(blur.size, Image.AFFINE, (1, 0, 3 * S, 0, 1, 3 * S)), np.float32) / 255, 0, 1)
    rgb = rgb * (0.58 + 0.42 * np.clip(edge * 1.4, 0, 1))[..., None] + 120 * lit[..., None]  # light from the top left
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert("RGBA")
    im.putalpha(m)
    return im


def fragment(seed, w, h, pals=(HEALTHY, BLEACHED), depth=4):
    m = silhouette(seed, w, h, depth)
    return [paint(m, pal, seed) for pal in pals]


def mix(a, b, c):
    """palette b blended into a: c 0 = a .. 1 = b, a number or an L mask the size of the sprites"""
    if isinstance(c, Image.Image):
        return Image.composite(b, a, c)
    return a if c <= 0 else b if c >= 1 else Image.blend(a, b, c)


def plug(d, x, y, w=120):
    """the ceramic plug a lab fragment is glued on, its top at y"""
    d.rounded_rectangle([(x - w / 2) * S, y * S, (x + w / 2) * S, (y + 26) * S], radius=8 * S, fill=(150, 154, 160, 255),
                        outline=(96, 100, 108, 255), width=2 * S)
    d.ellipse([(x - w / 2) * S, (y - 9) * S, (x + w / 2) * S, (y + 9) * S], fill=(186, 190, 196, 255), outline=(110, 114, 120, 255), width=2 * S)


def plug_sprite(w=96):
    """a plug on a sprite of its own, for a fragment that moves with its plug: place it at the plug top + 31"""
    sp = Image.new("RGBA", ((w + 8) * S, 44 * S))
    plug(ImageDraw.Draw(sp), w / 2 + 4, 13, w)
    return sp


def place(lay, sprite, x, ybase, a=1.0):
    """composite a 2x fragment sprite with the middle of its bottom edge at (x, ybase) in 1x coordinates"""
    if a <= 0.01:
        return
    lay.alpha_composite(sprite if a >= 1 else fade(sprite, a), (round(x * S - sprite.width / 2), round(ybase * S - sprite.height)))


def camera(im, k, c, c1):
    """zoom by k about the point c (1x) and slide that point to c1 on screen"""
    if k <= 1.0001 and c == c1:
        return im
    return im.transform((W, H), Image.AFFINE, (1 / k, 0, c[0] - c1[0] / k, 0, 1 / k, c[1] - c1[1] / k), resample=Image.BICUBIC)


# ---------- skema_panas ----------
def thermometer(lay, x, y0, y1, u):
    """a thermometer from y0 (top) to y1 (bulb centre) at x, filled red to the fraction u"""
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([(x - 24) * S, (y0 - 24) * S, (x + 24) * S, y1 * S], radius=24 * S, fill=(235, 240, 245, 230), outline=(60, 70, 90, 255), width=3 * S)
    d.ellipse([(x - 44) * S, (y1 - 44) * S, (x + 44) * S, (y1 + 44) * S], fill=(235, 240, 245, 230), outline=(60, 70, 90, 255), width=3 * S)
    top = y1 - (y1 - y0) * u
    d.rounded_rectangle([(x - 12) * S, top * S, (x + 12) * S, y1 * S], radius=12 * S, fill=RED + (255,))
    d.ellipse([(x - 32) * S, (y1 - 32) * S, (x + 32) * S, (y1 + 32) * S], fill=RED + (255,))
    for k in range(1, 7):  # ticks
        ty = y1 - 70 - (y1 - 70 - y0) * k / 7
        d.line([((x + 26) * S, ty * S), ((x + 44) * S, ty * S)], fill=(255, 255, 255, 200), width=3 * S)


def panas(times):
    photo = cover("img/2659622.jpg", 0.23)
    a = np.asarray(photo, np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32) / 255
    soft = np.asarray(photo.convert("L").filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    coral_m = np.clip((soft - 0.1) / 0.14, 0, 1)[..., None]  # the coral, without the dark water behind it
    white = np.stack([180 + 72 * lum, 186 + 68 * lum, 194 + 61 * lum], -1)
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    heat = np.zeros((H, W, 3), np.float32) + np.array([255, 118, 36], np.float32)
    heat_a = (0.08 + 0.14 * (yy / H))[..., None]
    rng = np.random.default_rng(26)
    pts = []  # algae on the coral, in the band between the title and the captions
    while len(pts) < 150:
        x, y = rng.uniform(220, 1040), rng.uniform(660, 1180)
        if coral_m[int(y), int(x), 0] > 0.8:
            pts.append((x, y, rng.uniform(0, 2 * math.pi), rng.uniform(0.7, 1.3)))
    dot = glow_sprite(9, ALGA)
    core = Image.new("RGBA", (12 * S, 12 * S), (0, 0, 0, 0))
    ImageDraw.Draw(core).ellipse([2 * S, 2 * S, 10 * S, 10 * S], fill=(190, 255, 150, 255), outline=(40, 120, 30, 255), width=S)
    dot.alpha_composite(core, ((dot.width - core.width) // 2, (dot.height - core.height) // 2))
    tag = label([("alga (zooxanthellae)", 40, ALGA, True)], edge=ALGA + (220,))
    lab_c = text_sprite([("SUHU NAIK", 34, WHITE, True)])
    # Kepanasan, 0.04, karang 1.00, mengusir 1.26, alga 1.73, sumber 2.02, makanannya... 2.38
    t_go, t_bleach = 1.22, 1.95
    out = []
    for t in times:
        b = 0.9 * ramp(t, t_bleach, 3.3)
        rgb = a * (1 - b * coral_m) + white * b * coral_m
        rgb = rgb * 0.86
        h = ramp(t, 0.0, 1.1)
        rgb = rgb * (1 - h * heat_a) + heat * h * heat_a
        im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert("RGBA")
        top = layer()
        thermometer(top, 120, 700, 1110, 0.25 + 0.65 * ramp(t, 0.05, 1.15))
        put(top, lab_c, 150, 646, a=ramp(t, 0.1, 0.25), scale=pop(t, 0.1))
        for x, y, ang, sp in pts:  # the algae drift off the coral, outward and up, and fade
            u = max(0.0, t - t_go) * sp
            dx, dy = x - 600, y - 930
            r = math.hypot(dx, dy) + 1
            px = x + (dx / r) * 160 * u + 40 * math.sin(ang + 3 * u) * min(u, 1)
            py = y + (dy / r) * 120 * u - 220 * u * u
            al = ramp(t, 0.15, 0.5) * (1 - ramp(u, 0.55, 1.25))
            put(top, dot, px, py, a=0.95 * al)
        put(top, tag, 760, 700, a=ramp(t, 1.7, 1.85) * (1 - ramp(t, 2.6, 2.8)), scale=pop(t, 1.7))
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_sentuh ----------
FA, FB, FW, FH = (330, 1120), (780, 1120), 300, 460  # bases of the healthy (A) and the bleached (B) fragment, fragment size


def tank():
    """the blurred reef tank behind the fragments, with the rack they stand on"""
    bg = cover("img/3624193.jpg", 0.5).filter(ImageFilter.GaussianBlur(16))
    a = np.asarray(bg, np.float32) * 0.42 + np.array([4, 12, 26], np.float32)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 1146 * S, W * S, 1176 * S], fill=(70, 78, 90, 255))
    for x in range(0, W, 36):  # the egg-crate rack
        d.line([(x * S, 1146 * S), (x * S, 1176 * S)], fill=(44, 50, 60, 255), width=3 * S)
    d.line([(0, 1146 * S), (W * S, 1146 * S)], fill=(120, 128, 140, 255), width=3 * S)
    plug(d, FA[0], FA[1])
    plug(d, FB[0], FB[1])
    im.alpha_composite(down(lay))
    return im


def falling(sprite, angle):
    """fragment A on a full 2x layer, tipped clockwise by `angle` degrees about the middle of its base"""
    lay = layer()
    place(lay, sprite, *FA)
    return lay if abs(angle) < 0.01 else lay.rotate(-angle, resample=Image.BICUBIC, center=(FA[0] * S, FA[1] * S))


def contact(a_sprite, b_lay):
    """the angle at which A first touches B, and the touching point (1x), worked out on 1x masks"""
    bm = np.asarray(b_lay.getchannel("A").resize((W, H)).filter(ImageFilter.MaxFilter(9)), np.float32) > 100
    a1 = a_sprite.getchannel("A").resize((a_sprite.width // S, a_sprite.height // S))
    am0 = Image.new("L", (W, H), 0)
    am0.paste(a1, (round(FA[0] - a1.width / 2), FA[1] - a1.height))
    for ang in np.arange(5, 70, 0.5):
        am = np.asarray(am0.rotate(-ang, resample=Image.BILINEAR, center=FA), np.float32) > 100
        hit = np.argwhere(am & bm)
        if len(hit) > 12:
            y, x = hit.mean(0)
            return ang, (x, y)
    raise SystemExit("A never reaches B")


def sentuh(times):
    bg = tank()
    a_h, = fragment(11, FW, FH, (HEALTHY,))
    b_w, b_h = fragment(11, FW, FH, (BLEACHED, HEALTHY))  # the same shape: a clone
    b_w, b_h = b_w.transpose(Image.FLIP_LEFT_RIGHT), b_h.transpose(Image.FLIP_LEFT_RIGHT)
    b_lay = layer()
    place(b_lay, b_w, *FB)
    th, cp = contact(a_h, b_lay)
    th += 1.5  # rest a little into B's branches
    bx0, by0 = round(FB[0] * S - b_w.width / 2), round(FB[1] * S - b_w.height)
    yy, xx = np.mgrid[0:b_w.height, 0:b_w.width].astype(np.float32)
    dist = np.hypot((xx + bx0) / S - cp[0], (yy + by0) / S - cp[1])
    lab_a = label([("SEHAT", 40, GREEN, True)], edge=GREEN + (220,))
    lab_b = label([("MEMUTIH", 40, (235, 240, 245), True)])
    rng = np.random.default_rng(7)
    algae = [(rng.uniform(4.15, 5.3), rng.uniform(0.6, 0.9), rng.normal(0, 26, 2), rng.normal(0, 60, 2)) for _ in range(22)]
    dot = glow_sprite(7, ALGA)
    # Di 0.03, lab 0.17, Stanford, 0.46, karang 0.98, sehat... 1.39, menimpa 2.01, kembarannya 2.41, yang 2.92, memutih. 3.03,
    # Di 3.66, titik 3.87, sentuhan... 4.13, warnanya 5.00, kembali! 5.43
    t_fall, t_hit, t_ring, t_col, t_back = 2.0, 2.38, 3.62, 4.55, 5.43
    cache = {}
    out = []
    for t in times:
        if t < t_fall:  # standing, a nervous wobble once it is named
            ang = 1.6 * math.sin(2 * math.pi * 2.2 * t) * ramp(t, 1.35, 1.6)
        elif t < t_hit:
            u = (t - t_fall) / (t_hit - t_fall)
            ang = th * u * u
        else:  # a small bounce on landing
            ang = th - 2.2 * math.exp(-(t - t_hit) / 0.09) * abs(math.sin((t - t_hit) * 22))
        key = round(ang, 2)
        if key not in cache:
            cache = {key: falling(a_h, ang)}
        im = bg.copy()
        R = 560 * ramp(t, t_col, 5.85) ** 0.8
        if R > 0:
            c = Image.fromarray((np.clip((R - dist) / 90, 0, 1) * 255).astype(np.uint8))
            b_now = mix(b_w, b_h, c)
        else:
            b_now = b_w
        top = layer()
        place(top, b_now, *FB)
        top.alpha_composite(cache[key])
        d = ImageDraw.Draw(top)
        if t >= t_ring:  # the contact point
            pulse = 1 + 0.08 * math.sin(2 * math.pi * 1.6 * (t - t_ring))
            ring(d, cp[0], cp[1], 62 * pop(t, t_ring) * pulse, YELLOW, 240 * (1 - ramp(t, 5.3, 5.7)), w=7)
        put(top, lab_a, FA[0], 700, a=ramp(t, 0.95, 1.08) * (1 - ramp(t, 1.9, 2.05)), scale=pop(t, 0.95))
        put(top, lab_b, FB[0], 700, a=ramp(t, 2.9, 3.03) * (1 - ramp(t, 3.55, 3.7)), scale=pop(t, 2.9))
        for t0, dur, j0, j1 in algae:  # algae crossing from A into B through the contact point
            u = (t - t0) / dur
            if 0 < u < 1:
                p0 = (cp[0] - 120 + j0[0], cp[1] + 40 + j0[1])
                p1 = (cp[0] + 140 + j1[0], cp[1] + 70 + j1[1])
                x = p0[0] + (p1[0] - p0[0]) * u
                y = p0[1] + (p1[1] - p0[1]) * u - 50 * math.sin(math.pi * u)
                put(top, dot, x, y, a=0.95 * min(1, u * 5, (1 - u) * 5))
        im.alpha_composite(down(top))
        k = 1 + 0.2 * ramp(t, 3.5, 5.3) + 0.06 * math.exp(-max(0.0, t - t_back) / 0.12) * (t >= t_back)
        c1 = (cp[0] + (540 - cp[0]) * ramp(t, 3.5, 5.3), cp[1] + (900 - cp[1]) * ramp(t, 3.5, 5.3))
        out.append(camera(im, k, cp, c1))
    return out


# ---------- skema_uji ----------
XS = [130, 325, 540, 755, 950]
Y_TOP, Y_BOT = 830, 1150  # bases of the touching row and of the separated row


def tray(d, x, y, w=170):
    """a dark tile carrying one pair, its top at y"""
    d.rounded_rectangle([(x - w / 2) * S, y * S, (x + w / 2) * S, (y + 20) * S], radius=8 * S, fill=(40, 52, 72, 255),
                        outline=(110, 124, 146, 255), width=2 * S)


def uji(times):
    bg = navy(540, 900)
    small = [fragment(30 + i, 64, 140, (HEALTHY, BLEACHED, DEAD), depth=3) for i in range(10)]
    racks = layer()
    d = ImageDraw.Draw(racks)
    for x in XS:
        for yb, dx in ((Y_TOP, 38), (Y_BOT, 54)):
            tray(d, x, yb + 14)
            plug(d, x - dx, yb, w=44)
            plug(d, x + dx, yb, w=44)
    racks = down(racks)
    lab_top = label([("5 PASANG BERSENTUHAN", 36, YELLOW, True)], edge=YELLOW + (220,))
    lab_bot = label([("5 PASANG DIPISAH", 36, WHITE, True)])
    weeks = [label([(f"MINGGU {k}", 38, GREEN, True)], edge=GREEN + (230,)) for k in range(1, 8)]
    gap = Image.new("RGBA", (44 * S, 24 * S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gap)
    gd.line([(4 * S, 12 * S), (40 * S, 12 * S)], fill=YELLOW + (255,), width=4 * S)
    for x0, s_ in ((4, 1), (40, -1)):
        gd.polygon([(x0 * S, 12 * S), ((x0 + 10 * s_) * S, 4 * S), ((x0 + 10 * s_) * S, 20 * S)], fill=YELLOW + (255,))
    # Diuji: 0.05, yang 0.71, bersentuhan 0.90, pulih 1.59, dalam 1.96, tujuh 2.17, minggu! 2.43, Yang 2.89, dipisah 3.11, beberapa 3.54
    out = []
    for t in times:
        im = bg.copy()
        im.alpha_composite(fade(racks, ramp(t, 0.0, 0.25)))
        top = layer()
        for i, x in enumerate(XS):
            a_h, a_w, _ = small[2 * i]
            b_h, b_w, b_d = small[2 * i + 1]
            al = ramp(t, 0.04 * i, 0.04 * i + 0.25)
            c = ramp(t, 1.62 + 0.07 * i, 2.4 + 0.07 * i)
            place(top, a_h, x - 38, Y_TOP, al)
            place(top, mix(b_w, b_h, c).transpose(Image.FLIP_LEFT_RIGHT), x + 38, Y_TOP, al)
            g = 0.55 * ramp(t, 3.15, 3.85)
            place(top, a_h, x - 54, Y_BOT, al)
            place(top, mix(b_w, b_d, g).transpose(Image.FLIP_LEFT_RIGHT), x + 54, Y_BOT, al)
        dd = ImageDraw.Draw(top)
        for i, x in enumerate(XS):
            if 0.85 < t < 1.75:  # the contact points of the touching row
                ring(dd, x, Y_TOP - 92, 24 * pop(t, 0.88 + 0.03 * i), YELLOW, 230 * (1 - ramp(t, 1.5, 1.75)), w=5)
            if t > 2.4 + 0.05 * i:
                check(dd, x, Y_TOP - 170, 20 * pop(t, 2.4 + 0.05 * i))
            put(top, gap, x, Y_BOT - 92, a=ramp(t, 3.1 + 0.04 * i, 3.25 + 0.04 * i))
        put(top, lab_top, 300, 600, a=ramp(t, 0.68, 0.8), scale=pop(t, 0.68))
        if t >= 1.56:
            k = min(6, int(7 * ramp(t, 1.6, 2.45)))
            put(top, weeks[k], 860, 600, scale=pop(t, 1.56))
        put(top, lab_bot, 300, 905, a=ramp(t, 2.86, 2.98), scale=pop(t, 2.86))
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_tolak ----------
def spark(d, x, y, u, a):
    """a red jagged spark at (x, y), grown to the fraction u"""
    rng = np.random.default_rng(3)
    for k in range(9):
        ang = 2 * math.pi * k / 9 + rng.uniform(-0.2, 0.2)
        pts, r = [(x, y)], 0
        for j in range(4):
            r += (16 + 10 * rng.random()) * u
            off = (8 if j % 2 else -8) * u
            pts.append((x + r * math.cos(ang) - off * math.sin(ang), y + r * math.sin(ang) + off * math.cos(ang)))
        d.line(sc(pts), fill=RED + (round(255 * a),), width=5 * S, joint="curve")


def cross(d, x, y, r, a):
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(170, 20, 20, round(235 * a)), outline=(255, 255, 255, round(230 * a)), width=3 * S)
    for s in (1, -1):
        d.line(sc([(x - 0.42 * r, y - 0.42 * r * s), (x + 0.42 * r, y + 0.42 * r * s)]), fill=(255, 255, 255, round(255 * a)), width=max(3, round(r * 0.2)) * S)


def tolak(times):
    bg = navy(540, 920)
    a_h, = fragment(41, 170, 230, (HEALTHY,))
    b_w, b_h = fragment(41, 170, 230, (BLEACHED, HEALTHY))
    c_w, = fragment(52, 170, 230, (BLEACHED,))
    f_f, = fragment(63, 180, 236, (FOREIGN,))
    b_w, b_h = b_w.transpose(Image.FLIP_LEFT_RIGHT), b_h.transpose(Image.FLIP_LEFT_RIGHT)
    racks = layer()
    d = ImageDraw.Draw(racks)
    for x in (450, 612):
        plug(d, x, 880, w=96)
    racks = down(racks)
    pl = plug_sprite(96)  # the bottom pair moves, so each keeps its plug under it
    lab_klon = label([("KLON", 38, GREEN, True)], edge=GREEN + (230,))
    lab_asing = label([("BEDA GEN", 38, (255, 120, 110), True)], edge=RED + (230,))
    # Tapi 0.02, harus 0.46, kembaran 0.65, sendiri... 0.97, karang 1.77, asing 2.14, saling 2.32, menolak, 2.58
    t_slide, t_hit, t_rej = 1.72, 2.12, 2.3
    out = []
    for t in times:
        im = bg.copy()
        im.alpha_composite(fade(racks, ramp(t, 0.0, 0.2)))
        top = layer()
        al = ramp(t, 0.0, 0.25)
        place(top, a_h, 450, 880, al)
        place(top, mix(b_w, b_h, ramp(t, 0.6, 1.2)), 612, 880, al)
        dd = ImageDraw.Draw(top)
        if t > 0.95:
            check(dd, 800, 760, 30 * pop(t, 0.95))
        put(top, lab_klon, 800, 850, a=ramp(t, 0.95, 1.08), scale=pop(t, 0.95))
        # the foreign coral slides in on its plug, touches, is rejected: both pull back
        ab = ramp(t, 1.45, 1.7)
        fx = 840 - 210 * ramp(t, t_slide, t_hit) + 34 * ramp(t, t_rej, t_rej + 0.25)
        cx = 450 - 22 * ramp(t, t_rej, t_rej + 0.25)
        for x, spr, a in ((cx, c_w, ab), (fx, f_f, ab * ramp(t, t_slide - 0.1, t_slide + 0.1))):
            place(top, pl, x, 1160 + 31, a)
            place(top, spr, x, 1160, a)
        dd = ImageDraw.Draw(top)
        if t >= t_rej:
            u = ramp(t, t_rej, t_rej + 0.18)
            spark(dd, 545, 1040, u, 1 - ramp(t, 2.85, 3.0))
            cross(dd, 545, 1040, 34 * pop(t, t_rej + 0.12), ramp(t, t_rej + 0.12, t_rej + 0.2))
        put(top, lab_asing, 850, 1130, a=ramp(t, 2.1, 2.22), scale=pop(t, 2.1))
        im.alpha_composite(down(top))
        out.append(im)
    return out


OUT = {"panas": "clips/skema_panas.mp4", "sentuh": "clips/skema_sentuh.mp4", "uji": "clips/skema_uji.mp4", "tolak": "clips/skema_tolak.mp4"}

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
            encode(globals()[name]([i / FPS for i in range(N[name])]), OUT[name])
