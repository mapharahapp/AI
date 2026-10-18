"""Render a Titik Heran short: Pixabay b-roll + Akram VO + word subtitles + big title cards.
usage: python3 render.py 05|06|07|08|09|10 [plan|subs]   (run in the episode work dir: clips/, img/, voNN.mp3, wNN.json)
From episode 09 on (STYLE 2): long VO pauses are tightened, the VO is mastered louder (two-pass loudnorm),
the spoken caption word turns yellow, title cards pop in, every shot gets a slow push-in and a colour grade,
and shot/title times can be word anchors: "danau#2" = start of the 2nd "danau", "batu>" = its end, "+0.2" shifts.
"plan" prints the shot and title timing without rendering; "subs" writes only the subtitles (segNN/subs.ass and the .srt).
"""
import json, re, subprocess, sys, os

EP = sys.argv[1]
W, H, FPS = 1080, 1920, 30
FONT = "Inter ExtraBold"
TAGFONT = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
# defaults keep episodes 05-08 as they were rendered
STYLE, LUFS, PAD, TIGHT, TARGET = 1, -14, 0.3, None, None

def run(cmd):
    subprocess.run(cmd, check=True)

# shots: (orig_start, orig_end, source, src_offset, kind, ilustrasi[, opts])
# kind: v video (cover crop), r video cropped to right edge, k green-screen keyed on black,
#       i still letterboxed with slow zoom, f still filling the frame with slow zoom,
#       b still over a blurred copy of itself (STYLE 2), s split screen "top|bottom" (STYLE 2)
# opts (STYLE 2): zoom (push amount, "pull" or "punch"), grade, pos (0-1 crop position), tag (text instead of "ilustrasi"),
#       pan (from, to): the crop slides between two positions over the shot (video only)
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
elif EP == "07":
    TEMPO = 1.18
    AUDIO = "vo07.mp3"
    SHOTS = [
        (0.0, 4.0, "clips/6681.mp4", 2, "v", True),
        (4.0, 6.1, "clips/311.mp4", 22, "r", True),
        (6.1, 8.5, "clips/105377.mp4", 0, "k", True),
        (8.5, 10.8, "clips/213424.mp4", 0, "v", False),
        (10.8, 14.0, "clips/26452.mp4", 2, "v", False),
        (14.0, 19.5, "img/3212803.jpg", 0, "f", False),
        (19.5, 21.3, "clips/86260.mp4", 4, "v", False),
        (21.3, 24.2, "clips/6681.mp4", 9, "v", True),
        (24.2, 28.8, "clips/105377.mp4", 8, "k", True),
        (28.8, 32.4, "clips/146578.mp4", 2, "v", False),
        (32.4, 36.0, "clips/236893.mp4", 4, "v", False),
    ]
    TITLES = [
        (0.0, 4.0, "HIU INI LAHIR\\NZAMAN VOC?"),
        (6.1, 8.5, "HIU GREENLAND"),
        (8.5, 10.8, "LAUT ARKTIK"),
        (10.8, 14.0, "±1 CM\\NPER TAHUN"),
        (14.0, 19.5, "GIMANA CARA\\NHITUNG UMURNYA?"),
        (19.5, 21.3, "2016\\N{\\fs54}Jurnal Science"),
        (21.3, 24.2, "LENSA MATA"),
        (24.2, 28.8, "±400 TAHUN"),
        (28.8, 32.4, "BARU DEWASA\\NUMUR 150"),
        (32.4, 36.0, "KAMU BARU TAHU?"),
    ]
    FIX = {}
elif EP == "08":
    TEMPO = 1.20
    AUDIO = "vo08.mp3"
    SHOTS = [
        (0.0, 3.7, "img/1840201.jpg", 0, "f", True),
        (3.7, 6.5, "clips/366842.mp4", 3, "v", True),
        (6.5, 8.6, "clips/347.mp4", 4, "v", True),
        (8.6, 11.8, "img/573339.jpg", 0, "f", True),
        (11.8, 13.8, "clips/37712.mp4", 2, "v", False),
        (13.8, 19.5, "clips/270311.mp4", 1, "v", False),
        (19.5, 25.7, "img/9333958.jpg", 0, "i", False),
        (25.7, 27.5, "clips/347.mp4", 0, "v", True),
        (27.5, 31.5, "clips/123272.mp4", 1, "v", False),
        (31.5, 34.0, "clips/218955.mp4", 2, "v", False),
        (34.0, 37.2, "clips/367035.mp4", 2, "v", False),
    ]
    TITLES = [
        (0.0, 3.7, "MANUSIA YANG\\NBEREVOLUSI?"),
        (3.7, 6.5, "SUKU BAJAU\\N{\\fs54}Pengembara laut"),
        (6.5, 11.8, "TANPA TABUNG"),
        (11.8, 13.8, "KENAPA BISA?"),
        (13.8, 19.5, "2018 · SULAWESI\\N{\\fs54}Jurnal Cell"),
        (21.5, 25.7, "LIMPA +50%"),
        (25.7, 27.5, "BAHKAN YANG\\NBUKAN PENYELAM"),
        (27.5, 31.5, "TABUNG OKSIGEN\\NALAMI"),
        (31.5, 34.0, "TERTULIS\\NDI GEN"),
        (34.0, 37.2, "KAMU BARU TAHU?"),
    ]
    FIX = {}
elif EP == "09":
    STYLE, LUFS, PAD, TARGET = 2, -12, 0.6, 30.0
    AUDIO = "vo09.mp3"
    TIGHT = {"mati": 0.24, "batu#2": 0.55, "bukan": 0.42, "anehnya": 0.38, "dunia": 0.5}
    SHOTS = [
        ("ada", "hewan", "clips/239675.mp4", 8, "v", True, {"grade": "pop"}),
        ("hewan", "danau#2", "img/3671600.jpg", 0, "f", True, {"grade": "cold"}),
        ("danau#2", "airnya", "img/4821665.jpg", 0, "b", False, {"tag": "Ol Doinyo Lengai, dekat Danau Natron"}),
        ("airnya", "bisa#2", "clips/352978.mp4", 2, "v", True, {}),
        ("bisa#2", "di#2", "clips/168670.mp4", 4, "v", True, {"grade": "pop", "pos": 0.75}),
        ("di#2", "dan", "img/216412.jpg", 0, "b", True, {"grade": "cold"}),
        ("dan", "tampak", "img/7295230.jpg", 0, "f", True, {"grade": "cold"}),
        ("tampak", "benarkah", "img/276191.jpg", 0, "f", True, {"grade": "cold", "pos": 0.04}),
        ("benarkah", "bukan", "img/3671600.jpg", 0, "f", True, {"grade": "cold", "zoom": "pull"}),
        ("bukan", "garam", "img/6635719.jpg", 0, "f", True, {"zoom": "punch"}),
        ("garam", "mengawetkan", "clips/381413.mp4", 3, "v", True, {"grade": "muted"}),
        ("mengawetkan", "mirip", "img/935258.jpg", 0, "b", True, {"grade": "muted"}),
        ("mirip", "anehnya", "img/4078155.jpg", 0, "f", False, {"grade": "muted"}),
        ("anehnya", "danau#4", "clips/172579.mp4", 3, "v", True, {"grade": "pop"}),
        ("danau#4", "tempat", "clips/239675.mp4", 15, "v", True, {"grade": "pop"}),
        ("tempat", "flamingo", "img/4644652.jpg", 0, "b", True, {"grade": "pop"}),
        ("flamingo", "kamu", "clips/120394.mp4", 6, "v", True, {"grade": "pop"}),
        ("kamu", "end", "clips/345464.mp4", 0, "v", True, {}),
    ]
    TITLES = [
        (0, "danau#2", "HEWAN JADI\\NBATU?"),
        ("danau#2", "airnya", "DANAU NATRON\\N{\\fs60}TANZANIA"),
        ("airnya", "di#2", "pH SAMPAI 10,5\\N{\\fs60}SUHU BISA 60°C"),
        ("di#2", "tampak", "BURUNG &\\NKELELAWAR MATI"),
        ("tampak", "benarkah", "SEPERTI PATUNG"),
        ("benarkah", "bukan", "BENARKAH\\NJADI BATU?"),
        ("bukan", "mirip", "BUKAN BATU..."),
        ("mirip", "anehnya", "TAPI \"MUMI\""),
        ("tempat", "kamu", "±75% FLAMINGO\\N{\\fs60}KECIL DUNIA LAHIR DI SINI"),
        ("kamu", "end", "KAMU BERANI\\NKE SINI?\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {}
elif EP == "10":
    STYLE, LUFS, PAD, TARGET = 2, -12, 0.6, 30.0
    AUDIO = "vo10.mp3"
    TIGHT = {"ini#1": 0.2, "enam#1": 0.12, "pecah": 0.42}
    TOP, BOT = {"style": "Label", "pos": (2, 540, 930)}, {"style": "Label", "pos": (8, 540, 990)}
    SHOTS = [
        ("pulau", "dari", "clips/219241.mp4", 0, "v", True, {}),
        ("dari", "pulau#2", "clips/272511.mp4", 1, "v", False, {"zoom": "punch", "grade": "pop"}),
        ("pulau#2", "banda", "clips/231923.mp4", 0.5, "v", True, {}),
        ("banda", "dulu", "img/5779375.jpg", 0, "b", True, {}),
        ("dulu", "tumbuh", "img/2110848.jpg", 0, "f", False, {}),
        ("tumbuh", "harganya", "img/2110851.jpg", 0, "f", False, {}),
        ("harganya", "masalahnya", "clips/134607.mp4", 0.5, "v", True, {}),
        ("masalahnya", "run#2", "clips/374656.mp4", 1, "v", True, {}),
        ("run#2", "padahal", "clips/1204.mp4", 1, "v", False, {}),
        ("padahal", "memonopoli", "clips/21413.mp4", 2, "v", False, {}),
        ("memonopoli", "perang", "img/7004902.jpg", 0, "f", False, {"pos": 0.58}),
        ("perang", "tahun", "clips/338280.mp4", 6, "v", True, {"zoom": "punch", "grade": "cold"}),
        ("tahun", "perjanjian", "clips/33237.mp4", 1, "v", True, {"grade": "bright"}),
        ("perjanjian", "belanda#2", "clips/325497.mp4", 0, "v", True, {"pan": (0.12, 0.5)}),
        ("belanda#2", "inggris#2", "clips/219241.mp4", 2, "v", True, {}),
        ("inggris#2", "yang#1", "clips/219241.mp4|clips/47335.mp4", "3|2", "s", True, {}),
        ("yang#1", "menurutmu", "clips/1366.mp4", 2, "v", False, {}),
        ("menurutmu", "end", "clips/231923.mp4|clips/272511.mp4", "3|5", "s", True, {}),
    ]
    TITLES = [
        (0, "pulau#2", "LEBIH BERHARGA\\NDARI MANHATTAN?"),
        ("pulau#2", "dulu", "PULAU RUN\\N{\\fs60}BANDA, MALUKU"),
        ("dulu", "harganya", "PALA: DULU CUMA\\NTUMBUH DI BANDA"),
        ("harganya", "masalahnya", "HARGA SELANGIT\\NDI EROPA"),
        ("run#2", "perang", "INGGRIS VS\\NBELANDA"),
        ("perang", "tahun", "PERANG!"),
        ("tahun", "belanda#2", "1667\\N{\\fs60}PERJANJIAN BREDA"),
        ("belanda#2", "yang#1", "BELANDA: PULAU RUN", TOP),
        ("inggris#2", "yang#1", "INGGRIS: MANHATTAN", BOT),
        ("yang#1", "menurutmu", "KINI JADI\\NNEW YORK"),
        ("menurutmu", "end", "SIAPA YANG\\NUNTUNG?\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
        ("menurutmu", "end", "PULAU RUN: < 2.000 JIWA", TOP),
        ("menurutmu", "end", "MANHATTAN: ±1,7 JUTA JIWA", BOT),
    ]
    FIX = {}
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

words = [w for w in json.load(open(f"w{EP}.json"))["words"] if w["type"] == "word"]
os.makedirs(f"seg{EP}", exist_ok=True)

def norm(t):
    return re.sub(r"\W", "", t.lower())

def word_index(name):
    """'danau#2' -> index of the 2nd word reading 'danau' (case and punctuation ignored)"""
    base, _, k = name.partition("#")
    hits = [i for i, w in enumerate(words) if norm(w["text"]) == norm(base)]
    if len(hits) < int(k or 1):
        raise SystemExit(f"anchor not found: {name}")
    return hits[int(k or 1) - 1]

def tighten(audio, keep):
    """Shorten long VO pauses (breaths included) to a natural length; shift the word times to match."""
    import numpy as np, wave
    sr, hang = 44100, 6  # 10 ms frames; speech keeps 60 ms of air on each side
    x = np.frombuffer(subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", audio, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]), np.float32)
    n = len(x) // 441
    db = 20 * np.log10(np.sqrt((x[:n * 441].reshape(n, 441) ** 2).mean(1)) + 1e-9)
    act, loud = db > -40, db > -26

    def runs(a, v):
        edges = np.flatnonzero(np.diff(np.r_[False, a == v, False].astype(int)))
        return list(zip(edges[::2], edges[1::2]))
    for s, e in runs(act, True):  # a short quiet sound away from any word is a breath, not speech
        if e - s < 15 and not loud[max(0, s - 10):e + 10].any():
            act[s:e] = False
    sp = act.copy()
    for s, e in runs(act, True):
        sp[max(0, s - hang):e + hang] = True
    want_at = {word_index(k): v for k, v in keep.items()}
    cuts = []
    for s, e in runs(sp, False):
        t0, t1 = s / 100, e / 100
        prev = [i for i, w in enumerate(words) if w["start"] <= t0]
        if not prev or e >= n or e - s < 8:
            continue
        i = prev[-1]
        quiet0, quiet1 = t0 - hang / 100, t1 + hang / 100  # where the voice really stops and starts again
        if t1 < words[i]["end"] - 0.03:  # a stretched stop inside a word
            want = want_at.get(i, 0.10)
        else:  # a pause between words: stay clear of the span Scribe heard as each word
            t0 = max(t0, words[i]["end"] + 0.05)
            if i + 1 < len(words):
                t1 = min(t1, words[i + 1]["start"] - 0.04)
            end = words[i]["text"][-1]
            want = want_at.get(i, 0.36 if end in ".?!" else 0.24 if end in ",;:" else 0.16)
        k = max(0.0, want - (t0 - quiet0) - (quiet1 - t1))
        if t1 - t0 > k + 0.03:
            cuts.append((t0 + 0.6 * k, t1 - 0.4 * k))
    xf = 441  # 10 ms crossfade at each joint
    ramp = np.linspace(0, 1, xf, dtype=np.float32)
    y, last = None, 0
    for c0, c1 in cuts + [(len(x) / sr, None)]:
        p = x[last:int(c0 * sr)]
        y = p if y is None else np.concatenate([y[:-xf], y[-xf:] * (1 - ramp) + p[:xf] * ramp, p[xf:]])
        last = int(c1 * sr) if c1 else 0

    def shift(t):
        d = 0.0
        for c0, c1 in cuts:
            d += c1 - c0 + xf / sr if t >= c1 else max(0.0, t - c0)
        return t - d
    for w in words:
        w["start"], w["end"] = shift(w["start"]), shift(w["end"])
    out = f"seg{EP}/vo_tight.wav"
    with wave.open(out, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
        f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    print(f"VO pauses tightened at {len(cuts)} spots: {len(x) / sr:.2f}s -> {len(y) / sr:.2f}s")
    return out

if TIGHT is not None:
    AUDIO = tighten(AUDIO, TIGHT)
AUD_LEN = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO]).decode())
if TARGET:  # the tempo that lands the video on TARGET seconds
    TEMPO = round(min(max(AUD_LEN / (TARGET - PAD), 1.0), 1.2), 3)
OUT_LEN = AUD_LEN / TEMPO + PAD
NF = round(OUT_LEN * FPS)

def at(a, lead=0.0):
    """shot/title time (seconds or word anchor) -> seconds in the output video"""
    if a == "end":
        return OUT_LEN
    if isinstance(a, str):
        m = re.fullmatch(r"(.+?)(>)?([+-]\d*\.?\d+)?", a)
        w = words[word_index(m.group(1))]
        a = (w["end"] if m.group(2) else w["start"] - lead) + float(m.group(3) or 0)
    return max(a, 0) / TEMPO

# shots cut a frame or so before the word lands; titles appear on the word
FR = [0] + [round(at(s[0], 0.04) * FPS) for s in SHOTS[1:]] + [NF]
TT = []
for t in TITLES:
    a, b = at(t[0]), at(t[1])
    if not isinstance(t[1], str) and t[1] >= SHOTS[-1][1]:
        b = OUT_LEN
    TT.append((a, b) + tuple(t[2:]))
if sys.argv[2:] == ["plan"]:
    print(f"TEMPO {TEMPO}  audio {AUD_LEN:.2f}s  video {OUT_LEN:.2f}s")
    for n, s in enumerate(SHOTS):
        print(f"shot {n:02d} {FR[n] / FPS:6.2f}-{FR[n + 1] / FPS:6.2f} ({(FR[n + 1] - FR[n]) / FPS:4.2f}s) {s[2]}")
    for t in TT:
        print(f"title {t[0]:6.2f}-{t[1]:6.2f} {t[2]}")
    sys.exit()

# ---------- ASS: word-chunk captions + title cards ----------
def ts(t):
    t = max(t, 0)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

# show spoken numbers as digits in the captions
NUMS = {"05": [("enam puluh enam juta", "66 juta"), ("sembilan belas sembilan puluh tujuh,", "1997,")],
        "06": [("tujuh puluh empat ribu", "74.000"), ("dua ribu delapan belas,", "2018,")],
        "07": [("v o c.", "VOC."), ("satu sentimeter", "1 sentimeter"), ("dua ribu enam belas,", "2016,"),
               ("empat ratus", "400"), ("seratus lima puluh.", "150.")],
        "08": [("dua ribu delapan belas,", "2018,"), ("lima puluh persen", "50 persen")],
        "09": [("tiga perempat", "3/4")],
        "10": [("seribu enam ratus enam puluh tujuh,", "1667,")]}[EP]
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
    f"Style: Label,{FONT},56,&H0000E1FF,&H0000E1FF,&H20401E0A,&H00000000,0,0,0,0,100,100,0,0,3,14,0,5,40,40,0,1",
    "", "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
]
for i, c in enumerate(chunks):
    st = c[0]["start"] / TEMPO
    en = (chunks[i + 1][0]["start"] / TEMPO) if i + 1 < len(chunks) else OUT_LEN
    en = min(en, c[-1]["end"] / TEMPO + 0.6)
    txt = [FIX.get(w["text"], w["text"]).upper() for w in c]
    if STYLE < 2:
        ass.append(f"Dialogue: 1,{ts(st)},{ts(en)},Cap,,0,0,0,,{' '.join(txt)}")
        continue
    for k, w in enumerate(c):  # the word being spoken turns yellow; each new chunk pops in
        a = st if k == 0 else w["start"] / TEMPO
        b = c[k + 1]["start"] / TEMPO if k + 1 < len(c) else en
        line = " ".join(f"{{\\c&H00E1FF&}}{t}{{\\c&HFFFFFF&}}" if j == k else t for j, t in enumerate(txt))
        pop = "{\\fscx86\\fscy86\\t(0,90,\\fscx100\\fscy100)}" if k == 0 else ""
        ass.append(f"Dialogue: 1,{ts(a)},{ts(b)},Cap,,0,0,0,,{pop}{line}")
for a, b, t, *rest in TT:
    o = rest[0] if rest else {}
    if STYLE < 2:
        ass.append(f"Dialogue: 2,{ts(a)},{ts(b)},Title,,0,0,0,,{{\\fad(120,0)}}{t}")
        continue
    pos = "\\an{}\\pos({},{})".format(*o["pos"]) if "pos" in o else ""
    pop = "" if a == 0 else "\\fad(60,0)\\fscx70\\fscy70\\t(0,110,\\fscx108\\fscy108)\\t(110,200,\\fscx100\\fscy100)"
    ass.append(f"Dialogue: 2,{ts(a)},{ts(b)},{o.get('style', 'Title')},,0,0,0,,{{{pos}{pop}}}{t}")
open(f"seg{EP}/subs.ass", "w").write("\n".join(ass) + "\n")

# ---------- SRT for the upload: one clause per cue, on two balanced lines when it is long ----------
def srt_ts(t):
    ms = round(max(t, 0) * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
def srt_text(c):
    ws = [FIX.get(w["text"], w["text"]) for w in c]
    if len(" ".join(ws)) <= 42:
        return " ".join(ws)
    k = min(range(1, len(ws)), key=lambda i: abs(len(" ".join(ws[:i])) - len(" ".join(ws[i:]))))
    return " ".join(ws[:k]) + "\n" + " ".join(ws[k:])
cues, cur = [], []
for w in words:
    if cur and len(" ".join(x["text"] for x in cur + [w])) > 84:
        cues.append(cur); cur = []
    cur.append(w)
    if w["text"][-1] in ".,?!":
        cues.append(cur); cur = []
if cur:
    cues.append(cur)
srt = []
for i, c in enumerate(cues):
    st = c[0]["start"] / TEMPO
    en = min(cues[i + 1][0]["start"] / TEMPO if i + 1 < len(cues) else OUT_LEN, c[-1]["end"] / TEMPO + 0.5)
    srt.append(f"{i + 1}\n{srt_ts(st)} --> {srt_ts(en)}\n{srt_text(c)}\n")
open(f"titik-heran-{EP}.srt", "w").write("\n".join(srt))
if sys.argv[2:] == ["subs"]:
    sys.exit()

COVER = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
GRADES = {"base": "eq=contrast=1.06:saturation=1.12", "pop": "eq=contrast=1.08:saturation=1.35",
          "cold": "eq=contrast=1.1:saturation=0.3:brightness=-0.02,colorbalance=rs=-0.05:rm=-0.03:bs=0.07:bm=0.05",
          "muted": "eq=contrast=1.05:saturation=0.65", "bright": "eq=gamma=1.45:contrast=1.15:saturation=1.2"}

def cover(pos=0.5, h=H):
    return (f"scale={W}:{h}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={W}:{h}:(iw-{W})*{pos}:(ih-{h})/2,setsar=1")

def zoom(kind, frames):
    """smooth sub-pixel zoom through the perspective filter (zoompan moves in whole-pixel steps)"""
    N = max(frames - 1, 1)
    z = {"pull": f"1+0.07*(1-on/{N})", "punch": f"1+0.14*exp(-on/4)+0.03*on/{N}"}.get(kind, f"1+{kind}*on/{N}")
    m = f"(1-1/({z}))/2"
    return (f"perspective=x0='W*{m}':y0='H*{m}':x1='W-W*{m}':y1='H*{m}':x2='W*{m}':y2='H-H*{m}'"
            f":x3='W-W*{m}':y3='H-H*{m}':interpolation=cubic:eval=frame")

segs = []
for n, (a, b, src, off, kind, ilu, *rest) in enumerate(SHOTS):
    o = rest[0] if rest else {}
    frames = FR[n + 1] - FR[n]
    dur = frames / FPS
    out = f"seg{EP}/{n:02d}.mp4"
    if STYLE >= 2:
        tag = ""
        if o.get("tag") or ilu:
            open(f"seg{EP}/tag{n:02d}.txt", "w").write(o.get("tag", "ilustrasi"))
            tag = (f",drawtext=fontfile={TAGFONT}:textfile=seg{EP}/tag{n:02d}.txt:fontsize=30:fontcolor=white@0.8"
                   f":shadowcolor=black@0.6:shadowx=2:shadowy=2:x=w-tw-40:y=60")
        look = f"{GRADES[o.get('grade', 'base')]},vignette=angle=PI/6"
        move = f",{zoom(o.get('zoom', 0.06), frames)}" if o.get("zoom", 0.06) else ""
        if kind == "s":
            ins = []
            for p, t in zip(src.split("|"), str(off).split("|")):
                ins += ["-ss", t, "-stream_loop", "-1", "-i", p]
            vf = (f"[0:v]{cover(0.5, H // 2)},fps={FPS}[t];[1:v]{cover(0.5, H // 2)},fps={FPS}[u];[t][u]vstack,"
                  f"drawbox=x=0:y={H // 2 - 4}:w={W}:h=8:color=0x0A1E40:t=fill,{look}{tag}")
        elif kind == "v":
            ins = ["-ss", str(off), "-stream_loop", "-1", "-i", src]
            pos = o.get("pos", 0.5)
            if "pan" in o:  # eased (smoothstep) slide of the crop window; quoted so the commas survive the filtergraph
                p0, p1 = o["pan"]
                e = f"clip(t/{dur:.3f},0,1)"
                pos = f"'({p0}+({p1}-{p0})*{e}*{e}*(3-2*{e}))'"
            vf = f"[0:v]{cover(pos)},fps={FPS},{look}{move}{tag}"
        elif kind == "f":
            ins = ["-loop", "1", "-framerate", str(FPS), "-i", src]
            vf = f"[0:v]{cover(o.get('pos', 0.5))},{look}{move}{tag}"
        else:  # b: sharp still in the middle, its own blurred copy behind
            ins = ["-loop", "1", "-framerate", str(FPS), "-i", src]
            vf = (f"[0:v]split[s][t];[s]{cover()},gblur=sigma=30,eq=brightness=-0.12:saturation=0.8[bg];"
                  f"[t]scale={W}:-2:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,{look}{move}{tag}")
        cmd = ["ffmpeg", "-v", "error", "-y"] + ins + ["-frames:v", str(frames), "-filter_complex", vf + ",format=yuv420p"]
    else:
        tag = (f",drawtext=fontfile={TAGFONT}:text=ilustrasi:"
               f"fontsize=30:fontcolor=white@0.75:x=w-tw-40:y=60") if ilu else ""
        if kind in ("v", "r"):
            cover1 = COVER if kind == "v" else f"scale=-2:{H},crop={W}:{H}:iw-{W}:0,setsar=1"  # r: keep right edge
            vf = f"{cover1},fps={FPS}{tag}"
            cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(off), "-stream_loop", "-1", "-i", src,
                   "-t", f"{dur:.3f}", "-vf", vf]
        elif kind == "k":
            vf = (f"color=c=0x05070a:s={W}x{H}:r={FPS}[bg];[0:v]chromakey=0x00ff00:0.25:0.08,"
                  f"scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,fps={FPS}{tag}")
            cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(off), "-stream_loop", "-1", "-i", src,
                   "-t", f"{dur:.3f}", "-filter_complex", vf]
        else:
            vf = (f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=decrease,"
                  f"pad={W*2}:{H*2}:(ow-iw)/2:(oh-ih)/2:color=0x05070a,format=yuv420p,"
                  f"zoompan=z='1+0.12*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}{tag}")
            if kind == "f" or src.endswith("6620258.jpg"):  # vertical aerial: fill the frame instead of letterboxing
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

# ---------- audio: tempo, then loudness (two-pass and a little louder from 09 on) ----------
af = f"atempo={TEMPO},apad=pad_dur={PAD}"
if STYLE >= 2:
    af += ",acompressor=threshold=-30dB:ratio=4:attack=1:release=60:knee=4"
    ln = f"loudnorm=I={LUFS}:TP=-1.0:LRA=7"
    def stats(chain):
        err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", AUDIO, "-af", f"{chain},{ln}:print_format=json",
                              "-f", "null", "-"], capture_output=True, text=True, check=True).stderr
        return json.loads(err[err.rindex("{"):err.rindex("}") + 1])
    # lift the voice to the target and shave consonant peaks, so loudnorm can stay linear (no pumping)
    af += f",volume={LUFS - float(stats(af)['input_i']) + 0.3:.2f}dB,alimiter=limit=0.79:attack=2:release=50:level=0"
    m = stats(af)
    af += (f",{ln}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
           f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
else:
    af += ",loudnorm=I=-14:TP=-1.5:LRA=11"
out = f"titik-heran-{EP}.mp4"
run(["ffmpeg", "-v", "error", "-y", "-i", f"seg{EP}/video.mp4", "-i", AUDIO,
     "-filter_complex", f"[0:v]ass=seg{EP}/subs.ass[v];[1:a]{af},aresample=48000[a]",
     "-map", "[v]", "-map", "[a]", "-t", f"{OUT_LEN:.3f}",
     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
     "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
print(out, OUT_LEN, TEMPO)
