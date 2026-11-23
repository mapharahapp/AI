"""VO cut for Titik Heran #77 (run in the episode work dir: vo77_raw.mp3 and w77_scribe.json from Scribe).
The v4 take ran 33,5 s, so the phrase the naskah marks as optional in sentence 4 comes out: "Peneliti menemukan:"
("Buat apa hidung sebesar itu? Makin besar hidungnya..."). The other optional phrase ("zaman penjajahan") stays: it
ends the hook sentence and carries its falling "!" intonation. The joint was picked on the 10 ms level trace: "itu?"
fades out by 16,12 s and the room is silent to 16,50 s (that pause stays whole); "Peneliti" starts at 16,53 s,
"menemukan:" ends at 17,58 s, a quiet breath runs to 17,94 s and "makin" starts at 17,96 s. One cut (16,49-17,93),
20 ms crossfade. Writes vo77.wav and w77.json for render.py (AUDIO = "vo77.wav").
"""
import json, subprocess, wave
import numpy as np

SR = 44100
x = np.frombuffer(subprocess.check_output(
    ["ffmpeg", "-v", "error", "-i", "vo77_raw.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]), np.float32)
words = json.load(open("w77_scribe.json"))["words"]
SPANS = [(16.49, 17.93)]
k0 = next(k for k, w in enumerate(words) if w["text"] == "Peneliti")
drop = {k0 - 1, k0, k0 + 1}            # "[curious]", "Peneliti", "menemukan:"
assert [words[k]["text"] for k in sorted(drop)] == ["[curious]", "Peneliti", "menemukan:"]
xf = 882
ramp = np.linspace(0, 1, xf, dtype=np.float32)
y, pos = x[:0], 0
for c0, c1 in SPANS:
    a = x[pos:int(c0 * SR)]
    y = a if not len(y) else np.concatenate([y[:-xf], y[-xf:] * (1 - ramp) + a[:xf] * ramp, a[xf:]])
    pos = int(c1 * SR)
b = x[pos:]
y = np.concatenate([y[:-xf], y[-xf:] * (1 - ramp) + b[:xf] * ramp, b[xf:]])
with wave.open("vo77.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
out = []
for k, w in enumerate(words):
    if k in drop:
        continue
    w = dict(w)
    past = [(c0, c1) for c0, c1 in SPANS if w["end"] > c1]
    d = sum(c1 - c0 + xf / SR for c0, c1 in past)
    if d:
        joint = past[-1][0] - sum(c1 - c0 + xf / SR for c0, c1 in past[:-1])
        w = dict(w, start=round(max(w["start"] - d, joint), 3), end=round(w["end"] - d, 3))
    out.append(w)
k1 = next(k for k, w in enumerate(out) if w["text"] == "makin")   # the sentence now starts with "Makin"
out[k1]["text"] = "Makin"
json.dump({"words": out}, open("w77.json", "w"), ensure_ascii=False)
print(f"cuts {SPANS}: {len(x) / SR:.2f}s -> {len(y) / SR:.2f}s")
for w in out[k1 - 2:k1 + 3]:
    print(w)
