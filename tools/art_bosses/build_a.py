"""Runner: coloso_magma, reina_escarcha, devorador_vacio, ent_ancestral. Uso: python3 build_a.py [id ...]"""
import sys, importlib, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lib import *
import view
IDS = ['coloso_magma', 'reina_escarcha', 'devorador_vacio', 'ent_ancestral']
sel = sys.argv[1:] or IDS
for bid in sel:
    mod = importlib.import_module('boss_' + bid)
    boss = mod.build()
    fr = render_boss(boss)
    write_sheet(boss, fr)
    previews(boss, fr, 2)
    js, f2 = view.sheet_frames(bid)
    class B: pass
    b = B(); b.cell = tuple(js['cell']); b.pivot = js['pivot']; b.id = bid
    picks = [('idle', 0), ('walk', 1), ('walk', 5), ('windup1', 4), ('attack1', 3), ('windup2', 4), ('attack2', 2), ('attack2', 4),
             ('windup3', 5), ('attack3', 1), ('attack3', 4), ('attack3', 6), ('cast', 2), ('cast', 5), ('hurt', 0), ('phase', 5),
             ('intro', 2), ('intro', 5), ('intro', 8), ('intro', 11), ('death', 2), ('death', 5), ('death', 8), ('death', 12)]
    contact(b, f2, picks, 2, 4).save(f'{PREV}/{bid}_overview.png')
    print('built', bid)
