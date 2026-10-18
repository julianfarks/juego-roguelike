#!/usr/bin/env bash
# Mercader errante: piso con enemigos vivos -> entrar -> comprar -> guardar/cargar -> salir -> mismo piso intacto -> no reentrar -> despejar -> salida normal.
set -u
cd "$(dirname "$0")/../.."
RUN=/tmp/run2.sh; [ -x "$RUN" ] || RUN=PC/run.sh
out=$(BOT_EVENT=1 BOT_MERCHTEST=1 BOT_WARP=combat:0 timeout 300 $RUN --headless --bot --frames 3000 2>&1 | grep MERCHTEST)
echo "$out"
echo "$out" | grep -q "MERCHTEST TODO OK" && ! echo "$out" | grep -q "FAIL" && echo "merchant_test OK" || { echo "merchant_test FALLOS"; exit 1; }
