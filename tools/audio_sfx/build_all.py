#!/usr/bin/env python3
"""Regenera todos los SFX (excepto amb_*). Uso: python3 tools/audio_sfx/build_all.py [--only prefijo ...] [--no-analyze]"""
import sys, os, json, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from multiprocessing import Pool
import reg
import core


def load_all():
    import s_ui_world, s_player, s_skills, s_enemies, s_bosses  # noqa  (registran sonidos)


def _job(name):
    try:
        return core.build_one(name)
    except Exception as e:  # noqa
        import traceback
        return name, 'ERR ' + traceback.format_exc()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', nargs='*', default=None)
    ap.add_argument('--no-analyze', action='store_true')
    ap.add_argument('--jobs', type=int, default=2)
    a = ap.parse_args()
    load_all()
    names = sorted(reg.REG)
    if a.only:
        names = [n for n in names if any(n.startswith(p) for p in a.only)]
    t0 = time.time()
    with Pool(a.jobs) as p:
        res = p.map(_job, names, chunksize=2)
    errs = [r for r in res if isinstance(r[1], str)]
    for n, e in errs:
        print('FALLO', n, e)
    durs = {n: round(d, 3) for n, d in res if not isinstance(d, str)}
    mpath = os.path.join(HERE, 'sfx_manifest.json')
    old = {}
    if a.only and os.path.exists(mpath):
        old = json.load(open(mpath)).get('sfx', {})
    old.update(durs)
    json.dump({'sfx': dict(sorted(old.items()))}, open(mpath, 'w'), indent=1)
    print(f'{len(durs)} sonidos en {time.time()-t0:.0f}s, errores: {len(errs)}')
    if not a.no_analyze:
        import analyze
        analyze.run(sorted(durs))
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
