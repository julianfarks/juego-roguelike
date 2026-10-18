#!/usr/bin/env bash
# Prueba REAL de ventana (Xvfb): arranca el juego de PC en pantalla completa / sin bordes / ventana con monitores virtuales de distintos
# tamanos, captura el escritorio y mide las franjas negras. No prueba hardware real (monitor, DPI de Windows, modo exclusivo): solo el
# camino de codigo de ventana + escalado + presentacion con un X11 virtual.
# Uso: tools/tests/pc_fullscreen_test.sh [MODO(0 ventana,1 completa,2 sin bordes)] [lista WxH ...]
set -uo pipefail
cd "$(dirname "$0")/../.."
MODE=${1:-1}; shift || true
SIZES=${*:-"1920x1080 2560x1440 1366x768 1920x1200 1600x900 1280x720 2560x1600"}
OUT=/tmp/swr_fstest; rm -rf "$OUT"; mkdir -p "$OUT/cls"
JV=$(javac -version 2>&1 | grep -o 'javac [0-9]*' | grep -o '[0-9]*' | head -1)
if [ "$JV" -ge 22 ]; then F="--release 22"; R=""; else F="--release 21 --enable-preview"; R="--enable-preview"; fi
find Shared/src/main/java PC/src/main/java -name '*.java' ! -name OggJorbis.java > "$OUT/s.txt"
javac $F -encoding UTF-8 -nowarn -d "$OUT/cls" @"$OUT/s.txt" 2>&1 | grep -v "^Note\|^Picked" ; [ -f "$OUT/cls/pc/PcMain.class" ] || { echo "no compila"; exit 1; }
fail=0
for sz in $SIZES; do
  W=${sz%x*}; H=${sz#*x}; D=$OUT/data_$sz; mkdir -p "$D"
  echo "pc_video=mode=$MODE;w=$W;h=$H;fps=60;vsync=0;showFps=0;scale=${SCALE:-0};q=2;part=100;light=1;vig=1" > "$D/pc_settings.properties"
  echo "pcsave=" >> "$D/pc_settings.properties"
  Xvfb :77 -screen 0 ${W}x${H}x24 >/dev/null 2>&1 & XP=$!
  sleep 1.5
  DISPLAY=:77 java $R -cp "$OUT/cls:PC/src/main/resources" pc.PcMain --assets Shared/assets --data "$D" --no-audio --no-pad > "$D/log.txt" 2>&1 & JP=$!
  sleep ${WAIT:-14}
  DISPLAY=:77 import -window root "$OUT/shot_${MODE}_$sz.png" 2>/dev/null
  kill $JP 2>/dev/null; sleep 0.5; kill -9 $JP 2>/dev/null; kill $XP 2>/dev/null; wait 2>/dev/null
  python3 - "$OUT/shot_${MODE}_$sz.png" "$W" "$H" "$MODE" <<'PY' || fail=1
import sys
from PIL import Image
import numpy as np
im=np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int); W,H,mode=int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])
h,w,_=im.shape
mx=im.max(axis=2)
def bar(v):  # filas/columnas contiguas completamente negras en cada borde
    t=0
    while t<len(v) and v[t]<6: t+=1
    b=0
    while b<len(v)-t and v[len(v)-1-b]<6: b+=1
    return t,b
rows=mx.max(axis=1); cols=mx.max(axis=0)
(tt,bb),(ll,rr)=bar(rows),bar(cols)
print("%dx%d captura %dx%d  franjas negras: arriba %d abajo %d izq %d der %d"%(W,H,w,h,tt,bb,ll,rr))
ok = (w,h)==(W,H) and mx.max()>60
if mode!=0: ok = ok and tt<=2 and bb<=2 and ll<=2 and rr<=2 if W*270>=H*480 and W*270<=H*640 else ok
print("  ->", "OK" if ok else "REVISAR")
sys.exit(0 if ok else 1)
PY
done
exit $fail
