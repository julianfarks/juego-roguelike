#!/usr/bin/env python3
"""Ventana de parry segun el escudo: se mide en el juego inyectando golpes reales (Level.hurtPlayer, la via comun de
enemigos, proyectiles y jefes) a distintos retardos tras pulsar el boton de escudo. Comprueba que cada categoria tiene su
ventana (basico < intermedio < superior), que coincide con los datos de Items.SH_WIN, que el enfriamiento impide
encadenar parries y que con jefes reales tambien se logran parries."""
import os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
RUN = '/tmp/run2.sh' if os.path.exists('/tmp/run2.sh') else 'PC/run.sh'
src = open('Shared/src/main/java/com/julianfarks/roguelike/core/Items.java', encoding='utf-8').read()
WIN = [float(x.rstrip('f')) for x in re.search(r'SH_WIN = \{([^}]*)\}', src).group(1).replace(' ', '').split(',')]
CD = [float(x.rstrip('f')) for x in re.search(r'SH_CD = \{([^}]*)\}', src).group(1).replace(' ', '').split(',')]
NAMES = ['madera (basico)', 'acero (intermedio)', 'runico (superior)', 'espinas (superior)']
fails = 0


def ck(n, ok, extra=''):
    global fails
    print(('ok   ' if ok else 'FAIL ') + n + ('' if ok else ' ' + str(extra)))
    fails += 0 if ok else 1


def sh(env, frames, script=None):
    e = dict(os.environ, BOT_CLASS='0', **env)
    cmd = [RUN, '--headless', '--bot', '--w', '480', '--frames', str(frames), '--store', '/tmp/parry_t.json', '--shots', '/tmp/parry_t_shots']
    if script:
        cmd += ['--script', script]
    r = subprocess.run(cmd, env=e, capture_output=True, text=True, timeout=900)
    return r.stdout + r.stderr


meas = {}
for sid in range(4):
    out = sh({'BOT_PARRYTEST': str(sid)}, 1200)
    start = int(re.search(r'PARRYSTART f=(\d+)', out).group(1))
    delays = list(range(2, 46, 2))
    lines, hits = [], []
    t = 60
    for d in delays:                                   # un intento por retardo, separados lo bastante para que acabe el enfriamiento
        lines += [f'{start + t} key C down', f'{start + t + 70} key C up']
        hits.append(f'{t + d}:d{d}')
        t += 160
    w = int(round(WIN[sid] * 60)); cdf = int(round(CD[sid] * 60))
    # prueba de encadenado: tras el golpe fallido se vuelve a pulsar dentro del enfriamiento -> no abre otra ventana
    lines += [f'{start + t} key C down', f'{start + t + w + 2} key C up', f'{start + t + w + 5} key C down', f'{start + t + 100} key C up']
    hits.append(f'{t + w + 8}:spam')
    t += 160
    # y pasado el enfriamiento si vuelve a funcionar
    lines += [f'{start + t} key C down', f'{start + t + 6} key C up', f'{start + t + cdf + 6} key C down', f'{start + t + cdf + 70} key C up']
    hits.append(f'{t + cdf + 6 + 4}:aftercd')
    t += cdf + 140
    open('/tmp/parry_t.script', 'w').write('\n'.join(lines) + '\n')
    out = sh({'BOT_PARRYTEST': str(sid) + ';' + ';'.join(hits)}, start + t + 120, '/tmp/parry_t.script')
    res = {m[1]: (m[2] == 'true', int(m[3])) for m in re.finditer(r'PARRYHIT shield=\d tag=(\w+) parried=(\w+) dano=(-?\d+)', out)}
    par = [d for d in delays if res.get(f'd{d}', (False, 0))[0]]
    win_f = max(par) if par else 0
    meas[sid] = win_f
    ck(f'{NAMES[sid]}: ventana medida {win_f} fotogramas (~{win_f / 60:.2f}s) vs dato {WIN[sid]:.2f}s', abs(win_f - w) <= 3 and par == [d for d in delays if d <= win_f], res)
    late = [d for d in delays if d > w + 3]
    ck(f'{NAMES[sid]}: fuera de ventana el golpe NO es parry (se bloquea con dano reducido)', all(not res[f'd{d}'][0] for d in late), res)
    ck(f'{NAMES[sid]}: bloqueo normal reduce el dano pero no lo anula', all(0 < res[f'd{d}'][1] < 10 for d in late if f'd{d}' in res), res)
    ck(f'{NAMES[sid]}: parry exitoso no recibe dano', all(res[f'd{d}'][1] == 0 for d in par), res)
    ck(f'{NAMES[sid]}: pulsar de nuevo dentro del enfriamiento no abre otra ventana', res.get('spam', (True,))[0] is False, res)
    ck(f'{NAMES[sid]}: pasado el enfriamiento ({CD[sid]:.2f}s) vuelve a funcionar', res.get('aftercd', (False,))[0] is True, res)
    ck(f'{NAMES[sid]}: cobertura maxima {WIN[sid] / CD[sid]:.0%} del tiempo (sin parry permanente)', WIN[sid] / CD[sid] <= 0.42)
ck('categorias: basico < intermedio < superior (medido en el juego)', meas[0] < meas[1] < meas[2] and meas[1] < meas[3])
ck('superior claramente mas ancho que basico (>=60%)', meas[2] >= meas[0] * 1.6)

# jefes reales: con el escudo superior y pulsando el boton a ritmo se logran parries contra ataques de jefe de verdad
lines = []
for k in range(0, 60):
    f = 600 + k * 75
    lines += [f'{f} key C down', f'{f + 30} key C up']
open('/tmp/parry_boss.script', 'w').write('\n'.join(lines) + '\n')
out = sh({'BOT_WARP': 'boss:0', 'BOT_GOD': '1', 'BOT_PARRYLOG': '1'}, 5400, '/tmp/parry_boss.script')
n = [int(m[1]) for m in re.finditer(r'PARRIES f=\d+ n=(\d+)', out)]
ck(f'contra un jefe real se logran parries pulsando el escudo (parries={max(n) if n else 0})', bool(n) and max(n) >= 1)
ck('sin excepciones', 'Exception' not in out)
print('parry_test OK' if not fails else f'parry_test FALLOS: {fails}')
sys.exit(1 if fails else 0)
