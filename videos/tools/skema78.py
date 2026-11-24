"""Schematic animations for Titik Heran #78 (run in the episode work dir; writes clips/skema_turun.mp4, h3turun.mp4,
skema_dalam.mp4, skema_tekanan.mp4, skema_gas.mp4, skema_rekor.mp4, h1gelap.mp4).
turun: Pixabay 26830 (an animated sunlit sea, tagged "ilustrasi") sinks into darkness while a pill counts the depth
  0 -> 6.148 m (the deposits were photographed at 6.148 m, Frontiers News).
h3turun: Arif's Higgsfield H3 (Pompeii at the top, the sea, a robot lighting a trench wall at the bottom); the camera
  slides from Pompeii down to the robot.
dalam: cross-section of the trench, depth to scale (surface y 560, 10.935 m at y 1190): a glowing marker on the wall
  at +-6 km "jejak letusan", Challenger Deep at the bottom, Everest (8.849 m) rising from the floor and still under water.
tekanan: Pixabay 31611 (bubbles on black, an animation) dimmed blue; counter 1x -> 600x, pill "dibanding di
  permukaan" (+-600 atm at 6 km: Live Science 592 atm, La Brujula Verde "over 600 atmospheres").
gas: a gas bubble inside magma tries to grow, arrows of water pressure push it back; on "meledak" a burst icon pops
  and is struck out with a red X (what scientists expected before this find, Nat Geo: Yeo, Stern).
rekor: two depth bars from the surface: "rekor lama +-4.000 m (Arktik, 2008)" and "temuan baru +-6.100 m", bracket
  "+2 km"; the source sits in the shot tag (render.py).
h1gelap: Higgsfield H1, lower-left part of the wall (cracked slabs), the light fades and a vignette closes in.
pad_h1: writes img/H1t.jpg, H1 with 25% more dark water on top (per-column colour of the top edge; the photo's top
  260 px, tethers included, fade into it), so the robot sits under the title in shot 09.
Event times are seconds from the start of each clip, read off `render.py 78 plan`. Text stays out of the watermark
band (y 935-985 around the centre), the title zone (y < ~600) and the captions (y >= 1210).
usage: python3 skema78.py [turun|h3turun|dalam|tekanan|gas|rekor|h1gelap|pad_h1 ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, text_sprite
from skema35 import sheet
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema74 import backdrop

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
WHITE, RED, ORANGE = (255, 255, 255), (232, 44, 40), (255, 128, 24)
N = {"turun": 60, "h3turun": 50, "dalam": 82, "tekanan": 78, "gas": 88, "rekor": 84, "h1gelap": 63}
OUT = {k: (f"clips/{k}.mp4" if k.startswith("h") else f"clips/skema_{k}.mp4") for k in N}
# from `render.py 78 plan`: turun = shot 02 ("kilometer" 0.25, "laut" 1.13, cut 1.90); h3turun = shot 03 ("Palung"
# 0.19, "Mariana" 0.47, cut 1.60); dalam = shot 04 ("padahal" 0.05, "harusnya" 0.83, "mustahil" 1.31, cut 2.67);
# tekanan = shot 05 ("Tekanan" 0.04, "airnya" 0.40, "enam" 1.00, "kali" 1.60, "lipat" 1.88, cut 2.53); gas = shot 07
# ("mengembang" 0.05, "jadi" 1.25, "tak" 1.61, "meledak" 2.13, cut 2.87); rekor = shot 10 ("dua" 0.04, "lebih" 0.84,
# "dalam" 1.08, "rekor" 1.68, "lama" 1.96, cut 2.73); h1gelap = shot 12 ("sampai" 0.04, "belum" 0.76, "ketemu" 1.16)
T = {"count0": 0.10, "count1": 1.50,
     "wall": 0.0, "mark": 0.30, "mlab": 0.45, "deep": 0.85, "ev0": 1.15, "ev1": 1.75, "evlab": 1.80,
     "x0": 0.38, "x1": 1.45, "xpill": 1.85,
     "push": 0.15, "ppill": 0.55, "burst": 2.08, "cross": 2.30,
     "barA": 0.0, "barB": 0.25, "brk": 1.00, "labB": 0.95}

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def clip_frames(path, n, ss=0.0):
    """n frames of a Pixabay clip, cover-cropped to 1080x1920, as float arrays"""
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", path, "-vf",
                                   f"scale=-2:{H}:flags=lanczos,crop={W}:{H},fps={FPS}", "-frames:v", str(n),
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    a = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(np.float32)
    return [a[min(i, len(a) - 1)] for i in range(n)]


def vignette(r0, soft):
    d = np.sqrt(((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2)
    return np.clip(1 - (d - r0) / soft, 0, 1)[..., None]


# ---------- turun ----------
def skema_turun(times=None):
    src = clip_frames("clips/26830.mp4", N["turun"], ss=1.0)
    vig = vignette(0.55, 0.8)
    frames = []
    for i in range(N["turun"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        u = ease(t / 1.75)
        k = 1.0 - 0.66 * u                              # sinking: the light dies away (YAVG ~35 at the end)
        a = src[i] * k * ((1 - u) + u * vig)            # and the dark closes in from the edges
        a = a * np.array([0.85 + 0.15 * (1 - u), 0.95, 1.0], np.float32)
        im = to_img(a).convert("RGBA")
        m = round(6148 * ease((t - 0.05) / 1.5) / 4) * 4 if t < 1.55 else 6148
        txt = f"kedalaman: {m:,} m".replace(",", ".")
        p = pill(txt, 44, col=WHITE, bg=(6, 20, 40, 220), edge=(120, 200, 255, 200))
        put1(im, p, 540, 1100, scale=min(pop(t, 0.0, 0.25), 1.04))
        # a small arrow under the pill, pointing down
        lay = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(lay)
        ay = 1150 + 8 * math.sin(t * 9)
        d.polygon([(520 * S, ay * S), (560 * S, ay * S), (540 * S, (ay + 26) * S)], fill=(120, 200, 255, 220))
        im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        frames.append(im.convert("RGB"))
    return frames


# ---------- h3turun ----------
def h3turun(times=None):
    im = Image.open("img/H3.jpg").convert("RGB")
    z = 1.45
    big = im.resize((round(W * z), round(W * z * im.height / im.width)), Image.LANCZOS)
    x0 = (big.width - W) // 2
    frames = []
    for i in range(N["h3turun"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        u = ease((t + 0.05) / 1.55)
        y0 = round((big.height - H) * u)
        frames.append(big.crop((x0, y0, x0 + W, y0 + H)))
    return frames


# ---------- dalam ----------
SURF, BOT, KM = 560, 1190, (1190 - 560) / 10.935
# the trench sits left of centre, so the eruption marker on the west wall stays clear of the watermark (x ~395-685)
PROFILE = [(0, SURF + 3.3 * KM), (120, SURF + 3.6 * KM), (210, SURF + 4.0 * KM), (310, SURF + 5.6 * KM),
           (380, SURF + 6.6 * KM), (470, SURF + 8.6 * KM), (540, SURF + 10.2 * KM), (600, BOT), (670, SURF + 10.4 * KM),
           (730, SURF + 8.4 * KM), (790, SURF + 6.0 * KM), (870, SURF + 4.4 * KM), (980, SURF + 3.6 * KM),
           (1080, SURF + 3.4 * KM)]


def wall_x(y):  # x on the western (left) wall at height y
    for (x0, y0), (x1, y1) in zip(PROFILE, PROFILE[1:]):
        if y0 <= y <= y1:
            return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
    return None


def dalam_bg():
    v = np.clip((YY - SURF) / (BOT - SURF), 0, 1)[..., None]
    sea = np.array([22, 78, 128], np.float32) * (1 - v) + np.array([2, 8, 22], np.float32) * v
    sky = np.array([10, 18, 32], np.float32)
    a = np.where((YY < SURF)[..., None], sky, sea)
    im = to_img(a).convert("RGBA")
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    pts = [(x * S, y * S) for x, y in PROFILE]
    d.polygon(pts + [(W * S, H * S), (0, H * S)], fill=(58, 50, 46, 255))
    d.line(pts, fill=(150, 132, 118, 255), width=5 * S, joint="curve")
    d.line([(0, SURF * S), (W * S, SURF * S)], fill=(150, 210, 255, 230), width=4 * S)
    im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    return im


EVX = 600                                  # Everest stands on the deepest point


def everest_sprite(h):
    """a mountain silhouette h px tall, white outline, translucent fill"""
    w = h * 0.66
    pts = [(0, h), (0.18 * w, 0.62 * h), (0.27 * w, 0.68 * h), (0.42 * w, 0.22 * h), (0.5 * w, 0), (0.56 * w, 0.12 * h),
           (0.63 * w, 0.08 * h), (0.78 * w, 0.5 * h), (0.86 * w, 0.46 * h), (w, h)]
    sp = Image.new("RGBA", (round((w + 20) * S), round((h + 20) * S)))
    d = ImageDraw.Draw(sp)
    P = [((x + 10) * S, (y + 10) * S) for x, y in pts]
    d.polygon(P, fill=(235, 240, 248, 70))
    d.line(P, fill=(255, 255, 255, 235), width=4 * S, joint="curve")
    return sp


def skema_dalam(times=None):
    bg = dalam_bg()
    my = SURF + 6.148 * KM
    mx = wall_x(my)
    glow = Image.new("RGBA", (160, 160))
    ImageDraw.Draw(glow).ellipse([50, 50, 110, 110], fill=ORANGE + (255,))
    glow = glow.filter(ImageFilter.GaussianBlur(16))
    ml = pill("±6 km: jejak letusan", 34, col=(30, 14, 0), bg=(255, 150, 40, 245), edge=(255, 255, 255, 220))
    zero = text_sprite([("0 m", 28, (190, 225, 255), False)])
    deep = text_sprite([("Challenger Deep ±10.935 m", 28, (220, 230, 240), True)])
    evh = 8.849 * KM
    ev = everest_sprite(evh)
    evl = text_sprite([("Everest 8.849 m", 30, WHITE, True), ("puncaknya masih", 24, (210, 225, 240), False),
                       ("di bawah air", 24, (210, 225, 240), False)])
    frames = []
    for i in range(N["dalam"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        put1(im, zero, 70, SURF + 26)
        # Everest rises from the trench floor, to scale, its peak ~2 km under the surface
        u = ease((t - T["ev0"]) / (T["ev1"] - T["ev0"]))
        if u > 0:
            sh = max(1, round(ev.height * u))
            part = ev.crop((0, 0, ev.width, sh))
            part = part.resize((ev.width // S, max(1, sh // S)), Image.LANCZOS)
            lay = Image.new("RGBA", (W, H))
            lay.alpha_composite(part, (round(EVX - ev.width / S / 2), round(BOT + 10 - part.height)))
            lay.putalpha(lay.getchannel("A").point(lambda q: int(q * min(1, u * 3))))
            im.alpha_composite(lay)
            put1(im, evl, 880, BOT - evh + 30, a=ramp(t, T["evlab"], T["evlab"] + 0.15))
        # the eruption marker on the wall
        a = ramp(t, T["mark"], T["mark"] + 0.12)
        if a > 0:
            pulse = 1.0 + 0.18 * math.sin((t - T["mark"]) * 10)
            g = glow.resize((round(160 * pulse), round(160 * pulse)), Image.LANCZOS)
            g.putalpha(g.getchannel("A").point(lambda q: int(q * a)))
            im.alpha_composite(g, (round(mx - g.width / 2), round(my - g.height / 2)))
            ImageDraw.Draw(im).ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=(255, 236, 200, int(255 * a)))
            lay = Image.new("RGBA", (W, H))
            ImageDraw.Draw(lay).line([(mx - 10, my - 12), (280, 850)], fill=(255, 190, 120, int(220 * a)), width=3)
            im.alpha_composite(lay)
        put1(im, ml, 230, 825, scale=min(pop(t, T["mlab"], 0.3), 1.04))
        put1(im, deep, 235, BOT - 45, a=ramp(t, T["deep"], T["deep"] + 0.15))
        frames.append(im.convert("RGB"))
    return frames


# ---------- tekanan ----------
def skema_tekanan(times=None):
    src = clip_frames("clips/31611.mp4", N["tekanan"], ss=2.0)
    tint = np.array([0.45, 0.75, 1.0], np.float32)
    glow = np.exp(-((XX - 540) ** 2 + (YY - 790) ** 2) / (2 * 380 ** 2))[..., None] * np.array([10, 34, 70], np.float32)
    pp = pill("dibanding tekanan di permukaan", 36, col=WHITE, bg=(6, 20, 40, 220), edge=(120, 200, 255, 200))
    f = ImageFont.truetype(XB, 250 * S)
    frames = []
    for i in range(N["tekanan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = to_img(src[i] * tint * 0.8 + glow + 6).convert("RGBA")
        u = ease((t - T["count0"]) / (T["count1"] - T["count0"]))
        v = 1 + round(599 * u ** 1.4)
        s = 1.0 + 0.12 * math.exp(-max(0.0, t - T["count1"]) * 7) * (t >= T["count1"])
        txt = f"{v}×"
        sp = Image.new("RGBA", (1000 * S, 330 * S))
        d = ImageDraw.Draw(sp)
        d.text((500 * S + 4 * S, 165 * S + 6 * S), txt, font=f, fill=(0, 0, 0, 170), anchor="mm")
        d.text((500 * S, 165 * S), txt, font=f, fill=YELLOW + (255,), anchor="mm")
        sp = sp.filter(ImageFilter.GaussianBlur(0.6))
        put1(im, sp, 540, 770, scale=s * min(pop(t, 0.0, 0.25), 1.04))
        put1(im, pp, 540, 1085, scale=min(pop(t, T["ppill"] + 1.2, 0.3), 1.04))
        frames.append(im.convert("RGB"))
    return frames


# ---------- gas ----------
def magma_bg():
    rng = np.random.default_rng(5)
    nz = np.zeros((H // 8 + 1, W // 8 + 1), np.float32)
    for sc_, amp in [(1, 0.5), (3, 0.3), (9, 0.2)]:
        g = rng.random((H // (8 * sc_) + 2, W // (8 * sc_) + 2)).astype(np.float32)
        g = np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((W // 8 + 1, H // 8 + 1), Image.BICUBIC), np.float32) / 255
        nz += amp * g
    nz = np.array(Image.fromarray((np.clip(nz, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
                  .filter(ImageFilter.GaussianBlur(9)), np.float32)[..., None] / 255
    r = np.exp(-((XX - 540) ** 2 + (YY - 800) ** 2) / (2 * 420 ** 2))[..., None]
    a = np.array([40, 8, 2], np.float32) + r * np.array([190, 70, 10], np.float32) * (0.55 + 0.6 * nz)
    a += (nz > 0.62) * np.array([60, 30, 0], np.float32) * r
    return to_img(a).convert("RGBA")


def arrow_sprite(L=110, col=(150, 215, 255, 240)):
    sp = Image.new("RGBA", ((L + 20) * S, 70 * S))
    d = ImageDraw.Draw(sp)
    d.rectangle([10 * S, 26 * S, (L - 30) * S, 44 * S], fill=col)
    d.polygon([((L - 40) * S, 8 * S), ((L + 10) * S, 35 * S), ((L - 40) * S, 62 * S)], fill=col)
    return sp


def burst_sprite(r=135):
    sp = Image.new("RGBA", ((2 * r + 20) * S, (2 * r + 20) * S))
    d = ImageDraw.Draw(sp)
    c = (r + 10) * S
    pts = []
    for k in range(24):
        a = math.pi * 2 * k / 24
        rr = r if k % 2 == 0 else r * 0.55
        pts.append((c + rr * S * math.cos(a), c + rr * S * math.sin(a)))
    d.polygon(pts, fill=(255, 200, 40, 255), outline=(255, 255, 255, 255), width=4 * S)
    d.text((c, c), "DUAR!", font=ImageFont.truetype(XB, 52 * S), fill=(120, 20, 0, 255), anchor="mm")
    return sp


def skema_gas(times=None):
    bg = magma_bg()
    arr = arrow_sprite()
    pl = pill("tekanan air ±600×", 36, col=WHITE, bg=(6, 20, 40, 225), edge=(150, 215, 255, 220))
    gl = text_sprite([("gas", 44, (255, 255, 255), True)])
    mg = text_sprite([("magma", 34, (255, 220, 180), True)])
    bu = burst_sprite()
    cx, cy = 540, 800
    frames = []
    for i in range(N["gas"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        # the bubble tries to grow and is pushed back (two tries), then holds small
        tryk = max(0.0, math.sin(min(t, 1.9) / 1.9 * 2 * math.pi * 1.5 - 0.3)) if t < 1.9 else 0.0
        r = 78 + 40 * tryk
        lay = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(lay)
        d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=(255, 235, 210, 90), outline=(255, 255, 255, 235), width=5 * S)
        d.ellipse([(cx - r * 0.55) * S, (cy - r * 0.62) * S, (cx - r * 0.15) * S, (cy - r * 0.3) * S], fill=(255, 255, 255, 150))
        im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        put1(im, gl, cx, cy + 4)
        put1(im, mg, 860, 1150, a=0.9)
        # the arrows of water pressure, pressing harder when the bubble swells
        a = ramp(t, T["push"], T["push"] + 0.2)
        for k in range(8):
            ang = math.pi * 2 * k / 8 + math.pi / 8
            dist = r + 40 + 120 - 30 * tryk
            ax, ay = cx + math.cos(ang) * dist, cy + math.sin(ang) * dist
            sp = arr.rotate(math.degrees(-ang) + 180, resample=Image.BICUBIC, expand=True)
            put1(im, sp, ax, ay, a=a)
        put1(im, pl, 540, 1110, scale=min(pop(t, T["ppill"], 0.3), 1.04))
        # "meledak": a burst pops over the bubble and is struck out
        b = pop(t, T["burst"], 0.25)
        if b > 0:
            put1(im, bu, cx, cy, scale=min(b, 1.06) * 0.95)
            v = ease((t - T["cross"]) / 0.2)
            if v > 0:
                lay = Image.new("RGBA", (W * S, H * S))
                d = ImageDraw.Draw(lay)
                R = 150
                d.line([((cx - R) * S, (cy - R) * S), ((cx - R + 2 * R * v) * S, (cy - R + 2 * R * v) * S)], fill=RED + (255,), width=26 * S)
                w2 = ease((t - T["cross"] - 0.12) / 0.2)
                if w2 > 0:
                    d.line([((cx + R) * S, (cy - R) * S), ((cx + R - 2 * R * w2) * S, (cy - R + 2 * R * w2) * S)], fill=RED + (255,), width=26 * S)
                im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        frames.append(im.convert("RGB"))
    return frames


# ---------- rekor ----------
RS, RK = 660, (1180 - 660) / 6.1          # surface y and px per km
BA, BB = (230, 370), (570, 710)            # bar x spans: rekor lama, temuan baru


def skema_rekor(times=None):
    v = np.clip((YY - RS) / (1200 - RS), 0, 1)[..., None]
    a = np.array([18, 64, 110], np.float32) * (1 - v) + np.array([3, 10, 26], np.float32) * v
    a = np.where((YY < RS)[..., None], np.array([10, 18, 32], np.float32), a)
    bg = to_img(a).convert("RGBA")
    d0 = ImageDraw.Draw(bg)
    d0.line([(0, RS), (W, RS)], fill=(150, 210, 255, 230), width=4)
    zero = text_sprite([("permukaan laut", 28, (190, 225, 255), False)])
    la = text_sprite([("rekor lama", 36, WHITE, True), ("±4.000 m · Arktik, 2008", 28, (215, 225, 235), False)])
    lb = text_sprite([("+2 km", 54, YELLOW, True), ("temuan baru", 34, WHITE, True), ("±6.100 m", 30, (230, 235, 240), False)])
    yA, yB = RS + 4.0 * RK, RS + 6.1 * RK
    frames = []
    for i in range(N["rekor"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        put1(im, zero, 900, RS + 28)
        lay = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(lay)
        ua = ease((t - T["barA"]) / 0.45)
        ub = ease((t - T["barB"]) / 0.7)
        if ua > 0:
            d.rounded_rectangle([BA[0] * S, RS * S, BA[1] * S, (RS + (yA - RS) * ua) * S], radius=14 * S, fill=(205, 214, 226, 255))
        if ub > 0:
            d.rounded_rectangle([BB[0] * S, RS * S, BB[1] * S, (RS + (yB - RS) * ub) * S], radius=14 * S, fill=YELLOW + (255,))
        # dashed line at the old record's depth, and the bracket for the extra 2 km
        k = ramp(t, T["brk"], T["brk"] + 0.15)
        if k > 0:
            x = BA[1] + 10
            while x < BB[1] + 40:
                d.line([(x * S, yA * S), (min(x + 18, BB[1] + 40) * S, yA * S)], fill=(255, 255, 255, int(230 * k)), width=4 * S)
                x += 30
            bx = BB[1] + 34
            d.line([(bx * S, yA * S), (bx * S, yB * S)], fill=YELLOW + (int(255 * k),), width=5 * S)
            for yy in (yA, yB):
                d.line([((bx - 14) * S, yy * S), (bx * S, yy * S)], fill=YELLOW + (int(255 * k),), width=5 * S)
        im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        put1(im, la, (BA[0] + BA[1]) / 2 + 20, yA + 62, a=ramp(t, 0.35, 0.5))
        put1(im, lb, 890, (yA + yB) / 2 + 10, scale=min(pop(t, T["labB"], 0.3), 1.04))
        frames.append(im.convert("RGB"))
    return frames


# ---------- h1gelap ----------
def h1gelap(times=None):
    im = Image.open("img/H1.jpg").convert("RGB")
    a0 = np.asarray(im, np.float32)
    frames = []
    cw = 0.64 * im.width                       # crop window width in source pixels at the start
    for i in range(N["h1gelap"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        u = ease(t / 2.0)
        w_ = cw / (1 + 0.08 * u)
        h_ = w_ * H / W
        cx, cy = 0.34 * im.width, im.height - h_ / 2 - 20
        box = (cx - w_ / 2, cy - h_ / 2, cx + w_ / 2, cy + h_ / 2)
        f = im.transform((W, H), Image.EXTENT, box, Image.BICUBIC)
        a = np.asarray(f, np.float32)
        light = 1.0 - 0.62 * u
        vig = vignette(0.75 - 0.35 * u, 0.55)
        a = a * light * (0.25 + 0.75 * vig)
        frames.append(to_img(a))
    return frames


# ---------- pad_h1 ----------
def pad_h1(times=None):
    im = np.asarray(Image.open("img/H1.jpg").convert("RGB"), np.float32)
    h, w, _ = im.shape
    pad, f = int(h * 0.25), 260
    col = np.median(im[:30], axis=0)
    col = np.asarray(Image.fromarray(np.clip(col[None].repeat(8, 0), 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40)), np.float32)[4]
    fill = col[None] * (0.7 + 0.3 * np.linspace(0, 1, pad)[:, None, None])
    out = np.concatenate([fill, im], 0)
    a = np.linspace(0, 1, f)[:, None, None]
    a = a * a * (3 - 2 * a)
    out[pad:pad + f] = out[pad:pad + f] * a + col[None] * (1 - a)
    to_img(out).save("img/H1t.jpg", quality=93)
    print("img/H1t.jpg")
    return None


FUN = {"turun": skema_turun, "h3turun": h3turun, "dalam": skema_dalam, "tekanan": skema_tekanan, "gas": skema_gas,
       "rekor": skema_rekor, "h1gelap": h1gelap, "pad_h1": pad_h1}

if __name__ == "__main__":
    args = sys.argv[1:]
    out, TIMES = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, TIMES = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    os.makedirs("clips", exist_ok=True)
    for name in args or list(N) + ["pad_h1"]:
        fr = FUN[name](TIMES)
        if fr is None:
            continue
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
