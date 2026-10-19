#!/usr/bin/env bash
# Pruebas automaticas (banco headless, sin hardware real) del tacto de combate: pausas de impacto, golpes diferenciados,
# parry/esquiva perfectos, ventana de contraataque, racha defensiva, pulsaciones durante la pausa y jefe sin interrupciones.
# Un modo por ejecucion (nunca en paralelo). Sale con 1 si algun chequeo falla.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
for m in "impact combat:0" "input combat:0" "parry combat:0" "impact boss:0"; do
  set -- $m
  echo "== $1 ($2)"
  out=$(BOT_COMBATTEST=$1 BOT_GOD=1 BOT_WARP=$2 timeout 300 $RUN --headless --bot --frames 2400 2>&1 | grep -E "^CT")
  echo "$out" | grep -E "FALLA|FIN|OK +jefe"
  if echo "$out" | grep -q "CT FIN"; then echo "$out" | grep -q "fallos=0" || fail=1
  else echo "$out" | grep -q "CT FALLA" && fail=1; echo "$out" | grep -q "CT OK" || fail=1; fi
done
[ $fail = 0 ] && echo "COMBATE OK" || echo "COMBATE FALLA"
exit $fail
