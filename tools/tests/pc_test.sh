#!/usr/bin/env bash
# Pruebas de la version de PC (sin ventana): plataforma, controles tactiles, ajustes de video y calidad.
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT=/tmp/swr_pctest; rm -rf "$OUT"; mkdir -p "$OUT"
JV=$(javac -version 2>&1 | grep -o 'javac [0-9]*' | grep -o '[0-9]*' | head -1)
if [ "$JV" -ge 22 ]; then F="--release 22"; R=""; else F="--release 21 --enable-preview"; R="--enable-preview"; fi
find Shared/src/main/java PC/src/main/java tools/tests/PcTest.java -name '*.java' ! -name OggJorbis.java > "$OUT/s.txt"
javac $F -encoding UTF-8 -nowarn -d "$OUT" @"$OUT/s.txt" 2>&1 | grep -v "^Note" || true
java $R -Djava.awt.headless=true -cp "$OUT" PcTest
