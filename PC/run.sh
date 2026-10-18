#!/usr/bin/env bash
# Banco de pruebas de escritorio: compila el motor (Shared) y el codigo de PC a /tmp/swr_build y ejecuta desktop.Main con los argumentos dados.
# Ej: PC/run.sh --headless --frames 300 --script PC/demo.script --shots /tmp/shots
#     PC/run.sh --headless --pc --frames 300 ...      (plataforma de PC: sin controles tactiles, con menu de video)
# Con --game desktop.StubGame se usa el juego de prueba del banco. Por defecto: com.julianfarks.roguelike.core.Game
# Nota: PcXInput usa la API de funciones externas (JDK 22+); con un JDK 21 local se compila como vista previa (--enable-preview).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT=${SWR_OUT:-/tmp/swr_build}
rm -rf "$OUT"; mkdir -p "$OUT"
find "$ROOT/Shared/src/main/java/com/julianfarks/roguelike/core" -name '*.java' > "$OUT/sources.txt"
find "$ROOT/PC/src/main/java" -name '*.java' >> "$OUT/sources.txt"
JV=$(javac -version 2>&1 | grep -o 'javac [0-9]*' | grep -o '[0-9]*' | head -1)
if [ "$JV" -ge 22 ]; then FLAGS="--release 22"; RUNF=""; else FLAGS="--release 21 --enable-preview"; RUNF="--enable-preview"; fi
if ! javac $FLAGS -encoding UTF-8 -nowarn -d "$OUT" @"$OUT/sources.txt" > "$OUT/javac.log" 2>&1; then cat "$OUT/javac.log"; exit 1; fi
cd "$ROOT"
exec java $RUNF -cp "$OUT:$ROOT/PC/src/main/resources" desktop.Main "$@"
