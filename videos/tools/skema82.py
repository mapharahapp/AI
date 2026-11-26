"""Image prep, schematic animations and the cover for Titik Heran #82 (run in the episode work dir).
prep: clips/191150f.mp4 (Pixabay 191150 cropped on the flames, the wall and a cardboard box pushed into shadow),
  img/H1k.jpg (Arif's Higgsfield H1 cropped on the bronze knife and the red-ink serpent, used on "diinjak ...
  diludahi"), img/H2c.jpg (H2 without its bottom rows: one fragment there carries marks that read like Latin letters).
garis_waktu: timeline on dark parchment: left dot "+-3.400 TAHUN LALU / 40 serpihan kutukan / dari kuil Thutmose III",
  a line drawn to the right with the pill "+-1.000 TAHUN", right dot "1.000 TAHUN KEMUDIAN / satu-satunya buku panduan
  ritual / (Papirus Bremner-Rhind)". The manual gets no BC date (press release: late 4th c. BC, paper: 3rd c.).
jarak: Earth to scale (150 px per Earth radius, centre off the left edge), the ring of geosynchronous satellites at
  +-36.000 km (35.786 km) above the surface, and Apophis on 13 April 2029 passing +-32.000 km above the surface (NASA:
  "within 20,000 miles"), inside the ring; pill "NASA: tidak ada risiko tabrakan (setidaknya 100 tahun)".
cover: img/cover82.jpg from H1 with the title "KUTUKAN / MESIR KUNO / UNTUK ULAR RAKSASA" and a small "ilustrasi" tag.
Event times are seconds from the start of each clip, read off `render.py 82 plan`. Text stays out of the watermark
band (y 935-985), the title zone (y < ~620) and the captions (y >= 1210).
usage: python3 skema82.py [prep|garis_waktu|jarak|cover ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode, dashed, text_sprite
from skema35 import sheet
from skema37 import to_img, put1, noise
from skema46 import pill, ease, wanted
from skema74 import backdrop

WHITE, GREY, RED = (255, 255, 255), (205, 198, 185), (225, 50, 40)
N = {"garis_waktu": 81, "jarak": 72}
# from `render.py 82 plan`: garis_waktu = shot 11 ("seribu" 0.05, "tahun" 0.35, "lebih" 0.54, "tua" 0.80, "dari" 1.11,
# "catatan" 1.33, "dikenal!" 1.75, cut 2.60); jarak = shot 14 ("lewat" 0.03, "lebih" 0.34, "dekat" 0.56, "dari" 1.01,
# "banyak" 1.32, "satelit!" 1.73, cut 2.30)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def label(lines):
    return text_sprite(lines, gap=6)


def finish(im, top=640):
    """paper grain plus dark bands under the titles and the captions"""
    a = np.asarray(im, np.float32)
    tex = noise((H, W), [(40, 0.6), (9, 0.4)], 82)[..., None]
    a[..., :3] *= 0.92 + 0.16 * tex
    shade = np.clip(np.maximum((top - YY) / 380, (YY - 1180) / 260), 0, 1)[..., None] * 0.75
    a[..., :3] *= 1 - shade
    return to_img(a).convert("RGBA")


# ---------- prep ----------
def prep():
    # the fire clip cropped on the flames, its wall and the cardboard box below them pushed into shadow
    import subprocess
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "clips/191150.mp4", "-vf",
                    "crop=675:1200:0:150,scale=1080:1920:flags=lanczos,curves=all='0/0 0.5/0.24 1/1'",
                    "-an", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "clips/191150f.mp4"], check=True)
    Image.open("img/H1.jpg").crop((270, 600, 1170, 2200)).resize((1080, 1920), Image.LANCZOS).save("img/H1k.jpg", quality=95)
    Image.open("img/H2.jpg").crop((180, 0, 1260, 1920)).save("img/H2c.jpg", quality=95)
    print("clips/191150f.mp4 img/H1k.jpg img/H2c.jpg")


# ---------- garis_waktu ----------
def fragments(n=7, seed=3):
    """a small heap of charred papyrus scraps with puncture holes, 2x sprite"""
    rng = np.random.default_rng(seed)
    sp = Image.new("RGBA", (200 * S, 130 * S))
    d = ImageDraw.Draw(sp)
    for k in range(n):
        cx, cy = 30 + (k % 4) * 46 + rng.uniform(-6, 6), 34 + (k // 4) * 58 + rng.uniform(-6, 6)
        w, h = rng.uniform(26, 36), rng.uniform(36, 48)
        ang = rng.uniform(-0.35, 0.35)
        pts = []
        for j in range(9):
            th = 2 * math.pi * j / 9
            r = 1 + rng.uniform(-0.12, 0.08)
            x, y = w / 2 * math.cos(th) * r, h / 2 * math.sin(th) * r
            pts.append(((cx + x * math.cos(ang) - y * math.sin(ang)) * S, (cy + x * math.sin(ang) + y * math.cos(ang)) * S))
        d.polygon(pts, fill=(196, 150, 96, 255), outline=(40, 22, 10, 255), width=3 * S)
        d.ellipse([(cx - 4) * S, (cy - 12) * S, (cx + 4) * S, (cy - 4) * S], fill=(20, 12, 8, 255))
        d.line([((cx - 9) * S, (cy + 6) * S), ((cx + 8) * S, (cy + 6) * S)], fill=(180, 40, 30, 255), width=3 * S)
    return sp


def scroll():
    """a rolled papyrus scroll, 2x sprite"""
    sp = Image.new("RGBA", (220 * S, 120 * S))
    d = ImageDraw.Draw(sp)
    d.rectangle([30 * S, 20 * S, 190 * S, 100 * S], fill=(214, 182, 128, 255), outline=(70, 46, 22, 255), width=3 * S)
    for x in (30, 190):
        d.rounded_rectangle([(x - 14) * S, 12 * S, (x + 14) * S, 108 * S], radius=12 * S, fill=(176, 138, 84, 255),
                            outline=(70, 46, 22, 255), width=3 * S)
    for k, y in enumerate((38, 54, 70, 86)):
        d.line([(52 * S, y * S), ((168 - 18 * (k % 2)) * S, y * S)], fill=(180, 40, 30, 255) if k == 0 else (40, 30, 20, 255),
               width=4 * S)
    return sp


def skema_garis_waktu(times=None):
    bg = finish(backdrop((58, 44, 30), (16, 12, 9), glow=(34, 24, 10), gy=900))
    AX0, AX1, AY = 110, 970, 1075
    XL, XR = 280, 810
    lab_l = label([("±3.400 TAHUN LALU", 46, YELLOW, True), ("40 serpihan kutukan", 38, WHITE, False),
                   ("kuil Thutmose III", 32, GREY, False)])
    lab_r = label([("1.000 TAHUN KEMUDIAN", 38, WHITE, True), ("satu-satunya buku", 38, WHITE, False),
                   ("panduan yang dikenal", 38, WHITE, False)])
    gap = pill("± 1.000 TAHUN", 40, (20, 20, 20), YELLOW + (245,), (255, 255, 255, 200))
    frag, scr = fragments(), scroll()
    frames = []
    for i in range(N["garis_waktu"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        L = Image.new("RGBA", (W * S, H * S))
        d = ImageDraw.Draw(L)
        u = ease(t / 0.3)
        d.line([(AX0 * S, AY * S), ((AX0 + (AX1 - AX0) * u) * S, AY * S)], fill=(150, 132, 104, 255), width=5 * S)
        v = ease((t - 0.25) / 0.85)
        if v > 0:   # the stretch between the two records lights up, left to right
            x1 = XL + (XR - XL) * v
            d.line([(XL * S, AY * S), (x1 * S, AY * S)], fill=YELLOW + (255,), width=9 * S)
            if v > 0.97:
                d.polygon([((XR - 26) * S, (AY - 16) * S), (XR * S, AY * S), ((XR - 26) * S, (AY + 16) * S)], fill=YELLOW + (255,))
        im.alpha_composite(L.resize((W, H), Image.LANCZOS))
        k = pop(t, 0.05)
        if k > 0:
            dd = ImageDraw.Draw(im)
            dd.ellipse([XL - 16, AY - 16, XL + 16, AY + 16], fill=YELLOW + (255,), outline=WHITE + (255,), width=3)
            put1(im, frag, XL, 718, a=min(1, k), scale=1.25 * min(k, 1.03))
            put1(im, lab_l, XL, 876, a=min(1, k), scale=min(k, 1.03))
        kg = pop(t, 0.55, 0.28)
        if kg > 0:
            put1(im, gap, (XL + XR) / 2, AY + 70, a=min(1, kg), scale=kg)
        kr = pop(t, 1.33)
        if kr > 0:
            dd = ImageDraw.Draw(im)
            dd.ellipse([XR - 16, AY - 16, XR + 16, AY + 16], fill=WHITE + (255,), outline=YELLOW + (255,), width=4)
            put1(im, scr, XR, 718, a=min(1, kr), scale=1.25 * min(kr, 1.03))
            put1(im, lab_r, XR, 876, a=min(1, kr), scale=min(kr, 1.03))
        frames.append(im.convert("RGB"))
    return frames


# ---------- jarak ----------
RE, EX, EY = 150.0, -40.0, 960.0            # px per Earth radius (6.371 km), Earth centre off the left edge
R_GEO = RE * (6371 + 35786) / 6371          # geosynchronous ring
R_APO = RE * (6371 + 32000) / 6371          # Apophis closest approach, from Earth's centre
K_PATH = 0.0011


def apo_xy(s):
    """Apophis track: closest to Earth at s = 0, bending away on both sides"""
    return EX + R_APO + K_PATH * s * s, EY + s


def earth_sprite():
    r = int(RE)
    sp = Image.new("RGBA", ((2 * r + 80) * S, (2 * r + 80) * S))
    c = (r + 40) * S
    glow = Image.new("RGBA", sp.size)
    ImageDraw.Draw(glow).ellipse([c - (r + 14) * S, c - (r + 14) * S, c + (r + 14) * S, c + (r + 14) * S], fill=(90, 170, 255, 170))
    sp.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14 * S)))
    yy, xx = np.mgrid[0:sp.height, 0:sp.width].astype(np.float32)
    rr = np.sqrt((xx - c) ** 2 + (yy - c) ** 2) / (r * S)
    tex = noise(sp.size[::-1], [(60, 0.6), (18, 0.4)], 7)
    land = tex > 0.56
    col = np.where(land[..., None], np.array([70, 120, 60], np.float32), np.array([28, 86, 170], np.float32))
    shade = np.clip(1.15 - 0.55 * ((xx - c + 0.4 * r * S) / (r * S)) ** 2 - 0.3 * ((yy - c) / (r * S)) ** 2, 0.35, 1.1)
    col = col * shade[..., None]
    a = np.dstack([col, (np.clip((1 - rr) * r * S / 2, 0, 1) * 255)])
    disc = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    sp.alpha_composite(disc)
    return sp


def sat_icon(scale=1.0):
    sp = Image.new("RGBA", (44 * S, 24 * S))
    d = ImageDraw.Draw(sp)
    d.rectangle([2 * S, 7 * S, 15 * S, 17 * S], fill=(70, 130, 230, 255), outline=WHITE + (255,), width=S)
    d.rectangle([29 * S, 7 * S, 42 * S, 17 * S], fill=(70, 130, 230, 255), outline=WHITE + (255,), width=S)
    d.rectangle([16 * S, 5 * S, 28 * S, 19 * S], fill=(225, 225, 225, 255))
    return sp


def rock():
    rng = np.random.default_rng(29)
    sp = Image.new("RGBA", (80 * S, 60 * S))
    pts = []
    for j in range(14):
        th = 2 * math.pi * j / 14
        r = 1 + rng.uniform(-0.12, 0.1)
        pts.append(((40 + 30 * r * math.cos(th)) * S, (30 + 20 * r * math.sin(th)) * S))
    d = ImageDraw.Draw(sp)
    d.polygon(pts, fill=(150, 140, 128, 255), outline=(60, 55, 50, 255), width=2 * S)
    d.ellipse([28 * S, 20 * S, 38 * S, 28 * S], fill=(110, 102, 94, 255))
    d.ellipse([46 * S, 30 * S, 52 * S, 35 * S], fill=(110, 102, 94, 255))
    return sp


def skema_jarak(times=None):
    bg = backdrop((6, 10, 24), (2, 4, 12), glow=(10, 18, 40), gx=200, gy=960)
    a = np.asarray(bg, np.float32).copy()
    rng = np.random.default_rng(2029)
    for _ in range(260):   # stars
        x, y = rng.integers(0, W), rng.integers(0, H)
        a[y, x, :3] = np.minimum(255, a[y, x, :3] + rng.uniform(60, 200))
    bg = to_img(a).convert("RGBA")
    bg = finish(bg, top=600)
    earth = earth_sprite()
    ring = Image.new("RGBA", (W * S, H * S))
    dashed(ImageDraw.Draw(ring), [(EX + R_GEO * math.cos(th), EY + R_GEO * math.sin(th))
                                  for th in np.linspace(-0.46, 0.46, 120)], (150, 190, 255, 210), 4, dash=12, gap=10)
    ring = ring.resize((W, H), Image.LANCZOS)
    sats = [(EX + R_GEO * math.cos(th), EY + R_GEO * math.sin(th)) for th in np.linspace(-0.4, 0.4, 7)]
    sat = sat_icon()
    rk = rock()
    lab_ring = label([("satelit geosinkron", 36, WHITE, True), ("±36.000 km dari permukaan", 30, GREY, False)])
    lab_apo = label([("APOPHIS", 48, YELLOW, True), ("±32.000 km dari permukaan", 30, WHITE, False)])
    date = pill("13 APRIL 2029", 40, (20, 20, 20), YELLOW + (245,), (255, 255, 255, 200))
    nasa = pill("NASA: tidak ada risiko tabrakan (setidaknya 100 tahun)", 28, WHITE, (10, 60, 30, 230), (140, 255, 170, 200))
    bumi = label([("BUMI", 34, WHITE, True)])
    s0, s1 = -470.0, 150.0
    frames = []
    for i in range(N["jarak"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        put1(im, earth, EX, EY)
        put1(im, bumi, 62, EY, a=ramp(t, 0.0, 0.2))
        im.alpha_composite(ring)
        glow = 1 + 0.5 * max(0.0, math.sin(min(max((t - 1.73) / 0.5, 0), 1) * math.pi))   # satellites flash on "satelit"
        for x, y in sats:
            put1(im, sat, x, y, scale=1.15 * glow)
        put1(im, lab_ring, 560, 700, a=min(1, pop(t, 0.15)), scale=min(1, pop(t, 0.15)))
        L = Image.new("RGBA", (W * S, H * S))
        dl = ImageDraw.Draw(L)
        dl.line([(760 * S, 700 * S), ((sats[1][0] - 22) * S, (sats[1][1] + 6) * S)], fill=(255, 255, 255, int(150 * ramp(t, 0.15, 0.35))), width=2 * S)
        # closest approach on "dari" (1.01 s), then on past the ring
        sc = s0 * (1 - ease(t / 1.01)) if t < 1.01 else s1 * ease((t - 1.01) / 1.2)
        trail = [apo_xy(s) for s in np.linspace(s0, sc, 60)]
        dashed(dl, trail, YELLOW + (230,), 4, dash=16, gap=10)
        im.alpha_composite(L.resize((W, H), Image.LANCZOS))
        put1(im, date, 300, 860, a=min(1, pop(t, 0.34)), scale=min(1.05, pop(t, 0.34)))
        x, y = apo_xy(sc)
        put1(im, rk, x, y, scale=1.5)
        ka = pop(t, 1.01)
        if ka > 0:
            dd = ImageDraw.Draw(im)
            dd.line([(660, 1050), (EX + R_APO - 44, EY + 14)], fill=(255, 225, 0, int(200 * min(1, ka))), width=3)
            put1(im, lab_apo, 470, 1062, a=min(1, ka), scale=min(1, ka))
        kn = pop(t, 1.32)
        if kn > 0:
            put1(im, nasa, 540, 1172, a=min(1, kn), scale=min(1, kn))
        frames.append(im.convert("RGB"))
    return frames


# ---------- cover ----------
def cover():
    im = Image.open("img/H1.jpg").convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")
    a = np.asarray(im, np.float32)
    a[..., :3] *= 1 - np.clip((760 - YY) / 520, 0, 1)[..., None] * 0.45   # a little darker behind the title
    im = to_img(a).convert("RGBA")
    t = text_sprite([("KUTUKAN", 84, WHITE, True), ("MESIR KUNO", 118, YELLOW, True), ("UNTUK ULAR RAKSASA", 66, WHITE, True)], gap=10)
    put1(im, t, 540, 420)
    put1(im, pill("ilustrasi", 24, WHITE), 960, 1860)
    im.convert("RGB").save("img/cover82.jpg", quality=93)
    print("img/cover82.jpg")


if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or ["prep", "garis_waktu", "jarak", "cover"]
    fns = {"garis_waktu": skema_garis_waktu, "jarak": skema_jarak}
    for name in todo:
        if name == "prep":
            prep()
            continue
        if name == "cover":
            cover()
            continue
        fr = fns[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, f"clips/skema_{name}.mp4")
