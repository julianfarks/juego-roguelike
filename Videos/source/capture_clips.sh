#!/usr/bin/env bash
# Graba las escenas de gameplay REAL (modo PC limpio: sin controles tactiles ni elementos de depuracion) a 1920x1080, 60 fps.
# Usa el banco de pruebas headless del repo (PC/run.sh --headless --pc --record ...). El bot (DebugBot) solo juega; no se dibuja nada suyo.
# Uso: bash Videos/source/capture_clips.sh [carpeta_salida]      (tarda ~1 h en 2 CPU; ejecutar de a una escena, nunca en paralelo)
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/Videos/source/clips}"; mkdir -p "$OUT"
clip() {  # NOMBRE CLASE WARP FRAMES   (WARP = tipo:bioma; boss/combat/elite/shop/bless/treasure/forge/evN)
  local N=$1 C=$2 W=$3 F=$4
  [ -f "$OUT/$N.mp4" ] && return 0
  ( cd "$ROOT" && BOT_CLASS=$C BOT_GOD=1 BOT_WARP=$W BOT_ULT=1 SWR_OUT=/tmp/swr_build_trailer \
    bash PC/run.sh --headless --pc --bot --w 480 --frames $((150+F)) --store "/tmp/trailer_store_$N" \
    --record "$OUT/$N.mp4" --rec-from 140 --rec-to $((150+F)) --shots "/tmp/trailer_shots_$N" > "$OUT/$N.log" 2>&1 )
}
clip b0_paladin 0 boss:0 800;  clip b1_flame 2 boss:1 800;   clip b2_frost 4 boss:2 800;   clip b3_shadow 1 boss:3 800
clip b4_verdant 5 boss:4 800;  clip b5_storm 3 boss:5 800;   clip b6_blood 6 boss:6 800;   clip b7_earth 7 boss:7 800
clip b8_astral 8 boss:8 900
clip c0_shadow 1 combat:0 700; clip c1_flame 2 combat:1 700; clip c2_frost 4 combat:2 700; clip c3_astral 8 combat:3 700
clip c4_verdant 5 combat:4 700; clip c5_storm 3 combat:5 700; clip c6_blood 6 combat:6 700; clip c7_steel 9 combat:7 700
clip e1_elite 0 elite:1 700;   clip e3_elite 3 elite:3 700
clip s_shop 0 shop:0 500; clip s_bless 0 bless:0 500; clip s_treasure 0 treasure:0 500; clip s_forge 0 forge:1 500
clip s_ev1 0 ev1:0 500; clip s_ev2 0 ev2:0 500; clip s_ev4 0 ev4:0 500; clip s_ev5 0 ev5:0 500; clip s_ev6 0 ev6:0 500
echo "Escenas en $OUT"
