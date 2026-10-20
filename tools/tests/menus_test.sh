#!/usr/bin/env bash
# Pruebas (banco headless, NO dispositivo real) del inventario rediseñado: pestañas, todos los elementos (200 bendiciones, reliquias, pactos, armas, objetos),
# recortes de fichas de arma, desplazamiento del detalle, equipar desde el inventario, teclas, regreso a la pausa y mundo en pausa. 3 resoluciones x 3 idiomas.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
for cfg in "480 270 0" "568 288 1" "640 320 3" "480 320 2"; do
  set -- $cfg
  o=$(BOT_LANG=$3 BOT_INVTEST=1 BOT_GOD=1 BOT_TXTSCREENS=1 timeout 500 $RUN --headless --bot --w $1 --h $2 --frames 1700 2>&1 | grep -E "^INVTEST (OK|FALLA|resumen)|Exception")
  if echo "$o" | grep -q "resumen: fallos=0" && ! echo "$o" | grep -q "FALLA\|Exception"; then echo "inventario ${1}x$2 lang=$3: OK ($(echo "$o" | grep -c 'INVTEST OK') comprobaciones)"
  else echo "inventario ${1}x$2 lang=$3: FALLA"; echo "$o" | grep -E "FALLA|Exception" | head -5; fail=1; fi
done
[ $fail = 0 ] && { echo "MENUS OK"; exit 0; } || { echo "MENUS FALLA"; exit 1; }
