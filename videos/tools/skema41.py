"""Schematic animations for Titik Heran #41 (run in the episode work dir after
`dl.py i:2443620 v:3627 i:3555047 i:1505672 i:1342172`; writes clips/skema_tinggi.mp4, skema_mekar.mp4 and skema_resmi.mp4).
usage: python3 skema41.py [tinggi|mekar|resmi ...] [--sheet out.jpg t1,t2,...]
skema_tinggi: the titan arum in bloom (2443620) pulls back to the whole flower; a ruler card compares a person (1,7 m) with a
  flower drawn at the record height (3,2 m, Meise 2024) - the photographed flower itself is not measured; then green scent rings
  spread from the spadix and "±800 m" pops (the distance Wikipedia gives from Guinness World Records).
skema_mekar: the Bonn bud in its pot (3555047); a year bar fills to 7 ("biasanya 3-7 tahun sekali"), a bloom marker lands on
  "mekar", a red sliver shows the 1-2 days of the bloom, and on "layu" the photo wilts to grey.
skema_resmi: the Bronx from the air over Yankee Stadium (1342172), slow push; a gold BUNGA RESMI · THE BRONX · 1939 seal thumps
  down on "resmi" (the Bronx Borough President made it the borough's official flower after the 1939 bloom; NYBG).
Event times are seconds from the start of each clip, read off `render.py 41 plan`: skema_tinggi starts at 8,20 ("tiga" 1,56,
"aromanya" 3,00, "delapan" 4,76), skema_mekar at 14,60 ("butuh" 1,40, "mekar" 2,88, "lalu" 3,76, "layu" 4,04),
skema_resmi at 23,23 ("resmi" 1,49).
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, text_sprite, dashed, encode
from skema35 import sheet
from skema37 import to_img, put1, ADULT
from skema39 import cover, push, lum, sat, title_shade, figure_mask

N = {"tinggi": 201, "mekar": 180, "resmi": 90}  # each clip runs ~0,3 s past its shot
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
GREEN, RED, GOLD = (150, 255, 140), (236, 52, 48), (246, 198, 72)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def wanted(i, times):
    return times is None or any(abs(i / FPS - x) < 0.5 / FPS for x in times)


def panel(d, box, a=1.0):
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=26 * S, fill=(10, 16, 30, int(200 * a)),
                        outline=(255, 255, 255, int(70 * a)), width=2 * S)


# ---------- height and smell ----------
def flower_icon(d, x, ground, h, a):
    """a plain titan arum outline: a flared spathe cup round a tall spadix, h px tall (2x layer)"""
    sx = lambda u: (x + u * h) * S
    sy = lambda v: (ground - v * h) * S
    spadix = [(-0.05, 0.28), (-0.036, 0.70), (-0.017, 0.95), (0.0, 1.0), (0.017, 0.95), (0.036, 0.70), (0.05, 0.28)]
    d.polygon([(sx(u), sy(v)) for u, v in spadix], fill=(232, 196, 110, int(255 * a)))
    cup = [(-0.04, 0.0), (-0.09, 0.10), (-0.13, 0.26), (-0.18, 0.39), (-0.11, 0.36), (-0.05, 0.41), (0.0, 0.37),
           (0.05, 0.41), (0.11, 0.36), (0.18, 0.39), (0.13, 0.26), (0.09, 0.10), (0.04, 0.0)]  # a narrow ruffled bell
    d.polygon([(sx(u), sy(v)) for u, v in cup], fill=(132, 30, 58, int(255 * a)), outline=(230, 120, 140, int(255 * a)))


def skema_tinggi(times=None):
    t_ruler, t_smell, t_800 = 1.56, 3.00, 4.76
    bg0 = cover("img/2443620.jpg", 0.5)
    card = (668, 600, 1050, 1196)
    G, PX = 1132, 132          # card ground line, px per metre (3,5 m fits)
    PXX, FX, RX = 752, 878, 1006  # person, flower icon, ruler
    person = figure_mask(ADULT, PXX, G, 1.7 * PX)
    lab = ImageFont.truetype(MED, 26 * S)
    labb = ImageFont.truetype(XB, 30 * S)
    lab800 = text_sprite([("±800 m", 60, YELLOW, True)])
    SC = (536, 690)  # scent rings start round the spadix
    frames = []
    for i in range(N["tinggi"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        z = 1.15 - 0.15 * ramp(t, 0.0, 1.4) + 0.03 * ramp(t, 1.4, N["tinggi"] / FPS)
        a = title_shade(push(bg0, z), k=0.35, y1=700)
        kc = ramp(t, t_ruler - 0.15, t_ruler + 0.25) * (1 - ramp(t, t_smell - 0.05, t_smell + 0.3))
        im = to_img(a).convert("RGBA")
        if t >= t_smell - 0.1:  # scent rings: a new ring every 0,42 s, each spreading for 1,9 s
            lay = Image.new("RGBA", (W * S, H * S))
            dark = Image.new("RGBA", (W * S, H * S))  # a dark halo under each ring, so it reads on the green leaves
            d, dd = ImageDraw.Draw(lay), ImageDraw.Draw(dark)
            k0 = ramp(t, t_smell - 0.1, t_smell + 0.2)
            for n in range(12):
                v = t - (t_smell + 0.42 * n)
                if 0 < v < 1.9:
                    r = 40 + 760 * (v / 1.9) ** 0.8
                    u = k0 * (1 - v / 1.9) ** 0.9
                    box = [(SC[0] - r) * S, (SC[1] - r) * S, (SC[0] + r) * S, (SC[1] + r) * S]
                    dd.ellipse(box, outline=(0, 0, 0, int(120 * u)), width=18 * S)
                    d.ellipse(box, outline=GREEN + (int(245 * u),), width=8 * S)
            lay = lay.resize((W, H), Image.LANCZOS)
            im.alpha_composite(dark.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(6)))
            im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6)))
            im.alpha_composite(lay)
        if kc > 0:  # the ruler card
            lay = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(lay)
            panel(d, card, kc)
            d.line([((card[0] + 24) * S, G * S), ((card[2] - 24) * S, G * S)], fill=(255, 255, 255, int(210 * kc)), width=3 * S)
            top = G - 3.5 * PX
            d.line([(RX * S, G * S), (RX * S, top * S)], fill=(255, 255, 255, int(230 * kc)), width=4 * S)
            for mm in (1, 2, 3):
                y = G - mm * PX
                d.line([((RX - 16) * S, y * S), ((RX + 4) * S, y * S)], fill=(255, 255, 255, int(230 * kc)), width=4 * S)
                d.text(((RX - 22) * S, y * S), f"{mm} m", font=lab, fill=(255, 255, 255, int(230 * kc)), anchor="rm")
            kf = ramp(t, t_ruler + 0.1, t_ruler + 0.6)  # the flower grows to the record
            hf = 3.2 * PX * max(kf, 0.02)
            flower_icon(d, FX, G, hf, kc)
            if kf > 0.98:
                yr = G - 3.2 * PX
                dashed(d, [(card[0] + 26, yr), (RX - 6, yr)], YELLOW + (int(255 * kc),), 4, dash=14, gap=10)
                d.text(((FX - 4) * S, (yr - 26) * S), "rekor 3,2 m", font=labb, fill=YELLOW + (int(255 * kc),), anchor="mm")
            d.text((PXX * S, (G + 30) * S), "orang 1,7 m", font=lab, fill=(255, 255, 255, int(230 * kc)), anchor="mm")
            im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
            pm = Image.fromarray((np.clip(person, 0, 1) * 255 * kc * 0.95).astype(np.uint8))
            white = Image.new("RGBA", (W, H), (250, 248, 240, 255))
            white.putalpha(pm)
            im.alpha_composite(white)
        k8 = pop(t, t_800, 0.35)
        if k8 > 0:
            put1(im, lab800, 858, 1020, a=min(1.0, k8), scale=max(k8, 0.01))
        frames.append(im.convert("RGB"))
    return frames


# ---------- years to bloom, two days to wilt ----------
def skema_mekar(times=None):
    t_fill0, t_fill1, t_lalu, t_layu = 1.40, 2.88, 3.76, 4.04
    bg0 = cover("img/3555047.jpg", 0.5)
    X0, X1, Y = 150, 930, 1110
    bar = (96, 1004, 984, 1186)
    tick = ImageFont.truetype(MED, 28 * S)
    tickb = ImageFont.truetype(XB, 30 * S)
    lab_bloom = text_sprite([("MEKAR!", 40, YELLOW, True)])
    lab_wilt = text_sprite([("cuma 1–2 hari", 34, (255, 140, 130), True)])
    frames = []
    for i in range(N["mekar"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        a = push(bg0, 1.0 + 0.06 * i / N["mekar"])
        kw = ramp(t, t_layu, t_layu + 1.2)  # wilting: the colour drains and the light drops
        if kw > 0:
            g = lum(a)[..., None]
            a = a * (1 - 0.85 * kw) + g * 0.85 * kw
            a = a * (1 - 0.28 * kw)
        a = title_shade(a, k=0.35, y1=700)
        im = to_img(a).convert("RGBA")
        kb = ramp(t, t_fill0 - 0.35, t_fill0)
        if kb > 0:
            lay = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(lay)
            panel(d, bar, kb)
            d.text(((X0 - 14) * S, (Y - 50) * S), "tahun ke-", font=tick, fill=(255, 255, 255, int(220 * kb)), anchor="lm")
            d.rounded_rectangle([X0 * S, (Y - 9) * S, X1 * S, (Y + 9) * S], radius=9 * S, fill=(255, 255, 255, int(70 * kb)))
            u = ramp(t, t_fill0, t_fill1)
            if u > 0:
                xe = X0 + (X1 - X0) * u
                d.rounded_rectangle([X0 * S, (Y - 9) * S, max(xe, X0 + 18) * S, (Y + 9) * S], radius=9 * S,
                                    fill=YELLOW + (int(255 * kb),))
            for n in range(1, 8):
                x = X0 + (X1 - X0) * n / 7
                lit = u >= n / 7 - 1e-3
                col = (YELLOW if lit else (255, 255, 255)) + (int(235 * kb),)
                d.line([(x * S, (Y + 14) * S), (x * S, (Y + 30) * S)], fill=col, width=3 * S)
                d.text((x * S, (Y + 52) * S), str(n), font=tickb if lit else tick, fill=col, anchor="mm")
            if t >= t_lalu:  # the bloom itself: a red sliver at the very end
                kr = ramp(t, t_lalu, t_lalu + 0.25)
                d.rounded_rectangle([(X1 - 10) * S, (Y - 16) * S, (X1 + 4) * S, (Y + 16) * S], radius=4 * S,
                                    fill=RED + (int(255 * kr),))
            im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
            kbl = pop(t, t_fill1, 0.3) * (1 - ramp(t, t_lalu - 0.1, t_lalu + 0.15))
            if kbl > 0:
                put1(im, lab_bloom, X1 - 40, Y - 56, a=min(1.0, kbl), scale=max(kbl, 0.01))
            if t >= t_lalu:
                kr = pop(t, t_lalu + 0.05, 0.3)
                put1(im, lab_wilt, X1 - 120, Y - 56, a=min(1.0, kr), scale=max(kr, 0.01))
        frames.append(im.convert("RGB"))
    return frames


# ---------- the official flower ----------
def seal_sprite(r=176, angle=-7):
    """a gold seal: two rings round BUNGA RESMI / 1939 / THE BRONX on a dark disc, ink a little broken; 2x sprite
    (all sizes follow r; drawn at r 196 first)"""
    q = r / 196
    m = 30 * S
    R = r * S
    sp = Image.new("RGBA", (2 * R + 2 * m, 2 * R + 2 * m))
    d = ImageDraw.Draw(sp)
    c = R + m
    d.ellipse([c - R, c - R, c + R, c + R], fill=(14, 18, 30, 190), outline=GOLD + (255,), width=round(10 * q) * S)
    ri = R - round(22 * q) * S
    d.ellipse([c - ri, c - ri, c + ri, c + ri], outline=GOLD + (255,), width=3 * S)
    f1, f2 = ImageFont.truetype(XB, round(34 * q) * S), ImageFont.truetype(XB, round(104 * q) * S)
    d.text((c, c - 92 * q * S), "BUNGA RESMI", font=f1, fill=GOLD + (255,), anchor="mm")
    d.text((c, c + 4 * q * S), "1939", font=f2, fill=GOLD + (255,), anchor="mm")
    d.text((c, c + 96 * q * S), "THE BRONX", font=f1, fill=GOLD + (255,), anchor="mm")
    for k in (-1, 1):  # two small stars beside the year
        x, y = c + k * 150 * q * S, c + 4 * q * S
        pts = [(x + 14 * q * S * math.cos(math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else 0.45),
                y - 14 * q * S * math.sin(math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else 0.45)) for j in range(10)]
        d.polygon(pts, fill=GOLD + (255,))
    rng = np.random.default_rng(41)
    speck = (rng.random((sp.height // 6, sp.width // 6)) > 0.07).astype(np.float32)
    mk = np.asarray(Image.fromarray((speck * 255).astype(np.uint8)).resize(sp.size, Image.BILINEAR)
                    .filter(ImageFilter.GaussianBlur(S)), np.float32) / 255
    al = np.asarray(sp.getchannel("A"), np.float32)
    ink = np.asarray(sp, np.float32)[..., :3].max(2) > 120  # only the gold ink is broken, not the dark disc
    al = np.where(ink, al * mk, al)
    sp.putalpha(Image.fromarray(al.astype(np.uint8)))
    sh = Image.new("RGBA", sp.size)
    ImageDraw.Draw(sh).ellipse([c - R - 10 * S, c - R - 6 * S, c + R + 10 * S, c + R + 14 * S], fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(16 * S))
    sh.alpha_composite(sp)
    return sh.rotate(angle, resample=Image.BICUBIC, expand=True)


def skema_resmi(times=None):
    t_res = 1.49
    im0 = Image.open("img/1342172.jpg").convert("RGB")
    s = H / im0.height
    big = im0.resize((round(im0.width * s), H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    x0 = round(0.485 * big.width - W / 2)
    bg0 = np.asarray(big.crop((x0, 0, x0 + W, H)), np.float32)
    seal = seal_sprite()
    frames = []
    for i in range(N["resmi"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        dy = 0.0
        if t >= t_res:  # the frame knocks when the seal lands
            v = t - t_res - 0.1
            dy = 9 * math.exp(-max(v, 0) * 9) * math.sin(2 * math.pi * 7 * max(v, 0)) if v > 0 else 0.0
        a = push(bg0, 1.0 + 0.07 * i / N["resmi"])
        if dy:
            a = np.roll(a, int(round(dy)), axis=0)
        a = title_shade(sat(a, 1.08), k=0.42, y1=840)
        im = to_img(a).convert("RGBA")
        k = ramp(t, t_res - 0.02, t_res + 0.12)
        if k > 0:
            put1(im, seal, 540, 1102 + dy, a=k, scale=1.6 - 0.6 * k)  # low: the watermark (y 935-985) crosses only the top
            # ring and the dark disc above "BUNGA RESMI", and the 4-line title (to y ~810) stays clear
        frames.append(im.convert("RGB"))
    return frames


OUT = {"tinggi": "clips/skema_tinggi.mp4", "mekar": "clips/skema_mekar.mp4", "resmi": "clips/skema_resmi.mp4"}
FUN = {"tinggi": skema_tinggi, "mekar": skema_mekar, "resmi": skema_resmi}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    for name in args or list(FUN):
        fr = FUN[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
