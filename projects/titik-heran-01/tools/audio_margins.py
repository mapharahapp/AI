"""audio_margins.py — how far the voice sits above everything else, word by word.

    python3 tools/audio_margins.py <projectDir> [minMarginDb=12] [--speech-band]

Rebuilds two stems from the <audio> tags in the BUILT index.html (same start / duration / volume / fade-out the
renderer uses): the voice-over alone, and the bed (music + every SFX). Then, for every word in
assets/vo/audio_meta.json, compares the voice's RMS with the bed's RMS over the same window. Prints the words whose
margin is under the target, worst first. Run it after `node build.mjs .` and before rendering."""
import json, math, os, re, subprocess, sys, wave, array, tempfile

proj = sys.argv[1] if len(sys.argv) > 1 else "."
MIN = float(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else 12.0
BAND = "--speech-band" in sys.argv          # 500-5000 Hz only: where a bed actually masks intelligibility
html = open(os.path.join(proj, "index.html")).read()
total = float(re.search(r'data-composition-id="main"[^>]*data-duration="([\d.]+)"', html).group(1))
tags = []
for m in re.finditer(r"<audio\b([^>]*)>", html):
    a = m.group(1)
    g = lambda k, d=None: (re.search(rf'\b{k}="([^"]*)"', a) or [None, d])[1]
    tags.append(dict(id=g("id"), src=g("src"), start=float(g("data-start")), dur=float(g("data-duration")),
                     vol=float(g("data-volume", 1)), fade=float(g("data-fade-out", 0) or 0)))

SR = 16000
def stem(items, out):
    if not items:
        return None
    ins, flt = [], []
    for i, t in enumerate(items):
        ins += ["-i", os.path.join(proj, t["src"])]
        f = f"[{i}:a]aresample={SR},aformat=channel_layouts=mono,atrim=0:{t['dur']},asetpts=PTS-STARTPTS,volume={t['vol']}"
        if t["fade"]:
            f += f",afade=t=out:st={max(0, t['dur'] - t['fade'])}:d={t['fade']}"
        f += f",adelay={int(round(t['start'] * 1000))}:all=1,apad=whole_dur={total}[s{i}]"
        flt.append(f)
    band = ",highpass=f=500,lowpass=f=5000" if BAND else ""
    flt.append("".join(f"[s{i}]" for i in range(len(items))) + f"amix=inputs={len(items)}:normalize=0:duration=longest,atrim=0:{total}{band}[o]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(flt), "-map", "[o]", "-ac", "1", "-ar", str(SR), out], check=True)
    w = wave.open(out); x = array.array("h"); x.frombytes(w.readframes(w.getnframes())); return x

tmp = tempfile.mkdtemp()
vo = stem([t for t in tags if t["id"] == "vo"], os.path.join(tmp, "vo.wav"))
bed = stem([t for t in tags if t["id"] != "vo"], os.path.join(tmp, "bed.wav"))
vo_start = next(t["start"] for t in tags if t["id"] == "vo")

def rms_db(x, t0, t1):
    i0, i1 = int(t0 * SR), max(int(t0 * SR) + 1, int(t1 * SR))
    s = x[i0:i1]
    if not len(s):
        return -120.0
    return 20 * math.log10(max(1e-9, math.sqrt(sum(v * v for v in s) / len(s))) / 32768)

words = json.load(open(os.path.join(proj, "assets/vo/audio_meta.json")))["scenes"][0]["words"]
# speech frames only: the aligner's word ends run late into the following pause, which would understate the margin
F = 0.02
rows = []
for w in words:
    t0, t1 = vo_start + w["start"], vo_start + w["end"]
    fr = []
    t = t0
    while t + F <= t1:
        v = rms_db(vo, t, t + F)
        if v > -40:
            fr.append((v, rms_db(bed, t, t + F)))
        t += F
    if not fr:
        continue
    v = 10 * math.log10(sum(10 ** (a / 10) for a, _ in fr) / len(fr))
    b = 10 * math.log10(sum(10 ** (c / 10) for _, c in fr) / len(fr))
    rows.append((v - b, w["text"], t0, v, b))
low = sorted(r for r in rows if r[0] < MIN)
print(f"{len(rows)} words; median margin {sorted(r[0] for r in rows)[len(rows) // 2]:.1f} dB; under {MIN:.0f} dB: {len(low)}")
for m, txt, t0, v, b in low:
    print(f"  {t0:6.2f}s  {txt:<14} voice {v:6.1f}  bed {b:6.1f}  margin {m:5.1f} dB")
