#!/usr/bin/env bash
# Pruebas automaticas (banco headless, NO dispositivo real) del tutorial inicial: aparicion unica, guardado, migracion y maquetacion.
# Uso: tools/tests/tutorial_test.sh            -> logica (10 casos) + escenas touch/kb/pad en 480 y 640 de ancho, 4 idiomas
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
out=$(BOT_TUTTEST=1 BOT_GOD=1 BOT_WARP=combat:0 timeout 200 $RUN --headless --bot --frames 600 2>&1 | grep -E "^AT|Exception|at com\.")
echo "$out" | grep -E "FALLA|FIN|Exception|at com\."
echo "$out" | grep -c "AT OK" | sed 's/^/logica OK: /'
echo "$out" | grep -q "fallos=0" || fail=1
for mode in touch kb pad; do
  pc=""; [ "$mode" != "touch" ] && pc="--pc"
  for w in 480 640; do
    for lang in 0 1 2 3; do
      o=$(BOT_LANG=$lang BOT_TUTSCENE=$mode BOT_GOD=1 BOT_WARP=combat:0 timeout 120 $RUN --headless --bot $pc --w $w --frames 1000 2>&1 | grep -E "^AT|Exception|at com\.")
      r=$(echo "$o" | grep -E "FALLA|Exception|at com\.")
      echo "$o" | grep -q "fallos=0" && echo "escena $mode w=$w $lang: OK" || { echo "escena $mode w=$w $lang: FALLA"; echo "$r"; fail=1; }
    done
  done
done
[ $fail = 0 ] && { echo "TUTORIAL OK"; exit 0; } || { echo "TUTORIAL FALLA"; exit 1; }
