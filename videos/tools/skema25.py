"""Reconstructions for Titik Heran #25 (run in the episode work dir after `dl.py i:1074131 v:107240`; writes clips/skema_tulis.mp4,
skema_bisik.mp4, skema_paraf.mp4 and skema_ikrar.mp4).
usage: python3 skema25.py FONT_DIR [tulis|bisik|paraf|ikrar ...] [--sheet out.jpg t1,t2,...]
       (FONT_DIR holds HomemadeApple-Regular.ttf and SpecialElite-Regular.ttf from github.com/google/fonts, folders
       apache/homemadeapple and apache/specialelite; --sheet saves those frames as a contact sheet instead of encoding)
All four are reconstructions, not copies of the real papers (whose look is not reproduced): a slip of old paper (Pixabay 1074131)
on a dark desk (a blurred frame of Pixabay 107240).
skema_tulis: Yamin's sentence "Ik heb een eleganter formulering voor de resolutie" is written on the slip, stroke by stroke.
skema_bisik: a close-up of the slip, the sentence marked in yellow as Akram whispers its meaning.
skema_paraf: "setuju" and a paraf appear on the slip (Sugondo), then it slides on and more parafs follow (the other delegates).
skema_ikrar: the three pledges typed in the original spelling, as shown by the Museum Sumpah Pemuda; the camera moves to the
third, a sticky note with the common misquote "berbahasa satu" is crossed out, and "mendjoendjoeng bahasa persatoean" is marked.
Event times are seconds from the start of each shot, read off `render.py 25 plan`.
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, layer, down, text_sprite, fade, put, encode
from skema18 import check

N = {"tulis": 102, "bisik": 78, "paraf": 93, "ikrar": 195}
FONTS = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in N else "fonts"
HAND, TYPE = os.path.join(FONTS, "HomemadeApple-Regular.ttf"), os.path.join(FONTS, "SpecialElite-Regular.ttf")
INK, INK2, RED = (34, 28, 62), (22, 40, 92), (214, 34, 30)
NOTE = ["Ik heb een eleganter", "formulering voor", "de resolutie"]
SLIP_W, SLIP_H = 900, 560  # the slip at 1x; everything on it is drawn at 2x


def desk():
    png = subprocess.run(["ffmpeg", "-v", "error", "-ss", "2", "-i", "clips/107240.mp4", "-frames:v", "1", "-f", "image2pipe",
                          "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    import io
    im = Image.open(io.BytesIO(png)).convert("RGB")
    k = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    a = np.asarray(im.filter(ImageFilter.GaussianBlur(22)), np.float32) * 0.42
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def paper(w, h, seed):
    """old paper (Pixabay 1074131) cut to w x h (2x pixels) with a slightly torn edge"""
    tex = Image.open("img/1074131.jpg").convert("RGB")
    k = max(w / tex.width, h / tex.height) * 1.02
    tex = tex.resize((round(tex.width * k), round(tex.height * k)), Image.LANCZOS).crop((0, 0, w, h)).convert("RGBA")
    rng = np.random.default_rng(seed)
    pts = []
    for side in range(4):
        n = 40
        for i in range(n):
            u = i / n
            j = rng.normal(0, 3.2 * S)
            x, y = [(u * w, 0), (w, u * h), (w - u * w, h), (0, h - u * h)][side]
            nx, ny = [(0, 1), (-1, 0), (0, -1), (1, 0)][side]
            pts.append((x + nx * (6 * S + j), y + ny * (6 * S + j)))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    tex.putalpha(m.filter(ImageFilter.GaussianBlur(1.2)))
    return tex


def hand_lines(d, lines, x0, y0, size, gap, fill):
    """handwritten lines; returns each line's (x0, y0, x1, y1) box in the slip's 2x pixels"""
    f = ImageFont.truetype(HAND, size * S)
    boxes = []
    y = y0
    for t in lines:
        b = f.getbbox(t)
        d.text((x0 * S, y * S), t, font=f, fill=fill)
        boxes.append((x0 * S + b[0], y * S + b[1], x0 * S + b[2], y * S + b[3]))
        y += gap
    return boxes


def note_layer():
    """the sentence alone on a clear layer the size of the slip (2x), with each line's box"""
    tx = Image.new("RGBA", (SLIP_W * S, SLIP_H * S), (0, 0, 0, 0))
    boxes = hand_lines(ImageDraw.Draw(tx), NOTE, 84, 70, 60, 138, INK + (240,))
    return tx, boxes


def reveal(tx, boxes, u):
    """the handwriting written up to fraction u of its letters, line by line, left to right"""
    lens = [len(t) for t in NOTE]
    goal = u * sum(lens)
    m = Image.new("L", tx.size, 0)
    d = ImageDraw.Draw(m)
    for (x0, y0, x1, y1), n in zip(boxes, lens):
        k = min(max(goal / n, 0.0), 1.0)
        if k > 0:
            d.rectangle([x0 - 10 * S, y0 - 30 * S, x0 + (x1 - x0 + 10 * S) * k, y1 + 30 * S], fill=255)
        goal -= n
    out = tx.copy()
    out.putalpha(ImageChops.multiply(tx.getchannel("A"), m.filter(ImageFilter.GaussianBlur(3 * S))))
    return out


def place(base, slip, cx, cy, ang, scale=1.0, shadow=True):
    """put a 2x slip on a 1x frame, rotated by ang degrees about its centre"""
    sp = slip.rotate(ang, resample=Image.BICUBIC, expand=True)
    sp = sp.resize((max(1, round(sp.width * scale / S)), max(1, round(sp.height * scale / S))), Image.LANCZOS)
    if shadow:
        sh = Image.new("RGBA", sp.size, (0, 0, 0, 0))
        sh.putalpha(sp.getchannel("A").point(lambda v: v * 0.65))
        sh = sh.filter(ImageFilter.GaussianBlur(14 * scale))
        base.alpha_composite(sh, (round(cx - sp.width / 2 + 10 * scale), round(cy - sp.height / 2 + 18 * scale)))
    base.alpha_composite(sp, (round(cx - sp.width / 2), round(cy - sp.height / 2)))


# ---------- skema_tulis ----------
def tulis(times):
    bg, slip, (tx, boxes) = desk(), paper(SLIP_W * S, SLIP_H * S, 25), note_layer()
    # Dan 0.05, bisikan 0.27, pertamanya... 0.68, bahasa 1.84, Belanda. 2.14
    out = []
    for t in times:
        im = bg.copy()
        sp = slip.copy()
        sp.alpha_composite(reveal(tx, boxes, ramp(t, 0.25, 2.45) ** 0.9))
        k = ramp(t, 0.0, 0.3)
        place(im, fade(sp, k) if k < 1 else sp, 540, 940 + 60 * (1 - k), -2.5)
        out.append(im)
    return out


# ---------- skema_bisik ----------
def marker(boxes, ws):
    """a yellow highlighter over fraction w of each line's box (2x slip pixels), for multiplying onto the slip"""
    m = Image.new("RGB", (SLIP_W * S, SLIP_H * S), (255, 255, 255))
    d = ImageDraw.Draw(m)
    for (x0, y0, x1, y1), w in zip(boxes, ws):
        if w > 0:
            d.rounded_rectangle([x0 - 14 * S, y0 + 2 * S, x0 - 14 * S + (x1 - x0 + 28 * S) * w, y1 + 6 * S], radius=10 * S,
                                fill=(255, 226, 70))
    return m


def bisik(times):
    bg, slip, (tx, boxes) = desk(), paper(SLIP_W * S, SLIP_H * S, 25), note_layer()
    # Saya 0.02, punya 0.37, rumusan 0.59, yang 1.04, lebih 1.19, elegan. 1.42
    spans = [(0.05, 0.62), (0.62, 1.12), (1.12, 1.6)]
    out = []
    for t in times:
        im = bg.copy()
        sp = slip.copy()
        hl = marker(boxes, [ramp(t, a, b) for a, b in spans])
        rgb = ImageChops.multiply(sp.convert("RGB"), hl)
        sp = Image.merge("RGBA", (*rgb.split(), sp.getchannel("A")))
        sp.alpha_composite(tx)
        place(im, sp, 560, 930, -2.5, scale=1.16 + 0.05 * ramp(t, 0.0, 2.6))
        out.append(im)
    return out


# ---------- skema_paraf ----------
def squiggle(d, x, y, s, seed, fill, width):
    """a made-up paraf: a looping flourish of size s at (x, y), 2x pixels"""
    rng = np.random.default_rng(seed)
    pts, a = [], rng.uniform(0, 1)
    for i in range(60):
        u = i / 59
        pts.append((x + s * (u * 1.6 - 0.8) + 0.28 * s * math.sin(u * 13 + a), y + 0.34 * s * math.sin(u * 9 + 2 * a) - 0.2 * s * u))
    d.line(pts, fill=fill, width=width, joint="curve")
    return pts


def ink_on(base, draw, u):
    """draw something on its own layer and reveal it left to right up to fraction u"""
    if u <= 0:
        return
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    box = draw(ImageDraw.Draw(lay))
    if u < 1:
        x0, x1 = box
        m = Image.new("L", base.size, 0)
        ImageDraw.Draw(m).rectangle([0, 0, x0 + (x1 - x0) * u, base.height], fill=255)
        lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m))
    base.alpha_composite(lay)


def paraf(times):
    bg, slip, (tx, boxes) = desk(), paper(SLIP_W * S, SLIP_H * S, 25), note_layer()
    slip.alpha_composite(tx)
    fh = ImageFont.truetype(HAND, 56 * S)

    def setuju(d):
        d.text((520 * S, 404 * S), "setuju", font=fh, fill=INK2 + (245,))
        squiggle(d, 800 * S, 452 * S, 58 * S, 7, INK2 + (245,), 4 * S)
        return 500 * S, 860 * S

    # the others initial it in the free space under "de resolutie", clear of Sugondo's "setuju"
    others = [(lambda d, x=x, y=y, k=k: (squiggle(d, x * S, y * S, 54 * S, k, INK + (235,), 4 * S), ((x - 56) * S, (x + 56) * S))[1])
              for x, y, k in ((130, 482, 11), (285, 500, 12), (430, 478, 13))]
    # Sugondo 0.03, memaraf 0.46, setuju, 0.87, kertas 1.61, beredar, 1.89
    out = []
    for t in times:
        im = bg.copy()
        sp = slip.copy()
        ink_on(sp, setuju, ramp(t, 0.42, 1.05))
        for k, f in enumerate(others):
            ink_on(sp, f, ramp(t, 1.85 + 0.22 * k, 2.1 + 0.22 * k))
        m = ramp(t, 1.5, 2.1)  # passed on: the slip slides a little, turns and shrinks, staying inside the frame
        place(im, sp, 540 - 40 * m + 30 * ramp(t, 2.1, 3.1), 940 + 20 * m, -2.5 + 5 * m, scale=1 - 0.1 * m)
        out.append(im)
    return out


# ---------- skema_ikrar ----------
PAGE_W, PAGE_H, COL_X, COL_W = 760, 1240, 70, 620
PLEDGES = [("Pertama", "Kami poetera dan poeteri Indonesia mengakoe bertoempah darah jang satoe, tanah Indonesia."),
           ("Kedoea", "Kami poetera dan poeteri Indonesia mengakoe berbangsa jang satoe, bangsa Indonesia."),
           ("Ketiga", "Kami poetera dan poeteri Indonesia mendjoendjoeng bahasa persatoean, bahasa Indonesia.")]
MARK = ("mendjoendjoeng", "bahasa", "persatoean,")


def typeset():
    """the typed page (1x units, drawn at 2x): returns the page, the pledge headings' boxes, the marked words' boxes and the box
    of the third pledge's last word"""
    pg = paper(PAGE_W * S, PAGE_H * S, 28)
    d = ImageDraw.Draw(pg)
    fh, fb = ImageFont.truetype(TYPE, 36 * S), ImageFont.truetype(TYPE, 34 * S)
    for k, t in enumerate(("Poetoesan Congres", "Pemoeda-Pemoeda Indonesia")):
        w = d.textlength(t, font=fh)
        d.text(((PAGE_W * S - w) / 2, (70 + 50 * k) * S), t, font=fh, fill=INK + (235,))
    d.line([(COL_X * S, 190 * S), ((COL_X + COL_W) * S, 190 * S)], fill=INK + (160,), width=2 * S)
    y, sp = 240, d.textlength(" ", font=fb)
    heads, marks, end3 = [], [], None
    for k, (head, body) in enumerate(PLEDGES):
        hb = d.textbbox((COL_X * S, y * S), head.upper(), font=fb)
        d.text((COL_X * S, y * S), head.upper(), font=fb, fill=INK + (240,))
        d.line([(hb[0], hb[3] + 4 * S), (hb[2], hb[3] + 4 * S)], fill=INK + (200,), width=2 * S)
        heads.append([v / S for v in hb])
        y += 58
        x = COL_X * S
        for word in body.split():
            w = d.textlength(word, font=fb)
            if x + w > (COL_X + COL_W) * S:
                x, y = COL_X * S, y + 50
            d.text((x, y * S), word, font=fb, fill=INK + (240,))
            if k == 2:
                b = [v / S for v in d.textbbox((x, y * S), word, font=fb)]
                end3 = b
                if word in MARK:
                    marks.append(b)
            x += w + sp
        y += 92
    return pg, heads, marks, end3


def sticky(seed=5):
    """a yellow sticky note with the misquote written on it (2x)"""
    w, h = 520 * S, 190 * S
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h], fill=(252, 226, 92, 255))
    d.rectangle([0, 0, w, 26 * S], fill=(236, 204, 70, 255))
    f = ImageFont.truetype(HAND, 50 * S)
    t = '"berbahasa satu"'
    tw = d.textlength(t, font=f)
    d.text(((w - tw) / 2, 52 * S), t, font=f, fill=(40, 40, 60, 255))
    return im


def ikrar(times):
    bg = desk()
    pg, heads, marks, end3 = typeset()
    note = sticky()
    # Tapi 0.04, coba 0.51, cek 0.81, ikrar 0.96, ketiga: 1.26, bukan 2.01, berbahasa 2.31, satu... 2.76, melainkan 3.58,
    # menjunjung 4.25, bahasa 4.85, persatuan. 5.23
    h3 = heads[2]
    c3 = (COL_X + COL_W / 2, (h3[1] + marks[-1][3]) / 2 + 20)
    # the whole page first, small enough that its heading sits below the title and its blank foot under the captions
    cam0, cam1 = ((PAGE_W / 2, 553), 0.75), ((c3[0], c3[1]), 1.55)
    word_t = [(4.2, 4.8), (4.8, 5.2), (5.2, 5.6)]
    out = []
    for t in times:
        z = ramp(t, 0.85, 1.55)
        k0 = cam0[1] + 0.05 * ramp(t, 0.0, 0.85)  # a slow push on the whole page, then the punch-in to the third pledge
        cx = cam0[0][0] + (cam1[0][0] - cam0[0][0]) * z
        cy = cam0[0][1] + (cam1[0][1] - cam0[0][1]) * z
        k = k0 + (cam1[1] - k0) * z + 0.03 * ramp(t, 1.55, 6.5)
        oy = 1000  # where the camera centre sits in the frame, below the title

        def P(x, y):  # page (1x) -> frame
            return 540 + (x - cx) * k, oy + (y - cy) * k
        # the page, marked words multiplied in yellow
        page = pg.copy()
        hl = Image.new("RGB", page.size, (255, 255, 255))
        dh = ImageDraw.Draw(hl)
        for (x0, y0, x1, y1), (a, b) in zip(marks, word_t):
            u = ramp(t, a, b)
            if u > 0:
                dh.rounded_rectangle([(x0 - 6) * S, (y0 - 4) * S, (x0 - 6 + (x1 - x0 + 12) * u) * S, (y1 + 8) * S], radius=6 * S,
                                     fill=(255, 224, 60))
        rgb = ImageChops.multiply(page.convert("RGB"), hl)
        page = Image.merge("RGBA", (*rgb.split(), page.getchannel("A")))
        sp = page.resize((round(PAGE_W * k), round(PAGE_H * k)), Image.LANCZOS)
        im = bg.copy()
        x0, y0 = P(0, 0)
        sh = Image.new("RGBA", sp.size, (0, 0, 0, 150))
        sh.putalpha(sp.getchannel("A").point(lambda v: v * 0.6))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)), (round(x0 + 12), round(y0 + 18)))
        im.alpha_composite(sp, (round(x0), round(y0)))
        top = layer()
        d = ImageDraw.Draw(top)
        # dim the first two pledges once the camera is on the third
        dim = 0.45 * ramp(t, 1.1, 1.6)
        if dim > 0:
            a0, a1 = P(0, 0), P(PAGE_W, heads[2][1] - 18)
            d.rectangle([a0[0] * S, a0[1] * S, a1[0] * S, a1[1] * S], fill=(10, 8, 6, round(255 * dim)))
        # "KETIGA" ringed in yellow on "ketiga"
        if t >= 1.26:
            a, b = P(h3[0] - 14, h3[1] - 12), P(h3[2] + 14, h3[3] + 14)
            u = pop(t, 1.26)
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            rx, ry = (b[0] - a[0]) / 2 * u, (b[1] - a[1]) / 2 * u
            d.rounded_rectangle([(mx - rx) * S, (my - ry) * S, (mx + rx) * S, (my + ry) * S], radius=14 * S,
                                outline=YELLOW + (round(240 * (1 - 0.5 * ramp(t, 3.4, 3.9))),), width=6 * S)
        # the check after the third pledge's last word
        if t >= 5.55:
            ex, ey = P(end3[2] + 40, (end3[1] + end3[3]) / 2)
            check(d, min(ex, W - 60), ey, 40 * pop(t, 5.55))
        im.alpha_composite(down(top))
        # the sticky note with the misquote: slapped on, crossed out, then pulled away
        s_in, s_out = pop(t, 2.0, 0.28), ramp(t, 3.5, 3.85)
        if s_in > 0.01 and s_out < 1:
            nt = note.copy()
            dn = ImageDraw.Draw(nt)
            for (p0, p1), (a, b) in ((((26, 46), (494, 176)), (2.72, 2.88)), (((494, 46), (26, 176)), (2.88, 3.04))):
                u = ramp(t, a, b)
                if u > 0:
                    q = (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)
                    dn.line([(p0[0] * S, p0[1] * S), (q[0] * S, q[1] * S)], fill=RED + (240,), width=16 * S)
            nt = nt.rotate(-4 + 10 * s_out, resample=Image.BICUBIC, expand=True)
            sc_ = s_in * (1 - 0.15 * s_out)
            nt = nt.resize((max(1, round(nt.width * sc_ / S)), max(1, round(nt.height * sc_ / S))), Image.LANCZOS)
            nx, ny = 540 + 300 * s_out, 680 - 260 * s_out
            sh = Image.new("RGBA", nt.size, (0, 0, 0, 0))
            sh.putalpha(nt.getchannel("A").point(lambda v: v * 0.5))
            im.alpha_composite(fade(sh.filter(ImageFilter.GaussianBlur(10)), 1 - s_out), (round(nx - nt.width / 2 + 8), round(ny - nt.height / 2 + 14)))
            im.alpha_composite(fade(nt, 1 - s_out), (round(nx - nt.width / 2), round(ny - nt.height / 2)))
        out.append(im)
    return out


OUT = {k: f"clips/skema_{k}.mp4" for k in N}

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != FONTS]
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
