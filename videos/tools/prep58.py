"""VO cuts for Titik Heran #58 (run in the episode work dir: vo58.mp3 and w58_scribe.json from Scribe).
The v4 take ran 36,7 s, so the optional words the naskah marks come out where a quiet joint exists: "ini berjajar"
("Ratusan kolam biru di Meksiko membentuk setengah lingkaran"), the sentence-opening "Dan" ("Kolam-kolam bernama cenote
itu...") and "itu," in the CTA ("Asteroid, bencana atau berkah?"). "sedang" and "tua" stay: they run into the next word
with no dip under -21 dB, so a cut would clip "mencari" / "membuktikannya". A joint sits on the quietest 10 ms frame between the
neighbouring words, with a 20 ms crossfade. Writes vo58cut.wav and w58.json for render.py.
"""
import json, subprocess, wave
import numpy as np

SR = 44100
x = np.frombuffer(subprocess.check_output(
    ["ffmpeg", "-v", "error", "-i", "vo58.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]), np.float32)
n = len(x) // 441
db = 20 * np.log10(np.sqrt((x[:n * 441].reshape(n, 441) ** 2).mean(1)) + 1e-9)
words = json.load(open("w58_scribe.json"))["words"]


def quietest(t0, t1):
    f0, f1 = int(t0 * 100), int(t1 * 100) + 1
    return (f0 + int(np.argmin(db[f0:f1]))) / 100


CUTS = (("ini", "berjajar", "Meksiko"), ("Dan", "Dan", "[softly]"), ("itu,", "itu,", "Asteroid"))
drop, spans = [], []
for first, last, before in CUTS:
    i = next(k for k, w in enumerate(words) if w["text"] == first and words[k - 1]["text"] == before)
    j = i + (first != last)
    p = i - 1 if not words[i - 1]["text"].startswith("[") else i - 2   # a v4 tag is not a word to cut against
    c0 = quietest(words[p]["end"] - 0.04, words[i]["start"] + 0.04)
    c1 = quietest(words[j]["end"] - 0.04, words[j + 1 + (words[j + 1]["text"].startswith("[") and 0)]["start"] + 0.04)
    print(f"{first}..{last}: cut {c0:.2f}-{c1:.2f}, joint levels {db[int(c0*100)]:.1f} dB / {db[int(c1*100)]:.1f} dB")
    drop += list(range(i, j + 1)); spans.append((c0, c1))
xf = 882
ramp = np.linspace(0, 1, xf, dtype=np.float32)
y, pos = x[:0], 0
for c0, c1 in spans:
    a = x[pos:int(c0 * SR)]
    y = a if not len(y) else np.concatenate([y[:-xf], y[-xf:] * (1 - ramp) + a[:xf] * ramp, a[xf:]])
    pos = int(c1 * SR)
b = x[pos:]
y = np.concatenate([y[:-xf], y[-xf:] * (1 - ramp) + b[:xf] * ramp, b[xf:]])
with wave.open("vo58cut.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
out = []
for k, w in enumerate(words):
    if k in drop:
        continue
    past = [(c0, c1) for c0, c1 in spans if w["end"] > c1]
    d = sum(c1 - c0 + xf / SR for c0, c1 in past)
    if d:
        joint = past[-1][0] - sum(c1 - c0 + xf / SR for c0, c1 in past[:-1])
        w = dict(w, start=round(max(w["start"] - d, joint), 3), end=round(w["end"] - d, 3))
    out.append(w)
json.dump({"words": out}, open("w58.json", "w"), ensure_ascii=False)
print(f"cuts {spans}: {len(x) / SR:.2f}s -> {len(y) / SR:.2f}s")
