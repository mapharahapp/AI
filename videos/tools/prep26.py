"""Stills for Titik Heran #26 (run in the episode work dir after `dl.py i:20497`).
img/20497v.jpg: the bleached coral skeleton (Pixabay 20497, shot on pure black) on a black vertical canvas, a little wider than the
frame, with the skeleton between the title and the captions; render.py shows it as kind f, so no blurred copy shows round it.
"""
from PIL import Image

im = Image.open("img/20497.jpg").convert("RGB")
w = 1180  # the skeleton spans 13-94% of the photo's width, so it still fits across the 1080 px frame
im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
canvas = Image.new("RGB", (1080, 1920))
canvas.paste(im, ((1080 - w) // 2, 470))
canvas.save("img/20497v.jpg", quality=95)
print("img/20497v.jpg")
