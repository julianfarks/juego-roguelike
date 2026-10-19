#!/usr/bin/env bash
# Pruebas automaticas (banco headless, NO dispositivo real) del Arsenal: armas secundarias, cambio, suelo, cofres, guardado.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
out=$(BOT_ARSENAL=1 BOT_GOD=1 BOT_WARP=combat:0 timeout 300 $RUN --headless --bot --frames 1200 2>&1 | grep -E "^AT|Exception|at com\.")
echo "$out" | grep -E "FALLA|FIN|Exception|at com\."
echo "$out" | grep -c "AT OK" | sed 's/^/OK: /'
echo "$out" | grep -q "fallos=0" && { echo "ARSENAL OK"; exit 0; } || { echo "ARSENAL FALLA"; exit 1; }
