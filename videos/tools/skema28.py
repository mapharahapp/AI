"""Schematic animations for Titik Heran #28 (run in the episode work dir after `dl.py i:840125 i:1692989 i:5564510`;
writes clips/skema_coret.mp4, skema_bekal.mp4, skema_alat.mp4 and skema_waktu.mp4).
usage: python3 skema28.py [coret|bekal|alat|waktu ...] [--sheet out.jpg t1,t2,...]   (--sheet saves those frames as a contact sheet)
skema_coret: a stethoscope (Pixabay 840125, a stand-in for "doctor") laid out like render.py's kind b, crossed out in red on "dokter":
none of Weni's titles calls him a doctor.
skema_bekal: a relief of offering bearers (Pixabay 1692989, another tomb, not Weni's) with four small bronze tools popping in one by one:
metal tools, often small models, were common grave goods for Old Kingdom officials.
skema_alat: the same four tools in the dark, lighting up gold one by one on "kalau terbukti alat medis".
The tools (chisel, knife, hook, needle) are generic Egyptian bronze shapes drawn here, not copies of the tools found in Weni's shaft.
skema_waktu: a Hippocrates bust (Pixabay 5564510, a modern statuette) with a time line from Weni (about 2300 BC) to Hippocrates
(born about 460 BC); the counter runs up to about 1,800 years.
Event times are seconds from the start of each shot, read off `render.py 28 plan`.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, glow_sprite, encode
from skema17 import ring
from skema24 import kind_b, stroke
from skema27 import glint

N = {"coret": 90, "bekal": 130, "alat": 75, "waktu": 84}
RED = (226, 40, 36)
GOLD = (255, 204, 96)


# ---------- the tools: outlines in units of the tool's height, centred on (0, 0), y down ----------
def hook_pts():
    c, r = (0.08, 0.3), 0.08
    arc = [(c[0] - r * math.cos(math.pi * k / 12), c[1] + r * math.sin(math.pi * k / 12)) for k in range(13)]
    return [(0.0, -0.46)] + arc + [(0.16, 0.2)]


TOOLS = {
    "pahat": [(-0.035, -0.5), (0.035, -0.5), (0.04, 0.28), (0.078, 0.47), (0.062, 0.5), (-0.062, 0.5), (-0.078, 0.47), (-0.04, 0.28)],
    "pisau": [(-0.02, -0.5), (0.02, -0.5), (0.025, -0.18), (0.06, -0.16), (0.078, 0.1), (0.062, 0.32), (0.0, 0.5), (-0.046, 0.3),
              (-0.062, 0.05), (-0.05, -0.16), (-0.025, -0.18)],
    "kait": None,  # a bent rod: drawn as a thick line along hook_pts()
    "jarum": [(-0.018, -0.44), (0.018, -0.44), (0.013, 0.3), (0.0, 0.5), (-0.013, 0.3)],
}
ORDER = ["pahat", "pisau", "kait", "jarum"]
XS = [210, 420, 650, 872]  # the tools' centres across the frame


def tool_mask(kind, h, pad=0):
    """the tool's silhouette at 2x in a box 0.5h wide and 1.1h tall, plus `pad` px on each side (room for a glow);
    the shapes are drawn 1.3x wider than listed, so the thin tools still read at Reels size"""
    bw, bh = round(0.5 * h) + 2 * pad, round(1.1 * h) + 2 * pad
    m = Image.new("L", (bw * S, bh * S), 0)
    d = ImageDraw.Draw(m)
    P = lambda pts: [((bw / 2 + 1.3 * x * h) * S, (bh / 2 + y * h) * S) for x, y in pts]
    if kind == "kait":
        pts = P(hook_pts())
        d.line(pts, fill=255, width=round(0.034 * h * S), joint="curve")
        for (x, y), rr in ((pts[0], 0.026 * h), (pts[-1], 0.012 * h)):
            d.ellipse([x - rr * S, y - rr * S, x + rr * S, y + rr * S], fill=255)
    else:
        d.polygon(P(TOOLS[kind]), fill=255)
        if kind == "jarum":  # the eye
            x, y = P([(0, -0.4)])[0]
            d.ellipse([x - 0.007 * h * S, y - 0.02 * h * S, x + 0.007 * h * S, y + 0.02 * h * S], fill=0)
    return m


def tool_sprite(kind, h, lit=False):
    """bronze (or, lit, glowing gold) metal: light on the left edge, dark on the right, a thin dark rim"""
    m = tool_mask(kind, h)
    w2, h2 = m.size
    xx = np.linspace(0, 1, w2, dtype=np.float32)[None, :]
    yy = np.linspace(0, 1, h2, dtype=np.float32)[:, None]
    lo, mid, hi = ((150, 96, 44), (196, 136, 70), (240, 196, 130)) if not lit else ((214, 150, 50), (255, 206, 96), (255, 246, 196))
    u = np.clip(0.5 + 0.9 * np.cos((xx - 0.42) * 7.0) * 0.5 - 0.15 * yy, 0, 1)[..., None]
    col = np.where(u > 0.5, np.array(mid) + (np.array(hi) - np.array(mid)) * (u - 0.5) * 2, np.array(lo) + (np.array(mid) - np.array(lo)) * u * 2)
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")
    rim = m.filter(ImageFilter.MaxFilter(5))
    out = Image.new("RGBA", m.size, (52, 30, 12, 0))
    out.putalpha(rim)
    im.putalpha(m)
    out.alpha_composite(im)
    return out


def tool_glow(kind, h):
    m = tool_mask(kind, h, pad=round(0.2 * h)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(0.06 * h * S))
    g = Image.new("RGBA", m.size, GOLD + (0,))
    g.putalpha(m.point(lambda v: min(255, int(v * 1.6))))
    return g


# ---------- skema_coret ----------
def coret(times):
    base, py, ph = kind_b("img/840125.jpg")
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    # Padahal... 0.02, ia 1.14, tak 1.37, pernah 1.52, disebut 1.75, dokter. 2.13
    out = []
    for t in times:
        im = base.copy()
        im.alpha_composite(fade(dark, 0.3 * ramp(t, 2.0, 2.3)))
        top = layer()
        stroke(ImageDraw.Draw(top), (160, py + 90), (920, py + ph - 90), ramp(t, 2.08, 2.26), 30, RED + (240,), wob=3)
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_bekal ----------
def bekal(times):
    base, py, ph = kind_b("img/1692989.jpg")
    h, cy = 250, 1166
    sp = [tool_sprite(k, h) for k in ORDER]
    band = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(band)
    d.rounded_rectangle([46, cy - 148, W - 46, cy + 140], radius=26, fill=(14, 10, 6, 165))
    band = band.filter(ImageFilter.GaussianBlur(3))
    gl = glint(26)
    # Ahli 0.03, mengingatkan 0.30, perkakas 1.24, seperti 1.62, ini 1.92, sering 2.38, jadi 2.76, bekal 2.98, kubur 3.25, pejabat 3.52
    t_in = [1.2 + 0.22 * k for k in range(4)]
    out = []
    for t in times:
        im = base.copy()
        im.alpha_composite(fade(band, ramp(t, 1.0, 1.3)))
        top = layer()
        for k in range(4):
            put(top, sp[k], XS[k], cy, a=ramp(t, t_in[k], t_in[k] + 0.12), scale=pop(t, t_in[k], 0.32))
        for k in range(4):  # a glint runs down each tool as it lands
            u = ramp(t, t_in[k] + 0.12, t_in[k] + 0.5)
            if 0 < u < 1:
                put(top, gl, XS[k] + 6, cy - 90 + 150 * u, a=math.sin(math.pi * u), scale=0.6 + 0.5 * math.sin(math.pi * u))
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_alat ----------
def alat(times):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt((xx - 540) ** 2 + ((yy - 930) * 0.8) ** 2) / 900
    bg = np.array([46, 30, 16]) * np.clip(1 - r, 0, 1)[..., None] ** 1.6 + np.array([4, 3, 2])
    base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
    h, cy = 430, 935
    dim = [tool_sprite(k, h) for k in ORDER]
    lit = [tool_sprite(k, h, lit=True) for k in ORDER]
    glow = [tool_glow(k, h) for k in ORDER]
    gl = glint(40)
    # Tapi 0.05, kalau 0.49, terbukti 0.72, alat 1.10, medis... 1.40
    t_on = [0.5 + 0.25 * k for k in range(4)]
    out = []
    for t in times:
        im = base.copy()
        top = layer()
        for k in range(4):
            u = ramp(t, t_on[k], t_on[k] + 0.28)
            swell = 1 + 0.25 * ramp(t, 1.38, 1.6) * (0.6 + 0.4 * math.sin(6 * (t - 1.38)))
            put(top, glow[k], XS[k], cy, a=min(1.0, 0.85 * u * swell))
            put(top, dim[k], XS[k], cy, a=0.75 + 0.25 * ramp(t, 0, 0.3))
            put(top, lit[k], XS[k], cy, a=u)
        for k in range(4):  # all four flash on "medis"
            v = ramp(t, 1.38 + 0.06 * k, 1.75 + 0.06 * k)
            if 0 < v < 1:
                put(top, gl, XS[k], cy - 150 + 60 * (k % 2), a=math.sin(math.pi * v), scale=0.5 + 0.6 * math.sin(math.pi * v))
        im.alpha_composite(down(top))
        out.append(im)
    return out


# ---------- skema_waktu ----------
def framed(src, w, bottom, at):
    """kind b with a smaller photo: `w` px wide, its row `at` (0-1 of its height) on y = `bottom`, edges feathered into the blur"""
    im = Image.open(src).convert("RGB")
    k = max(W / im.width, H / im.height)  # the blurred, darkened background of kind_b()
    bg = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(30))
    base = Image.fromarray(np.clip(np.asarray(bg, np.float32) * 0.8 - 8, 0, 255).astype(np.uint8)).convert("RGBA")
    fg = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    y = np.minimum(np.arange(fg.height), fg.height - 1 - np.arange(fg.height))[:, None]
    x = np.minimum(np.arange(fg.width), fg.width - 1 - np.arange(fg.width))[None, :]
    a = np.clip(np.minimum(x, y) / 40, 0, 1)
    fg.putalpha(Image.fromarray((a * a * (3 - 2 * a) * 255).astype(np.uint8)))
    base.alpha_composite(fg.convert("RGBA"), ((W - w) // 2, round(bottom - at * fg.height)))
    return base


def waktu(times):
    base = framed("img/5564510.jpg", 918, 1150, 0.95)  # the bust from its head to its name plate, between the title and the band
    band = Image.new("RGBA", (W, H))
    ImageDraw.Draw(band).rounded_rectangle([34, 1158, W - 34, 1306], radius=24, fill=(8, 8, 12, 178))
    base.alpha_composite(band.filter(ImageFilter.GaussianBlur(3)))
    x0, x1, ly = 120, 960, 1236
    left = text_sprite([("WENI ±2300 SM", 31, WHITE, True)])
    right = text_sprite([("HIPPOCRATES ±460 SM", 31, WHITE, True)])
    dot_y, dot_w = glow_sprite(18, YELLOW), glow_sprite(18, WHITE)
    # seribu 0.02, delapan 0.33, ratus 0.63, tahun 1.01, sebelum 1.39, Hipokrates! 1.69
    out = []
    for t in times:
        im = base.copy()
        top = layer()
        d = ImageDraw.Draw(top)
        p = ramp(t, 0.0, 1.15)
        d.line(sc([(x0, ly), (x1, ly)]), fill=(255, 255, 255, 110), width=6 * S)
        d.line(sc([(x0, ly), (x0 + (x1 - x0) * p, ly)]), fill=YELLOW + (255,), width=9 * S)
        put(top, dot_y, x0, ly, a=1.0, scale=0.75)
        put(top, dot_w, x1, ly, a=0.5 + 0.5 * ramp(t, 1.6, 1.8), scale=0.75)
        d.ellipse(sc([(x0 - 13, ly - 13), (x0 + 13, ly + 13)]), fill=YELLOW + (255,), outline=(20, 20, 20, 255), width=3 * S)
        hit = ramp(t, 1.66, 1.82)
        d.ellipse(sc([(x1 - 13, ly - 13), (x1 + 13, ly + 13)]), fill=(255, 255, 255, 255) if hit < 1 else YELLOW + (255,),
                  outline=(20, 20, 20, 255), width=3 * S)
        if 0 < ramp(t, 1.66, 2.3) < 1:  # a ring goes out from Hippocrates on his name
            u = ramp(t, 1.66, 2.3)
            ring(d, x1, ly, 16 + 46 * u, YELLOW, 255 * (1 - u), w=4)
        put(top, left, x0 - 50 + left.width / S / 2, ly + 42)
        put(top, right, x1 + 50 - right.width / S / 2, ly + 42)
        v = round(1800 * p / 10) * 10
        num = text_sprite([(f"±{v:,} TAHUN".replace(",", "."), 46, YELLOW, True)])
        put(top, num, (x0 + x1) / 2, ly - 44, a=ramp(t, 0.0, 0.15))
        im.alpha_composite(down(top))
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
