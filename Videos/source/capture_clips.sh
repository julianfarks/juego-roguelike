#!/usr/bin/env bash
# Graba las escenas de gameplay REAL de la version actual (modo PC limpio: sin controles tactiles ni elementos de depuracion), 1920x1080, 60 fps.
# Cada escena se graba DOS veces con la misma semilla (BOT_SEED): con el juego en espanol (clips/es) y en ingles (clips/en). Con la semilla fija
# la partida es identica en los dos idiomas (se comprueba comparando el registro de sonidos), asi los dos trailers muestran las mismas jugadas.
# Uso: bash Videos/source/capture_clips.sh [carpeta_salida]     (secuencial: nunca dos grabaciones a la vez)
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/Videos/source/clips}"
rec() {  # LANG NOMBRE FOTOGRAMAS VARIABLES...
  local L=$1 N=$2 F=$3; shift 3
  local D="$OUT/$L"; mkdir -p "$D"
  [ -f "$D/$N.mp4" ] && return 0
  local LG=0; [ "$L" = en ] && LG=1
  ( cd "$ROOT" && env BOT_SEED=${SEED:-4242} BOT_LANG=$LG BOT_GOD=1 "$@" SWR_OUT=/tmp/swr_build_trailer \
    bash PC/run.sh --headless --pc --bot --w 480 --frames $F --store "/tmp/trailer_store_${L}_$N" \
    --record "$D/$N.mp4" --rec-from 140 --rec-to $F > "$D/$N.log" 2>&1 ) || echo "FALLO $L $N"
  echo "$(date +%T) $L $N"
}
all() {
  for L in es en; do
    # ambiente (salas sin enemigos)
    rec $L i_cat 900 BOT_TRAILER=calm BOT_CLASS=0 BOT_WARP=bless:0
    rec $L i_eclipse 900 BOT_TRAILER=calm BOT_CLASS=8 BOT_WARP=bless:7
    rec $L i_forge 900 BOT_TRAILER=calm BOT_CLASS=2 BOT_WARP=forge:1
    rec $L i_still 1000 BOT_TRAILER=still BOT_CLASS=8 BOT_WARP=bless:7
    rec $L i_s0 900 BOT_TRAILER=still BOT_CLASS=0 BOT_WARP=bless:0
    rec $L i_s4 900 BOT_TRAILER=still BOT_CLASS=5 BOT_WARP=bless:4
    # combate por biomas (clase distinta en cada uno)
    rec $L c0 1000 BOT_ULT=1 BOT_CLASS=1 BOT_WARP=combat:0
    rec $L c1 1000 BOT_ULT=1 BOT_CLASS=2 BOT_WARP=combat:1
    rec $L c2 1000 BOT_ULT=1 BOT_CLASS=4 BOT_WARP=combat:2
    rec $L c3 1000 BOT_ULT=1 BOT_CLASS=8 BOT_WARP=combat:3
    rec $L c4 1000 BOT_ULT=1 BOT_CLASS=5 BOT_WARP=combat:4
    rec $L c5 1000 BOT_ULT=1 BOT_CLASS=3 BOT_WARP=combat:5
    rec $L c6 1000 BOT_ULT=1 BOT_CLASS=6 BOT_WARP=combat:6
    rec $L c7 1000 BOT_ULT=1 BOT_CLASS=9 BOT_WARP=combat:7
    rec $L e1 1100 BOT_ULT=1 BOT_CLASS=0 BOT_WARP=elite:1
    rec $L e5 1100 BOT_ULT=1 BOT_CLASS=7 BOT_WARP=elite:5
    # jefes
    rec $L b0 1300 BOT_ULT=1 BOT_CLASS=0 BOT_WARP=boss:0
    rec $L b1 1300 BOT_ULT=1 BOT_CLASS=2 BOT_WARP=boss:1
    rec $L b2 1300 BOT_ULT=1 BOT_CLASS=4 BOT_WARP=boss:2
    rec $L b3 1300 BOT_ULT=1 BOT_CLASS=1 BOT_WARP=boss:3
    rec $L b4 1300 BOT_ULT=1 BOT_CLASS=5 BOT_WARP=boss:4
    rec $L b5 1300 BOT_ULT=1 BOT_CLASS=3 BOT_WARP=boss:5
    rec $L b6 1300 BOT_ULT=1 BOT_CLASS=6 BOT_WARP=boss:6
    rec $L b7 1300 BOT_ULT=1 BOT_CLASS=7 BOT_WARP=boss:7
    rec $L b8 1400 BOT_ULT=1 BOT_CLASS=8 BOT_WARP=boss:8
    # escenas con TrailerProbe (solo coloca la situacion; pantallas y reglas reales del juego)
    rec $L t_chest 2200 BOT_TRAILER=chest BOT_OVLOG=1 BOT_OVWAIT=2.6 BOT_ULT=1 BOT_CLASS=0 BOT_WARP=combat:0
    rec $L t_arsenal 1500 BOT_TRAILER=arsenal BOT_CLASS=1 BOT_WARP=combat:6
    rec $L t_charge 1300 BOT_TRAILER=charge BOT_CLASS=9 BOT_WARP=combat:7
    rec $L t_inv 800 BOT_TRAILER=inv BOT_CLASS=0 BOT_WARP=combat:0
    rec $L t_bless 800 BOT_TRAILER=bless BOT_ULT=1 BOT_CLASS=0 BOT_WARP=combat:0
    rec $L t_parry 2100 BOT_TRAILER=parry BOT_PARRYBOSS=1 BOT_ULT=1 BOT_CLASS=0 BOT_WARP=boss:7
    rec $L t_fire 900 BOT_TRAILER=fire BOT_ULT=1 BOT_CLASS=2 BOT_WARP=combat:1
  done
}
all
echo "Escenas en $OUT"
