"""VO trim, image prep, schematic animations and the cover for Titik Heran #83 (run in the episode work dir; needs
../geo/ne_10m_land.geojson and ../geo/ne_10m_rivers_lake_centerlines.geojson from Natural Earth).
vocut: the naskah's optional words "tua" (sentence 2) and "pun" (sentence 4) cut out of the one Akram v4 take
  (vo83.mp3 -> vo83c.wav, w83_raw.json -> w83.json with the later words shifted), each cut from the silence before
  the word to the level dip where the next word starts, with 10 ms crossfades.
prep: img/H4k.jpg (Arif's Higgsfield H4 cropped on the rattan cane and the letter, used on "dicambuk"), img/H2k.jpg
  (H2 cropped on the empty throne, used on "sultan terkesan").
peta: East Kalimantan (225 px per degree, north up): the Mahakam, Tenggarong (seat of the Kutai sultanate) and Paser
  (Paser Belengkong) to the south, which pulses on "Paser".
kartu: old paper source card: "KISAH DARI BUKU / The Head-Hunters of Borneo / Carl Bock, London 1881 / diulas Alfred
  Russel Wallace / di jurnal Nature, 3 Nov 1881", red stamp "TAK PERCAYA" on "percaya" (Wallace: Bock "disbelieved
  the whole story").
balik: the same map: a letter flies Kutai -> Paser, a red cross and "diusir, diancam dicambuk" at Paser on "diusir",
  a dashed line back to Kutai on "pulang", pill "0 manusia berekor" on "kosong" (Wallace: "had not been able to
  procure any tailed men").
reveal: H5 with labels: a bracket over the file of attendants "ORANG BUNTUT" on "buntut", "= pengiring pribadi"
  under it on "pengiring", and "SULTAN" on "sultan" (Wallace: "the Sultan's personal attendants are known by the
  term 'Orang-boentoet di Sultan di Passir'").
cover: img/cover83.jpg from H4 with the title "KUTAI PERNAH MENJEMPUT / MANUSIA BEREKOR" and a small "ilustrasi" tag.
Event times are seconds from the start of each clip, read off `render.py 83 plan`. Text stays out of the watermark
band (y 935-985), the title zone (y < ~620) and the captions (y >= 1210).
usage: python3 skema83.py [vocut|prep|peta|kartu|balik|reveal|cover ...] [--sheet out.jpg t1,t2,...]
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed, text_sprite
from skema35 import sheet
from skema37 import to_img, put1, noise
from skema46 import pill, ease, wanted
from skema68 import pulse
from skema74 import backdrop

XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
WHITE, GREY, RED, INK = (255, 255, 255), (205, 198, 185), (214, 40, 36), (52, 36, 22)
N = {"peta": 48, "kartu": 66, "balik": 96, "reveal": 99}
# from `render.py 83 plan` (after vocut): see the shot list in the naskah
T_PASER = 0.42                                   # peta: "Paser..."
T_PERCAYA = 1.12                                 # kartu: "percaya,"
T_DIUSIR, T_PULANG, T_KOSONG = 0.92, 1.76, 2.37  # balik
T_BUNTUT, T_PENGIRING, T_SULTAN = 0.33, 1.56, 2.29  # reveal
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
CUTS = [("tua", 8.62, 8.82), ("pun", 20.69, 20.965)]   # word, cut from, cut to (seconds in vo83.mp3)


# ---------- vocut ----------
def vocut():
    sr, xf = 44100, 441
    x = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", "vo83.mp3", "-ac", "1", "-ar", str(sr),
                                               "-f", "f32le", "-"]), np.float32)
    ramp_ = np.linspace(0, 1, xf, dtype=np.float32)
    y, last = None, 0
    for _, c0, c1 in CUTS + [(None, len(x) / sr, None)]:
        p = x[last:int(c0 * sr)]
        y = p if y is None else np.concatenate([y[:-xf], y[-xf:] * (1 - ramp_) + p[:xf] * ramp_, p[xf:]])
        last = int(c1 * sr) if c1 else 0
    with wave.open("vo83c.wav", "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
        f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    words = json.load(open("w83_raw.json"))["words"]
    out = []
    for w in words:
        drop = any(w["text"].strip(",.").lower() == name and c0 <= w["start"] <= c1 for name, c0, c1 in CUTS)
        if drop:
            continue
        # a kept word that starts after a cut's start lies after that cut (it may start a few ms before c1)
        after = [(c0, c1) for _, c0, c1 in CUTS if w["start"] >= c0]
        d = sum(c1 - c0 + xf / sr for c0, c1 in after)
        joint = after[-1][0] - (d - (after[-1][1] - after[-1][0] + xf / sr)) if after else 0
        out.append(dict(w, start=round(max(w["start"] - d, joint), 3), end=round(w["end"] - d, 3)))
    json.dump({"words": out}, open("w83.json", "w"))
    print(f"vo83c.wav {len(y) / sr:.2f}s, w83.json {len(out)} words (dropped {len(words) - len(out)})")


# ---------- prep ----------
def prep():
    Image.open("img/H4.jpg").crop((90, 330, 1035, 2010)).resize((1080, 1920), Image.LANCZOS).save("img/H4k.jpg", quality=95)
    Image.open("img/H2.jpg").crop((330, 700, 1260, 2353)).resize((1080, 1920), Image.LANCZOS).save("img/H2k.jpg", quality=95)
    print("img/H4k.jpg img/H2k.jpg")


# ---------- map ----------
K, LON0, LAT0, Y0 = 225.0, 114.6, -0.42, 760    # Tenggarong's latitude sits at y 760
TENGGARONG, PASER = (116.99, -0.42), (116.17, -1.87)


def xy(lon, lat):
    return ((lon - LON0) * K, Y0 + (LAT0 - lat) * K)


def finish(im, top=620):
    a = np.asarray(im, np.float32)
    tex = noise((H, W), [(40, 0.6), (9, 0.4)], 83)[..., None]
    a[..., :3] *= 0.92 + 0.16 * tex
    shade = np.clip(np.maximum((top - YY) / 380, (YY - 1180) / 260), 0, 1)[..., None] * 0.8
    a[..., :3] *= 1 - shade
    return to_img(a).convert("RGBA")


def map_base():
    v = (YY / H)[..., None]
    sea = np.array((12, 44, 72), np.float32) * (1 - v) + np.array((8, 30, 54), np.float32) * v
    base = Image.fromarray(sea.astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(lay)
    for f in json.load(open("../geo/ne_10m_land.geojson"))["features"]:
        g = f["geometry"]
        for p in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            ring = p[0]
            xs, ys = [q[0] for q in ring], [q[1] for q in ring]
            if max(xs) < 112 or min(xs) > 121 or max(ys) < -6 or min(ys) > 4:
                continue
            d.polygon([(xy(*q)[0] * S, xy(*q)[1] * S) for q in ring], fill=(74, 96, 60, 255), outline=(150, 176, 120, 255))
    for f in json.load(open("../geo/ne_10m_rivers_lake_centerlines.geojson"))["features"]:
        if f["properties"].get("name") not in ("Mahakam", "Barito"):
            continue
        g = f["geometry"]
        for line in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
            d.line([(xy(*q)[0] * S, xy(*q)[1] * S) for q in line], fill=(110, 170, 220, 255), width=5 * S, joint="curve")
    base.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    base = finish(base)
    put1(base, text_sprite([("Sungai Mahakam", 34, (170, 210, 240), False)]), *xy(116.35, -0.05))
    put1(base, text_sprite([("Selat Makassar", 36, (150, 190, 220), False)]), *xy(118.35, -1.55))
    return base


def env_icon():
    sp = Image.new("RGBA", (70 * S, 50 * S))
    d = ImageDraw.Draw(sp)
    d.rectangle([4 * S, 6 * S, 66 * S, 46 * S], fill=(250, 244, 225, 255), outline=(60, 40, 20, 255), width=2 * S)
    d.line([(4 * S, 6 * S), (35 * S, 30 * S), (66 * S, 6 * S)], fill=(60, 40, 20, 255), width=2 * S)
    d.rectangle([28 * S, 26 * S, 42 * S, 36 * S], fill=YELLOW + (255,))
    return sp


def kutai_dot(im, t=1.0):
    x, y = xy(*TENGGARONG)
    d = ImageDraw.Draw(im)
    d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=YELLOW + (255,), outline=WHITE + (255,), width=3)
    put1(im, label([("KUTAI", 54, YELLOW, True), ("Tenggarong", 32, WHITE, False)]), x - 165, y - 8)


def label(lines):
    return text_sprite(lines, gap=4)


def skema_peta(times=None):
    base = map_base()
    kutai_dot(base)
    pas = label([("PASER", 58, WHITE, True)])
    frames = []
    for i in range(N["peta"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        x, y = xy(*PASER)
        pulse(im, x, y, (255, 80, 60), t, T_PASER - 0.05)
        k = pop(t, T_PASER)
        if k > 0:
            put1(im, pas, x - 150, y + 4, a=min(1, k), scale=min(k, 1.05))
        frames.append(im.convert("RGB"))
    return frames


def skema_balik(times=None):
    base = map_base()
    kutai_dot(base)
    x0, y0 = xy(*TENGGARONG)
    x1, y1 = xy(*PASER)
    route = [(x0 + 4, y0 + 14), (x0 + 120, y0 + 140), (x1 + 120, y1 - 40), (x1 + 10, y1 - 8)]   # down the coast
    back = [(x1 - 14, y1 - 10), (x1 - 60, y1 - 160), (x0 - 50, y0 + 130), (x0 - 6, y0 + 16)]
    env = env_icon()
    pas = label([("PASER", 58, WHITE, True)])
    usir = pill("diusir, diancam dicambuk", 30, WHITE, RED + (235,), (255, 255, 255, 200))
    nol = pill("0 manusia berekor", 36, (20, 20, 20), YELLOW + (245,), (255, 255, 255, 200))

    def along(pts, u):
        seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
        L, acc = sum(seg) * u, 0.0
        for (a, b), s in zip(zip(pts, pts[1:]), seg):
            if acc + s >= L:
                f = (L - acc) / s
                return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
            acc += s
        return pts[-1]
    frames = []
    for i in range(N["balik"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = base.copy()
        put1(im, pas, x1 - 150, y1 + 4)
        L = Image.new("RGBA", (W * S, H * S))
        dl = ImageDraw.Draw(L)
        u = ease(t / 0.75)
        dashed(dl, route, YELLOW + (230,), 5, dash=18, gap=12, upto=u * sum(math.dist(a, b) for a, b in zip(route, route[1:])))
        if t > T_PULANG:
            v = ease((t - T_PULANG) / 0.55)
            dashed(dl, back, (235, 235, 235, 220), 5, dash=12, gap=12, upto=v * sum(math.dist(a, b) for a, b in zip(back, back[1:])))
        im.alpha_composite(L.resize((W, H), Image.LANCZOS))
        if t < T_DIUSIR + 0.1:
            ex, ey = along(route, u)
            put1(im, env, ex, ey, a=1 - ramp(t, T_DIUSIR - 0.05, T_DIUSIR + 0.1))
        k = pop(t, T_DIUSIR, 0.25)
        if k > 0:
            d = ImageDraw.Draw(im)
            r = 30 * min(k, 1.1)
            for s in (1, -1):
                d.line([(x1 - r, y1 - s * r), (x1 + r, y1 + s * r)], fill=RED + (255,), width=10)
            put1(im, usir, 520, y1 + 86, a=min(1, k), scale=min(k, 1.05))
        if t > T_PULANG + 0.4:
            bx, by = along(back, ease((t - T_PULANG) / 0.55))
            d = ImageDraw.Draw(im)
            d.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=WHITE + (255,))
        kn = pop(t, T_KOSONG)
        if kn > 0:
            put1(im, nol, x0 + 290, y0 + 30, a=min(1, kn), scale=min(kn, 1.05))
        frames.append(im.convert("RGB"))
    return frames


# ---------- kartu ----------
def paper_card(w=880, h=500):
    rng = np.random.default_rng(1881)
    a = np.ones((h, w, 3), np.float32) * np.array([232, 216, 182], np.float32)
    a *= (0.9 + 0.1 * noise((h, w), [(30, 0.6), (6, 0.4)], 5))[..., None]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    edge = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
    a *= (0.78 + 0.22 * np.clip(edge / 40, 0, 1))[..., None]
    a += rng.normal(0, 3, (h, w, 1)).astype(np.float32)
    im = to_img(a).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle([14, 14, w - 15, h - 15], outline=(120, 90, 50, 255), width=2)
    return im


def text_center(im, y, text, size, col, font=XB):
    f = ImageFont.truetype(font, size)
    d = ImageDraw.Draw(im)
    b = f.getbbox(text)
    d.text(((im.width - (b[2] - b[0])) / 2 - b[0], y - (b[3] - b[1]) / 2 - b[1]), text, font=f, fill=col + (255,))


def stamp(text, size=52, col=RED, ang=-12):
    f = ImageFont.truetype(XB, size * S)
    b = f.getbbox(text)
    w, h = b[2] - b[0] + 60 * S, b[3] - b[1] + 40 * S
    sp = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle([4 * S, 4 * S, w - 4 * S, h - 4 * S], radius=12 * S, outline=col + (235,), width=6 * S)
    d.text((30 * S - b[0], 20 * S - b[1]), text, font=f, fill=col + (235,))
    return sp.rotate(ang, expand=True, resample=Image.BICUBIC)


def skema_kartu(times=None):
    bg = finish(backdrop((54, 36, 22), (16, 10, 6), glow=(30, 20, 8), gy=920))
    card = paper_card()
    # card top at y 670: lines sit at absolute y 712, 778, 840, 898 | (watermark band) | 1028, 1074
    text_center(card, 42, "KISAH DARI BUKU", 26, (120, 90, 50), MED)
    text_center(card, 108, "The Head-Hunters", 56, INK)
    text_center(card, 170, "of Borneo", 56, INK)
    text_center(card, 228, "Carl Bock · London, 1881", 32, (90, 66, 40), MED)
    text_center(card, 358, "diulas Alfred Russel Wallace", 32, (90, 66, 40), MED)
    text_center(card, 404, "di jurnal Nature, 3 Nov 1881", 32, (90, 66, 40), MED)
    sp = card.resize((card.width * S, card.height * S), Image.LANCZOS)
    st = stamp("TAK PERCAYA", 38, ang=-6)
    frames = []
    for i in range(N["kartu"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        k = min(pop(t, 0.0, 0.35), 1.04)
        put1(im, sp, 540, 920, a=min(1, k * 1.5), scale=k)
        ks = pop(t, T_PERCAYA, 0.22)
        if ks > 0:
            put1(im, st, 835, 963, a=min(1, ks), scale=1.6 - 0.6 * min(ks, 1))
        frames.append(im.convert("RGB"))
    return frames


# ---------- reveal ----------
def skema_reveal(times=None):
    src = Image.open("img/H5.jpg").convert("RGB").resize((W, H), Image.LANCZOS)
    a = np.asarray(src, np.float32) * np.array([1.04, 1.0, 0.94], np.float32)   # the warm grade of the other shots
    src = to_img(a)
    tag_b = pill("ORANG BUNTUT", 40, (20, 20, 20), YELLOW + (245,), (255, 255, 255, 220))
    tag_p = pill("= pengiring pribadi", 30, WHITE, (10, 14, 24, 220))
    tag_s = pill("SULTAN", 34, WHITE, (10, 14, 24, 220), (255, 225, 0, 220))
    BX0, BX1, BY = 600, 1050, 790
    frames = []
    for i in range(N["reveal"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        z = 1.12 + 0.05 * t / (N["reveal"] / FPS)       # slow push toward the attendants
        cw, ch = W / z, H / z
        cx, cy = min(W * 0.56, W - cw / 2), min(H * 0.52, H - ch / 2)   # keep the crop inside the image
        im = src.crop((round(cx - cw / 2), round(cy - ch / 2), round(cx + cw / 2), round(cy + ch / 2))).resize((W, H), Image.LANCZOS).convert("RGBA")

        def zp(x, y):
            return (x - (cx - cw / 2)) * z, (y - (cy - ch / 2)) * z
        k = pop(t, T_BUNTUT, 0.3)
        if k > 0:
            L = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(L)
            (ax, ay), (bx, by) = zp(BX0, BY), zp(BX1, BY)
            u = ease((t - T_BUNTUT) / 0.3)
            mx = ax + (bx - ax) * u
            d.line([(ax * S, (ay + 26) * S), (ax * S, ay * S), (mx * S, ay * S)] + ([(bx * S, (by + 26) * S)] if u >= 1 else []),
                   fill=YELLOW + (255,), width=7 * S, joint="curve")
            im.alpha_composite(L.resize((W, H), Image.LANCZOS))
            put1(im, tag_b, (ax + bx) / 2, ay - 52, a=min(1, k), scale=min(k, 1.05))
        kp = pop(t, T_PENGIRING, 0.3)
        if kp > 0:
            (ax, ay), (bx, by) = zp(BX0, BY), zp(BX1, BY)
            put1(im, tag_p, (ax + bx) / 2, ay + 70, a=min(1, kp), scale=min(kp, 1.05))
        ks = pop(t, T_SULTAN, 0.3)
        if ks > 0:
            sx, sy = zp(440, 1060)
            d = ImageDraw.Draw(im)
            d.line([(sx - 170, sy + 6), (sx - 20, sy - 30)], fill=(255, 225, 0, int(230 * min(1, ks))), width=4)
            put1(im, tag_s, sx - 230, sy + 20, a=min(1, ks), scale=min(ks, 1.05))
        frames.append(im.convert("RGB"))
    return frames


# ---------- cover ----------
def cover():
    im = Image.open("img/H4.jpg").convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")
    a = np.asarray(im, np.float32)
    a[..., :3] *= 1 - np.clip((780 - YY) / 520, 0, 1)[..., None] * 0.5
    im = to_img(a).convert("RGBA")
    t = text_sprite([("KUTAI PERNAH MENJEMPUT", 66, WHITE, True), ("MANUSIA", 120, YELLOW, True), ("BEREKOR", 120, YELLOW, True)], gap=8)
    put1(im, t, 540, 440)
    put1(im, pill("ilustrasi", 24, WHITE), 960, 1860)
    im.convert("RGB").save("img/cover83.jpg", quality=93)
    print("img/cover83.jpg")


if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or ["prep", "peta", "kartu", "balik", "reveal", "cover"]
    fns = {"peta": skema_peta, "kartu": skema_kartu, "balik": skema_balik, "reveal": skema_reveal}
    for name in todo:
        if name in ("vocut", "prep", "cover"):
            {"vocut": vocut, "prep": prep, "cover": cover}[name]()
            continue
        fr = fns[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, f"clips/skema_{name}.mp4")
