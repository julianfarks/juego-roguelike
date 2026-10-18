import sys, json
from PIL import Image
name=sys.argv[1]; fr=[int(x) for x in sys.argv[2].split(',')]; row=int(sys.argv[3]) if len(sys.argv)>3 else 0; z=int(sys.argv[4]) if len(sys.argv)>4 else 10
O='/home/claude/juego-roguelike/Shared/assets/sprites/'
im=Image.open(O+name+'.png'); W,H=json.load(open(O+name+'.json'))['cell']
s=Image.new('RGBA',(len(fr)*W*z,H*z),(34,30,44,255))
for k,f in enumerate(fr):
    s.alpha_composite(im.crop((f*W,row*H,(f+1)*W,(row+1)*H)).resize((W*z,H*z),Image.NEAREST),(k*W*z,0))
s.convert('RGB').save('/home/claude/juego-roguelike/tools/previews/art_enemies/_z.png')
