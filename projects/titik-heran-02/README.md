# Titik Heran #2 — Ngengat Bogong

Vertical (1080×1920, 30 fps) short built from the doc *"Titik Heran: Naskah & Storyboard Video #2"*, with the
Hyperframe Pro loop in this repo: one voice take → word-locked cues → generator → lint → check → render.

| Layer | Source |
|---|---|
| Voice-over | ElevenLabs, voice **Akram** (`mKyb2q1tbP41xJ8qTnox`), `eleven_v4`, one take (580.94 credits), pauses capped (`tools/cap_pauses.py`) |
| Music / SFX | none, by request |
| B-roll | **Pixabay**, 9 slots (licences in `publish/sources.txt`), sourced with `tools/pixabay.py`; AI-flagged items refused via the API's `isAiGenerated` |
| Map | Natural Earth via `world-atlas` (`tools/make_map.mjs`) |
| Moth swarms, wind, map camera, pins, labels | drawn: `assets/swarm.js`, a pure function of time fed by seeded tables from `build.mjs` |
| Population line | drawn, schematic (labelled "ilustrasi tren"); only the two sourced points are marked: −99,5 % (2017) and 2026 |

No HeyGen avatar. Pixabay has no footage of a moth swarm, so the swarm is drawn over real night footage of Sydney.

Master: `publish/titik-heran-02_master.mp4` — 1080×1920, 30 fps, 41.1 s, H.264 + AAC, −13.8 LUFS integrated,
true peak −1.3 dBFS, no black frames, last frame vs first frame SSIM 0.967 (the end card returns to frame 0 for the
loop). Measured with `python3 -I tools/qa.py <video> qa/qa2_results.json`.

## Build

```bash
npm install
node tools/make_map.mjs .
node build.mjs .                  # refuses to build while any slot has no Pixabay clip (DRAFT=1 for placeholders)
node ../../plugins/hyperframe-pro/scripts/lint.mjs . build.mjs
HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
  npx hyperframes check .
npx hyperframes render . -o renders/titik-heran-02.mp4 -f 30
```

`check` and `render` rewrite `index.html` in place; run `node build.mjs .` again before linting.

## The drawn layer

`assets/swarm.js` redraws one canvas from composition time alone: no `Math.random`, no clocks, no state carried
between frames. It is driven by a full-length proxy tween's `onUpdate` and by the runtime's `hf-seek` event. The
map camera is evaluated analytically there too (and written to `#mapz`), so the pins and the moths on the map can
never drift from the land under them. Out-of-focus moths are sprites blurred once on small canvases: a canvas
`filter: blur()` per draw call costs seconds per frame in the software rasterizer the renderer uses.

## Sourcing a b-roll slot

```bash
python3 -I tools/pixabay.py search videos "sydney opera house night" raw/pixabay/sydney/q1   # look at sheet.jpg
python3 -I tools/pixabay.py fetch  videos <id> raw/pixabay/sydney
python3 -I tools/pixabay.py sheet  raw/pixabay/sydney/<id>.mp4 raw/pixabay/sydney/<id>-sheet.jpg
python3 -I tools/pixabay.py prep   raw/pixabay/sydney/<id>.mp4 assets/footage/sydney.mp4 --focus 0.36 --ss 0 --t 5.6
python3 -I tools/pixabay.py record sydney assets/footage/sydney.mp4 raw/pixabay/sydney/<id>.json --at 1.2
# a landscape PHOTO goes through a plate first (readable size, feathered into a blurred copy of itself or black)
python3 -I tools/pixabay.py plate  raw/pixabay/moth/<id>.jpg raw/plates/window.png --fw 1300 --cy 880 --sides
```
