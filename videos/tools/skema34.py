"""Framing and animations for Titik Heran #34 (run in the episode work dir after
`dl.py i:2150062 i:8069142 i:2013929 i:6778117 i:300437 i:565648`; writes img/2150062v.jpg, img/8069142v.jpg, img/2013929v.jpg,
clips/skema_ir.mp4, clips/skema_mata.mp4 and clips/skema_weker.mp4).
usage: python3 skema34.py [bonn|bed|hp|ir|mata|weker ...] [--sheet out.jpg t1,t2,...]   (--sheet saves those frames as a contact sheet)
bonn: the main building of Universitas Bonn (Pixabay 2150062) set lower, so its tower stands under the title; the sky is continued above.
bed: the sleeping woman (Pixabay 8069142, a stand-in) set lower, the headboard colour fading to dark above her, so the title clears her face.
hp: the man lit by his phone in a dark room (Pixabay 2013929) framed on his face, under the CTA title.
skema_ir: a white jumping spider (Pixabay 6778117, not Portia fimbriata) as a night camera would show it: green monochrome, grain,
scanlines, a blinking "REC", "IR" and a running clock; the frame pushes in slowly, and on "berkedut" its legs twitch and curl three
times (a twirl-and-pull warp around the body: the body stays still, the legs move).
skema_mata: the hook spider's face (Pixabay 300437) close on its two big front eyes in the same night-camera look; from "matanya"
a soft shine inside each eye darts left and right together, like the retina movements seen in the REM-like phase. The clock
carries on from skema_ir.
skema_weker: the blurred alarm clock (Pixabay 565648) shaking as if it rings.
Event times are seconds from the start of each clip, read off `render.py 34 plan`: skema_ir starts at 6,30 s (shot 3; "kakinya"
at 1,44, "berkedut..." at 1,93), skema_mata at 9,20 s (shot 4; "bergerak-gerak." at 0,65), skema_weker at 15,03 s (shot 7).
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, encode, ramp

MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"
N = {"ir": 96, "mata": 57, "weker": 105}  # frames: each clip runs ~0,3 s past its shot
CLOCK0 = 2 * 3600 + 13 * 60 + 7  # 02:13:07 at the start of skema_ir
IR_LEN = 2.90  # length of the skema_ir shot, so the clock in skema_mata carries on


def cover(im, s=1.0):
    """the photo scaled to fill the frame (times s), centred"""
    k = max(W / im.width, H / im.height) * s
    b = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    return b.crop(((b.width - W) // 2, (b.height - H) // 2, (b.width - W) // 2 + W, (b.height - H) // 2 + H))


def bonn():
    im = Image.open("img/2150062.jpg").convert("RGB")
    s, tx, ty, fx, fy = 2.1, 670, 190, 540, 700  # the tower's vane tip (670, 190) lands at (540, 700)
    big = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0, y0 = round(tx * s - fx), round(fy - ty * s)
    part = np.asarray(big.crop((x0, 0, x0 + W, min(big.height, H - y0))), np.float32)
    out = np.zeros((H, W, 3), np.float32)
    out[y0:y0 + part.shape[0]] = part
    row = part[:12].mean(0)  # the sky at the photo's top edge, carried up and deepened a little
    yy = np.arange(y0, dtype=np.float32)[:, None, None]
    out[:y0] = row[None] * (1 - 0.14 * (y0 - yy) / y0)
    out[:y0 + 40] = np.asarray(Image.fromarray(out[:y0 + 40].clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float32)
    out[y0 + 40:y0 + 60] = part[40:60]  # keep the photo sharp below the blend
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save("img/2150062v.jpg", quality=95)
    print("img/2150062v.jpg")


def bed():
    im = Image.open("img/8069142.jpg").convert("RGB")
    s, fx0, fy0, fx, fy = 1.4, 600, 320, 540, 880  # her face (600, 320) lands at (540, 880)
    big = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0, y0 = round(fx0 * s - fx), round(fy - fy0 * s)
    part = np.asarray(big.crop((x0, 0, x0 + W, min(big.height, H - y0))), np.float32)
    # above the photo: its top rows (headboard and pillow) stretched up, blurred, and fading into a dark room
    col = part[:24].mean((0, 1))  # one colour, so the pillow corner leaves no streak
    yy = np.arange(y0 + 60, dtype=np.float32)[:, None, None]
    top = col[None, None] * (0.2 + 0.8 * (yy / (y0 + 60)) ** 1.5) * np.ones((1, W, 1), np.float32)
    out = np.zeros((H, W, 3), np.float32)
    out[:y0 + 60] = top
    a = np.clip(np.arange(part.shape[0], dtype=np.float32) / 70, 0, 1)[:, None, None]
    out[y0:y0 + part.shape[0]] = part * a + out[y0:y0 + part.shape[0]] * (1 - a)
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save("img/8069142v.jpg", quality=95)
    print("img/8069142v.jpg")


def hp():
    im = Image.open("img/2013929.jpg").convert("RGB")
    s, fx0, fy0, fx, fy = 2.0, 839, 462, 540, 1040  # his face (839, 462) lands at (540, 1040)
    big = np.asarray(im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS), np.float32)
    x0, y0 = round(fx0 * s - fx), round(fy - fy0 * s)
    out = np.zeros((H, W, 3), np.float32)
    top = max(0, y0)
    out[top:] = big[top - y0:top - y0 + H - top, x0:x0 + W]
    out[:top] = big[0, x0:x0 + W].mean(0) * 0.9  # the dark room carried up over the few rows the photo does not reach
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save("img/2013929v.jpg", quality=95)
    print("img/2013929v.jpg")


# ---------- night camera ----------
def bilinear(src, u, v):
    """sample a float image at (u, v) (pixel units), 0 outside"""
    h, w = src.shape
    x0, y0 = np.floor(u).astype(np.int32), np.floor(v).astype(np.int32)
    fx, fy = u - x0, v - y0
    ok = (x0 >= 0) & (y0 >= 0) & (x0 < w - 1) & (y0 < h - 1)
    x0, y0 = np.clip(x0, 0, w - 2), np.clip(y0, 0, h - 2)
    a, b, c, d = src[y0, x0], src[y0, x0 + 1], src[y0 + 1, x0], src[y0 + 1, x0 + 1]
    out = (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
    return np.where(ok, out, 0.0)


YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = 1 - 0.5 * (((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2) / 2
SCAN = np.where(np.arange(H) % 4 == 0, 0.92, 1.0).astype(np.float32)[:, None]


def night_look(L, rng):
    """luminance 0-1 -> the green monochrome of an infrared camera, with grain, scanlines and a vignette"""
    L = np.clip((L - 0.02) * 1.12, 0, 1) ** 0.85
    g = rng.normal(0, 0.05, (H // 2, W // 2)).astype(np.float32)
    L = L + np.repeat(np.repeat(g, 2, 0), 2, 1) * (0.6 + 0.4 * L)
    L = np.clip(L * VIG * SCAN * (1 + rng.uniform(-0.015, 0.015)), 0, 1)
    rgb = np.stack([0.70 * L + 0.015, 0.98 * L + 0.05, 0.72 * L + 0.025], -1)
    return Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))


def hud(im, t, clock_s):
    """viewfinder corners, a blinking REC dot, "IR" and the clock, top left (the corner tag sits top right)"""
    d = ImageDraw.Draw(im, "RGBA")
    col, k, a, wd = (225, 255, 225, 215), 24, 64, 4
    for cx, cy, sx, sy in [(k, k, 1, 1), (W - k, k, -1, 1), (k, H - k, 1, -1), (W - k, H - k, -1, -1)]:
        d.line([(cx, cy + sy * a), (cx, cy), (cx + sx * a, cy)], fill=col, width=wd)
    if (t % 1.0) < 0.6:
        d.ellipse([60, 66, 82, 88], fill=(235, 45, 45, 240))
    f = ImageFont.truetype(MED, 34)
    d.text((94, 59), "REC", font=f, fill=col)
    d.rectangle([186, 62, 230, 92], outline=col, width=3)
    d.text((193, 63), "IR", font=ImageFont.truetype(MED, 24), fill=col)
    c = int(clock_s)
    d.text((60, 106), f"{c // 3600:02d}:{c // 60 % 60:02d}:{c % 60:02d}", font=ImageFont.truetype(MONO, 32), fill=col)
    return im


def skema_ir(times=None):
    rng = np.random.default_rng(34)
    src = Image.open("img/6778117.jpg").convert("L")
    src = np.asarray(src.resize((src.width * 2, src.height * 2), Image.LANCZOS), np.float32) / 255
    src[1740:1840, 1380:] = 0  # a stray white speck at the photo's right edge
    au, av, u0, v0 = 375, 545, 390, 560  # anchor (orig px) -> frame (540, 1000); twitch centre on the body
    tw = [(1.95, 1, 0.3), (2.17, -1, 1.4), (2.47, 1, 2.2)]  # (time, direction, phase) of the three twitches
    frames = []
    for i in range(N["ir"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        s = 1.55 + 0.15 * ramp(t, 0, N["ir"] / FPS)
        u, v = au + (XX - 540) / s, av + (YY - 1000) / s
        e = [(tt, sg, ph, (t - tt) / 0.045 * math.exp(1 - (t - tt) / 0.045) if t >= tt else 0.0) for tt, sg, ph in tw]
        if any(x[3] > 0.01 for x in e):
            du, dv = u - u0, v - v0
            r, th = np.hypot(du, dv), np.arctan2(dv, du)
            wr = np.clip((r - 60) / 160, 0, 1)
            wr = wr * wr * (3 - 2 * wr)
            for _, sg, ph, k in e:
                if k > 0.01:
                    th = th - 0.10 * sg * k * wr * np.sin(2 * th + ph)
                    r = r * (1 + 0.08 * k * wr)
            u, v = u0 + r * np.cos(th), v0 + r * np.sin(th)
        L = bilinear(src, u * 2, v * 2)
        im = night_look(L, rng)
        frames.append(hud(im, t, CLOCK0 + t).convert("RGB"))
    return frames


def skema_mata(times=None):
    rng = np.random.default_rng(341)
    src = Image.open("img/300437.jpg").convert("L")
    src = np.asarray(src.resize((src.width * 2, src.height * 2), Image.LANCZOS), np.float32) / 255
    au, av = 414, 722  # between the two big front eyes -> frame (540, 1040)
    eyes, R = [(342, 725), (486, 720)], 58
    keys = [(0, 0), (0.28, 0), (0.34, -1), (0.58, -1), (0.64, 0.9), (0.80, 0.9), (0.86, -0.5), (0.98, -0.5), (1.04, 1.0),
            (1.22, 1.0), (1.28, -0.8), (1.46, -0.8), (1.52, 0.4), (2.5, 0.4)]  # saccades: quick jumps, then a hold
    kt, kp = [k[0] for k in keys], [k[1] for k in keys]
    frames = []
    for i in range(N["mata"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        s = 2.6 + 0.3 * ramp(t, 0, N["mata"] / FPS)
        u, v = au + (XX - 540) / s, av + (YY - 1040) / s
        L = bilinear(src, u * 2, v * 2) * 0.82
        p = float(np.interp(t, kt, kp))
        q = 0.15 * math.sin(7.3 * t)
        for ex, ey in eyes:
            inside = np.clip((0.93 * R - np.hypot(u - ex, v - ey)) / (0.08 * R), 0, 1)
            d = np.hypot(u - (ex + 0.30 * R * p), v - (ey + 0.10 * R * q))
            shine = np.clip((0.42 * R - d) / (0.16 * R), 0, 1)
            L = L + 0.42 * shine * shine * inside
        im = night_look(L, rng)
        frames.append(hud(im, t, CLOCK0 + IR_LEN + t).convert("RGB"))
    return frames


def skema_weker(times=None):
    base = cover(Image.open("img/565648.jpg").convert("RGB"), 1.05)
    frames = []
    for i in range(N["weker"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        a = 1.0 if (t % 0.9) < 0.65 else 0.25  # rings in bursts
        dx = a * (7 * math.sin(2 * math.pi * 11 * t) + 3 * math.sin(2 * math.pi * 17 * t + 1))
        dy = a * 4 * math.sin(2 * math.pi * 13 * t + 2)
        rot = a * 0.6 * math.sin(2 * math.pi * 9 * t + 0.5)
        im = base.rotate(rot, resample=Image.BICUBIC, center=(W / 2 + dx, H / 2 + dy), translate=(dx, dy))
        frames.append(im)
    return frames


def sheet(frames, name, out):
    picks = [f for f in frames if f is not None]
    tw, th = 360, 640
    sh = Image.new("RGB", (len(picks) * (tw + 6) - 6, th), (40, 40, 40))
    for k, f in enumerate(picks):
        sh.paste(f.resize((tw, th), Image.LANCZOS), (k * (tw + 6), 0))
    base, ext = os.path.splitext(out)
    sh.save(f"{base}_{name}{ext}", quality=88)
    print(f"{base}_{name}{ext}")


if __name__ == "__main__":
    args = sys.argv[1:]
    times, out = None, None
    if "--sheet" in args:
        k = args.index("--sheet")
        out, times = args[k + 1], [float(x) for x in args[k + 2].split(",")]
        args = args[:k] + args[k + 3:]
    todo = args or ["bonn", "bed", "hp", "ir", "mata", "weker"]
    for name, fn in [("bonn", bonn), ("bed", bed), ("hp", hp)]:
        if name in todo:
            fn()
    for name, fn in [("ir", skema_ir), ("mata", skema_mata), ("weker", skema_weker)]:
        if name in todo:
            fr = fn(times)
            if times is not None:
                sheet(fr, name, out)
            else:
                encode(fr, f"clips/skema_{name}.mp4")
