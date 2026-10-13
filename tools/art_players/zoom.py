import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import build_all as B
import anims as AN
from kit import reset_mats
from rig import skeleton, simulate
from common import render_frame
cid, name = sys.argv[1], sys.argv[2]
idx = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else None
sc = int(sys.argv[4]) if len(sys.argv) > 4 else 10
reset_mats(); cls = B.load(cid); cls.init_mats()
seq = cls.seq(name); n = AN.N[name]; loop = AN.LOOP.get(name, False)
rb = simulate(cls.ribbons, seq.at, lambda p: skeleton(p, cls.D), n, loop=loop)
hit = cls.attacks[name][1] if name in cls.attacks else None
idx = idx or list(range(n))
ims = []
for i in idx:
    tr = (lambda X, i=i: cls.trail_draw(X, seq, i, hit)) if hit else None
    ims.append(Image.fromarray(render_frame(cls, seq, rb, i, n, name, trail=tr), 'RGBA'))
W = Image.new('RGBA', (64 * len(ims), 48), (30, 26, 44, 255))
for k, f in enumerate(ims):
    W.alpha_composite(f, (64 * k, 0))
W = W.resize((W.width * sc, W.height * sc), Image.NEAREST)
out = f'/home/claude/juego-roguelike/tools/previews/art_players/zoom_{cid}_{name}.png'
W.save(out); print(out, W.size)
