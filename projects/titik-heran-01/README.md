# Titik Heran #1 — Lentera Lobak

Vertical (1080×1920, 30 fps) short built from the doc *"Titik Heran: Naskah & Storyboard Video #1"*, with the
Hyperframe Pro loop in this repo: one voice take → word-locked cues → generator → lint → snapshot → render.

| Layer | Source |
|---|---|
| Voice-over | ElevenLabs, voice **Akram** (`mKyb2q1tbP41xJ8qTnox`), `eleven_v4`, take 3 of 4, pauses capped (`tools/cap_pauses.py`) |
| Music bed | ElevenLabs Music v2.5, instrumental, variation 1, envelope dips under the problem act |
| SFX | ElevenLabs SFX v2 — match, ting, carve, blow, whoosh, pop, sting (`tools/prep_sfx.sh`) |
| Map | Natural Earth via `world-atlas` (`tools/make_map.mjs`) |
| B-roll | **Pixabay** — 8 of 11 slots (licences in `publish/sources.txt`), sourced with `tools/pixabay.py` |
| Turnip lantern + carving | generic AI stills (ElevenLabs gpt-image-2.5): Pixabay has no turnip-lantern footage; approved by the user, as the script's production note suggests |

No HeyGen avatar.

## Checks before a render

```bash
node build.mjs . && node ../../plugins/hyperframe-pro/scripts/lint.mjs . build.mjs
python3 tools/audio_margins.py . 10 --speech-band     # voice above the bed, word by word
```

## Build

```bash
npm install
node tools/make_map.mjs .
DRAFT=1 node build.mjs .          # preview: empty b-roll slots render as labelled placeholders
node build.mjs .                  # final: refuses to build while any slot has no Pixabay clip
node ../../plugins/hyperframe-pro/scripts/lint.mjs . build.mjs
HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
  npx hyperframes render . -o renders/titik-heran-01.mp4 -f 30
```

## Sourcing a b-roll slot

```bash
python3 -I tools/pixabay.py search videos "turnip lantern" raw/pixabay/turnip/q1   # look at sheet.jpg
python3 -I tools/pixabay.py fetch  videos <id> raw/pixabay/turnip
python3 -I tools/pixabay.py sheet  raw/pixabay/turnip/<id>.mp4 raw/pixabay/turnip/<id>-sheet.jpg
python3 -I tools/pixabay.py prep   raw/pixabay/turnip/<id>.mp4 assets/footage/turnip.mp4 --focus 0.5
python3 -I tools/pixabay.py record turnip assets/footage/turnip.mp4 raw/pixabay/turnip/<id>.json --at 1.2
```

`record` writes `assets/footage/manifest.json` and the licence line in `publish/sources.txt` (the lint refuses
footage without one). `at` is the clip time of the slot's first frame; see the usage table printed by the
cue script in the session notes for how long each slot must run after `at`.
