import sys, importlib
sys.path.insert(0, '/home/claude/juego-roguelike/tools/art_bosses')
from build_lib import *
from PIL import Image
def sheet_frames(bid):
    import json
    im = Image.open(f'{A}/sprites/bs_{bid}.png'); js = json.load(open(f'{A}/sprites/bs_{bid}.json'))
    W, H = js['cell']
    fr = {}
    for k, a in js['anims'].items():
        fr[k] = [np.asarray(im.crop((i * W, a['row'] * H, (i + 1) * W, (a['row'] + 1) * H))) for i in range(a['n'])]
    return js, fr
if __name__ == '__main__':
    bid = sys.argv[1]; mode = sys.argv[2]; sc = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    js, fr = sheet_frames(bid)
    class B: pass
    b = B(); b.cell = tuple(js['cell']); b.pivot = js['pivot']; b.id = bid
    if mode == 'overview':
        picks = [('idle', 0), ('idle', 3), ('walk', 1), ('walk', 5), ('windup1', 4), ('attack1', 3), ('windup2', 4), ('attack2', 2),
                 ('windup3', 5), ('attack3', 1), ('attack3', 4), ('cast', 4), ('hurt', 0), ('phase', 5), ('intro', 3), ('intro', 7),
                 ('intro', 10), ('death', 3), ('death', 6), ('death', 10), ('death', 13), ('attack1', 1), ('attack2', 4), ('cast', 2)]
        cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6
        contact(b, fr, picks, sc, cols).save(f'{PREV}/{bid}_overview.png')
    else:
        names = mode.split(',')
        for nm in names:
            strip(b, fr[nm], sc).save(f'{PREV}/{bid}_{nm}.png')
