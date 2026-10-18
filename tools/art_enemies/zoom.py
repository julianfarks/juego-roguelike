import sys, json
from PIL import Image
OUT='/home/claude/juego-roguelike/Shared/assets/sprites/'
name=sys.argv[1]; rows=sys.argv[2]; sc=int(sys.argv[3]) if len(sys.argv)>3 else 8
frames=sys.argv[4] if len(sys.argv)>4 else ''
im=Image.open(OUT+name+'.png'); js=json.load(open(OUT+name+'.json'))
W,H=js['cell']; names=list(js['anims'])
sel=[]
for r in rows.split(','):
    a=js['anims'][r]
    fl=range(a['n']) if not frames else [int(x) for x in frames.split(',') if int(x)<a['n']]
    for i in fl: sel.append((a['row'],i))
cols=min(len(sel),6)
rws=(len(sel)+cols-1)//cols
sheet=Image.new('RGBA',(cols*W*sc,rws*H*sc),(40,36,52,255))
for k,(r,i) in enumerate(sel):
    f=im.crop((i*W,r*H,(i+1)*W,(r+1)*H)).resize((W*sc,H*sc),Image.NEAREST)
    sheet.alpha_composite(f,((k%cols)*W*sc,(k//cols)*H*sc))
sheet.convert('RGB').save('/home/claude/juego-roguelike/tools/previews/art_enemies/_zoom.png')
