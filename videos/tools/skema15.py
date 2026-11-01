"""Schematic maps for Titik Heran #15 (run in the episode work dir; writes clips/skema_riwayat.mp4 and clips/skema_orbit.mp4).
usage: python3 skema15.py GEO_DIR [riwayat|orbit ...]   (GEO_DIR holds ne_50m_land.geojson and ne_50m_admin_0_countries.geojson
       from github.com/nvkelso/natural-earth-vector, folder geojson/)
skema_riwayat: space debris that fell on Indonesia since 1981 in the LAPAN/BRIN record: Gorontalo 1981, Lampung 1988,
Bengkulu Utara 2003, Sumenep 2016, Agam 2017, Sanggau 2022 and near Sampit 2026; each marker sits on the town or regency.
skema_orbit: example ground tracks (inclination 28,5°, 42° and 51,6°, the Earth turning ±23° per orbit) on a world map.
Every orbit crosses the equator; the map then zooms in on Indonesia, which lies along it.
Event times are seconds from the start of each shot, read off `render.py 15 plan`.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skema11 import W, H, FPS, S, YELLOW, WHITE, ramp, pop, layer, down, sc, text_sprite, put, dashed, encode
from skema13 import navy, marker

GEO = sys.argv[1] if len(sys.argv) > 1 else "geo"
CY = 930


def polys(path, keep=lambda p: True):
    """outer rings of the (multi)polygons of a geojson file whose properties pass `keep`"""
    out = []
    for f in json.load(open(os.path.join(GEO, path)))["features"]:
        if not keep(f["properties"]):
            continue
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            out.append(poly[0])
    return out


def chip(year, place):
    """a year over a place name on a navy tag"""
    tx = text_sprite([(year, 48, YELLOW, True), (place, 31, WHITE, False)], gap=2)
    bw, bh = tx.width - 22 * S, tx.height - 30 * S
    box = Image.new("RGBA", tx.size, (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([(tx.width - bw) // 2, (tx.height - bh) // 2, (tx.width + bw) // 2, (tx.height + bh) // 2],
                                          radius=14 * S, fill=(8, 24, 54, 215), outline=(255, 255, 255, 70), width=2 * S)
    box.alpha_composite(tx)
    return box


def riwayat(n=192):
    K, LON0 = 23.5, 118.0

    def xy(lon, lat):
        return 540 + (lon - LON0) * K, CY - lat * K
    near = lambda p: True
    countries = polys("ne_50m_admin_0_countries.geojson", near)
    indo = polys("ne_50m_admin_0_countries.geojson", lambda p: p["ADMIN"] == "Indonesia")
    inwin = lambda r: max(x for x, _ in r) > 85 and min(x for x, _ in r) < 152 and max(y for _, y in r) > -25 and min(y for _, y in r) < 25
    bg = navy(540, CY, [xy(lon, 0)[0] for lon in (100, 110, 120, 130, 140)], [xy(0, lat)[1] for lat in (10, -10, -20)])
    g = layer()
    d = ImageDraw.Draw(g)
    for r in countries:
        if inwin(r):
            d.polygon(sc([xy(*p) for p in r]), fill=(112, 100, 78, 255), outline=(78, 68, 52, 255))
    for r in indo:
        d.polygon(sc([xy(*p) for p in r]), fill=(222, 200, 150, 255), outline=(120, 100, 68, 255))
    dashed(d, [(0, CY), (W, CY)], (255, 255, 255, 60), 2, dash=16, gap=12)
    put(g, text_sprite([("lokasi jatuhan sampah antariksa · catatan LAPAN/BRIN", 28, WHITE, False)]), 540, 575, a=0.8)
    bg.alpha_composite(down(g))
    # (year, place, lon, lat, label centre, appears at): one marker a beat, after "seribu sembilan ratus delapan puluh satu"
    events = [("1981", "Gorontalo", 123.06, 0.54, (770, 772), 1.80),
              ("1988", "Lampung", 105.2, -4.9, (280, 1212), 2.35),
              ("2003", "Bengkulu Utara", 102.0, -3.35, (152, 1105), 2.90),
              ("2016", "Sumenep", 113.86, -7.01, (500, 1210), 3.45),
              ("2017", "Agam, Sumbar", 100.15, -0.25, (142, 805), 4.00),
              ("2022", "Sanggau, Kalbar", 110.6, 0.12, (330, 690), 4.50),
              ("2026", "dekat Sampit", 112.95, -2.54, (560, 845), 5.00)]  # chips kept clear of each other and the frame edge
    chips = [chip(y, p) for y, p, *_ in events]
    dot = marker()
    frames = []
    for i in range(n):
        t = i / FPS
        im = bg.copy()
        top = layer()
        d = ImageDraw.Draw(top)
        for (year, place, lon, lat, (lx, ly), t0), cp in zip(events, chips):
            if t < t0:
                continue
            mx, my = xy(lon, lat)
            a = ramp(t, t0 + 0.05, t0 + 0.2)
            d.line(sc([(mx, my), (lx, ly)]), fill=(255, 255, 255, round(170 * a)), width=2 * S)
            if year == "2026":
                ph = ((t - t0) % 0.9) / 0.9
                r = (20 + 46 * ph) * S
                d.ellipse([mx * S - r, my * S - r, mx * S + r, my * S + r], outline=YELLOW + (round(220 * (1 - ph) ** 1.5),), width=4 * S)
            put(top, dot, mx, my, scale=pop(t, t0) * (1.25 if year == "2026" else 0.85))
            put(top, cp, lx, ly, a=a, scale=pop(t, t0 + 0.05))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_riwayat.mp4")


def orbit(n=136):
    land = [r for r in polys("ne_50m_land.geojson") if min(y for _, y in r) > -60 and min(y for _, y in r) < 59.5]  # no Antarctica, no Greenland
    indo = polys("ne_50m_admin_0_countries.geojson", lambda p: p["ADMIN"] == "Indonesia")
    LC0, LC1, LAT1 = 150.0, 118.0, -2.5  # map centre longitude at the start and of the zoom; latitude the zoom ends on
    t_eq, t_in, t_z1 = 0.9, 2.42, 3.35  # "khatulistiwa" lands at 0.94, "termasuk" at 2.45

    def view(t):
        u = ramp(t, t_in, t_z1)
        return LC0 + (LC1 - LC0) * u, LAT1 * u, 3.0 * (1 + 3.0 * u)  # centre lon, lat, pixels per degree

    def proj(ring_, v, close=True):
        lc, la, k = v
        out, prev = [], None
        segs = []
        for lon, lat in ring_:
            x = (lon - lc + 180) % 360 - 180
            if prev is not None and abs(x - prev) > 180:
                segs.append(out)
                out = []
            out.append((540 + x * k, CY - (lat - la) * k))
            prev = x
        segs.append(out)
        return segs
    tracks = []
    for inc, node in ((28.5, 105.0), (51.6, 150.0), (42.0, -100.0)):
        pts = []
        for k in range(721):
            u = 2 * math.pi * k / 720
            lat = math.degrees(math.asin(math.sin(math.radians(inc)) * math.sin(u)))
            lon = node + math.degrees(math.atan2(math.cos(math.radians(inc)) * math.sin(u), math.cos(u))) - 23.0 * k / 720
            pts.append((lon, lat))
        tracks.append(pts)

    def base(v, hl):
        lc, la, k = v
        im = navy(540, CY)
        g = layer()
        d = ImageDraw.Draw(g)
        for lat in (-60, -30, 30, 60):
            y = CY - (lat - la) * k
            d.line(sc([(0, y), (W, y)]), fill=(255, 255, 255, 22), width=2 * S)
        for r in land:
            for seg in proj(r, v):
                if len(seg) > 2:
                    d.polygon(sc(seg), fill=(150, 134, 100, 255))
        if hl > 0:
            for r in indo:
                for seg in proj(r, v):
                    if len(seg) > 2:
                        d.polygon(sc(seg), fill=(255, 214, 40, round(255 * hl)))
        im.alpha_composite(down(g))
        return im
    eq_lab = text_sprite([("KHATULISTIWA 0°", 40, YELLOW, True)])
    note = text_sprite([("contoh lintasan orbit", 28, WHITE, False)])
    static0 = base(view(0), 0)
    cache = {}
    frames = []
    for i in range(n):
        t = i / FPS
        v = view(t)
        hl = ramp(t, t_in, t_in + 0.25)
        key = (round(v[0], 3), round(hl, 3))
        if t < t_in:
            im = static0.copy()
        else:
            if key not in cache:
                cache = {key: base(v, hl)}  # the zoom changes every frame; the end view repeats
            im = cache[key].copy()
        top = layer()
        d = ImageDraw.Draw(top)
        lc, la, k = v
        y_eq = CY + la * k
        dashed(d, [(0, y_eq), (W, y_eq)], YELLOW + (235,), 5, dash=26, gap=14, upto=ramp(t, t_eq, t_eq + 0.4) * W)
        put(top, eq_lab, 840, y_eq + 44, a=ramp(t, t_eq + 0.2, t_eq + 0.45) * (1 - ramp(t, t_in, t_in + 0.3)))
        for j, tr in enumerate(tracks):  # drawn on one after another while "pasti melintasi" is said
            upto = ramp(t, 0.05 + 0.2 * j, 0.75 + 0.2 * j)
            if upto <= 0:
                continue
            m = max(2, int(upto * len(tr)))
            for seg in proj(tr[:m], v):
                if len(seg) > 1:
                    d.line(sc(seg), fill=(160, 225, 255, 215), width=4 * S, joint="curve")
            for c in (0, 360):  # where the track crosses the equator
                if c < m:
                    x = (tr[c][0] - lc + 180) % 360 - 180
                    cx = 540 + x * k
                    r = 9 * pop(t, t_eq + 0.15 * j, 0.25)
                    d.ellipse([(cx - r) * S, (y_eq - r) * S, (cx + r) * S, (y_eq + r) * S], fill=WHITE + (255,), outline=(20, 40, 80, 255), width=2 * S)
        if t >= t_in + 0.2:
            ph = ((t - t_in - 0.2) % 1.0) / 1.0
            cx, cy = 540 + ((118 - lc + 180) % 360 - 180) * k, CY - (-2.5 - la) * k
            r = (24 * k * (0.9 + 0.5 * ph)) * S
            d.ellipse([cx * S - r, cy * S - r * 0.42, cx * S + r, cy * S + r * 0.42], outline=YELLOW + (round(200 * (1 - ph) ** 1.5),), width=5 * S)
        put(top, note, 540, 1262, a=0.8 * ramp(t, 0.3, 0.6))
        im.alpha_composite(down(top))
        frames.append(im)
    encode(frames, "clips/skema_orbit.mp4")


for name in sys.argv[2:] or ["riwayat", "orbit"]:
    globals()[name]()
