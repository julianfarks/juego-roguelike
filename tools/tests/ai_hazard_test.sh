#!/usr/bin/env bash
# Prueba de IA ante peligros (pinchos, fosos, puentes) con enemigos REALES en una zona construida de la sala (banco headless, sin hardware real).
# Un escenario por ejecucion (nunca en paralelo). Falla (exit 1) si algun enemigo se mata en pinchos, no persigue, se queda sin ruta valida o el pincho no daña en contacto real.
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
run() { # escenario ids frames
  BOT_GOD=1 BOT_WARP=combat:0 BOT_AITEST=$1:$2 BOT_AIFRAMES=$3 timeout 300 $RUN --headless --bot --frames $(($3+500)) 2>&1 | grep -E "^AIT $1 " ; }
chk() { # nombre condicion(awk sobre TOTAL) salida
  if [ "$2" = ok ]; then echo "  OK   $1"; else echo "  FALLA $1  -> $3"; fail=1; fi; }
val() { echo "$1" | sed -E "s/.*[ ]$2=([0-9]+).*/\1/"; }
echo "== 1 pinchos entre enemigo y jugador (tira de 3): ningun tipo muere"
for e in esqueleto zombi escudero_hueso bruto_forja lobo_musgo carbonero_forja caballero_osario cubo_magma arana; do
  o=$(run strip3 $e 700); t=$(echo "$o" | grep TOTAL); th=$(val "$t" trapHits)
  [ "${th:-9}" = 0 ] && chk "strip3 $e" ok || chk "strip3 $e" bad "$t"
done
echo "== 2 tira ancha de 8 / 3 foso con pinchos: se detiene antes"
for s in strip8 pit; do o=$(run $s esqueleto 600); t=$(echo "$o" | grep TOTAL); [ "$(val "$t" trapHits)" = 0 ] && echo "$o" | grep -q "alive=true" && chk "$s esqueleto" ok || chk "$s esqueleto" bad "$o"; done
echo "== 3 ruta alternativa segura (puente) y salto de 1 pincho si el tipo puede"
o=$(run bridge esqueleto 600); t=$(echo "$o" | grep TOTAL); d=$(echo "$o" | grep "id=esqueleto" | sed -E 's/.*minDistPlayer=([0-9]+).*/\1/')
[ "$(val "$t" trapHits)" = 0 ] && [ "${d:-999}" -le 30 ] && chk "bridge esqueleto llega al jugador (dist $d)" ok || chk "bridge" bad "$o"
o=$(run strip1 esqueleto 600); t=$(echo "$o" | grep TOTAL)
[ "$(val "$t" trapHits)" = 0 ] && [ "$(val "$t" hops)" -ge 1 ] && [ "$(val "$t" playerHits)" -ge 1 ] && chk "strip1 salta el pincho y ataca" ok || chk "strip1" bad "$o"
o=$(run strip1 carbonero_forja,lobo_musgo 600); t=$(echo "$o" | grep TOTAL)
[ "$(val "$t" trapHits)" = 0 ] && chk "strip1 exploder+pouncer" ok || chk "strip1 exploder+pouncer" bad "$o"
echo "== 4 sin pinchos sigue persiguiendo y atacando"
for s in safe ledge; do o=$(run $s esqueleto 600); t=$(echo "$o" | grep TOTAL); [ "$(val "$t" playerHits)" -ge 1 ] && chk "$s ataca" ok || chk "$s" bad "$o"; done
o=$(run strip3 arquero_hueso 600); t=$(echo "$o" | grep TOTAL); [ "$(val "$t" playerHits)" -ge 1 ] && chk "arquero dispara desde el borde" ok || chk "arquero" bad "$o"
echo "== 5 sin bucles: giros por enemigo <= 12 (un solo enemigo)"
for e in esqueleto zombi lobo_musgo; do o=$(run strip3 $e 900); f=$(echo "$o" | grep "id=$e" | sed -E 's/.*flips=([0-9]+).*/\1/'); [ "${f:-99}" -le 12 ] && chk "flips $e=$f" ok || chk "flips $e" bad "$o"; done
echo "== 6 varios enemigos juntos (empujones entre ellos no los meten en pinchos)"
o=$(run strip3 esqueleto,zombi,lobo_musgo,carbonero_forja,bruto_forja 700); t=$(echo "$o" | grep TOTAL); [ "$(val "$t" trapHits)" = 0 ] && chk "multitud" ok || chk "multitud" bad "$o"
echo "== 7 el pincho SIGUE dañando en contacto real"
o=$(run contact esqueleto,zombi 500); t=$(echo "$o" | grep TOTAL); [ "$(val "$t" trapHits)" -ge 2 ] && chk "contacto daña a enemigos" ok || chk "contacto" bad "$o"
[ $fail = 0 ] && echo "RESULTADO: TODO OK" || { echo "RESULTADO: HAY FALLOS"; exit 1; }
