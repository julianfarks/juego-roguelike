#!/usr/bin/env bash
# Pruebas automaticas (banco headless, NO dispositivo real): mas enemigos tras cada jefe (escalado central), tope de vivos a la vez,
# entrada gradual, persecucion, transiciones sin duplicados, dificultad, Infinito independiente y rendimiento.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
out=$(BOT_ESCAL=1 BOT_GOD=1 BOT_SEED=11 BOT_WARP=combat:0 timeout 400 $RUN --headless --bot --frames 1200 2>&1 | grep -E "^ES|Exception|at com\.")
echo "$out" | grep -E "FALLA|FIN|PERF|Exception|at com\."
echo "$out" | grep -c "ES OK" | sed 's/^/OK: /'
echo "$out" | grep -q "fallos=0" && { echo "ESCALADO OK"; exit 0; } || { echo "ESCALADO FALLA"; exit 1; }
