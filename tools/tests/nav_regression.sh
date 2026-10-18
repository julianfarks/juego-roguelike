#!/usr/bin/env bash
# Regresion: moverse por el salon de operaciones y por la preparacion NO debe abrir pantallas solas.
# La coleccion (CodexScr) solo se abre al pulsar Aceptar sobre su estacion. Ejecuta el banco de pruebas de escritorio.
set -u
cd "$(dirname "$0")/../.."
RUN=/tmp/run2.sh; [ -x "$RUN" ] || RUN=PC/run.sh
S=/tmp/nav_test.script; : > $S
f=40
k() { echo "$f key $1 down" >> $S; echo "$((f+3)) key $1 up" >> $S; f=$((f+${2:-12})); }
# 1) recorrer todo el salon a la derecha y a la izquierda (teclado), sin aceptar
for i in $(seq 1 14); do k 39; done
for i in $(seq 1 14); do k 37; done
# 2) arriba/abajo y mantener pulsada la flecha derecha con repeticion automatica
k 38; k 40
echo "$f key 39 down" >> $S; for i in $(seq 1 20); do echo "$((f+i*2)) key 39 down" >> $S; done; echo "$((f+60)) key 39 up" >> $S; f=$((f+80))
# 3) abrir y cerrar la coleccion 3 veces de forma intencionada (Aceptar sobre la estacion y Esc)
for i in 1 2 3; do
  for j in $(seq 1 14); do k 37 6; done          # al principio
  for j in 1 2 3 4 5 6 7; do k 39 6; done        # hasta la Coleccion (indice 7)
  k 10 50; k 27 60                                # abrir / cerrar
  for j in 1 2 3; do k 39 12; done                 # seguir moviendo a la derecha: no debe reabrirse
done
echo "$((f+30)) shot s_final" >> $S
OUT=/tmp/nav_test.log
BOT_NAVLOG=1 BOT_SHOW=ops BOT_NOSTART=1 timeout 600 $RUN --headless --bot --w 480 --frames $((f+60)) --script $S --shots /tmp/nav_test_shots --store /tmp/nav_test_store.json > $OUT 2>&1
fails=0
chk() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1 (esperado $3, fue $2)"; fails=$((fails+1)); fi; }
codex=$(grep -c "NAV .* CodexScr" $OUT)
chk "la coleccion se abre solo las 3 veces pedidas" "$codex" 3
chk "sin excepciones" "$(grep -c EXCEPTION $OUT)" 0
other=$(grep "^NAV" $OUT | grep -v " Ops$\| CodexScr$\| Title$\| Boot$\| LoadScreen$" | wc -l)
chk "ninguna otra pantalla se abre sola" "$other" 0
# tras cada cierre se vuelve al salon
seq=$(grep "^NAV" $OUT | awk '{print $3}' | tr '\n' ' ')
echo "secuencia: $seq"
case "$seq" in *"CodexScr Ops CodexScr Ops CodexScr Ops "*) echo "ok   al cerrar la coleccion se vuelve al salon"; ;; *) echo "FAIL al cerrar la coleccion se vuelve al salon"; fails=$((fails+1));; esac

# ---- Parte 2: preparacion. Moverse en todas direcciones (y mantener pulsado) no activa nada: ni lanza la run ni abre pantallas.
S2=/tmp/nav_prep.script; : > $S2; f=40
k2() { echo "$f key $1 down" >> $S2; echo "$((f+3)) key $1 up" >> $S2; f=$((f+${2:-10})); }
for i in $(seq 1 25); do k2 39; done; for i in $(seq 1 25); do k2 37; done
for i in 1 2 3 4 5; do k2 38; k2 40; done
for c in 65 68 65 68; do k2 $c; done
echo "$f key 39 down" >> $S2; for i in $(seq 1 30); do echo "$((f+i*2)) key 39 down" >> $S2; done; echo "$((f+70)) key 39 up" >> $S2; f=$((f+90))
echo "$f shot s_prep_after" >> $S2
OUT2=/tmp/nav_prep.log
BOT_NAVLOG=1 BOT_SHOW=prep:0:0:1:2:0:-1 BOT_NOSTART=1 timeout 600 $RUN --headless --bot --w 480 --frames $((f+60)) --script $S2 --shots /tmp/nav_prep_shots --store /tmp/nav_prep_store.json > $OUT2 2>&1
chk "preparacion: sin excepciones" "$(grep -c EXCEPTION $OUT2)" 0
chk "preparacion: ninguna pantalla se abre por moverse" "$(grep '^NAV' $OUT2 | grep -v ' PrepScreen$\| Ops$\| Title$\| Boot$\| LoadScreen$' | wc -l)" 0
chk "preparacion: la run no se lanza al mover" "$(grep -c 'NAV .* RunScreen\|NAV .* Cinematic' $OUT2)" 0
cls=$(grep -c '^PREPCLS' $OUT2)
if [ "$cls" -gt 1 ]; then echo "ok   preparacion: izquierda/derecha solo cambia de personaje ($cls cambios)"; else echo "FAIL preparacion: el personaje no cambia al mover"; fails=$((fails+1)); fi
[ $fails -eq 0 ] && echo "nav_regression OK" || echo "nav_regression FALLOS: $fails"
exit $fails
