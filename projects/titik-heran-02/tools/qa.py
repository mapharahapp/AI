"""qa.py — measurable checks on a rendered master.

    python3 -I tools/qa.py <video.mp4> [out.json]

Prints and writes: stream facts, integrated loudness / true peak (EBU R128), black and frozen stretches, and the
loop seam (how close the LAST frame is to the FIRST, as SSIM) — the end card is built to return to frame 0."""
import json, re, subprocess, sys

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else None


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout + r.stderr


probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", src],
                                  capture_output=True, text=True).stdout)
v = next(s for s in probe["streams"] if s["codec_type"] == "video")
a = next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)
res = {
    "file": src, "bytes": int(probe["format"]["size"]), "duration": float(probe["format"]["duration"]),
    "video": {"codec": v["codec_name"], "w": v["width"], "h": v["height"], "fps": v["r_frame_rate"], "pix": v.get("pix_fmt"),
              "frames": int(v.get("nb_frames", 0) or 0)},
    "audio": {"codec": a["codec_name"], "rate": a["sample_rate"], "ch": a["channels"]} if a else None,
}
e = run(["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-filter_complex", "ebur128=peak=true", "-f", "null", "-"])
summ = e[e.rfind("Summary:"):]
res["loudness"] = {"I_LUFS": float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1)),
                   "LRA": float(re.search(r"LRA:\s+(-?[\d.]+) LU", summ).group(1)),
                   "truePeak_dBFS": float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1))}
b = run(["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-vf", "blackdetect=d=0.15:pix_th=0.06", "-an", "-f", "null", "-"])
res["black"] = [(float(m.group(1)), float(m.group(2))) for m in re.finditer(r"black_start:([\d.]+) black_end:([\d.]+)", b)]
f = run(["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-vf", "freezedetect=n=0.002:d=0.6", "-an", "-f", "null", "-"])
starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", f)]
ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", f)]
res["frozen"] = list(zip(starts, ends + [res["duration"]] * (len(starts) - len(ends))))
# loop seam: SSIM of the last frame against the first
n = res["video"]["frames"] or round(res["duration"] * 30)
s = run(["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-i", src, "-filter_complex",
         f"[0:v]select='eq(n\\,{n - 1})',setpts=PTS-STARTPTS[a];[1:v]select='eq(n\\,0)',setpts=PTS-STARTPTS[b];[a][b]ssim",
         "-frames:v", "1", "-f", "null", "-"])
m = re.search(r"All:([\d.]+)", s)
res["loopSeamSSIM"] = float(m.group(1)) if m else None
print(json.dumps(res, indent=1))
if out:
    json.dump(res, open(out, "w"), indent=1)
