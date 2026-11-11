"""VO cuts for Titik Heran #52 (run in the episode work dir: vo52.mp3 and w52_scribe.json from Scribe).
The v4 take ran 33,6 s, so the script's optional words "tersembunyi" and "juga" come out
("Kota suku Maya ditemukan di hutan Meksiko", "Dan nama Sakil terukir di kota musuhnya").
Each joint sits on the quietest 10 ms frame between the neighbouring words, with a 20 ms crossfade.
Writes vo52cut.wav and w52.json for render.py.
"""
import json, subprocess, wave
import numpy as np

SR = 44100
x = np.frombuffer(subprocess.check_output(
    ["ffmpeg", "-v", "error", "-i", "vo52.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]), np.float32)
n = len(x) // 441
db = 20 * np.log10(np.sqrt((x[:n * 441].reshape(n, 441) ** 2).mean(1)) + 1e-9)
words = json.load(open("w52_scribe.json"))["words"]


def quietest(t0, t1):
    f0, f1 = int(t0 * 100), int(t1 * 100) + 1
    return (f0 + int(np.argmin(db[f0:f1]))) / 100


drop, spans = [], []
for word, before in (("tersembunyi", "ditemukan"), ("juga", "Sakil")):
    i = next(k for k, w in enumerate(words) if w["text"] == word and words[k - 1]["text"] == before)
    c0 = quietest(words[i - 1]["end"] - 0.04, words[i]["start"] + 0.04)
    c1 = quietest(words[i]["end"] - 0.04, words[i + 1]["start"] + 0.04)
    print(f"{word}: joint levels {db[int(c0*100)]:.1f} dB / {db[int(c1*100)]:.1f} dB")
    drop.append(i); spans.append((c0, c1))
xf = 882  # 20 ms crossfade: both joints sit in voiced air, not silence
ramp = np.linspace(0, 1, xf, dtype=np.float32)
y, pos = x[:0], 0
for c0, c1 in spans:
    a = x[pos:int(c0 * SR)]
    y = a if not len(y) else np.concatenate([y[:-xf], y[-xf:] * (1 - ramp) + a[:xf] * ramp, a[xf:]])
    pos = int(c1 * SR)
b = x[pos:]
y = np.concatenate([y[:-xf], y[-xf:] * (1 - ramp) + b[:xf] * ramp, b[xf:]])
with wave.open("vo52cut.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
out = []
for k, w in enumerate(words):
    if k in drop:
        continue
    past = [(c0, c1) for c0, c1 in spans if w["start"] >= c0]  # "di" starts a hair before its joint
    d = sum(c1 - c0 + xf / SR for c0, c1 in past)
    if d:
        w = dict(w, start=round(max(w["start"] - d, past[-1][0]), 3), end=round(w["end"] - d, 3))
    out.append(w)
json.dump({"words": out}, open("w52.json", "w"), ensure_ascii=False)
print(f"cuts {spans}: {len(x) / SR:.2f}s -> {len(y) / SR:.2f}s")
