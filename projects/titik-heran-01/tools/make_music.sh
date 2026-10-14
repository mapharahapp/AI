#!/bin/bash
# make_music.sh — music bed from ElevenLabs Music variation 1 (raw/music/music_1.mp3, 41 s).
# The generated outro starts at ~34 s, so the CTA would play dry. Repeat the 24-30 s body once
# (0.5 s crossfades) so the outro lands on the end card, then dip under the problem act and lift after.
set -euo pipefail
cd "${1:-.}"
SRC=raw/music/music_1.mp3
ffmpeg -v error -y -i $SRC -filter_complex "
  [0:a]atrim=0:30.25,asetpts=PTS-STARTPTS[a];
  [0:a]atrim=23.75:30.25,asetpts=PTS-STARTPTS[b];
  [0:a]atrim=29.75,asetpts=PTS-STARTPTS[c];
  [a][b]acrossfade=d=0.5:c1=tri:c2=tri[ab];
  [ab][c]acrossfade=d=0.5:c1=tri:c2=tri,
  volume='if(lt(t,16.2),1,if(lt(t,16.9),1-0.45*(t-16.2)/0.7,if(lt(t,24.0),0.55,if(lt(t,24.6),0.55+0.6*(t-24.0)/0.6,1.15))))':eval=frame[out]" \
  -map "[out]" -ar 44100 -ac 2 -c:a aac -b:a 192k assets/audio/music.m4a
echo "music.m4a $(ffprobe -v error -show_entries format=duration -of csv=p=0 assets/audio/music.m4a)s"
