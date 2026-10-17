#!/usr/bin/env bash
# Musica de menus: titulo/salon/preparacion/tienda/coleccion... usan UNA sola pista (mus_menu) sin repetir ni reiniciar;
# al empezar la run vuelve la musica original de partida; al volver al menu regresa mus_menu. Los efectos no se tocan.
set -u
cd "$(dirname "$0")/../.."
RUN=/tmp/run2.sh; [ -x "$RUN" ] || RUN=tools/desktop/run.sh
fails=0; chk() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1 (esperado '$3', fue '$2')"; fails=$((fails+1)); fi; }
# 1) recorrer todos los menus
L=/tmp/menu_music1.log
BOT_SHOW=title,lang,ops,class,prep,shop,sanct,stats,trophy,options,codes,controls,story,comp,garden,codex,retos,ops,prep,title BOT_NOSTART=1 timeout 600 $RUN --headless --bot --w 480 --frames 1300 --audio-log --store /tmp/menu_music1.json > $L 2>&1
chk "sin excepciones (menus)" "$(grep -c EXCEPTION $L)" 0
seq=$(grep -o "music [a-z_0-9]*" $L | awk '{print $2}' | tr '\n' ' ')
echo "musica en menus: $seq"
chk "en todos los menus solo se pide mus_menu, una vez (sin reinicios ni duplicados)" "$seq" "mus_menu "
chk "no falta el archivo de audio" "$(grep -c 'MISSING audio: music/mus_menu' $L)" 0
# 2) partida: menu -> run (musica original) 
L2=/tmp/menu_music2.log
timeout 900 $RUN --headless --bot --w 480 --frames 2500 --audio-log --store /tmp/menu_music2.json > $L2 2>&1
chk "sin excepciones (partida)" "$(grep -c EXCEPTION $L2)" 0
seq2=$(grep -o "music [a-z_0-9]*" $L2 | awk '{print $2}' | head -3 | tr '\n' ' ')
echo "musica en partida: $seq2"
first=$(echo $seq2 | awk '{print $1}'); second=$(echo $seq2 | awk '{print $2}')
chk "primero suena mus_menu" "$first" mus_menu
case "$second" in mus_menu|"") echo "FAIL al empezar la run no cambia a la musica de partida (fue '$second')"; fails=$((fails+1));; *) echo "ok   al empezar la run suena la musica original de partida ($second)";; esac
# 2b) volver de la partida al menu: regresa mus_menu una sola vez
L3=/tmp/menu_music3.log
BOT_TOOPS=700 BOT_NAVLOG=1 timeout 900 $RUN --headless --bot --w 480 --frames 1200 --audio-log --store /tmp/menu_music3.json > $L3 2>&1
seq3=$(grep -o "music [a-z_0-9]*" $L3 | awk '{print $2}' | tr '\n' ' ')
echo "musica partida->menu: $seq3"
pre=$(echo $seq3 | awk '{print $1" "$3}'); chk "al volver al menu suena mus_menu justo despues de la musica de partida (el bot reinicia otra run despues)" "$pre" "mus_menu mus_menu"; chk "entre medias solo la musica de partida" "$(echo $seq3 | awk '{print ($2 != "mus_menu" && $2 != "") ? "ok" : "no"}')" ok
# 3) los efectos de sonido siguen igual: el manifiesto de sfx y los .ogg de sfx no cambian respecto a git
chk "efectos de sonido sin modificar (git)" "$(git status --porcelain app/src/main/assets/audio/sfx | wc -l)" 0
chk "sfx del manifiesto intactos" "$(git diff HEAD -- app/src/main/assets/audio/manifest.json | grep '^[-+]' | grep -v '^+++\|^---' | grep -vc 'mus_menu\|"dur": 178.4\|"loop": true\|^+},\|^+$')" 0
chk "efectos suenan con la musica (sfx registrados en la partida)" "$([ "$(grep -c '^sfx\|sfx ' $L2)" -gt 20 ] && echo si || echo no)" si
[ $fails -eq 0 ] && echo "menu_music OK" || echo "menu_music FALLOS: $fails"
exit $fails
