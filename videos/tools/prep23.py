"""Clips for Titik Heran #23 (run in the episode work dir after `dl.py i:8325935 i:4703397 i:6055308`).
clips/8325935k.mp4, clips/4703397k.mp4: the two young orangutan photos as 3 s clips, 1080x960, each with a slow push-in that keeps
the face still, for the split screen (top: the wild one in the canopy; bottom: the zoo one on the ropes, its face kept below the
captions).
clips/6055308j.mp4: the playful young orangutan on a vertical canvas, the top darkened for the title; a "JADWAL MAIN" calendar
sticker pops in on "jadwal" and a day is circled on "main!" (0.86 s and 1.62 s into the shot, from `render.py 23 plan`).
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, BOLD, MED, ramp, pop, encode


def push_in(src, up, crop, face, out, n=90, z1=1.08):
    """upscale src by `up`, crop (x, y, w, h) at 1.125:1, then zoom 1 -> z1 about the face point (in the crop) so it stays put"""
    x, y, w, h = crop
    fx, fy = face
    z = f"1+{z1 - 1}*on/{n}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", src,
                    "-vf", f"scale=iw*{up}:-2:flags=lanczos,crop={w}:{h}:{x}:{y},"
                           f"zoompan=z='{z}':x='{fx}*(1-1/zoom)':y='{fy}*(1-1/zoom)':d={n}:s=1080x960:fps={FPS},format=yuv420p",
                    "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium", "-crf", "16", out], check=True)
    print(out)


# face points read off the photos: 8325935 (1280x857) at (400, 286), 4703397 (853x1280) at (487, 641)
push_in("img/8325935.jpg", 3, (0, 0, 2892, 2571), (1200, 858), "clips/8325935k.mp4")
push_in("img/4703397.jpg", 2160 / 853, (0, 383, 2160, 1920), (1233, 1240), "clips/4703397k.mp4")


def calendar():
    """the sticker at 2x: a white page with a red header, two rings and a 4 x 3 grid of days; returns (sprite, centre of day 8)"""
    w, h, r = 290 * S, 300 * S, 26 * S
    m = 30 * S  # room for the shadow
    im = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle([m + 6 * S, m + 10 * S, m + w + 6 * S, m + h + 10 * S], r, fill=130)
    im.putalpha(sh.filter(ImageFilter.GaussianBlur(9 * S)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([m, m, m + w, m + h], r, fill=(252, 249, 240, 255))
    d.rounded_rectangle([m, m, m + w, m + 86 * S], r, fill=(226, 58, 48, 255))
    d.rectangle([m, m + 60 * S, m + w, m + 86 * S], fill=(226, 58, 48, 255))
    d.text((m + w / 2, m + 50 * S), "JADWAL MAIN", font=ImageFont.truetype(BOLD, 33 * S), fill=(255, 255, 255, 255), anchor="mm")
    for rx in (0.27, 0.73):
        cx = m + rx * w
        d.ellipse([cx - 9 * S, m + 6 * S, cx + 9 * S, m + 24 * S], fill=(140, 30, 24, 255))
        d.rounded_rectangle([cx - 5 * S, m - 16 * S, cx + 5 * S, m + 16 * S], 5 * S, fill=(200, 200, 205, 255))
    f = ImageFont.truetype(MED, 30 * S)
    gx, gy, cw, ch = m + 22 * S, m + 104 * S, (w - 44 * S) / 4, 62 * S
    day8 = None
    for k in range(12):
        cx, cy = gx + (k % 4 + 0.5) * cw, gy + (k // 4 + 0.5) * ch
        d.text((cx, cy), str(k + 1), font=f, fill=(90, 90, 96, 255), anchor="mm")
        if k + 1 == 8:
            day8 = (cx, cy)
    return im, day8


def circle_on(im, c, u, seed=3):
    """a hand-drawn red marker loop around c, drawn up to fraction u"""
    if u <= 0:
        return
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    wob = rng.normal(0, 0.035, 8)
    pts = []
    for i in range(int(64 * u) + 1):
        a = -2.2 + 2 * math.pi * 1.12 * i / 64
        rr = 1 + sum(wob[j] * math.sin((j + 1) * a + j) for j in range(8))
        pts.append((c[0] + 38 * S * rr * math.cos(a), c[1] + 31 * S * rr * math.sin(a)))
    d.line(pts, fill=(226, 40, 36, 255), width=6 * S, joint="curve")


def playful(n=66, t_pop=0.86, t_ring=1.62, at=(165, 770)):
    src = Image.open("img/6055308.jpg").convert("RGB").resize((1280, 1920), Image.LANCZOS).crop((100, 0, 1180, 1920))
    a = np.asarray(src, np.float32)
    y = np.arange(H, dtype=np.float32)[:, None, None]
    u = np.clip(1 - y / 640, 0, 1)
    a = a * (1 - 0.62 * u * u * (3 - 2 * u)) + np.array([10, 16, 28], np.float32) * 0.62 * u * u * (3 - 2 * u)
    base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    page, day8 = calendar()
    out = []
    for i in range(n):
        t = i / FPS
        im = base.copy()
        k = pop(t, t_pop, 0.32)
        if k > 0.01:
            sp = page.copy()
            circle_on(sp, day8, ramp(t, t_ring, t_ring + 0.26))
            ang = 7 + 9 * math.exp(-(t - t_pop) * 7) * math.sin((t - t_pop) * 22)
            sp = sp.resize((max(1, round(sp.width * k / S)), max(1, round(sp.height * k / S))), Image.LANCZOS)
            sp = sp.rotate(ang, resample=Image.BICUBIC, expand=True)
            im.alpha_composite(sp, (round(at[0] - sp.width / 2), round(at[1] - sp.height / 2)))
        out.append(im)
    return out


if "--sheet" in sys.argv:
    ts = [float(v) for v in sys.argv[sys.argv.index("--sheet") + 1].split(",")]
    fr = playful(n=int(max(ts) * FPS) + 1)
    fr = [fr[int(round(t * FPS))].convert("RGB").resize((W // 3, H // 3)) for t in ts]
    sheet = Image.new("RGB", (len(fr) * W // 3, H // 3))
    for k, f in enumerate(fr):
        sheet.paste(f, (k * W // 3, 0))
    sheet.save("sheet_6055308j.jpg", quality=85)
else:
    encode(playful(), "clips/6055308j.mp4")
