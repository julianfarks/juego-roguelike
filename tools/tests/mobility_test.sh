#!/usr/bin/env bash
# Pruebas (banco headless, NO dispositivo real): rodada por huecos estrechos y colocacion validada de cofres.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
o=$(BOT_ROLLGAP=1 BOT_GOD=1 timeout 400 $RUN --headless --bot --frames 1900 2>&1 | grep -E "^ROLLGAP (OK|FALLA|resumen)")
echo "$o" | grep -q "fallos=0 frames dentro de un bloque=0" && echo "rodada: OK ($(echo "$o" | grep -c 'ROLLGAP OK') escenarios)" || { echo "rodada: FALLA"; echo "$o" | grep FALLA; fail=1; }
o=$(BOT_CHESTPOS=1 timeout 400 $RUN --headless --bot --frames 900 2>&1 | grep "^CHESTPOS")
echo "$o" | grep -q "nuevo invalido=0 ultimo recurso=0 forzado=0 solapados=0" && echo "cofres: OK ($o)" || { echo "cofres: FALLA $o"; fail=1; }
[ $fail = 0 ] && { echo "MOVILIDAD OK"; exit 0; } || { echo "MOVILIDAD FALLA"; exit 1; }
