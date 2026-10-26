"""Render a Titik Heran short: Pixabay b-roll + Akram VO + word subtitles + big title cards.
usage: python3 render.py 05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23 [plan|subs]   (run in the episode work dir: clips/, img/, voNN.mp3, wNN.json)
From episode 09 on (STYLE 2): long VO pauses are tightened, the VO is mastered louder (two-pass loudnorm),
the spoken caption word turns yellow, title cards pop in, every shot gets a slow push-in and a colour grade,
and shot/title times can be word anchors: "danau#2" = start of the 2nd "danau", "batu>" = its end, "+0.2" shifts.
"plan" prints the shot and title timing (and the words spoken in each shot) without rendering; "subs" writes only the subtitles (segNN/subs.ass and the .srt).
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
# opts (STYLE 2): zoom (push amount, "pull" or "punch"), grade, pos (0-1 crop position; "top|bottom" for kind s), tag (text instead of "ilustrasi"),
#       top (kind f: extend the photo upward by this fraction, so the title clears the subject),
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
elif EP == "11":
    STYLE, LUFS, PAD, TARGET = 2, -12, 0.6, 30.0
    AUDIO = "vo11.mp3"
    # Akram read this one slowly (40 s raw): every sentence and comma pause goes down to its natural minimum
    TIGHT = {"cucu": 0.3, "pulaunya": 0.22, "krakatau#3": 0.22, "sukarno-hatta": 0.22, "baru": 0.22, "luas": 0.2,
             "menghapusnya": 0.24, "tenggelam": 0.18, "bertahan#1": 0.22, "menurutmu": 0.16, "bertahan#2": 0.26,
             "laut": 0.16, "berlanjut": 0.16, "tulis": 0.08}
    # clips/skema1883.mp4 and clips/skema2026.mp4 are the map animations made by skema11.py
    SHOTS = [
        ("krakatau", "dulu", "img/10489207.jpg", 0, "f", True, {"zoom": "punch", "grade": "pop"}),
        ("dulu", "melenyapkan", "img/8879993.jpg", 0, "f", True, {"grade": "sepia", "pos": 0.37}),
        ("melenyapkan", "dari", "clips/skema1883.mp4", 0, "v", False, {"tag": "skema", "zoom": 0.03}),
        ("dari", "lahirlah", "clips/37712.mp4", 2, "v", True, {}),
        ("lahirlah", "september", "img/6001245.jpg", 0, "b", False, {"tag": "foto arsip"}),
        ("september", "dua", "clips/97291.mp4", 3, "v", True, {"zoom": "punch", "grade": "pop"}),
        ("dua", "abunya", "clips/97291.mp4", 12.5, "v", True, {"zoom": 0.1, "grade": "pop", "pos": 0.45}),
        ("abunya", "lalu#2", "clips/3586.mp4", 27, "v", True, {"grade": "ash"}),
        ("lalu#2", "erupsi#2", "clips/skema2026.mp4", 0, "v", False, {"tag": "skema", "zoom": 0.03}),
        ("erupsi#2", "berhenti", "clips/152085.mp4", 2, "v", True, {"pos": 0.42}),
        ("berhenti", "anak#2", "clips/279635.mp4", 3, "v", True, {}),
        ("anak#2", "sebelum", "clips/348909.mp4", 2, "v", True, {}),
        ("sebelum", "menurutmu", "img/6001245.jpg", 0, "b", False, {"tag": "foto arsip", "zoom": "pull"}),
        ("menurutmu", "end", "clips/382760.mp4", 2, "v", True, {}),
    ]
    TITLES = [
        (0, "dulu", "KRAKATAU\\NPUNYA CUCU?"),
        ("dulu", "dari", "1883\\N{\\fs60}LETUSAN KRAKATAU"),
        ("dari", "september", "1927\\N{\\fs60}ANAK KRAKATAU LAHIR"),
        ("september", "dua", "4–6 SEPTEMBER\\N2026"),
        ("dua", "abunya", "25 JAM\\NNONSTOP"),
        ("abunya", "lalu#2", "BANDARA\\NSOEKARNO-HATTA\\NDITUTUP"),
        ("lalu#2", "erupsi#2", "2 DARATAN\\NBARU"),
        ("erupsi#2", "berhenti", "ERUPSI LANJUT:\\NMAKIN LUAS"),
        ("berhenti", "anak#2", "ERUPSI BERHENTI:\\NDIKIKIS OMBAK"),
        ("anak#2", "sebelum", "1927–1930\\N{\\fs60}TIMBUL TENGGELAM"),
        ("sebelum", "menurutmu", "BERTAHAN\\NSEJAK 1930"),
        ("menurutmu", "end", "BERTAHAN ATAU\\NHILANG?\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    # the TTS text spells the airport the way it is said; show its real spelling on screen
    FIX = {"Sukarno-Hatta.": "Soekarno-Hatta."}
elif EP == "12":
    STYLE, LUFS, PAD, TARGET = 2, -12, 0.6, 30.0
    AUDIO = "vo12.mp3"
    TIGHT = {"namanya": 0.3}  # a short beat before the name
    SHOTS = [
        ("dikira", "ternyata", "img/7236420.jpg", 0, "f", True, {"zoom": "punch", "grade": "pop", "top": 0.25}),
        ("ternyata", "seorang", "img/6863538.jpg", 0, "f", True, {"pos": 0.6}),
        ("seorang", "lalu", "clips/132493.mp4", 4, "v", True, {}),
        ("lalu", "sadar", "clips/11716.mp4|clips/11626.mp4", "4|2", "s", True, {}),
        ("sadar", "ia", "clips/27038.mp4", 3, "v", True, {"pos": 0.08}),
        ("ia", "ahli", "img/1200175.jpg", 0, "b", True, {}),
        ("ahli", "tes", "img/6656870.jpg", 0, "b", True, {"zoom": 0.03}),  # a slow push, so the labels stay on the spots and tail
        ("tes", "ia#2", "clips/174944.mp4", 2, "v", False, {"grade": "pop"}),
        ("ia#2", "namanya", "img/10429935.jpg", 0, "f", True, {}),
        ("namanya", "bakal", "clips/265333.mp4", 1, "v", True, {}),
        ("bakal", "end", "img/7222680.jpg", 0, "f", True, {"zoom": "pull"}),
    ]
    TITLES = [
        (0, "ternyata", "DIKIRA KUCING\\NKAMPUNG?"),
        ("ternyata", "seorang", "SPESIES BARU!\\N{\\fs60}PERTAMA DALAM 100+ TAHUN"),
        ("seorang", "lalu", "BOLIVIA, ±2016"),
        ("lalu", "sadar", "DIKASIH MI & NASI\\N{\\fs60}±1 TAHUN"),
        ("sadar", "ia", "TERNYATA\\NKUCING LIAR"),
        ("ia", "ahli", "SUAKA SATWA\\N{\\fs60}SENDA VERDE, BOLIVIA"),
        ("ahli", "tutul", "AHLI BIOLOGI\\NCURIGA"),
        ("tutul", "tes", "TUTUL & EKORNYA\\NTIDAK COCOK"),
        ("tutul", "tes", "TUTUL?", {"style": "Label", "pos": (5, 280, 880)}),
        ("ekornya", "tes", "EKOR?", {"style": "Label", "pos": (5, 170, 1575)}),
        ("tes", "ia#2", "TES DNA\\N{\\fs60}38 GENOM DIBANDINGKAN"),
        ("ia#2", "namanya", "TERPISAH ±1,4\\NJUTA TAHUN LALU"),
        ("namanya", "bakal", "LEOPARDUS\\NTILCAYO\\N{\\fs56}RESMI DINAMAI 17 SEP 2026"),
        ("bakal", "end", "KAMU BAKAL\\NSADAR?\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    # the TTS text spells the name the way it is said; show its real spelling on screen
    FIX = {"tilkayo.": "tilcayo."}
elif EP == "13":
    STYLE, LUFS, PAD, TARGET = 2, -12, 0.6, 30.0
    AUDIO = "vo13.mp3"
    TIGHT = {"benar": 0.55}  # a beat after "Dia benar."
    MID = {"pos": (8, 540, 990)}  # below the laughing faces
    # clips/skema_papua.mp4, skema_es.mp4 and skema_bor.mp4 are the schematic animations made by skema13.py
    SHOTS = [
        ("empat", "ditertawakan", "img/2275399.jpg", 0, "f", True, {"zoom": "punch", "grade": "sepia"}),
        ("ditertawakan", "salju", "img/9035692.jpg", 0, "f", True, {"zoom": "punch", "pos": 0.28}),
        ("salju", "khatulistiwa>+0.12", "img/9035692.jpg", 0, "f", True, {"pos": 0.8}),
        ("khatulistiwa>+0.12", "ada", "clips/22512.mp4", 2, "v", True, {"grade": "pop"}),
        ("ada", "tapi", "clips/skema_papua.mp4", 0, "v", False, {"tag": "skema", "zoom": 0.03}),
        ("tapi", "be", "clips/skema_es.mp4", 0, "v", False, {"tag": "skema", "zoom": 0.03}),
        ("be", "es", "clips/376.mp4", 2, "v", True, {"grade": "cold"}),
        ("es", "paling", "clips/3147.mp4", 5, "v", True, {"grade": "cold"}),
        ("paling", "untungnya", "clips/26452.mp4", 2, "v", False, {}),
        ("untungnya", "dan", "clips/skema_bor.mp4", 0, "v", False, {"tag": "skema", "zoom": 0.03}),
        ("dan", "menurutmu", "clips/192281.mp4", 4, "v", True, {"grade": "cold"}),
        ("menurutmu", "end", "clips/220945.mp4", 19, "v", True, {"zoom": "pull"}),
    ]
    TITLES = [
        (0, "ditertawakan", "1623\\N{\\fs60}PENJELAJAH BELANDA"),
        ("ditertawakan", "salju", "DITERTAWAKAN\\N{\\fs60}DI EROPA", MID),
        ("salju", "khatulistiwa>+0.12", "\"SALJU DI\\NKHATULISTIWA?\"", MID),
        ("dia", "ada", "DIA BENAR!"),
        ("ada", "tapi", "PUNCAK JAYA\\N{\\fs60}PAPUA · 4.884 m"),
        ("tinggal", "be", "TINGGAL ±2%"),
        ("be", "paling", "TEBAL ES\\N{\\fs60}32 m (2010) → ±4 m (2024)"),
        ("paling", "untungnya", "BISA HABIS\\NAKHIR 2026\\N{\\fs56}PERKIRAAN BMKG\\N{\\fs56}STUDI LAIN: ±2030"),
        ("untungnya", "dan", "2010: INTI ES\\NDIBOR SAMPAI DASAR"),
        ("dan", "menurutmu", "DISIMPAN BEKU\\N{\\fs60}JADI CATATAN IKLIM"),
        ("menurutmu", "end", "BERTAHAN\\NSAMPAI KAPAN?\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {}
elif EP == "14":
    STYLE, LUFS, PAD, TARGET = 2, -12, 0.6, 30.0
    AUDIO = "vo14.mp3"  # Eleven v4 with audio tags: its pauses are the direction, so none are tightened
    G, P, Y = "{\\c&H5AFF8C&}", "{\\c&HCF8FFF&}", "{\\c&H00E1FF&}"  # green, pink, back to the title yellow
    # clips/skema_*.mp4 are the schematic animations made by skema14.py
    SHOTS = [
        (0, "tidak", "clips/285663.mp4", 3, "v", False, {"zoom": "punch"}),
        ("tidak", "padahal", "clips/skema_warna.mp4", 0, "v", False, {"tag": "skema", "zoom": 0.03}),
        ("padahal", "paling", "clips/365692.mp4", 1, "v", True, {}),
        ("paling", "tapi", "clips/skema_spektrum.mp4", 0, "v", False, {"tag": "skema", "zoom": 0.03}),
        ("tapi", "jadi", "clips/364908.mp4", 0, "v", False, {"pos": 0.45}),
        ("jadi", "barubaru", "clips/skema_putih.mp4", 0, "v", False, {"tag": "skema", "zoom": 0.03}),
        ("barubaru", "bintang#3", "clips/skema_titik.mp4", 0, "v", False, {"tag": "skema · warna perkiraan", "zoom": 0}),
        ("bintang#3", "menelan", "clips/185459.mp4", 4, "v", True, {"pos": 0.62}),
        ("menelan", "natriumnya", "clips/230767.mp4", 2, "v", True, {"pos": 0.6}),
        ("natriumnya", "kuning", "img/6728600.jpg", 0, "f", False, {"pos": 0.62}),
        ("kuning", "mereka", "clips/skema_serap.mp4", 0, "v", False, {"tag": "skema · warna perkiraan", "zoom": 0.03}),
        ("mereka", "end", "clips/skema_duo.mp4", 0, "v", False, {"tag": "skema · warna perkiraan", "zoom": 0.04}),
    ]
    TITLES = [
        (0, "tidak", "BINTANG HIJAU?"),
        ("tidak", "padahal", "BINTANG HIJAU?\\N{\\fs60}TIDAK ADA SATU PUN"),
        ("padahal", "paling", "CAHAYA\\NMATAHARI"),
        ("paling", "tapi", "PALING KUAT\\NDI HIJAU!\\N{\\fs56}puncaknya ±500 nm"),
        ("tapi", "jadi", "WARNA LAIN\\NIKUT BERCAMPUR"),
        ("jadi", "barubaru", "SEMUA WARNA\\N= PUTIH"),
        ("barubaru", "bintang#3", "BINTANG HIJAU\\NPERTAMA!\\N{\\fs56}Univ. Warwick · Okt 2026"),
        ("bintang#3", "menelan", "BINTANG MATI\\N{\\fs60}KATAI PUTIH"),
        ("menelan", "natriumnya", "MENELAN PUING\\NPLANETNYA"),
        ("natriumnya", "kuning", "NATRIUM (Na)\\N{\\fs56}ADA JUGA DI GARAM DAPUR"),
        ("kuning", "menyisakan", "MENYERAP KUNING\\NSAMPAI MERAH"),
        ("menyisakan", "mereka", f"TINGGAL\\N{G}HIJAU!"),
        ("mereka", "kamu", f"ADA JUGA\\NBINTANG {P}PINK!"),
        ("kamu", "end", f"TIM {G}HIJAU{Y}\\NATAU TIM {P}PINK{Y}?\\N{{\\fs58\\c&HFFFFFF&}}@titikheran"),
    ]
    FIX = {}
elif EP == "15":
    STYLE, LUFS, PAD, TARGET = 2, -12, 0.6, 30.0
    AUDIO = "vo15.mp3"
    TIGHT = {"berdentum": 0.75, "khatulistiwa": 0.85, "indonesia#2": 0.5}  # the v4 [pause] beats stay
    # clips/skema_*.mp4 are the schematic maps made by skema15.py
    SHOTS = [
        (0, "besoknya", "clips/225504.mp4", 1, "v", True, {"zoom": "punch"}),
        ("besoknya", "ditemukan", "clips/333648.mp4", 2, "v", True, {}),
        ("ditemukan", "ternyata", "clips/98437.mp4", 3, "v", True, {}),
        ("ternyata", "sejak", "clips/236.mp4", 38, "v", True, {"pos": 0.57}),
        ("sejak", "semua", "clips/skema_riwayat.mp4", 0, "v", False, {"tag": "skema", "zoom": 0.02}),
        ("semua", "pasti", "clips/1236.mp4", 2, "v", True, {"pos": 0.55}),
        ("pasti", "untungnya", "clips/skema_orbit.mp4", 0, "v", False, {"tag": "skema", "zoom": 0.02}),
        ("untungnya", "negara", "img/96866.jpg", 0, "f", True, {"top": 0.4, "grade": "dim"}),  # "TREATY" below the title
        ("negara", "kalau#2", "clips/236.mp4", 44.5, "v", True, {"pos": 0.33}),
        ("kalau#2", "end", "img/2104784.jpg", 0, "f", True, {"zoom": "pull", "pos": 0.45}),
    ]
    TITLES = [
        (0, "besoknya", "DENTUMAN DI\\NLANGIT SAMPIT\\N{\\fs56}Minggu, 18 Okt 2026"),
        ("besoknya", "ternyata", "LOGAM RAKSASA\\NDI KEBUN SAWIT\\N{\\fs56}Kotawaringin Timur, Kalteng"),
        ("ternyata", "sejak", "SISA ROKET\\NCHINA!\\N{\\fs54}ZhuQue-2E · identifikasi BRIN"),
        ("sejak", "semua", "SEJAK 1981\\N{\\fs60}SUDAH BERKALI-KALI"),
        ("semua", "termasuk", "SEMUA ORBIT\\NMELINTASI\\NKHATULISTIWA"),
        ("termasuk", "untungnya", "{\\fs84}TERMASUK DI ATAS\\N{\\fs92}INDONESIA!"),
        ("untungnya", "negara", "KONVENSI PBB 1972\\N{\\fs54}kerugian akibat benda antariksa"),
        ("negara", "kalau#2", "NEGARA PELUNCUR\\NWAJIB GANTI RUGI\\N{\\fs48}Indonesia ikut sejak 1996 · China sejak 1988"),
        ("kalau#2", "end", "KALAU JATUH DI\\NDEKAT RUMAHMU?\\N{\\fs50\\c&HFFFFFF&}jangan disentuh · lapor petugas"
                            "\\N{\\fs58}@titikheran"),
    ]
    FIX = {"Cina!": "China!"}  # written "Cina" for the Indonesian pronunciation
elif EP == "16":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # -15 LUFS from 16 on: Akram back at the level of 05-08
    AUDIO = "vo16.mp3"
    # the v4 [pause] beats stay, only a little shorter
    TIGHT = {"rumahnya": 0.45, "firaun": 0.35, "mesir": 0.3, "diamdiam": 0.4, "lapor#1": 0.3, "meter#1": 0.25,
             "meter#2": 0.3, "kejujurannya": 0.3}
    G, R, Y = "{\\c&H5AFF8C&}", "{\\c&H5A5AFF&}", "{\\c&H00E1FF&}"  # green, red, back to the title yellow
    # clips/skema_*.mp4 are the size comparisons made by skema16.py
    SHOTS = [
        (0, "batu", "img/1534713.jpg", 0, "f", True, {"zoom": "punch", "pos": 0.7}),
        ("batu", "ternyata", "img/587138.jpg", 0, "f", True, {"zoom": 0.08}),
        ("ternyata", "dia", "img/4283322.jpg", 0, "b", True, {"grade": "dim", "zoom": 0.05, "tag": "ilustrasi · Ramses II di Memphis"}),
        ("dia", "dia#2", "img/5268692.jpg", 0, "f", True, {}),
        ("dia#2", "tapi", "img/587138.jpg", 0, "f", True, {"grade": "dim", "zoom": "pull"}),
        ("tapi", "arkeolog", "img/1534713.jpg", 0, "f", True, {"pos": 0.7, "grade": "pop"}),
        ("arkeolog", "kepala#2", "img/59167.jpg", 0, "f", True, {}),
        ("kepala#2", "patung", "clips/skema_kepala.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),  # no push: it cuts on the same head
        ("patung", "balasan", "clips/skema_patung.mp4", 0, "v", False, {"tag": "skema · ukuran perkiraan", "zoom": 0}),
        ("balasan", "dia#4", "clips/198048.mp4", 3, "v", True, {}),
        ("dia#4", "kalau", "img/2217859.jpg", 0, "f", True, {}),
        ("kalau", "end", "img/2166020.jpg", 0, "f", True, {"zoom": "pull", "tag": "ilustrasi · Ramses II di Luxor"}),
    ]
    TITLES = [
        (0, "ternyata", "BATU ANEH DI\\NDEPAN RUMAH"),
        ("kepala", "dia", "DI BAWAHNYA:\\NKEPALA FIRAUN!"),
        ("dia", "dia#2", "KEBUN TIMUN\\N{\\fs56}Delta Nil, Mesir"),
        ("dia#2", "tapi", "SIMPAN\\NDIAM-DIAM?"),
        ("tapi", "arkeolog", f"DIA MEMILIH\\N{G}LAPOR!"),
        ("arkeolog", "kepala#2", "ARKEOLOG\\NMENGGALI"),
        ("kepala#2", "patung", "KEPALA RAKSASA\\NRAMSES II"),
        ("patung", "balasan", "PATUNG UTUH\\N±8,5 METER\\N{\\fs50}perkiraan, termasuk alas"),
        ("balasan", "dia#4", "BALASAN\\NKEJUJURANNYA?"),
        ("dia#4", "kalau", "HADIAH:\\NUMRAH BERDUA!\\N{\\fs48}dari Menteri Pariwisata & Purbakala Mesir"),
        ("kalau", "end", f"{G}LAPOR{Y} ATAU\\N{R}SIMPAN{Y}?\\N{{\\fs58\\c&HFFFFFF&}}@titikheran"),
    ]
    FIX = {}
elif EP == "17":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.93, 30.0  # the v4 take is 29,07 s: no tightening, no speed-up
    AUDIO = "vo17.mp3"
    R, Y = "{\\c&H5A5AFF&}", "{\\c&H00E1FF&}"
    TOP, BOT = {"style": "Label", "pos": (2, 540, 930)}, {"style": "Label", "pos": (8, 540, 990)}  # either side of the split
    # clips/skema_*.mp4 are the map and cross-sections made by skema17.py
    SHOTS = [
        (0, "ditonton", "img/7814755.jpg", 0, "f", True, {"zoom": "punch"}),
        ("ditonton", "padahal", "img/6679479.jpg", 0, "f", True, {"zoom": "pull"}),
        ("padahal", "itu#2", "clips/338283.mp4", 22, "v", True, {"grade": "bright"}),
        ("itu#2", "selatan", "clips/244188.mp4|clips/32451.mp4", "2|10", "s", True, {"pos": "0.5|0.3"}),
        ("selatan", "kenapa", "clips/skema_jawa.mp4", 0, "v", False, {"tag": "skema", "zoom": 0.02}),
        ("kenapa", "membuat", "clips/skema_upwelling.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("membuat", "hiu#3", "img/1656504.jpg", 0, "f", True, {"zoom": 0.08}),
        ("hiu#3", "lalu", "clips/338283.mp4", 38.6, "v", True, {"grade": "bright"}),
        ("lalu", "kalau", "clips/skema_dangkal.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("kalau", "jujur", "img/207401.jpg", 0, "f", True, {}),
        ("jujur", "end", "img/2575575.jpg", 0, "f", True, {"zoom": "pull"}),
    ]
    TITLES = [
        (0, "ditonton", '"PAUS" TERDAMPAR\\NDI PARANGTRITIS'),
        ("ditonton", "padahal", '"PAUS" TERDAMPAR\\NDI PARANGTRITIS\\N{\\fs62}1,4 JUTA TAYANGAN'),
        ("bukan", "itu#2", f"{R}BUKAN{Y} PAUS!"),
        ("itu#2", "ikan", "HIU PAUS!"),
        ("ikan", "selatan", "IKAN TERBESAR\\NDI DUNIA"),
        ("itu#2", "selatan", "PAUS = MAMALIA", TOP),
        ("itu#2", "selatan", "HIU PAUS = IKAN", BOT),
        ("selatan", "titik", "SELATAN JAWA"),
        ("titik", "kenapa", "TITIK PALING\\NRAWAN!\\N{\\fs50}di Indonesia · studi 2011–2023"),
        ("kenapa", "tiap", "KENAPA?"),
        ("tiap", "membuat", "MUSIM KEMARAU:\\NAIR DINGIN NAIK"),
        ("membuat", "hiu#3", "TERI MELIMPAH\\NDEKAT PANTAI"),
        ("hiu#3", "lalu", "MENGEJAR TERI..."),
        ("lalu", "kalau", "TERJEBAK DI\\NAIR DANGKAL"),
        ("kalau", "jujur", "CEPAT LAPOR\\NPETUGAS!\\N{\\fs48}Buleleng, 15 Okt 2026: berhasil dievakuasi ke laut"),
        ("jujur", "end", "JUJUR, KAMU\\NNGIRA ITU PAUS?\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {}
elif EP == "18":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 29,88 s: no tightening, a 1,6 % speed-up
    AUDIO = "vo18.mp3"
    # clips/751c.mp4 is 751 without its letterbox bars; clips/skema_*.mp4 are the timeline, maps and seabed made by skema18.py
    SHOTS = [
        (0, "di", "clips/751c.mp4", 5.5, "v", True, {"zoom": "punch"}),
        ("di", "umurnya", "img/1839616.jpg", 0, "f", False, {"zoom": 0.08}),
        ("umurnya", "ditemukan", "clips/skema_garis.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("ditemukan", "masalahnya", "clips/skema_kekova.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("masalahnya", "jadi", "clips/skema_dasar.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("jadi", "bentuknya", "img/2671703.jpg", 0, "f", True, {"zoom": 0.1}),
        ("bentuknya", "dan#2", "clips/skema_guci.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("dan#2", "menurutmu", "img/3453311.jpg", 0, "f", True, {"zoom": 0.08, "grade": "dim"}),
        ("menurutmu", "end", "img/3702935.jpg", 0, "f", True, {"zoom": "pull", "tag": "ilustrasi · Pulau Kekova"}),
    ]
    TITLES = [
        (0, "umurnya", "TENGGELAM DI\\NZAMAN PIRAMIDA?"),
        ("umurnya", "diklaim", "±4.400–4.700\\NTAHUN"),
        ("diklaim", "ditemukan", "DIKLAIM TERTUA\\NDI DUNIA"),
        ("ditemukan", "masalahnya", "PULAU KEKOVA,\\NTURKI\\N{\\fs50}±30 m di bawah laut"),
        ("masalahnya", "umurnya#2", "KAYUNYA\\NLENYAP"),
        ("umurnya#2", "jadi", "TAK BISA\\NUJI KARBON"),
        ("jadi", "bentuknya", "ARKEOLOG\\NMEMBACA GUCINYA"),
        ("bentuknya", "dan#2", "COCOK DENGAN GUCI\\NZAMAN PERUNGGU\\N{\\fs46}tanah liat dari Lembah Yordan (analisis awal)"),
        ("masih", "menurutmu", "MASIH ADA\\NSISA ISINYA!"),
        ("menurutmu", "end", "ISINYA APA?\\N{\\fs50\\c&HFFFFFF&}minyak zaitun? anggur? getah pohon?\\N{\\fs58}@titikheran"),
    ]
    FIX = {}
elif EP == "19":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 31,32 s: no tightening, a 6,5 % speed-up
    AUDIO = "vo19.mp3"
    Y, O, R = "{\\c&H00E1FF&}", "{\\c&H0090FF&}", "{\\c&H5A5AFF&}"  # yellow, orange, red
    # clips/skema_*.mp4 are the light scattering and particle animations made by skema19.py
    SHOTS = [
        (0, "siang", "img/4361699.jpg", 0, "f", True, {"zoom": "punch"}),
        ("siang", "normalnya", "clips/225244.mp4", 1.0, "v", True, {}),
        ("normalnya", "tapi", "clips/skema_biru.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("tapi", "menghalangi", "clips/204361.mp4", 5.0, "v", True, {}),
        ("menghalangi", "masalahnya", "clips/skema_asap.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("masalahnya", "masker", "clips/skema_pm25.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("masker", "pakai", "img/5760039.jpg", 0, "f", True, {"zoom": 0.08}),
        ("pakai", "di#2", "img/6313929.jpg", 0, "f", True, {"zoom": 0.06}),
        ("di#2", "end", "clips/158384.mp4", 2.0, "v", True, {"zoom": "pull"}),
    ]
    TITLES = [
        (0, "siang", "INI BUKAN\\NFILTER"),
        ("siang", "seperti", "LANGIT KALIMANTAN\\NJADI ORANYE\\N{\\fs50}Palangka Raya, Okt 2026"),
        ("seperti", "normalnya", "SEPERTI\\NDI MARS!"),
        ("normalnya", "tapi", "NORMALNYA:\\NBIRU DISEBAR UDARA"),
        ("tapi", "menghalangi", "ASAP KARHUTLA"),
        ("menghalangi", "yang", "MENGHALANGI\\NCAHAYA BIRU"),
        ("yang", "masalahnya", f"YANG LOLOS:\\N{Y}KUNING, {O}ORANYE,\\N{R}MERAH"),
        ("partikel", "bisa", "PM2.5: 30x LEBIH\\NKECIL DARI RAMBUT"),
        ("bisa", "masker", "BISA MASUK KE\\NPARU-PARU"),
        ("masker", "pakai", f"MASKER KAIN\\N{R}TAK CUKUP"),
        ("pakai", "di#2", "PAKAI N95/KN95\\N{\\fs54}kurangi keluar rumah"),
        ("di#2", "end", "DI KOTAMU,\\NLANGITNYA\\NMASIH BIRU?\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {}
elif EP == "20":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 32,03 s: sentence pauses trimmed a little, then a small speed-up
    AUDIO = "vo20.mp3"
    TIGHT = {"pergi": 0.8, "sengatnya#1": 0.22}  # the whispered hook keeps its dramatic pauses
    # clips/skema_*.mp4 are the stinger, barb, pump, stopwatch and scraping animations made by skema20.py
    SHOTS = [
        (0, "tapi", "clips/39122.mp4", 5.5, "v", False, {"zoom": "punch", "pos": 0.43}),
        ("tapi", "sengat", "clips/skema_sengat.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("sengat", "saat", "clips/skema_gerigi.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("saat", "sengatnya#2", "clips/37902.mp4", 7.5, "v", False, {"pos": 0.47}),
        ("sengatnya#2", "kamera", "clips/skema_kabur.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("kamera", "sengat#2", "clips/16758.mp4", 6.8, "v", True, {"tag": "ilustrasi · slow motion", "pan": (0.87, 0.68), "grade": "dim"}),
        ("sengat#2", "bisa", "clips/skema_pompa.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("bisa", "saat#2", "clips/skema_menit.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("saat#2", "bau", "clips/375601.mp4", 2.0, "v", False, {}),
        ("bau", "memanggil", "img/3700718.jpg", 0, "f", True, {"zoom": 0.1, "grade": "dim"}),
        ("memanggil", "jadi#2", "clips/119962.mp4", 6.0, "v", False, {"grade": "dim"}),
        ("jadi#2", "kamu", "clips/skema_kerok.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("kamu", "end", "clips/165065.mp4", 17.0, "v", False, {"zoom": "pull"}),
    ]
    TITLES = [
        (0, "tapi", "LEBAHNYA\\NSUDAH PERGI..."),
        ("tapi", "sengat", "TAPI SENGATNYA\\NMASIH\\NMENYERANG!"),
        ("sengat", "jadi", "SENGATNYA\\NBERGERIGI"),
        ("jadi", "saat", "TERSANGKUT\\NDI KULIT"),
        ("saat", "sengatnya#2", "LEBAH KABUR..."),
        ("sengatnya#2", "lebahnya#2", "{\\fs84}SENGAT + KANTONG\\NRACUN TERTINGGAL"),
        ("lebahnya#2", "kamera", "LEBAHNYA\\NMATI"),
        ("kamera", "sengat#2", "KAMERA SUPER\\NCEPAT\\N{\\fs50}100–300 fps · PNAS, 12 Okt 2026"),
        ("sengat#2", "seperti", "TERUS MEMOMPA\\NRACUN SENDIRI"),
        ("seperti", "bisa", "SEPERTI MESIN\\N2 PISTON"),
        ("bisa", "saat#2", "BISA SAMPAI\\N1 MENIT!\\N{\\fs48}pompaan kuat 15–70 detik (UNSW)"),
        ("saat#2", "bau", "SAAT\\NMENYENGAT..."),
        ("bau", "memanggil", "BAU MIRIP\\NPISANG!\\N{\\fs48}feromon alarm (isopentil asetat)"),
        ("memanggil", "jadi#2", "MEMANGGIL\\NLEBAH LAIN"),
        ("jadi#2", "kamu", "{\\fs80}KEROK PAKAI\\NKUKU, SECEPATNYA!\\N{\\fs50}jangan tunggu pinset"),
        ("kamu", "end", "KAMU PERNAH\\NDISENGAT LEBAH?\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {}
elif EP == "21":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 30,51 s: no tightening, a 3,8 % speed-up
    AUDIO = "vo21.mp3"
    TOP, BOT = {"style": "Label", "pos": (2, 540, 930)}, {"style": "Label", "pos": (8, 540, 990)}  # either side of the split
    # img/10214497v.jpg is the loris illustration set on a vertical canvas; clips/2104784k.mp4 is the oil palm photo with a slow push-in;
    # clips/skema_*.mp4 are the Bangka map and the rescue counter made by skema21.py
    SHOTS = [
        (0, "ternyata", "img/10214497v.jpg", 0, "f", True, {"zoom": "punch", "grade": "base"}),
        ("ternyata", "namanya", "clips/160892.mp4", 4.0, "v", True, {}),
        ("namanya", "sepuluh", "clips/skema_bangka.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("sepuluh", "beberapa", "clips/skema_selamat.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("beberapa", "hutannya", "clips/10749.mp4", 0.5, "v", True, {"pos": 0.3, "grade": "cold"}),
        ("hutannya", "kini", "clips/210647.mp4|clips/2104784k.mp4", "26|0", "s", True, {}),
        ("kini", "delapan", "img/10214497v.jpg", 0, "f", True, {"zoom": "pull", "grade": "pop"}),
        ("delapan", "di", "clips/233197.mp4", 30.0, "v", True, {"zoom": 0.1}),
        ("di", "end", "clips/11721.mp4", 12.0, "v", True, {"zoom": "pull"}),
    ]
    TITLES = [
        (0, "dikira", "PRIMATA\\NBERBISA"),
        ("dikira", "ternyata", "DIKIRA PUNAH\\N±100 TAHUN"),
        ("ternyata", "namanya", "TERNYATA ADA DI\\NKEBUN WARGA!"),
        ("namanya", "catatan", "KUKANG BANGKA"),
        ("catatan", "sepuluh", "{\\fs84}CATATAN TERAKHIR:\\NZAMAN BELANDA"),
        ("sepuluh", "sekitar", "10 TAHUN\\NTERAKHIR"),
        ("sekitar", "beberapa", "90+ EKOR\\NDISELAMATKAN"),
        ("beberapa", "hutannya", "KESETRUM\\NKABEL LISTRIK\\N{\\fs48}min. 7 ekor luka bakar"),
        ("hutannya", "tambang", "HUTANNYA\\NTERUS BERUBAH..."),
        ("tambang", "kini", "TAMBANG TIMAH", TOP),
        ("sawit", "kini", "KEBUN SAWIT", BOT),
        ("kini", "ia#2", "ILMUWAN\\NMEMASTIKAN:\\N{\\fs50}Spixiana, Okt 2026"),
        ("ia#2", "delapan", "IA MASIH ADA!"),
        ("delapan", "di", "{\\fs150}86{\\fs92}\\NEKOR KEMBALI\\NKE HUTAN"),
        ("di", "end", "DI DAERAHMU\\NMASIH ADA\\NKUKANG?\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {}
elif EP == "22":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 30,24 s: no tightening, a 3 % speed-up
    AUDIO = "vo22.mp3"
    # clips/142647n.mp4 is the wing and storm cloud graded to night under a taller sky, with a faint red flash above the cloud (skema22.py malam);
    # clips/skema_*.mp4 are the 1989 tape, the altitude diagram, the Calvi reconstruction and the map made by skema22.py
    SHOTS = [
        (0, "kilatan", "clips/47338.mp4", 9.5, "v", True, {"grade": "night", "pos": 0.7, "zoom": "punch"}),
        ("kilatan", "tapi", "clips/142647n.mp4", 0, "v", True, {"zoom": 0.05}),
        ("tapi", "sampai", "clips/125192.mp4", 6.4, "v", True, {}),  # flickers from the start, the long flash lands on "Kilatannya"
        ("sampai", "tak", "clips/24496.mp4", 2.4, "v", True, {"pos": 0.55}),
        ("tak", "namanya", "clips/skema_1989.mp4", 0, "v", False, {"tag": "rekonstruksi", "zoom": 0}),
        ("namanya", "september", "clips/skema_tinggi.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("september", "padahal", "clips/skema_korsika.mp4", 0, "v", False, {"tag": "rekonstruksi · foto kota Calvi, Korsika", "zoom": 0}),
        ("padahal", "kirim", "clips/skema_peta.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("kirim", "end", "clips/226276.mp4", 9.4, "v", True, {"zoom": "pull"}),
    ]
    TITLES = [
        (0, "kilatan", "PULUHAN TAHUN,\\NPARA PILOT\\NMELAPORKAN..."),
        ("kilatan", "tapi", "KILATAN ANEH\\NDI ATAS BADAI"),
        ("tapi", "kilatannya", "TAPI ILMUWAN\\NRAGU"),
        ("kilatannya", "sampai", "CUMA BEBERAPA\\NMILIDETIK"),
        ("sampai", "tak", "SAMPAI SEBUAH\\NKAMERA..."),
        ("tak", "namanya", "JULI 1989\\N{\\fs50}terekam pertama kali\\Noleh Univ. of Minnesota"),
        ("namanya", "kilat", "RED SPRITE"),
        ("kilat", "nyaris", "KILAT MERAH\\NRAKSASA"),
        ("nyaris", "september", "NYARIS DI TEPI\\NLUAR ANGKASA"),
        ("september", "seolah", "16 SEP 2026\\NKORSIKA, PRANCIS\\N{\\fs50}fotografer: Florian Riou"),
        ("seolah", "padahal", "SEOLAH MELAYANG\\NDI ATAS DESA"),
        ("padahal", "kirim", "BADAINYA\\NDI SPANYOL!"),
        ("kirim", "end", "KIRIM KE TEMANMU\\NYANG TAKUT PETIR!\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {"sprait:": "sprite:"}  # sent to the TTS as "red sprait" so Akram reads it the English way
elif EP == "23":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 31,92 s: a few long pauses trimmed, then a small speed-up
    AUDIO = "vo23.mp3"
    TIGHT = {"makannya": 0.3, "hal": 0.48, "main#2": 0.34, "terbakar": 0.42, "diselamatkan": 0.22, "bayinya": 0.30, "pertamamu": 0.22}  # the whispered hook and the turn to the fires keep their pauses
    MID = {"style": "Label", "pos": (5, 540, 960)}  # on the line of the split screen
    # clips/8325935k.mp4 and clips/4703397k.mp4 are the two young orangutan photos as slow push-in clips for the split screen,
    # clips/6055308j.mp4 is the playful young orangutan with a "JADWAL MAIN" calendar sticker popping in (prep23.py);
    # clips/skema_*.mp4 are the Tuanan map, the top-down playdate walk and the rescue counter made by skema23.py
    SHOTS = [
        (0, "teman#1", "clips/180691.mp4", 0.0, "v", True, {"zoom": "punch", "pos": 0.5}),
        ("teman#1", "orangutan#2", "clips/8325935k.mp4|clips/4703397k.mp4", "0|0", "s", True, {}),
        ("orangutan#2", "lima#1", "img/3712512.jpg", 0, "b", True, {"zoom": "pull"}),
        ("lima#1", "induk#2", "clips/skema_tuanan.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("induk#2", "persis", "clips/skema_main.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("persis", "tapi", "clips/6055308j.mp4", 0, "v", True, {"zoom": "punch"}),
        ("tapi", "kembali", "clips/225244.mp4", 1.0, "v", True, {}),
        ("kembali", "lebih#2", "img/62864.jpg", 0, "f", True, {"tag": "ilustrasi · citra satelit lama", "zoom": 0.08}),
        ("lebih#2", "termasuk", "clips/skema_selamat.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("termasuk", "siapa", "img/6230436.jpg", 0, "f", True, {"zoom": 0.08}),
        ("siapa", "end", "img/3985939.jpg", 0, "f", True, {"zoom": "pull", "pos": 0.26}),
    ]
    TITLES = [
        (0, "teman#1", "INDUK ORANGUTAN\\NRELA MENGURANGI\\NWAKTU MAKAN..."),
        ("teman#1", "orangutan#2", "DEMI TEMAN MAIN\\NUNTUK ANAKNYA", MID),
        ("orangutan#2", "lima#1", "KERA BESAR\\NPALING PENYENDIRI"),
        ("lima#1", "induk#2", "15 TAHUN\\NDIAMATI\\N{\\fs50}jurnal PNAS, 6 Okt 2026"),
        ("induk#2", "mendekati", "INDUK BERJALAN\\NLEBIH JAUH"),
        ("mendekati", "persis", "MENDEKATI\\NANAK SEBAYA"),
        ("persis", "tapi", "PERSIS MENGATUR\\NJADWAL MAIN!"),
        ("tapi", "lebih#2", "HUTAN KALIMANTAN\\NKEMBALI TERBAKAR"),
        ("lebih#2", "termasuk", "53 ORANGUTAN\\NDISELAMATKAN"),
        ("termasuk", "siapa", "TERMASUK INDUK\\N& BAYINYA"),
        ("siapa", "end", "SIAPA TEMAN MAIN\\NPERTAMAMU?\\N{\\fs58\\c&HFFFFFF&}Tag dia! @titikheran"),
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

def drop_tags(words, audio):
    """Eleven v4 audio tags ([pause], [short pause], [curious] ...) come back from Scribe as words with a sliver of time,
    often taken from the start of the next word: drop them and start that word where the voice does."""
    import numpy as np
    x = np.frombuffer(subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", audio, "-ac", "1", "-ar", "44100", "-f", "f32le", "-"]), np.float32)
    n = len(x) // 441
    act = 20 * np.log10(np.sqrt((x[:n * 441].reshape(n, 441) ** 2).mean(1)) + 1e-9) > -40  # 10 ms frames
    out, tag0 = [], None
    for w in words:
        if w["text"].startswith("[") or w["text"].endswith("]"):
            tag0 = w["start"] if tag0 is None else tag0
            continue
        if tag0 is not None:
            on = np.flatnonzero(act[int(tag0 * 100):]) if int(tag0 * 100) < n else []
            if len(on):
                w["start"] = min(w["start"], max(tag0, (int(tag0 * 100) + on[0]) / 100))
            tag0 = None
        out.append(w)
    return out
if any(w["text"].startswith("[") for w in words):
    words = drop_tags(words, AUDIO)

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
        t0, t1 = FR[n] / FPS, FR[n + 1] / FPS
        print("    " + " ".join(f"{w['text']}@{w['start'] / TEMPO - t0:.2f}" for w in words if t0 <= w["start"] / TEMPO < t1))
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
        "10": [("seribu enam ratus enam puluh tujuh,", "1667,")],
        "11": [("dua puluh lima", "25")],
        "12": [("seratus", "100"), ("de en a", "DNA"), ("satu koma empat juta", "1,4 juta")],
        "13": [("empat ratus", "400"), ("dua persen.", "2 persen."), ("be em ka ge", "BMKG"),
               ("dua ribu dua puluh enam.", "2026.")],
        "14": [],
        "15": [("seribu sembilan ratus delapan puluh satu,", "1981,")],
        "16": [("ramses kedua,", "Ramses II,"), ("satu koma enam meter!", "1,6 meter!"), ("delapan setengah meter.", "8,5 meter.")],
        "17": [("sejuta", "1 juta")],
        "18": [("empat ribu tujuh ratus", "4.700")],
        "19": [("tiga puluh", "30"), ("en sembilan lima,", "N95,")],
        "20": [("satu menit!", "1 menit!"), ("dua piston.", "2 piston.")],
        "21": [("seratus", "100"), ("sepuluh", "10"), ("sembilan puluh", "90"), ("delapan puluh enam", "86")],
        "22": [("lima ratus", "500")],
        "23": [("lima belas", "15"), ("lima puluh", "50")]}[EP]
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
    if w["text"][-1] in ".,?!:":
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
          "muted": "eq=contrast=1.05:saturation=0.65", "bright": "eq=gamma=1.45:contrast=1.15:saturation=1.2",
          "sepia": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,eq=contrast=1.08",
          "ash": "curves=all='0/0 0.5/0.34 1/0.68',eq=contrast=1.15:saturation=0.4,colorbalance=rm=0.04:gm=0.02:bm=-0.04",
          "dim": "eq=brightness=-0.12:contrast=1.05:saturation=0.9",
          # day for night: highlights pulled down to moonlight, colour drained, shadows pushed blue
          "night": "curves=all='0/0 0.35/0.11 0.7/0.32 1/0.56',eq=saturation=0.5,colorbalance=bs=0.16:bm=0.1:bh=0.05:rs=-0.06:rm=-0.05:gs=-0.02,"
                   "eq=contrast=1.06:saturation=1.12"}

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
            ins, pt, pb = [], *str(o.get("pos", "0.5|0.5")).split("|")
            for p, t in zip(src.split("|"), str(off).split("|")):
                ins += ["-ss", t, "-stream_loop", "-1", "-i", p]
            vf = (f"[0:v]{cover(pt, H // 2)},fps={FPS}[t];[1:v]{cover(pb, H // 2)},fps={FPS}[u];[t][u]vstack,"
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
            # top: room above the subject for the title, the photo's top edge stretched upward and blurred
            pre = (f"format=rgb24,split[m][n];[n]crop=iw:ih*0.04:0:0,scale=iw:ih*{o['top'] / 0.04:g},gblur=sigma=20[e];"
                   f"[e][m]vstack,") if "top" in o else ""
            vf = f"[0:v]{pre}{cover(o.get('pos', 0.5))},{look}{move}{tag}"
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
           f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
           ",alimiter=limit=0.83:attack=1:release=40:level=0")  # loudnorm's make-up gain can push peaks back over -1 dBTP
else:
    af += ",loudnorm=I=-14:TP=-1.5:LRA=11"
out = f"titik-heran-{EP}.mp4"
run(["ffmpeg", "-v", "error", "-y", "-i", f"seg{EP}/video.mp4", "-i", AUDIO,
     "-filter_complex", f"[0:v]ass=seg{EP}/subs.ass[v];[1:a]{af},aresample=48000[a]",
     "-map", "[v]", "-map", "[a]", "-t", f"{OUT_LEN:.3f}",
     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
     "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
print(out, OUT_LEN, TEMPO)
