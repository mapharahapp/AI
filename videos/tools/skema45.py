"""Hook tilt, cards and typography clips for Titik Heran #45 (run in the episode work dir after
`dl.py i:1037212 i:10225493 i:19176 i:6817925 i:4013049 i:1619740 i:3180636 i:4365774 v:157861 v:306357`; writes
clips/pohon45.mp4, clips/tajuk45.mp4, clips/majalah45.mp4, clips/dongeng45.mp4, clips/kapal45.mp4 and clips/anchar45.mp4).
Pixabay has no photo of a real upas tree, its sap or the K-162: the tree, pages and submarine are labelled stand-ins
("ilustrasi"), and the cards are typography only (no facsimile of The London Magazine).
usage: python3 skema45.py [pohon|tajuk|majalah|dongeng|kapal|anchar ...] [--sheet out.jpg t1,t2,...]
pohon: the buttress-root tree 1037212 tilting up from the roots to the trunk while pushing in, darker at the top for the title.
tajuk: canopy clip 306357 turning slowly (ffmpeg rotate on a 1,2x scale, so the corners stay filled).
majalah: old pages 10225493 (2,25x, softened, sepia) behind a paper card "THE LONDON MAGAZINE · DESEMBER 1783 · kisah pohon
  racun dari Jawa"; on "dikirim" the legend's claim "katanya: tak ada yang hidup dalam radius puluhan km" fades in.
dongeng: the same pages and card drained to black and white; on "dongeng" a red stamp "DONGENG!" slams onto the card.
kapal: the Soviet submarine U-461 3180636 ("ilustrasi: kapal selam Soviet lain") across the frame over its own blurred,
  navy-tinted copy, pushing in faster from "kapal" with speed lines streaming past (the 0 -> 82,8 km/jam counter is a title).
anchar: a navy sonar card: rings ping from the middle while the Russian word "АНЧАР" flips letter by letter into "ANCAR";
  "bahasa Rusia" under it gives way on "nama" to "nama Jawa pohon upas", a pill "PROYEK 661 · K-162" above.
Event times are seconds from the start of each clip, read off `render.py 45 plan`: majalah starts at 7,50 ("dikirim" 0,72,
"getahnya" 1,55), dongeng at 12,03 ("dongeng" 0,79), kapal at 20,33 ("kapal" 1,47, "tercepat" 2,04), anchar at 23,87
("Ancar" 0,05, "nama" 0,93).
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, encode
from skema27 import stamp_sprite
from skema35 import blur, sheet, sepia
from skema37 import noise, to_img, put1
from skema39 import cover, lum, sat, title_shade

N = {"pohon": 99, "tajuk": 75, "majalah": 93, "dongeng": 68, "kapal": 117, "anchar": 81}  # each clip runs ~0,3 s past its shot
OUT = {k: f"clips/{k}45.mp4" for k in N}
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def wanted(i, times):
    return times is None or any(abs(i / FPS - x) < 0.5 / FPS for x in times)


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def view(img, z, dx=0.0, dy=0.0):
    """an RGB image zoomed by z about its centre and shifted by (dx, dy) frame pixels, sub-pixel smooth"""
    w, h = W / z, H / z
    x0, y0 = (W - w) / 2 - dx / z, (H - h) / 2 - dy / z
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


def pill(text, size=34, col=WHITE, bg=(8, 18, 36, 200), edge=(120, 230, 255, 160), pad=(22, 12)):
    """a rounded label, 2x sprite"""
    f = ImageFont.truetype(XB, size * S)
    x0, y0, x1, y1 = f.getbbox(text)
    w, h = x1 - x0 + 2 * pad[0] * S, y1 - y0 + 2 * pad[1] * S
    sp = Image.new("RGBA", (w + 20 * S, h + 20 * S))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([10 * S, 10 * S, 10 * S + w, 10 * S + h], radius=h // 2, fill=bg, outline=edge, width=3 * S)
    d.text((10 * S + pad[0] * S - x0, 10 * S + pad[1] * S - y0), text, font=f, fill=col + (255,))
    return sp


def shadow_text(text, font, col, blur_r=6, alpha=200):
    """a line of text with a soft dark shadow, 2x sprite"""
    x0, y0, x1, y1 = font.getbbox(text)
    m = 30 * S
    sp = Image.new("RGBA", (x1 - x0 + 2 * m, y1 - y0 + 2 * m))
    sh = Image.new("RGBA", sp.size)
    ImageDraw.Draw(sh).text((m - x0 + 2 * S, m - y0 + 3 * S), text, font=font, fill=(0, 0, 0, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur_r * S))
    ImageDraw.Draw(sh).text((m - x0, m - y0), text, font=font, fill=col + (255,))
    return sh


# ---------- pohon (hook) ----------
def skema_pohon(times=None):
    im = Image.open("img/1037212.jpg").convert("RGB")  # 879x1280, the trunk at x ~452
    frames = []
    n = N["pohon"]
    for i in range(n):
        if not wanted(i, times):
            frames.append(None)
            continue
        u = ease(i / (n - 1))
        s = 1.60 + 0.14 * u
        ww, hh = W / s, H / s
        cy = (im.height - hh / 2) * (1 - u) + 560 * u  # from the roots up the trunk
        cy = min(max(cy, hh / 2), im.height - hh / 2)
        cx = 452
        f = im.resize((W, H), Image.LANCZOS, box=(cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2))
        frames.append(to_img(title_shade(np.asarray(f, np.float32), 0.5, 820)))
    return frames


# ---------- tajuk ----------
def tajuk():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "6", "-i", "clips/306357.mp4", "-t", f"{N['tajuk'] / FPS:.3f}", "-vf",
                    "scale=1296:2304:flags=lanczos,rotate=a='0.035*t':ow=1080:oh=1920:bilinear=1,fps=30,setsar=1",
                    "-an", "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", OUT["tajuk"]], check=True)
    print(OUT["tajuk"])


# ---------- the old pages and the magazine card ----------
CARD_X, CARD_Y, CARD_ANG = 540, 610, -2.5


def pages():
    """the pages photo 2,25x across the frame, softened so the Spanish print does not compete with the card"""
    return blur(cover("img/10225493.jpg", 0.47), 3.6)


def card_parts():
    """the paper card (2x, unrotated) and its last two lines as a separate overlay of the same size"""
    w, h, m = 800 * S, 480 * S, 40 * S
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nz = noise((h, w), [(60 * S, 0.5), (12 * S, 0.3), (3 * S, 0.2)], 45)
    edge = np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]) / (40 * S)
    paper = np.array([236, 224, 196], np.float32) * (0.9 + 0.12 * nz[..., None])
    paper *= (0.84 + 0.16 * np.clip(edge, 0, 1) ** 0.6)[..., None]  # aged, darker edges
    card = Image.new("RGBA", (w + 2 * m, h + 2 * m))
    sh = Image.new("RGBA", card.size)
    ImageDraw.Draw(sh).rectangle([m + 6 * S, m + 10 * S, m + w + 6 * S, m + h + 10 * S], fill=(0, 0, 0, 170))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14 * S)))
    card.paste(Image.fromarray(paper.clip(0, 255).astype(np.uint8)).convert("RGBA"), (m, m))
    d = ImageDraw.Draw(card)
    ink, red = (44, 30, 20, 255), (150, 28, 22, 255)
    cx = m + w // 2
    d.text((cx, m + 82 * S), "THE LONDON MAGAZINE", font=ImageFont.truetype(SERIF_B, 62 * S), fill=ink, anchor="ms")
    d.line([(m + 48 * S, m + 108 * S), (m + w - 48 * S, m + 108 * S)], fill=ink, width=4 * S)
    d.line([(m + 48 * S, m + 118 * S), (m + w - 48 * S, m + 118 * S)], fill=ink, width=1 * S)
    d.text((cx, m + 186 * S), "DESEMBER 1783", font=ImageFont.truetype(SERIF_B, 54 * S), fill=red, anchor="ms")
    d.text((cx, m + 256 * S), "kisah pohon racun dari Jawa", font=ImageFont.truetype(SERIF_I, 44 * S), fill=ink, anchor="ms")
    d.line([(m + 250 * S, m + 300 * S), (m + w - 250 * S, m + 300 * S)], fill=(44, 30, 20, 160), width=2 * S)
    over = Image.new("RGBA", card.size)
    d = ImageDraw.Draw(over)
    f = ImageFont.truetype(SERIF_I, 40 * S)
    d.text((cx, m + 370 * S), "katanya: tak ada yang hidup", font=f, fill=(110, 24, 18, 255), anchor="ms")
    d.text((cx, m + 424 * S), "dalam radius puluhan km", font=f, fill=(110, 24, 18, 255), anchor="ms")
    return card, over


def gray_sprite(sp):
    a = np.asarray(sp, np.float32)
    y = lum(a[..., :3])[..., None]
    return Image.fromarray(np.concatenate([np.repeat(y, 3, 2), a[..., 3:]], 2).clip(0, 255).astype(np.uint8))


def place_card(im, card, over, k_over, k_in=1.0, dx=0.0, dy=0.0):
    c = card.copy()
    if k_over > 0:
        o = over.copy()
        o.putalpha(o.getchannel("A").point(lambda v: int(v * k_over)))
        c.alpha_composite(o)
    ang = CARD_ANG - 7 * (1 - k_in)
    c = c.rotate(ang, resample=Image.BICUBIC, expand=True)
    put1(im, c, CARD_X + dx, CARD_Y - 70 * (1 - k_in) + dy, a=min(1.0, 1.6 * k_in), scale=1.2 * (0.86 + 0.14 * k_in))


def skema_majalah(times=None):
    bg = Image.fromarray(sepia(pages(), 0.85).clip(0, 255).astype(np.uint8))
    card, over = card_parts()
    t_in, t_line = 0.06, 0.72  # the card drops in; "dikirim"
    frames = []
    n = N["majalah"]
    for i in range(n):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = view(bg, 1.0 + 0.05 * i / n).convert("RGBA")
        dim = Image.new("RGBA", (W, H), (0, 0, 0, 95))
        im.alpha_composite(dim)
        k = pop(t, t_in, 0.4)
        if k > 0:
            place_card(im, card, over, ramp(t, t_line, t_line + 0.35), min(k, 1.15))
        frames.append(im.convert("RGB"))
    return frames


def skema_dongeng(times=None):
    a = pages()
    g = lum(a)[..., None]
    bg = Image.fromarray(np.repeat(g * 0.82, 3, 2).clip(0, 255).astype(np.uint8))
    card, over = card_parts()
    card, over = gray_sprite(card), gray_sprite(over)
    st = stamp_sprite("DONGENG!", 118, 8)
    t_on, d_on = 0.79, 0.12  # "dongeng"
    frames = []
    n = N["dongeng"]
    for i in range(n):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        dx = dy = 0.0
        if t > t_on + d_on:  # the frame jolts as the stamp lands
            e = math.exp(-(t - t_on - d_on) / 0.07)
            dx, dy = 9 * e * math.sin(70 * (t - t_on)), 7 * e * math.cos(55 * (t - t_on))
        im = view(bg, 1.05 + 0.04 * i / n, dx, dy).convert("RGBA")
        im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 95)))
        place_card(im, card, over, 1.0, 1.0, dx, dy)
        u = min(max((t - t_on) / d_on, 0.0), 1.0)
        if u > 0:
            put1(im, st, 540 + dx, 632 + dy, a=min(1.0, 3 * u), scale=1.12 * (1.75 - 0.75 * u * u))
        frames.append(im.convert("RGB"))
    return frames


# ---------- kapal ----------
def navy(a, k=1.0):
    a = sat(a, 1 - 0.3 * k)
    return a * (1 + k * (np.array([0.86, 0.95, 1.1], np.float32) - 1)) + k * np.array([0, 3, 12], np.float32)


def skema_kapal(times=None):
    im = Image.open("img/3180636.jpg").convert("RGB")  # 1280x691, the bow on the left
    bg = navy(blur(cover("img/3180636.jpg", 0.5), 26)) * 0.42
    bg = Image.fromarray(bg.clip(0, 255).astype(np.uint8))
    fw = 1240
    fg = im.resize((fw, round(im.height * fw / im.width)), Image.LANCZOS)
    fg = Image.fromarray(navy(np.asarray(fg, np.float32), 0.9).clip(0, 255).astype(np.uint8))
    CY = 1062
    rng = np.random.default_rng(45)
    lines = [(rng.uniform(140, 1820), rng.uniform(0, 2000), rng.uniform(160, 560), rng.uniform(2.5, 6.5),
              rng.uniform(2400, 4400), rng.uniform(0.25, 0.62)) for _ in range(110)]
    t_go, t_top = 1.40, 2.04  # "kapal", "tercepat"
    frames = []
    n = N["kapal"]
    for i in range(n):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        go = ease((t - t_go) / 1.3)
        z = 1.0 + 0.03 * t / (n / FPS) + 0.13 * go
        frame = view(bg, 1.04 + 0.03 * t).convert("RGBA")
        f = fg.resize((round(fw * z), round(fg.height * z)), Image.BICUBIC)
        frame.alpha_composite(f.convert("RGBA"), (round(540 - f.width / 2 - 40 * go), round(CY - f.height / 2)))
        k = ramp(t, t_go - 0.2, t_top)
        if k > 0:
            lay = Image.new("RGBA", (W, H))
            d = ImageDraw.Draw(lay)
            for y, x0, L, th, v, al in lines:
                x = (x0 + v * (t - t_go + 0.2)) % (W + L + 200) - L - 100
                inside = abs(y - CY) < f.height / 2
                a = int(255 * al * k * (0.55 if inside else 1.0))
                d.line([(x, y), (x + L, y)], fill=(225, 240, 255, a), width=max(1, round(th)))
            frame.alpha_composite(lay.filter(ImageFilter.BoxBlur(1)))
        frames.append(frame.convert("RGB"))
    return frames


# ---------- anchar ----------
AC = (540, 700)  # the word and the sonar centre


def sonar_bg():
    r = np.sqrt((XX - AC[0]) ** 2 + (YY - AC[1]) ** 2)
    v = np.clip(r / 1100, 0, 1)[..., None]
    a = np.array([18, 48, 92], np.float32) * (1 - v) + np.array([3, 9, 22], np.float32) * v
    g = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for x in range(0, W + 1, 90):
        d.line([(x * S, 0), (x * S, H * S)], fill=(140, 220, 255, 12), width=2 * S)
    for y in range(AC[1] % 90, H + 1, 90):
        d.line([(0, y * S), (W * S, y * S)], fill=(140, 220, 255, 12), width=2 * S)
    for rr in (170, 340, 510, 680):
        d.ellipse([(AC[0] - rr) * S, (AC[1] - rr) * S, (AC[0] + rr) * S, (AC[1] + rr) * S], outline=(140, 230, 255, 34), width=2 * S)
    d.line([(AC[0] * S, (AC[1] - 700) * S), (AC[0] * S, (AC[1] + 700) * S)], fill=(140, 230, 255, 24), width=2 * S)
    d.line([((AC[0] - 700) * S, AC[1] * S), ((AC[0] + 700) * S, AC[1] * S)], fill=(140, 230, 255, 24), width=2 * S)
    g.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    return g


def letter(ch, font, col):
    """one letter with a soft glow, 2x sprite with the letter's ink box centred"""
    x0, y0, x1, y1 = font.getbbox(ch)
    m = 40 * S
    sp = Image.new("RGBA", (x1 - x0 + 2 * m, y1 - y0 + 2 * m))
    gl = Image.new("RGBA", sp.size)
    ImageDraw.Draw(gl).text((m - x0, m - y0), ch, font=font, fill=col + (200,))
    sp.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14 * S)))
    ImageDraw.Draw(sp).text((m - x0, m - y0), ch, font=font, fill=col + (255,))
    return sp


def skema_anchar(times=None):
    bg = sonar_bg()
    f = ImageFont.truetype(XB, 210 * S)
    cyr, lat = "АНЧАР", "ANCAR"
    adv = [max(f.getlength(a), f.getlength(b)) / S for a, b in zip(cyr, lat)]
    gap = 10
    total = sum(adv) + gap * (len(adv) - 1)
    xs, x = [], AC[0] - total / 2
    for a in adv:
        xs.append(x + a / 2)
        x += a + gap
    CYAN = (200, 245, 255)
    spr_c = [letter(c, f, CYAN) for c in cyr]
    spr_l = [letter(c, f, YELLOW) for c in lat]
    t_flip, step, d_flip = 0.30, 0.085, 0.18
    rus = shadow_text("bahasa Rusia", ImageFont.truetype(MED, 46 * S), (190, 225, 240))
    jawa = shadow_text("nama Jawa pohon upas", ImageFont.truetype(XB, 60 * S), WHITE)
    tag = pill("PROYEK 661 · K-162", 36)
    t_nama = 0.93
    pings = [0.0, 0.8, 1.6, 2.4]
    frames = []
    for i in range(N["anchar"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        ring = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(ring)
        for tk in pings:
            u = (t - tk) / 1.7
            if 0 <= u < 1:
                rr = 60 + 900 * u
                al = int(150 * (1 - u) ** 1.4)
                d.ellipse([(AC[0] - rr) * S, (AC[1] - rr) * S, (AC[0] + rr) * S, (AC[1] + rr) * S], outline=(140, 235, 255, al), width=5 * S)
        # the sweep: a line turning once every 2,4 s with a fading wake
        th0 = -math.pi / 2 + 2 * math.pi * t / 2.4
        for k in range(14):
            th = th0 - k * 0.045
            al = int(70 * (1 - k / 14) ** 2)
            d.line([(AC[0] * S, AC[1] * S), ((AC[0] + 720 * math.cos(th)) * S, (AC[1] + 720 * math.sin(th)) * S)],
                   fill=(140, 235, 255, al), width=(6 if k == 0 else 10) * S)
        im.alpha_composite(ring.resize((W, H), Image.LANCZOS))
        for k in range(5):
            u = min(max((t - t_flip - k * step) / d_flip, 0.0), 1.0)
            sp = spr_c[k] if u < 0.5 else spr_l[k]
            sy = abs(math.cos(math.pi * u))
            if sy < 0.04:
                continue
            sp = sp.resize((sp.width, max(1, round(sp.height * sy))), Image.LANCZOS)
            put1(im, sp, xs[k], AC[1], a=1.0)
        put1(im, tag, 540, 470, a=ramp(t, 0.0, 0.25))
        kr = 1 - ramp(t, t_flip + 0.1, t_flip + 0.35)
        if kr > 0:
            put1(im, rus, 540, 872, a=kr)
        kj = pop(t, t_nama, 0.3)
        if kj > 0:
            put1(im, jawa, 540, 872, a=min(1.0, kj), scale=kj)
        frames.append(im.convert("RGB"))
    return frames


FUN = {"pohon": skema_pohon, "majalah": skema_majalah, "dongeng": skema_dongeng, "kapal": skema_kapal, "anchar": skema_anchar}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    os.makedirs("clips", exist_ok=True)
    for name in args or list(N):
        if name == "tajuk":
            if not out:
                tajuk()
            continue
        fr = FUN[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
