"""VO pauses for Titik Heran #84 (run in the episode work dir: vo84.mp3 and w84_scribe.json from Scribe).
The v4 take runs only 28,9 s, so nothing is cut. Two dramatic pauses came out short: 0,34 s after "kaisar?" (the
script asks for about 0,4 s before the reveal, and the reel needs the beat) and only 0,09 s after "Ternyata..." (the
quiet run at 21,76 s is the closure of the "t" inside the word, not the pause; the pause is the run at 22,31-22,40 s
before "cuma"). Each grows inside the quiet window given below, filled with that window's own room tone (mirrored back
and forth, so there are no clicks), and every word after it moves down by the same amount. Same method as prep78.py.
Writes vo84pad.wav and w84.json for render.py.
"""
import json, subprocess, wave
import numpy as np

SR = 44100
x = np.frombuffer(subprocess.check_output(
    ["ffmpeg", "-v", "error", "-i", "vo84.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]), np.float32)
n = len(x) // 441
lvl = 20 * np.log10(np.sqrt((x[:n * 441].reshape(n, 441) ** 2).mean(1)) + 1e-9)  # 10 ms frames
quiet = lvl < -40

words = json.load(open("w84_scribe.json"))["words"]
ADD = {"kaisar?": (0.2, 20.93, 21.20), "Ternyata...": (0.3, 22.31, 22.40)}  # seconds added, quiet window (s)


cuts = []  # (time, seconds added, room-tone start, room-tone end)
for w in words:
    if w["text"] in ADD:
        add, s, e = ADD[w["text"]]
        assert quiet[int(s * 100):int(e * 100)].all(), (w["text"], s, e)
        # grow the pause in the quietest 80 ms of the window, which also gives the room tone
        f0 = min(range(int(s * 100), int(e * 100) - 7), key=lambda f: lvl[f:f + 8].max())
        cuts.append((f0 / 100 + 0.04, add, f0 / 100, f0 / 100 + 0.08))
assert len(cuts) == len(ADD), cuts

xf = 220  # 5 ms crossfades
ramp = np.linspace(0, 1, xf, dtype=np.float32)
y, last = [], 0
for m, add, s, e in cuts:
    tone = x[int(s * SR):int(e * SR)]
    fill = np.concatenate([tone, tone[::-1]] * ((int(add * SR) + 2 * xf) // (2 * len(tone)) + 1))[:int(add * SR) + 2 * xf]
    a = x[last:int(m * SR)]
    y.append(a[:-xf])
    y.append(a[-xf:] * (1 - ramp) + fill[:xf] * ramp)
    y.append(fill[xf:-xf])
    b = x[int(m * SR):int(m * SR) + xf]
    y.append(fill[-xf:] * (1 - ramp) + b * ramp)
    last = int(m * SR) + xf
y.append(x[last:])
y = np.concatenate(y)
with wave.open("vo84pad.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())

out = []
for w in words:
    st = sum(add for m, add, *_ in cuts if w["start"] >= m)
    en = sum(add for m, add, *_ in cuts if w["end"] > m)
    out.append(dict(w, start=round(w["start"] + st, 3), end=round(w["end"] + en, 3)))
json.dump({"words": out}, open("w84.json", "w"), ensure_ascii=False)
print(" ".join(f"{m:.2f}s +{add:.2f}" for m, add, *_ in cuts) + f": {len(x) / SR:.2f}s -> {len(y) / SR:.2f}s")
