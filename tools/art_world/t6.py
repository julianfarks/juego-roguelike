import sys
from PIL import Image
A='/home/claude/juego-roguelike/app/src/main/assets/bg/bg_%s_%d.png'
names=sys.argv[1:]
out=Image.new('RGBA',(1536,288*len(names)))
for j,b in enumerate(names):
    comp=Image.new('RGBA',(512,288),(0,0,0,255))
    for i in range(3):
        comp.alpha_composite(Image.open(A%(b,i)).convert('RGBA'))
    for k in range(3): out.paste(comp,(k*512,j*288))
out.save('../previews/art_world/t6.png')
