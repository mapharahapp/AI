"""Framing and animations for Titik Heran #33 (run in the episode work dir after
`dl.py i:3258364 i:5536858 i:961977 i:5396848 i:1340187`; writes img/3258364v.jpg, img/3258364es.jpg, img/5536858v.jpg,
clips/skema_gigi.mp4, clips/skema_ukuran.mp4
and clips/skema_globe.mp4).
usage: python3 skema33.py [es|sakit|gigi|ukuran|globe ...] [--sheet out.jpg t1,t2,...]   (--sheet saves those frames as a contact sheet)
es: the hook photo of green areca nuts (Pixabay 3258364) framed so the cut nuts sit under the title (img/3258364v.jpg), and the
same frame with a frost rim and ice crystals growing in from the edges (img/3258364es.jpg), for the cut on "zaman es".
sakit: the man with toothache (Pixabay 5536858) set lower in the frame so the title clears his eyes; the wall above is continued.
skema_gigi: a panoramic dental X-ray (Pixabay 961977, a modern X-ray, not the Sulawesi teeth) pushes in; on "dengan" it dims
under a diagram of three lower teeth, on "lekukan" a round scoop in their crowns lights up, on "bulat" a dashed circle completes
its round shape, on "aneh" a question mark pops. The teeth and the scoop are drawn to show the idea, not traced from the find.
skema_ukuran: dried areca nuts (Pixabay 5396848) framed higher, the table continued below the photo by stretching its plain
bottom edge; on "pinang" a dashed circle locks on one nut and turns, on "utuh" a "10-20 mm" label pops (the size of the
hard round object the notches fit, as the researchers describe it).
skema_globe: a lit globe (Pixabay 1340187) pushes in on Sulawesi; on "tertua" the frame jolts and a pulsing gold dot lands on
South Sulawesi (Maros), on "dunia" its label pops to the left of it.
Event times are seconds from the start of each clip, read off `render.py 33 plan`: skema_gigi starts at 9,87 s (shot 4),
skema_ukuran at 13,27 s (shot 5), skema_globe at 22,67 s (shot 8).
"""
import io, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, BOLD, YELLOW, WHITE, ramp, pop, layer, down, sc, fade, put, glow_sprite, encode, text_sprite, chaikin

N = {"gigi": 105, "ukuran": 123, "globe": 90}
GOLD = (255, 200, 60)


def cover_blur(im, dark=0.45, blur=28):
    """the photo scaled to fill the frame, blurred and darkened, as a backdrop"""
    s = max(W / im.width, H / im.height)
    b = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    b = b.crop(((b.width - W) // 2, (b.height - H) // 2, (b.width - W) // 2 + W, (b.height - H) // 2 + H))
    b = b.filter(ImageFilter.GaussianBlur(blur))
    return Image.fromarray((np.asarray(b, np.float32) * dark).astype(np.uint8))


def place(base, im, s, ax, ay, fx, fy, feather=0, bottom=True):
    """paste im scaled by s so that its point (ax, ay) lands on frame point (fx, fy); feather softens its top edge, and its
    bottom edge too unless bottom is False"""
    w, h = round(im.width * s), round(im.height * s)
    x0, y0 = round(fx - ax * s), round(fy - ay * s)
    # crop to the visible part before resizing, so big scales stay cheap
    cx0, cy0 = max(0, -x0), max(0, -y0)
    cx1, cy1 = min(w, W - x0), min(h, H - y0)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    box = (cx0 / s, cy0 / s, min(cx1 / s, im.width), min(cy1 / s, im.height))
    part = im.resize((cx1 - cx0, cy1 - cy0), Image.LANCZOS, box=box)
    if feather:
        a = np.ones((cy1 - cy0, cx1 - cx0), np.float32)
        yy = np.arange(cy0, cy1, dtype=np.float32)[:, None]
        a *= np.clip(yy / feather, 0, 1) * (np.clip((h - yy) / feather, 0, 1) if bottom else 1)
        base.paste(part, (x0 + cx0, y0 + cy0), Image.fromarray((a * 255).astype(np.uint8)))
    else:
        base.paste(part, (x0 + cx0, y0 + cy0))


# ---------- es: the hook photo with a frost rim ----------
def hook_frame():
    """the photo fitted to the frame's width and set low enough that the cut nuts sit under the title; the 183 px above it
    continue the nuts with the photo's own top rows, mirrored, blurred and a little darker, so no seam shows"""
    im = Image.open("img/3258364.jpg").convert("RGB")
    s = W / im.width
    ph = im.resize((W, round(im.height * s)), Image.LANCZOS)
    over = H - ph.height
    ext = Image.new("RGB", (W, H))
    ext.paste(ph, (0, over))
    ext.paste(ph.crop((0, 0, W, over)).transpose(Image.FLIP_TOP_BOTTOM), (0, 0))
    a = np.asarray(ext, np.float32)
    soft = np.asarray(ext.filter(ImageFilter.GaussianBlur(12)), np.float32)
    y = np.arange(H, dtype=np.float32)[:, None, None]
    blur = np.clip((over + 50 - y) / 90, 0, 1)
    dark = 1 - 0.35 * np.clip((over + 20 - y) / (over + 20), 0, 1)
    return Image.fromarray(np.clip((a * (1 - blur) + soft * blur) * dark, 0, 255).astype(np.uint8))


def octave(rng, n):
    g = rng.random((max(2, round(n * H / W)) + 2, n + 2)).astype(np.float32)
    return np.asarray(Image.fromarray(g, "F").resize((W, H), Image.BICUBIC))


def frost():
    rng = np.random.default_rng(33)
    base = hook_frame()
    base.save("img/3258364v.jpg", quality=94)
    print("img/3258364v.jpg")
    img = np.asarray(base, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.minimum.reduce([xx, W - 1 - xx, yy, H - 1 - yy])
    nz = 0.5 * octave(rng, 5) + 0.3 * octave(rng, 13) + 0.2 * octave(rng, 37)
    reach = 120 + 230 * nz  # the rim's depth wanders along the edge
    rim = np.clip(1 - d / reach, 0, 1) ** 1.5 * (0.55 + 0.45 * octave(rng, 60))
    # ice crystals: thin feathery strokes growing in from the edges, with side branches
    cr = Image.new("L", (W * S, H * S), 0)
    dr = ImageDraw.Draw(cr)
    for _ in range(520):
        side = rng.integers(4)
        u = rng.random()
        x, y, ang = [(u * W, 0, 90), (u * W, H, -90), (0, u * H, 0), (W, u * H, 180)][side]
        ang = math.radians(ang + rng.uniform(-55, 55))
        L = rng.uniform(40, 230) * (0.6 + 0.8 * rng.random())
        a = int(rng.uniform(90, 200))

        def stroke(x, y, ang, L, a, wdt, depth):
            x1, y1 = x + L * math.cos(ang), y + L * math.sin(ang)
            dr.line([(x * S, y * S), (x1 * S, y1 * S)], fill=a, width=wdt)
            if depth:
                for f in (0.3, 0.55, 0.78):
                    bx, by = x + f * L * math.cos(ang), y + f * L * math.sin(ang)
                    for sgn in (-1, 1):
                        stroke(bx, by, ang + sgn * math.radians(rng.uniform(45, 70)), L * 0.32 * (1 - f * 0.6),
                               int(a * 0.8), max(1, wdt - 1), depth - 1)
        stroke(x, y, ang, L, a, 3, 2)
    cr = np.asarray(cr.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255
    cr *= np.clip(1 - d / 330, 0, 1) ** 0.8  # crystals thin out toward the middle
    A = np.clip(0.85 * rim + 0.7 * cr, 0, 0.93)[..., None]
    ice = np.array([226, 240, 255], np.float32)
    cool = img * 0.9 + np.array([10, 22, 40], np.float32)  # the whole photo a touch colder
    out = cool * (1 - A) + ice * A
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save("img/3258364es.jpg", quality=94)
    print("img/3258364es.jpg")


# ---------- sakit: the toothache photo set lower ----------
def sakit_frame():
    """Pixabay 5536858 at 2x with the face centred and set 214 px lower, so the title clears the eyes. Behind it, the grey wall
    continues: the photo's top row (the hair bridged by the wall on either side), smoothed and carried up the frame, a little
    darker toward the top; the photo's top edge fades into it, so the top of his hair goes soft instead of cut"""
    im = Image.open("img/5536858.jpg").convert("RGB")
    s, fx, top = 2.0, 688, 214
    ph = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0 = round(fx * s - W / 2)
    row = np.asarray(ph.crop((x0, 0, x0 + W, 8)), np.float32).mean(0)  # (W, 3)
    good = row.mean(1) > 150  # the wall, not the hair
    idx = np.arange(W)
    wall = np.stack([np.interp(idx, idx[good], row[good, c]) for c in range(3)], 1)
    wall = np.asarray(Image.fromarray(wall[None].astype(np.uint8)).filter(ImageFilter.GaussianBlur(30)), np.float32)[0]
    yy = np.arange(H, dtype=np.float32)[:, None, None]
    bg = np.repeat(wall[None], H, 0) * (0.84 + 0.16 * np.clip(yy / top, 0, 1))
    bg += np.random.default_rng(5).normal(0, 2.0, bg.shape)  # grain, so the wall doesn't look painted
    bg = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))
    place(bg, im, s, fx, 0, W / 2, top, feather=110, bottom=False)
    bg.save("img/5536858v.jpg", quality=94)
    print("img/5536858v.jpg")


# ---------- skema_gigi ----------
XRAY_CROP = (38, 0, 1246, 574)  # the X-ray without its white border
XR_ANCHOR = (604, 330)  # a point between the tooth rows (crop coordinates) that stays put while the camera pushes in
XR_AT = (540, 880)
NOTCH = (420, 774, 82)  # the round scoop in the crowns: centre x, y and radius (frame coordinates)


def tooth_outline(cx, top, w, crown_h, root_len, roots):
    """a lower tooth seen from the side: crown up, roots down, as a smoothed closed outline (1x)"""
    nk, ny = 0.41 * w, top + crown_h
    if roots == 2:
        crown = [(cx - w / 2 + 4, top + crown_h * 0.55), (cx - w / 2 + 10, top + 24), (cx - w * 0.25, top),
                 (cx, top + 18), (cx + w * 0.25, top), (cx + w / 2 - 10, top + 24), (cx + w / 2 - 4, top + crown_h * 0.55)]
        root = [(cx + nk, ny), (cx + w * 0.36, ny + root_len * 0.55), (cx + w * 0.27, ny + root_len), (cx + w * 0.13, ny + root_len * 0.52),
                (cx + 0.02 * w, ny + 46), (cx - w * 0.12, ny + root_len * 0.52), (cx - w * 0.27, ny + root_len * 0.96),
                (cx - w * 0.37, ny + root_len * 0.55), (cx - nk, ny)]
    else:
        crown = [(cx - w / 2 + 6, top + crown_h * 0.55), (cx - w / 2 + 16, top + 30), (cx, top - 4),
                 (cx + w / 2 - 16, top + 30), (cx + w / 2 - 6, top + crown_h * 0.55)]
        root = [(cx + nk, ny), (cx + w * 0.3, ny + root_len * 0.6), (cx + w * 0.06, ny + root_len), (cx - w * 0.08, ny + root_len * 0.97),
                (cx - w * 0.3, ny + root_len * 0.6), (cx - nk, ny)]
    return chaikin(crown + root, 3)


TEETH = [(318, 772, 168, 140, 230, 1), (548, 760, 236, 150, 250, 2), (790, 766, 224, 146, 240, 2)]


def teeth_layers():
    """the diagram at 2x: teeth (with the scoop cut out), the gum in front of their necks, the bone behind their roots"""
    full = Image.new("L", (W * S, H * S), 0)
    for t in TEETH:
        ImageDraw.Draw(full).polygon(sc(tooth_outline(*t)), fill=255)
    nx, ny, nr = NOTCH
    cut = full.copy()
    ImageDraw.Draw(cut).ellipse([(nx - nr) * S, (ny - nr) * S, (nx + nr) * S, (ny + nr) * S], fill=0)
    # shading: enamel crowns brighter than the roots, a soft highlight down the left side of each tooth
    yy = np.arange(H * S, dtype=np.float32)[:, None, None] / S
    tone = np.where(yy < 905, np.array([246, 240, 222], np.float32), np.array([214, 200, 172], np.float32))
    tone = np.broadcast_to(tone, (H * S, W * S, 3)).copy()
    m = np.asarray(cut, np.float32) / 255
    edge = np.asarray(cut.filter(ImageFilter.GaussianBlur(14 * S)), np.float32) / 255
    tone *= (0.82 + 0.18 * edge)[..., None]  # darker toward the outline: a little volume
    teeth = np.dstack([tone, m * 255]).astype(np.uint8)
    teeth = Image.fromarray(teeth, "RGBA")
    # white outline
    ol = cut.filter(ImageFilter.MaxFilter(7)).point(lambda v: 255 if v > 0 else 0)
    ol = np.clip(np.asarray(ol, np.float32) - np.asarray(cut, np.float32), 0, 255)
    outline = Image.fromarray(np.dstack([np.full(ol.shape + (3,), 255, np.float32), ol]).astype(np.uint8), "RGBA")
    teeth.alpha_composite(outline)
    back = layer()
    db = ImageDraw.Draw(back)
    db.rounded_rectangle(sc([(150, 930), (930, 1175)]), radius=40 * S, fill=(150, 160, 180, 70))  # bone
    gum = layer()
    pts = [(150, 950)]
    for x in range(150, 931, 10):  # the gum line rises a little between the teeth
        pts.append((x, 900 + 10 * math.cos((x - 318) / 115 * math.pi)))
    pts += [(930, 950)]
    ImageDraw.Draw(gum).polygon(sc(pts), fill=(214, 96, 112, 175))
    return back, teeth, gum, full


def notch_arc():
    """points along the scoop's edge inside the teeth, left to right (1x)"""
    nx, ny, nr = NOTCH
    full = teeth_layers.full
    pts = []
    for k in range(0, 181):
        a = math.radians(180 - k)
        x, y = nx + nr * math.cos(a), ny + nr * math.sin(a)  # lower half: y grows downward
        if full.getpixel((min(W * S - 1, int(x * S)), min(H * S - 1, int(y * S)))):
            pts.append((x, y))
    return pts


def xray_frame(t, xr, bg):
    im = bg.copy()
    s = (1450 / xr.width) * (1 + 0.07 * ramp(t, 0, 3.4))
    place(im, xr, s, XR_ANCHOR[0], XR_ANCHOR[1], XR_AT[0], XR_AT[1], feather=40)
    return im


def skema_gigi(times=None):
    xr = Image.open("img/961977.jpg").convert("RGB").crop(XRAY_CROP)
    bg = cover_blur(xr, 0.35)
    back, teeth, gum, full = teeth_layers()
    teeth_layers.full = full
    arc = notch_arc()
    nx, ny, nr = NOTCH
    t_dim, t_notch, t_round, t_q = 1.62, 1.94, 2.31, 2.91
    q = text_sprite([("?", 150, YELLOW, True)])
    frames = []
    for i in range(N["gigi"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        im = xray_frame(t, xr, bg).convert("RGBA")
        k = ramp(t, t_dim, t_dim + 0.3)
        if k > 0:
            # the X-ray dims and a dark panel comes up behind the diagram
            dim = Image.new("RGBA", (W, H), (6, 14, 30, int(150 * k)))
            im.alpha_composite(dim)
            g = layer()
            ImageDraw.Draw(g).rounded_rectangle(sc([(110, 600), (970, 1190)]), radius=36 * S, fill=(12, 30, 62, int(215 * k)),
                                                outline=(255, 255, 255, int(70 * k)), width=3 * S)
            im.alpha_composite(down(g))
            lift = (1 - pop(t, t_dim, 0.4)) * 40  # the teeth rise into place
            dia = layer()
            dia.alpha_composite(back)
            dia.alpha_composite(teeth)
            dia.alpha_composite(gum)
            dia = down(dia)
            dia = fade(dia, k) if k < 1 else dia
            im.alpha_composite(dia, (0, round(lift)))
        u = ramp(t, t_notch, t_notch + 0.36)
        if u > 0 and len(arc) > 1:
            # the scoop's edge draws on from left to right and glows
            n = max(2, round(len(arc) * u))
            g = layer()
            ImageDraw.Draw(g).line(sc(arc[:n]), fill=YELLOW + (255,), width=9 * S, joint="curve")
            glow = g.filter(ImageFilter.GaussianBlur(9 * S))
            pulse = 0.75 + 0.25 * math.sin(max(0, t - t_notch) * 7)
            im.alpha_composite(down(fade(glow, min(1, 1.6 * pulse))))
            im.alpha_composite(down(g))
        v = ramp(t, t_round, t_round + 0.4)
        if v > 0:
            # a dashed circle completes the round shape the scoop belongs to
            g = layer()
            d = ImageDraw.Draw(g)
            span = 360 * v
            for a0 in range(0, 360, 20):
                if a0 >= span:
                    break
                a1 = min(a0 + 12, span)
                d.arc([(nx - nr) * S, (ny - nr) * S, (nx + nr) * S, (ny + nr) * S], start=180 + a0, end=180 + a1,
                      fill=(255, 225, 0, 235), width=5 * S)
            im.alpha_composite(down(g))
        if t >= t_q:
            sw = 1 + 0.06 * math.sin((t - t_q) * 9) * math.exp(-(t - t_q) * 2)
            g = layer()
            put(g, q, nx + 6, 625, a=1.0, scale=pop(t, t_q, 0.35) * sw)
            im.alpha_composite(down(g))
        frames.append(im.convert("RGB"))
    return frames


# ---------- skema_ukuran ----------
NUT = (522, 557)  # the front nut's centre in the photo
NUT_AT = (540, 930)
RING = 250  # the dashed circle's radius in the frame


def nut_photo():
    """the photo continued below its bottom edge: the plain table along that edge stretched downward, blurred and a little darker
    (mirroring would bring the nuts' shadows back into the frame)"""
    im = Image.open("img/5396848.jpg").convert("RGB")
    over, strip = 260, 50
    ext = Image.new("RGB", (im.width, im.height + over))
    ext.paste(im, (0, 0))
    ext.paste(im.crop((0, im.height - strip, im.width, im.height)).resize((im.width, over), Image.BICUBIC), (0, im.height))
    a = np.asarray(ext, np.float32)
    soft = np.asarray(ext.filter(ImageFilter.GaussianBlur(10)), np.float32)
    y = np.arange(ext.height, dtype=np.float32)[:, None, None]
    blur = np.clip((y - (im.height - 40)) / 80, 0, 1)
    dark = 1 - 0.4 * np.clip((y - (im.height - 20)) / (over + 20), 0, 1) ** 1.2
    return Image.fromarray(np.clip((a * (1 - blur) + soft * blur) * dark, 0, 255).astype(np.uint8))


def skema_ukuran(times=None):
    ph = nut_photo()
    t_ring, t_label = 1.80, 2.10
    cx, cy = NUT_AT
    lab = text_sprite([("Ø 10–20 mm", 50, YELLOW, True)])
    frames = []
    for i in range(N["ukuran"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        im = Image.new("RGB", (W, H))
        s = 2.0 * (1 + 0.06 * ramp(t, 0, 4.1))
        place(im, ph, s, NUT[0], NUT[1], cx, cy)
        im = im.convert("RGBA")
        u = ramp(t, t_ring, t_ring + 0.35)
        if u > 0:
            # everything outside the circle darkens a little, so the eye goes to the nut
            yy, xx = np.ogrid[0:H, 0:W]
            r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
            sh = (np.clip((r - RING) / 60, 0, 1) * 105 * u).astype(np.uint8)
            im.alpha_composite(Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), sh]), "RGBA"))
            g = layer()
            d = ImageDraw.Draw(g)
            spin = max(0.0, t - t_ring - 0.35) * 24  # degrees: the dashes keep turning, like the nut turned in the mouth
            span = 360 * u
            for a0 in range(0, 360, 15):
                if a0 >= span:
                    break
                a1 = min(a0 + 9, span)
                d.arc([(cx - RING) * S, (cy - RING) * S, (cx + RING) * S, (cy + RING) * S], start=-90 + a0 + spin,
                      end=-90 + a1 + spin, fill=(255, 225, 0, 245), width=7 * S)
            glow = g.filter(ImageFilter.GaussianBlur(7 * S))
            im.alpha_composite(down(fade(glow, 0.8)))
            im.alpha_composite(down(g))
        if t >= t_label:
            k = pop(t, t_label, 0.35)
            g = layer()
            # a short leader from the circle's lower left to the label
            a = math.radians(140)
            p0 = (cx + RING * math.cos(a), cy + RING * math.sin(a))
            p1 = (232, 1092)
            ImageDraw.Draw(g).line(sc([p0, (p0[0] + (p1[0] - p0[0]) * min(1, k), p0[1] + (p1[1] - p0[1]) * min(1, k))]),
                                   fill=(255, 225, 0, 230), width=4 * S)
            put(g, lab, 175, 1112, a=min(1, k), scale=max(0.01, k))
            im.alpha_composite(down(g))
        frames.append(im.convert("RGB"))
    return frames


# ---------- skema_globe ----------
SULSEL = (679, 584)  # South Sulawesi (Maros, near the map's "Ujung Pandang") on the globe photo
DOT_AT = (540, 1090)


def skema_globe(times=None):
    ph = Image.open("img/1340187.jpg").convert("RGB")
    bg = cover_blur(ph, 0.4)
    t_hit, t_label = 0.70, 1.37
    lab = text_sprite([("MAROS, SULAWESI", 44, WHITE, True)])
    dot = glow_sprite(30, GOLD)
    frames = []
    for i in range(N["globe"]):
        t = i / FPS
        if times is not None and not any(abs(t - x) < 0.5 / FPS for x in times):
            frames.append(None)
            continue
        im = bg.copy()
        s = 1.2 * (1 + 0.16 * ramp(t, 0, 3.0))
        if t >= t_hit:  # the jolt on "tertua"
            s *= 1 + 0.12 * math.exp(-(t - t_hit) / 0.14)
        place(im, ph, s, SULSEL[0], SULSEL[1], DOT_AT[0], DOT_AT[1], feather=70)
        im = im.convert("RGBA")
        if t >= t_hit:
            g = layer()
            dx, dy = DOT_AT
            for k in range(4):  # rings ripple out from the dot
                tt = t - t_hit - k * 0.5
                if tt > 0:
                    r = 22 + tt * 150
                    a = int(230 * max(0.0, 1 - tt / 1.1))
                    if a > 0:
                        ImageDraw.Draw(g).ellipse([(dx - r) * S, (dy - r) * S, (dx + r) * S, (dy + r) * S],
                                                  outline=GOLD + (a,), width=5 * S)
            k = pop(t, t_hit, 0.3)
            put(g, dot, dx, dy, a=0.9, scale=k * (1 + 0.12 * math.sin((t - t_hit) * 8)))
            core = Image.new("RGBA", (40 * S, 40 * S))
            ImageDraw.Draw(core).ellipse([4 * S, 4 * S, 36 * S, 36 * S], fill=GOLD + (255,), outline=(255, 255, 255, 255), width=4 * S)
            put(g, core, dx, dy, scale=max(0.01, k))
            if t >= t_label:
                kk = pop(t, t_label, 0.35)
                # to the left of the dot, so Sulawesi itself stays in view
                put(g, lab, dx - 38 - lab.width / S / 2 + 24, dy, a=min(1, kk), scale=max(0.01, kk))
            im.alpha_composite(down(g))
        frames.append(im.convert("RGB"))
    return frames


def sheet(frames, name, times, out):
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
    todo = args or ["es", "sakit", "gigi", "ukuran", "globe"]
    if "es" in todo:
        frost()
    if "sakit" in todo:
        sakit_frame()
    for name, fn in [("gigi", skema_gigi), ("ukuran", skema_ukuran), ("globe", skema_globe)]:
        if name in todo:
            fr = fn(times)
            if times is not None:
                sheet(fr, name, times, out)
            else:
                encode(fr, f"clips/skema_{name}.mp4")
