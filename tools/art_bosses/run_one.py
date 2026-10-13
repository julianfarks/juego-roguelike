import sys, importlib, time
sys.path.insert(0, '/home/claude/juego-roguelike/tools/art_bosses')
from build_lib import *
name = sys.argv[1]
only = sys.argv[2].split(',') if len(sys.argv) > 2 else None
mod = importlib.import_module('boss_' + name)
t = time.time()
boss = mod.build()
fr = render_boss(boss, only)
previews(boss, fr, 3)
if not only:
    write_sheet(boss, fr)
print('ok', round(time.time() - t, 1), 's')
