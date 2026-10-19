#!/usr/bin/env bash
# Pruebas automaticas (banco headless, sin hardware real) del HUD de combate: tiempos de reutilizacion y senal de "lista",
# botones fijos, senales de sinergia sin repeticion (y por tipo), estados, y textos del HUD sin cortes en 4 idiomas x 480/640
# (con vida baja, jefe, desafio y recursos grandes). Un modo por ejecucion (nunca en paralelo). Sale con 1 si algo falla.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
for m in cd syn status; do
  echo "== $m"; out=$(BOT_HUDTEST=$m BOT_GOD=1 BOT_WARP=combat:0 timeout 300 $RUN --headless --bot --frames 1500 2>&1 | grep -E "^HUD")
  echo "$out" | grep -E "FALLA|FIN"; echo "$out" | grep -q "fallos=0" || fail=1
done
echo "== textos (4 idiomas x 480/640, sala y jefe)"
for W in 480 640; do for L in 0 1 2 3; do for WARP in combat:0 boss:0; do
  o=$(BOT_LANG=$L BOT_HUDTEST=ui BOT_GOD=1 BOT_WARP=$WARP timeout 300 $RUN --headless --bot --w $W --frames 900 2>&1 | grep -E "^FIT|^HUD FIN")
  echo "$o" | grep -q "desajustes=0" && echo "  ok   idioma $L ancho $W $WARP" || { echo "  FALLA idioma $L ancho $W $WARP"; echo "$o" | head -3; fail=1; }
done; done; done
[ $fail = 0 ] && echo "HUD OK" || echo "HUD FALLA"
exit $fail
