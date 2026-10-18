#!/usr/bin/env bash
# Compila SwordsmanMagic: Eternal Abyss para PC y genera la carpeta ejecutable de Windows (SwordsmanMagic.exe + JRE incluido).
# Requisitos: JDK 22 o superior (con jpackage) y bash (Git Bash en Windows). Uso:  bash PC/build.sh
# Resultado: PC/build/dist/SwordsmanMagic/SwordsmanMagic.exe  (en Linux/macOS genera la app equivalente para pruebas).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && { pwd -W 2>/dev/null || pwd; })"   # en Git Bash: ruta de Windows (javac no lee rutas /d/... dentro de @archivos)
B="$ROOT/PC/build"
rm -rf "$B/classes" "$B/input" "$B/dist"
mkdir -p "$B/classes" "$B/lib" "$B/input" "$B/dist"

JV=$(javac -version 2>&1 | grep -o 'javac [0-9]*' | grep -o '[0-9]*' | head -1)
[ "$JV" -ge 22 ] || { echo "Se necesita JDK 22 o superior (hay $JV)"; exit 1; }

# Dependencias de EJECUCION (solo para leer OGG con Java Sound; el codigo no las importa)
MVN=https://repo1.maven.org/maven2
dl() { [ -s "$B/lib/$(basename "$1")" ] || curl -fsSL --retry 3 -o "$B/lib/$(basename "$1")" "$MVN/$1"; }
dl com/googlecode/soundlibs/vorbisspi/1.0.3.3/vorbisspi-1.0.3.3.jar
dl com/googlecode/soundlibs/jorbis/0.0.17.4/jorbis-0.0.17.4.jar
dl com/googlecode/soundlibs/tritonus-share/0.3.7.4/tritonus-share-0.3.7.4.jar

# Motor compartido (Shared) + codigo de PC
find "$ROOT/Shared/src/main/java" "$ROOT/PC/src/main/java" -name '*.java' > "$B/sources.txt"
javac --release 22 -encoding UTF-8 -nowarn -cp "$B/lib/jorbis-0.0.17.4.jar" -d "$B/classes" @"$B/sources.txt"
cp -r "$ROOT/PC/src/main/resources/." "$B/classes/"
jar --create --file "$B/input/swordsmanmagic.jar" --main-class pc.PcMain -C "$B/classes" .
cp "$B"/lib/*.jar "$B/input/"
cp -r "$ROOT/Shared/assets" "$B/input/assets"       # el juego busca "assets" junto a sus jar

ICON=()
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) ICON=(--icon "$ROOT/PC/packaging/icon.ico");; esac
jpackage --type app-image --name SwordsmanMagic --app-version 2.1 --vendor JulianFarKs \
  --description "SwordsmanMagic: Eternal Abyss" \
  --input "$B/input" --main-jar swordsmanmagic.jar --main-class pc.PcMain \
  --add-modules java.desktop,java.logging,java.prefs,jdk.unsupported \
  --java-options "-Dsun.java2d.uiScale=1" --java-options "--enable-native-access=ALL-UNNAMED" --java-options "-Xmx768m" \
  "${ICON[@]}" --dest "$B/dist"
echo "Listo: $B/dist/SwordsmanMagic"
