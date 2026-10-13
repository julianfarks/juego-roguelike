import sys, numpy as np
from PIL import Image
from terrain import terrain_tile
from biomes import CFG, BIOMES
names = sys.argv[1:] or BIOMES
rows=[]
for b in names:
    sheet = np.zeros((48,256,4),np.uint8)
    for v in range(3):
        for m in range(16):
            sheet[v*16:(v+1)*16, m*16:(m+1)*16] = terrain_tile(CFG[b], m, v)
    rows.append(sheet)
img = np.concatenate(rows,0)
bg = Image.new('RGBA',(img.shape[1],img.shape[0]),(40,40,50,255))
bg.alpha_composite(Image.fromarray(img,'RGBA'))
bg = bg.resize((bg.width*3,bg.height*3),Image.NEAREST)
bg.save('../previews/art_world/t1.png')
