"""VO cuts for Titik Heran #76 (run in the episode work dir: vo76_raw.mp3 and w76_scribe.json from Scribe).
The v4 take ran 33,9 s (hook alone 9,7 s), so two optional bits come out:
- "orang kaya zaman Romawi." (sentence 2; the naskah allowed "zaman Romawi", the rest had to go too to stay near
  atempo 1,07; the card on screen still says "orang kaya Romawi, abad ke-4"). "Amandinus," hisses to 12,50 s and
  fades by 12,54 s; "orang" starts at 12,72 s; "Romawi." fades by 14,12 s and the room is silent to 14,46 s, where
  "Kerangkanya" starts. Cut 12,60-14,14: the sentence pause after "Amandinus" stays ~0,38 s.
- "lagi" (sentence 3: "...dibuka tahun 2016"): "dibuka" ends at 17,78 s (dip 17,80 s), "lagi" runs 17,82-18,34 s,
  quiet to 18,44 s, "tahun" from 18,46 s. Cut 17,80-18,38.
Joints picked on the 20 ms level and spectral-centroid trace; 20 ms crossfades. Writes vo76.wav and w76.json for
render.py (AUDIO = "vo76.wav").
"""
import json, subprocess, wave
import numpy as np

SR = 44100
x = np.frombuffer(subprocess.check_output(
    ["ffmpeg", "-v", "error", "-i", "vo76_raw.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]), np.float32)
words = json.load(open("w76_scribe.json"))["words"]
SPANS = [(12.60, 14.14), (17.80, 18.38)]
ka = next(k for k, w in enumerate(words) if w["text"] == "Amandinus,")
kl = next(k for k, w in enumerate(words) if w["text"] == "lagi")
drop = {ka + 1, ka + 2, ka + 3, ka + 4, kl}
assert [words[k]["text"] for k in sorted(drop)] == ["orang", "kaya", "zaman", "Romawi.", "lagi"]
xf = 882
ramp = np.linspace(0, 1, xf, dtype=np.float32)
y, pos = x[:0], 0
for c0, c1 in SPANS:
    a = x[pos:int(c0 * SR)]
    y = a if not len(y) else np.concatenate([y[:-xf], y[-xf:] * (1 - ramp) + a[:xf] * ramp, a[xf:]])
    pos = int(c1 * SR)
b = x[pos:]
y = np.concatenate([y[:-xf], y[-xf:] * (1 - ramp) + b[:xf] * ramp, b[xf:]])
with wave.open("vo76.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
out = []
for k, w in enumerate(words):
    if k in drop:
        continue
    w = dict(w)
    for c0, c1 in SPANS:   # a word whose end Scribe ran into a cut ends at the joint
        if w["start"] < c0 < w["end"] <= c1:
            w["end"] = c0
    past = [(c0, c1) for c0, c1 in SPANS if w["end"] > c1]
    d = sum(c1 - c0 + xf / SR for c0, c1 in past)
    if d:
        joint = past[-1][0] - sum(c1 - c0 + xf / SR for c0, c1 in past[:-1])
        w = dict(w, start=round(max(w["start"] - d, joint), 3), end=round(w["end"] - d, 3))
    if w["text"] == "Amandinus,":   # the sentence now ends here
        w["text"] = "Amandinus."
    out.append(w)
json.dump({"words": out}, open("w76.json", "w"), ensure_ascii=False)
print(f"cuts {SPANS}: {len(x) / SR:.2f}s -> {len(y) / SR:.2f}s")
for w in out:
    if w["text"] in ("Amandinus.", "Kerangkanya", "dibuka", "tahun", "dua"):
        print(w)
