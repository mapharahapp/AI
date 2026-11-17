"""Schematic animations for Titik Heran #63 (run in the episode work dir; needs img/1033489.jpg, img/571462.jpg and
img/3985939.jpg; writes clips/skema_catatan.mp4, skema_homo.mp4, skema_jam.mp4).
catatan: an old paper card over the sepia Kota Tua photo: "BATAVIA, ±1631" and the Malays' story as Bontius noted it
  (a summary, not a quote): it can talk, but won't, so it is not made to work.
homo: a specimen-label card "Homo troglodytes · Linnaeus, 1758" over an orangutan face; at "golongan" the word Homo lights up
  and a pill "HOMO = GENUS MANUSIA" pops.
jam: a circular timer over the mother and baby: "predator pergi" at 0, the arc sweeps to 20 minutes with a tick at the
  ±7-minute average; pills "rata-rata ±7 menit", "terlama 20 menit" and "Science Advances, 2018 · Ketambe, Aceh".
Event times are seconds from the start of each clip, read off `render.py 63 plan`. Text stays out of the watermark band
(y 935-985), the title zone (y < 660) and the captions (y >= 1210).
usage: python3 skema63.py [catatan|homo|jam ...] [--sheet out.jpg t1,t2,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, ramp, pop, encode
from skema35 import sheet, SERIF_BI, SERIF_I
from skema37 import to_img, put1
from skema46 import pill, ease, wanted
from skema53 import XB
from skema61 import cover, paper_card

N = {"catatan": 47, "homo": 103, "jam": 99}
OUT = {k: f"clips/skema_{k}.mp4" for k in N}
# set from `render.py 63 plan`: catatan "Batavia" 0.03, "mencatatnya" 0.55; homo "Li-ne-us" 0.05, "memasukkannya" 1.08,
# "golongan" 1.94, "manusia" 2.27; jam "induk" 0.47, "diam" 0.92, "sampai" 1.36, "dua" 1.81, "menit" 2.34
T = {"card": 0.0, "kutip": 0.45, "label": 0.1, "homo": 1.9, "genus": 2.2,
     "pergi": 0.35, "sweep0": 0.9, "sweep1": 2.4, "avg": 1.45, "top": 2.35, "src": 2.0}
RED = (170, 40, 30, 255)
INK = (52, 38, 26, 255)


def graded(path, cx, cy, k, blur=0, sepia=False):
    im = cover(path, cx, cy)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im, np.float32)
    if sepia:
        a = a @ np.array([[.393, .349, .272], [.769, .686, .534], [.189, .168, .131]], np.float32)
    return to_img(a * k).convert("RGBA")


# ---------- catatan ----------
def skema_catatan(times=None):
    bg = graded("img/1033489.jpg", 0.5, 0.5, 0.45, blur=5, sepia=True)
    cw, ch = 820, 330
    card = paper_card(cw, ch)
    d = ImageDraw.Draw(card)
    ox, oy = 30, 30
    # the card's top sits at y 600 on screen (the title ends near 570); every row ends above the watermark band (935)
    d.text((ox + 44, oy + 28), "BATAVIA, ±1631", font=ImageFont.truetype(XB, 32), fill=RED)
    d.line([(ox + 44, oy + 74), (ox + cw - 44, oy + 74)], fill=(150, 120, 90, 255), width=2)
    f = ImageFont.truetype(SERIF_BI, 44)
    d.text((ox + 44, oy + 86), "\u201cOrang Melayu bilang, ia bisa", font=f, fill=INK)
    d.text((ox + 44, oy + 136), "bicara... tapi tidak mau,", font=f, fill=INK)
    d.text((ox + 44, oy + 186), "takut disuruh kerja.\u201d", font=f, fill=INK)
    d.text((ox + 44, oy + 262), "ringkasan catatan Jacobus Bontius, dokter Belanda di Batavia",
           font=ImageFont.truetype(SERIF_I, 24), fill=(90, 70, 50, 255))
    frames = []
    for i in range(N["catatan"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        u = ease(t / 0.3)
        c = card.rotate(-3 * (1 - u) - 1.2, resample=Image.BICUBIC, expand=True)
        c.putalpha(c.getchannel("A").point(lambda v: int(v * min(1, u * 1.4))))
        im.alpha_composite(c, (540 - c.width // 2, round(600 + 40 * (1 - u))))
        frames.append(im.convert("RGB"))
    return frames


# ---------- homo ----------
def skema_homo(times=None):
    bg = graded("img/571462.jpg", 0.5, 0.45, 0.62)
    cw, ch = 760, 190
    base = Image.new("RGBA", (cw * S, ch * S))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([0, 0, cw * S - 1, ch * S - 1], radius=16 * S, fill=(244, 238, 222, 245), outline=(120, 96, 60, 255), width=3 * S)
    d.rounded_rectangle([12 * S, 12 * S, cw * S - 13 * S, ch * S - 13 * S], radius=10 * S, outline=(160, 130, 90, 255), width=2 * S)
    fbig = ImageFont.truetype(SERIF_BI, 76 * S)
    homo_w = fbig.getlength("Homo ")
    tw = fbig.getlength("Homo troglodytes")
    x0 = (cw * S - tw) / 2
    d.text((x0 + homo_w, 34 * S), "troglodytes", font=fbig, fill=INK)
    d.text((cw * S / 2, 150 * S), "Linnaeus, 1758", font=ImageFont.truetype(SERIF_I, 34 * S), fill=(90, 70, 50, 255), anchor="mm")

    def homo_word(lit):
        sp = Image.new("RGBA", (cw * S, ch * S))
        ds = ImageDraw.Draw(sp)
        if lit:
            bb = ds.textbbox((x0, 34 * S), "Homo", font=fbig)
            ds.rounded_rectangle([bb[0] - 10 * S, bb[1] - 6 * S, bb[2] + 10 * S, bb[3] + 8 * S], radius=10 * S, fill=YELLOW + (255,))
        ds.text((x0, 34 * S), "Homo", font=fbig, fill=(20, 20, 20, 255) if lit else INK)
        return sp
    card0, card1 = base.copy(), base.copy()
    card0.alpha_composite(homo_word(False))
    card1.alpha_composite(homo_word(True))
    genus = pill("HOMO = GENUS MANUSIA", 44, col=(20, 20, 20), bg=YELLOW + (245,), edge=(255, 255, 255, 230), pad=(28, 14))
    frames = []
    for i in range(N["homo"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        lit = ramp(t, T["homo"], T["homo"] + 0.15)
        c = card0 if lit < 0.5 else card1
        put1(im, c, 540, 1095, scale=min(pop(t, T["label"], 0.35), 1.06))
        if t > T["genus"]:
            put1(im, genus, 540, 850, scale=min(pop(t, T["genus"], 0.3), 1.1))
        frames.append(im.convert("RGB"))
    return frames


# ---------- jam ----------
CX, CY, R = 540, 790, 130


def skema_jam(times=None):
    bg = graded("img/3985939.jpg", 0.45, 0.5, 0.5, blur=2)
    rng_bg = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(rng_bg)
    d.ellipse([(CX - R - 26) * S, (CY - R - 26) * S, (CX + R + 26) * S, (CY + R + 26) * S], fill=(8, 12, 18, 200))
    d.ellipse([(CX - R) * S, (CY - R) * S, (CX + R) * S, (CY + R) * S], outline=(255, 255, 255, 70), width=16 * S)
    for k in range(20):  # minute ticks
        a = -math.pi / 2 + 2 * math.pi * k / 20
        r0, r1 = (R - 30, R - 18) if k % 5 else (R - 36, R - 16)
        d.line([((CX + r0 * math.cos(a)) * S, (CY + r0 * math.sin(a)) * S), ((CX + r1 * math.cos(a)) * S, (CY + r1 * math.sin(a)) * S)],
               fill=(255, 255, 255, 150), width=3 * S)
    ring = rng_bg.resize((W, H), Image.LANCZOS)
    fnum = ImageFont.truetype(XB, 92 * S)
    fsub = ImageFont.truetype(XB, 26 * S)
    # the pills sit right of centre: the baby's face is at x ~345, y ~1050
    avg = pill("rata-rata ±7 menit", 34, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(24, 12))
    top = pill("terlama 20 menit", 34, col=(20, 20, 20), bg=YELLOW + (240,), edge=(255, 255, 255, 220), pad=(24, 12))
    src = pill("Science Advances, 2018 · Ketambe, Aceh", 26, col=(235, 235, 240), bg=(10, 14, 24, 205))
    frames = []
    for i in range(N["jam"]):
        t = i / FPS
        if not wanted(i, times):
            frames.append(None)
            continue
        im = bg.copy()
        a_in = ramp(t, 0.0, 0.25)
        r = ring.copy()
        r.putalpha(r.getchannel("A").point(lambda v: int(v * a_in)))
        im.alpha_composite(r)
        g = ease((t - T["sweep0"]) / (T["sweep1"] - T["sweep0"]))   # 0 -> 1 = 0 -> 20 minutes
        lay = Image.new("RGBA", (W * S, H * S))
        dl = ImageDraw.Draw(lay)
        if g > 0:
            dl.arc([(CX - R) * S, (CY - R) * S, (CX + R) * S, (CY + R) * S], -90, -90 + 360 * g, fill=YELLOW + (255,), width=16 * S)
        if g >= 7 / 20 or t > T["avg"]:   # the average mark stays once the arc passes it
            a = -math.pi / 2 + 2 * math.pi * 7 / 20
            dl.line([((CX + (R - 22) * math.cos(a)) * S, (CY + (R - 22) * math.sin(a)) * S),
                     ((CX + (R + 22) * math.cos(a)) * S, (CY + (R + 22) * math.sin(a)) * S)], fill=(255, 255, 255, 255), width=6 * S)
            dl.text(((CX + (R + 52) * math.cos(a)) * S, (CY + (R + 40) * math.sin(a)) * S), "±7", font=ImageFont.truetype(XB, 34 * S),
                    fill=(255, 255, 255, 255), anchor="mm")
        mins = round(20 * g)
        dl.text((CX * S, (CY - 14) * S), f"{mins}", font=fnum, fill=(255, 255, 255, 255) if mins < 20 else YELLOW + (255,), anchor="mm")
        sub = "predator pergi" if g <= 0 else "MENIT"
        if t > T["pergi"]:
            dl.text((CX * S, (CY + 56) * S), sub, font=fsub, fill=(230, 230, 235, int(255 * ramp(t, T["pergi"], T["pergi"] + 0.2))), anchor="mm")
        im.alpha_composite(lay.resize((W, H), Image.LANCZOS) if a_in >= 1 else Image.blend(Image.new("RGBA", (W, H)), lay.resize((W, H), Image.LANCZOS), a_in))
        if t > T["avg"]:
            put1(im, avg, 800, 1030, scale=min(pop(t, T["avg"], 0.3), 1.08))
        if t > T["top"]:
            put1(im, top, 800, 1095, scale=min(pop(t, T["top"], 0.3), 1.08))
        if t > T["src"]:
            put1(im, src, 700, 1160, a=ramp(t, T["src"], T["src"] + 0.25))
        frames.append(im.convert("RGB"))
    return frames


FUN = {"catatan": skema_catatan, "homo": skema_homo, "jam": skema_jam}

if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    os.makedirs("clips", exist_ok=True)
    for name in args or list(N):
        fr = FUN[name](times)
        if out:
            sheet(fr, name, out)
        else:
            encode(fr, OUT[name])
