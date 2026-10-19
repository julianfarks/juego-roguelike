#!/bin/bash
# Regenera UNA clase (grupo 2): build_all -> make_smear -> make_unarmed -> polish. Uso: tools/art_players/regen_class.sh shadow
set -e
cd "$(dirname "$0")/../.."
C=$1; S=Shared/assets/sprites
python3 tools/art_players/build_all.py $C --nopreview | tail -1
python3 tools/art/make_smear.py | tail -1
python3 tools/art/make_unarmed.py --only $C | tail -1
python3 tools/art/polish.py $S/pl_$C.png $S/plx_$C.png $S/splash_$C.png $S/portrait_$C.png | tail -4
git status --short Shared | head
git checkout -- Shared/assets/sprites/pl_$C.json 2>/dev/null || true   # los anclajes/JSON funcionales no cambian nunca
