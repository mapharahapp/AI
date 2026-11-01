"""VO cut for Titik Heran #29 (run in the episode work dir: vo29.mp3 and w29_scribe.json from Scribe).
The v4 take ran 33,9 s, too long for 30 s at a natural tempo, so "Kok bisa?" comes out as the script's own fallback says.
The cut keeps 0,2 s of the quiet before it and 0,2 s of the quiet after it; the words after it move up by the same amount.
Writes vo29cut.wav and w29.json for render.py.
"""
import json, subprocess, wave
import numpy as np

SR = 44100
x = np.frombuffer(subprocess.check_output(
    ["ffmpeg", "-v", "error", "-i", "vo29.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]), np.float32)
n = len(x) // 441
quiet = 20 * np.log10(np.sqrt((x[:n * 441].reshape(n, 441) ** 2).mean(1)) + 1e-9) < -40  # 10 ms frames

words = json.load(open("w29_scribe.json"))["words"]
idx = {w["text"]: i for i, w in enumerate(words)}
kok, bisa = idx["Kok"], idx["bisa?"]

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

s1, _ = quiet_run(words[kok - 2]["start"], words[kok]["start"] + 0.1)  # after "belum."
_, e2 = quiet_run(words[bisa]["start"], words[bisa + 2]["start"] + 0.1)  # before "Namanya" ([seriously] sits between)
c0, c1 = s1 + 0.2, e2 - 0.2
xf = 441
ramp = np.linspace(0, 1, xf, dtype=np.float32)
a, b = x[:int(c0 * SR)], x[int(c1 * SR):]
y = np.concatenate([a[:-xf], a[-xf:] * (1 - ramp) + b[:xf] * ramp, b[xf:]])
with wave.open("vo29cut.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())

d = c1 - c0 + xf / SR
out = []
for i, w in enumerate(words):
    if i in (kok - 1, kok, bisa):  # [curious] Kok bisa?
        continue
    if w["start"] >= c1:
        w = dict(w, start=round(w["start"] - d, 3), end=round(w["end"] - d, 3))
    out.append(w)
json.dump({"words": out}, open("w29.json", "w"), ensure_ascii=False)
print(f"cut {c0:.2f}-{c1:.2f} s: {len(x) / SR:.2f}s -> {len(y) / SR:.2f}s")
