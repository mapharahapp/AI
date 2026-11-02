"""Framing and animations for Titik Heran #35 (run in the episode work dir after
`dl.py i:6527482 i:1540371 i:5315917`; writes img/6527482v.jpg, img/6527482k.jpg, img/6527482z.jpg, img/6527482c.jpg,
clips/skema_hook.mp4, clips/skema_terbang.mp4, clips/skema_bulu.mp4, clips/skema_kaki.mp4 and clips/skema_nama.mp4).
usage: python3 skema35.py [stills|hook|terbang|bulu|kaki|nama ...] [--sheet out.jpg t1,t2,...]   (--sheet saves those frames)
stills: the hook bird (Pixabay 6527482, a lesser bird-of-paradise in a zoo) framed under the title (v), close on the stump where its
feet hide (z), and lower in the frame for the CTA (c); the wall above the photo continues its own top rows, mirrored and blurred.
k is the trade-skin look: the bird cut out (a difference matte against the blurred wall, inside a hand-traced outline that leaves
the stump out), toned sepia and laid slightly tilted in a dark box. The real trade skins had their feet (and often the wings) cut off.
skema_hook: the hook frame; on "tak" a yellow ring pops around the spot where the feet should be, and a "?" beside it on "kaki".
skema_terbang: the same cut-out skin, in gold light, rises slowly through the sunbeams of Pixabay 5315917 (the dove cropped out).
skema_bulu: close on the plumes; on "burung surga" a soft gold light runs down them.
skema_kaki: Pixabay 1540371 (a bird-of-paradise gripping a trunk, both feet in view) as render.py's kind b; yellow rings pop on
both feet on "Ternyata", and on "dipotong" red dashed cut lines draw across the legs above them.
skema_nama: a museum label card for Paradisaea apoda (Linnaeus, 1758) over the blurred, darkened 1540371; on "Artinya" the parts of
the name light up with their meanings (Paradisaea = burung surga, a- = tanpa, poda = kaki).
Event times are seconds from the start of each clip, read off `render.py 35 plan`: skema_hook starts at 0 ("tak" 3,11, "kaki!"
3,52), skema_terbang at 8,50, skema_bulu at 12,87 ("burung" 1,44), skema_kaki at 16,43 ("dipotong" 1,35), skema_nama at 22,47
("Artinya:" 1,66, "burung" 2,53).
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode

MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
SERIF_BI = "/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf"
SERIF_I = "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"
N = {"hook": 138, "terbang": 104, "bulu": 81, "kaki": 114, "nama": 108}  # frames: each clip runs ~0,3 s past its shot
RED = (235, 52, 52)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def box1(x, r, axis):
    c = np.cumsum(np.pad(x, [(r + 1, r) if k == axis else (0, 0) for k in range(x.ndim)], mode="edge"), axis=axis)
    n = x.shape[axis]
    return (np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis) - np.take(c, np.arange(n), axis=axis)) / (2 * r + 1)


def blur(x, s):
    """three box passes, close to a Gaussian of sigma s (float arrays; PIL cannot blur them)"""
    r = max(1, int(round(s * 0.9)))
    for _ in range(3):
        x = box1(box1(x, r, 0), r, 1)
    return x


# ---------- the hook photo ----------
BIRD = "img/6527482.jpg"
SAFE = 200  # the photo's top 200 rows are wall only (the head starts at y 245), so they can be mirrored upward


def framed(s, ax, ay, fx, fy):
    """6527482 scaled by s with its point (ax, ay) on frame point (fx, fy); rows above its top edge continue the wall:
    its top rows reflected back and forth, blurred more and darkened a little the further they are from the photo"""
    im = Image.open(BIRD).convert("RGB")
    big = np.asarray(im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS), np.float32)
    x0, y0 = round(ax * s - fx), round(fy - ay * s)
    big = big[:, x0:x0 + W]
    out = np.zeros((H, W, 3), np.float32)
    top = max(0, y0)
    out[top:] = big[top - y0:top - y0 + H - top]
    if y0 > 0:
        safe = round(SAFE * s)
        k = np.arange(1, y0 + 1)
        src = np.abs((k - 1 + safe) % (2 * safe) - safe)  # a triangle wave: mirrored, then the right way round, ...
        ext = big[src][::-1]  # row y0-1 (just above the photo) is the photo's row 0
        d = (y0 - np.arange(y0, dtype=np.float32))[:, None, None] / y0  # 0 at the photo edge, 1 at the frame top
        soft = blur(ext, 9)
        e = ext * (1 - np.clip(d * 3, 0, 1)) + soft * np.clip(d * 3, 0, 1)
        out[:y0] = e * (1 - 0.22 * d)
        lo, a0 = max(0, y0 - 40), max(0, y0 - 12)  # soften the fold
        out[a0:y0 + 12] = blur(out[lo:y0 + 40], 3)[a0 - lo:a0 - lo + y0 + 12 - a0]
    return out


def stills():
    for name, args in [("v", (1.7, 400, 265, 540, 600)), ("z", (2.2, 330, 590, 540, 960)), ("c", (1.5, 400, 265, 540, 860))]:
        Image.fromarray(framed(*args).clip(0, 255).astype(np.uint8)).save(f"img/6527482{name}.jpg", quality=95)
        print(f"img/6527482{name}.jpg")
    Image.fromarray(kulit_still()).save("img/6527482k.jpg", quality=95)
    print("img/6527482k.jpg")


# ---------- the cut-out skin ----------
OUTLINE = [(185, 296), (205, 275), (228, 262), (248, 250), (275, 245), (300, 250), (318, 262), (340, 284), (348, 296), (382, 316),
           (432, 345), (472, 385), (503, 425), (524, 456), (540, 488), (548, 512), (585, 545), (605, 570), (618, 600), (620, 650),
           (614, 700), (605, 760), (592, 815), (583, 880), (565, 920), (548, 950), (540, 1000), (522, 1100), (505, 1180), (495, 1270),
           (240, 1270), (238, 1180), (250, 1120), (268, 1050), (290, 980), (310, 920), (330, 860), (345, 790), (358, 720), (366, 670),
           (370, 600), (373, 560), (376, 532), (370, 522), (352, 515), (332, 502), (310, 482), (285, 455), (262, 428), (245, 400),
           (234, 368), (231, 338), (230, 318), (218, 305), (200, 302)]


def skin():
    """the bird as an RGBA array (photo size): solid inside the traced outline, a difference matte against the wall at its edge,
    the plume tips fading out above the branches at the bottom"""
    im = Image.open(BIRD).convert("RGB")
    a = np.asarray(im, np.float32)
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).polygon(OUTLINE, fill=255)
    out = 1 - np.asarray(m.filter(ImageFilter.MaxFilter(15)), np.float32) / 255
    bg = blur(a * out[..., None], 30) / (blur(out, 30)[..., None] + 1e-4)  # the wall behind the bird, filled in from around it
    d = np.sqrt(((a - bg) ** 2).sum(-1))
    matte = np.clip((d - 30) / 40, 0, 1) * np.asarray(m.filter(ImageFilter.GaussianBlur(2)), np.float32) / 255
    core = np.asarray(m.filter(ImageFilter.MinFilter(37)).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    yy = np.arange(im.height, dtype=np.float32)[:, None]
    alpha = np.maximum(matte, core) * np.clip((1210 - yy) / 330, 0, 1) ** 1.6
    return np.dstack([a, alpha * 255])


def sepia(rgb, k=1.0):
    m = np.array([[.393, .769, .189], [.349, .686, .168], [.272, .534, .131]], np.float32)
    return rgb * (1 - k) + (rgb @ m.T) * k


def sprite(arr, s, rot):
    """an RGBA float array scaled by s and rotated by rot degrees (counter-clockwise), as a PIL RGBA image"""
    im = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return im.rotate(rot, resample=Image.BICUBIC, expand=True)


def paste_center(base, sp, cx, cy, alpha=1.0):
    if alpha < 1:
        sp = sp.copy()
        sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(sp, (round(cx - sp.width / 2), round(cy - sp.height / 2)))


SKIN_BOX = (245, 1200)  # the skin's height span in the photo (head top to faded plume tips)


def kulit_still():
    """the trade skin, sepia and a little faded, lying tilted in a dark wooden box"""
    rng = np.random.default_rng(35)
    g = rng.normal(0, 1, (H // 8, W // 2)).astype(np.float32)
    grain = np.asarray(Image.fromarray(g).resize((W, H), Image.BICUBIC), np.float32)  # streaks along the wood
    v = (YY / H)[..., None]
    wood = (np.array([58, 40, 26], np.float32) * (1 - v) + np.array([34, 23, 15], np.float32) * v) * (1 + 0.10 * grain[..., None])
    edge = np.minimum(np.minimum(XX, W - XX), np.minimum(YY, H - YY))
    wood *= (0.45 + 0.55 * np.clip(edge / 140, 0, 1))[..., None]  # the box walls in shadow
    base = Image.fromarray(wood.clip(0, 255).astype(np.uint8)).convert("RGBA")
    sk = skin()
    sk[..., :3] = sepia(sk[..., :3], 0.85) * 0.92 + 8
    sp = sprite(sk[200:1240], 1.3, -14)
    sh = Image.new("RGBA", sp.size, (0, 0, 0, 0))
    sh.putalpha(sp.getchannel("A").point(lambda x: int(x * 0.7)).filter(ImageFilter.GaussianBlur(14)))
    paste_center(base, sh, 540 + 18, 1180 + 26)
    paste_center(base, sp, 540, 1180)
    out = np.asarray(base.convert("RGB"), np.float32)
    out *= (1 - 0.35 * (((XX - W / 2) / (W / 2)) ** 2 + ((YY - 1150) / (H / 2)) ** 2) / 2)[..., None]  # vignette
    return out.clip(0, 255).astype(np.uint8)


# ---------- skema_hook ----------
FEET = (472, 1075)  # where the feet should be in img/6527482v.jpg (they grip the stump behind the plumes)


def ring_layer(rings, size=(W, H)):
    """see-through rings drawn at 2x on their own layer: [(x, y, r, colour, alpha 0-1, width)]"""
    L = Image.new("RGBA", (size[0] * S, size[1] * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    for x, y, r, col, a, w in rings:
        if a > 0.01 and r > 1:
            d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], outline=col + (round(255 * min(a, 1)),), width=w * S)
    return L.resize(size, Image.LANCZOS)


def qmark(size, a):
    f = ImageFont.truetype(XB, size * S)
    sp = Image.new("RGBA", (size * S * 2, size * S * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(sp)
    d.text((size * S, size * S), "?", font=f, fill=YELLOW + (round(255 * a),), anchor="mm", stroke_width=round(size * 0.06) * S,
           stroke_fill=(0, 0, 0, round(255 * a)))
    return sp.resize((size * 2, size * 2), Image.LANCZOS)


def skema_hook(times=None):
    base = Image.open("img/6527482v.jpg").convert("RGBA")
    t_ring, t_q = 3.10, 3.52
    frames = []
    for i in range(N["hook"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        im = base.copy()
        if t >= t_ring:
            r = 82 * pop(t, t_ring, 0.28) * (1 + 0.04 * math.sin(2 * math.pi * 2.2 * (t - t_ring)))
            glow = ring_layer([(FEET[0], FEET[1], r, YELLOW, 0.35, 16)]).filter(ImageFilter.GaussianBlur(8))
            im.alpha_composite(glow)
            im.alpha_composite(ring_layer([(FEET[0], FEET[1], r, YELLOW, 1.0, 7)]))
        if t >= t_q:
            k = pop(t, t_q, 0.3)
            q = qmark(round(120 * max(k, 0.05) * (1 + 0.06 * math.sin(2 * math.pi * 2.2 * (t - t_q)))), 1.0)
            paste_center(im, q, FEET[0] - 165, FEET[1] - 10)
        frames.append(im.convert("RGB"))
    return frames


# ---------- skema_terbang ----------
def skema_terbang(times=None):
    sky = Image.open("img/5315917.jpg").convert("RGB")
    sk = skin()[200:1240]
    sk[..., :3] = sepia(sk[..., :3], 0.55) * 1.05 + np.array([18, 10, 0], np.float32)  # an old skin, warmed by the light
    alpha_glow = np.asarray(Image.fromarray((sk[..., 3]).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18)), np.float32) / 255
    halo = np.dstack([np.full(alpha_glow.shape + (3,), (255, 228, 160), np.float32), alpha_glow * 170])
    frames = []
    n = N["terbang"]
    for i in range(n):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        u = t / (n / FPS)
        s = 2.27 * (1 + 0.06 * u)  # the sky pushes in slowly toward the light (2,27x just fills the frame's height)
        cx, cy = 520, 426.5 - 15 * u
        box = (cx - W / 2 / s, cy - H / 2 / s, cx + W / 2 / s, cy + H / 2 / s)
        bg = sky.resize((W, H), Image.LANCZOS, box=box)
        bg = np.asarray(bg, np.float32)
        bg = bg * np.array([1.06, 1.0, 0.86], np.float32) + np.array([10, 4, -6], np.float32)  # gold grade
        im = Image.fromarray(bg.clip(0, 255).astype(np.uint8)).convert("RGBA")
        e = 1 - (1 - min(u * 1.15, 1)) ** 2  # ease-out rise
        y = 1500 - 470 * e
        rot = -10 + 6 * e + 2.2 * math.sin(2 * math.pi * 0.45 * t)
        sc_ = 0.58 + 0.04 * e
        gl = sprite(halo, sc_, rot)
        paste_center(im, gl, 540, y, 0.55 + 0.35 * e)
        paste_center(im, sprite(sk, sc_, rot), 540, y, min(1.0, t / 0.15 + 0.2))
        frames.append(im.convert("RGB"))
    return frames


# ---------- skema_bulu ----------
def skema_bulu(times=None):
    s_, ax, ay = 2.0, 430, 200  # the photo's (430, 200) at the frame's top centre: head above the title, the yellow in the middle
    base = framed(s_, ax, ay, 540, 0) * 0.9  # a little darker, so the light has room to show
    a = Image.fromarray(skin()[..., 3].astype(np.uint8))
    a = a.resize((round(a.width * s_), round(a.height * s_)), Image.LANCZOS)
    x0, y0 = round(ax * s_ - 540), round(ay * s_)
    plume = np.asarray(a, np.float32)[y0:y0 + H, x0:x0 + W] / 255
    plume *= np.clip((YY - 560) / 160, 0, 1)  # the plumes only, not the dark back
    rng = np.random.default_rng(351)
    glints = [(rng.uniform(0.05, 0.95), rng.uniform(-60, 60), rng.uniform(0.6, 1.0)) for _ in range(9)]
    t0, t1 = 1.25, 2.35  # "burung surga"
    frames = []
    for i in range(N["bulu"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        out = base.copy()
        u = (t - t0) / (t1 - t0)
        warm = ramp(t, 1.1, 2.0)
        out += (plume * 0.12 * warm)[..., None] * np.array([255, 205, 120], np.float32)  # the plumes warm up
        if -0.2 < u < 1.3:
            c = 300 + 1900 * u  # a diagonal band running down the plumes
            band = np.exp(-((XX * 0.35 + YY * 0.94) - c) ** 2 / (2 * 110 ** 2)) * plume
            out += band[..., None] * np.array([255, 232, 170], np.float32) * 0.5
            out += blur(band, 22)[..., None] * np.array([255, 200, 90], np.float32) * 0.6  # its glow spills past the edge
            out = out.clip(0, 255)
            im = Image.fromarray(out.astype(np.uint8)).convert("RGBA")
            for p, off, k in glints:  # small glints where the band crosses the plumes
                gy = 560 + p * 1250
                gx = (c - gy * 0.94) / 0.35 + off
                if 0 < gx < W and plume[int(min(gy, H - 1)), int(gx)] > 0.5:
                    put_glint(im, gx, gy, 26 * k)
            frames.append(im.convert("RGB"))
            continue
        frames.append(Image.fromarray(out.clip(0, 255).astype(np.uint8)))
    return frames


def put_glint(im, x, y, r):
    """a soft four-point star"""
    L = Image.new("RGBA", (round(4 * r), round(4 * r)), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    c = 2 * r
    d.polygon([(c, c - 2 * r), (c + 0.18 * r, c), (c, c + 2 * r), (c - 0.18 * r, c)], fill=(255, 250, 225, 230))
    d.polygon([(c - 1.4 * r, c), (c, c - 0.14 * r), (c + 1.4 * r, c), (c, c + 0.14 * r)], fill=(255, 250, 225, 230))
    L = L.filter(ImageFilter.GaussianBlur(1.2))
    g = Image.new("RGBA", L.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([c - 0.5 * r, c - 0.5 * r, c + 0.5 * r, c + 0.5 * r], fill=(255, 236, 180, 200))
    g = g.filter(ImageFilter.GaussianBlur(0.4 * r))
    g.alpha_composite(L)
    im.alpha_composite(g, (round(x - c), round(y - c)))


# ---------- skema_kaki ----------
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
    return bg.convert("RGBA"), (H - fg.height) // 2, W / im.width


def dashed_line(d, a, b, u, col, width, dash=16, gap=11):
    """a dashed line from a to b (1x points), drawn on up to the fraction u of its length, on a 2x layer"""
    L = math.dist(a, b) * u
    k = 0
    while k * (dash + gap) < L:
        s0, s1 = k * (dash + gap), min(k * (dash + gap) + dash, L)
        p = [(a[0] + (b[0] - a[0]) * s / math.dist(a, b), a[1] + (b[1] - a[1]) * s / math.dist(a, b)) for s in (s0, s1)]
        d.line([(x * S, y * S) for x, y in p], fill=col, width=width * S)
        k += 1


def skema_kaki(times=None):
    base, y0, k = kind_b("img/1540371.jpg")
    P = lambda x, y: (x * k, y0 + y * k)
    feet = [(P(915, 305), 60, 0.28), (P(845, 640), 64, 0.42)]  # (centre, radius, pop time): the foot on the trunk, the lower foot
    cuts = [(P(872, 236), P(860, 372)), (P(824, 530), P(728, 616))]  # across the legs just above each foot
    t_cut = 1.36
    frames = []
    for i in range(N["kaki"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        im = base.copy()
        rings = []
        for (x, y), r, tp in feet:
            if t >= tp:
                rr = r * pop(t, tp, 0.28) * (1 + 0.035 * math.sin(2 * math.pi * 2.0 * (t - tp)))
                rings.append((x, y, rr, YELLOW, 1.0, 6))
        if rings:
            im.alpha_composite(ring_layer([(x, y, r, c, 0.4, 16) for x, y, r, c, _, _ in rings]).filter(ImageFilter.GaussianBlur(7)))
            im.alpha_composite(ring_layer(rings))
        if t >= t_cut:
            L = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
            d = ImageDraw.Draw(L)
            for n_, (a, b) in enumerate(cuts):
                u = ramp(t, t_cut + 0.12 * n_, t_cut + 0.12 * n_ + 0.3)
                if u > 0:
                    dashed_line(d, a, b, u, (255, 255, 255, 230), 12)
                    dashed_line(d, a, b, u, RED + (255,), 8)
            im.alpha_composite(L.resize((W, H), Image.LANCZOS))
        frames.append(im.convert("RGB"))
    return frames


# ---------- skema_nama ----------
def skema_nama(times=None):
    bird = Image.open("img/1540371.jpg").convert("RGB")
    k = max(W / bird.width, H / bird.height)
    bg = bird.resize((round(bird.width * k), round(bird.height * k)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = Image.fromarray((np.asarray(bg.filter(ImageFilter.GaussianBlur(24)), np.float32) * 0.42).astype(np.uint8)).convert("RGBA")
    CARD = (90, 590, 990, 1180)
    t_in, t_art, t_apo = 0.02, 1.70, 2.30  # "Paradisea", "Artinya:", then the parts of "apoda"
    cream, ink, brown = (246, 239, 222), (40, 30, 22), (120, 96, 70)
    fn = ImageFont.truetype(SERIF_BI, 98 * S)
    f_small = ImageFont.truetype(MED, 30 * S)
    f_auth = ImageFont.truetype(SERIF_I, 42 * S)
    f_mean = ImageFont.truetype(XB, 44 * S)
    f_note = ImageFont.truetype(MED, 28 * S)
    w1, wa, wp = fn.getlength("Paradisaea "), fn.getlength("a"), fn.getlength("poda")
    x_name = W * S / 2 - (w1 + wa + wp) / 2
    y_name = 765 * S

    def mix(c0, c1, u):  # fade text in on the opaque card (ImageDraw replaces pixels, so alpha would show the photo through)
        return tuple(round(a * (1 - u) + b * u) for a, b in zip(c0, c1)) + (255,)

    def card(t):
        L = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        x0, y0, x1, y1 = [v * S for v in CARD]
        d.rounded_rectangle([x0 + 10 * S, y0 + 14 * S, x1 + 10 * S, y1 + 14 * S], radius=26 * S, fill=(0, 0, 0, 110))
        d.rounded_rectangle([x0, y0, x1, y1], radius=26 * S, fill=cream + (255,))
        d.rounded_rectangle([x0 + 18 * S, y0 + 18 * S, x1 - 18 * S, y1 - 18 * S], radius=16 * S, outline=brown + (255,), width=2 * S)
        d.text((W * S / 2, 655 * S), "NAMA ILMIAH", font=f_small, fill=brown + (255,), anchor="mm")
        hl = [(x_name, x_name + w1 - fn.getlength(" "), ramp(t, t_art, t_art + 0.25)),
              (x_name + w1, x_name + w1 + wa, ramp(t, t_apo, t_apo + 0.2)),
              (x_name + w1 + wa + 6 * S, x_name + w1 + wa + wp, ramp(t, t_apo + 0.25, t_apo + 0.45))]
        for a, b, u in hl:  # a highlighter swiped under each part
            if u > 0:
                d.rounded_rectangle([a - 6 * S, y_name - 50 * S, a + (b - a + 6 * S) * u + 6 * S, y_name + 46 * S], radius=10 * S,
                                    fill=(255, 222, 92, 255))
        d.text((x_name, y_name), "Paradisaea ", font=fn, fill=ink + (255,), anchor="lm")
        d.text((x_name + w1, y_name), "a", font=fn, fill=ink + (255,), anchor="lm")
        d.text((x_name + w1 + wa, y_name), "poda", font=fn, fill=ink + (255,), anchor="lm")
        d.text((W * S / 2, 868 * S), "Linnaeus, 1758  ·  cenderawasih besar", font=f_auth, fill=brown + (255,), anchor="mm")
        rows = [("Paradisaea = burung surga", t_art + 0.1, 1026), ("a- = tanpa  ·  poda = kaki", t_apo + 0.3, 1086)]
        for text, tt, y in rows:
            u = ramp(t, tt, tt + 0.25)
            if u > 0:
                d.text((W * S / 2, (y + 14 * (1 - u)) * S), text, font=f_mean, fill=mix(cream, (150, 30, 20), u), anchor="mm")
        u = ramp(t, t_apo + 0.5, t_apo + 0.75)
        if u > 0:
            d.text((W * S / 2, 1132 * S), "dari bahasa Yunani", font=f_note, fill=mix(cream, brown, u), anchor="mm")
        return L.resize((W, H), Image.LANCZOS)

    frames = []
    for i in range(N["nama"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        im = bg.copy()
        c = card(t)
        p = pop(t, t_in, 0.32)
        if p < 0.999:
            sc_ = 0.82 + 0.18 * p
            cw, ch = round(W * sc_), round(H * sc_)
            c = c.resize((cw, ch), Image.LANCZOS)
            cc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            cc.alpha_composite(c, ((W - cw) // 2, round(885 - 885 * sc_)))
            c = cc
            c.putalpha(c.getchannel("A").point(lambda v: int(v * min(1.0, t / 0.12))))
        im.alpha_composite(c)
        frames.append(im.convert("RGB"))
    return frames


def sheet(frames, name, out):
    picks = [f for f in frames if f is not None]
    tw, th = 360, 640
    sh = Image.new("RGB", (len(picks) * (tw + 6) - 6, th), (40, 40, 40))
    for k, f in enumerate(picks):
        sh.paste(f.resize((tw, th), Image.LANCZOS), (k * (tw + 6), 0))
    base, ext = os.path.splitext(out)
    sh.save(f"{base}_{name}{ext}", quality=88)
    print(f"{base}_{name}{ext}")


if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or ["stills", "hook", "terbang", "bulu", "kaki", "nama"]
    if "stills" in todo:
        stills()
    for name, fn in [("hook", skema_hook), ("terbang", skema_terbang), ("bulu", skema_bulu), ("kaki", skema_kaki), ("nama", skema_nama)]:
        if name in todo:
            fr = fn(times)
            if times is not None:
                sheet(fr, name, out)
            else:
                encode(fr, f"clips/skema_{name}.mp4")
