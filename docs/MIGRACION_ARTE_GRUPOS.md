# Migración artística por grupos (SwordsmanMagic: Eternal Abyss)

Referencia de calidad: Paladín del Alba con casco cerrado. Cada grupo se integra y se prueba antes del siguiente.

## Grupo 1 — Paladín del Alba (INTEGRADO)
- Cambio: yelmo cerrado (visera con ranura de ojos y rejilla vertical, proa, nuca acorazada). Resto del diseño v3 intacto.
- Generador: `tools/art_players/cls_paladin.py`. Cadena: `build_all.py paladin` -> `make_smear.py` -> `make_unarmed.py --only paladin` -> `polish.py`.
- Recursos regenerados: `pl_paladin.png`, `plx_paladin.png`, `splash_paladin.png`, `portrait_paladin.png`. `pl_paladin.json` sin cambios (anclajes, cajas y tiempos iguales).
- Pruebas (headless, no Android/Windows reales): anim_sheets_check, anim_test (40/0), arsenal_test (254), combat_test, hud_test, ui_test: OK.
- Para revertir: restaurar esos 4 PNG y `cls_paladin.py` del commit anterior.

## Grupo 2 — Las otras 9 clases (INTEGRADO, un commit por clase)
Orden: shadow, flame, storm, frost, verdant, blood, earth, astral, steel. Solo cambia `draw`/`init_mats` en cada `cls_*.py` (Dims, cintas, animaciones y ataques intactos).
- Cada clase: placas/ropa con juntas y filos de luz, hombrera en laminas o charretera, yelmo/capucha/mascara con mas estructura, brazales, cinturon, y arma con guarda, bisel o abrazaderas propias de su tema.
- Cadena por clase: `tools/art_players/regen_class.sh <clase>` (build_all -> smear -> unarmed -> polish y restaura el JSON funcional). Comparacion: `tools/art_players/cmp_class.py <clase>` -> `docs/capturas_arte/<clase>_grupo2_*.png`.
- Los 10 `pl_*.json` son identicos al estado previo al grupo 2 (anclajes, cajas, tiempos). `anim_sheets_check` OK para las 10 clases.
- Limite honesto: son mejoras de acabado (estructura, materiales, filos de luz), no cambios de silueta. Los smear de shadow y steel salen algo mas apagados porque se derivan de la paleta del sprite.
- Revertir una clase: `git revert <commit de esa clase>`.
- Pruebas headless: anim_test 40/0, combat, hud, ui OK. arsenal_test dio 253/254 una vez y 254/254 en 3 repeticiones siguientes (intermitente, no reproducido ni atribuido).

## Pendiente (sin tocar)
- Enemigos (40, `tools/art_enemies/en_*.py`), minibosses/élites y jefes (`tools/art_bosses/boss_*.py`).
