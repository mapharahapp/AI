"""Render a Titik Heran short: Pixabay b-roll + Akram VO + word subtitles + big title cards.
usage: python3 render.py 05|06
"""
import json, subprocess, sys, os

EP = sys.argv[1]
W, H, FPS = 1080, 1920, 30
FONT = "Inter ExtraBold"

def run(cmd):
    subprocess.run(cmd, check=True)

# shots: (orig_start, orig_end, source, src_offset, kind, ilustrasi)
# kind: v = video, i = still image (slow zoom), k = green-screen video keyed on black
if EP == "05":
    TEMPO = 1.18
    AUDIO = "vo05.mp3"
    SHOTS = [
        (0.0, 3.4, "clips/207996.mp4", 0, "v", True),
        (3.4, 6.5, "clips/197826.mp4", 0, "v", False),
        (6.5, 8.0, "clips/211373.mp4", 6, "v", True),
        (8.0, 11.6, "img/201044.jpg", 0, "i", False),
        (11.6, 13.3, "clips/140144.mp4", 0, "k", False),
        (13.3, 16.3, "clips/212499.mp4", 0, "v", False),
        (16.3, 20.0, "clips/288051.mp4", 2, "v", False),
        (20.0, 23.6, "clips/146632.mp4", 1, "v", False),
        (23.6, 26.5, "clips/197826.mp4", 4, "v", False),
        (26.5, 28.6, "clips/211373.mp4", 16, "v", True),
        (28.6, 31.4, "clips/190642.mp4", 3, "v", False),
        (31.4, 33.4, "clips/50570.mp4", 4, "v", False),
        (33.4, 36.0, "clips/31611.mp4", 5, "v", False),
    ]
    TITLES = [  # (orig_start, orig_end, text)
        (0.0, 3.4, "DIKIRA PUNAH,\\NDIJUAL DI PASAR?"),
        (6.5, 8.0, "COELACANTH"),
        (8.0, 11.6, "FOSIL RATUSAN\\NJUTA TAHUN"),
        (13.3, 16.3, "PUNAH 66 JUTA\\NTAHUN LALU?"),
        (16.3, 20.0, "1997 · MANADO"),
        (26.5, 28.6, "SPESIES BARU\\N{\\fs54\\i1}Latimeria menadoensis"),
        (31.4, 33.4, "\"IKAN RAJA LAUT\""),
        (33.4, 36.0, "KAMU PERNAH\\NDENGAR?"),
    ]
    # Scribe spells the TTS respelling; show the real name on screen
    FIX = {"selakan.": "coelacanth."}
else:
    TEMPO = 1.10
    AUDIO = "vo06.mp3"
    SHOTS = [
        (0.0, 2.2, "clips/254367.mp4", 0, "v", False),
        (2.2, 5.2, "clips/311626.mp4", 9, "v", True),
        (5.2, 9.7, "clips/373489.mp4", 3, "v", True),
        (9.7, 13.1, "clips/2150.mp4", 4, "v", False),
        (13.1, 19.0, "clips/173799.mp4", 5, "v", False),
        (19.0, 25.6, "clips/22619.mp4", 3, "v", False),
        (25.6, 27.9, "img/9528384.jpg", 0, "i", True),
        (27.9, 29.6, "clips/269567.mp4", 10, "v", False),
        (29.6, 33.2, "img/6620258.jpg", 0, "i", False),
    ]
    TITLES = [
        (0.0, 5.2, "DANAU TOBA =\\NBEKAS LETUSAN?"),
        (5.2, 9.7, "74.000\\NTAHUN LALU"),
        (9.7, 13.1, "ABU SAMPAI\\NINDIA & AFRIKA"),
        (13.1, 19.0, "HAMPIR PUNAH?"),
        (19.0, 25.6, "2018 · AFRIKA SELATAN\\N{\\fs54}Jurnal Nature"),
        (25.6, 27.9, "ALAT BATU MANUSIA"),
        (27.9, 29.6, "MANUSIA BERTAHAN"),
        (29.6, 33.2, "KAMU BARU TAHU?"),
    ]
    FIX = {}

AUD_LEN = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO]).decode())
OUT_LEN = AUD_LEN / TEMPO + 0.3
os.makedirs(f"seg{EP}", exist_ok=True)

COVER = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
segs = []
for n, (a, b, src, off, kind, ilu) in enumerate(SHOTS):
    a_o = a / TEMPO
    b_o = OUT_LEN if n == len(SHOTS) - 1 else b / TEMPO
    dur = b_o - a_o
    out = f"seg{EP}/{n:02d}.mp4"
    tag = (f",drawtext=fontfile=/usr/share/fonts/opentype/inter/Inter-Medium.otf:text=ilustrasi:"
           f"fontsize=30:fontcolor=white@0.75:x=w-tw-40:y=60") if ilu else ""
    if kind == "v":
        vf = f"{COVER},fps={FPS}{tag}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(off), "-stream_loop", "-1", "-i", src,
               "-t", f"{dur:.3f}", "-vf", vf]
    elif kind == "k":
        vf = (f"color=c=0x05070a:s={W}x{H}:r={FPS}[bg];[0:v]chromakey=0x00ff00:0.25:0.08,"
              f"scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,fps={FPS}{tag}")
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(off), "-stream_loop", "-1", "-i", src,
               "-t", f"{dur:.3f}", "-filter_complex", vf]
    else:
        frames = int(round(dur * FPS))
        vf = (f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=decrease,"
              f"pad={W*2}:{H*2}:(ow-iw)/2:(oh-ih)/2:color=0x05070a,format=yuv420p,"
              f"zoompan=z='1+0.12*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}{tag}")
        if src.endswith("6620258.jpg"):  # vertical aerial: fill the frame instead of letterboxing
            vf = (f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
                  f"zoompan=z='1+0.12*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}{tag}")
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-frames:v", str(frames),
               "-filter_complex", vf]
    cmd += ["-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out]
    run(cmd)
    segs.append(out)

with open(f"seg{EP}/list.txt", "w") as f:
    for s in segs:
        f.write(f"file '{os.path.basename(s)}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"seg{EP}/list.txt",
     "-c", "copy", f"seg{EP}/video.mp4"])

# ---------- ASS: word-chunk captions + title cards ----------
def ts(t):
    t = max(t, 0)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

words = [w for w in json.load(open(f"w{EP}.json"))["words"] if w["type"] == "word"]
# show spoken numbers as digits in the captions
NUMS = {"05": [("enam puluh enam juta", "66 juta"), ("sembilan belas sembilan puluh tujuh,", "1997,")],
        "06": [("tujuh puluh empat ribu", "74.000"), ("dua ribu delapan belas,", "2018,")]}[EP]
for phrase, digits in NUMS:
    p = phrase.split()
    for i in range(len(words) - len(p) + 1):
        if [w["text"].lower() for w in words[i:i + len(p)]] == p:
            words[i:i + len(p)] = [{"text": digits, "type": "word",
                                    "start": words[i]["start"], "end": words[i + len(p) - 1]["end"]}]
            break
    else:
        raise SystemExit(f"number phrase not found: {phrase}")
chunks, cur = [], []
for w in words:
    cur.append(w)
    end_sentence = w["text"][-1] in ".,?:!"
    if len(cur) == 3 or end_sentence:
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)

ass = [
    "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    f"Style: Cap,{FONT},78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,6,2,2,80,80,520,1",
    f"Style: Title,{FONT},92,&H0000E1FF,&H0000E1FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,7,3,8,70,70,300,1",
    "", "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
]
for i, c in enumerate(chunks):
    st = c[0]["start"] / TEMPO
    en = (chunks[i + 1][0]["start"] / TEMPO) if i + 1 < len(chunks) else OUT_LEN
    en = min(en, c[-1]["end"] / TEMPO + 0.6)
    text = " ".join(FIX.get(w["text"], w["text"]) for w in c).upper()
    ass.append(f"Dialogue: 1,{ts(st)},{ts(en)},Cap,,0,0,0,,{text}")
for a, b, t in TITLES:
    b_o = OUT_LEN if b >= SHOTS[-1][1] else b / TEMPO
    ass.append(f"Dialogue: 2,{ts(a / TEMPO)},{ts(b_o)},Title,,0,0,0,,{{\\fad(120,0)}}{t}")
open(f"seg{EP}/subs.ass", "w").write("\n".join(ass) + "\n")

out = f"titik-heran-{EP}.mp4"
run(["ffmpeg", "-v", "error", "-y", "-i", f"seg{EP}/video.mp4", "-i", AUDIO,
     "-filter_complex",
     f"[0:v]ass=seg{EP}/subs.ass[v];[1:a]atempo={TEMPO},apad=pad_dur=0.3,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
     "-map", "[v]", "-map", "[a]", "-t", f"{OUT_LEN:.3f}",
     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
     "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
print(out, OUT_LEN)
