#!/usr/bin/env python3
"""Regenera todo el arte de FX e interfaz: python3 tools/art_fx_ui/build_all.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_a, fx_b, fx_c
fx_a.build(); fx_b.build(); fx_c.build()
print('fx ok')
for mod in ('ui_parts', 'icons', 'fonts', 'logo', 'title'):
    try:
        m = __import__(mod)
    except ModuleNotFoundError as e:
        if e.name == mod:
            continue
        raise
    m.build()
    print(mod, 'ok')
