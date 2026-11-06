"""Stills and schematic animations for Titik Heran #42 (run in the episode work dir after
`dl.py v:89527 v:197525 i:3895160 v:145647` and the museum photos below; writes img/lock1v.jpg, img/lock4v.jpg,
clips/skema_cincin.mp4 and clips/skema_kode.mp4).
The lock photos are Amgueddfa Cymru - Museum Wales's own (object no. 2025.17H/2.6, "Image: by permission of Amgueddfa Cymru -
Museum Wales"), read from the IIIF server behind https://museum.wales/collections/online/object/f33a582e-7d7d-35f0-8011-f0cac35e8aba
(base https://museum.wales/col-media/iiif/2/; museum.wales has to be an allowed host of the cloud environment):
  img/lock1h.jpg  zoom%2F226%2F197%2Fannefrancis_presentation_ri014.ptif/full/3100,/0/default.jpg  three-quarter view with reflection
  img/lock4h.jpg  zoom%2F226%2F183%2Fannefrancin_lock_presentation.ptif/full/2626,/0/default.jpg     front, other letters turned up
  img/lock5h.jpg  zoom%2F236%2F725%2F2026_06_09_09_35_50__b_r8_s4_.ptif/full/full/0/default.jpg      front, cm scale below (June 2026)
The museum's reuse terms ask for written permission (images@museumwales.ac.uk); the video credits the museum on every shot.
usage: python3 skema42.py [prep|cincin|kode ...] [--sheet out.jpg t1,t2,...]
prep: img/lock1v.jpg and img/lock4v.jpg, the lock set into 9:16 on its own black ground (the hook title above, captions below).
skema_cincin: lock5h close on the letter cylinder; the four rings that turn are outlined and numbered one by one, then blur as
  if spun ("diputar"); the camera pulls back to the whole lock over the cm scale, and on "gagal" a red TETAP TERKUNCI stamp lands
  with a shake and a 3,2 cm dimension line appears (the museum gives 31,8 mm; the scale in the photo agrees).
skema_kode: the same close view turned into a cyan scan look by a sweeping line; on each spelled letter its ring lights up and
  a gold card shows the code letter (A N C E on rings 1-4, as in the museum's ring list). A schematic, not the CT image.
Event times are seconds from the start of each clip, read off `render.py 42 plan`: skema_cincin starts at 12,93 ("cincin" 0,37,
"diputar" 1,80, "tapi" 2,97, "gagal" 4,49), skema_kode at 21,47 ("dan" 0,05, "A" 1,51, "En" 2,36, "Ce" 2,94, "E" 3,51).
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, text_sprite, encode
from skema27 import stamp_sprite
from skema35 import blur, sheet
from skema37 import to_img, put1
from skema39 import lum, title_shade

N = {"cincin": 179, "kode": 131}  # each clip runs ~0,3 s past its shot
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
GOLD = (255, 205, 70)

# lock5h.jpg (2928 x 2612): the four turning rings (x spans), the letter cylinder (rows), the whole lock and the cm scale
RINGS = [(1086, 1226), (1226, 1372), (1372, 1519), (1519, 1671)]
CYL = (952, 1202, 1941, 1830)   # x0, y0, x1, y1 of the cylinder with its two end plates
LOCK = (947, 455, 1941, 1836)   # shackle top to cylinder bottom: 31,8 mm
CLOSE = (1.0, (1446, 1516), (540, 985))      # scale, source point, where it lands in the frame
WIDE = (0.42, (1444, 1145.5), (540, 980))
CODE = "ANCE"
YY = np.mgrid[0:H, 0:W][0].astype(np.float32)


def wanted(i, times):
    return times is None or any(abs(i / FPS - x) < 0.5 / FPS for x in times)


# ---------- prep: the two hook stills ----------
def prep():
    im = Image.open("img/lock1h.jpg").convert("RGB")
    s = 0.909  # the lock 550 px tall, its top at y 650 (under the two-line title and the KARAM 1583 label)
    big = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    big.crop((835, 168, 835 + W, 168 + H)).save("img/lock1v.jpg", quality=95)
    print("img/lock1v.jpg")
    im = Image.open("img/lock4h.jpg").convert("RGB")
    s = 0.70  # the lock 560 px tall from y 730 (under the three-line title)
    big = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    f = Image.new("RGB", (W, H), (0, 0, 0))
    f.paste(big.crop((345, 0, 345 + W, big.height)), (0, 542))
    f.save("img/lock4v.jpg", quality=95)
    print("img/lock4v.jpg")


# ---------- the camera on lock5h ----------
SRC = None


def source():
    global SRC
    if SRC is None:
        im = Image.open("img/lock5h.jpg").convert("RGB")
        SRC = (im, im.resize((im.width // 2, im.height // 2), Image.LANCZOS))  # the half copy keeps the wide view from aliasing
    return SRC


def cam(u):
    """the camera between CLOSE (u=0) and WIDE (u=1): scale, source point, frame point"""
    (s0, c0, f0), (s1, c1, f1) = CLOSE, WIDE
    s = math.exp(math.log(s0) + (math.log(s1) - math.log(s0)) * u)
    c = (c0[0] + (c1[0] - c0[0]) * u, c0[1] + (c1[1] - c0[1]) * u)
    f = (f0[0] + (f1[0] - f0[0]) * u, f0[1] + (f1[1] - f0[1]) * u)
    return s, c, f


def view(s, c, f, dx=0.0):
    full, half = source()
    im, k = (half, 0.5) if s < 0.7 else (full, 1.0)
    sk = s / k
    data = (1 / sk, 0, c[0] * k - (f[0] + dx) / sk, 0, 1 / sk, c[1] * k - f[1] / sk)
    return im.transform((W, H), Image.AFFINE, data, resample=Image.BICUBIC, fillcolor=(0, 0, 0))


def to_frame(x, y, s, c, f, dx=0.0):
    return (x - c[0]) * s + f[0] + dx, (y - c[1]) * s + f[1]


def vblur_strip(a, x0, x1, y0, y1, r):
    """vertical box blur of one ring's strip (radius r px), as if it spins"""
    if r < 1:
        return
    x0, x1, y0, y1 = int(x0), int(x1), int(y0), int(y1)
    r = int(r)
    seg = a[y0 - r:y1 + r + 1, x0:x1]
    cs = np.cumsum(np.pad(seg, ((1, 0), (0, 0), (0, 0))), axis=0)
    out = (cs[2 * r + 1:] - cs[:-2 * r - 1]) / (2 * r + 1)
    a[y0:y1, x0:x1] = out[:y1 - y0]


def number_badge(n):
    f = ImageFont.truetype(XB, 40 * S)
    sp = Image.new("RGBA", (84 * S, 84 * S))
    d = ImageDraw.Draw(sp)
    d.ellipse([4 * S, 4 * S, 80 * S, 80 * S], fill=(16, 22, 40, 225), outline=YELLOW + (255,), width=4 * S)
    d.text((42 * S, 43 * S), str(n), font=f, fill=YELLOW + (255,), anchor="mm")
    return sp


def skema_cincin(times=None):
    t_ring, t_spin, t_pull, t_fail = 0.37, 1.80, 2.97, 4.49
    badges = [number_badge(k + 1) for k in range(4)]
    stamp = stamp_sprite("TETAP TERKUNCI", size=64, angle=-7)
    dim_lab = text_sprite([("3,2 cm", 46, YELLOW, True), ("tinggi gemboknya", 26, WHITE, False)], gap=2)
    frames = []
    for i in range(N["cincin"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        u = ramp(t, t_pull, t_pull + 1.3)
        s, c, f = cam(u)
        dx = 0.0
        if t >= t_fail:  # the lock jerks when the stamp lands
            v = t - t_fail
            dx = 13 * math.exp(-v * 6.5) * math.sin(2 * math.pi * 8 * v)
        im = view(s, c, f, dx)
        a = title_shade(np.asarray(im, np.float32), k=0.4, y1=720)  # the shackle under the titles is bright brass
        if u < 0.02 and t_spin <= t < t_pull + 0.2:  # the rings blur as if spun, one after another, then settle
            for k, (x0, x1) in enumerate(RINGS):
                v = t - t_spin - 0.1 * k
                r = 30 * math.sin(math.pi * min(max(v / 0.9, 0), 1)) if v > 0 else 0
                fx0, fy0 = to_frame(x0 + 4, CYL[1] + 6, s, c, f, dx)
                fx1, fy1 = to_frame(x1 - 4, CYL[3] - 6, s, c, f, dx)
                vblur_strip(a, fx0, fx1, fy0 + 32, fy1 - 32, r)
        im = to_img(a).convert("RGBA")
        out_a = 1 - ramp(t, t_pull, t_pull + 0.4)
        if out_a > 0:
            lay = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(lay)
            for k, (x0, x1) in enumerate(RINGS):
                ka = ramp(t, t_ring + 0.12 * k, t_ring + 0.12 * k + 0.2) * out_a
                if ka <= 0:
                    continue
                fx0, fy0 = to_frame(x0 + 3, CYL[1] + 4, s, c, f, dx)
                fx1, fy1 = to_frame(x1 - 3, CYL[3] - 4, s, c, f, dx)
                d.rounded_rectangle([fx0 * S, fy0 * S, fx1 * S, fy1 * S], radius=14 * S,
                                    outline=YELLOW + (int(235 * ka),), width=5 * S)
            im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
            for k, (x0, x1) in enumerate(RINGS):
                kb = pop(t, t_ring + 0.12 * k, 0.3)
                if kb > 0:
                    fx, fy = to_frame((x0 + x1) / 2, CYL[1] + 52, s, c, f, dx)
                    put1(im, badges[k], fx, fy, a=min(1.0, kb) * out_a, scale=max(kb, 0.01))
        if t >= t_fail:  # dimension line beside the whole lock
            kd = ramp(t, t_fail + 0.05, t_fail + 0.4)
            x = to_frame(LOCK[2], 0, s, c, f)[0] + 44
            ya, yb = to_frame(0, LOCK[1], s, c, f)[1], to_frame(0, LOCK[3], s, c, f)[1]
            ym = (ya + yb) / 2
            lay = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(lay)
            col = YELLOW + (int(255 * kd),)
            y0, y1 = ym - (ym - ya) * kd, ym + (yb - ym) * kd
            d.line([(x * S, y0 * S), (x * S, y1 * S)], fill=col, width=5 * S)
            for y in (y0, y1):
                d.line([((x - 18) * S, y * S), ((x + 18) * S, y * S)], fill=col, width=5 * S)
            im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
            put1(im, dim_lab, x + 112, ym, a=kd)
            ks = ramp(t, t_fail, t_fail + 0.12)
            put1(im, stamp, 540 + dx, to_frame(0, (CYL[1] + CYL[3]) / 2, s, c, f)[1], a=ks, scale=1.5 - 0.5 * ks)
        frames.append(im.convert("RGB"))
    return frames


# ---------- the code, read off a scan ----------
def scan_look(a):
    """the photo as a cyan scan: brightness mapped to a dark-teal to cyan ramp, a faint grid and scan lines"""
    y = np.clip(lum(a) / 255, 0, 1) ** 0.85
    out = np.array([8, 26, 38], np.float32) * (1 - y)[..., None] + np.array([140, 250, 255], np.float32) * y[..., None]
    grid = np.zeros((H, W), np.float32)
    grid[::48, :] = 1
    grid[:, ::48] = 1
    out = out + grid[..., None] * np.array([10, 40, 52], np.float32)
    out = out * (1 - 0.07 * ((np.arange(H) % 4) < 1)[:, None, None])
    return out


def letter_card(ch):
    f = ImageFont.truetype(XB, 112 * S)
    w, h = 126 * S, 164 * S
    sp = Image.new("RGBA", (w + 40 * S, h + 40 * S))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([20 * S, 20 * S, 20 * S + w, 20 * S + h], radius=18 * S, fill=(14, 20, 36, 232),
                        outline=GOLD + (255,), width=6 * S)
    d.text((20 * S + w / 2, 20 * S + h / 2 + 4 * S), ch, font=f, fill=GOLD + (255,), anchor="mm")
    glow = Image.new("RGBA", sp.size)
    ImageDraw.Draw(glow).rounded_rectangle([14 * S, 14 * S, 26 * S + w, 26 * S + h], radius=22 * S, fill=GOLD + (120,))
    glow = glow.filter(ImageFilter.GaussianBlur(14 * S))
    glow.alpha_composite(sp)
    return glow


def skema_kode(times=None):
    t0, t1 = 0.05, 1.35                          # the scan line sweeps the cylinder
    t_let = [1.51, 2.36, 2.94, 3.51]             # "A", "En", "Ce", "E"
    s, c, f = cam(0.0)
    base = np.asarray(view(s, c, f), np.float32)
    scan = title_shade(scan_look(base), k=0.5, y1=720)
    base = title_shade(base, k=0.4, y1=720)
    cards = [letter_card(ch) for ch in CODE]
    ya, yb = -20, H + 20  # the line sweeps the whole frame
    frames = []
    for i in range(N["kode"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        ys = ya + (yb - ya) * ramp(t, t0, t1) if t < t1 + 0.4 else H + 100
        m = np.clip((ys - YY) / 10, 0, 1)[..., None]  # above the line: scanned
        a = base * (1 - m) + scan * m
        if t < t1 + 0.4:  # the line itself, with a soft glow
            g = np.exp(-((YY - ys) / 9) ** 2) * 0.95 + np.exp(-((YY - ys) / 40) ** 2) * 0.35
            g *= 1 - ramp(t, t1, t1 + 0.4)
            a = a + g[..., None] * np.array([120, 255, 255], np.float32)
        for k, (x0, x1) in enumerate(RINGS):  # the ring that gives a letter lights up
            kl = ramp(t, t_let[k] - 0.05, t_let[k] + 0.15)
            if kl > 0:
                fx0, fy0 = to_frame(x0 + 3, CYL[1] + 4, s, c, f)
                fx1, fy1 = to_frame(x1 - 3, CYL[3] - 4, s, c, f)
                pulse = 1 + 0.5 * math.exp(-max(t - t_let[k], 0) * 5)
                band = ((YY >= fy0) & (YY <= fy1)).astype(np.float32)
                xs = np.zeros(W, np.float32)
                xs[int(fx0):int(fx1)] = 1
                a = a + (band * xs[None, :] * 0.18 * kl * pulse)[..., None] * np.array([255, 210, 90], np.float32)
        im = to_img(a).convert("RGBA")
        lay = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(lay)
        for k, (x0, x1) in enumerate(RINGS):
            kl = ramp(t, t_let[k] - 0.05, t_let[k] + 0.15)
            if kl > 0:
                fx0, fy0 = to_frame(x0 + 3, CYL[1] + 4, s, c, f)
                fx1, fy1 = to_frame(x1 - 3, CYL[3] - 4, s, c, f)
                d.rounded_rectangle([fx0 * S, fy0 * S, fx1 * S, fy1 * S], radius=14 * S, outline=GOLD + (int(240 * kl),), width=5 * S)
        im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        for k, (x0, x1) in enumerate(RINGS):
            kp = pop(t, t_let[k], 0.28)
            if kp > 0:
                fx, _ = to_frame((x0 + x1) / 2, 0, s, c, f)
                fy = to_frame(0, (CYL[1] + CYL[3]) / 2, s, c, f)[1]
                tail = 1 + 0.06 * math.sin(math.pi * ramp(t, t_let[3] + 0.3, t_let[3] + 0.6))  # all four pulse once after "E"
                put1(im, cards[k], fx, fy, a=min(1.0, kp), scale=max(kp, 0.01) * tail)
        frames.append(im.convert("RGB"))
    return frames


OUT = {"cincin": "clips/skema_cincin.mp4", "kode": "clips/skema_kode.mp4"}
FUN = {"cincin": skema_cincin, "kode": skema_kode}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    for name in args or ["prep", "cincin", "kode"]:
        if name == "prep":
            prep()
            continue
        fr = FUN[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
