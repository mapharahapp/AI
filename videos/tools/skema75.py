"""Schematic animations for Titik Heran #75 (run in the episode work dir; writes clips/skema_jawa.mp4, skema_oak.mp4,
skema_kamus.mp4, skema_minecraft.mp4). No logos anywhere (Java, Android, Minecraft, Sun, Oracle, Peet's) and nothing
that imitates Minecraft's look (no blocks or cubes).
jawa: "JAVA = JAWA" in one line, the V and the W light up yellow, small labels "bahasa Inggris" / "bahasa Indonesia",
  pill "nama Pulau Jawa dalam bahasa Inggris".
oak: Pixabay photo 2018822 (Angel Oak, an oak tree) with a slow push; on "Ouk" a white name card "OAK" pops up, on
  "ditolak" a red stamp DITOLAK slams onto it, on "dipakai" pill "sudah jadi merek Oak Technologies" (InfoWorld/JavaWorld,
  "So why did they decide to call it Java?"). The first OAK_OFF seconds have no card and run as the photo.
kamus: dictionary-style card, no logo: kamus Merriam-Webster, java, "= KOPI", from the name of Java, Indonesia.
minecraft: text card: MINECRAFT, game terlaris sepanjang masa, versi aslinya dibuat dengan bahasa JAVA (Java Edition).
Event times are seconds from the start of each clip, read off `render.py 75 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < ~640) and the captions (y >= 1210).
usage: python3 skema75.py [jawa|oak|kamus|minecraft ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, text_sprite
from skema35 import sheet
from skema37 import put1
from skema46 import pill, ease, wanted
from skema74 import backdrop, push

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
WHITE, RED = (255, 255, 255), (222, 36, 32)
OAK_OFF = 31 / FPS            # frames of shot 06 ("nama" -> "ouk") in `render.py 75 plan`
N = {"jawa": 42, "oak": 162, "kamus": 52, "minecraft": 108}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 75 plan`: jawa "Namanya" 0.06, "Java" 0.59, cut 1.27; oak = shot 06 (1.03 s) + shot 07 ("Ouk" 0.05,
# "ditolak" 1.25, "pengacara" 1.64, "dipakai" 2.90, cut 4.20); kamus "Amerika" 0.05, "untuk" 0.69, "kopi" 0.93,
# cut 1.63; minecraft "game" 0.04, "terlaris" 0.24, "masa" 1.11, "lahir" 1.83, "bahasa" 2.39, cut 3.47
T = {"java": 0.04, "jawa": 0.45, "vw": 0.55, "labels": 0.62, "jpill": 0.72,
     "card": OAK_OFF + 0.02, "stamp": OAK_OFF + 1.22, "opill": OAK_OFF + 2.85,
     "k1": 0.15, "k2": 0.25, "k3": 0.45, "k4": 0.72, "k5": 1.00,
     "m1": 0.10, "m2": 0.30, "m3": 1.80, "m4": 2.30}


# ---------- jawa ----------
def word_sprite(word, hi, size=112):
    """one word in white with the letter at index hi in yellow, 2x sprite with a soft shadow"""
    f = ImageFont.truetype(XB, size * S)
    x0, y0, x1, y1 = f.getbbox(word)
    m = 30 * S
    w, h = x1 - x0 + 2 * m, y1 - y0 + 2 * m
    sh, tx = Image.new("RGBA", (w, h)), Image.new("RGBA", (w, h))
    ds, dt = ImageDraw.Draw(sh), ImageDraw.Draw(tx)
    x = m - x0
    for k, ch in enumerate(word):
        col = YELLOW if k == hi else WHITE
        ds.text((x + 3 * S, m - y0 + 5 * S), ch, font=f, fill=(0, 0, 0, 200))
        dt.text((x, m - y0), ch, font=f, fill=col + (255,))
        x += f.getlength(ch)
    sh = sh.filter(ImageFilter.GaussianBlur(6 * S))
    sh.alpha_composite(tx)
    return sh


def skema_jawa(times=None):
    bg = backdrop((14, 44, 34), (4, 12, 9), glow=(14, 40, 26), gy=880)
    plain_java, plain_jawa = word_sprite("JAVA", -1), word_sprite("JAWA", -1)
    hi_java, hi_jawa = word_sprite("JAVA", 2), word_sprite("JAWA", 2)
    eq = text_sprite([("=", 96, WHITE, True)])
    lj = text_sprite([("bahasa Inggris", 32, (200, 220, 210), False)])
    li = text_sprite([("bahasa Indonesia", 32, (200, 220, 210), False)])
    jp = pill("nama Pulau Jawa dalam bahasa Inggris", 34, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 220))
    frames = []
    for i in range(N["jawa"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        hv = ramp(t, T["vw"], T["vw"] + 0.12)
        sj = min(pop(t, T["java"], 0.25), 1.05)
        put1(im, plain_java, 270, 800, scale=sj)
        put1(im, hi_java, 270, 800, a=hv, scale=sj)
        put1(im, eq, 540, 796, a=ramp(t, T["jawa"] - 0.05, T["jawa"] + 0.1))
        sw = min(pop(t, T["jawa"], 0.25), 1.05)
        put1(im, plain_jawa, 812, 800, scale=sw)
        put1(im, hi_jawa, 812, 800, a=hv, scale=sw)
        put1(im, lj, 270, 900, a=ramp(t, T["labels"], T["labels"] + 0.12))
        put1(im, li, 812, 900, a=ramp(t, T["labels"], T["labels"] + 0.12))
        put1(im, jp, 540, 1080, scale=min(pop(t, T["jpill"], 0.25), 1.05))
        frames.append(im.convert("RGB"))
    return frames


# ---------- oak ----------
def oak_bg():
    im = Image.open("img/2018822.jpg").convert("RGB")
    cw = im.height * 9 / 16
    x0 = 512 - cw / 2                                      # the trunk sits at x ~512 of 1280
    return im.crop((x0, 0, x0 + cw, im.height)).resize((W, H), Image.LANCZOS).convert("RGBA")


def name_card(grey=False):
    cw, ch = 560, 250
    c = Image.new("RGBA", (cw * S, ch * S))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([0, 0, cw * S - 1, ch * S - 1], radius=26 * S, fill=(250, 248, 242, 255))
    d.rectangle([0, 0, cw * S, 58 * S], fill=(30, 70, 50, 255))
    d.rounded_rectangle([0, 0, cw * S - 1, 70 * S], radius=26 * S, fill=(30, 70, 50, 255))
    d.rectangle([0, 44 * S, cw * S, 70 * S], fill=(250, 248, 242, 255))
    f1, f2 = ImageFont.truetype(MED, 30 * S), ImageFont.truetype(XB, 130 * S)
    d.text((cw * S / 2, 24 * S), "nama awal bahasa ini", font=f1, fill=(255, 255, 255, 255), anchor="mm")
    d.text((cw * S / 2, 160 * S), "OAK", font=f2, fill=(150, 150, 150, 255) if grey else (24, 24, 24, 255), anchor="mm")
    sh = Image.new("RGBA", ((cw + 60) * S, (ch + 60) * S))
    ImageDraw.Draw(sh).rounded_rectangle([34 * S, 40 * S, (cw + 34) * S, (ch + 40) * S], radius=26 * S, fill=(0, 0, 0, 140))
    sh = sh.filter(ImageFilter.GaussianBlur(12 * S))
    sh.alpha_composite(c, (30 * S, 30 * S))
    return sh


def stamp():
    f = ImageFont.truetype(XB, 104 * S)
    x0, y0, x1, y1 = f.getbbox("DITOLAK")
    pad = 28 * S
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    st = Image.new("RGBA", (w + 40 * S, h + 40 * S))
    d = ImageDraw.Draw(st)
    d.rounded_rectangle([20 * S, 20 * S, 20 * S + w, 20 * S + h], radius=18 * S, outline=RED + (255,), width=10 * S)
    d.text((20 * S + pad - x0, 20 * S + pad - y0), "DITOLAK", font=f, fill=RED + (255,))
    rng = np.random.default_rng(4)                         # worn ink: knock small holes out of the stamp
    a = np.asarray(st.getchannel("A"), np.float32)
    holes = rng.random(a.shape) < 0.025
    holes = np.asarray(Image.fromarray((holes * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) > 0
    a = np.where(holes, a * 0.55, a)
    st.putalpha(Image.fromarray(a.astype(np.uint8)))
    return st.rotate(-11, expand=True, resample=Image.BICUBIC)


def skema_oak(times=None):
    bg = oak_bg()
    card, card_g, stp = name_card(), name_card(True), stamp()
    op = pill("sudah jadi merek Oak Technologies", 34, col=WHITE, bg=(150, 22, 20, 235), edge=(255, 255, 255, 170))
    C = (540, 820)
    frames = []
    dur = N["oak"] / FPS
    for i in range(N["oak"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        z = 1.0 + 0.09 * t / dur
        im = push(bg, z, C)
        if t >= T["card"]:
            dim = Image.new("RGBA", (W, H), (0, 0, 0, int(90 * ramp(t, T["card"], T["card"] + 0.2))))
            im.alpha_composite(dim)
        sc = min(pop(t, T["card"], 0.3), 1.05)
        dt = t - T["stamp"]
        shake = 9 * math.exp(-dt * 14) * math.sin(dt * 70) if 0.12 < dt < 0.6 else 0.0
        put1(im, card, 540 + shake, 810, scale=sc)
        if dt > 0.1:
            put1(im, card_g, 540 + shake, 810, a=ramp(dt, 0.1, 0.25), scale=sc)
        if dt > 0:
            k = min(dt / 0.12, 1.0)
            s_ = 2.2 - 1.2 * k * k
            put1(im, stp, 545 + shake, 845, a=min(1.0, 0.4 + k), scale=s_)
        put1(im, op, 540, 1090, scale=min(pop(t, T["opill"], 0.3), 1.05))
        frames.append(im.convert("RGB"))
    return frames


# ---------- cards ----------
def card_frames(n, lines, hl_box, hl_key, bg, head=(150, 36, 24), cw=860, ch=520, cy0=668):
    """a white card that slides up; lines = (text, font, size, colour, y, key, x) appear on T[key]"""
    card = Image.new("RGBA", (cw * S, ch * S))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, cw * S - 1, ch * S - 1], radius=22 * S, fill=(250, 248, 242, 255))
    d.rectangle([0, 0, cw * S, 14 * S], fill=head + (255,))
    sprites = []
    for text, font, size, col, y, key, x in lines:
        lay = Image.new("RGBA", (cw * S, ch * S))
        ImageDraw.Draw(lay).text((x * S, y * S), text, font=ImageFont.truetype(font, size * S), fill=col + (255,))
        sprites.append((lay, key))
    hl = Image.new("RGBA", (cw * S, ch * S))
    ImageDraw.Draw(hl).rounded_rectangle([v * S for v in hl_box], radius=14 * S, fill=YELLOW + (255,))
    cx0 = (W - cw) // 2
    frames = []
    for i in range(n):
        t = i / FPS
        if not wanted(i, None if TIMES is None else TIMES):
            frames.append(None)
            continue
        c = card.copy()
        if t > T[hl_key]:
            h2 = hl.copy()
            h2.putalpha(h2.getchannel("A").point(lambda q, a=ramp(t, T[hl_key], T[hl_key] + 0.12): int(q * a)))
            c.alpha_composite(h2)
        for lay, key in sprites:
            a = ramp(t, T[key], T[key] + 0.15)
            if a > 0:
                l2 = lay.copy()
                l2.putalpha(l2.getchannel("A").point(lambda q, a=a: int(q * a)))
                c.alpha_composite(l2)
        c = c.resize((cw, ch), Image.LANCZOS)
        im = bg.copy()
        sh = Image.new("RGBA", (W, H))
        y = cy0 + 700 * (1 - ease(t / 0.3))
        ImageDraw.Draw(sh).rounded_rectangle([cx0 + 10, y + 18, cx0 + cw + 10, y + ch + 18], radius=22, fill=(0, 0, 0, 120))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
        im.alpha_composite(c, (cx0, round(y)))
        frames.append(im.convert("RGB"))
    return frames


TIMES = None


def skema_kamus(times=None):
    bg = backdrop((48, 30, 18), (12, 7, 4))
    lines = [("kamus Merriam-Webster", XB, 40, (150, 36, 24), 50, "k1", 54),
             ("java", XB, 110, (20, 20, 20), 96, "k2", 54),
             ("kata benda · bahasa sehari-hari Amerika", MED, 32, (90, 90, 90), 250, "k3", 54),
             ("= KOPI", XB, 60, (20, 20, 20), 326, "k4", 66),
             ("dari nama Pulau Jawa (Java), Indonesia", MED, 34, (40, 40, 40), 438, "k5", 54)]
    return card_frames(N["kamus"], lines, (38, 312, 300, 408), "k4", bg)


def skema_minecraft(times=None):
    bg = backdrop((20, 26, 36), (6, 8, 12))
    lines = [("MINECRAFT", XB, 92, (20, 20, 20), 56, "m1", 54),
             ("game terlaris sepanjang masa", MED, 40, (60, 60, 60), 190, "m2", 54),
             ("versi aslinya dibuat dengan", MED, 36, (60, 60, 60), 300, "m3", 54),
             ("bahasa JAVA", XB, 62, (20, 20, 20), 368, "m4", 66)]
    return card_frames(N["minecraft"], lines, (38, 356, 470, 450), "m4", bg, head=(40, 110, 60))


FUN = {"jawa": skema_jawa, "oak": skema_oak, "kamus": skema_kamus, "minecraft": skema_minecraft}

if __name__ == "__main__":
    args = sys.argv[1:]
    out = None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, TIMES = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    os.makedirs("clips", exist_ok=True)
    for name in args or list(N):
        fr = FUN[name](TIMES)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
