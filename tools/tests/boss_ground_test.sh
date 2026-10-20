#!/usr/bin/env bash
# Pruebas (banco headless, NO dispositivo real) del combate terrestre de la Reina de la Escarcha (boss:2), con 3 semillas.
# Suelo -> plataformas -> saltos junto a ella -> fase 2 -> dano real: nunca vuela, nunca flota, nunca dentro de un bloque; sigue atacando y haciendo dano.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
for s in 4242 7 99; do
  out=$(BOT_SEED=$s BOT_BOSSGROUND=1 BOT_GOD=1 BOT_WARP=boss:2 timeout 400 $RUN --headless --bot --frames 12000 2>&1 | grep -E "^BG|Exception|at com\.")
  echo "$out" | grep -E "FALLA|FIN|Exception|at com\." | sed "s/^/semilla $s: /"
  echo "$out" | grep -q "FIN ok=.* fallos=0" || fail=1
done
[ $fail = 0 ] && echo "JEFE HIELO OK" || echo "JEFE HIELO FALLA"
exit $fail
