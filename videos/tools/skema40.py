"""Schematic animations for Titik Heran #40 (run in the episode work dir after
`dl.py v:20042 i:8652303 v:27770 v:179777 i:4229845 i:67757 i:4006343`; writes clips/20042s.mp4, img/8652303cut.png,
img/4006343v.jpg and clips/skema_jarak.mp4, skema_kirim.mp4, skema_balas.mp4, skema_daya.mp4, skema_piringan.mp4,
skema_sapaan.mp4).
usage: python3 skema40.py [prep|jarak|kirim|balas|daya|piringan|sapaan ...] [--sheet out.jpg t1,t2,...]
clips/20042s.mp4: the first 1,75 s of the 3D Voyager render (20042, close on the Golden Record) slowed 2,25x with motion
  interpolation. Later in that clip a spiral galaxy fills the background, which would suggest Voyager has left the Milky Way
  (it has not), so only the opening is used.
img/8652303cut.png: the Voyager vector drawing cut out of its black ground (alpha from brightness; the parts cut by the image
  edge fade out). img/4006343v.jpg: the lantern photo set higher (ground continued below), so the person stands above the
  subtitles.
skema_jarak: the Voyager drawing over a star field (27770 turned upright) pulls away; a dashed line runs to a blue dot BUMI and
  a light pulse travels it ("1 hari cahaya": light takes a day).
skema_kirim: the radio telescope (179777) sends yellow wave arcs up; a calendar card shows HARI INI.
skema_balas: the dish at dusk (4229845) catches waves coming in; the card flips to BESOK, then LUSA.
skema_daya: the drawing shrinks and turns as it flies off; a power bar drains from green to red and blinks on "sekarat".
skema_piringan: the Golden Record photo (67757, NASA) with a gold glint; a reel of greeting languages (real ones from the 55,
  in Indonesian) spins and stops on INDONESIA.
skema_sapaan: Voyager a tiny glint over the stars; gold rings pulse out of it in time with the voice.
Event times are seconds from the start of each clip, read off `render.py 40 plan`: skema_jarak starts at 3,53 ("sejauh" 1,99,
"satu" 2,60, "cahaya" 3,05), skema_kirim at 7,30 ("kirim" 1,04, "hari" 1,73), skema_balas at 9,97 ("lusa" 1,14), skema_daya at
11,80 ("kini" 2,86, "sekarat" 3,92), skema_piringan at 16,37 ("piringan" 1,23, "sapaan" 2,74, "Indonesia" 3,50), skema_sapaan
at 20,87 (follows the voice in segNN/vo_tight.wav, which `render.py 40 plan` writes).
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, text_sprite, dashed, encode
from skema35 import blur, sheet
from skema36 import reframe
from skema37 import to_img, put1
from skema39 import cover, push, lum, sat

N = {"jarak": 122, "kirim": 89, "balas": 64, "daya": 146, "piringan": 144, "sapaan": 159}  # each clip runs ~0,3 s past its shot
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
RED, GREEN, GOLD = (232, 44, 40), (70, 220, 100), (255, 200, 96)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
ANCHOR = (400, 310)  # the dish and bus in the 1280x926 drawing
CAL = (250, 1140)    # the calendar card, in the same place in both antenna shots
SAPAAN_T0, TEMPO = 20.87, 1.057  # skema_sapaan's start in the video and the VO tempo, from `render.py 40 plan`


def wanted(i, times):
    return times is None or any(abs(i / FPS - x) < 0.5 / FPS for x in times)


def frames_of(path, t0, n, rot=False):
    """n frames from a clip at 30 fps, cover-cropped to 1080x1920 (rot: a landscape clip turned upright, no upscaling)"""
    vf = f"fps={FPS}," + ("transpose=1," if rot else "") + f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(t0), "-i", path, "-frames:v", str(n), "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    last = None
    for _ in range(n):
        buf = p.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            last = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
        yield last
    p.stdout.close()
    p.wait()


def stars(f):
    """the star field a little lifted towards deep blue, so it is not dead black"""
    return f * 1.12 + (np.array([5, 9, 22], np.float32) * (0.6 + 0.4 * YY / H)[..., None])


# ---------- prep ----------
def prep():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-t", "1.75", "-i", "clips/20042.mp4", "-vf",
                    "setpts=2.25*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
                    "-an", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "clips/20042s.mp4"], check=True)
    print("clips/20042s.mp4")
    im = np.asarray(Image.open("img/8652303.jpg").convert("RGB"), np.float32)
    a = np.clip((im.max(2) - 16) / 46, 0, 1)
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    a *= np.clip(np.minimum.reduce([xx, yy, w - 1 - xx, h - 1 - yy]).astype(np.float32) / 60, 0, 1)
    rgb = np.clip(im / np.maximum(a, 0.05)[..., None], 0, 255)
    Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), "RGBA").save("img/8652303cut.png")
    print("img/8652303cut.png")
    reframe("img/4006343.jpg", 1920 / 840, 864, -380, "img/4006343v.jpg")


VOY = None


def voyager():
    global VOY
    if VOY is None:
        VOY = Image.open("img/8652303cut.png")
    return VOY


def place(base, scale, angle, ax, ay, alpha=1.0, bright=1.0):
    """the Voyager drawing scaled and turned (degrees, counter-clockwise) with its ANCHOR on (ax, ay) of a 1x RGBA image"""
    sp = voyager()
    sp = sp.resize((max(1, round(sp.width * scale)), max(1, round(sp.height * scale))), Image.LANCZOS)
    cx, cy = sp.width / 2, sp.height / 2
    dx, dy = ANCHOR[0] * scale - cx, ANCHOR[1] * scale - cy
    sp = sp.rotate(angle, resample=Image.BICUBIC, expand=True)
    th = math.radians(angle)
    px = sp.width / 2 + math.cos(th) * dx + math.sin(th) * dy
    py = sp.height / 2 - math.sin(th) * dx + math.cos(th) * dy
    if bright != 1.0 or alpha != 1.0:
        r, g, b, a = sp.split()
        r, g, b = (c.point(lambda v: int(v * bright)) for c in (r, g, b))
        sp = Image.merge("RGBA", (r, g, b, a.point(lambda v: int(v * alpha))))
    base.alpha_composite(sp, (round(ax - px), round(ay - py)))


def glow_dot(r, col, core=1.0):
    g = Image.new("RGBA", (8 * r * S, 8 * r * S), col + (0,))
    ImageDraw.Draw(g).ellipse([2.6 * r * S, 2.6 * r * S, 5.4 * r * S, 5.4 * r * S], fill=col + (220,))
    g = g.filter(ImageFilter.GaussianBlur(1.4 * r * S))
    ImageDraw.Draw(g).ellipse([3.3 * r * S, 3.3 * r * S, 4.7 * r * S, 4.7 * r * S],
                              fill=tuple(round(c + (255 - c) * 0.5) for c in col) + (int(255 * core),))
    return g


# ---------- distance ----------
def skema_jarak(times=None):
    t_line, t_one, t_c = 1.99, 2.60, 3.05  # "sejauh", "satu", "cahaya"
    earth = glow_dot(14, (70, 150, 255))
    pulse = glow_dot(9, (255, 246, 210))
    bumi = text_sprite([("BUMI", 34, WHITE, True)])
    chip = text_sprite([("1 hari cahaya", 34, YELLOW, True)])
    E = (205, 1185)
    frames = []
    for i, f in enumerate(frames_of("clips/27770.mp4", 6.0, N["jarak"], rot=True)):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = to_img(stars(f)).convert("RGBA")
        u = ramp(t, 0, N["jarak"] / FPS)
        vx, vy = 600 + 40 * u, 800 - 25 * u
        place(im, 0.62 - 0.18 * u, -4 + 7 * u, vx, vy)
        if t >= t_line:
            ke = pop(t, t_line, 0.35)
            put1(im, earth, *E, a=min(1, ke), scale=max(0.01, ke))
            put1(im, bumi, E[0] + 92, E[1] + 2, a=ramp(t, t_line + 0.1, t_line + 0.35))
            lay = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(lay)
            L = math.hypot(E[0] - vx, E[1] - vy)
            dashed(d, [(vx, vy), (E[0], E[1])], (255, 255, 255, 220), 4, dash=20, gap=14, upto=L * ramp(t, t_line, t_c))
            im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
            if t >= t_c:  # light leaves the Earth and takes the whole line to reach Voyager
                v = ((t - t_c) / 0.9) % 1.0
                put1(im, pulse, E[0] + (vx - E[0]) * v, E[1] + (vy - E[1]) * v, a=min(1, (t - t_c) / 0.1))
        if t >= t_one:
            k = pop(t, t_one, 0.3)
            put1(im, chip, 560, 1035, a=min(1, k), scale=max(0.01, k))
        frames.append(im.convert("RGB"))
    return frames


# ---------- the radio link ----------
def arcs(im, c, ang, span, radii, alphas, col=YELLOW, width=7):
    """wave fronts: arcs round centre c, `ang` the direction they face (degrees, image coordinates), with a soft glow"""
    lay = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(lay)
    for r, a in zip(radii, alphas):
        if a <= 0.01 or r <= 2:
            continue
        d.arc([c[0] - r, c[1] - r, c[0] + r, c[1] + r], ang - span, ang + span, fill=col + (int(255 * a),), width=width)
    g = lay.filter(ImageFilter.GaussianBlur(9))
    im.alpha_composite(g)
    im.alpha_composite(g)
    im.alpha_composite(lay)


def calendar(text, hl=False):
    f = ImageFont.truetype(XB, 50 * S)
    w, h, hd = 300 * S, 172 * S, 48 * S
    sp = Image.new("RGBA", (w + 60 * S, h + 60 * S))
    sh = Image.new("RGBA", sp.size)
    ImageDraw.Draw(sh).rounded_rectangle([26 * S, 34 * S, 34 * S + w, 40 * S + h], radius=22 * S, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(10 * S))
    d = ImageDraw.Draw(sp)
    x0, y0 = 30 * S, 30 * S
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=20 * S, fill=YELLOW + (255,) if hl else (250, 250, 248, 255))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + hd], radius=20 * S, fill=(205, 38, 38, 255))
    d.rectangle([x0, y0 + hd - 20 * S, x0 + w, y0 + hd], fill=(205, 38, 38, 255))
    for rx in (x0 + 80 * S, x0 + w - 80 * S):
        d.ellipse([rx - 9 * S, y0 + 14 * S, rx + 9 * S, y0 + 32 * S], fill=(120, 20, 20, 255))
    d.text((x0 + w / 2, y0 + hd + (h - hd) / 2), text, font=f, fill=(28, 28, 30, 255), anchor="mm")
    sh.alpha_composite(sp)
    return sh


def flip_card(im, texts, t, a=1.0):
    """texts: [(t_from, text, highlighted)]; the card squashes shut and opens on each change"""
    cur = [x for x in texts if t >= x[0]]
    if not cur:
        return
    t0, text, hl = cur[-1]
    first = len(cur) == 1
    k = pop(t, t0, 0.3) if first else 1.0
    sy = 1.0 if first else min(1.0, abs((t - t0) - 0.07) / 0.07)
    card = calendar(text, hl)
    if (t - t0) < 0.07 and not first:  # still closing the previous page
        card = calendar(cur[-2][1], cur[-2][2])
    s = max(0.01, k)
    sp = card.resize((max(1, round(card.width * s / S)), max(1, round(card.height * s * max(sy, 0.04) / S))), Image.LANCZOS)
    if a < 1:
        sp.putalpha(sp.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(sp, (round(CAL[0] - sp.width / 2), round(CAL[1] - sp.height / 2)))


def skema_kirim(times=None):
    t_send, t_day = 1.04, 1.73  # "kirim", "hari"
    feed = (530, 520)
    frames = []
    for i, f in enumerate(frames_of("clips/179777.mp4", 0.0, N["kirim"])):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = to_img(push(f, 1 + 0.04 * i / N["kirim"])).convert("RGBA")
        if t >= t_send:
            ages = [t - t_send - 0.3 * k for k in range(12)]
            ages = [g for g in ages if g >= 0]
            arcs(im, feed, -78, 46, [40 + 560 * g for g in ages], [min(1, g / 0.08) * max(0, 1 - g / 1.3) for g in ages])
        flip_card(im, [(t_day, "HARI INI", False)], t)
        frames.append(im.convert("RGB"))
    return frames


def skema_balas(times=None):
    t_lusa = 1.14
    bg0 = cover("img/4229845.jpg", 0.26) * 1.2 + 6  # a dark dusk photo: lifted so it holds up next to the bright field
    dish = (700, 905)
    frames = []
    for i in range(N["balas"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = to_img(push(bg0, 1 + 0.04 * i / N["balas"])).convert("RGBA")
        ages = [t + 0.25 * k for k in range(-8, 5)]
        ages = [g for g in ages if 0 <= g <= 1.1]
        arcs(im, dish, -42, 34, [880 - 720 * g for g in ages], [min(1, g / 0.15) * min(1, (1.1 - g) / 0.25) for g in ages])
        flip_card(im, [(0.0, "HARI INI", False), (0.36, "BESOK", False), (t_lusa, "LUSA", True)], t)
        frames.append(im.convert("RGB"))
    return frames


# ---------- the power runs down ----------
def bar(fill, col, blink):
    w, h = 420, 60
    sp = Image.new("RGBA", ((w + 140) * S, (h + 40) * S))
    d = ImageDraw.Draw(sp)
    x0, y0 = 110 * S, 20 * S
    d.text((x0 - 20 * S, y0 + h * S / 2), "DAYA", font=ImageFont.truetype(XB, 34 * S), fill=(255, 255, 255, 255), anchor="rm")
    d.rounded_rectangle([x0, y0, x0 + w * S, y0 + h * S], radius=12 * S, fill=(0, 0, 0, 140), outline=(255, 255, 255, 235), width=4 * S)
    d.rounded_rectangle([x0 + w * S, y0 + 18 * S, x0 + (w + 12) * S, y0 + (h - 18) * S], radius=4 * S, fill=(255, 255, 255, 235))
    if fill > 0.005:
        a = int(255 * (1 - 0.75 * blink))
        d.rounded_rectangle([x0 + 9 * S, y0 + 9 * S, x0 + 9 * S + max(14 * S, (w - 18) * S * fill), y0 + (h - 9) * S],
                            radius=7 * S, fill=col + (a,))
    return sp


def skema_daya(times=None):
    t_now, t_dead = 2.86, 3.92  # "kini", "sekarat"
    frames = []
    for i, f in enumerate(frames_of("clips/27770.mp4", 14.0, N["daya"], rot=True)):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = to_img(stars(f)).convert("RGBA")
        u = ramp(t, 0, N["daya"] / FPS)
        drain = ramp(t, t_now + 0.25, t_dead)
        place(im, 0.42 - 0.29 * u ** 0.8, 2 - 16 * u, 560 + 90 * u, 820 - 60 * u, bright=1 - 0.3 * drain)
        if t >= t_now:
            fill = 1 - 0.88 * drain
            c = np.array(GREEN) * max(0, 1 - 2 * drain) + np.array(YELLOW) * (1 - abs(2 * drain - 1)) + np.array(RED) * max(0, 2 * drain - 1)
            bl = 1.0 if t > t_dead and int((t - t_dead) * 6) % 2 == 0 else 0.0
            k = pop(t, t_now, 0.3)
            put1(im, bar(fill, tuple(int(x) for x in c), bl), 505, 1150, a=min(1, k), scale=max(0.01, k))
        frames.append(im.convert("RGB"))
    return frames


# ---------- the Golden Record ----------
LANGS = ["INGGRIS", "JEPANG", "ARAB", "BELANDA", "HINDI", "LATIN", "MANDARIN", "SUMERIA", "RUSIA", "SPANYOL", "YUNANI", "KOREA",
         "THAI", "TURKI", "VIETNAM", "BENGALI", "PERSIA", "IBRANI", "JERMAN", "PRANCIS", "PORTUGIS", "SWEDIA", "INDONESIA", "URDU",
         "WALES", "ITALIA"]


def skema_piringan(times=None):
    t_glint, t_reel, t_id = 1.23, 2.74, 3.50  # "piringan", "sapaan", "Indonesia"
    bg0 = cover("img/67757.jpg", 0.5)
    gold = np.clip((lum(bg0) - 40) / 120, 0, 1)
    f_row = ImageFont.truetype(XB, 54 * S)
    ROW, CX, CY, PW = 78, 540, 790, 640
    i_id = LANGS.index("INDONESIA")
    frames = []
    for i in range(N["piringan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        z = 1 + 0.07 * i / N["piringan"]
        a = bg0.copy()
        g = ramp(t, t_glint, t_glint + 0.75)
        if 0 < g < 1:  # a gold glint sweeps across the record
            band = np.exp(-(((XX - 1.25 * W * g + 0.3 * W) * 0.94 + (YY - H / 2) * 0.34) / 90) ** 2)
            a = a + (band * gold * 150)[..., None] * np.array([1.0, 0.88, 0.6], np.float32)
        im = to_img(push(a, z)).convert("RGBA")
        if t >= t_reel:
            k = pop(t, t_reel, 0.3)
            u = ramp(t, t_reel + 0.05, t_id)
            p = i_id - 18 * (1 - u) ** 2.2
            lay = Image.new("RGBA", (W * S, H * S))
            d = ImageDraw.Draw(lay)
            top, bot = CY - 1.5 * ROW, CY + 1.5 * ROW
            d.rounded_rectangle([(CX - PW / 2) * S, top * S, (CX + PW / 2) * S, bot * S], radius=26 * S, fill=(8, 6, 2, 170),
                                outline=GOLD + (230,), width=4 * S)
            rows = Image.new("RGBA", (W * S, H * S))
            dr = ImageDraw.Draw(rows)
            for j in range(int(p) - 3, int(p) + 4):
                if 0 <= j < len(LANGS):
                    y = CY + (j - p) * ROW
                    on = j == i_id and t >= t_id
                    al = 255 if abs(y - CY) < ROW / 2 else 120
                    dr.text((CX * S, y * S), LANGS[j], font=f_row, fill=(YELLOW if on else WHITE) + (al,), anchor="mm")
            clipm = Image.new("L", rows.size, 0)
            ImageDraw.Draw(clipm).rounded_rectangle([(CX - PW / 2 + 6) * S, (top + 6) * S, (CX + PW / 2 - 6) * S, (bot - 6) * S],
                                                    radius=22 * S, fill=255)
            ra = np.asarray(rows.getchannel("A"), np.float32) * np.asarray(clipm, np.float32) / 255
            rows.putalpha(Image.fromarray(ra.astype(np.uint8)))
            d.rounded_rectangle([(CX - PW / 2 + 14) * S, (CY - ROW / 2) * S, (CX + PW / 2 - 14) * S, (CY + ROW / 2) * S],
                                radius=14 * S, outline=YELLOW + (200,), width=3 * S)
            lay.alpha_composite(rows)
            lay = lay.resize((W, H), Image.LANCZOS)
            if k < 1:
                s = max(0.01, k)
                lay = lay.resize((round(W * s), round(H * s)), Image.LANCZOS)
                tmp = Image.new("RGBA", (W, H))
                tmp.alpha_composite(lay, (round(CX - CX * s), round(CY - CY * s)))
                lay = tmp
            if t >= t_id:  # INDONESIA lands: a glow behind it
                gk = pop(t, t_id, 0.35)
                gl = Image.new("RGBA", (W, H), YELLOW + (0,))
                ImageDraw.Draw(gl).rounded_rectangle([CX - 250, CY - 34, CX + 250, CY + 34], radius=30, fill=YELLOW + (int(110 * min(1, gk)),))
                im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(18)))
            im.alpha_composite(lay)
        frames.append(im.convert("RGB"))
    return frames


# ---------- the greeting ----------
def envelope():
    """loudness of the tightened VO (0-1) as a function of the video time"""
    with wave.open("seg40/vo_tight.wav") as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32768
    hop = sr // 100
    n = len(x) // hop
    db = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    e = np.clip((db + 46) / 28, 0, 1)
    return lambda tv: float(np.interp(tv * TEMPO * 100, np.arange(n), e))


def skema_sapaan(times=None):
    env = envelope()
    tw = glow_dot(6, (255, 236, 200))
    frames = []
    for i, f in enumerate(frames_of("clips/27770.mp4", 24.0, N["sapaan"], rot=True)):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = to_img(stars(f) * 0.92).convert("RGBA")
        u = ramp(t, 0, N["sapaan"] / FPS)
        vx, vy = 560 + 40 * u, 900 - 22 * u
        spawn = [k * 0.2 for k in range(int(t / 0.2) + 1)]
        ages = [t - s for s in spawn if t - s < 1.6]
        amps = [env(SAPAAN_T0 + s) for s in spawn if t - s < 1.6]
        arcs(im, (vx, vy), -90, 180, [26 + 290 * g for g in ages], [min(1, 1.15 * a) * (1 - g / 1.6) ** 1.4 for g, a in zip(ages, amps)],
             col=GOLD, width=5)
        place(im, 0.075, -6 + 4 * u, vx, vy)
        put1(im, tw, vx + 3, vy - 2, a=0.55 + 0.45 * math.sin(5 * t) ** 2, scale=0.9 + 0.3 * env(SAPAAN_T0 + t))
        frames.append(im.convert("RGB"))
    return frames


FUNCS = {"jarak": skema_jarak, "kirim": skema_kirim, "balas": skema_balas, "daya": skema_daya, "piringan": skema_piringan,
         "sapaan": skema_sapaan}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k]
    os.makedirs("clips", exist_ok=True)
    for name in args or ["prep"] + list(N):
        if name == "prep":
            prep()
            continue
        frames = FUNCS[name](times)
        if out:
            sheet(frames, name, out)
        else:
            encode(frames, OUT[name])
