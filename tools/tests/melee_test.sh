#!/usr/bin/env bash
# Pruebas (banco headless, NO dispositivo real) del cuerpo a cuerpo: arma principal de 5 clases y las 13 armas secundarias cuerpo a cuerpo,
# maniqui a -8..80 px quieto y corriendo; pared de por medio, enemigo en movimiento, giro rapido, enemigo detras y sin impactos duplicados.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
# a -8..20 px (pegado o solapado) todo golpe debe acertar
chk() { echo "$1" | grep -E "^MELEE .*\|" | while read -r l; do r=$(echo "$l" | sed 's/.*|\(.*\)|/\1/'); case "${r:0:8}" in *.*) echo "FALLO CERCA: $l";; esac; done; }
out=$(BOT_MELEETEST=1 BOT_GOD=1 BOT_CLASS=0 BOT_WARP=combat:0 timeout 1500 $RUN --headless --bot --frames 21000 2>&1 | grep -E "^MELEE|Exception|at com\.")
echo "$out" | grep -E "\||FALLA|resumen|Exception"
c=$(chk "$out"); [ -n "$c" ] && { echo "$c"; fail=1; }
echo "$out" | grep -q "resumen fallos=0" || fail=1
for cl in 1 3 7 9; do
  o=$(BOT_MELEETEST=1 BOT_GOD=1 BOT_CLASS=$cl BOT_WARP=combat:0 timeout 400 $RUN --headless --bot --frames 1900 2>&1 | grep -E "^MELEE principal|Exception")
  echo "$o" | sed "s/^/clase $cl: /"; c=$(chk "$o"); [ -n "$c" ] && { echo "$c"; fail=1; }
done
[ $fail = 0 ] && echo "CUERPO A CUERPO OK" || echo "CUERPO A CUERPO FALLA"
exit $fail
