import sys, numpy as np
from PIL import Image
from terrain import terrain_tile
from biomes import CFG, BIOMES
def mapgrid():
    g=np.zeros((17,40),bool)
    g[14:,:]=True; g[:2,:]=True; g[:,:2]=True; g[:,38:]=True
    g[14:,14:17]=False; g[15:,27:29]=False
    g[9:11,6:10]=True; g[5:14,21:23]=True; g[12:14,10:13]=True; g[11:14,30:34]=True; g[2:5,30:36]=True
    g[8:10,14:19]=True; g[6:8,26:29]=True
    return g
def auto(g,r,c):
    def s(rr,cc): return rr<0 or cc<0 or rr>=g.shape[0] or cc>=g.shape[1] or g[rr,cc]
    return (1 if s(r-1,c) else 0)|(2 if s(r,c+1) else 0)|(4 if s(r+1,c) else 0)|(8 if s(r,c-1) else 0)
if __name__=="__main__":
    g=mapgrid()
    names=sys.argv[1:] or ['catacumbas']
    outs=[]
    for b in names:
        im=Image.new('RGBA',(640,272),(30,30,40,255))
        rs=np.random.RandomState(3)
        for r in range(17):
            for c in range(40):
                if g[r,c]:
                    t=terrain_tile(CFG[b],auto(g,r,c),rs.randint(3))
                    im.alpha_composite(Image.fromarray(t,'RGBA'),(c*16,r*16))
        im=im.crop((0,96,320,272)); outs.append(im.resize((1280,704),Image.NEAREST))
    H=sum(o.height for o in outs)
    out=Image.new('RGBA',(1280,H))
    y=0
    for o in outs: out.paste(o,(0,y)); y+=o.height
    out.save('../previews/art_world/t2.png')
    