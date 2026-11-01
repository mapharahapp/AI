"""VO cut for Titik Heran #34 (run in the episode work dir: vo34.mp3 and w34_scribe.json from Scribe).
The v4 take ran 33,5 s, too long for 30 s at a natural tempo, so "Tengah malam," comes out as the script's own fallback says
(the night is already set by "tiap malam... dengan kamera inframerah" and by the night-camera clock on screen).
The cut keeps 0,2 s of the quiet before it and 0,2 s of the quiet after it; the words after it move up by the same amount.
The whisper carries on into "kakinya berkedut...", so the [whispers] tag goes with the cut words.
Writes vo34cut.wav and w34.json for render.py.
"""
import json, subprocess, wave
import numpy as np

SR = 44100
x = np.frombuffer(subprocess.check_output(
    ["ffmpeg", "-v", "error", "-i", "vo34.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]), np.float32)
n = len(x) // 441
quiet = 20 * np.log10(np.sqrt((x[:n * 441].reshape(n, 441) ** 2).mean(1)) + 1e-9) < -40  # 10 ms frames

words = json.load(open("w34_scribe.json"))["words"]
tengah = next(i for i, w in enumerate(words) if w["text"] == "Tengah")
kaki = next(i for i, w in enumerate(words) if w["text"] == "kakinya")
assert words[tengah - 1]["text"] == "[whispers]" and kaki == tengah + 2, [w["text"] for w in words[tengah - 2:kaki + 1]]


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


s1, _ = quiet_run(words[tengah - 2]["start"], words[tengah]["start"] + 0.1)  # after "inframerah."
_, e2 = quiet_run(words[tengah + 1]["start"], words[kaki]["start"] + 0.1)  # before "kakinya"
c0, c1 = s1 + 0.2, e2 - 0.2
xf = 441
ramp = np.linspace(0, 1, xf, dtype=np.float32)
a, b = x[:int(c0 * SR)], x[int(c1 * SR):]
y = np.concatenate([a[:-xf], a[-xf:] * (1 - ramp) + b[:xf] * ramp, b[xf:]])
with wave.open("vo34cut.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())

d = c1 - c0 + xf / SR
out = []
for i, w in enumerate(words):
    if i in (tengah - 1, tengah, tengah + 1):  # [whispers] Tengah malam,
        continue
    if w["start"] >= c1:
        w = dict(w, start=round(w["start"] - d, 3), end=round(w["end"] - d, 3))
    out.append(w)
json.dump({"words": out}, open("w34.json", "w"), ensure_ascii=False)
print(f"cut {c0:.2f}-{c1:.2f} s: {len(x) / SR:.2f}s -> {len(y) / SR:.2f}s")
