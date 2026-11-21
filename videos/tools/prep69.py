"""VO cuts for Titik Heran #69 (run in the episode work dir: vo69_raw.mp3 and w69_scribe.json from Scribe).
The v4 take ran 34,7 s, so the two words the naskah marks as optional come out: "sampai" (sentence 2: "Lokasinya
dipasangi garis polisi.") and "Dan" (sentence 5: "Ukirannya... ternyata mirip wajah manusia!"). The joints were picked by
hand on the 10 ms level and spectral-centroid trace: "Lokasinya" runs straight into "sampai", whose "s" hisses from
7,14 s (centroid 7-8 kHz), so the cut goes from the end of "-nya" (7,135 s) to the "d" closure of "dipasangi" (7,85 s); "Dan" sits between the sentence pause (silent to 24,19 s) and the soft "u" of
"ukirannya" (dip at 24,40 s, after the "n" of "Dan" at 24,35-24,38 s). 20 ms crossfades. Writes vo69.wav and w69.json for render.py (AUDIO = "vo69.wav").
"""
import json, subprocess, wave
import numpy as np

SR = 44100
x = np.frombuffer(subprocess.check_output(
    ["ffmpeg", "-v", "error", "-i", "vo69_raw.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]), np.float32)
words = json.load(open("w69_scribe.json"))["words"]
SPANS = [(7.135, 7.85), (24.19, 24.40)]
DROP = [("sampai", "Lokasinya"), ("Dan", "[dramatic]")]
drop = [next(k for k, w in enumerate(words) if w["text"] == a and words[k - 1]["text"] == b) for a, b in DROP]
xf = 882
ramp = np.linspace(0, 1, xf, dtype=np.float32)
y, pos = x[:0], 0
for c0, c1 in SPANS:
    a = x[pos:int(c0 * SR)]
    y = a if not len(y) else np.concatenate([y[:-xf], y[-xf:] * (1 - ramp) + a[:xf] * ramp, a[xf:]])
    pos = int(c1 * SR)
b = x[pos:]
y = np.concatenate([y[:-xf], y[-xf:] * (1 - ramp) + b[:xf] * ramp, b[xf:]])
with wave.open("vo69.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
out = []
for k, w in enumerate(words):
    if k in drop:
        continue
    w = dict(w)
    if w["text"] == "[dramatic]" and words[k + 1]["text"] == "Dan":   # the tag before a cut word goes with it
        continue
    for c0, c1 in SPANS:   # Scribe lets "Lokasinya" run into the cut "s": end it at the joint
        if w["start"] < c0 < w["end"] <= c1:
            w["end"] = c0
    past = [(c0, c1) for c0, c1 in SPANS if w["end"] > c1]
    d = sum(c1 - c0 + xf / SR for c0, c1 in past)
    if d:
        joint = past[-1][0] - sum(c1 - c0 + xf / SR for c0, c1 in past[:-1])
        w = dict(w, start=round(max(w["start"] - d, joint), 3), end=round(w["end"] - d, 3))
    out.append(w)
for w in out:   # the sentence after a cut word now starts with a capital
    if w["text"] == "ukirannya...":
        w["text"] = "Ukirannya..."
json.dump({"words": out}, open("w69.json", "w"), ensure_ascii=False)
print(f"cuts {SPANS}: {len(x) / SR:.2f}s -> {len(y) / SR:.2f}s")
for w in out:
    if w["text"] in ("Lokasinya", "dipasangi", "kandungan.", "Ukirannya...", "ternyata"):
        print(w)
