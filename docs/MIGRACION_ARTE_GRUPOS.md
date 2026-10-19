# Migración artística por grupos (SwordsmanMagic: Eternal Abyss)

Referencia de calidad: Paladín del Alba con casco cerrado. Cada grupo se integra y se prueba antes del siguiente.

## Grupo 1 — Paladín del Alba (INTEGRADO)
- Cambio: yelmo cerrado (visera con ranura de ojos y rejilla vertical, proa, nuca acorazada). Resto del diseño v3 intacto.
- Generador: `tools/art_players/cls_paladin.py`. Cadena: `build_all.py paladin` -> `make_smear.py` -> `make_unarmed.py --only paladin` -> `polish.py`.
- Recursos regenerados: `pl_paladin.png`, `plx_paladin.png`, `splash_paladin.png`, `portrait_paladin.png`. `pl_paladin.json` sin cambios (anclajes, cajas y tiempos iguales).
- Pruebas (headless, no Android/Windows reales): anim_sheets_check, anim_test (40/0), arsenal_test (254), combat_test, hud_test, ui_test: OK.
- Para revertir: restaurar esos 4 PNG y `cls_paladin.py` del commit anterior.

## Pendiente (sin tocar)
- Clases: shadow, flame, storm, frost, verdant, blood, earth, astral, steel (`tools/art_players/cls_*.py`).
- Enemigos (40, `tools/art_enemies/en_*.py`), minibosses/élites y jefes (`tools/art_bosses/boss_*.py`).
