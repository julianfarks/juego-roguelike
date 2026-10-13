#!/usr/bin/env python3
import sys, os, importlib, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

MODULES = ['en_catacumbas', 'en_forja', 'en_helado', 'en_vacio', 'en_bosque', 'en_tormenta', 'en_sangre',
           'en_eclipse', 'props']


def main(argv):
    names = set(argv)
    for mname in MODULES:
        try:
            m = importlib.import_module(mname)
        except ModuleNotFoundError as e:
            if e.name == mname:
                continue
            raise
        for sheet_fn in m.SHEETS:
            nm = sheet_fn.__name__.replace('sheet_', '')
            if names and nm not in names:
                continue
            sh = sheet_fn()
            sh.save(OUT, PREV)
            print('ok', sh.name)


if __name__ == '__main__':
    main(sys.argv[1:])
