import sys, os
import numpy as np
from bgkit import *
from bgs import BGS
OUT = '/home/claude/juego-roguelike/app/src/main/assets/bg'
BIO = ['catacumbas', 'forja', 'helado', 'vacio', 'bosque', 'tormenta', 'sangre', 'eclipse', 'cazador']


def main(names=None):
    os.makedirs(OUT, exist_ok=True)
    for b in names or BIO:
        r0, L1, L2 = BGS[b]()
        finish_opaque(r0, f'{OUT}/bg_{b}_0.png', 64, 16)
        finish_alpha(L1, f'{OUT}/bg_{b}_1.png', 64)
        finish_alpha(L2, f'{OUT}/bg_{b}_2.png', 64)
        print('bg', b)


if __name__ == '__main__':
    main(sys.argv[1:] or None)
