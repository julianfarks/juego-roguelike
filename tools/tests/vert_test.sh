#!/usr/bin/env bash
# Pruebas (generador, sin pantalla) de las mazmorras verticales: alcanzabilidad, enemigos, cofres, estructura. NO es un dispositivo real.
ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
OUT=/tmp/vt_build; rm -rf "$OUT"; mkdir -p "$OUT"
find Shared/src/main/java/com/julianfarks/roguelike/core -name '*.java' ! -name OggJorbis.java > "$OUT/src.txt"
echo tools/tests/VertGenTest.java >> "$OUT/src.txt"
javac --release 21 --enable-preview -encoding UTF-8 -nowarn -d "$OUT" @"$OUT/src.txt" 2>&1 | grep -v "^Note\|JAVA_TOOL" 
java --enable-preview -cp "$OUT:Shared/assets" com.julianfarks.roguelike.core.VertGenTest "${1:-40}" 2>&1 | grep -v JAVA_TOOL
