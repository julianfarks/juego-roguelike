#!/usr/bin/env bash
# Prueba de estres: jefe + ultimate + las 3 habilidades pulsadas cada 20 fotogramas, durante ~13 s (banco headless con render real DesktopGfx).
# Mide: fotogramas lentos (>35 ms), pico de update/render, objetos vivos (proj/fx/part), heap y GC (Xlog:gc). Sin hardware real: es el banco del motor.
# Uso: perf_stress_test.sh [salida.txt]   (RUN=/tmp/run2.sh por defecto)
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
OUT=${1:-/tmp/perf_run.txt}; S=/tmp/perf_stress.script
python3 - <<PY > $S
for f in range(420, 1400, 20):
    for k in "UIOP": print(f, "key", k, "down"); print(f+4, "key", k, "up")
PY
export JAVA_TOOL_OPTIONS="-Xmx512m -Xlog:gc:file=${OUT%.txt}_gc.log"
BOT_PERF=1 BOT_SLOW=35 BOT_GOD=1 BOT_CLASS=${BOT_CLASS:-0} BOT_WARP=boss:0 BOT_ULT=1 timeout 900 $RUN --headless --bot --pc --frames 1500 --script $S > $OUT 2>&1
slow=$(grep -c '^SLOW' $OUT); worst=$(grep '^SLOW' $OUT | sed -E 's/.*upd=([0-9.]+)ms rnd=([0-9.]+)ms/\1 \2/' | awk '{if($1>u)u=$1; if($2>r)r=$2} END{printf "upd_max=%.1fms rnd_max=%.1fms", u, r}')
gc20=$(grep -oE '[0-9.]+ms$' ${OUT%.txt}_gc.log | tr -d 'ms' | awk '$1>20' | wc -l)
oom=$(grep -c OutOfMemory $OUT)
echo "slow>35ms=$slow $worst gc>20ms=$gc20 oom=$oom"
grep '^PERF' $OUT | tail -3
grep '^PERF' $OUT | sed -E 's/.*heapMB=([0-9]+).*/\1/' | sort -n | tail -1 | sed 's/^/heap_max_MB=/'
