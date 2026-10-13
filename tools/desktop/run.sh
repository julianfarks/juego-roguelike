#!/usr/bin/env bash
# Compila core + desktop (sin android) a /tmp/swr_build y ejecuta el banco de pruebas con los argumentos dados.
# Ej: tools/desktop/run.sh --headless --frames 300 --script tools/desktop/demo.script --shots /tmp/shots
# Con --game desktop.StubGame se usa el juego de prueba del banco. Por defecto: com.julianfarks.roguelike.core.Game
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT=/tmp/swr_build
rm -rf "$OUT"; mkdir -p "$OUT"
find "$ROOT/app/src/main/java/com/julianfarks/roguelike/core" -name '*.java' > "$OUT/sources.txt"
find "$ROOT/tools/desktop" -name '*.java' >> "$OUT/sources.txt"
javac --release 17 -encoding UTF-8 -nowarn -d "$OUT" @"$OUT/sources.txt"
cd "$ROOT"
exec java -cp "$OUT" desktop.Main "$@"
