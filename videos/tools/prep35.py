"""VO cut for Titik Heran #35 (run in the episode work dir: vo35.mp3 and w35_scribe.json from Scribe).
The v4 take ran 33,6 s (32,4 s with the plain pauses tightened, a 1,10x speed-up), so "Lalu," comes out as the script's own
fallback says: "Ke mana kakinya?" asks the same question on its own.
The cut keeps 0,4 s of the quiet after "surga." (a sentence break, as before "Lalu,") and the second half of the short quiet before "ke" (the voice runs on from
"Lalu," into it); the words after it move up by the same amount. The [curious] tag goes with the cut word, and "ke" now opens
the sentence, so it is written "Ke".
Writes vo35cut.wav and w35.json for render.py.
"""
import json, subprocess, wave
import numpy as np

SR = 44100
x = np.frombuffer(subprocess.check_output(
    ["ffmpeg", "-v", "error", "-i", "vo35.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]), np.float32)
n = len(x) // 441
quiet = 20 * np.log10(np.sqrt((x[:n * 441].reshape(n, 441) ** 2).mean(1)) + 1e-9) < -40  # 10 ms frames

words = json.load(open("w35_scribe.json"))["words"]
lalu = next(i for i, w in enumerate(words) if w["text"] == "Lalu,")
assert words[lalu - 1]["text"] == "[curious]" and words[lalu + 1]["text"] == "ke", [w["text"] for w in words[lalu - 2:lalu + 2]]


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


s1, e1 = quiet_run(words[lalu - 2]["start"], words[lalu]["start"] + 0.1)  # after "surga."
s2, e2 = quiet_run(words[lalu]["start"], words[lalu + 1]["start"] + 0.1)  # before "ke"
c0, c1 = min(s1 + 0.4, e1 - 0.05), e2 - min(0.2, (e2 - s2) / 2)
xf = 441
ramp = np.linspace(0, 1, xf, dtype=np.float32)
a, b = x[:int(c0 * SR)], x[int(c1 * SR):]
y = np.concatenate([a[:-xf], a[-xf:] * (1 - ramp) + b[:xf] * ramp, b[xf:]])
with wave.open("vo35cut.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())

d = c1 - c0 + xf / SR
out = []
for i, w in enumerate(words):
    if i in (lalu - 1, lalu):  # [curious] Lalu,
        continue
    if i == lalu + 1:
        w = dict(w, text="Ke")
    if w["start"] >= c1:
        w = dict(w, start=round(w["start"] - d, 3), end=round(w["end"] - d, 3))
    out.append(w)
json.dump({"words": out}, open("w35.json", "w"), ensure_ascii=False)
print(f"cut {c0:.2f}-{c1:.2f} s: {len(x) / SR:.2f}s -> {len(y) / SR:.2f}s")
