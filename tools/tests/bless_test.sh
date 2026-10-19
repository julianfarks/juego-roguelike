#!/usr/bin/env bash
# Banco de pruebas de las 200 bendiciones (headless, sin hardware real). Una ejecucion de bot a la vez (nunca en paralelo).
# Uso: tools/tests/bless_test.sh [rapido]   (rapido = solo catalogo + sinergias + estres corto)
RUN=${RUN:-/tmp/run2.sh}; [ -x "$RUN" ] || RUN=PC/run.sh
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
fail=0
cls() { # compila core + clase de prueba (en /tmp) y la ejecuta
  OUT=/tmp/bless_test_$1; rm -rf "$OUT"; mkdir -p "$OUT"
  find Shared/src/main/java/com/julianfarks/roguelike/core -name '*.java' ! -name OggJorbis.java > "$OUT/s.txt"; echo "tools/tests/$1.java" >> "$OUT/s.txt"
  find PC/src/main/java -name '*.java' ! -name OggJorbis.java >> "$OUT/s.txt"
  javac --release 21 --enable-preview -encoding UTF-8 -nowarn -d "$OUT" @"$OUT/s.txt" 2>&1 | grep -v "^Note\|Picked up" ; java --enable-preview -cp "$OUT" com.julianfarks.roguelike.core.$1 2>&1 | grep -v "Picked up"; return ${PIPESTATUS[1]}; }
echo "== 1 reglas del catalogo (analizador real)"; cls BlessRuleCheck | tail -3 || fail=1
echo "== 2 catalogo: unicidad, iconos, rarezas, sinergias, traducciones, ofertas, guardado antiguo"; cls BlessCatalogTest | grep -E "FAIL|INFO|TODO|FALLOS" || true
cls BlessCatalogTest >/dev/null || fail=1
probe() { BOT_GOD=1 BOT_WARP=combat:0 BOT_BLESSTEST=$1 timeout 1500 $RUN --headless --bot --frames $2 2>&1 | grep -E "^BP|Exception|rror" ; }
echo "== 3 sinergias: activas con need, apagadas con need-1, con efecto real"
o=$(probe syn 12000); echo "$o" | grep -E "FALLA|FIN"; echo "$o" | grep -q "BP FIN ok=20 fallos=0" || fail=1
echo "== 4 estres: 200 bendiciones al maximo (limites y rendimiento)"
o=$(BOT_GOD=1 BOT_WARP=combat:0 BOT_BLESSTEST=stress BOT_BLESSFRAMES=${STRESS:-3000} timeout 900 $RUN --headless --bot --frames 5000 2>&1 | grep -E "^BPSTRESS|Exception|rror"); echo "$o"
echo "$o" | grep -q "BPSTRESS fin" || fail=1
# limites: dano de bendiciones <= x3 (x1,2 por maldito = 3,6), curacion por sala <= 25%, ejecuciones/s <= 90, invulnerabilidad < 25% del tiempo
echo "$o" | grep "BPSTRESS fin" | awk '{ for (i=1;i<=NF;i++) { split($i,a,"="); v[a[1]]=a[2]+0 } ok = (v["maxMultDanoModDamage"] <= 3.61 && v["maxCuracionSalaPct"] <= 25 && v["maxEjecucionesPorSeg"] <= 90 && v["invulnerable"] < 25); print (ok ? "ok   limites respetados" : "FALLA limites"); exit ok ? 0 : 1 }' || fail=1
echo "== 4b persistencia: cambio de sala/jefe/piso, guardar/cargar, partida antigua de 28 entradas"
o=$(BOT_GOD=1 BOT_WARP=combat:0 BOT_BLESSTEST=persist timeout 300 $RUN --headless --bot --frames 3000 2>&1 | grep -E "^BPPERSIST|Exception|rror"); echo "$o" | grep -E "FALLA|FIN"; echo "$o" | grep -q "FIN ok=9 fallos=0" || fail=1
echo "== 4c interfaz: cartas del altar y lista (todas las paginas) sin textos cortados, 4 idiomas a 480 px y 640 px"
for L in 0 1 2 3; do for W in 480 640; do o=$(BOT_LANG=$L BOT_GOD=1 BOT_WARP=combat:0 BOT_BLESSTEST=ui timeout 300 $RUN --headless --bot --w $W --frames 3000 2>&1 | grep -E "^FIT|^BPUI|Exception|rror" | sort -u); echo "$o" | grep -q "desajustes=0" && echo "  ok   idioma $L ancho $W" || { echo "  FALLA idioma $L ancho $W"; echo "$o" | head -5; fail=1; }; done; done
if [ "$1" != rapido ]; then
echo "== 5 cada bendicion por separado (efecto real con eventos del juego)"
o=$(probe single 90000); echo "$o" | grep -E "FALLA|FIN"; echo "$o" | grep -q "BP FIN ok=200 fallos=0" || fail=1
fi
[ $fail = 0 ] && echo "TODO OK" || { echo "HAY FALLOS"; exit 1; }
