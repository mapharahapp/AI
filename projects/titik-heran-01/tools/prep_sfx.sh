#!/bin/bash
# prep_sfx.sh — pick one take per SFX (ElevenLabs flow YpSWNR6YtnCiwra54JQR), peak-normalise to -3 dBFS,
# write assets/audio/sfx/<name>.wav + assets/audio/sfx.json. The mix level is set per cue in build.mjs.
set -euo pipefail
cd "${1:-.}"
PICK="match:2 ting:1 carve:1 blow:4 whoosh:3 pop:4 sting:2 hum:1 wind:3 flame:4"
echo "{" > assets/audio/sfx.json; first=1
for p in $PICK; do
  n=${p%%:*}; k=${p##*:}; src=raw/sfx/${n}_${k}.mp3; out=assets/audio/sfx/$n.wav
  peak=$(ffmpeg -hide_banner -i "$src" -af volumedetect -f null - 2>&1 | sed -n 's/.*max_volume: \(-\?[0-9.]*\) dB/\1/p')
  gain=$(python3 -c "print(round(-3 - ($peak), 2))")
  ffmpeg -v error -y -i "$src" -af "volume=${gain}dB" -ar 44100 -ac 2 -c:a pcm_s16le "$out"
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")
  [ $first = 1 ] || echo "," >> assets/audio/sfx.json; first=0
  printf '  "%s": { "file": "%s", "dur": %s, "take": %s, "gain_db": %s }' "$n" "$out" "$dur" "$k" "$gain" >> assets/audio/sfx.json
  echo "  $n  take $k  peak $peak dB -> gain ${gain} dB  ${dur}s"
done
printf '\n}\n' >> assets/audio/sfx.json
