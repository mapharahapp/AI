"""VO pauses for Titik Heran #38 (run in the episode work dir: vo38.mp3 and w38_scribe.json from Scribe).
The v4 take runs only 28,1 s and its pauses are short: 0,32 s after "buaya...", 0,16 s after "itu..." and 0,38 s after
"obat.". The script asks for about half a second after "buaya..." and "itu...", and the punchline ("...makan mumi sebagai
obat.") needs a beat before the question. So each of these pauses grows inside its own quiet run, filled with that run's
own room tone (mirrored back and forth, so there are no clicks), and every word after it moves down by the same amount.
The video then plays at natural speed and holds the CTA card for the rest of the 30 s.
Writes vo38pad.wav and w38.json for render.py.
"""
import json, subprocess, wave
import numpy as np

SR = 44100
x = np.frombuffer(subprocess.check_output(
    ["ffmpeg", "-v", "error", "-i", "vo38.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]), np.float32)
n = len(x) // 441
lvl = 20 * np.log10(np.sqrt((x[:n * 441].reshape(n, 441) ** 2).mean(1)) + 1e-9)  # 10 ms frames
quiet = lvl < -40

words = json.load(open("w38_scribe.json"))["words"]
ADD = {"buaya...": 0.15, "itu...": 0.35, "obat.": 0.22}  # seconds added to the pause after each of these words


def quiet_run(t0, t1):
    """the longest quiet run between t0 and t1 (seconds)"""
    best, s = (0, 0), None
    for f in range(int(t0 * 100), int(t1 * 100)):
        if quiet[f] and s is None:
            s = f
        if (not quiet[f] or f == int(t1 * 100) - 1) and s is not None:
            best = max(best, (s, f), key=lambda r: r[1] - r[0])
            s = None
    return best[0] / 100, best[1] / 100


cuts = []  # (time, seconds added)
for i, w in enumerate(words):
    if w["text"] in ADD:
        nxt = next(v for v in words[i + 1:] if not v["text"].startswith("["))
        s, e = quiet_run(w["start"], nxt["start"] + 0.1)
        assert e - s >= 0.12, (w["text"], s, e)
        # the run can start inside the word's soft decay: take the quietest 80 ms of it as the room tone, and grow the
        # pause in the middle of that stretch
        f0 = min(range(int(s * 100), int(e * 100) - 7), key=lambda f: lvl[f:f + 8].max())
        cuts.append((f0 / 100 + 0.04, ADD[w["text"]], f0 / 100, f0 / 100 + 0.08))
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
with wave.open("vo38pad.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())

out = []
for w in words:
    st = sum(add for m, add, *_ in cuts if w["start"] >= m)
    en = sum(add for m, add, *_ in cuts if w["end"] > m)
    out.append(dict(w, start=round(w["start"] + st, 3), end=round(w["end"] + en, 3)))
json.dump({"words": out}, open("w38.json", "w"), ensure_ascii=False)
print(" ".join(f"{m:.2f}s +{add:.2f}" for m, add, *_ in cuts) + f": {len(x) / SR:.2f}s -> {len(y) / SR:.2f}s")
