"""VO cut for Titik Heran #47 (run in the episode work dir: vo47.mp3 and w47_scribe.json from Scribe).
The v4 take ran 35,9 s, so the script's optional phrase "dan teman-temannya" comes out
("Hujan badai mengurung Lord Byron di sebuah vila di Swiss"; the screen still names the group).
Each joint sits on the quietest 10 ms frame between the neighbouring words, with a 10 ms crossfade.
Writes vo47cut.wav and w47.json for render.py.
"""
import json, subprocess, wave
import numpy as np

SR = 44100
x = np.frombuffer(subprocess.check_output(
    ["ffmpeg", "-v", "error", "-i", "vo47.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]), np.float32)
n = len(x) // 441
db = 20 * np.log10(np.sqrt((x[:n * 441].reshape(n, 441) ** 2).mean(1)) + 1e-9)
words = json.load(open("w47_scribe.json"))["words"]
i = next(k for k, w in enumerate(words) if w["text"] == "dan" and words[k - 1]["text"] == "Bairon")
assert words[i + 1]["text"] == "teman-temannya" and words[i + 2]["text"] == "di"


def quietest(t0, t1):
    f0, f1 = int(t0 * 100), int(t1 * 100) + 1
    return (f0 + int(np.argmin(db[f0:f1]))) / 100


c0 = quietest(words[i - 1]["end"] - 0.04, words[i]["start"] + 0.04)
c1 = quietest(words[i + 1]["end"] - 0.04, words[i + 2]["start"] + 0.04)
print(f"joint levels {db[int(c0*100)]:.1f} dB / {db[int(c1*100)]:.1f} dB")
xf = 441
ramp = np.linspace(0, 1, xf, dtype=np.float32)
a, b = x[:int(c0 * SR)], x[int(c1 * SR):]
y = np.concatenate([a[:-xf], a[-xf:] * (1 - ramp) + b[:xf] * ramp, b[xf:]])
with wave.open("vo47cut.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
d = c1 - c0 + xf / SR
out = []
for k, w in enumerate(words):
    if k in (i, i + 1):
        continue
    if w["start"] >= c1:
        w = dict(w, start=round(w["start"] - d, 3), end=round(w["end"] - d, 3))
    out.append(w)
json.dump({"words": out}, open("w47.json", "w"), ensure_ascii=False)
print(f"cut {c0:.2f}-{c1:.2f} s: {len(x) / SR:.2f}s -> {len(y) / SR:.2f}s")
