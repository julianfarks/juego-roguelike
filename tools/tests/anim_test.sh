#!/usr/bin/env bash
# Pruebas (banco headless, NO dispositivo real) de animacion de combate: smear frames, pesos de duracion, contacto real, pose de impacto, presupuesto de sonido.
# Ademas comprueba que las hojas nuevas conservan EXACTAMENTE los fotogramas originales (solo se anadio el smear) y las cajas de golpe.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
python3 tools/tests/anim_sheets_check.py || fail=1
out=$(BOT_ANIMTEST=1 BOT_GOD=1 BOT_WARP=combat:0 timeout 300 $RUN --headless --bot --frames 900 2>&1 | grep -E "^AN|Exception|at com\.")
echo "$out" | grep -E "FALLA|FIN|Exception|at com\."
echo "$out" | grep -q "fallos=0" || fail=1
[ $fail = 0 ] && echo "ANIM OK" || echo "ANIM FALLA"
exit $fail
