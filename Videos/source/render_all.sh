#!/usr/bin/env bash
# Renderiza los dos trailers finales a partir de las escenas grabadas. Requiere ffmpeg (libx264, aac), python3, numpy, Pillow.
set -e
cd "$(dirname "$0")"
CL="${1:-./clips}"
python3 edit_trailer.py es ../Trailer_Spanish.mp4 --clips "$CL"
python3 edit_trailer.py en ../Trailer_English.mp4 --clips "$CL"
rm -f ../*.audio.raw
