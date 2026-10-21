#!/usr/bin/env bash
# Pruebas automaticas (banco headless, NO dispositivo real): mejoras acumulables por niveles, generacion de recompensas segun la build,
# omitir/reabrir sin duplicar, pestaña Mejoras del inventario y sinergias.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
out=$(BOT_UPGRADES=1 BOT_GOD=1 BOT_SEED=7 BOT_WARP=combat:0 timeout 300 $RUN --headless --bot --frames 1200 2>&1 | grep -E "^UP|Exception|at com\.")
echo "$out" | grep -E "FALLA|FIN|Exception|at com\."
echo "$out" | grep -c "UP OK" | sed 's/^/OK: /'
echo "$out" | grep -q "fallos=0" && { echo "MEJORAS OK"; exit 0; } || { echo "MEJORAS FALLA"; exit 1; }
