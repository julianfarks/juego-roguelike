"""Vista rapida: python3 prev2.py <mod> "idle:0,attack1:3,..." [escala] [columnas] [salida]
   Anim sin fotograma = tira completa."""
import sys, importlib, time
sys.path.insert(0, '/home/claude/juego-roguelike/tools/art_bosses')
from build_lib import *

mod = importlib.import_module('boss_' + sys.argv[1])
picks = []
boss = mod.build()
for tok in sys.argv[2].split(','):
    if ':' in tok:
        a, i = tok.split(':')
        picks.append((a, int(i)))
    else:
        n = [x for x in ORDER if x[0] == tok][0][1]
        picks += [(tok, i) for i in range(n)]
sc = int(sys.argv[3]) if len(sys.argv) > 3 else 2
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6
cache = {}
fr = {}
for a, i in picks:
    fr.setdefault(a, {})
    if i not in fr[a]:
        fr[a][i] = boss.frame(a, i, [x for x in ORDER if x[0] == a][0][1], boss.pose_at(a, i))
frames = {a: [fr[a].get(i) for i in range(max(fr[a]) + 1)] for a in fr}
out = sys.argv[5] if len(sys.argv) > 5 else f'{PREV}/{boss.id}_pick.png'
contact(boss, frames, picks, sc, cols).save(out)
print('ok', out)
