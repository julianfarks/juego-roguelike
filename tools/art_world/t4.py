import sys
from PIL import Image
A='/home/claude/juego-roguelike/app/src/main/assets/tiles/tiles_%s.png'
b=sys.argv[1]; Z=int(sys.argv[2]) if len(sys.argv)>2 else 4
rows=sys.argv[3] if len(sys.argv)>3 else '0-7'
r0,r1=map(int,rows.split('-'))
im=Image.open(A%b).convert('RGBA').crop((0,r0*16,256,(r1+1)*16))
bg=Image.new('RGBA',im.size,(60,52,70,255))
# cuadricula suave para ver bordes de baldosa
bg.alpha_composite(im)
bg=bg.resize((im.width*Z,im.height*Z),Image.NEAREST)
bg.save('../previews/art_world/t4.png')
