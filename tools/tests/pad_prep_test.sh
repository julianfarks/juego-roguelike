#!/usr/bin/env bash
# Preparacion con mando: confirmar espadachin NO inicia; secuencia completa espadachin->bendicion->dificultad->opciones->COMENZAR.
# Los botones del mando entran como codigos virtuales (Pad.*) igual que desde PcXInput/Android.
set -u
cd "$(dirname "$0")/../.."
RUN=/tmp/run2.sh; [ -x "$RUN" ] || RUN=PC/run.sh
A=1000; DU=1012; DD=1013; DL=1014; DR=1015
S=/tmp/pad_prep.script; : > $S; f=60
k() { echo "$f key $1 down" >> $S; echo "$((f+3)) key $1 up" >> $S; f=$((f+${2:-15})); }
k $DR            # cambiar personaje
k $DR
k $A 30          # confirmar personaje (NO debe empezar)
k $DR            # bendicion: tarjeta 2
k $A 30          # elegir bendicion
k $DL            # dificultad: Normal -> Facil
k $DL            # (ya en Facil: queda)
k $DR; k $DR     # -> Dificil
k $A 30          # pasar a otras opciones
k $DR; k $DR; k $DL   # recorrer opciones (Modo, Retos, Companero)
echo "$f shot s_before_start" >> $S; f=$((f+10))
k $DD; k $DD 30  # bajar hasta COMENZAR
echo "$f shot s_on_start" >> $S
echo "$f key $A down" >> $S; for i in 1 2 3 4 5 6; do echo "$((f+i*3)) key $A down" >> $S; done; echo "$((f+25)) key $A up" >> $S   # A mantenida: una sola vez
f=$((f+200))
OUT=/tmp/pad_prep.log
BOT_NAVLOG=1 BOT_SHOW=prep BOT_NOSTART=1 BOT_CLASS=0 timeout 600 $RUN --headless --bot --w 480 --frames $f --script $S --shots /tmp/pad_prep_shots --store /tmp/pad_prep_store.json > $OUT 2>&1
grep -E "^(PREP|NAV)" $OUT
fails=0
chk() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1 (esperado $3, fue $2)"; fails=$((fails+1)); fi; }
l=$(grep "^PREP" $OUT)
chk "sin excepciones" "$(grep -c EXCEPTION $OUT)" 0
chk "tras confirmar personaje sigue en preparacion (fila bendicion, sin launch)" "$(echo "$l" | grep -c 'row=1 .*launch=false')" "$(echo "$l" | grep -c 'row=1 .*launch=false')"
echo "$l" | grep -q "row=1.*launch=false" && echo "ok   A en personaje -> fila bendicion sin iniciar" || { echo "FAIL A en personaje no paso a bendicion"; fails=$((fails+1)); }
echo "$l" | grep -q "row=2 bCur=1.*bless=" && echo "ok   bendicion elegida y conservada" || { echo "FAIL bendicion"; fails=$((fails+1)); }
echo "$l" | grep -q "row=3.*diff=2.*launch=false" && echo "ok   dificultad Dificil aplicada, opciones accesibles" || { echo "FAIL dificultad/opciones"; fails=$((fails+1)); }
echo "$l" | grep -q "row=4.*launch=false" && echo "ok   llegado a COMENZAR sin iniciar" || { echo "FAIL fila COMENZAR"; fails=$((fails+1)); }
echo "$l" | grep -q "launch=true" && echo "ok   COMENZAR inicia" || { echo "FAIL COMENZAR no inicia"; fails=$((fails+1)); }
chk "COMENZAR lanza una sola vez (A mantenida)" "$(grep -c 'NAV .*\(Cinematic\|RunScreen\)' $OUT)" 1
# --- teclado: Enter sobre el personaje no inicia; flechas/Enter recorren; tocar COMENZAR (raton/tactil) inicia
S2=/tmp/pad_prep2.script; : > $S2; f=60
k2() { echo "$f key $1 down" >> $S2; echo "$((f+3)) key $1 up" >> $S2; f=$((f+${2:-15})); }
rm -f /tmp/pad_prep_store.json
k2 39; k2 10 30; k2 10 30; k2 37; k2 37; k2 40; k2 40 30
echo "$f tap 330 258" >> $S2; f=$((f+200))
OUT2=/tmp/pad_prep2.log
BOT_NAVLOG=1 BOT_SHOW=prep BOT_NOSTART=1 BOT_CLASS=0 timeout 600 $RUN --headless --bot --w 480 --frames $f --script $S2 --shots /tmp/pad_prep_shots --store /tmp/pad_prep_store.json > $OUT2 2>&1
echo "--- teclado/raton"; grep -E "^(PREP |NAV)" $OUT2
l2=$(grep '^PREP' $OUT2)
echo "$l2" | grep -q "row=1.*launch=false" && echo "ok   Enter en personaje no inicia (teclado)" || { echo "FAIL teclado"; fails=$((fails+1)); }
echo "$l2" | grep -q "diff=0.*launch=false" && echo "ok   dificultad por teclado" || { echo "FAIL dificultad teclado"; fails=$((fails+1)); }
chk "tocar COMENZAR inicia una vez" "$(echo "$l2" | grep -c 'launch=true')" 1
echo "fallos: $fails"; exit $fails
