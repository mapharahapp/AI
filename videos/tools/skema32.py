"""Framing and animations for Titik Heran #32 (run in the episode work dir after `dl.py i:5798229 i:2505841 i:6252750`;
writes img/5798229v.jpg, clips/skema_buka.mp4, clips/skema_ayam.mp4, clips/6252750s.mp4 and clips/2505841s.mp4).
usage: python3 skema32.py [hook|buka|ayam|split ...] [--sheet out.jpg t1,t2,...]   (--sheet saves those frames as a contact sheet)
hook: the lidded stone sarcophagus at dusk (Pixabay 5798229, Bulgaria, not the Tomis one) framed so the seam between lid and box
sits above the captions; the grass below the photo's bottom edge is its own bottom rows mirrored and blurred.
skema_buka: the same frame; on "dibuka" a spark runs along the seam and leaves it glowing, as if light came out of the opened coffin.
skema_ayam: a close-up of a clay rooster (Pixabay 2505841, Indonesian handmade toys, not the Tomis toy). On "kerincingan" it is
shaken (the frame jolts, rattle arcs pulse at its sides); on "butirannya" a see-through window opens on its belly and shows small
pellets inside, which bounce, settle and glow. The pellets and the cavity are drawn to show the idea, not taken from the find.
Event times are seconds from the start of each clip, read off `render.py 32 plan`: skema_buka starts at 4,133 s (shot 1),
skema_ayam at 20,033 s (shot 8, "ayam"; shot 9 starts 1,067 s into it).
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, layer, down, sc, fade, put, glow_sprite, encode

N = {"buka": 56, "ayam": 176}
GOLD = (255, 214, 140)

# ---------- hook / skema_buka ----------
HOOK = (2.3, 290, 113)  # scale, and the photo's x, y at the frame's top left corner (so the seam lands at y ~1110-1230)
SEAM = [(425, 620), (450, 630), (480, 635), (520, 632), (560, 625), (600, 617), (640, 607), (680, 600), (720, 589), (748, 584)]


def hook_base():
    s, x0, y0 = HOOK
    im = Image.open("img/5798229.jpg").convert("RGB")
    h = round(H / s)
    over = y0 + h - im.height
    ext = Image.new("RGB", (im.width, y0 + h))
    ext.paste(im, (0, 0))
    if over > 0:  # the photo ends above the captions: continue the grass with its own bottom rows, mirrored,
        # then let the foreground go out of focus and into shadow, so the fold doesn't show
        ext.paste(im.crop((0, im.height - over, im.width, im.height)).transpose(Image.FLIP_TOP_BOTTOM), (0, im.height))
        a = np.asarray(ext, np.float32)
        soft = np.asarray(ext.filter(ImageFilter.GaussianBlur(7)), np.float32)
        y = np.arange(ext.height, dtype=np.float32)[:, None, None]
        blur = np.clip((y - (im.height - 90)) / 110, 0, 1)
        dark = 1 - 0.5 * np.clip((y - (im.height - 40)) / (over + 40), 0, 1) ** 1.2
        ext = Image.fromarray(np.clip((a * (1 - blur) + soft * blur) * dark, 0, 255).astype(np.uint8))
    return ext.crop((x0, y0, x0 + round(W / s), y0 + h)).resize((W, H), Image.LANCZOS)


def seam_frame():
    s, x0, y0 = HOOK
    return [((x - x0) * s, (y - y0) * s) for x, y in SEAM]


def path_len(pts):
    acc = [0.0]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(bx - ax, by - ay))
    return acc


def point_at(pts, acc, L):
    for (ax, ay), (bx, by), a0, a1 in zip(pts, pts[1:], acc, acc[1:]):
        if L <= a1:
            u = (L - a0) / max(a1 - a0, 1e-6)
            return ax + (bx - ax) * u, ay + (by - ay) * u
    return pts[-1]


def skema_buka(times=None):
    base = np.asarray(hook_base(), np.float32)
    seam = seam_frame()
    acc = path_len(seam)
    t_open, t_run = 0.79, 0.42  # "dibuka", and how long the spark takes to run along the seam

    def light(pts, width, blur, dy=0):
        """a stroke along the seam as a blurred 0-1 light mask (1x)"""
        m = Image.new("L", (W * S, H * S), 0)
        ImageDraw.Draw(m).line(sc([(x, y + dy) for x, y in pts]), fill=255, width=width * S, joint="curve")
        return np.asarray(m.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(blur)), np.float32)[..., None] / 255
    # light is added, not painted over: a white-hot core, an amber glow, a wide bloom, and a spill on the box face below the gap
    passes = [(4, 1.2, 0, (255, 248, 225), 1.0), (14, 6, 0, (255, 196, 105), 0.9), (70, 30, 0, (255, 150, 55), 0.6),
              (60, 34, 34, (255, 170, 80), 0.4)]
    full = [light(seam, w, b, dy) for w, b, dy, *_ in passes]
    frames = []
    for i in range(N["buka"]):
        t = i / FPS
        u = ramp(t, t_open, t_open + t_run)
        if u <= 0:
            frames.append(Image.fromarray(base.astype(np.uint8)))
            continue
        L = acc[-1] * u
        sx, sy = point_at(seam, acc, L)
        part = [p for p, a in zip(seam, acc) if a <= L] + [(sx, sy)]
        masks = full if u >= 1 else [light(part, w, b, dy) for w, b, dy, *_ in passes]
        flare = 1 + 0.5 * math.exp(-max(t - t_open - t_run, 0) / 0.12) * (u >= 1)  # a brief flare as the seam fills
        k = (0.86 + 0.14 * math.sin(2 * math.pi * 1.7 * (t - t_open))) * flare
        out = base.copy()
        for m, (*_, col, a) in zip(masks, passes):
            out += m * np.array(col, np.float32) * a * k
        if u < 1:  # the spark running ahead
            yy, xx = np.ogrid[0:H, 0:W]
            r2 = (xx - sx) ** 2 + (yy - sy) ** 2
            out += (np.exp(-r2 / (2 * 9.0 ** 2)) * 1.0 + np.exp(-r2 / (2 * 34.0 ** 2)) * 0.55)[..., None] * np.array([255, 236, 200], np.float32)
        frames.append(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)))
    return frames


# ---------- skema_ayam ----------
AYAM = (2.3, 1827, 21)  # scale of 2505841, and the crop's top left corner in the scaled photo
BODY = (990, 413)  # the rooster's round body (photo coordinates)
WIN = (933, 484, 57)  # window centre and radius on the belly (photo coordinates)
T_SHAKE, T_WIN = 2.367, 3.647  # "kerincingan", "butirannya"


def to_frame(x, y, dx=0, dy=0):
    s, x0, y0 = AYAM
    return x * s - x0 + dx, y * s - y0 + dy


def shake(t):
    """horizontal jolts that die away, as when a rattle is shaken (pixels)"""
    if t < T_SHAKE or t > T_SHAKE + 1.3:
        return 0.0, 0.0
    u = t - T_SHAKE
    k = math.exp(-u / 0.42) * ramp(u, 0, 0.05)
    return 17 * k * math.sin(2 * math.pi * 5.5 * u), 4 * k * math.sin(2 * math.pi * 11 * u + 0.6)


def pellet_sprite(r):
    """a small clay ball at 2x: lit from the top left, a darker rim, a soft contact shadow under it"""
    n = 4 * r * S
    sp = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    sh = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    c = n / 2
    ImageDraw.Draw(sh).ellipse([c - r * S * 1.05, c + r * S * 0.55, c + r * S * 1.05, c + r * S * 1.15], fill=(0, 0, 0, 150))
    sp.alpha_composite(sh.filter(ImageFilter.GaussianBlur(r * S * 0.25)))
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    d = np.sqrt((xx - c) ** 2 + (yy - c) ** 2) / (r * S)
    lit = np.clip(1 - np.sqrt((xx - c + 0.4 * r * S) ** 2 + (yy - c + 0.45 * r * S) ** 2) / (1.6 * r * S), 0, 1)
    col = np.array([150, 104, 70], np.float32) + lit[..., None] * np.array([92, 82, 66], np.float32)
    a = np.clip((1 - d) * r * S * 0.9, 0, 1)
    ball = Image.fromarray(np.dstack([np.clip(col, 0, 255), a * 255]).astype(np.uint8), "RGBA")
    sp.alpha_composite(ball)
    return sp


def cavity(R):
    """the inside of the hollow body as seen through the window, at 2x and R (1x) in radius: dark clay, lighter floor,
    the cut wall of the shell as a band round the edge"""
    n = 2 * R * S
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    u, v = (xx - n / 2) / (R * S), (yy - n / 2) / (R * S)
    rr = np.sqrt(u ** 2 + v ** 2)
    floor = np.clip((v - 0.15) / 0.8, 0, 1) ** 1.5
    col = (np.array([34, 18, 11], np.float32) * (1 - floor[..., None]) + np.array([92, 52, 32], np.float32) * floor[..., None])
    col *= (1.15 - 0.45 * rr ** 2)[..., None]
    wall = np.clip((rr - 0.86) / 0.04, 0, 1)[..., None]
    col = col * (1 - wall) + np.array([196, 106, 64], np.float32) * wall * (0.85 + 0.15 * v[..., None])
    a = np.clip((1 - rr) * R * S, 0, 1) * 255
    return Image.fromarray(np.dstack([np.clip(col, 0, 255), a]).astype(np.uint8), "RGBA")


PELLETS = [(-0.46, 0.55, 18), (-0.15, 0.63, 19), (0.17, 0.62, 18), (0.47, 0.5, 17), (-0.3, 0.33, 17), (0.02, 0.36, 18)]  # x, y in window radii, r px


def window_sprite(cav, balls, glows, R, w, t, phase):
    """the see-through window at scale w as a 1x RGBA sprite: the cavity, the pellets (bouncing after the shake, then glowing),
    clipped to the circle, with a white rim and a soft shadow round it"""
    n = (2 * R + 48) * S
    c1 = n / S / 2
    sp = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    put(sp, cav, c1, c1, scale=w)
    settle = math.exp(-max(t - T_WIN, 0) / 0.28)
    gl = ramp(t, T_WIN + 0.15, T_WIN + 0.45) * (0.75 + 0.25 * math.sin(2 * math.pi * 1.4 * (t - T_WIN)))
    for (px, py, r), ball, glow, p in zip(PELLETS, balls, glows, phase):
        hop = 26 * settle * abs(math.sin(2 * math.pi * 3.1 * (t - T_WIN) + p))
        qx, qy = c1 + px * R * w, c1 + (py * R - hop) * w
        put(sp, glow, qx, qy, a=gl * w, scale=w)
        put(sp, ball, qx, qy, scale=w)
    mask = Image.new("L", (n, n), 0)
    rr = R * w * 0.995 * S
    ImageDraw.Draw(mask).ellipse([n / 2 - rr, n / 2 - rr, n / 2 + rr, n / 2 + rr], fill=255)
    sp.putalpha(Image.fromarray(np.minimum(np.asarray(sp.getchannel("A")), np.asarray(mask))))
    ro = (R * w + 2) * S
    ring = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([n / 2 - ro - 3 * S, n / 2 - ro - 3 * S, n / 2 + ro + 3 * S, n / 2 + ro + 3 * S],
                                 outline=(0, 0, 0, 150), width=10 * S)
    ring = ring.filter(ImageFilter.GaussianBlur(5 * S))
    ImageDraw.Draw(ring).ellipse([n / 2 - ro, n / 2 - ro, n / 2 + ro, n / 2 + ro], outline=(255, 255, 255, 245), width=6 * S)
    ring.alpha_composite(sp)
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    out.alpha_composite(ring)
    out.alpha_composite(sp)
    return out.resize((n // S, n // S), Image.LANCZOS)


def arcs_band(t, dx, dy, cy, half=230):
    """three rattle arcs on each side of the toy, pulsing outward, on a 1x band (y cy-half .. cy+half)"""
    ka = ramp(t, T_SHAKE, T_SHAKE + 0.1) * (1 - ramp(t, T_SHAKE + 1.0, T_SHAKE + 1.35))
    if ka <= 0.01:
        return None
    band = Image.new("RGBA", (W * S, 2 * half * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(band)
    cx, cyl = 540 + dx, half + dy
    for k, r in enumerate((420, 458, 496)):
        ph = ((t - T_SHAKE) * 3.2 - k * 0.22) % 1.0
        a = round(235 * ka * (0.35 + 0.65 * max(0.0, math.sin(math.pi * ph))))
        box = [(cx - r) * S, (cyl - r) * S, (cx + r) * S, (cyl + r) * S]
        for a0 in (180, 0):
            d.arc(box, a0 - 20, a0 + 20, fill=(0, 0, 0, a // 2), width=11 * S)
            d.arc(box, a0 - 19, a0 + 19, fill=(255, 255, 255, a), width=7 * S)
    return band.resize((W, 2 * half), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))


def skema_ayam(times=None):
    s, x0, y0 = AYAM
    photo = Image.open("img/2505841.jpg").convert("RGB")
    big = photo.resize((round(photo.width * s), round(photo.height * s)), Image.LANCZOS)
    arr = np.asarray(big, np.float32)
    wx, wy = to_frame(WIN[0], WIN[1])
    R = round(WIN[2] * s)
    cav = cavity(R)
    balls = [pellet_sprite(r) for *_, r in PELLETS]
    glows = [glow_sprite(r + 10, (255, 196, 90)) for *_, r in PELLETS]
    phase = np.random.default_rng(32).uniform(0, 2 * math.pi, len(PELLETS))
    cy_arcs = to_frame(*BODY)[1] - 10  # the arcs are centred on the whole toy, tail included
    want = None if times is None else {min(round(t * FPS), N["ayam"] - 1) for t in times}
    frames = []
    for i in range(N["ayam"]):
        if want is not None and i not in want:
            frames.append(None)
            continue
        t = i / FPS
        dx, dy = shake(t)
        dx2, dy2 = shake(t + 0.5 / FPS)  # a second sample half a frame later, blended in: a touch of motion blur
        crops = []
        for ddx, ddy in ((dx, dy), (dx2, dy2)):
            xa, ya = int(round(x0 - ddx)), int(round(y0 - ddy))
            crops.append(arr[ya:ya + H, xa:xa + W])
        im = Image.fromarray(((crops[0] + crops[1]) / 2).astype(np.uint8)).convert("RGBA")
        band = arcs_band(t, dx, dy, cy_arcs)
        if band is not None:
            im.alpha_composite(band, (0, round(cy_arcs - band.height / 2)))
        w = pop(t, T_WIN, 0.32)
        if w > 0.01:
            sp = window_sprite(cav, balls, glows, R, w, t, phase)
            im.alpha_composite(sp, (round(wx + dx - sp.width / 2), round(wy + dy - sp.height / 2)))
        frames.append(im)
    return frames


def split_clips():
    for i in ("6252750", "2505841"):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", f"img/{i}.jpg", "-t", "3",
                        "-vf", "crop=trunc(iw/2)*2:trunc(ih/2)*2:0:0,format=yuv420p", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "14", f"clips/{i}s.mp4"], check=True)
        print(f"clips/{i}s.mp4")


def sheet(frames, times, out):
    tiles = [frames[min(round(t * FPS), len(frames) - 1)].convert("RGB").resize((360, 640), Image.LANCZOS) for t in times]
    for tile, t in zip(tiles, times):
        ImageDraw.Draw(tile).text((8, 8), f"{t:.2f}", fill=(255, 255, 0))
    s = Image.new("RGB", (len(tiles) * 366, 640), (40, 40, 40))
    for k, tile in enumerate(tiles):
        s.paste(tile, (k * 366, 0))
    s.save(out, quality=88)
    print(out)


if __name__ == "__main__":
    args = sys.argv[1:]
    sheet_out = times = None
    if "--sheet" in args:
        k = args.index("--sheet")
        sheet_out, times = args[k + 1], [float(t) for t in args[k + 2].split(",")]
        args = args[:k]
    todo = args or ["hook", "buka", "ayam", "split"]
    for name in todo:
        if name == "split":
            split_clips()
            continue
        if name == "hook":
            hook_base().save("img/5798229v.jpg", quality=95)
            print("img/5798229v.jpg")
            continue
        frames = skema_buka() if name == "buka" else skema_ayam(times if sheet_out else None)
        if sheet_out:
            sheet(frames, times, sheet_out.replace(".jpg", f"_{name}.jpg"))
        else:
            encode(frames, f"clips/skema_{name}.mp4")
