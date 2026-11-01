"""Contact sheet of a rendered video: python3 sheet.py VIDEO OUT.jpg t1,t2,... [cols]
Each frame is grabbed with ffmpeg at the given second and labelled with its time."""
import subprocess, sys, io
from PIL import Image, ImageDraw, ImageFont

video, out, times = sys.argv[1], sys.argv[2], [float(t) for t in sys.argv[3].split(",")]
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6
tw, th = 360, 640
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
frames = []
for t in times:
    png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", video, "-frames:v", "1", "-f", "image2pipe",
                          "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(png)).convert("RGB").resize((tw, th), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rectangle((0, th - 38, 110, th), fill=(0, 0, 0))
    d.text((8, th - 34), f"{t:.2f}", font=font, fill=(255, 255, 0))
    frames.append(im)
rows = (len(frames) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw + (cols - 1) * 6, rows * th + (rows - 1) * 6), (40, 40, 40))
for i, im in enumerate(frames):
    sheet.paste(im, ((i % cols) * (tw + 6), (i // cols) * (th + 6)))
sheet.save(out, quality=88)
print(out, sheet.size)
