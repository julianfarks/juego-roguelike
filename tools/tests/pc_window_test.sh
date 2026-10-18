#!/usr/bin/env bash
# Cambios de modo/resolucion en una ventana real sobre un X11 virtual (Xvfb): ventana -> sin bordes -> completa -> ventana -> completa -> ventana.
# Uso: tools/tests/pc_window_test.sh [WxH del monitor virtual, por defecto 2560x1440]
set -uo pipefail
cd "$(dirname "$0")/../.."
SZ=${1:-2560x1440}
OUT=/tmp/swr_wintest; rm -rf "$OUT"; mkdir -p "$OUT/cls"
JV=$(javac -version 2>&1 | grep -o 'javac [0-9]*' | grep -o '[0-9]*' | head -1)
if [ "$JV" -ge 22 ]; then F="--release 22"; R=""; else F="--release 21 --enable-preview"; R="--enable-preview"; fi
find Shared/src/main/java PC/src/main/java tools/tests/pc -name '*.java' ! -name OggJorbis.java > "$OUT/s.txt"
javac $F -encoding UTF-8 -nowarn -d "$OUT/cls" @"$OUT/s.txt" 2>&1 | grep -v "^Note\|^Picked"
Xvfb :78 -screen 0 ${SZ}x24 >/dev/null 2>&1 & XP=$!
sleep 1.5
DISPLAY=:78 java $R -cp "$OUT/cls:PC/src/main/resources" pc.WindowTest "$OUT/shots" 2>&1 | grep -v "^Picked"; RC=${PIPESTATUS[0]}
kill $XP 2>/dev/null
exit $RC
