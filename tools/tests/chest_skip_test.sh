#!/usr/bin/env bash
# Pruebas (banco headless, NO dispositivo real) del cofre con «Omitir»: abrir con interactuar, omitir con un toque real, el cofre sigue
# con las mismas ofertas, reabrir varias veces sin botin repetido, elegir y que se consuma; botones (Elegir centrado, Omitir abajo a la
# derecha, separados, sin invadir las cartas) en 4 resoluciones y 8 semillas.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
for cfg in "480 270" "568 288" "640 320" "480 320"; do
  set -- $cfg
  for s in 1 3 6 9 11 14 17 20; do
    o=$(BOT_SEED=$s BOT_CHESTFLOW=1 BOT_GOD=1 BOT_WARP=combat:$((s % 9)) timeout 300 $RUN --headless --bot --w $1 --h $2 --frames 1500 2>&1 | grep -E "^CF (FALLA|FIN)|Exception")
    echo "$o" | grep -q "FIN ok=.* fallos=0" || { echo "cofre ${1}x$2 semilla $s: FALLA"; echo "$o" | head -3; fail=1; }
  done
  [ $fail = 0 ] && echo "cofre ${1}x$2: OK (8 semillas)"
done
[ $fail = 0 ] && { echo "COFRE OMITIR OK"; exit 0; } || { echo "COFRE OMITIR FALLA"; exit 1; }
