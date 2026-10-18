import sys
from PIL import Image
A='/home/claude/juego-roguelike/Shared/assets/tiles/tiles_%s.png'
names=sys.argv[1:]
Z=4
out=Image.new('RGBA',(256*Z,64*Z*len(names)))
for j,b in enumerate(names):
    im=Image.open(A%b).convert('RGBA').crop((0,48,256,112))
    bg=Image.new('RGBA',im.size,(58,50,66,255)); bg.alpha_composite(im)
    out.paste(bg.resize((256*Z,64*Z),Image.NEAREST),(0,j*64*Z))
out.save('../previews/art_world/t7.png')
