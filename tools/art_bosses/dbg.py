import sys, importlib
sys.path.insert(0,'/home/claude/juego-roguelike/tools/art_bosses')
from build_lib import *
from PIL import Image
def show(boss, anim, f, only=None, hide=None, sc=6, out='dbg'):
    p = dict(boss.pose_at(anim, f))
    for pt in boss.parts:
        if only and pt.name not in only: p[pt.name+'.v']=0
        if hide and pt.name in hide: p[pt.name+'.v']=0
    fr = boss.frame(anim, f, 6, p)
    im = Image.fromarray(fr,'RGBA'); bg=Image.new('RGBA',im.size,(34,30,46,255)); bg.alpha_composite(im)
    bg.resize((im.width*sc, im.height*sc), Image.NEAREST).save(f'{PREV}/{out}.png')
if __name__=='__main__':
    mod=importlib.import_module('boss_'+sys.argv[1]); b=mod.build()
    only=sys.argv[4].split(',') if len(sys.argv)>4 and sys.argv[4]!='-' else None
    hide=sys.argv[5].split(',') if len(sys.argv)>5 else None
    show(b, sys.argv[2], int(sys.argv[3]), only, hide)
