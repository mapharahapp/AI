"""Stills for Titik Heran #21 (run in the episode work dir after `dl.py i:10214497 i:2104784`).
img/10214497v.jpg: the landscape slow loris illustration on a vertical canvas: the face sharp and large in the middle, the rest of the
picture blurred and darkened above and below it, the edges blended, so it can fill a 1080x1920 shot.
clips/2104784k.mp4: the oil palm photo as a 6 s clip with a slow push-in, for the bottom half of the split screen.
"""
import subprocess
import numpy as np
from PIL import Image, ImageFilter

W, H = 1080, 1920
src = Image.open("img/10214497.jpg").convert("RGB")
sw, sh = src.size
k = H / sh
bg = src.resize((round(sw * k), H), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40))
bg = Image.fromarray((np.array(bg, np.float32) * 0.6).astype(np.uint8))
x0, x1, top = 300, 980, 470  # the crop around the face, and where its top edge lands
fg = src.crop((x0, 0, x1, sh))
fg = fg.resize((W, round(sh * W / (x1 - x0))), Image.LANCZOS)
y = np.arange(fg.height, dtype=np.float32)
a = np.clip(y / 140, 0, 1) * np.clip((fg.height - y) / 160, 0, 1)
a = a * a * (3 - 2 * a)
mask = Image.fromarray((np.repeat(a[:, None], W, 1) * 255).astype(np.uint8))
bg.paste(fg, (0, top), mask)
bg.save("img/10214497v.jpg", quality=95)
print("img/10214497v.jpg", bg.size)

subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-i", "img/2104784.jpg",
                "-vf", "scale=3840:-2:flags=lanczos,zoompan=z='1+0.08*on/180':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                ":d=180:s=1920x1080:fps=30,format=yuv420p",
                "-frames:v", "180", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "clips/2104784k.mp4"], check=True)
print("clips/2104784k.mp4")
