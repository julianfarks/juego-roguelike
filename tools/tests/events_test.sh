#!/usr/bin/env bash
# Pruebas automaticas (banco headless, sin hardware real) de los sucesos de riesgo: altar de riesgo, cofre maldito, salas de desafio,
# reparto/variedad, ruta (entrar/salir sin saltar contenido), guardado/carga y textos sin cortes en 4 idiomas x 2 anchos.
# Un modo por ejecucion (nunca en paralelo). Sale con 1 si algo falla.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
run() { # modo warp [env extra]
  env $3 BOT_EVENTTEST=$1 BOT_GOD=1 BOT_WARP=$2 timeout 300 $RUN --headless --bot --frames 400 2>&1 | grep -E "^EV"; }
chk() { out=$(run "$@"); echo "== $1 ($2 $3)"; echo "$out" | grep -E "FALLA|FIN"; echo "$out" | grep -q "fallos=0" || fail=1; }
chk altar ev7:0
chk cursed ev8:0
chk chal ev9:0
chk roll ev7:0
chk save ev9:0
for k in 7 8 9; do chk nav combat:0 BOT_EVENT=$k; done
echo "== merchant_test (mercader sin romper el piso)"; tools/tests/merchant_test.sh | tail -1 || fail=1
echo "== textos (4 idiomas x 480/640)"
for L in 0 1 2 3; do for W in 480 640; do
  o=$(BOT_LANG=$L BOT_EVENTTEST=ui BOT_GOD=1 BOT_WARP=combat:0 timeout 300 $RUN --headless --bot --w $W --frames 400 2>&1 | grep -E "^FIT|^EVUI")
  echo "$o" | grep -q "desajustes=0" && echo "  ok   idioma $L ancho $W" || { echo "  FALLA idioma $L ancho $W"; echo "$o" | head -3; fail=1; }
done; done
[ $fail = 0 ] && echo "SUCESOS OK" || echo "SUCESOS FALLA"
exit $fail
