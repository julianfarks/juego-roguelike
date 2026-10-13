#!/usr/bin/env python3
import sys, os, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MODS = ['props_arch', 'props_objs', 'props_pick']


def main(argv):
    names = set(argv)
    for mn in MODS:
        try:
            m = importlib.import_module(mn)
        except ModuleNotFoundError as e:
            if e.name == mn:
                continue
            raise
        for fn in m.SHEETS:
            nm = fn.__name__.replace('sheet_', '')
            if names and nm not in names:
                continue
            sh = fn(); sh.save(); print('ok', sh.name)


if __name__ == '__main__':
    main(sys.argv[1:])
