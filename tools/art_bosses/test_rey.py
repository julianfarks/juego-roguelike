import sys
sys.path.insert(0,'/home/claude/juego-roguelike/tools/art_bosses')
import boss_rey as B
from anim import *
from build_lib import *
idle = K([(0,{'uarm_f':-35,'farm_f':-45,'sword':68})])
anims = {n:{'pose':idle} for n,_,_,_ in ORDER}
b = B.make(anims, None)
fr = [b.frame('idle',0,6,b.pose_at('idle',0))]
from PIL import Image
im = Image.fromarray(fr[0],'RGBA')
bg = Image.new('RGBA',im.size,(34,30,46,255)); bg.alpha_composite(im)
bg.resize((128*6,128*6),Image.NEAREST).save(PREV+'/rey_test.png')
