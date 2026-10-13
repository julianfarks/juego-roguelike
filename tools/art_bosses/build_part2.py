"""Construye los jefes de la parte 2: python3 build_part2.py [titan matriarca guardian cazador1 cazador2 cazador3]"""
import sys, importlib, time
sys.path.insert(0, '/home/claude/juego-roguelike/tools/art_bosses')
from build_lib import *
MODS = ['titan', 'matriarca', 'guardian', 'cazador1', 'cazador2', 'cazador3']
sel = sys.argv[1:] or MODS
for m in sel:
    t = time.time()
    boss = importlib.import_module('boss_' + m).build()
    fr = render_boss(boss)
    write_sheet(boss, fr)
    previews(boss, fr, 3)
    picks = [('idle', 0), ('walk', 1), ('windup1', 4), ('attack1', 3), ('windup2', 4), ('attack2', 2), ('windup3', 5), ('attack3', 1), ('attack3', 4), ('cast', 4), ('hurt', 0), ('phase', 5),
             ('intro', 3), ('intro', 6), ('intro', 10), ('death', 3), ('death', 6), ('death', 10), ('death', 13), ('attack1', 1)]
    contact(boss, fr, picks, 2, 5).save(f'{PREV}/{boss.id}_overview.png')
    print(m, 'ok', round(time.time() - t, 1), 's')
