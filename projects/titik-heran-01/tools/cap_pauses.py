"""cap_pauses.py — cap the pauses of the chosen take, using the REAL silences in the wav (energy), not the
alignment's word ends (Scribe's ends run ~0.2 s late here, so trim-vo.py would under-cut).

    python3 tools/cap_pauses.py <projectDir>

Reads raw/vo/take3.words.raw.json (Scribe alignment, audio tags included) and assets/vo/vo.wav
(already loudnormed). Writes assets/vo/vo.wav (spliced, sample-exact) + assets/vo/audio_meta.json in the
tts.mjs shape, words re-timed from the frames ACTUALLY removed. Keeps raw/vo/vo.untrimmed.wav as backup."""
import json, sys, wave, array, math, re, shutil, os

proj = sys.argv[1]
raw = json.load(open(f"{proj}/raw/vo/take3.words.raw.json"))
words = [w for w in raw if not re.fullmatch(r"\[.*\]", w["text"])]          # drop [audio tags]
DISPLAY = {"helowin": "Halloween", "bukan": "bukan"}                         # TTS respelling / emphasis caps -> script text
for w in words:
    core = re.sub(r"[^A-Za-z]", "", w["text"]).lower()
    if core in DISPLAY: w["text"] = re.sub(r"[A-Za-z]+", DISPLAY[core], w["text"], count=1)

wav_p = f"{proj}/assets/vo/vo.wav"; bak = f"{proj}/raw/vo/vo.untrimmed.wav"
if not os.path.exists(bak): shutil.copy(wav_p, bak)
w = wave.open(bak, "rb"); sr = w.getframerate(); n = w.getnframes()
pcm = array.array("h"); pcm.frombytes(w.readframes(n)); w.close()
peak = max(abs(x) for x in pcm); hop = int(sr * 0.01)
rms = [math.sqrt(sum(x * x for x in pcm[i:i + hop]) / hop) for i in range(0, n - hop, hop)]
thr = peak * 0.02

runs, s = [], None
for i, v in enumerate(rms):
    if v < thr:
        if s is None: s = i
    else:
        if s is not None and i - s >= 12: runs.append((s * hop, i * hop))
        s = None

def cap_for(prev_text, next_text):
    if prev_text.endswith("..."): return 99                     # the scripted beat before "dan ganti sayur": keep
    if next_text in ("Ini", "Masalahnya,", "Tapi", "Kirim"): return 0.36   # act changes keep a breath
    if prev_text.endswith("."): return 0.30
    return 0.20                                                  # commas / mid-sentence

cuts = []
for a, b in runs:
    t_end = b / sr
    nxt = next((k for k, wd in enumerate(words) if wd["start"] >= t_end - 0.12), None)
    if nxt is None or nxt == 0: continue                         # leading / trailing air: leave
    cap = cap_for(words[nxt - 1]["text"], words[nxt]["text"])
    dur = (b - a) / sr
    if dur > cap:
        keep = int(cap / 2 * sr); cs, ce = a + keep, b - keep
        if ce > cs: cuts.append((cs, ce, words[nxt - 1]["text"], words[nxt]["text"], round(dur, 3)))

RAMP = int(0.006 * sr); out = array.array("h"); pos = 0; joins = []
for cs, ce, *_ in cuts:
    seg = pcm[pos:cs]; m = min(RAMP, len(seg))
    for k in range(m): seg[len(seg) - m + k] = int(seg[len(seg) - m + k] * (1 - k / m))
    out.extend(seg); joins.append(len(out)); pos = ce
out.extend(pcm[pos:])
for j in joins:
    m = min(RAMP, len(out) - j)
    for k in range(m): out[j + k] = int(out[j + k] * (k / m))

def shift(t):
    f = t * sr; d = 0
    for cs, ce, *_ in cuts:
        if ce <= f: d += ce - cs
        elif cs < f < ce: d += f - cs
    return round((f - d) / sr, 4)

# verify: no cut lands on speech (peak in 30 ms either side < 10 % of take peak)
bad = []
for cs, ce, p, q, _ in cuts:
    win = int(0.03 * sr)
    edge = max(max(abs(x) for x in pcm[cs - win:cs]), max(abs(x) for x in pcm[ce:ce + win]))
    if edge > 0.10 * peak: bad.append((p, q, round(edge / peak, 3)))

ow = wave.open(wav_p, "wb"); ow.setnchannels(1); ow.setsampwidth(2); ow.setframerate(sr)
ow.writeframes(out.tobytes()); ow.close()
for wd in words: wd["start"], wd["end"] = shift(wd["start"]), shift(wd["end"])
dur = round(len(out) / sr, 3)
meta = {"voiceId": "mKyb2q1tbP41xJ8qTnox", "voiceName": "Akram", "modelId": "eleven_v4",
        "source": "ElevenLabs flow YpSWNR6YtnCiwra54JQR, generation A6P5q9rcDz4TuAAMVv7j (take 3 of 4)",
        "scenes": [{"id": "vo", "text": " ".join(w["text"] for w in words), "wav": "vo.wav", "duration": dur,
                    "speechStart": words[0]["start"], "speechEnd": words[-1]["end"],
                    "words": [{"id": f"w{i}", "text": w["text"], "start": w["start"], "end": w["end"]} for i, w in enumerate(words)]}]}
json.dump(meta, open(f"{proj}/assets/vo/audio_meta.json", "w"), ensure_ascii=False, indent=1)
for cs, ce, p, q, d in cuts: print(f"  {p:>14} | {q:<12} pause {d:.2f}s -> cut {(ce - cs) / sr:.2f}s")
print(f"cuts {len(cuts)}  removed {(n - len(out)) / sr:.3f}s  VO {n / sr:.2f} -> {dur:.2f}s  words {len(words)}")
print("speech-edge check:", "OK" if not bad else f"CUTS ON SPEECH: {bad}")
