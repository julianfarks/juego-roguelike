#!/bin/bash
# Regenera enemigos (fase 3 enemigos): build_all -> polish; restaura el JSON funcional. Uso: tools/art_enemies/regen_enemy.sh esqueleto zombi
cd "$(dirname "$0")/../.."
S=Shared/assets/sprites
for E in "$@"; do
  (cd tools/art_enemies && python3 build_all.py $E | tail -1)
  python3 tools/art/polish.py $S/en_$E.png | tail -1
  git checkout -- $S/en_$E.json 2>/dev/null || true
done
