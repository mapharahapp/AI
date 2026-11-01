"""Schematic animations for Titik Heran #30 (run in the episode work dir after
`dl.py i:4366989 i:456486 i:7372015 i:1284033`; writes clips/skema_sidik.mp4, skema_alur.mp4, skema_persen1.mp4 and skema_persen2.mp4).
usage: python3 skema30.py [sidik|alur|persen1|persen2 ...] [--sheet out.jpg t1,t2,...]   (--sheet saves those frames as a contact sheet)
skema_sidik: a close-up of a real Terracotta warrior's cheek (Pixabay 4366989, Pit 1, Xi'an); a fingerprint (Pixabay 456486, a modern
ink print, not one from the statues) glows on the clay and fades: render.py adds the punch zoom on "sidik".
skema_alur: the same print in clay colours, lying on its side as inked; a magnifier marks the width of one ridge ("lebar alur"), then three lenses compare ridges
as wide as an adult man's, narrower (a woman's) and narrowest (a child's). The widths are drawn to show the idea, not measured.
skema_persen1/2: the share of the 79 prints in the model estimate (Li et al. 2026, Journal of Cultural Heritage): women ±32,7 %,
under-15s ±22,3 %, adult men ±45 %, as a bar over the potter photos (Pixabay 7372015 and 1284033, potters today, not Qin workers).
Event times are seconds from the start of each shot, read off `render.py 30 plan`.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, BOLD, MED, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, glow_sprite, encode

N = {"sidik": 66, "alur": 115, "persen1": 116, "persen2": 138}
GOLD = (255, 206, 110)
CLAY, CLAY_DARK = (222, 138, 86), (58, 30, 16)
ORANGE, GREY = (255, 140, 30), (118, 118, 118)
PRINT_BOX = (490, 230, 890, 485)  # the clearest print in 456486 (it spans x 508-870, y 246-467)


def print_mask():
    """the central ink print of 456486 as a float mask (1 = ridge), its neighbours cut away with a soft oval"""
    g = np.asarray(Image.open("img/456486.jpg").convert("L").crop(PRINT_BOX), np.float32) / 255
    ridge = np.clip((0.82 - g) / 0.5, 0, 1)
    h, w = ridge.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # an oval that leaves out the smudged left end of the print
    oval = np.clip((1 - ((xx - 0.54 * w) / (0.41 * w)) ** 2 - ((yy - 0.47 * h) / (0.45 * h)) ** 2) * 5, 0, 1)
    return ridge * oval


def mask_image(m, size=None, angle=0, sx=1.0):
    """float mask -> 8-bit L image, scaled (sx squashes it sideways) and rotated"""
    im = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8))
    if size:
        im = im.resize((round(size[0] * sx), size[1]), Image.LANCZOS)
    return im.rotate(angle, resample=Image.BICUBIC, expand=True) if angle else im


def solid(col, alpha):
    """an RGBA image of one colour with the given L image as alpha"""
    im = Image.new("RGBA", alpha.size, col + (0,))
    im.putalpha(alpha)
    return im


def scale_alpha(im, a):
    return fade(im, a) if a < 0.999 else im


# ---------- skema_sidik ----------
CROP = (545, 266, 330)  # x0, y0, width of the 9:16 window on 4366989 (it ends at the photo's bottom edge, y 853)
CHEEK = (446, 1000, -16)  # where the print sits in the frame (centre x, y) and its tilt


def cheek_base():
    im = Image.open("img/4366989.jpg").convert("RGB")
    x0, y0, w = CROP
    h = round(w * 16 / 9)
    ext = Image.new("RGB", (im.width, y0 + h))
    ext.paste(im, (0, 0))
    over = y0 + h - im.height
    if over > 0:  # mirror the bottom rows, blurred, so the chest continues under the captions
        mir = im.crop((0, im.height - over, im.width, im.height)).transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(6))
        ext.paste(mir, (0, im.height))
    im = ext.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.LANCZOS).convert("RGBA")
    if over > 0:  # and fade that strip into the dark, like the shadow below a bust
        y1 = round((h - over) / h * H)  # the seam
        g = np.clip((np.arange(H, dtype=np.float32) - (y1 - 120)) / 220, 0, 1) ** 1.3 * 0.85
        shade = Image.new("RGBA", (W, H), (6, 4, 3, 0))
        shade.putalpha(Image.fromarray(np.repeat((g * 255).astype(np.uint8)[:, None], W, 1)))
        im.alpha_composite(shade)
    return im


def sidik(times):
    base = cheek_base()
    m = print_mask()
    ridge = mask_image(m, (400, 255), CHEEK[2], sx=0.9)  # the print in frame pixels, a little squashed by the turn of the cheek
    ridge = ridge.point(lambda v: 0 if v < 70 else min(255, int((v - 70) * 1.6)))  # crisp ridges, clay showing between them
    bloom = ridge.filter(ImageFilter.GaussianBlur(14))
    groove = solid((20, 10, 4), ridge.point(lambda v: v * 0.5))
    glow = solid(GOLD, ridge.point(lambda v: v * 0.8))
    halo = solid((255, 170, 70), bloom.point(lambda v: v * 0.45))
    px, py = CHEEK[0] - ridge.width // 2, CHEEK[1] - ridge.height // 2
    # a light band sweeps across the ridges once they are lit
    xx = np.arange(ridge.width, dtype=np.float32)[None, :] + 0.5 * np.arange(ridge.height, dtype=np.float32)[:, None]
    # sidik 0.04, jarinya 0.39, berkata 0.83, lain. 1.14; the shot ends at 2.03
    out = []
    for t in times:
        im = base.copy()
        a = ramp(t, 0.06, 0.42) * (1 - ramp(t, 1.45, 1.95))
        if a > 0.01:
            im.alpha_composite(scale_alpha(groove, a), (px, py))
            im.alpha_composite(scale_alpha(halo, 0.55 * a), (px, py))
            u = ramp(t, 0.42, 1.1)
            band = 0.55 + 0.9 * np.exp(-((xx - (-80 + (ridge.width + 200) * u)) / 46) ** 2) if 0 < u < 1 else 0.55
            g = np.asarray(glow.getchannel("A"), np.float32) * band * a
            gl = glow.copy()
            gl.putalpha(Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)))
            im.alpha_composite(gl, (px, py))
        out.append(im)
    return out


# ---------- skema_alur ----------
def dark_clay():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt((xx - 540) ** 2 + ((yy - 880) * 0.8) ** 2) / 950
    bg = np.array([66, 36, 20]) * np.clip(1 - r, 0, 1)[..., None] ** 1.5 + np.array([8, 5, 3])
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")


def tinted(mask_l, ridge_col, ground_col=None):
    """ridges in one colour on transparent (or on a ground colour)"""
    out = Image.new("RGBA", mask_l.size, (ground_col or ridge_col) + ((255,) if ground_col else (0,)))
    out.alpha_composite(solid(ridge_col, mask_l))
    return out


def lens(m, cx, cy, zoom, r, rot=0):
    """a round 2x sprite of radius r (1x) showing the print around source point (cx, cy) enlarged `zoom` times"""
    half = r / zoom * 1.5
    patch = m[max(0, int(cy - half)):int(cy + half), max(0, int(cx - half)):int(cx + half)]
    sp = mask_image(patch, (round(patch.shape[1] * zoom * S), round(patch.shape[0] * zoom * S)), rot)
    sp = sp.crop(((sp.width - 2 * r * S) // 2, (sp.height - 2 * r * S) // 2, (sp.width + 2 * r * S) // 2, (sp.height + 2 * r * S) // 2))
    disc = Image.new("L", sp.size, 0)
    ImageDraw.Draw(disc).ellipse([0, 0, sp.width - 1, sp.height - 1], fill=255)
    face = tinted(sp, CLAY, (74, 38, 20))
    face.putalpha(disc)
    rim = Image.new("RGBA", (sp.width + 16 * S, sp.height + 16 * S))
    d = ImageDraw.Draw(rim)
    d.ellipse([0, 0, rim.width - 1, rim.height - 1], fill=(0, 0, 0, 120))
    rim = rim.filter(ImageFilter.GaussianBlur(5 * S))
    rim.alpha_composite(face, (8 * S, 8 * S))
    ImageDraw.Draw(rim).ellipse([8 * S, 8 * S, 8 * S + sp.width - 1, 8 * S + sp.height - 1], outline=(250, 246, 236, 255), width=7 * S)
    return rim


def bracket(width, col=YELLOW, h=40):
    """|<--->| as a 2x sprite, `width` px between the bars (1x), on a dark outline"""
    sp = Image.new("RGBA", ((width + 24) * S, (h + 16) * S))
    d = ImageDraw.Draw(sp)
    x0, x1, y = 12 * S, (12 + width) * S, (h // 2 + 8) * S
    for wd, c in ((11, (0, 0, 0, 210)), (6, col + (255,))):
        for x in (x0, x1):
            d.line([(x, 8 * S), (x, (h + 8) * S)], fill=c, width=wd * S)
        d.line([(x0, y), (x1, y)], fill=c, width=wd * S)
    return sp


PERIOD = 8.6  # ridge period of the print in source pixels (FFT across its ridges: 7.4-9.9)
PATCH = (650, 340)  # a stretch of near-vertical parallel ridges left of the core, shown in every lens


def alur(times):
    bg = dark_clay()
    m = print_mask()
    bh, bw = m.shape
    k = 820 / bw  # the print lies on its side, as inked, 820 px wide
    big = tinted(mask_image(m, (round(bw * k * S), round(bh * k * S))), CLAY)
    shade = solid((0, 0, 0), big.getchannel("A").filter(ImageFilter.GaussianBlur(10 * S)).point(lambda v: v * 0.55))
    cx, cy = 540, 912
    px, py = PATCH[0] - PRINT_BOX[0], PATCH[1] - PRINT_BOX[1]
    lx, ly = cx + (px - bw / 2) * k, cy + (py - bh / 2) * k
    zm = 3.6 * k
    mag, mag_br = lens(m, px, py, zm, 118, rot=0), bracket(round(PERIOD * zm), h=44)
    tag = text_sprite([("LEBAR ALUR", 34, YELLOW, True)])
    zooms = [4.6, 3.6, 2.7]
    names = ["PRIA DEWASA", "PEREMPUAN", "ANAK"]
    subs = ["alur paling lebar", "lebih rapat", "paling rapat"]
    xs, ly3, r3 = [188, 540, 892], 782, 138
    lenses = [lens(m, px, py, z, r3, rot=0) for z in zooms]
    brackets = [bracket(round(PERIOD * z), h=40) for z in zooms]
    labels = [text_sprite([(n, 36, WHITE, True), (s, 29, (255, 226, 160), False)], gap=6) for n, s in zip(names, subs)]
    # Lebar 0.04, alurnya 0.35, beda... 0.83, menurut 1.72, usia 2.01, dan 2.48, jenis 2.68, kelamin. 2.88
    t3 = [1.86, 2.06, 2.26]
    out = []
    for t in times:
        im = bg.copy()
        top = layer()
        a1 = ramp(t, 0.0, 0.25) * (1 - ramp(t, 1.62, 1.86))
        if a1 > 0.01:
            s1 = 0.94 + 0.06 * ramp(t, 0.0, 0.5)
            put(top, shade, cx + 6, cy + 10, a=a1, scale=s1)
            put(top, big, cx, cy, a=a1, scale=s1)
            u = pop(t, 0.35, 0.32)
            if u > 0.01:
                hx, hy = lx + 0.71 * 126, ly + 0.71 * 126
                d = ImageDraw.Draw(top)
                for wd, col in ((26, (40, 26, 16)), (16, (196, 160, 110))):
                    d.line(sc([(hx, hy), (hx + 80 * u, hy + 80 * u)]), fill=col + (round(255 * a1),), width=wd * S)
                put(top, mag, lx, ly, a=a1, scale=u)
                b = pop(t, 0.8, 0.3)
                put(top, mag_br, lx, ly, a=a1 * min(1, b), scale=max(b, 0.01))
                put(top, tag, lx, ly + 176, a=a1 * ramp(t, 0.85, 1.0), scale=pop(t, 0.85))
        for i in range(3):
            u = pop(t, t3[i], 0.34)
            if u > 0.01:
                pulse = 1 + 0.05 * math.sin(math.pi * ramp(t, 2.86 + 0.08 * i, 3.26 + 0.08 * i))
                put(top, lenses[i], xs[i], ly3, scale=u * pulse)
                put(top, brackets[i], xs[i], ly3, a=ramp(t, t3[i] + 0.2, t3[i] + 0.32))
                put(top, labels[i], xs[i], 1036, a=ramp(t, t3[i] + 0.06, t3[i] + 0.2), scale=pop(t, t3[i] + 0.06))
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_persen ----------
BAR = (64, 1034, 1016, 1104)  # x0, y0, x1, y1 of the bar (1x), between the watermark band and the captions
SHARES = [("PEREMPUAN ±33%", 0.327, YELLOW, (34, 26, 0)), ("ANAK ±22%", 0.223, ORANGE, (40, 16, 0)),
          ("PRIA DEWASA ±45%", 0.45, GREY, (255, 255, 255))]


def photo(src, pos, top=0.0, trim=0):
    """render.py's kind f at 1x without the push: cover crop at `pos`, optional blurred room above (`top`); `trim` cuts a white border"""
    im = Image.open(src).convert("RGB")
    if trim:
        im = im.crop((trim, trim, im.width - trim, im.height - trim))
    if top:
        band = im.crop((0, 0, im.width, round(im.height * 0.04))).resize((im.width, round(im.height * top)), Image.BICUBIC)
        band = band.filter(ImageFilter.GaussianBlur(20))
        st = Image.new("RGB", (im.width, im.height + band.height))
        st.paste(band, (0, 0))
        st.paste(im, (0, band.height))
        im = st
    k = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x = round((im.width - W) * pos)
    return im.crop((x, (im.height - H) // 2, x + W, (im.height - H) // 2 + H)).convert("RGBA")


def bar_frame(fill, glow_k, blink=0.0):
    """the bar at 2x: fill[i] is how much of segment i is filled (0-1), glow_k[i] its glow, blink an outline pulse on segment 1"""
    x0, y0, x1, y1 = BAR
    top = layer()
    d = ImageDraw.Draw(top)
    d.rounded_rectangle(sc([(x0 - 22, y0 - 20), (x1 + 22, y1 + 20)]), radius=26 * S, fill=(10, 8, 6, 165))
    d.rounded_rectangle(sc([(x0, y0), (x1, y1)]), radius=14 * S, fill=(255, 255, 255, 26), outline=(255, 255, 255, 90), width=2 * S)
    font = ImageFont.truetype(BOLD, 27 * S)
    x = x0
    for i, (name, share, col, ink) in enumerate(SHARES):
        w = (x1 - x0) * share
        if glow_k[i] > 0.01:
            g = Image.new("L", (round((w + 100) * S), round((y1 - y0 + 100) * S)), 0)
            ImageDraw.Draw(g).rounded_rectangle([50 * S, 50 * S, g.width - 50 * S, g.height - 50 * S], radius=16 * S, fill=255)
            k = 2.2 * glow_k[i]  # a halo that reaches well past the segment
            g = g.filter(ImageFilter.GaussianBlur(17 * S)).point(lambda v: min(255, int(v * k)))
            top.alpha_composite(solid(col, g), (round((x - 50) * S), round((y0 - 50) * S)))
            d = ImageDraw.Draw(top)
        if fill[i] > 0.005:
            fx1 = x + w * fill[i]
            seg = Image.new("RGBA", top.size)
            ImageDraw.Draw(seg).rounded_rectangle(sc([(x + 2, y0 + 2), (max(fx1 - 2, x + 6), y1 - 2)]), radius=12 * S, fill=col + (255,))
            top.alpha_composite(seg)
            d = ImageDraw.Draw(top)
            tb = font.getbbox(name)
            tx, ty = (x + w / 2) * S - (tb[2] - tb[0]) / 2 - tb[0], (y0 + y1) / 2 * S - (tb[1] + tb[3]) / 2
            txt = Image.new("RGBA", top.size)
            ImageDraw.Draw(txt).text((tx, ty), name, font=font, fill=ink + (255,))
            # the label shows only where the segment is already filled
            m = Image.new("L", top.size, 0)
            ImageDraw.Draw(m).rectangle([x * S, y0 * S, fx1 * S, y1 * S], fill=255)
            txt.putalpha(Image.fromarray(np.minimum(np.asarray(txt.getchannel("A")), np.asarray(m))))
            top.alpha_composite(txt)
            d = ImageDraw.Draw(top)
        if i == 1 and blink > 0.01:
            d.rounded_rectangle(sc([(x + 3, y0 + 3), (x + w - 3, y1 - 3)]), radius=12 * S, outline=ORANGE + (round(255 * blink),), width=5 * S)
        if i < 2:
            d.line(sc([(x + w, y0 + 8), (x + w, y1 - 8)]), fill=(255, 255, 255, 110), width=2 * S)
        x += w
    return top


def persen1(times):
    base = photo("img/7372015.jpg", 0.8, top=0.25, trim=3)
    # Hasilnya, 0.05, sekitar 0.99, sepertiga 1.39, diduga 2.22, milik 2.65, perempuan. 2.89
    out = []
    for t in times:
        im = base.copy()
        f = ramp(t, 1.38, 1.78)
        gl = 0.35 * math.sin(math.pi * ramp(t, 1.5, 2.1)) + 0.75 * math.sin(math.pi * ramp(t, 2.86, 3.5))
        top = bar_frame([f, 0, 0], [gl, 0, 0])
        im.alpha_composite(fade(down(top), ramp(t, 0.0, 0.3)))
        out.append(im)
    return out


def persen2(times):
    base = photo("img/1284033.jpg", 0.3)
    # Dan 0.04, lebih 0.34, dari 0.81, seperlima... 1.05, milik 1.92, anak 2.31, di 2.63, bawah 2.82, lima 3.18, belas 3.37, tahun! 3.65
    out = []
    for t in times:
        im = base.copy()
        blink = 0.0 if t < 1.0 or t > 2.32 else 0.5 + 0.5 * math.cos(2 * math.pi * (t - 1.0) / 0.42)
        f = [1.0, ramp(t, 2.28, 2.6), ramp(t, 3.62, 4.02)]
        gl = [0.0, 0.9 * math.sin(math.pi * ramp(t, 2.3, 3.1)), 0.0]
        im.alpha_composite(down(bar_frame(f, gl, blink * 0.9)))
        out.append(im)
    return out


OUT = {k: f"clips/skema_{k}.mp4" for k in N}

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
