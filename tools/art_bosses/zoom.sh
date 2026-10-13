#!/bin/bash
# uso: zoom.sh boss anim frame [scale]
cd /home/claude/juego-roguelike/tools/art_bosses
python3 - "$@" <<'PY'
import sys,importlib
sys.path.insert(0,'.')
from build_lib import *
m=importlib.import_module('boss_'+sys.argv[1]); b=m.build()
sc=int(sys.argv[4]) if len(sys.argv)>4 else 5
frs=[int(x) for x in sys.argv[3].split(',')]
ims=[]
for f in frs:
    fr=b.frame(sys.argv[2],f,14,b.pose_at(sys.argv[2],f))
    im=Image.fromarray(fr,'RGBA'); bg=Image.new('RGBA',im.size,(34,30,46,255)); bg.alpha_composite(im); ims.append(bg)
W,H=ims[0].size
out=Image.new('RGBA',(W*len(ims),H)); [out.paste(x,(i*W,0)) for i,x in enumerate(ims)]
out.resize((out.width*sc,out.height*sc),Image.NEAREST).save(PREV+'/z.png')
PY
