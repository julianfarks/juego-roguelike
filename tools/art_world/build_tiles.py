import sys, os
import numpy as np
from kit import *
import biome_specs as S
from tiles_special import build_sheet
from biomes import BIOMES
OUT = '/home/claude/juego-roguelike/Shared/assets/tiles'


def main(names=None):
    os.makedirs(OUT, exist_ok=True)
    for b in names or BIOMES:
        sh = build_sheet(b, S.PAL[b], S.SPECS[b])
        save_png(sh, f'{OUT}/tiles_{b}.png')
        print('tiles', b)


if __name__ == '__main__':
    main(sys.argv[1:] or None)
