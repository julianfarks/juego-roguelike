import sys, numpy as np
from PIL import Image
from terrain import terrain_tile
from biomes import CFG, BIOMES
from t2 import mapgrid, auto
g=mapgrid()
names=sys.argv[2:]; Z=int(sys.argv[1])
tiles=[]
for b in names:
    im=Image.new('RGBA',(640,272),(30,30,40,255))
    rs=np.random.RandomState(3)
    for r in range(17):
        for c in range(40):
            if g[r,c]:
                t=terrain_tile(CFG[b],auto(g,r,c),rs.randint(3))
                im.alpha_composite(Image.fromarray(t,'RGBA'),(c*16,r*16))
    im=im.crop((16,112,336,272)).resize((320*Z,160*Z),Image.NEAREST)
    tiles.append(im)
cols=2; rows=(len(tiles)+1)//2
out=Image.new('RGBA',(320*Z*cols,160*Z*rows))
for i,t in enumerate(tiles): out.paste(t,((i%cols)*320*Z,(i//cols)*160*Z))
out.save('../previews/art_world/t3.png')
