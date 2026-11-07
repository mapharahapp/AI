"""Render a Titik Heran short: Pixabay b-roll + Akram VO + word subtitles + big title cards.
usage: python3 render.py 05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42|43|44 [plan|subs]   (run in the episode work dir: clips/, img/, voNN.mp3, wNN.json)
From episode 09 on (STYLE 2): long VO pauses are tightened, the VO is mastered louder (two-pass loudnorm),
the spoken caption word turns yellow, title cards pop in, every shot gets a slow push-in and a colour grade,
and shot/title times can be word anchors: "danau#2" = start of the 2nd "danau", "batu>" = its end, "+0.2" shifts.
From episode 26 on every video carries a faint "@titikheran" watermark in the middle of the frame, under the titles and captions.
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
elif EP == "24":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 31,40 s with short natural pauses: no tightening, a 6,8 % speed-up
    AUDIO = "vo24.mp3"
    G, R, Y = "{\\c&H5AFF8C&}", "{\\c&H5A5AFF&}", "{\\c&H00E1FF&}"  # green, red, back to the title yellow
    # clips/skema_*.mp4 are the map, the CT sweep, the crossed-out senyulong and the missing snout made by skema24.py;
    # clips/1057155c.mp4 is the Sphinx face with a ring drawn round the missing nose (skema24.py hidung)
    SHOTS = [
        (0, "buaya", "img/997632.jpg", 0, "f", False, {"zoom": 0.1, "pos": 0.58, "top": 0.15}),
        ("buaya", "hampir", "img/3940781.jpg", 0, "b", True, {"zoom": "punch"}),
        ("hampir", "tengkoraknya", "img/388557.jpg", 0, "f", True, {"grade": "sepia", "pos": 0.19}),
        ("tengkoraknya", "lalu", "clips/223565.mp4", 3.0, "v", False, {"pos": 0.95}),
        ("lalu", "buaya#2", "img/347262.jpg", 0, "b", True, {"tag": "ilustrasi · senyulong"}),
        ("buaya#2", "sampai", "clips/skema_peta.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("sampai", "membongkar", "clips/4122.mp4", 0, "v", True, {"zoom": 0.1}),
        ("membongkar", "ia#2", "clips/skema_scan.mp4", 0, "v", False, {"tag": "skema · tengkorak ilustrasi", "zoom": 0}),
        ("ia#2", "tapi", "clips/skema_coret.mp4", 0, "v", True, {"tag": "ilustrasi · senyulong", "zoom": 0}),
        ("tapi", "namanya", "img/7745715.jpg", 0, "f", True, {"zoom": "punch", "pos": 0.82, "top": 0.25, "tag": "ilustrasi · gharial India"}),
        ("namanya", "sebab", "img/7105523.jpg", 0, "b", False, {"zoom": 0.08}),
        ("sebab", "persis", "clips/skema_moncong.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("persis", "kirim", "clips/1057155c.mp4", 0, "v", False, {"zoom": "punch"}),
        ("kirim", "end", "clips/205415.mp4", 1.0, "v", False, {"zoom": "pull"}),
    ]
    TITLES = [
        (0, "buaya", "BUAYA PURBA\\NDI BATU SPHINX"),
        ("buaya", "hampir", "BUAYA PURBA\\NDI BATU SPHINX\\N{\\fs60}umurnya ±45 juta tahun"),
        ("hampir", "ia", "HAMPIR\\N100 TAHUN..."),
        ("ia", "tengkoraknya", f"{R}SALAH{Y}\\NDIKENALI!"),
        ("tengkoraknya", "lalu", "DIGALI DEKAT\\NKAIRO\\N{\\fs50}1920-an · batu kapur Formasi Mokattam"),
        ("lalu", "buaya#2", "1927: DICAP\\NKERABAT\\NSENYULONG"),
        ("buaya#2", "sampai", "BUAYA MONCONG\\NPANJANG"),
        ("sampai", "ia#2", "CT SCAN\\NMEMBONGKARNYA"),
        ("ia#2", "tapi", f"{R}BUKAN{Y} GOLONGAN\\NSENYULONG"),
        ("tapi", "namanya", f"CABANG AWAL\\NKELUARGA {G}GHARIAL!{Y}\\N{{\\fs50}}pemburu ikan di laut dangkal Mesir"),
        ("namanya", "dewa", "HERUGAVIALIS\\N{\\fs64}CAIRENSIS"),
        ("dewa", "sebab", "HERU = HORUS\\N{\\fs50}Sphinx dipuja sebagai Horus"),
        ("sebab", "persis", "UJUNG MONCONGNYA\\NHILANG..."),
        ("persis", "kirim", "PERSIS HIDUNG\\NSPHINX!"),
        ("kirim", "end", "KIRIM KE TEMANMU\\NYANG SUKA\\NMISTERI MESIR!\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    # sent to the TTS as Akram should say them; the captions show the real spelling
    FIX = {"Sfinks...": "Sphinx...", "Sfinks!": "Sphinx!", "garial!": "gharial!"}
elif EP == "25":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 32,37 s: sentence pauses trimmed a little, then a small speed-up
    AUDIO = "vo25.mp3"
    # the whispered hook, "pertamanya...", "kongres...", "ketiga:" and "satu..." keep their dramatic pauses
    TIGHT = {"pemuda": 0.46, "kertas": 0.30, "pertamanya": 0.22, "belanda": 0.30, "pemuda#2": 0.22, "mengawasi": 0.30,
             "pidato": 0.20, "kongres#2": 0.40, "elegan": 0.32, "setuju": 0.20, "dibacakan": 0.30, "ketiga": 0.32, "satu": 0.31,
             "persatuan": 0.29}
    G, R, Y = "{\\c&H5AFF8C&}", "{\\c&H5A5AFF&}", "{\\c&H00E1FF&}"  # green, red, back to the title yellow
    # clips/skema_*.mp4 are the reconstructed note, the whisper, the initials and the three pledges made by skema25.py
    SHOTS = [
        (0, "dan", "clips/87050.mp4", 1.0, "v", True, {"grade": "sepia", "zoom": 0.1, "pos": 0.55}),
        ("dan", "malam", "clips/skema_tulis.mp4", 0, "v", False, {"tag": "rekonstruksi", "zoom": 0}),
        ("malam", "polisi", "img/1033489.jpg", 0, "f", True, {"grade": "night", "pos": 0.05, "tag": "ilustrasi · gedung kolonial di Kota Tua Jakarta"}),
        ("polisi", "di", "clips/4615.mp4", 2.0, "v", True, {"pos": 0.47}),
        ("di", "saya", "clips/107240.mp4", 2.0, "v", True, {"pos": 0.62}),
        ("saya", "sugondo", "clips/skema_bisik.mp4", 0, "v", False, {"tag": "rekonstruksi", "zoom": 0}),
        ("sugondo", "dan#2", "clips/skema_paraf.mp4", 0, "v", False, {"tag": "rekonstruksi", "zoom": 0}),
        ("dan#2", "tapi", "clips/107243.mp4", 2.0, "v", True, {"pos": 0.32}),
        ("tapi", "kirim", "clips/skema_ikrar.mp4", 0, "v", False, {"tag": "rekonstruksi · ejaan asli", "zoom": 0}),
        ("kirim", "end", "img/2792979.jpg", 0, "f", True, {"zoom": 0.08, "pos": 0.23}),
    ]
    TITLES = [
        (0, "dan", "SUMPAH PEMUDA\\NLAHIR DARI\\NSECARIK KERTAS"),
        ("dan", "bahasa", "BISIKAN\\NPERTAMANYA..."),
        ("bahasa", "malam", "BAHASA\\NBELANDA!"),
        ("malam", "polisi", "28 OKTOBER 1928\\N{\\fs56}malam terakhir Kongres Pemuda II, Batavia"),
        ("polisi", "di", "DIAWASI\\NPOLISI BELANDA"),
        ("di", "yamin", "DI TENGAH\\NPIDATO...\\N{\\fs50}Sunario sedang berpidato"),
        ("yamin", "saya", "MOHAMMAD YAMIN\\N{\\fs56}menyodorkan kertas ke Sugondo,\\Nketua kongres"),
        ("saya", "sugondo", "YAMIN\\NBERBISIK..."),
        ("sugondo", "kertas#3", f"PARAF SUGONDO:\\N{G}\"SETUJU\""),
        ("kertas#3", "dan#2", "KERTAS\\NBEREDAR..."),
        ("dan#2", "tapi", "DIBACAKAN\\NMALAM ITU JUGA!"),
        ("tapi", "bukan", "CEK IKRAR\\NKETIGA!"),
        ("bukan", "melainkan", f"BUKAN\\N{R}\"BERBAHASA SATU\""),
        ("melainkan", "kirim", f"TAPI {G}\"MENJUNJUNG\\NBAHASA PERSATUAN\""),
        ("kirim", "end", "KIRIM KE TEMANMU\\NYANG MASIH HAFAL\\N\"BERBAHASA SATU\"!\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    # the misquote is set in quotes in the captions
    FIX = {"berbahasa": "\"berbahasa", "satu...": "satu\"...", "satu!": "satu\"!"}
elif EP == "26":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 34,27 s: the plain pauses trimmed, then a speed-up
    AUDIO = "vo26.mp3"
    # Scribe stretches each word over the pause after it, so every pause gets its own length here;
    # the dramatic ones ("ini...", "penemuannya...", "makanannya...", "sehat...", "sentuhan...", "milimeter...") are kept whole
    TIGHT = {"ini": 0.4, "sentuhan": 0.32, "penemuannya": 1.0, "sengaja": 0.24, "kepanasan": 0.16, "makanannya": 1.0,
             "memutih": 0.18, "kelaparan": 0.24, "stanford": 0.16, "sehat": 1.0, "memutih#2": 0.24, "sentuhan#2": 1.0,
             "kembali": 0.2, "diuji": 0.16, "minggu": 0.2, "milimeter": 0.32, "mati": 0.22, "menolak": 0.16, "organ": 0.18}
    G, R, Y = "{\\c&H5AFF8C&}", "{\\c&H5A5AFF&}", "{\\c&H00E1FF&}"  # green, red, back to the title yellow
    # clips/skema_*.mp4 are the heat and algae overlay, the reconstructed fall and recovery, the 10-pair test
    # and the rejection made by skema26.py
    SHOTS = [
        (0, "hidup", "img/1354925.jpg", 0, "f", True, {"grade": "cold", "zoom": 0.1, "pos": 0.6}),
        ("hidup", "sentuhan", "img/3628397.jpg", 0, "f", True, {"pos": 0.62}),
        ("sentuhan", "dan", "img/3628397.jpg", 0, "f", True, {"zoom": "punch", "pos": 0.62}),
        ("dan", "kepanasan", "clips/192281.mp4", 1.0, "v", True, {"pan": (0.3, 0.6)}),
        ("kepanasan", "memutih", "clips/skema_panas.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("memutih", "di", "img/7754905.jpg", 0, "f", True, {"grade": "muted", "zoom": 0.08}),
        ("di", "diuji", "clips/skema_sentuh.mp4", 0, "v", False, {"tag": "rekonstruksi", "zoom": 0}),
        ("diuji", "milimeter", "clips/skema_uji.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("milimeter", "mati", "img/20497v.jpg", 0, "f", True, {"zoom": 0.05}),  # prep26.py: the skeleton on black
        ("mati", "tapi", "img/20497v.jpg", 0, "f", True, {"zoom": "punch"}),
        ("tapi", "seperti", "clips/skema_tolak.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("seperti", "kirim", "clips/378726.mp4", 1.0, "v", True, {"pos": 0.56}),
        ("kirim", "end", "clips/273757.mp4", 1.0, "v", False, {"zoom": "pull"}),
    ]
    TITLES = [
        (0, "hidup", "KARANG SEKARAT\\NINI..."),
        ("hidup", "dan", f"{G}HIDUP LAGI{Y}\\NKARENA SATU\\NSENTUHAN"),
        ("dan", "kepanasan", "DITEMUKAN\\NTANPA SENGAJA\\N{\\fs50}studi Stanford, terbit 14 Okt 2026"),
        ("kepanasan", "memutih", "LAUT KEPANASAN,\\NALGA DIUSIR\\N{\\fs50}alga = sampai 90% energi karang"),
        ("memutih", "di", "MEMUTIH,\\NLALU KELAPARAN\\N{\\fs50}84% terumbu dunia kena panas\\Npemutih (2023-2025)"),
        ("di", "di#2", "LAB STANFORD,\\NCALIFORNIA\\N{\\fs50}potongan sehat menimpa\\Nkembarannya (klon)"),
        ("di#2", "warnanya", "DI TITIK\\NSENTUHAN..."),
        ("warnanya", "diuji", f"{G}WARNANYA\\NKEMBALI!{Y}\\N{{\\fs50}}alga terlihat pindah\\Ndalam 3 hari"),
        ("diuji", "pulih", "UJI 10 PASANG\\NKARANG KEMBAR"),
        ("pulih", "yang#3", f"{G}PULIH PENUH{Y}\\NDALAM 7 MINGGU ✓"),
        ("yang#3", "mati", "DIPISAH\\NBEBERAPA MM..."),
        ("mati", "tapi", f"DIPISAH\\NBEBERAPA MM...\\N{R}MATI"),
        ("tapi", "karang#4", "TAPI HARUS\\NKEMBARAN SENDIRI\\N{\\fs50}klon dari koloni yang sama"),
        ("karang#4", "seperti", f"KARANG ASING\\N{R}SALING MENOLAK"),
        ("seperti", "kirim", "SEPERTI TUBUH\\NMENOLAK ORGAN\\NCANGKOKAN"),
        ("kirim", "end", "KIRIM KE\\NSAUDARAMU YANG\\NSELALU MENOLONGMU!\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {}
elif EP == "27":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 30,43 s: no tightening, a small speed-up
    AUDIO = "vo27.mp3"
    G, R, Y = "{\\c&H5AFF8C&}", "{\\c&H5A5AFF&}", "{\\c&H00E1FF&}"  # green, red, back to the title yellow
    # clips/skema_*.mp4 are the 1859 map, the "TIDAK TERJUAL" stamp on the loose diamonds and the 70 -> 38 carat cut made by skema27.py
    SHOTS = [
        (0, "konon", "img/316611.jpg", 0, "f", True, {"zoom": 0.06, "top": 0.25}),  # the whole stone under the title
        ("konon", "ia", "clips/107255.mp4", 1.0, "v", True, {"pos": 0.86}),  # the candle and the compass
        ("ia", "belanda", "img/3713564.jpg", 0, "f", False, {"zoom": 0.08, "tag": "pasar terapung Lok Baintan, hari ini"}),
        ("belanda", "berlian#2", "clips/21413.mp4", 2.0, "v", False, {"grade": "dim"}),
        ("berlian#2", "di", "clips/skema_peta.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("di", "akhirnya", "clips/skema_asah.mp4", 0, "v", True, {"zoom": 0}),
        ("akhirnya", "lebih", "img/1269462.jpg", 0, "f", False, {"zoom": 0.08}),
        ("lebih", "tahun", "img/4825124.jpg", 0, "f", True, {"zoom": 0.06}),
        ("tahun", "indonesia", "clips/24671.mp4", 2.0, "v", False, {}),
        ("indonesia", "tapi", "clips/24671.mp4", 4.37, "v", False, {"zoom": "punch"}),
        ("tapi", "kirim", "clips/skema_karat.mp4", 0, "v", False, {"tag": "skema", "zoom": 0}),
        ("kirim", "end", "img/3569545.jpg", 0, "f", False, {"zoom": "pull"}),
    ]
    TITLES = [
        (0, "tak", "BERLIAN\\NSULTAN BANJAR\\NINI..."),
        ("tak", "konon", f"BERLIAN\\NSULTAN BANJAR\\N{R}TAK PERNAH LAKU"),
        ("konon", "terkutuk", "KONON..."),
        ("terkutuk", "ia", f"KONON...\\N{R}TERKUTUK"),
        ("ia", "belanda", "PUSAKA\\NKESULTANAN BANJAR\\N{\\fs50}milik Sultan Adam, lambang kedaulatan"),
        ("belanda", "berlian#2", "1859: BELANDA\\NMEREBUT\\NBANJARMASIN"),
        ("berlian#2", "di", f"JADI {R}RAMPASAN\\NPERANG{Y}\\N{{\\fs50}}kesultanan Banjar dihapus"),
        ("di", "tetap", "1870: DIASAH\\NDI BELANDA"),
        ("tetap", "akhirnya", f"TETAP\\N{R}TAK LAKU"),
        ("akhirnya", "tahun", "RIJKSMUSEUM,\\NAMSTERDAM\\N{\\fs50}dipajang sejak 1902 (124 tahun)"),
        ("tahun", "tapi", "9 OKTOBER 2026\\NRESMI DISERAHKAN\\NKEMBALI!\\N{\\fs50}bersama 19 benda budaya lain,\\Nfisiknya tiba awal 2027"),
        ("tapi", "dan", "PERGI\\N±70 KARAT..."),
        ("dan", "kirim", f"PULANG\\N{R}38 KARAT{Y}\\N{{\\fs50}}hampir separuh hilang saat diasah"),
        ("kirim", "end", "KIRIM KE TEMANMU\\NYANG URANG\\NBANJAR!\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {}
elif EP == "28":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 32,21 s: the plain pauses trimmed, then a small speed-up
    AUDIO = "vo28.mp3"
    # the dramatic pauses ("perunggu...", "Padahal...", "Sakara...", "raja...", "medis...") are kept whole
    TIGHT = {"perunggu": 1.0, "medis": 0.3, "padahal": 1.0, "dokter": 0.3, "weni": 0.36, "sakara": 1.0, "lebih": 0.3,
             "banyak": 0.3, "raja": 1.0, "dokter#2": 0.3, "mengingatkan": 0.24, "pejabat#2": 0.3, "medis#2": 1.0, "hipokrates": 0.3}
    G, R, Y, WT = "{\\c&H5AFF8C&}", "{\\c&H5A5AFF&}", "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    # clips/skema_*.mp4 are the stethoscope crossed out, the tools as grave goods, the tools lighting up and the time line
    # to Hippocrates made by skema28.py
    RELIEF = "ilustrasi: relief pejabat lain di Saqqara"
    SHOTS = [
        (0, "diduga", "img/3326900.jpg", 0, "f", False, {"zoom": 0.06, "top": 0.4, "pos": 0.3, "tag": RELIEF}),
        ("diduga", "padahal", "img/3326900.jpg", 0, "f", False, {"zoom": "punch", "top": 0.4, "pos": 0.3, "tag": RELIEF}),
        ("padahal", "namanya", "clips/skema_coret.mp4", 0, "v", True, {"zoom": 0.04}),
        ("namanya", "usianya", "img/3326950.jpg", 0, "f", False, {"zoom": 0.06, "top": 0.2, "pos": 0.45, "tag": "Saqqara, hari ini"}),
        ("usianya", "gelarnya", "img/7259923.jpg", 0, "f", True, {"zoom": 0.08, "pos": 0.6}),
        ("gelarnya", "ahli", "img/597658.jpg", 0, "f", True, {"grade": "dim", "zoom": 0.05}),
        ("ahli", "tapi", "clips/skema_bekal.mp4", 0, "v", False, {"tag": "ilustrasi + skema", "zoom": 0.03}),
        ("tapi", "seribu", "clips/skema_alat.mp4", 0, "v", False, {"tag": "skema", "zoom": 0.06}),
        ("seribu", "kirim", "clips/skema_waktu.mp4", 0, "v", False, {"tag": "ilustrasi + skema", "zoom": 0.03}),
        ("kirim", "end", "clips/6015.mp4", 1.0, "v", True, {"pos": 0.62}),
    ]
    # "tak ada DOKTER" is struck through with a red bar wiped in from the left (a vector drawing; its box is DOKTER at \fs80)
    STRIKE = ("{\\an7\\pos(%d,%d)\\bord3\\shad0\\3c&H000000&\\c&H3030E8&\\clip(%d,0,%d,1920)\\t(0,180,\\clip(%d,0,%d,1920))\\p1}"
              "m 0 0 l %d 0 %d %d 0 %d{\\p0}")
    SX0, SX1, SY, SH = 384, 698, 752, 15  # DOKTER's letters span x 406-675, y 736-783 (measured on a test frame)
    TITLES = [
        (0, "diduga", "PEJABAT FIRAUN\\NINI..."),
        ("diduga", "padahal", f"{WT}DIKUBUR BERSAMA{Y}\\NALAT MEDIS?"),
        ("padahal", "dokter", "PADAHAL...\\NTAK PERNAH\\NDISEBUT"),
        ("dokter", "namanya", f"PADAHAL...\\NTAK PERNAH\\NDISEBUT {R}DOKTER"),
        ("namanya", "makamnya", "WENI"),
        ("makamnya", "usianya", "WENI\\N{\\fs76}SAQQARA, MESIR\\N{\\fs50}makam diumumkan 26 Okt 2026"),
        ("usianya", "gelarnya", "LEBIH DARI\\N4.000 TAHUN\\N{\\fs50}zaman Kerajaan Lama,\\Ndekat piramida Raja Merenre"),
        ("gelarnya", "ahli", "GELARNYA:"),
        ("wali", "ahli", "{\\fs80}WALI KOTA ✓", {"pos": (8, 540, 420)}),
        ("bendahara", "ahli", "{\\fs80}BENDAHARA RAJA ✓", {"pos": (8, 540, 520)}),
        ("raja+0.45", "ahli", "{\\fs80}PEMIMPIN EKSPEDISI ✓", {"pos": (8, 540, 620)}),
        ("tak#2", "ahli", f"{{\\fs80}}{R}DOKTER", {"pos": (8, 540, 720)}),
        ("dokter#2", "ahli", STRIKE % (SX0, SY, SX0, SX0, SX0, SX1, SX1 - SX0, SX1 - SX0, SH, SH), {"raw": True}),
        ("ahli", "sering", "AHLI\\NMENGINGATKAN..."),
        ("sering", "tapi", "SERING JADI\\NBEKAL KUBUR\\N{\\fs50}fungsi alat Weni masih diteliti,\\Nlogamnya akan diuji"),
        ("tapi", "seribu", "KALAU TERBUKTI\\NALAT MEDIS..."),
        ("seribu", "sebelum", "±1.800 TAHUN..."),
        ("sebelum", "kirim", "±1.800 TAHUN\\NSEBELUM\\NHIPPOCRATES!"),
        ("kirim", "end", "KIRIM KE\\NTEMANMU YANG\\NKULIAH\\NKEDOKTERAN!\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {"Sakara...": "Saqqara...", "Hipokrates!": "Hippocrates!"}
elif EP == "29":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 33,84 s: prep29.py cuts "Kok bisa?" (32,81 s), then the plain pauses trimmed and a speed-up
    AUDIO = "vo29cut.wav"
    # the dramatic pauses ("Banjar...", "ini, belum", "ditangkap...", "Belanda...", "Gana...") are kept whole
    TIGHT = {"banjar": 1.0, "ini": 1.0, "belum": 0.39, "antasari": 0.3, "ditangkap": 1.0, "martapura": 0.32, "belanda#2": 1.0,
             "laiden": 0.32, "pulang": 0.28, "gana": 1.0, "juga": 0.3}
    G, R, Y = "{\\c&H5AFF8C&}", "{\\c&H5A5AFF&}", "{\\c&H00E1FF&}"
    SHOTS = [
        (0, "tapi", "img/316611.jpg", 0, "f", True, {"zoom": 0.06, "top": 0.44}),  # the same stone as #27, below the 5-line title
        ("tapi", "namanya", "img/7555673.jpg", 0, "f", True, {"zoom": 0.04, "top": 0.45, "pos": 0.04, "tag": "ilustrasi: bukan tengkorak Demang Lehman"}),
        ("namanya", "seperjuangan", "img/5907266.jpg", 0, "f", False, {"zoom": 0.06, "pos": 0.2, "tag": "Kalimantan Selatan, hari ini"}),
        ("seperjuangan", "ia", "img/5907266.jpg", 0, "f", False, {"zoom": "punch", "pos": 0.2, "tag": "Kalimantan Selatan, hari ini"}),
        ("ia", "kepalanya", "clips/230528.mp4", 1.0, "v", False, {"grade": "cold"}),
        ("kepalanya", "tercatat", "img/6389684.jpg", 0, "f", False, {"zoom": 0.06, "pos": 0.62, "tag": "Leiden, hari ini"}),
        ("tercatat", "awal", "img/1867707.jpg", 0, "f", True, {"zoom": 0.06, "pos": 0.5}),
        ("awal", "padahal", "clips/24671.mp4", 2.0, "v", False, {}),
        ("padahal", "dari", "clips/21398.mp4", 2.0, "v", False, {}),
        ("dari", "kirim", "img/114290.jpg", 0, "f", False, {"zoom": "punch", "pos": 0.5, "tag": "Leiden, hari ini"}),
        ("kirim", "end", "img/7573238.jpg", 0, "f", False, {"zoom": "pull", "pos": 0.45, "tag": "Banjarmasin, hari ini"}),
    ]
    TITLES = [
        (0, "tapi", "BELANDA RESMI\\NMENGEMBALIKAN\\NBERLIAN SULTAN\\NBANJAR...\\N{\\fs50}9 Okt 2026 (lihat #27)"),
        ("tapi", "belum", "TAPI KEPALA\\NPANGLIMA INI..."),
        ("belum", "namanya", f"TAPI KEPALA\\NPANGLIMA INI...\\N{R}BELUM"),
        ("namanya", "seperjuangan", "DEMANG LEHMAN\\N{\\fs50}panglima Perang Banjar,\\Nlahir ±1832 di Barabai"),
        ("seperjuangan", "ia", "DEMANG LEHMAN\\N{\\fs50}seperjuangan\\NPangeran Antasari"),
        ("ia", "digantung", "DITANGKAP\\NLEWAT TIPU DAYA..."),
        ("digantung", "kepalanya", "27 FEBRUARI 1864\\N{\\fs50}dihukum gantung Belanda\\Ndi Martapura"),
        ("kepalanya", "tercatat", "DIBAWA\\NKE BELANDA\\N{\\fs50}tercatat tiba tahun 1867"),
        ("tercatat", "awal", "KOLEKSI MUSEUM\\NANATOMI LEIDEN\\N{\\fs50}label katalog: \"Demang Lèman,\\NBorneo (Martapoera)\""),
        ("awal", "padahal", "5 OKTOBER 2026:\\NKALSEL MINTA\\NKEPALANYA PULANG\\N{\\fs50}Belanda minta surat resmi,\\NPemprov sedang menyiapkannya"),
        ("padahal", "dari", "2009: KEPALA\\NRAJA GHANA\\NDIPULANGKAN\\N{\\fs50}Raja Badu Bonsu II,\\Ndieksekusi Belanda tahun 1838"),
        ("dari", "kirim", "DARI\\NLEIDEN JUGA!\\N{\\fs50}disimpan di koleksi anatomi\\NLUMC, Leiden"),
        ("kirim", "end", "KIRIM KE TEMANMU,\\NSUPAYA BELIAU\\NTIDAK DILUPAKAN!\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {"Léhman,": "Lehman,", "Laiden.": "Leiden.", "Laiden": "Leiden", "Gana...": "Ghana..."}
elif EP == "30":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 29,81 s: no tightening, a 1,4 % speed-up
    AUDIO = "vo30.mp3"
    G, R, Y, WT = "{\\c&H5AFF8C&}", "{\\c&H5A5AFF&}", "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    O = "{\\c&H1E8CFF&}"  # the orange of the ANAK segment in skema_persen
    XIAN = "Xi'an, China"
    # clips/skema_*.mp4 are the fingerprint glowing on a warrior's cheek, the ridge widths compared and the share bar over the
    # potter photos, made by skema30.py; the hook is 2669203 (faces sit clear of the captions), 4366989 is the cheek close-up
    SHOTS = [
        (0, "sidik", "img/2669203.jpg", 0, "f", False, {"zoom": 0.07, "pos": 0.42, "grade": "warm", "tag": XIAN}),
        ("sidik", "ini#2", "clips/skema_sidik.mp4", 0, "v", False, {"zoom": "punch", "grade": "warm", "tag": XIAN + " · sidik jari: ilustrasi"}),
        ("ini#2", "penjaga", "img/6362566.jpg", 0, "f", False, {"zoom": 0.06, "grade": "warm", "tag": XIAN}),
        ("penjaga", "peneliti", "img/4855072.jpg", 0, "b", False, {"zoom": 0.06, "grade": "warm", "tag": XIAN}),
        ("peneliti", "tertinggal", "img/1837073.jpg", 0, "f", True, {"zoom": 0.06}),
        ("tertinggal", "lebar", "img/1837073.jpg", 0, "f", True, {"zoom": "punch"}),
        ("lebar", "hasilnya", "clips/skema_alur.mp4", 0, "v", False, {"zoom": 0.03, "tag": "skema"}),
        ("hasilnya", "dan#2", "clips/skema_persen1.mp4", 0, "v", False, {"zoom": 0.04, "tag": "ilustrasi + skema"}),
        ("dan#2", "tag", "clips/skema_persen2.mp4", 0, "v", False, {"zoom": 0.04, "tag": "ilustrasi + skema"}),
        ("tag", "end", "clips/45455.mp4", 0.5, "v", True, {"grade": "warm"}),
    ]
    TITLES = [
        (0, "tapi", "DIKIRA BUATAN\\NPRIA..."),
        ("tapi", "ini#2", f"{WT}...TAPI {Y}SIDIK\\NJARINYA{WT}\\NBERKATA LAIN"),
        ("ini#2", "penjaga", "PASUKAN TERAKOTA\\N{\\fs50}±8.000 prajurit tanah liat\\Ndekat Xi'an, China"),
        ("penjaga", "peneliti", "PENJAGA MAKAM\\NKAISAR PERTAMA\\NCHINA\\N{\\fs50}Qin Shi Huang, ±2.200 tahun lalu"),
        ("peneliti", "lebar", "79 SIDIK JARI\\N{\\fs50}dari patung di Lubang 1\\NJournal of Cultural Heritage, 2026"),
        ("lebar", "hasilnya", "LEBAR ALUR =\\NPETUNJUK USIA &\\NJENIS KELAMIN"),
        ("hasilnya", "sepertiga", "HASILNYA..."),
        ("sepertiga", "dan#2", "SEPERTIGA\\NDIDUGA PEREMPUAN\\N{\\fs50}±32,7% sidik jari, perkiraan model"),
        ("dan#2", "anak", "LEBIH DARI\\NSEPERLIMA..."),
        ("anak", "tag", f"{O}ANAK{Y} DI BAWAH\\N15 TAHUN!\\N{{\\fs50}}±22,3% · bagian sidik jari,\\Nbukan jumlah pekerja"),
        ("tag", "end", "TAG TEMANMU\\NYANG HOBI MAIN\\NTANAH LIAT!\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {"Cina.": "China."}
elif EP == "31":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 30,51 s: no tightening, a 3,8 % speed-up
    AUDIO = "vo31.mp3"
    G, R, Y, WT = "{\\c&H5AFF8C&}", "{\\c&H5A5AFF&}", "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    BUKAN, BDG = "ilustrasi: bukan Earhart", "Bandung, hari ini"
    # clips/skema_*.mp4 are the Bandung-Surabaya-Bandung flight map, the airliner fading from the sky and the letter on hotel paper,
    # made by skema31.py
    SHOTS = [
        (0, "pilot", "img/808398.jpg", 0, "f", False, {"zoom": 0.07, "top": 0.15, "grade": "aged", "tag": BUKAN}),
        ("pilot", "masih", "img/808398.jpg", 0, "f", False, {"zoom": "punch", "top": 0.15, "grade": "aged", "tag": BUKAN}),
        ("masih", "namanya", "img/1595296.jpg", 0, "b", False, {"zoom": "punch", "tag": BDG}),
        ("namanya", "sedang", "img/808401.jpg", 0, "f", False, {"zoom": 0.06, "grade": "aged", "tag": BUKAN}),
        ("sedang", "di#2", "img/808401.jpg", 0, "f", False, {"zoom": "punch", "grade": "aged", "tag": BUKAN}),
        ("di#2", "sempat", "img/7399896.jpg", 0, "f", True, {"zoom": 0.07, "pos": 0.45, "grade": "aged"}),
        ("sempat", "lalu", "clips/skema_rute.mp4", 0, "v", False, {"zoom": 0.03, "tag": "skema"}),
        ("lalu", "bulan", "clips/skema_lenyap.mp4", 0, "v", False, {"zoom": 0.06, "grade": "night", "tag": "ilustrasi: bukan pesawat Earhart"}),
        ("bulan", "ternyata", "img/7882119.jpg", 0, "f", False, {"zoom": 0.06, "pos": 0.4, "grade": "muted", "tag": "ilustrasi: bukan Nikumaroro"}),
        ("ternyata", "dan", "img/482653.jpg", 0, "f", True, {"zoom": "punch", "pos": 0.3, "grade": "muted"}),
        ("dan", "kirim", "clips/skema_surat.mp4", 0, "v", False, {"zoom": 0.04, "tag": "ilustrasi"}),
        ("kirim", "end", "img/6839388.jpg", 0, "f", False, {"zoom": 0.06, "pos": 0.4, "grade": "warm", "tag": BDG}),
    ]
    TITLES = [
        (0, "pilot", "5 HARI SEBELUM\\NLENYAP..."),
        ("pilot", "masih", "PILOT PEREMPUAN\\NPALING TERKENAL\\NSEDUNIA"),
        ("masih", "bandung", f"{WT}...MASIH DI"),
        ("bandung", "namanya", f"{WT}...MASIH DI\\N{Y}BANDUNG"),
        ("namanya", "sedang", "AMELIA EARHART"),
        ("sedang", "di#2", "AMELIA EARHART\\N{\\fs50}1937: terbang keliling dunia\\Nbersama navigator Fred Noonan"),
        ("di#2", "sempat", "DIPERBAIKI DI ANDIR\\N{\\fs50}lapangan terbang Bandung,\\Noleh mekanik KNILM"),
        ("sempat", "lalu", "BOLAK-BALIK\\NSURABAYA\\N{\\fs50}24–25 Juni 1937: alat terbang\\Njarak jauhnya bermasalah lagi"),
        ("lalu", "bulan", "2 JULI 1937:\\NLENYAP DI ATAS\\NPASIFIK\\N{\\fs50}pesawatnya tak pernah ditemukan"),
        ("bulan", "ternyata", "OKT 2026 ·\\NNIKUMARORO\\N{\\fs50}ekspedisi ke \"Taraia Object\",\\Ndiduga pesawatnya sejak 2020"),
        ("ternyata", "dan", "TERNYATA CUMA\\NTUMPUKAN POHON\\N{\\fs50}Purdue & ALI, 19 Okt 2026:\\N\"kemungkinan besar\""),
        ("dan", "ditulis", "SURAT FRED NOONAN\\N{\\fs50}navigator Earhart, 23 Juni 1937"),
        ("ditulis", "kirim", f"{WT}DITULIS DI {Y}GRAND\\NHOTEL PREANGER\\N{{\\fs50}}{WT}Bandung; hotelnya masih berdiri\\Ndi Jl. Asia Afrika"),
        ("kirim", "end", "KIRIM KE TEMANMU\\NORANG BANDUNG!\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {"Erhart,": "Earhart,"}
elif EP == "32":
    STYLE, LUFS, PAD, TEMPO = 2, -15, 1.161, 1.0  # the v4 take is 28,84 s: natural speed, the CTA card held 1,2 s to land on 30,0 s
    AUDIO = "vo32.mp3"
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    PETI, MAINAN = "ilustrasi: bukan peti aslinya", "ilustrasi: bukan mainan aslinya"
    AYAM2 = 1.067  # where the "Ayam jago itu" shot starts inside skema_ayam (read off `plan`)
    # made by skema32.py: img/5798229v.jpg frames the hook photo with the lid seam above the captions, skema_buka lights the seam
    # on "dibuka", skema_ayam shakes the clay rooster on "kerincingan" and opens a window on its pellets on "butirannya";
    # clips/*s.mp4 are the two toy photos as clips for the split screen
    SHOTS = [
        (0, "dan", "img/5798229v.jpg", 0, "f", False, {"zoom": 0.07, "grade": "dusk", "tag": PETI}),
        ("dan", "ditemukan", "clips/skema_buka.mp4", 0, "v", False, {"zoom": "punch", "grade": "dusk", "tag": PETI}),
        ("ditemukan", "di#3", "img/4150405.jpg", 0, "f", False, {"zoom": 0.06, "tag": "Museum MINAC, Constanța"}),
        ("di#3", "karangan", "img/3610252.jpg", 0, "f", False, {"zoom": 0.07, "top": 0.12, "grade": "cold", "tag": PETI}),
        ("karangan", "bahkan", "img/2354950.jpg", 0, "f", True, {"zoom": 0.06, "grade": "aged"}),
        ("bahkan", "ia", "img/2354950.jpg", 0, "f", True, {"zoom": "punch", "grade": "aged"}),
        ("ia", "kuda", "clips/6252750s.mp4|clips/2505841s.mp4", "0|0", "s", False, {"pos": "0.39|0.95", "grade": "warm", "tag": MAINAN}),
        ("kuda", "ayam", "img/6252750.jpg", 0, "f", False, {"zoom": 0.06, "pos": 0.39, "grade": "warm", "tag": MAINAN}),
        ("ayam", "ayam#2", "clips/skema_ayam.mp4", 0, "v", False, {"zoom": 0.04, "grade": "warm", "tag": MAINAN}),
        ("ayam#2", "kirim", "clips/skema_ayam.mp4", AYAM2, "v", False, {"zoom": "punch", "grade": "warm", "tag": "ilustrasi + skema"}),
        ("kirim", "end", "img/1799224.jpg", 0, "f", True, {"zoom": 0.06, "pos": 0.05}),
    ]
    TITLES = [
        (0, "dan", "TERSEGEL\\N1.800 TAHUN..."),
        ("dan", "dibuka", f"{WT}...DAN BARU SAJA"),
        ("dibuka", "ditemukan", f"{WT}...DAN BARU SAJA\\N{Y}DIBUKA!\\N{{\\fs50}}{WT}27 Oktober 2026"),
        ("ditemukan", "di#3", "PEMAKAMAN\\NKUNO TOMIS\\N{\\fs50}kini Constanța, Rumania;\\Nmakamnya belum pernah dibongkar"),
        ("di#3", "seorang", "DI DALAMNYA..."),
        ("seorang", "karangan", "SEORANG BOCAH\\N{\\fs50}usianya masih diteliti"),
        ("karangan", "bahkan", "KARANGAN\\NBUNGANYA\\NMASIH ADA..."),
        ("bahkan", "ia", f"{WT}...BAHKAN\\N{Y}RAMBUTNYA\\N{{\\fs50}}{WT}peti kayunya pun hampir utuh"),
        ("ia", "kuda", "DIBEKALI 2 MAINAN\\NTANAH LIAT\\N{\\fs50}catnya pun masih terlihat"),
        ("kuda", "ayam", "KUDA KECIL..."),
        ("ayam", "ayam#2", f"{WT}KUDA KECIL...\\N{Y}& AYAM JAGO"),
        ("ayam#2", "kerincingan", "AYAM JAGO ITU\\NTERNYATA..."),
        ("kerincingan", "butirannya", "KERINCINGAN!"),
        ("butirannya", "kirim", "BUTIRANNYA\\NMASIH ADA\\NDI DALAM!"),
        ("kirim", "end", "KIRIM KE TEMANMU\\NYANG MASIH SIMPAN\\NMAINAN MASA KECIL!\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {}
elif EP == "33":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 32,88 s: plain pauses tightened, then sped up to land on 30,0 s
    AUDIO = "vo33.mp3"
    # the hook, "parah", "utuh", "obat" and "dunia" keep their dramatic pauses
    TIGHT = {"ini": 1.0, "buktinya": 0.30, "parah": 1.0, "aneh": 0.40, "rupanya": 0.30, "utuh": 1.0, "obat": 1.0, "dunia": 1.0}
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    # made by skema33.py: img/3258364v.jpg frames the hook photo so the cut nuts sit under the title, img/3258364es.jpg adds a frost rim,
    # img/5536858v.jpg sets the man with toothache lower so the title clears his eyes; skema_gigi shows the dental X-ray and, on "lekukan",
    # a molar diagram whose round notch lights up; skema_ukuran frames dried areca nuts higher in the frame and locks a dashed
    # "10-20 mm" circle on one; skema_globe pushes in on Sulawesi and drops a pulsing gold dot on it on "tertua"
    SHOTS = [
        (0, "zaman", "img/3258364v.jpg", 0, "f", False, {"zoom": 0.07, "grade": "pop"}),
        ("zaman", "buktinya", "img/3258364es.jpg", 0, "f", False, {"zoom": "punch", "grade": "cold"}),
        ("buktinya", "berumur", "img/780297.jpg", 0, "f", False, {"zoom": 0.06, "tag": "Bantimurung, Maros"}),
        ("berumur", "giginya", "img/1835825.jpg", 0, "f", False, {"zoom": "punch", "pos": 0.66, "grade": "cold", "tag": "ilustrasi: bukan gua aslinya"}),
        ("giginya", "rupanya", "clips/skema_gigi.mp4", 0, "v", False, {"zoom": 0.04, "tag": "ilustrasi + skema"}),
        ("rupanya", "zat", "clips/skema_ukuran.mp4", 0, "v", False, {"zoom": 0.04, "tag": "skema"}),
        ("zat", "diduga", "img/1817641.jpg", 0, "f", True, {"zoom": "punch", "pos": 0.6, "grade": "bright"}),
        ("diduga", "ini#2", "img/5536858v.jpg", 0, "f", True, {"zoom": 0.06, "grade": "warm"}),
        ("ini#2", "tumbuhan", "clips/skema_globe.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("tumbuhan", "tag", "img/241989.jpg", 0, "f", False, {"zoom": 0.07, "pos": 0.6, "grade": "pop"}),
        ("tag", "end", "img/4671646.jpg", 0, "f", False, {"zoom": 0.06, "grade": "warm"}),
    ]
    TITLES = [
        (0, "zaman", "PINANG INI..."),
        ("zaman", "buktinya", f"{WT}...SEJAK\\N{Y}ZAMAN ES?!"),
        ("buktinya", "berumur", "GIGI MANUSIA\\NPURBA SULAWESI\\N{\\fs50}gua Leang Bulu Bettue (Maros)\\N& Leang Cappalombo (Bone)"),
        ("berumur", "giginya", "HINGGA\\N25.000 TAHUN\\N{\\fs50}umurnya 16.000–25.000 tahun"),
        ("giginya", "dengan", "GIGINYA\\NRUSAK PARAH..."),
        ("dengan", "rupanya", "...ADA LEKUKAN\\NBULAT ANEH"),
        ("rupanya", "zat", "BEKAS MENGEMUT\\NPINANG UTUH\\N{\\fs50}bukan dikunyah, tapi diemut\\Nbertahun-tahun"),
        ("zat", "diduga", "ZAT PINANGNYA\\NMASIH ADA!\\N{\\fs50}arekolin terdeteksi\\Ndi jaringan gigi"),
        ("diduga", "ini#2", "OBAT\\NSAKIT GIGI?\\N{\\fs50}arekolin bisa meredakan nyeri\\N{\\fs40\\c&HFFFFFF&}*kini pinang diketahui memicu\\Nkanker mulut, jangan ditiru"),
        ("ini#2", "tertua", "INI BUKTI..."),
        ("tertua", "tumbuhan", f"{WT}BUKTI\\N{Y}TERTUA DI DUNIA!\\N{{\\fs50}}{WT}rekor lama: ribuan tahun,\\Nkini hingga 25.000 tahun"),
        ("tumbuhan", "tag", "TUMBUHAN\\NPENGARUH OTAK\\N{\\fs50}pinang kini no. 4 di dunia,\\Nsetelah alkohol, kafein & nikotin"),
        ("tag", "end", "TAG TEMANMU\\NYANG HOBI\\NMAKAN PINANG!\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {}
elif EP == "34":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 33,52 s: prep34.py cuts "Tengah malam," (32,22 s), then plain pauses tightened and a speed-up
    AUDIO = "vo34cut.wav"
    # the dramatic pauses ("Laba-laba ini...", "malam...", "berkedut...", "kita...", "dibuat...", "Besoknya?", "itu...") are kept whole
    TIGHT = {"ini": 1.0, "malam": 1.0, "berkedut": 1.0, "kita": 1.0, "dibuat": 1.0, "besoknya": 1.0, "itu#3": 1.0}
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    LABA = "ilustrasi: laba-laba pelompat"  # no Portia fimbriata on Pixabay: every spider is another jumping spider
    # made by skema34.py: img/2150062v.jpg sets the Bonn tower under the title (sky continued above); img/8069142v.jpg sets the
    # sleeping woman lower over a blurred copy so the title clears her face; img/2013929v.jpg frames the man with the phone;
    # skema_ir is the white jumping spider in a night-camera look (green mono, grain, REC, IR, a running clock) with leg twitches
    # on "berkedut"; skema_mata pushes in on the hook spider's eyes in the same look while their inner shine darts left and right;
    # skema_weker shakes the blurred alarm clock as if it rings
    SHOTS = [
        (0, "balas", "img/300437.jpg", 0, "f", False, {"zoom": 0.06, "grade": "pop", "tag": LABA}),
        ("balas", "peneliti", "img/300437.jpg", 0, "f", False, {"zoom": "punch", "grade": "night", "tag": LABA}),
        ("peneliti", "kamera", "img/2150062v.jpg", 0, "f", False, {"zoom": 0.06, "tag": "Universitas Bonn, Jerman"}),
        ("kamera", "matanya", "clips/skema_ir.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi + efek"}),
        ("matanya", "mirip", "clips/skema_mata.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi + efek"}),
        ("mirip", "tapi", "img/8069142v.jpg", 0, "f", True, {"zoom": 0.06, "grade": "night"}),
        ("tapi", "saat#2", "img/8411355.jpg", 0, "f", False, {"zoom": 0.07, "pos": 0.76, "grade": "dim", "tag": LABA}),
        ("saat#2", "lalu", "clips/skema_weker.mp4", 0, "v", True, {"zoom": 0.0}),
        ("lalu", "begadang", "img/6510044.jpg", 0, "f", False, {"zoom": 0.06}),
        ("begadang", "besoknya", "img/6510044.jpg", 0, "f", False, {"zoom": "punch"}),
        ("besoknya", "delapan", "img/3500156.jpg", 0, "f", False, {"zoom": 0.06, "grade": "warm", "tag": LABA}),
        ("delapan", "kirim", "img/3500156.jpg", 0, "f", False, {"zoom": "punch", "grade": "warm", "tag": LABA}),
        ("kirim", "end", "img/2013929v.jpg", 0, "f", False, {"zoom": 0.06}),
    ]
    TITLES = [
        (0, "balas", "LABA-LABA INI..."),
        ("balas", "peneliti", f"{WT}...BISA {Y}BALAS\\NDENDAM TIDUR?!"),
        ("peneliti", "kamera", "PENELITI\\NUNIVERSITAS BONN\\N{\\fs50}laba-laba pelompat\\N{\\i1}Portia fimbriata{\\i0} (Australia)"),
        ("kamera", "kakinya", "DIREKAM\\NTIAP MALAM\\N{\\fs50}pakai kamera inframerah,\\Nberhari-hari"),
        ("kakinya", "matanya", "KAKI\\NBERKEDUT..."),
        ("matanya", "mirip", f"{WT}...MATA\\N{Y}BERGERAK-GERAK!"),
        ("mirip", "tapi", "MIRIP KITA\\NSAAT BERMIMPI\\N{\\fs50}mirip fase REM, fase tidur\\Nyang penuh mimpi"),
        ("tapi", "saat#2", "TIDUR ATAU\\NCUMA DIAM?"),
        ("tapi>", "saat#2", "{\\fs260\\bord9\\t(0,250,\\fscx118\\fscy118)\\t(250,500,\\fscx100\\fscy100)\\t(500,750,\\fscx118\\fscy118)"
                            "\\t(750,1000,\\fscx100\\fscy100)\\t(1000,1250,\\fscx118\\fscy118)\\t(1250,1500,\\fscx100\\fscy100)}?",
         {"pos": (5, 950, 760)}),
        ("saat#2", "lalu", "PALING SUSAH\\NDIBANGUNKAN\\N{\\fs50}dites pakai suara:\\Nreaksinya paling lambat,\\Nada yang tak bereaksi sama sekali"),
        ("lalu", "besoknya", "DIBUAT BEGADANG\\NSEMALAMAN\\N{\\fs50}tidurnya diganggu lalat buah"),
        ("besoknya", "fase#2", f"{WT}BESOKNYA?\\N{Y}BALAS DENDAM\\NTIDUR!"),
        ("fase#2", "delapan", f"{WT}FASE MIRIP\\NMIMPI ITU..."),
    ]
    # on "delapan puluh persen" the number counts up under the title, then the last step pops
    STEP = 0.03
    TITLES += [(f"delapan+{k * STEP:.2f}", f"delapan+{(k + 1) * STEP:.2f}",
                f"{WT}FASE MIRIP\\NMIMPI ITU...\\N{Y}{{\\fs200}}+{5 * k}%", {"raw": True}) for k in range(16)]
    TITLES += [(f"delapan+{16 * STEP:.2f}", "kirim",
                f"{WT}FASE MIRIP\\NMIMPI ITU...\\N{Y}{{\\fs200\\t(0,110,\\fscx116\\fscy116)\\t(110,220,\\fscx100\\fscy100)}}+80%"
                f"\\N{{\\fs50}}{WT}lebih lama dari malam biasa", {"raw": True}),
               ("kirim", "end", "KIRIM KE TEMANMU\\NYANG HOBI\\NBEGADANG!\\N{\\fs58\\c&HFFFFFF&}@titikheran")]
    FIX = {"kakinya": "Kakinya"}  # after the cut it opens the sentence (shows in the .srt; the burned-in captions are upper case)
elif EP == "35":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 33,60 s: prep35.py cuts "Lalu," (32,76 s), then plain pauses tightened and a speed-up
    AUDIO = "vo35cut.wav"
    # the dramatic pauses ("yakin...", "Maluku...", "mendarat...", "dijuluki...", "Ternyata...", "ilmiahnya...") are kept whole
    TIGHT = {"yakin": 1.0, "maluku": 1.0, "mendarat": 1.0, "dijuluki": 1.0, "ternyata": 1.0, "ilmiahnya": 1.0}
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    HOOK1, KAKI1 = 3.067, 1.333  # where shots 1 and 10 start inside skema_hook and skema_kaki (read off `plan`)
    # made by skema35.py: img/6527482v.jpg frames the hook bird (a lesser bird-of-paradise) under the title; skema_hook rings the
    # spot where its feet should be and pops a "?" on "tak"; img/6527482k.jpg is the bird cut out as a sepia trade skin with no feet,
    # lying tilted in a dark box; skema_terbang floats that skin up through the sunbeams; skema_bulu runs a soft gold light down the
    # plumes; img/6527482z.jpg is close on the stump; skema_kaki rings both feet of 1540371 and draws dashed cut lines above them on
    # "dipotong"; skema_nama is a museum label card for Paradisaea apoda whose parts light up with their meanings on "Artinya";
    # img/6527482c.jpg frames the whole bird lower for the CTA
    SHOTS = [
        (0, "tak", "clips/skema_hook.mp4", 0, "v", False, {"zoom": 0.06, "grade": "pop"}),
        ("tak", "lima", "clips/skema_hook.mp4", HOOK1, "v", False, {"zoom": "punch", "grade": "pop"}),
        ("lima", "dibawa", "img/5779375.jpg", 0, "b", False, {"zoom": 0.06, "tag": "Maluku Utara"}),
        ("dibawa", "tanpa", "img/1572636.jpg", 0, "f", False, {"zoom": 0.07, "grade": "aged", "tag": "ilustrasi: kapal replika"}),
        ("tanpa", "dikira", "img/6527482k.jpg", 0, "f", False, {"zoom": 0.05, "tag": "ilustrasi + efek"}),
        ("dikira", "hanya", "clips/skema_terbang.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi + efek"}),
        ("hanya", "ia", "img/8687801.jpg", 0, "b", True, {"zoom": 0.08}),
        ("ia", "ke", "clips/skema_bulu.mp4", 0, "v", False, {"zoom": 0.05, "grade": "warm"}),
        ("ke", "ternyata", "img/6527482z.jpg", 0, "f", False, {"zoom": 0.08, "grade": "dim"}),
        ("ternyata", "dipotong", "clips/skema_kaki.mp4", 0, "v", False, {"zoom": 0.05, "grade": "pop"}),
        ("dipotong", "tapi", "clips/skema_kaki.mp4", KAKI1, "v", False, {"zoom": "punch", "grade": "pop"}),
        ("tapi", "paradisea", "img/850868.jpg", 0, "b", False, {"zoom": 0.06, "tag": "patung Linnaeus, Chicago"}),
        ("paradisea", "tanpa#2", "clips/skema_nama.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("tanpa#2", "pernah#2", "img/1540371.jpg", 0, "b", False, {"zoom": "punch", "grade": "pop"}),
        ("pernah#2", "end", "img/6527482c.jpg", 0, "f", False, {"zoom": "pull", "grade": "warm"}),
    ]
    TITLES = [
        (0, "cenderawasih", "DULU, EROPA\\NYAKIN..."),
        ("cenderawasih", "lima", f"{WT}...CENDERAWASIH\\N{Y}TAK PUNYA KAKI?!"),
        ("lima", "tanpa", "SEJAK 1522:\\NDIBAWA DARI MALUKU\\N{\\fs50}pertama lewat kapal ekspedisi Magellan,\\Nhadiah Raja Bacan untuk Raja Spanyol"),
        ("tanpa", "dikira", "...TANPA KAKI\\N{\\fs50}begitu kulit dagangannya tiba di Eropa"),
        ("dikira", "ia", "DIKIRA TAK PERNAH\\NMENDARAT\\N{\\fs50}terbang seumur hidup,\\Nhidup dari embun"),
        ("ia", "burung", "DIJULUKI..."),
        ("burung", "ke", "\"BURUNG SURGA\"\\N{\\fs50}bird of paradise\\N(di Maluku: \"burung dewata\")"),
        ("ke", "ternyata", "KE MANA\\NKAKINYA?"),
        ("ke>", "ternyata", "{\\fs260\\bord9\\t(0,250,\\fscx118\\fscy118)\\t(250,500,\\fscx100\\fscy100)\\t(500,750,\\fscx118\\fscy118)"
                            "\\t(750,1000,\\fscx100\\fscy100)}?", {"pos": (5, 330, 1010)}),
        ("ternyata", "dipotong", "TERNYATA\\NKAKINYA ADA!"),
        ("dipotong", "tapi", "DIPOTONG\\NSEBELUM DIJUAL!\\N{\\fs50}kulit dagangan: kaki (dan sering\\Nsayapnya) dibuang"),
        ("tapi", "tanpa#2", "NAMA ILMIAHNYA\\NSAMPAI SEKARANG:"),
        ("tanpa#2", "pernah#2", f"{WT}BURUNG SURGA\\N{Y}TANPA KAKI!\\N{{\\fs50}}{WT}padahal kakinya ada"),
        ("pernah#2", "end", "PERNAH LIHAT\\NCENDERAWASIH\\NLANGSUNG?\\N{\\fs50}jawab di komentar\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {"Paradisea": "Paradisaea"}  # spelled for the TTS; the real name on screen
elif EP == "36":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.94, 30.0  # the v4 take is 30,40 s: plain pauses tightened to 29,06 s, natural speed, the CTA card held 0,94 s
    AUDIO = "vo36.mp3"
    # the dramatic pauses ("tahun...", "parfum...", "Pemiliknya...", "kain...", "siapa?", "Diduga...") are kept whole, and the
    # sentence breaks after "tersentuh!", "koin.", "membawanya." and "dewasa." keep a little more air than the plain ones
    TIGHT = {"tahun": 1.0, "parfum": 1.0, "pemiliknya": 1.0, "kain": 1.0, "siapa": 1.0, "diduga": 1.0,
             "tersentuh": 0.5, "koin": 0.55, "membawanya": 0.5, "dewasa": 0.55}
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    LEMARI1 = 3.333  # where shot 1 starts inside skema_lemari (read off `plan`)
    # made by skema36.py: skema_lemari frames the old cupboard door with its key (Pixabay 3886500, a stand-in) and lets a gold light
    # leak out of the door's seam on "isinya"; img/3832301v.jpg sets the glass bottle lower in its case, under the title;
    # skema_kalung is the reconstruction: one cloth pouch (from 1281266) in sepia, then 24 small amulets (hands, feet, pine cones,
    # grapes, Bes, Mercury; bone, glass, pottery, crystal) fly out of it one by one onto a cord; skema_tumbuh dissolves the Roman
    # child statue into the Pompeii fresco while the necklace glows below; img/2458500v.jpg sets the arch under the CTA title
    SHOTS = [
        (0, "isinya", "clips/skema_lemari.mp4", 0, "v", True, {"zoom": 0.06}),
        ("isinya", "arkeolog", "clips/skema_lemari.mp4", LEMARI1, "v", True, {"zoom": "punch"}),
        ("arkeolog", "pinset", "img/4053847.jpg", 0, "b", False, {"zoom": 0.06, "tag": "Pompeii, Italia"}),
        ("pinset", "tiga", "img/3832301v.jpg", 0, "f", True, {"zoom": 0.08, "grade": "dim"}),
        ("tiga", "pemiliknya", "img/4786028.jpg", 0, "f", True, {"zoom": "punch", "pos": 0.875, "grade": "warm"}),
        ("pemiliknya", "di", "img/922764.jpg", 0, "f", False, {"zoom": 0.07, "pos": 0.51, "grade": "dusk",
                                                                "tag": "ilustrasi: lukisan dinding Pompeii"}),
        ("di", "milik", "clips/skema_kalung.mp4", 0, "v", False, {"zoom": 0.0, "tag": "rekonstruksi"}),
        ("milik", "diduga", "img/1344300.jpg", 0, "f", False, {"zoom": 0.08, "pos": 0.276, "grade": "dim",
                                                               "tag": "ilustrasi: patung anak Romawi"}),
        ("diduga", "kamu", "clips/skema_tumbuh.mp4", 0, "v", False, {"zoom": 0.0, "grade": "warm", "tag": "ilustrasi + rekonstruksi"}),
        ("kamu", "end", "img/2458500v.jpg", 0, "f", False, {"zoom": 0.06, "grade": "dusk", "tag": "Pompeii, Italia"}),
    ]
    TITLES = [
        (0, "isinya", "LEMARI INI TERKUBUR\\N1.947 TAHUN..."),
        ("isinya", "arkeolog", f"{WT}...ISINYA\\N{Y}TAK TERSENTUH!"),
        ("arkeolog", "pinset", "POMPEII, ITALIA\\N{\\fs50}diumumkan 29 Oktober 2026,\\Nrumah di Via dell'Abbondanza"),
        ("pinset", "tiga", "PINSET", {"pos": (8, 540, 300)}),
        ("alat", "tiga", "ALAT RIAS", {"pos": (8, 540, 411)}),
        ("botol", "tiga", "BOTOL PARFUM", {"pos": (8, 540, 522)}),
    ]
    # on "tiga puluh delapan" the coins count up, then the last step pops
    STEP = 0.03
    TITLES += [(f"tiga+{k * STEP:.2f}", f"tiga+{(k + 1) * STEP:.2f}",
                f"{{\\fs200}}{2 * k}\\N{WT}KOIN PERUNGGU", {"raw": True}) for k in range(19)]
    TITLES += [(f"tiga+{19 * STEP:.2f}", "pemiliknya",
                f"{{\\fs200\\t(0,110,\\fscx116\\fscy116)\\t(110,220,\\fscx100\\fscy100)}}38\\N{WT}KOIN PERUNGGU"
                f"\\N{{\\fs50}}di keranjang anyaman kecil", {"raw": True}),
               ("pemiliknya", "di", "PEMILIKNYA\\NTAK SEMPAT\\NMEMBAWANYA"),
               ("di", "kalung", "DI KANTONG KAIN..."),
               ("kalung", "milik", "KALUNG 24\\NJIMAT ANAK\\N{\\fs50}\"crepundia\": tulang, kaca, gerabah, kristal\\Nsetidaknya 24 buah"),
               ("milik", "diduga", "MILIK SIAPA?"),
               ("milik>", "diduga", "{\\fs260\\bord9\\t(0,250,\\fscx118\\fscy118)\\t(250,500,\\fscx100\\fscy100)"
                                    "\\t(500,750,\\fscx118\\fscy118)\\t(750,1000,\\fscx100\\fscy100)}?", {"pos": (5, 880, 560)}),
               ("diduga", "kamu", "JIMAT MASA\\NKECILNYA SENDIRI\\N{\\fs50}disimpan sampai dewasa\\N(dugaan peneliti)"),
               ("kamu", "end", "KAMU MASIH SIMPAN\\NBARANG MASA KECIL\\NAPA?\\N{\\fs50}jawab di komentar\\N{\\fs58\\c&HFFFFFF&}@titikheran")]
    FIX = {"Pompei": "Pompeii"}  # spelled for the TTS ("pom-pe-i"); the real name on screen
elif EP == "37":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 32,16 s: plain pauses tightened to 31,28 s, then a 6,4 % speed-up
    AUDIO = "vo37.mp3"
    # the dramatic pauses ("dunia...", "tahun...", "rapi.", "anak-anak...") are kept whole; "sembuh." and "sebelumnya:" keep a beat
    TIGHT = {"dunia": 1.0, "tahun": 1.0, "rapi": 1.0, "anak-anak": 1.0, "sembuh": 0.45, "sebelumnya": 0.3}
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    ANAK1 = 2.367  # where shot 6 starts inside skema_anak (read off `plan`)
    # made by skema37.py: skema_peta draws Borneo (Natural Earth coastlines) over the dimmed Kapuas river photo (3400179, a stand-in,
    # West Kalimantan) and pops a pulsing dot at Liang Tebo in the Sangkulirang-Mangkalihat karst; skema_kerangka lays a line-art
    # skeleton on the mossy ledge of the cave photo 1835823 (a stand-in), revealed head to toe, its left lower leg (the distal third
    # of the tibia and fibula, and the foot) never drawn; on "tanpa" a red dashed ghost shows the missing part; skema_tulang zooms
    # in on the stump: the clean oblique cut glints on "rapi", a fang sign is struck out on "digigit", and the cut end rounds over
    # on "sembuh"; skema_anak is the reconstruction: a child's silhouette on one leg with a wooden stick, backlit on the same ledge,
    # a warm glow on "selamat"; skema_rekor compares the two records as bars (Kalimantan 31.000, France 7.000, +24.000);
    # skema_hidup grows the child into a teenager and fades in three adults by a fire glow on "dirawat"
    SHOTS = [
        (0, "ternyata", "img/650534.jpg", 0, "f", True, {"zoom": 0.07, "grade": "cold", "pos": 0.35}),
        ("ternyata", "di#3", "img/2289357.jpg", 0, "f", True, {"zoom": "punch", "grade": "pop"}),
        ("di#3", "kerangka", "clips/skema_peta.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi + skema"}),
        ("kerangka", "potongannya", "clips/skema_kerangka.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("potongannya", "ia#1", "clips/skema_tulang.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("ia#1", "dan", "clips/skema_anak.mp4", 0, "v", False, {"zoom": 0.04, "tag": "ilustrasi + rekonstruksi"}),
        ("dan", "rekor", "clips/skema_anak.mp4", ANAK1, "v", False, {"zoom": "punch", "grade": "warm", "tag": "ilustrasi + rekonstruksi"}),
        ("rekor", "ia#2", "clips/skema_rekor.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("ia#2", "menurutmu", "clips/skema_hidup.mp4", 0, "v", False, {"zoom": 0.04, "grade": "warm", "tag": "ilustrasi + rekonstruksi"}),
        ("menurutmu", "end", "img/601542.jpg", 0, "f", True, {"zoom": 0.06, "grade": "pop"}),
    ]
    TITLES = [
        (0, "ternyata", "{\\fs88}OPERASI AMPUTASI\\NTERTUA DI DUNIA..."),
        ("ternyata", "di#3", f"{WT}...TERNYATA DI\\N{Y}KALIMANTAN!"),
        ("di#3", "kerangka", "{\\fs84}LIANG TEBO,\\NKALIMANTAN TIMUR\\N{\\fs50}gua kapur, dicapai dengan perahu"),
        ("kerangka", "tiga", "KERANGKA\\NMANUSIA PURBA"),
    ]
    # on "tiga puluh satu ribu" the years count up, then the last step pops
    STEP = 0.03
    TITLES += [(f"tiga+{k * STEP:.2f}", f"tiga+{(k + 1) * STEP:.2f}",
                f"{{\\fs200}}{f'{k}.000' if k else '0'}\\N{WT}TAHUN", {"raw": True}) for k in range(31)]
    TITLES += [(f"tiga+{31 * STEP:.2f}", "tanpa",
                f"{{\\fs200\\t(0,110,\\fscx116\\fscy116)\\t(110,220,\\fscx100\\fscy100)}}31.000\\N{WT}TAHUN\\N{{\\fs50}}sedikitnya",
                {"raw": True}),
               ("tanpa", "potongannya", "TANPA KAKI\\NKIRI BAWAH!"),
               ("potongannya", "bukan", "POTONGANNYA\\NRAPI & MIRING"),
               ("bukan", "tulangnya", "BUKAN DIGIGIT\\NHEWAN!\\N{\\fs50}juga bukan kecelakaan\\N(kata peneliti)"),
               ("tulangnya", "ia#1", "TULANGNYA\\NSEMBUH"),
               ("ia#1", "dan", "DIAMPUTASI SAAT\\NANAK-ANAK...\\N{\\fs50}(kemungkinan besar, kata peneliti)"),
               ("dan", "rekor", f"{WT}...DAN\\N{Y}SELAMAT!"),
               ("rekor", "ia#2", "REKOR LAMA:\\NPRANCIS"),
               ("ia#2", "dirawat", "HIDUP 6–9\\NTAHUN LAGI"),
               ("dirawat", "menurutmu", "HIDUP 6–9\\NTAHUN LAGI\\N{\\fs50}dirawat kelompoknya\\N(dugaan peneliti)", {"raw": True}),
               ("menurutmu", "end", "MENURUTMU,\\NDIPOTONG\\NPAKAI APA?\\N{\\fs50}tulis di komentar\\N{\\fs58\\c&HFFFFFF&}@titikheran")]
    FIX = {}
elif EP == "38":
    STYLE, LUFS, PAD, TEMPO = 2, -15, 1.2, 1.0  # the v4 take is 28,11 s; prep38.py grows three pauses to 28,80 s; natural speed, the CTA card held 1,2 s
    AUDIO = "vo38pad.wav"
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    NASKAH = "ilustrasi: naskah kuno"
    # made by skema38.py: img/935258v.jpg sets the museum mummy face (935258, a stand-in for the Marburg head) into 9:16 at 1,55x,
    # so the whole face reads (a cover crop shows one eye socket); skema_scan sweeps a green scan line down that face and lights up
    # spots tagged aloin and aloeresin (a schematic: the compounds were found by chemical analysis of samples); skema_apotek
    # pans the black-and-white apothecary shelf (4496863, a stand-in) to its ALOE jar
    SHOTS = [
        (0, "ditemukan", "img/4529704.jpg", 0, "f", False, {"zoom": 0.08, "pos": 0.28, "grade": "pop"}),
        ("ditemukan", "berumur", "img/935258v.jpg", 0, "f", False, {"zoom": "punch", "grade": "dim",
                                                                   "tag": "ilustrasi: mumi Mesir di museum"}),
        ("berumur", "penulis", "img/2796707.jpg", 0, "f", True, {"zoom": 0.07, "grade": "dim"}),
        ("penulis", "tapi", "img/2757109.jpg", 0, "f", False, {"zoom": 0.07, "pos": 0.22, "grade": "warm", "tag": NASKAH}),
        ("tapi", "universitas", "img/1503029.jpg", 0, "f", False, {"zoom": "punch", "pos": 0.3, "grade": "aged", "tag": NASKAH}),
        ("universitas", "menguji", "img/239201.jpg", 0, "f", False, {"zoom": 0.07, "pos": 0.62, "tag": "Marburg, Jerman"}),
        ("menguji", "jejaknya", "img/220005.jpg", 0, "f", True, {"zoom": 0.06, "grade": "cold"}),
        ("jejaknya", "dan", "clips/skema_scan.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi + skema"}),
        ("dan", "ya", "clips/skema_apotek.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi: apotek tua"}),
        ("ya", "makan", "img/2055130.jpg", 0, "f", True, {"zoom": 0.06, "grade": "warm"}),
        ("makan", "kamu", "img/2055130.jpg", 0, "f", True, {"zoom": "punch", "grade": "warm"}),
        ("kamu", "end", "img/7605895.jpg", 0, "f", False, {"zoom": 0.06, "grade": "pop"}),
    ]
    TITLES = [
        (0, "ditemukan", "JEJAK\\NLIDAH BUAYA..."),
        ("ditemukan", "dua#1", f"{WT}...DI KEPALA\\N{Y}MUMI MESIR!"),
    ]
    # on "dua ribu tujuh ratus" the years count up, then the last step pops; the same for "dua puluh empat" objects
    STEP = 0.03
    TITLES += [(f"dua#1+{k * STEP:.2f}", f"dua#1+{(k + 1) * STEP:.2f}",
                f"{{\\fs200}}{k * 100:,}\\N{WT}TAHUN".replace(",", "."), {"raw": True}) for k in range(27)]
    TITLES += [(f"dua#1+{27 * STEP:.2f}", "penulis",
                f"{{\\fs200\\t(0,110,\\fscx116\\fscy116)\\t(110,220,\\fscx100\\fscy100)}}2.700\\N{WT}TAHUN"
                f"\\N{{\\fs50}}abad ke-8 SM (penanggalan radiokarbon)", {"raw": True}),
               ("penulis", "tapi", "PENULIS ABAD\\NPERTENGAHAN\\N{\\fs50}sudah menulis: mumi dibalsem\\Ndengan lidah buaya"),
               ("tapi", "universitas", "DIANGGAP\\NCUMA MENEBAK"),
               ("menebak", "universitas", "{\\fs260\\bord9\\t(0,250,\\fscx118\\fscy118)\\t(250,500,\\fscx100\\fscy100)"
                                          "\\t(500,750,\\fscx118\\fscy118)\\t(750,1000,\\fscx100\\fscy100)}?", {"pos": (5, 880, 700)}),
               ("universitas", "dua#2", "UNIVERSITAS\\NMARBURG, JERMAN")]
    TITLES += [(f"dua#2+{k * STEP:.2f}", f"dua#2+{(k + 1) * STEP:.2f}",
                f"{{\\fs200}}{k}\\N{WT}BENDA DIUJI", {"raw": True}) for k in range(24)]
    TITLES += [(f"dua#2+{24 * STEP:.2f}", "jejaknya",
                f"{{\\fs200\\t(0,110,\\fscx116\\fscy116)\\t(110,220,\\fscx100\\fscy100)}}24\\N{WT}BENDA DIUJI"
                f"\\N{{\\fs50}}perban, sisa balsem, bagian tubuh mumi,\\Nobat dari bubuk mumi", {"raw": True}),
               ("jejaknya", "dan", "JEJAK\\NDITEMUKAN!\\N{\\fs50}senyawa khas lidah buaya\\N(terkait aloin dan aloeresin)"),
               ("dan", "ya", "OBAT BUBUK MUMI,\\NABAD KE-18\\N{\\fs50}\"Mumia vera aegyptiaca\"\\Ndari apotek di Offenbach, Jerman"),
               ("ya", "makan", f"{WT}ORANG EROPA\\NDULU..."),
               ("makan", "kamu", f"{WT}...MAKAN\\N{Y}MUMI!\\N{{\\fs50}}dijual di apotek sebagai \"mumia\"\\N(abad ke-12 sampai ke-18)"),
               ("kamu", "end", "KAMU PAKAI\\NLIDAH BUAYA\\NBUAT APA?\\N{\\fs50}rambut? kulit? diminum?\\Ntulis di komentar"
                               "\\N{\\fs58\\c&HFFFFFF&}@titikheran")]
    FIX = {}
elif EP == "39":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 32,03 s: plain pauses tightened, then a small speed-up
    AUDIO = "vo39.mp3"
    # the dramatic pauses ("Flores...", "Bua...", "punah...") are kept whole
    TIGHT = {"flores": 1.0, "bua": 1.0, "punah": 1.0}
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    BANGKAI = "ilustrasi: komodo & bangkai"
    SHOTS = [
        (0, "ternyata", "img/10518742v.jpg", 0, "f", False, {"zoom": 0.08, "grade": "warm"}),  # reframed by skema39.py foto()
        ("ternyata", "namanya", "clips/167283.mp4", 0, "v", False, {"zoom": "punch", "pos": 0.55, "grade": "warm", "tag": BANGKAI}),
        ("namanya", "dulu", "clips/skema_ukur.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi: lanskap NTT + skema"}),
        ("dulu", "tapi#1", "clips/skema_dugaan.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi: gajah Asia; Stegodon sudah punah"}),
        ("tapi#1", "gigitan", "clips/skema_gua.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi: gua kapur + skema"}),
        ("gigitan", "bagian", "clips/167283.mp4", 4.0, "v", False, {"zoom": 0.05, "pos": 0.58, "grade": "warm", "tag": BANGKAI}),
        ("bagian", "hari", "clips/skema_stegodon.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema + rekonstruksi"}),
        ("hari", "tapi#2", "clips/skema_punah.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi + rekonstruksi"}),
        ("tapi#2", "kamu", "img/10518757v.jpg", 0, "f", False, {"zoom": "punch", "grade": "pop"}),
        ("kamu", "end", "clips/110536.mp4", 0, "v", False, {"zoom": 0.06, "pan": (0.5, 0.92), "grade": "pop"}),  # open jaws, then the eye
    ]
    TITLES = [
        (0, "ternyata", "{\\fs88}MANUSIA PURBA\\NDI FLORES..."),
        ("ternyata", "namanya", f"{WT}...MAKAN SISA\\NBURUAN {Y}KOMODO!\\N{{\\fs50}}{WT}menurut studi Science Advances 2026"),
        ("namanya", "satu", f"HOMO\\NFLORESIENSIS\\N{{\\fs50}}{WT}dijuluki \"manusia hobbit\",\\Nfosilnya hanya ditemukan di Flores"),
        ("satu", "dulu", f"{WT}TINGGINYA\\N{Y}±1 METER\\N{{\\fs50}}{WT}kerangka LB1: 1,06 meter"),
        ("dulu", "tapi#1", f"{WT}DULU DIKIRA:\\N{Y}PEMBURU\\NGAJAH PURBA\\N{{\\fs50}}{WT}Stegodon, kerabat gajah"),
    ]
    # on "Tapi tulang-tulang" the bone count runs up, then the last step pops
    STEP = 0.03
    TITLES += [(f"tapi#1+{k * STEP:.2f}", f"tapi#1+{(k + 1) * STEP:.2f}",
                f"{{\\fs200}}{k * 100:,}\\N{WT}PECAHAN TULANG".replace(",", "."), {"raw": True}) for k in range(32)]
    TITLES += [(f"tapi#1+{32 * STEP:.2f}", "bercerita",
                f"{{\\fs200\\t(0,110,\\fscx116\\fscy116)\\t(110,220,\\fscx100\\fscy100)}}3.155\\N{WT}PECAHAN TULANG"
                f"\\N{{\\fs50}}Stegodon dari gua Liang Bua,\\Ndiperiksa ulang", {"raw": True}),
               ("bercerita", "gigitan", f"{WT}...BERCERITA\\N{Y}LAIN\\N{{\\fs50}}{WT}Liang Bua, Flores"),
               ("gigitan", "goresan", f"{{\\fs80}}{WT}BEKAS GIGITAN KOMODO:\\N{Y}BAGIAN PALING\\NBERDAGING"
                                      f"\\N{{\\fs50}}{WT}komodo makan duluan (kata peneliti)"),
               ("goresan", "kebanyakan", f"{{\\fs80}}{WT}GORESAN ALAT\\NBATU {Y}HOBBIT?"),
               ("kebanyakan", "hari", f"{{\\fs80}}{WT}KEBANYAKAN DI\\N{Y}TULANG SISA\\N{{\\fs50}}{WT}rusuk, ruas jari, pecahan tengkorak"),
               ("hari", "tapi#2", f"{WT}HARI INI,\\NHOBBIT {Y}PUNAH...\\N{{\\fs50}}{WT}jejak terakhirnya ±50.000 tahun lalu"),
               ("tapi#2", "kamu", f"{WT}...TAPI KOMODONYA\\N{Y}MASIH ADA!\\N{{\\fs50}}{WT}hidup liar di Flores, Komodo, Rinca"),
               ("kamu", "end", "KAMU BERANI\\NREBUTAN MAKANAN\\NSAMA KOMODO?\\N{\\fs50}jawab di komentar"
                               "\\N{\\fs58\\c&HFFFFFF&}@titikheran")]
    FIX = {"hobit?": "hobbit?", "hobit": "hobbit"}  # the TTS input spells "hobit" so Akram reads it the Indonesian way
elif EP == "40":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 31,71 s: plain pauses tightened, then a small speed-up
    AUDIO = "vo40.mp3"
    # the dramatic pauses ("sejarah...", "hari ini...", "menjauh...", before and inside the greeting) are kept whole;
    # whispered words have quiet gaps between syllables ("Ar-ti-nya" lost its "ti" to a 0,18 s cut) and Scribe stretches
    # "sekalian..." and "berpisah," over their pauses, so they are protected by name
    TIGHT = {"artinya": 1.0, "sejarah": 1.0, "ini": 1.0, "menjauh": 1.0, "sekarat": 0.45, "indonesia": 1.0, "sekalian": 1.0,
             "berpisah": 1.0}
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    SHOTS = [
        (0, "benda", "clips/20042s.mp4", 0, "v", False, {"zoom": 0.05, "pos": 0.56, "grade": "cold", "tag": "ilustrasi 3D"}),
        ("benda", "artinya", "clips/skema_jarak.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi + skema"}),
        ("artinya", "balasannya", "clips/skema_kirim.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi: antena radio + skema"}),
        ("balasannya", "hampir", "clips/skema_balas.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi: antena radio + skema"}),
        ("hampir", "tapi", "clips/skema_daya.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi + skema"}),
        ("tapi", "selamat#1", "clips/skema_piringan.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("selamat#1", "kalau", "clips/skema_sapaan.mp4", 0, "v", False, {"zoom": 0.0, "tag": "ilustrasi + skema"}),
        ("kalau", "end", "img/4006343v.jpg", 0, "f", False, {"zoom": 0.06, "grade": "base"}),
    ]
    TITLES = [
        (0, "benda", f"{WT}VOYAGER 1\\NSEBENTAR LAGI\\N{Y}CETAK SEJARAH"),
        ("sebentar", "benda", "{\\3c&H00E1FF&\\c&H141414&}18 NOV 2026", {"style": "Label", "pos": (5, 540, 720)}),
        ("benda", "artinya", f"{{\\fs84}}{WT}BENDA BUATAN MANUSIA\\NPERTAMA SEJAUH\\N{Y}1 HARI CAHAYA"
                             f"\\N{{\\fs50}}{WT}±25,9 miliar km dari Bumi"),
        ("artinya", "balasannya", f"{WT}KIRIM {Y}\"HALO\"\\N{WT}HARI INI..."),
        ("balasannya", "hampir", f"{WT}...BALASANNYA\\NDATANG {Y}LUSA\\N{{\\fs50}}{WT}sinyal radio butuh 24 jam sekali jalan"),
        ("hampir", "kini", f"{WT}HAMPIR {Y}50 TAHUN\\N{WT}TERBANG\\N{{\\fs50}}diluncurkan 5 September 1977"),
        ("kini", "tapi", f"{WT}KINI DAYANYA\\N{Y}SEKARAT\\N{{\\fs50}}{WT}turun ±4 watt per tahun,\\Ntinggal 2 alat sains menyala"),
        ("tapi", "bahasa", f"{WT}PIRINGAN EMAS\\N{Y}(GOLDEN RECORD)\\N{{\\fs50}}{WT}sapaan dalam 55 bahasa"),
        ("bahasa", "selamat#1", f"{WT}SALAH SATUNYA\\N{Y}BAHASA INDONESIA!"),
        ("selamat#1", "selamat#2", f"{{\\i1}}{WT}\"SELAMAT MALAM\\NHADIRIN SEKALIAN...\""),
        ("selamat#2", "kalau", f"{{\\i1}}{WT}\"...SELAMAT BERPISAH,\\N{Y}DAN SAMPAI\\NBERTEMU LAGI.\""
                               f"\\N{{\\i0\\fs50}}{WT}sapaan asli: Ilyas Harun, 1977 (dibacakan ulang)"),
        ("kalau", "end", "KALAU BOLEH\\NTITIP PESAN,\\NKAMU MAU\\NBILANG APA?\\N{\\fs50}tulis di komentar"
                         "\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    FIX = {"Voyejer": "Voyager"}  # the TTS input spells "Voyejer" so Akram says it the way Indonesians do
elif EP == "41":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.69, 30.0  # the v4 take is 29,31 s: natural speed, no pause tightened, the CTA card held 0,69 s
    AUDIO = "vo41.mp3"
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    # made by skema41.py: skema_tinggi (the bloom pulled back, a ruler card with a 1,7 m person and the 3,2 m record, smell rings
    # out to 800 m), skema_mekar (the Bonn bud with a 7-year bar that ends in a 2-day sliver, then the photo wilts to grey) and
    # skema_resmi (the Bronx aerial with a gold "BUNGA RESMI" stamp)
    SHOTS = [
        (0, "tapi", "img/2443620.jpg", 0, "f", False, {"zoom": 0.1, "pos": 0.5, "grade": "pop"}),
        ("tapi", "tingginya", "clips/3627.mp4", 0, "v", True, {"zoom": 0.04, "pos": 0.42, "grade": "warm"}),
        ("tingginya", "masalahnya", "clips/skema_tinggi.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("masalahnya", "di#2", "clips/skema_mekar.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("di#2", "sampai#2", "img/1505672.jpg", 0, "f", False, {"zoom": 0.08, "grade": "bright"}),
        ("sampai#2", "kamu", "clips/skema_resmi.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("kamu", "end", "img/2443620.jpg", 0, "f", False, {"zoom": 0.06, "pos": 0.5, "grade": "dusk"}),
    ]
    LAB_ON, LAB_OFF = "{\\3c&H00E1FF&\\c&H141414&}", "{\\3c&H20401E0A&\\c&HFFFFFF&}"
    TITLES = [
        (0, "tapi", f"{{\\fs88}}{WT}BUNGA BANGKAI\\NDARI {Y}SUMATRA"),
        ("busuk", "tapi", f"{LAB_ON}BAUNYA BUSUK!", {"style": "Label", "pos": (5, 540, 600)}),
        ("tapi", "tingginya", f"{WT}TAPI DIANTRE\\N{Y}BERJAM-JAM\\N{WT}DI LUAR NEGERI"
                              f"\\N{{\\fs50}}The Huntington, AS (Juli 2026):\\N±5.000 orang sehari,\\Nada yang antre 3 jam lebih"),
        ("tingginya", "aromanya", f"{WT}BISA LEBIH DARI\\N{Y}3 METER\\N{{\\fs50}}{WT}rekor 3,2 m (Belgia, 2024)"),
        ("aromanya", "masalahnya", f"{WT}BAUNYA TERCIUM\\NSAMPAI {Y}800 M\\N{{\\fs50}}{WT}untuk memanggil\\Nkumbang bangkai dan lalat"),
        ("masalahnya", "layu", f"{WT}MEKARNYA\\N{Y}BERTAHUN-TAHUN\\N{WT}SEKALI\\N{{\\fs50}}biasanya 3–7 tahun sekali"),
        ("layu", "di#2", f"{WT}LALU {Y}LAYU\\N{WT}DALAM 1–2 HARI"),
        ("di#2", "sampai#2", f"{WT}NEW YORK, {Y}1937\\N{{\\fs50}}{WT}pertama mekar di benua Amerika,\\Nrumah kacanya diserbu\\Npengunjung dan wartawan"),
        ("sampai#2", "kamu", f"{Y}1939:\\N{WT}DIJADIKAN\\NBUNGA RESMI\\N{Y}BRONX!\\N{{\\fs50}}{WT}dari hutan Sumatra ke New York"),
        ("kamu", "end", "KAMU BERANI\\NANTRE UNTUK\\NMENCIUMNYA?\\N{\\fs50}jawab di komentar\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
    ]
    # two answer buttons light up in turn from "berani" to the end
    for k in range(9):
        a, b = f"berani+{k * 0.45:.2f}", f"berani+{(k + 1) * 0.45:.2f}" if k < 8 else "end"
        on = k % 2 == 0
        TITLES += [(a, b, f"{LAB_ON if on else LAB_OFF}BERANI", {"style": "Label", "pos": (5, 300, 1080), "raw": True}),
                   (a, b, f"{LAB_OFF if on else LAB_ON}NGGAK DEH", {"style": "Label", "pos": (5, 760, 1080), "raw": True})]
    FIX = {}
elif EP == "42":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 31,16 s: plain pauses tightened, then a small speed-up
    AUDIO = "vo42.mp3"
    # the dramatic pauses ("tahun...", "diputar...", "sken...", "terlihat:", between the spelled letters, "artinya...") are kept
    # whole; "mencoba," keeps a short breath before "gagal"
    TIGHT = {"tahun": 1.0, "diputar": 1.0, "mencoba": 0.45, "sken": 1.0, "terlihat": 1.0, "a": 1.0, "en": 1.0, "ce": 1.0,
             "e": 0.5, "artinya": 1.0}
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    # made by skema42.py (Pixabay + skema only, Arif 2026-11-06): img/hook42v.jpg and img/hook42c.jpg set Pixabay's antique
    # brass padlock (2503865, "ilustrasi") on a dark ground; skema_cincin and skema_kode draw the Ann Francis lock from the
    # museum record (four letter rings between two lettered end plates): rings numbered, spun in vain, a red stamp and a 3,2 cm
    # dimension line on "gagal"; then an X-ray look where each ring turns to A, N, C, E and the shackle lifts
    SHOTS = [
        (0, "dan#1", "img/hook42v.jpg", 0, "f", True, {"zoom": 0.08, "grade": "warm"}),
        ("dan#1", "pemburu", "img/hook42c.jpg", 0, "f", True, {"zoom": "punch", "grade": "warm"}),
        ("pemburu", "tempat", "clips/89527.mp4", 0, "v", True, {"zoom": 0.04, "pos": 0.42, "grade": "warm"}),
        ("tempat", "empat#2", "clips/197525.mp4", 0, "v", True, {"zoom": 0.04, "grade": "cold"}),
        ("empat#2", "sampai", "clips/skema_cincin.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("sampai", "dan#2", "img/3895160.jpg", 0, "b", False, {"zoom": 0.06, "grade": "cold", "tag": "ilustrasi: alat CT scan"}),
        ("dan#2", "tak", "clips/skema_kode.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("tak", "end", "clips/145647.mp4", 2, "v", False, {"zoom": 0.05, "pos": 0.6, "grade": "dusk"}),
    ]
    FLASH = "{\\an7\\pos(0,0)\\bord0\\shad0\\1c&HFFFFFF&\\1a&H50&\\fad(0,240)\\p1}m 0 0 l 1080 0 1080 1920 0 1920{\\p0}"
    SCAN = "{\\an7\\bord0\\shad0\\blur5\\1c&HFFE45A&\\1a&H30&\\move(0,560,0,1340)\\p1}m 0 0 l 1080 0 1080 7 0 7{\\p0}"
    TITLES = [
        (0, "dan#1", f"{{\\fs84}}{WT}GEMBOK {Y}KAPAL KARAM\\N{WT}TERKUNCI {Y}400+ TAHUN"),
        ("kapal", "dan#1", "{\\3c&H00E1FF&\\c&H141414&}KARAM 1583", {"style": "Label", "pos": (5, 540, 580)}),
        ("dan#1", "pemburu", f"{WT}...DAN KODENYA\\N{Y}BARU SAJA\\NDIPECAHKAN!\\N{{\\fs50}}{WT}diumumkan 4 November 2026"),
        ("dipecahkan", "dipecahkan+0.3", FLASH, {"raw": True}),
        ("pemburu", "tempat", f"{{\\fs84}}{WT}DITEMUKAN\\N{Y}PEMBURU HARTA\\N{WT}DI PANTAI {Y}WALES\\N{{\\fs50}}{WT}dengan detektor logam"),
        ("tempat", "empat#2", f"{{\\fs84}}{WT}KAPAL {Y}ANN FRANCIS\\N{WT}KARAM DIHANTAM\\N{Y}BADAI\\N{{\\fs50}}{WT}malam 28 Desember 1583"),
        ("empat#2", "diputar", f"{Y}4 CINCIN HURUF\\N{{\\fs50}}{WT}6 huruf di tiap cincin"),
    ]
    # on "diputar" the combination count runs up, then the last step pops
    STEP = 0.03
    TITLES += [(f"diputar+{k * STEP:.2f}", f"diputar+{(k + 1) * STEP:.2f}",
                f"{Y}4 CINCIN HURUF\\N{WT}= {{\\fs120}}{round(1296 * k / 32):,}\\N{{\\fs72}}KOMBINASI".replace(",", "."), {"raw": True})
               for k in range(32)]
    TITLES += [(f"diputar+{32 * STEP:.2f}", "gagal",
                f"{Y}4 CINCIN HURUF\\N{WT}= {{\\fs120\\t(0,110,\\fscx116\\fscy116)\\t(110,220,\\fscx100\\fscy100)}}1.296"
                f"\\N{{\\fs72}}KOMBINASI", {"raw": True}),
               ("gagal", "sampai", f"{WT}SEMUA YANG\\NMENCOBA {Y}GAGAL\\N{{\\fs50}}{WT}tingginya cuma 3,2 cm"),
               ("sampai", "dan#2", f"{WT}DIPINDAI DENGAN\\N{Y}MICRO-CT\\N{{\\fs50}}{WT}alat yang biasa dipakai\\Nuntuk memindai tulang\\N(Cardiff University)"),
               ("memindainya", "dan#2", SCAN, {"raw": True}),
               ("dan#2", "a", f"{WT}KODENYA\\NTERLIHAT..."),
               ("a", "en", f"{WT}KODENYA:\\N{{\\fs170}}{Y}A"),
               ("en", "ce", f"{WT}KODENYA:\\N{{\\fs170}}{Y}A N"),
               ("ce", "e", f"{WT}KODENYA:\\N{{\\fs170}}{Y}A N C"),
               ("e", "tak", f"{WT}KODENYA:\\N{{\\fs170}}{Y}A N C E"),
               ("tak", "menurutmu", f"{{\\fs170}}{Y}ANCE = ?\\N{{\\fs84}}{WT}TAK ADA YANG\\NTAHU ARTINYA"),
               ("menurutmu", "end", "MENURUTMU\\NARTINYA APA?\\N{\\fs50}tulis di komentar\\N{\\fs58\\c&HFFFFFF&}@titikheran")]
    FIX = {"Wels,": "Wales,", "En...": "N...", "Ce...": "C..."}  # the TTS input spells "Wels" and the letter names
elif EP == "43":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 29,73 s: no pause tightened, a 1% speed-up lands on 30,0 s
    AUDIO = "vo43.mp3"
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    # made by skema43.py: img/hook43.jpg and img/hook43c.jpg frame Pixabay's fiery streak over a riverside town (1715020,
    # "ilustrasi") larger than kind b would, the second closer on its bright head; img/11180v.jpg puts Cassiopeia A on black
    # (kind b showed the band's edges on its red blur); skema_swift draws the Swift telescope (shape
    # approximate) above the Earth with a 2004-2026 bar against the planned 2 years; skema_orbit lowers its orbit while the
    # active Sun pulses and the upper air thickens, ending on "275 km"; skema_link sends the LINK robot to 12-15 km, sets it
    # tumbling and drops it into the air with a tail of fire, calendar cards 25 SEP 2026 / 4 NOV 2026
    SHOTS = [
        (0, "bukan", "img/hook43.jpg", 0, "f", True, {"zoom": 0.08, "grade": "pop"}),
        ("bukan", "itu", "img/559641.jpg", 0, "f", True, {"zoom": "punch", "grade": "base"}),
        ("itu", "teleskop", "img/hook43c.jpg", 0, "f", True, {"zoom": 0.1, "grade": "pop"}),
        ("teleskop", "tapi#1", "img/11612.jpg", 0, "f", False, {"zoom": 0.06, "grade": "base", "tag": "ilustrasi: roket Delta II lain"}),
        ("tapi#1", "memburu", "clips/skema_swift.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("memburu", "masalahnya", "img/11180v.jpg", 0, "f", False,
         {"zoom": 0.08, "grade": "base", "tag": "ilustrasi: sisa supernova Cassiopeia A"}),
        ("masalahnya", "nasa#2", "clips/skema_orbit.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("nasa#2", "tapi#2", "img/693224.jpg", 0, "b", False, {"zoom": 0.06, "grade": "base", "tag": "ilustrasi: lengan robot ISS"}),
        ("tapi#2", "kamu", "clips/skema_link.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("kamu", "end", "img/5862911.jpg", 0, "b", False, {"zoom": 0.06, "grade": "dusk", "tag": "Masjid Raya Al-Mashun, Medan"}),
    ]
    FLASH = "{\\an7\\pos(0,0)\\bord0\\shad0\\1c&HFFFFFF&\\1a&H50&\\fad(0,240)\\p1}m 0 0 l 1080 0 1080 1920 0 1920{\\p0}"
    # a burst of light from the middle of the supernova remnant on "ledakan"
    BURST = ("{\\an5\\pos(540,870)\\bord0\\shad0\\blur36\\1c&HE8F8FF&\\fscx15\\fscy15\\t(0,260,\\fscx260\\fscy260)\\fad(0,520)\\p1}"
             "m -100 0 b -100 -55 -55 -100 0 -100 b 55 -100 100 -55 100 0 b 100 55 55 100 0 100 b -55 100 -100 55 -100 0{\\p0}")
    LAB_ON, LAB_OFF = "{\\3c&H00E1FF&\\c&H141414&}", "{\\3c&H20401E0A&\\c&HFFFFFF&}"
    TITLES = [
        (0, "bukan", f"{{\\fs88}}{WT}BOLA API DI\\NLANGIT {Y}SUMATRA"),
        ("rabu", "bukan", f"{LAB_ON}RABU 4 NOV · 19.39 WIB", {"style": "Label", "pos": (5, 540, 575)}),
        ("bukan", "itu", "{\\3c&H2C2CDC&\\c&HFFFFFF&\\fs96\\frz6}BUKAN METEOR!", {"style": "Label", "pos": (5, 540, 690)}),
        ("itu", "teleskop", f"{WT}SATELIT {Y}NASA\\N{WT}YANG JATUH\\NTERBAKAR\\N{{\\fs50}}teleskop Swift, ±1.450 kg"),
        ("terbakar", "terbakar+0.3", FLASH, {"raw": True}),
        ("teleskop", "tapi#1", f"{WT}DIRANCANG\\NUNTUK {Y}2 TAHUN\\N{{\\fs50}}{WT}diluncurkan 20 November 2004"),
        ("tapi#1", "memburu", f"{WT}BERTAHAN\\NHAMPIR {Y}22 TAHUN"),
        ("ledakan", "ledakan+0.6", BURST, {"raw": True}),
    ]
    # on "memburu" the burst count runs up, then the last step pops
    STEP, SUB = 0.03, f"\\N{{\\fs50}}{WT}dan ±1.400 supernova:\\Nledakan terdahsyat di alam semesta"
    TITLES += [(f"memburu+{k * STEP:.2f}", f"memburu+{(k + 1) * STEP:.2f}",
                f"{Y}{round(2000 * k / 30):,}\\N{WT}LEDAKAN\\NSINAR GAMMA{SUB}".replace(",", "."), {"raw": True}) for k in range(30)]
    TITLES += [(f"memburu+{30 * STEP:.2f}", "masalahnya",
                f"{Y}{{\\t(0,110,\\fscx116\\fscy116)\\t(110,220,\\fscx100\\fscy100)}}2.000+{{\\fscx100\\fscy100}}\\N{WT}LEDAKAN"
                f"\\NSINAR GAMMA{SUB}", {"raw": True}),
               ("masalahnya", "nasa#2", f"{WT}TANPA\\N{Y}MESIN PENDORONG"),
               ("nasa#2", "tapi#2", f"{Y}$30 JUTA\\N{WT}UNTUK ROBOT\\NPENYELAMAT\\N{{\\fs50}}±Rp540 miliar · robot LINK\\Ndari Katalyst Space"),
               ("tapi#2", "dan", f"{WT}ROBOTNYA\\N{Y}HILANG KENDALI"),
               ("dan", "kamu", f"{WT}...DAN MALAH\\NJATUH {Y}DULUAN!\\N{{\\fs50}}{WT}25 September 2026,\\N40 hari sebelum Swift"),
               ("kamu", "end", "KAMU SEMPAT\\NLIHAT\\NCAHAYANYA?\\N{\\fs50}tulis di komentar\\N{\\fs58\\c&HFFFFFF&}@titikheran")]
    # two answer buttons light up in turn from "lihat" to the end
    for k in range(6):
        a, b = f"lihat+{k * 0.45:.2f}", f"lihat+{(k + 1) * 0.45:.2f}" if k < 5 else "end"
        on = k % 2 == 0
        TITLES += [(a, b, f"{LAB_ON if on else LAB_OFF}SEMPAT LIHAT", {"style": "Label", "pos": (5, 320, 1090), "raw": True}),
                   (a, b, f"{LAB_OFF if on else LAB_ON}NGGAK", {"style": "Label", "pos": (5, 780, 1090), "raw": True})]
    FIX = {"Nasa": "NASA"}  # the TTS input spells "Nasa" so Akram says it as a word
elif EP == "44":
    STYLE, LUFS, PAD, TARGET = 2, -15, 0.6, 30.0  # the v4 take is 30,51 s: no pause tightened, a 3,8% speed-up lands on 30,0 s
    AUDIO = "vo44.mp3"
    Y, WT = "{\\c&H00E1FF&}", "{\\c&HFFFFFF&}"
    # made by skema44.py: img/dadu44.jpg (Pixabay dice 1502706 framed larger than kind b), img/jung44.jpg (the red-sail junk
    # 2644630 with the Hong Kong skyline blurred into haze and the modern hull name softened), clips/topan.mp4 (typhoon
    # photo 67581 turning slowly about its eye), skema_bangkai (seabed cross-section: the buried stern under 1 m+ of mud at
    # ±18 m, a knife, a mortar bowl and fish bones, then 5 dice) and skema_kepingan (old dominoes 969104 with an inset card of
    # one 3 x 1,5 cm tile beside a 1 cm die on a ruler, shape approximate)
    SHOTS = [
        # 751c = Pixabay 751 without its 2.35:1 letterbox and fade-in, gamma lifted (skema44.py prep)
        (0, "dan#1", "clips/751c.mp4", 0, "v", True, {"zoom": 0.04, "pos": 0.43, "grade": "base"}),
        ("dan#1", "armadanya", "img/dadu44.jpg", 0, "f", True, {"zoom": 0.08, "grade": "warm"}),
        ("armadanya", "tapi", "img/jung44.jpg", 0, "f", False, {"zoom": 0.06, "grade": "sepia", "tag": "ilustrasi: kapal jung Tiongkok"}),
        ("tapi", "badai", "clips/topan.mp4", 0, "v", False, {"zoom": 0.0, "grade": "cold", "tag": "ilustrasi: topan dari satelit"}),
        ("badai", "di#2", "clips/216500.mp4", 20.5, "v", True, {"zoom": 0.04, "grade": "cold"}),
        ("di#2", "dan#3", "clips/skema_bangkai.mp4", 0, "v", False, {"zoom": 0.0, "tag": "skema"}),
        ("dan#3", "sepertinya", "clips/skema_kepingan.mp4", 0, "v", True, {"zoom": 0.0}),
        ("sepertinya", "kalau", "img/5926938.jpg", 0, "b", True, {"zoom": 0.07, "grade": "base"}),
        ("kalau", "end", "clips/28659.mp4", 2.4, "v", False, {"zoom": 0.0, "pan": (0.0, 1.0), "grade": "warm"}),
    ]
    FLASH = "{\\an7\\pos(0,0)\\bord0\\shad0\\1c&HFFFFFF&\\1a&H50&\\fad(0,240)\\p1}m 0 0 l 1080 0 1080 1920 0 1920{\\p0}"
    LAB = "{\\3c&H00E1FF&\\c&H141414&}"
    TITLES = [
        (0, "dan#1", f"{{\\fs88}}{WT}KAPAL PERANG\\N{Y}MONGOL\\N{WT}TENGGELAM 1281"),
        ("tenggelam", "dan#1", f"{LAB}745 TAHUN DI DASAR LAUT", {"style": "Label", "pos": (5, 540, 690)}),
        ("dadu#1", "armadanya", f"{WT}...DAN DI DALAMNYA\\NADA {Y}DADU!\\N{{\\fs50}}{WT}diumumkan 28 Oktober 2026"),
        ("dadu#1", "dadu#1+0.3", FLASH, {"raw": True}),
        ("armadanya", "menaklukkan", f"{WT}ARMADA\\N{Y}KUBILAI KHAN\\N{{\\fs50}}{WT}cucu Jenghis Khan"),
        ("menaklukkan", "tapi", f"{Y}±4.400 KAPAL\\N±140.000 ORANG\\N{{\\fs50}}{WT}tahun 1281, untuk menaklukkan Jepang"),
        ("tapi", "badai", f"{WT}TOPAN\\NMENENGGELAMKAN\\N{Y}SEBAGIAN BESAR\\N{WT}ARMADA\\N{{\\fs50}}15 Agustus 1281"),
        ("badai", "kamikaze", f"{WT}BADAI YANG\\NDIJULUKI..."),
        ("kamikaze", "di#2", f"{{\\fs150}}{Y}KAMIKAZE\\N{{\\fs50}}{WT}artinya \"angin dewa\""),
        ("di#2", "lima", f"{WT}DI DEKAT\\N{Y}ALAT DAPUR\\N{WT}DAN TULANG IKAN..."),
        ("lima", "dan#3", f"{{\\fs130}}{Y}5 DADU\\N{{\\fs50}}{WT}masing-masing ±1 cm"),
        ("dan#3", "sepertinya", f"{Y}29 KEPINGAN\\N{WT}MIRIP DOMINO\\N{{\\fs50}}benda permainan pertama\\Ndari ±4.000 artefak di situs ini"),
        ("sepertinya", "kalau", f"{WT}DIDUGA\\N{Y}ALAT HIBURAN\\N{WT}AWAK KAPAL\\N{{\\fs50}}kata peneliti Kokugakuin University"),
        ("kalau", "end", "KALAU KAMU,\\NMAU MAIN APA?\\N{\\fs50}tulis di komentar\\N{\\fs58\\c&HFFFFFF&}@titikheran"),
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
            if i not in want_at:  # a word with its own length: Scribe's end can run into the pause (#26), so trust the level
                t0 = max(t0, words[i]["end"] + 0.05)
            if i + 1 < len(words):
                t1 = min(t1, words[i + 1]["start"] - 0.04)
            end = words[i]["text"][-1]
            want = want_at.get(i, 0.36 if end in ".?!" else 0.24 if end in ",;:" else 0.16)
        k = max(0.0, want - (t0 - quiet0) - (quiet1 - t1))
        if t1 - t0 > k + 0.03:
            cuts.append((t0 + 0.6 * k, t1 - 0.4 * k))
    if sys.argv[2:] == ["plan"]:  # where the cuts fall, so a whispered word cut in half shows up before the render
        for c0, c1 in cuts:
            i = [k for k, w in enumerate(words) if w["start"] <= c0][-1]
            print(f"  cut {c0:6.2f}-{c1:6.2f} ({c1 - c0:.2f}s) after \"{words[i]['text']}\"")
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
        "23": [("lima belas", "15"), ("lima puluh", "50")],
        "24": [("seratus", "100"), ("si ti sken", "CT scan")],
        "25": [],
        "26": [("tujuh minggu!", "7 minggu!")],
        "27": [("tujuh puluh karat...", "70 karat..."), ("tiga puluh delapan.", "38.")],
        "28": [("empat ribu", "4.000"), ("seribu delapan ratus", "1.800")],
        "29": [],
        "30": [("delapan ribu", "8.000"), ("lima belas", "15")],
        "31": [("lima hari", "5 hari")],
        "32": [("seribu delapan ratus", "1.800"), ("dua", "2")],
        "33": [("dua puluh lima ribu", "25.000")],
        "34": [("delapan puluh persen!", "80%!")],
        "35": [("lima abad", "5 abad")],
        "36": [("dua ribu tahun...", "2.000 tahun..."), ("tiga puluh delapan koin.", "38 koin."), ("dua puluh empat", "24")],
        "37": [("tiga puluh satu ribu", "31.000"), ("tujuh ribu", "7.000"), ("enam", "6"), ("sembilan", "9")],
        "38": [("dua ribu tujuh ratus tahun.", "2.700 tahun."), ("dua puluh empat", "24"), ("kedelapan belas.", "ke-18.")],
        "39": [("satu meter.", "1 meter.")],
        "40": [("voyejer satu", "Voyager 1"), ("satu hari", "1 hari"), ("lima puluh tahun", "50 tahun")],
        "41": [("tiga meter...", "3 meter..."), ("delapan ratus meter.", "800 meter."), ("dua hari.", "2 hari.")],
        "42": [("empat ratus tahun...", "400 tahun..."), ("empat cincin", "4 cincin"), ("si ti sken...", "CT scan...")],
        "43": [("dua tahun...", "2 tahun..."), ("dua puluh dua tahun,", "22 tahun,"), ("tiga puluh juta dolar", "30 juta dolar")],
        "44": [("tujuh abad", "7 abad"), ("lima dadu...", "5 dadu..."), ("dua puluh sembilan", "29")]}[EP]
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
    end_sentence = w["text"].rstrip("\"'”)")[-1:] in tuple(".,?:!")  # a closing quote still ends the clause (#40: lagi.")
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
    # raw: the text brings its own override tags (a vector drawing such as a strike-through), so no pop-in
    pop = "" if a == 0 or o.get("raw") else "\\fad(60,0)\\fscx70\\fscy70\\t(0,110,\\fscx108\\fscy108)\\t(110,200,\\fscx100\\fscy100)"
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
    if w["text"].rstrip("\"'”)")[-1:] in tuple(".,?!:"):
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
          # warm: terracotta and clay a little warmer; aged: half-way to sepia, for the 1937 scenes
          "warm": "eq=contrast=1.06:saturation=1.12,colorbalance=rs=0.05:rm=0.06:rh=0.03:bs=-0.05:bm=-0.05:bh=-0.02",
          "aged": "colorchannelmixer=.6965:.3845:.0945:0:.1745:.843:.084:0:.136:.267:.5655,eq=contrast=1.06",
          # dusk: twilight with bluish shadows and warm light on the stone, brighter than dim (the #32 hook)
          "dusk": "eq=brightness=-0.03:contrast=1.1:saturation=1.1,colorbalance=bs=0.06:bm=0.03:rh=0.05:rm=0.03",
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


def watermark(path):
    """a thin, see-through "@titikheran" centred on the frame, with a soft shadow so it still reads on white coral or sky"""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 96)  # drawn at 2x, then scaled down
    text, track = "@titikheran", 6
    x = W - (sum(f.getlength(c) for c in text) + track * (len(text) - 1)) / 2
    _, y0, _, y1 = f.getbbox(text)
    y = H - (y0 + y1) / 2
    fg, sh = Image.new("RGBA", (2 * W, 2 * H)), Image.new("RGBA", (2 * W, 2 * H))
    for c in text:
        ImageDraw.Draw(sh).text((x + 2, y + 3), c, font=f, fill=(0, 0, 0, 56))
        ImageDraw.Draw(fg).text((x, y), c, font=f, fill=(255, 255, 255, 61))
        x += f.getlength(c) + track
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    sh.alpha_composite(fg)
    sh.resize((W, H), Image.LANCZOS).save(path)


vf = f"[0:v]ass=seg{EP}/subs.ass[v]"
if int(EP) >= 26:  # anti-theft watermark (Arif, 2026-10-28): drawn before the titles and captions, so it never covers them
    watermark(f"seg{EP}/wm.png")
    vf = f"movie=seg{EP}/wm.png[wm];[0:v][wm]overlay=0:0,ass=seg{EP}/subs.ass[v]"
out = f"titik-heran-{EP}.mp4"
run(["ffmpeg", "-v", "error", "-y", "-i", f"seg{EP}/video.mp4", "-i", AUDIO,
     "-filter_complex", f"{vf};[1:a]{af},aresample=48000[a]",
     "-map", "[v]", "-map", "[a]", "-t", f"{OUT_LEN:.3f}",
     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
     "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
print(out, OUT_LEN, TEMPO)
