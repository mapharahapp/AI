"""Schematic animations for Titik Heran #21 (run in the episode work dir; writes clips/skema_bangka.mp4 and clips/skema_selamat.mp4).
usage: python3 skema21.py GEO_DIR [bangka|selamat ...] [--sheet out.jpg t1,t2,...]   (GEO_DIR holds ne_10m_land.geojson from
       github.com/nvkelso/natural-earth-vector, folder geojson/; --sheet saves those frames as a contact sheet)
skema_bangka: Bangka Island off the east coast of South Sumatra, from the Natural Earth coastlines; a card names the Bangka slow loris
(Nycticebus bancanus), then an archive card gives its last scientific record, 1930-1932, in the Dutch colonial era (Re:wild, Reuters).
skema_selamat: the Alobi wildlife rescue centre on Bangka took in more than 90 Bangka slow lorises in 2015-2025 (Spixiana 2026,
via Reuters): one loris icon per animal, 90 in all, and the count runs up to "90+".
Event times are seconds from the start of each shot, read off `render.py 21 plan`.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, BOLD, MED, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, fade, put, encode
from skema13 import navy, marker
from skema17 import ring, label

GEO = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in ("bangka", "selamat") else "geo"
K, LON0, LAT0, CY = 300, 105.95, -2.3, 880  # pixels per degree; Bangka's middle sits at (540, CY)
FUR, PATCH, EYE, STRIPE = (178, 140, 98), (92, 62, 40), (236, 176, 62), (244, 236, 222)


def xy(lon, lat):
    return 540 + (lon - LON0) * K, CY + (LAT0 - lat) * K


def loris_sprite(r):
    """a slow loris face as an icon of radius r (1x): round head, dark eye rings, a pale stripe down the nose"""
    im = Image.new("RGBA", (round(3 * r * S), round(3 * r * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = 1.5 * r * S

    def e(x, y, rx, ry, fill):
        d.ellipse([c + (x - rx) * S, c + (y - ry) * S, c + (x + rx) * S, c + (y + ry) * S], fill=fill)
    for sx in (-1, 1):
        e(sx * 0.78 * r, -0.62 * r, 0.3 * r, 0.3 * r, PATCH + (255,))
    e(0, 0, r, 0.92 * r, FUR + (255,))
    for sx in (-1, 1):
        e(sx * 0.4 * r, -0.12 * r, 0.33 * r, 0.36 * r, PATCH + (255,))
        e(sx * 0.4 * r, -0.12 * r, 0.21 * r, 0.21 * r, EYE + (255,))
        e(sx * 0.4 * r, -0.12 * r, 0.1 * r, 0.1 * r, (20, 14, 10, 255))
        e(sx * 0.35 * r, -0.19 * r, 0.05 * r, 0.05 * r, (255, 255, 255, 230))
    d.polygon([(c - 0.09 * r * S, c - 0.85 * r * S), (c + 0.09 * r * S, c - 0.85 * r * S), (c + 0.12 * r * S, c + 0.32 * r * S),
               (c - 0.12 * r * S, c + 0.32 * r * S)], fill=STRIPE + (255,))
    e(0, 0.42 * r, 0.16 * r, 0.11 * r, (60, 40, 30, 255))
    return im


def card(lines, icon_r=44, box=(8, 24, 54, 225), edge=YELLOW + (230,)):
    """a rounded navy card: a loris icon on the left, text lines on the right"""
    tx = text_sprite(lines, gap=6)
    ic = loris_sprite(icon_r)
    pad = 26 * S
    w = ic.width + tx.width + pad
    h = max(ic.height, tx.height) + 10 * S
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([6 * S, 6 * S, w - 6 * S, h - 6 * S], radius=22 * S, fill=box, outline=edge, width=4 * S)
    im.alpha_composite(ic, (pad // 2, (h - ic.height) // 2))
    im.alpha_composite(tx, (pad // 2 + ic.width - 12 * S, (h - tx.height) // 2))
    return im


def archive_card():
    """an old paper record card, slightly turned"""
    w, h = 660, 360
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(21)
    edge = [(14 + rng.uniform(-3, 3), 14 + rng.uniform(-3, 3)), (w - 14 + rng.uniform(-3, 3), 12), (w - 12, h - 14 + rng.uniform(-3, 3)),
            (16 + rng.uniform(-3, 3), h - 12)]
    d.polygon([(x * S, y * S) for x, y in edge], fill=(236, 222, 184, 255), outline=(170, 146, 104, 255))
    stains = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(stains)
    for _ in range(9):
        x, y, r = rng.uniform(60, w - 60), rng.uniform(50, h - 50), rng.uniform(26, 70)
        sd.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(196, 170, 120, 40))
    stains = stains.filter(ImageFilter.GaussianBlur(14 * S))
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon([(x * S, y * S) for x, y in edge], fill=255)
    stains.putalpha(Image.fromarray(np.minimum(np.array(stains.getchannel("A")), np.array(mask)).astype(np.uint8)))
    im.alpha_composite(stains)
    d = ImageDraw.Draw(im)
    d.rectangle([34 * S, 34 * S, (w - 34) * S, (h - 34) * S], outline=(150, 120, 80, 200), width=2 * S)
    ink = (84, 56, 34, 255)
    d.text((w / 2 * S, 92 * S), "CATATAN ILMIAH TERAKHIR", font=ImageFont.truetype(BOLD, 32 * S), fill=ink, anchor="mm")
    d.text((w / 2 * S, 178 * S), "1930–1932", font=ImageFont.truetype(BOLD, 96 * S), fill=(140, 40, 26, 255), anchor="mm")
    d.text((w / 2 * S, 262 * S), "zaman Hindia Belanda", font=ImageFont.truetype(MED, 36 * S), fill=ink, anchor="mm")
    return im.rotate(3, resample=Image.BICUBIC, expand=True)


# ---------- skema_bangka ----------
def bangka_land():
    rings = []
    for f in json.load(open(os.path.join(GEO, "ne_10m_land.geojson")))["features"]:
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            lon = [p[0] for p in poly[0]]
            lat = [p[1] for p in poly[0]]
            if max(lon) > 103.0 and min(lon) < 109.0 and max(lat) > -7.0 and min(lat) < 1.5:
                rings.append(poly[0])
    isl = min(rings, key=lambda r: math.dist((sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r)), (106.05, -2.3))
              if len(r) > 200 else 99)
    return rings, isl


def bangka(times):
    rings, isl = bangka_land()
    bg = navy(540, CY, [xy(lon, 0)[0] for lon in range(104, 109)], [xy(0, lat)[1] for lat in range(1, -7, -1)])
    land = layer()
    d = ImageDraw.Draw(land)
    for r in rings:
        hot = r is isl
        d.polygon(sc([xy(*p) for p in r]), fill=(222, 200, 150, 255) if hot else (150, 134, 102, 255),
                  outline=(120, 100, 68, 255) if hot else (96, 84, 62, 255))
    land = down(land)
    coast = [xy(*p) for p in isl]
    lab_sum = text_sprite([("SUMATRA", 44, (64, 52, 32), True)])
    lab_isl = text_sprite([("PULAU BANGKA", 46, WHITE, True)])
    kartu = card([("Kukang Bangka", 42, WHITE, True), ("Nycticebus bancanus", 30, YELLOW, False)])
    arsip = archive_card()
    dot = marker()
    pin = xy(106.12, -2.12)
    # Namanya 0.05, kukang 0.74, Bangka 1.20, Catatan 2.05, ilmiah 2.55, terakhirnya 2.90, dari 3.52, zaman 3.75, Belanda 3.98
    t_card, t_isl, t_arc, t_zaman = 0.74, 1.20, 2.05, 3.75
    frames = []
    for t in times:
        im = bg.copy()
        im.alpha_composite(fade(land, ramp(t, 0.0, 0.25)))
        glow = layer()
        dg = ImageDraw.Draw(glow)
        top = layer()
        d = ImageDraw.Draw(top)
        hv = ramp(t, t_isl, t_isl + 0.3)
        if hv > 0:
            boost = 1 + 0.4 * math.exp(-((t - t_isl - 0.3) / 0.25) ** 2)
            dg.line(sc(coast + coast[:1]), fill=YELLOW + (round(170 * hv * boost),), width=round(26 * boost) * S, joint="curve")
            d.line(sc(coast + coast[:1]), fill=YELLOW + (round(255 * hv),), width=5 * S, joint="curve")
        im.alpha_composite(down(glow).filter(ImageFilter.GaussianBlur(8)))
        put(top, lab_sum, *xy(104.55, -3.55), a=ramp(t, 0.15, 0.4))
        put(top, lab_isl, 800, 680, a=ramp(t, t_isl, t_isl + 0.2), scale=pop(t, t_isl))
        if t >= t_isl:
            for ph0 in (0.0, 0.5):
                ph = ((t - t_isl + ph0) % 1.0) / 1.0
                ring(d, pin[0], pin[1], 16 + 60 * ph, YELLOW, 230 * (1 - ph) ** 1.5, w=4)
            put(top, dot, *pin, scale=pop(t, t_isl))
        ca = ramp(t, t_card, t_card + 0.15) * (1 - ramp(t, t_arc - 0.1, t_arc + 0.1))
        put(top, kartu, 540, 1130, a=ca, scale=pop(t, t_card))  # clear of the two-line caption below
        im.alpha_composite(down(top))
        dim = ramp(t, t_arc, t_arc + 0.25)
        if dim > 0:  # the map steps back for the archive card
            im.alpha_composite(Image.new("RGBA", (W, H), (6, 16, 36, round(150 * dim))))
            top = layer()
            d = ImageDraw.Draw(top)
            put(top, arsip, 540, 900, a=dim, scale=pop(t, t_arc))
            ua = ramp(t, t_zaman, t_zaman + 0.3)
            if ua > 0:  # underline "zaman Hindia Belanda"
                d.line(sc([(372, 1018), (372 + 336 * ua, 1018 - 336 * ua * math.tan(math.radians(3)))]), fill=(200, 60, 40, 230), width=6 * S)
            im.alpha_composite(down(top))
        frames.append(im)
    return frames


# ---------- skema_selamat ----------
def selamat(times):
    bg = navy(540, 900)
    icon = loris_sprite(26)
    cols, rows, x0, y0, dx, dy = 15, 6, 78, 900, 66, 62
    cells = [(x0 + dx * (k % cols), y0 + dy * (k // cols)) for k in range(cols * rows)]
    head = text_sprite([("Pusat Penyelamatan Satwa Alobi, Bangka", 30, WHITE, False)])
    yr0, yr1 = text_sprite([("2015", 40, YELLOW, True)]), text_sprite([("2025", 40, YELLOW, True)])
    f_num = ImageFont.truetype(BOLD, 150 * S)
    # Sepuluh 0.04, tahun 0.41, terakhir 0.64, sekitar 1.41, sembilan 1.80, puluh 2.19, ekor 2.42, diselamatkan 2.84
    t_line, t_c0, t_c1 = 0.05, 1.41, 2.84
    frames = []
    for t in times:
        im = bg.copy()
        top = layer()
        d = ImageDraw.Draw(top)
        u = ramp(t, t_line, t_line + 0.6)
        xa, xb, yl = 250, 830, 610
        if u > 0:
            d.line(sc([(xa, yl), (xa + (xb - xa) * u, yl)]), fill=YELLOW + (255,), width=6 * S)
            for x, t0 in ((xa, t_line), (xb, t_line + 0.6)):
                if t >= t0:
                    r = 11 * pop(t, t0)
                    d.ellipse(sc([(x - r, yl - r), (x + r, yl + r)]), fill=YELLOW + (255,))
        put(top, yr0, xa - 95, yl, a=ramp(t, t_line, t_line + 0.15))
        put(top, yr1, xb + 95, yl, a=ramp(t, t_line + 0.55, t_line + 0.7))
        put(top, head, 540, yl + 58, a=ramp(t, 0.2, 0.45))
        c = min(max((t - t_c0) / (t_c1 - t_c0), 0.0), 1.0)  # linear, so the count matches the icons
        n = int(round(90 * c))
        if t >= t_c0:
            txt = "90+" if t >= t_c1 else str(n)
            s = pop(t, t_c1) if t >= t_c1 else 1.0
            num = Image.new("RGBA", (600 * S, 200 * S), (0, 0, 0, 0))
            nd = ImageDraw.Draw(num)
            nd.text((303 * S, 106 * S), txt, font=f_num, fill=(0, 0, 0, 170), anchor="mm")
            nd.text((300 * S, 100 * S), txt, font=f_num, fill=YELLOW + (255,), anchor="mm")
            put(top, num, 540, 775, scale=s)
        for k, (x, y) in enumerate(cells):
            tk = t_c0 + (t_c1 - t_c0) * k / 90
            if t >= tk:
                put(top, icon, x, y, scale=pop(t, tk, 0.2))
        im.alpha_composite(down(top))
        frames.append(im)
    return frames


N = {"bangka": 150, "selamat": 124}
if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != GEO]
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
            encode(globals()[name]([i / FPS for i in range(N[name])]), f"clips/skema_{name}.mp4")
