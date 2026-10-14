"""pixabay.py — source b-roll from Pixabay for build.mjs slots. Key: PIXABAY_API_KEY (env, never printed).

    python3 -I tools/pixabay.py search  videos|images "<query>" raw/pixabay/<slot>/<tag>   [--n 16] [--orientation vertical]
    python3 -I tools/pixabay.py fetch   videos|images <id> raw/pixabay/<slot>             (best rendition; writes <id>.json)
    python3 -I tools/pixabay.py sheet   <clip.mp4> <out.jpg>                               (1 frame/s, labelled — pick the segment)
    python3 -I tools/pixabay.py prep    <clip.mp4|image> assets/footage/<slot>.mp4 [--focus 0.5] [--still-dur 9]
    python3 -I tools/pixabay.py record  <slot> assets/footage/<slot>.mp4 raw/pixabay/<slot>/<id>.json --at <sec> [--note "..."]

`search` downloads every hit's thumbnail and tiles them into <dir>/sheet.jpg labelled with the Pixabay id, so
candidates are chosen by LOOKING, not by tags. Downloads land in raw/ (untrusted data, gitignored); this script
lives in tools/. `prep` crops to 9:16 around a horizontal focus point (0 = left edge, 1 = right edge), scales to
1080x1920 @ 30 fps, strips audio. `record` writes the slot into assets/footage/manifest.json and the licence line
into publish/sources.txt (the lint refuses footage without one)."""
import json, os, subprocess, sys, urllib.parse, shutil

API = {"videos": "https://pixabay.com/api/videos/", "images": "https://pixabay.com/api/"}
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def key():
    k = os.environ.get("PIXABAY_API_KEY")
    if not k: sys.exit("PIXABAY_API_KEY is not set")
    return k


def get_json(url):
    r = subprocess.run(["curl", "-sS", "--fail", "--max-time", "40", url], capture_output=True, text=True)
    if r.returncode: sys.exit("pixabay request failed: " + r.stderr.replace(key(), "<key>")[:300])
    return json.loads(r.stdout)


def download(url, out):
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    r = subprocess.run(["curl", "-sS", "--fail", "-L", "--max-time", "300", "-o", out, url], capture_output=True, text=True)
    if r.returncode: raise RuntimeError(f"download failed {url[:80]}: {r.stderr[:200]}")
    return out


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(" ".join(cmd[:4]) + " … " + r.stderr[-600:])
    return r.stdout


def probe(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration", "-of", "json", path])
    j = json.loads(out); s = j["streams"][0]
    return s["width"], s["height"], float(j.get("format", {}).get("duration") or 0)


def search(kind, q, outdir, n=16, orientation=None):
    params = {"key": key(), "q": q, "per_page": max(3, min(n, 200)), "safesearch": "true"}
    if kind == "images": params.update(image_type="photo")
    if orientation and kind == "images": params["orientation"] = orientation
    data = get_json(API[kind] + "?" + urllib.parse.urlencode(params))
    os.makedirs(outdir, exist_ok=True)
    hits, thumbs = [], []
    for h in data.get("hits", [])[:n]:
        if kind == "videos":
            v = h["videos"]; best = max(v.values(), key=lambda r: (r.get("width") or 0))
            info = {"id": h["id"], "tags": h["tags"], "duration": h["duration"], "w": best["width"], "h": best["height"],
                    "user": h["user"], "page": h["pageURL"], "thumb": (v.get("medium") or best).get("thumbnail")}
        else:
            info = {"id": h["id"], "tags": h["tags"], "w": h["imageWidth"], "h": h["imageHeight"],
                    "user": h["user"], "page": h["pageURL"], "thumb": h["webformatURL"]}
        hits.append(info)
        if info["thumb"]:
            t = os.path.join(outdir, f"t_{info['id']}.jpg")
            try:
                download(info["thumb"], t); thumbs.append((info, t))
            except RuntimeError as e:
                print("  thumb skipped:", e)
    json.dump({"kind": kind, "q": q, "total": data.get("totalHits"), "hits": hits}, open(os.path.join(outdir, "results.json"), "w"), indent=1)
    # labelled tiles -> one sheet
    tiles = []
    for info, t in thumbs:
        lab = f"{info['id']}  {info['w']}x{info['h']}" + (f"  {info['duration']}s" if kind == "videos" else "")
        o = t.replace("t_", "l_")
        try:
            run(["ffmpeg", "-v", "error", "-y", "-i", t, "-vf",
                 f"scale=480:270:force_original_aspect_ratio=decrease,pad=480:300:(ow-iw)/2:0:black,"
                 f"drawtext=fontfile={FONT}:text='{lab}':x=8:y=278:fontsize=18:fontcolor=white", o])
            tiles.append(o)
        except RuntimeError as e:
            print("  label skipped:", e)
    if tiles:
        cols = 4; rows = (len(tiles) + cols - 1) // cols
        ins = sum([["-i", t] for t in tiles], [])
        pads = len(tiles)
        flt = "".join(f"[{i}:v]" for i in range(pads)) + f"xstack=inputs={pads}:layout=" + "|".join(
            f"{(i % cols) * 480}_{(i // cols) * 300}" for i in range(pads)) + ":fill=black[v]"
        if pads == 1: flt = "[0:v]null[v]"
        run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", flt, "-map", "[v]", "-frames:v", "1", os.path.join(outdir, "sheet.jpg")])
    print(f"{kind} '{q}': {data.get('totalHits')} total, {len(hits)} listed -> {outdir}/sheet.jpg")
    for h in hits:
        print(f"  {h['id']:>9}  {h['w']}x{h['h']}" + (f"  {h['duration']:>3}s" if kind == "videos" else "") + f"  {h['tags'][:70]}")


def fetch(kind, pid, outdir):
    params = {"key": key(), "id": pid}
    if kind == "images": params["image_type"] = "photo"
    data = get_json(API[kind] + "?" + urllib.parse.urlencode(params))
    if not data.get("hits"): sys.exit(f"no {kind} hit for id {pid}")
    h = data["hits"][0]; os.makedirs(outdir, exist_ok=True)
    if kind == "videos":
        v = h["videos"]
        # prefer >=2160 tall-enough masters (crop to 9:16 keeps detail); else the largest available
        r = max((r for r in v.values() if r.get("url")), key=lambda r: (r.get("width") or 0) * (r.get("height") or 0))
        out = download(r["url"], os.path.join(outdir, f"{pid}.mp4"))
        meta = {"kind": "video", "id": pid, "page": h["pageURL"], "user": h["user"], "tags": h["tags"], "w": r["width"], "h": r["height"], "file": out}
    else:
        url = h.get("largeImageURL") or h["webformatURL"]
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".jpg"
        out = download(url, os.path.join(outdir, f"{pid}{ext}"))
        meta = {"kind": "image", "id": pid, "page": h["pageURL"], "user": h["user"], "tags": h["tags"], "w": h["imageWidth"], "h": h["imageHeight"], "file": out}
    json.dump(meta, open(os.path.join(outdir, f"{pid}.json"), "w"), indent=1)
    if meta["kind"] == "video":
        w, hh, d = probe(out); meta.update(w=w, h=hh, duration=round(d, 2))
        json.dump(meta, open(os.path.join(outdir, f"{pid}.json"), "w"), indent=1)
    print(json.dumps(meta))


def sheet(clip, out):
    w, h, d = probe(clip)
    n = max(1, int(d))
    run(["ffmpeg", "-v", "error", "-y", "-i", clip, "-vf",
         f"fps=1,scale=360:-2,drawtext=fontfile={FONT}:text='%{{pts\\:hms}}':x=8:y=8:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.6,"
         f"tile=6x{(n + 5) // 6}", "-frames:v", "1", out])
    print(f"{clip}: {w}x{h} {d:.2f}s -> {out}")


def prep(src, out, focus=0.5, still_dur=9.0):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    is_img = os.path.splitext(src)[1].lower() in (".jpg", ".jpeg", ".png", ".webp")
    w, h, d = probe(src) if not is_img else (*probe(src)[:2], still_dur)
    # crop the widest 9:16 window that fits, centred on `focus`, then scale to 1080x1920
    cw = min(w, int(h * 9 / 16) // 2 * 2); ch = min(h, int(w * 16 / 9) // 2 * 2)
    cx = int(max(0, min(w - cw, focus * w - cw / 2)))
    vf = f"crop={cw}:{ch}:{cx}:{(h - ch) // 2},scale=1080:1920:flags=lanczos,fps=30"
    if cw < 1080: vf += ",unsharp=5:5:0.4:5:5:0.0"
    if is_img:
        cmd = ["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(still_dur), "-i", src, "-vf", vf + ",format=yuv420p"]
    else:
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf]
    run(cmd + ["-an", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out])
    W, H, D = probe(out)
    print(f"prep {src} ({w}x{h}, crop {cw}x{ch}@x{cx}) -> {out} {W}x{H} {D:.2f}s" + ("  [upscaled]" if cw < 1080 else ""))


def record(slot, file, meta_json, at, note=""):
    m = json.load(open(meta_json)); W, H, D = probe(file)
    man_p = "assets/footage/manifest.json"
    man = json.load(open(man_p)) if os.path.exists(man_p) else {}
    man[slot] = {"file": file, "w": W, "h": H, "dur": round(D, 3), "at": round(float(at), 3),
                 "pixabay": {"kind": m["kind"], "id": m["id"], "page": m["page"], "user": m["user"]}, "note": note}
    json.dump(man, open(man_p, "w"), indent=1)
    os.makedirs("publish", exist_ok=True)
    line = f"{os.path.basename(file)}  slot={slot}  Pixabay {m['kind']} #{m['id']} by {m['user']}  {m['page']}  (Pixabay Content License; stock footage, not a record of the events narrated)"
    sp = "publish/sources.txt"; old = open(sp).read().splitlines() if os.path.exists(sp) else []
    old = [l for l in old if not l.startswith(os.path.basename(file) + " ")]
    open(sp, "w").write("\n".join(old + [line]) + "\n")
    print("recorded", slot, man[slot])


if __name__ == "__main__":
    a = sys.argv[1:]
    opt = lambda k, d=None: (a[a.index(k) + 1] if k in a else d)
    if not a: sys.exit(__doc__)
    if a[0] == "search": search(a[1], a[2], a[3], int(opt("--n", 16)), opt("--orientation"))
    elif a[0] == "fetch": fetch(a[1], a[2], a[3])
    elif a[0] == "sheet": sheet(a[1], a[2])
    elif a[0] == "prep": prep(a[1], a[2], float(opt("--focus", 0.5)), float(opt("--still-dur", 9)))
    elif a[0] == "record": record(a[1], a[2], a[3], opt("--at", 0), opt("--note", ""))
    else: sys.exit(__doc__)
