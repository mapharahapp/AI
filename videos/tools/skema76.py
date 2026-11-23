"""Schematic animations for Titik Heran #76 (run in the episode work dir; writes clips/skema_numpang.mp4,
skema_prasasti.mp4, skema_karbon.mp4, skema_tulang.mp4). Nothing here is the real Westminster coffin: plain line art.
numpang: outline of a stone coffin with a lid; on its front the name VALERIUS AMANDINUS + "abad ke-4"; on "orang" a
  red line strikes the name, on "lain" a yellow tag "???" pops in, on "numpang" a yellow stamp NUMPANG slams down.
prasasti: cream stone card, the translated inscription (Live Science / Medievalists): "untuk mengenang VALERIUS
  AMANDINUS", "dibuat kedua putranya untuk ayah mereka", pill "orang kaya Romawi - abad ke-4 M".
karbon: "uji karbon (radiokarbon)"; a year counter rolls up and lands on 987-1052 M (95,4%, Medievalists.net,
  ScienceDaily), "wafat +-tahun 1000"; on "ratusan" the counter slides right and a timeline grows from "+-300-400 M,
  peti dibuat" to it, pill "+-600-700 TAHUN".
tulang: a plain line-drawn body (no bones, no skull); small blue dots at the spine, shoulder and wrist "radang sendi",
  then on "asam" an orange dot pulses at the big toe, "asam urat? (kemungkinan)" (the report: possible gout).
Event times are seconds from the start of each clip, read off `render.py 76 plan`. Text stays out of the watermark
band (y 935-985), the title zone (y < ~650) and the captions (y >= 1210).
usage: python3 skema76.py [numpang|prasasti|karbon|tulang ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, text_sprite
from skema35 import sheet
from skema37 import put1
from skema46 import pill, ease, wanted
from skema74 import backdrop

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
WHITE, RED, ORANGE, BLUE = (255, 255, 255), (222, 36, 32), (255, 140, 30), (90, 190, 255)
N = {"numpang": 96, "prasasti": 60, "karbon": 138, "tulang": 72}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# from `render.py 76 plan`: numpang = shot 03 ("tapi" 0.03, "isinya" 0.72, "orang" 1.33, "lain" 1.56, "numpang" 1.98,
# cut 2.90); prasasti = shot 05 ("Valerius" 0.04, "Amandinus" 0.65, cut 1.77); karbon = shot 08 ("Uji" 0.04,
# "membuktikan" 0.63, "dia" 1.56, "seribu" 2.82, "ratusan" 3.55, "tahun" 4.05, cut 4.40); tulang = shot 11 ("yang"
# 0.03, "kemungkinan" 0.18, "kena" 0.95, "asam" 1.17, "urat" 1.60, cut 2.20)
T = {"box": 0.0, "name": 0.15, "strike": 1.33, "q": 1.56, "stamp": 1.98,
     "card": 0.0, "p1": 0.08, "p2": 0.22, "p3": 0.55, "p4": 0.85,
     "uji": 0.05, "roll0": 0.55, "roll1": 2.80, "wafat": 2.95, "move": 3.50, "line": 3.62, "bracket": 3.95,
     "body": 0.0, "joints": 0.25, "toe": 1.15}


def stone_bg():
    return backdrop((44, 40, 36), (10, 9, 8), glow=(40, 34, 26), gy=820)


def lay2():
    return Image.new("RGBA", (W * S, H * S))


def flat(lay):
    return lay.resize((W, H), Image.LANCZOS)


# ---------- numpang ----------
def coffin(u, col=(235, 225, 205, 255)):
    """line art of a coffin with a gabled lid; u = how much of it is drawn (0-1)"""
    lay = lay2()
    d = ImageDraw.Draw(lay)
    x0, x1, y0, y1 = 150, 930, 760, 925          # box front
    segs = [[(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)],
            [(x0 - 20, y0), (x0 + 30, 690), (x1 - 30, 690), (x1 + 20, y0)],          # lid
            [(x0 + 30, 690), (x0 + 80, 668), (x1 - 80, 668), (x1 - 30, 690)]]      # gable
    k = max(0.0, min(1.0, u)) * 3
    for n, pts in enumerate(segs):
        f = max(0.0, min(1.0, k - n))
        if f <= 0:
            continue
        L = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
        left, out = L * f, [pts[0]]
        for a, b in zip(pts, pts[1:]):
            seg = math.dist(a, b)
            if left >= seg:
                out.append(b); left -= seg
            else:
                out.append((a[0] + (b[0] - a[0]) * left / seg, a[1] + (b[1] - a[1]) * left / seg)); break
        d.line([(x * S, y * S) for x, y in out], fill=col, width=6 * S, joint="curve")
    return flat(lay)


def name_lay():
    lay = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(lay)
    d.text((540, 815), "VALERIUS AMANDINUS", font=ImageFont.truetype(XB, 58), fill=(240, 232, 214, 255), anchor="mm")
    d.text((540, 885), "abad ke-4", font=ImageFont.truetype(MED, 32), fill=(200, 190, 170, 255), anchor="mm")
    return lay


def stamp_sprite(text="NUMPANG"):
    f = ImageFont.truetype(XB, 104 * S)
    x0, y0, x1, y1 = f.getbbox(text)
    pad = 28 * S
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    st = Image.new("RGBA", (w + 40 * S, h + 40 * S))
    d = ImageDraw.Draw(st)
    d.rounded_rectangle([20 * S, 20 * S, 20 * S + w, 20 * S + h], radius=18 * S, outline=YELLOW + (255,), width=10 * S)
    d.text((20 * S + pad - x0, 20 * S + pad - y0), text, font=f, fill=YELLOW + (255,))
    rng = np.random.default_rng(7)
    a = np.asarray(st.getchannel("A"), np.float32)
    holes = rng.random(a.shape) < 0.02
    holes = np.asarray(Image.fromarray((holes * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) > 0
    st.putalpha(Image.fromarray(np.where(holes, a * 0.55, a).astype(np.uint8)))
    return st.rotate(8, expand=True, resample=Image.BICUBIC)


def skema_numpang(times=None):
    bg, nm, stp = stone_bg(), name_lay(), stamp_sprite()
    q = pill("???", 60, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230), pad=(34, 10))
    frames = []
    for i in range(N["numpang"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        im.alpha_composite(coffin(ease(t / 0.45)))
        a = ramp(t, T["name"], T["name"] + 0.2)
        if a > 0:
            n2 = nm.copy(); n2.putalpha(n2.getchannel("A").point(lambda v, a=a: int(v * a)))
            im.alpha_composite(n2)
        u = ease((t - T["strike"]) / 0.2)
        if u > 0:
            lay = lay2()
            ImageDraw.Draw(lay).line([(240 * S, 818 * S), ((240 + 600 * u) * S, 812 * S)], fill=RED + (255,), width=10 * S)
            im.alpha_composite(flat(lay))
        put1(im, q, 540, 718, scale=min(pop(t, T["q"], 0.3), 1.05))
        dt = t - T["stamp"]
        if dt > 0:
            k = min(dt / 0.12, 1.0)
            put1(im, stp, 540, 1090, a=min(1.0, 0.4 + k), scale=2.0 - 1.0 * k * k)
        frames.append(im.convert("RGB"))
    return frames


# ---------- prasasti ----------
def skema_prasasti(times=None):
    bg = stone_bg()
    cw, ch, cx0, cy0 = 900, 520, 90, 676
    card = Image.new("RGBA", (cw * S, ch * S))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, cw * S - 1, ch * S - 1], radius=22 * S, fill=(238, 228, 205, 255))
    noise = (np.random.default_rng(3).random((ch * S, cw * S)) * 18).astype(np.uint8)
    grain = Image.fromarray(noise).convert("L")
    card = Image.composite(Image.new("RGBA", card.size, (200, 188, 160, 255)), card, grain.point(lambda v: v * 4))
    card.putalpha(Image.new("L", card.size, 0))
    m = Image.new("L", card.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, cw * S - 1, ch * S - 1], radius=22 * S, fill=255)
    card.putalpha(m)
    # text rows, in card coordinates; card y 259-309 = watermark band, kept empty
    rows = [("terjemahan tulisan di peti:", MED, 30, (120, 60, 40), 46, "p1"),
            ("\"Untuk mengenang", MED, 44, (50, 40, 30), 110, "p1"),
            ("VALERIUS AMANDINUS\"", XB, 70, (30, 24, 18), 186, "p2"),
            ("dibuat kedua putranya untuk ayah mereka", MED, 34, (60, 50, 40), 362, "p3")]
    sprites = []
    for text, font, size, col, y, key in rows:
        lay = Image.new("RGBA", (cw * S, ch * S))
        ImageDraw.Draw(lay).text((cw * S / 2, y * S), text, font=ImageFont.truetype(font, size * S), fill=col + (255,), anchor="mm")
        sprites.append((lay, key))
    pl = pill("orang kaya Romawi · abad ke-4 M", 36, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230))
    frames = []
    for i in range(N["prasasti"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        c = card.copy()
        for lay, key in sprites:
            a = ramp(t, T[key], T[key] + 0.15)
            if a > 0:
                l2 = lay.copy(); l2.putalpha(l2.getchannel("A").point(lambda v, a=a: int(v * a)))
                c.alpha_composite(l2)
        c = c.resize((cw, ch), Image.LANCZOS)
        im = bg.copy()
        y = cy0 + 700 * (1 - ease(t / 0.28))
        sh = Image.new("RGBA", (W, H))
        ImageDraw.Draw(sh).rounded_rectangle([cx0 + 10, y + 18, cx0 + cw + 10, y + ch + 18], radius=22, fill=(0, 0, 0, 130))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
        im.alpha_composite(c, (cx0, round(y)))
        put1(im, pl, 540, round(y) + 458, scale=min(pop(t, T["p4"], 0.3), 1.05))
        frames.append(im.convert("RGB"))
    return frames


# ---------- karbon ----------
def year_sprite(text, size=118, col=YELLOW):
    return text_sprite([(text, size, col, True)])


def skema_karbon(times=None):
    bg = backdrop((18, 26, 40), (5, 7, 12), glow=(18, 30, 50), gy=820)
    up = pill("uji karbon (radiokarbon)", 36, col=WHITE, bg=(10, 14, 24, 215), edge=(255, 255, 255, 150))
    final = year_sprite("987–1052 M")
    wafat = text_sprite([("wafat ±tahun 1000", 38, WHITE, False)])
    left = text_sprite([("±300–400 M", 52, (240, 232, 214), True)])
    lsub = text_sprite([("peti dibuat", 32, (200, 200, 200), False)])
    rsub = text_sprite([("dikubur di peti ini", 32, (200, 200, 200), False)])
    br = pill("±600–700 TAHUN", 46, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230))
    cache = {}
    frames = []
    for i in range(N["karbon"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        mv = ease((t - T["move"]) / 0.3)
        put1(im, up, 540, 700, a=1 - mv, scale=min(pop(t, T["uji"], 0.3), 1.05))
        # the counter: rolls 300 -> 1020 with an ease-out, then lands on the range
        cx, cy, sc = 540 + 250 * mv, 830 - 50 * mv, 1.0 - 0.5 * mv
        if t < T["roll1"]:
            u = ramp(t, T["roll0"], T["roll1"])
            u = 1 - (1 - u) ** 3
            yv = int(300 + 720 * u) if t >= T["roll0"] else 300
            key = f"{yv} M"
            if key not in cache:
                cache[key] = year_sprite(key, col=WHITE)
            put1(im, cache[key], cx, cy, a=ramp(t, T["roll0"] - 0.2, T["roll0"]))
        else:
            put1(im, final, cx, cy, scale=sc * min(pop(t, T["roll1"], 0.3), 1.05))
        put1(im, wafat, 540, 1040, a=ramp(t, T["wafat"], T["wafat"] + 0.15) * (1 - mv))
        if mv > 0:
            put1(im, left, 290, 780, a=mv)
            put1(im, lsub, 290, 832, a=mv)
            put1(im, rsub, 790, 832, a=mv)
            u = ease((t - T["line"]) / 0.3)
            lay = lay2()
            d = ImageDraw.Draw(lay)
            d.line([(290 * S, 900 * S), ((290 + 500 * u) * S, 900 * S)], fill=WHITE + (230,), width=6 * S)
            for x in (290, 790):
                if x == 290 or u > 0.98:
                    d.ellipse([(x - 13) * S, 887 * S, (x + 13) * S, 913 * S], fill=YELLOW + (255,))
            v = ease((t - T["bracket"]) / 0.2)
            if v > 0:
                d.line([(290 * S, 1010 * S), (290 * S, 1030 * S), (790 * S, 1030 * S), (790 * S, 1010 * S)], fill=YELLOW + (int(255 * v),), width=5 * S)
            im.alpha_composite(flat(lay))
            put1(im, br, 540, 1100, scale=min(pop(t, T["bracket"], 0.3), 1.05))
        frames.append(im.convert("RGB"))
    return frames


# ---------- tulang ----------
def body_lay(u):
    """a plain outline body, standing, drawn at 2x; u = draw-in progress"""
    lay = lay2()
    d = ImageDraw.Draw(lay)
    col = (230, 236, 240, int(230 * u))
    w = 6 * S
    cx = 400
    d.ellipse([(cx - 46) * S, 668 * S, (cx + 46) * S, 770 * S], outline=col, width=w)                 # head
    d.line([(cx * S, 770 * S), (cx * S, 790 * S)], fill=col, width=w)                                   # neck
    d.rounded_rectangle([(cx - 82) * S, 790 * S, (cx + 82) * S, 990 * S], radius=40 * S, outline=col, width=w)  # torso
    d.line([((cx - 82) * S, 810 * S), ((cx - 128) * S, 925 * S), ((cx - 140) * S, 1020 * S)], fill=col, width=w, joint="curve")  # arms
    d.line([((cx + 82) * S, 810 * S), ((cx + 128) * S, 925 * S), ((cx + 140) * S, 1020 * S)], fill=col, width=w, joint="curve")
    d.line([((cx - 40) * S, 990 * S), ((cx - 52) * S, 1090 * S), ((cx - 56) * S, 1180 * S)], fill=col, width=w, joint="curve")  # legs
    d.line([((cx + 40) * S, 990 * S), ((cx + 52) * S, 1090 * S), ((cx + 56) * S, 1180 * S)], fill=col, width=w, joint="curve")
    d.line([((cx - 56) * S, 1180 * S), ((cx - 100) * S, 1188 * S)], fill=col, width=w)                 # feet
    d.line([((cx + 56) * S, 1180 * S), ((cx + 100) * S, 1188 * S)], fill=col, width=w)
    return flat(lay)


def dot(im, x, y, r, col, a=1.0, glow=0.0):
    lay = lay2()
    d = ImageDraw.Draw(lay)
    if glow > 0:
        g = Image.new("RGBA", (W * S, H * S))
        ImageDraw.Draw(g).ellipse([(x - r * 2.6) * S, (y - r * 2.6) * S, (x + r * 2.6) * S, (y + r * 2.6) * S], fill=col + (int(150 * glow * a),))
        lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(10 * S)))
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=col + (int(255 * a),))
    im.alpha_composite(flat(lay))


def skema_tulang(times=None):
    bg = backdrop((22, 26, 34), (6, 7, 10), glow=(20, 28, 40), gy=880)
    rs = text_sprite([("radang sendi", 36, BLUE, True)])
    au = text_sprite([("asam urat?", 50, ORANGE, True), ("(kemungkinan)", 32, (235, 210, 180), False)])
    frames = []
    for i in range(N["tulang"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        im.alpha_composite(body_lay(ease(t / 0.3)))
        a = ramp(t, T["joints"], T["joints"] + 0.15)
        if a > 0:
            for x, y in ((400, 840), (318, 810), (260, 1020), (540, 1020), (400, 900)):   # shoulders, wrists, spine
                dot(im, x, y, 11, BLUE, a)
            put1(im, rs, 690, 745, a=a)
            lay = lay2()
            ImageDraw.Draw(lay).line([(560 * S, 760 * S), (490 * S, 820 * S)], fill=BLUE + (int(200 * a),), width=3 * S)
            im.alpha_composite(flat(lay))
        b = ramp(t, T["toe"], T["toe"] + 0.12)
        if b > 0:
            pulse = 0.6 + 0.4 * math.sin((t - T["toe"]) * 9)
            dot(im, 500, 1186, 15 + 4 * pulse, ORANGE, b, glow=pulse)
            put1(im, au, 750, 1110, a=b)
            lay = lay2()
            ImageDraw.Draw(lay).line([(640 * S, 1130 * S), (525 * S, 1180 * S)], fill=ORANGE + (int(220 * b),), width=3 * S)
            im.alpha_composite(flat(lay))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"numpang": skema_numpang, "prasasti": skema_prasasti, "karbon": skema_karbon, "tulang": skema_tulang}

if __name__ == "__main__":
    args = sys.argv[1:]
    out, TIMES = None, None
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
