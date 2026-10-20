#!/usr/bin/env bash
# Pruebas (banco headless, NO dispositivo real) del vuelo de jefes voladores: Devorador del Vacio (boss:3) y Matriarca de Sangre (boss:6). La Reina de la Escarcha es terrestre desde 2026-10-20 (ver boss_ground_test.sh).
# El jugador recorre suelo -> todas las plataformas -> saltos bajo el jefe -> fase 2; en cada fotograma el jefe debe estar dentro de su banda de vuelo.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
for b in 3 6; do
  out=$(BOT_BOSSFLY=1 BOT_GOD=1 BOT_WARP=boss:$b timeout 280 $RUN --headless --bot --frames 9000 2>&1 | grep -E "^BF|Exception|at com\.")
  echo "$out" | grep -E "jefe=|FALLA|FIN|Exception|at com\."
  echo "$out" | grep -q "fallos=0" || fail=1
done
[ $fail = 0 ] && echo "VUELO JEFES OK" || echo "VUELO JEFES FALLA"
exit $fail
