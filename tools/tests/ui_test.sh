#!/usr/bin/env bash
# Pruebas (banco headless, NO dispositivo real) de la actualizacion de interfaz: seleccion directa de armas, controles tactiles sin solapes,
# pausa sin accesos redundantes y boton contextual de interaccion. Tactil y PC (--pc: clic/teclado) x 480/568/640 x alturas 270/320 x 4 idiomas.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
run() { # modo ancho alto idioma
  local pc=""; [ "$1" = pc ] && pc="--pc"
  local o; o=$(BOT_LANG=$4 BOT_UISCENE=1 BOT_GOD=1 BOT_WARP=combat:0 timeout 200 $RUN --headless --bot $pc --w $2 --h $3 --frames 1300 2>&1 | grep -E "^AT|Exception|at com\.")
  if echo "$o" | grep -q "fallos=0"; then echo "ui $1 ${2}x$3 lang=$4: OK ($(echo "$o" | grep -c 'AT OK') comprobaciones)"
  else echo "ui $1 ${2}x$3 lang=$4: FALLA"; echo "$o" | grep -E "FALLA|Exception|at com\.|ENCAJE" | head -8; fail=1; fi
}
for mode in touch pc; do
  for dim in "480 270" "568 288" "640 270" "640 320" "480 320"; do
    set -- $dim; run $mode $1 $2 0
  done
done
for lang in 1 2 3; do run touch 480 270 $lang; run pc 640 288 $lang; done
[ $fail = 0 ] && { echo "UI OK"; exit 0; } || { echo "UI FALLA"; exit 1; }
