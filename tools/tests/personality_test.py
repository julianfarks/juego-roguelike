#!/usr/bin/env python3
"""Animaciones de personalidad de los espadachines: recursos, comportamiento propio de cada clase, activacion natural en
la inactividad, interrupcion inmediata al actuar y reacciones a sucesos del juego (cofre, puerta, reliquia, jefe, poca vida).
Uso: python3 tools/tests/personality_test.py   (usa /tmp/run2.sh o tools/desktop/run.sh)"""
import os, re, subprocess, sys, json, hashlib
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
RUN = '/tmp/run2.sh' if os.path.exists('/tmp/run2.sh') else 'tools/desktop/run.sh'
CLASSES = ['paladin', 'shadow', 'flame', 'storm', 'frost', 'verdant', 'blood', 'earth', 'astral', 'steel']
IDLES = ['idle1', 'idle2', 'idle3', 'idle4']
fails = 0


def ck(name, ok, extra=''):
    global fails
    print(('ok   ' if ok else 'FAIL ') + name + (' ' + extra if extra and not ok else ''))
    if not ok:
        fails += 1


def run(cls, mode, frames, script=None):
    env = dict(os.environ, BOT_PERSONA=mode, BOT_CLASS=str(cls))
    cmd = [RUN, '--headless', '--bot', '--w', '480', '--frames', str(frames), '--store', f'/tmp/pers_t{cls}.json', '--shots', '/tmp/pers_t_shots']
    if script:
        cmd += ['--script', script]
    out = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=900)
    rows = []
    for l in (out.stdout + out.stderr).splitlines():
        m = re.match(r'PERSONA t=(\d+) f=(\d+) cls=(\w+) estado=(\d+) anim=(\w+) act=(\w+) frame=(\d+) hp=(-?\d+)', l)
        if m:
            rows.append(dict(t=int(m[1]), f=int(m[2]), cls=m[3], st=int(m[4]), anim=m[5], act=m[6], fr=int(m[7]), hp=int(m[8])))
    bad = [l for l in (out.stdout + out.stderr).splitlines() if 'EXCEPTION' in l or 'Exception' in l]
    return rows, bad


# ---- 1) recursos: hoja de personalidad por clase, comportamientos propios (siluetas distintas), nada recortado
A = 'app/src/main/assets/sprites'
sig = {}
for c in CLASSES:
    png, js = f'{A}/plx_{c}.png', f'{A}/plx_{c}.json'
    ok = os.path.exists(png) and os.path.exists(js)
    ck(f'{c}: existe la hoja de personalidad', ok)
    if not ok:
        continue
    d = json.load(open(js)); im = Image.open(png).convert('RGBA'); W, H = d['cell']
    for a in IDLES + ['chest', 'awe', 'touch', 'victory', 'weary']:
        r, n = d['anims'][a]['row'], d['anims'][a]['n']
        sig[(c, a)] = hashlib.md5(b''.join(im.crop((i * W, r * H, (i + 1) * W, (r + 1) * H)).getchannel('A').tobytes() for i in range(n))).hexdigest()
for a in IDLES + ['awe', 'victory']:
    hs = [sig[(c, a)] for c in CLASSES if (c, a) in sig]
    ck(f'{a}: cada espadachin tiene una silueta/animacion propia (no es el mismo movimiento recoloreado)', len(set(hs)) == len(hs))
for c in CLASSES:
    hs = [sig[(c, a)] for a in IDLES if (c, a) in sig]
    ck(f'{c}: sus 4 reposos son distintos entre si', len(set(hs)) == 4)
r = subprocess.run([sys.executable, 'tools/validate_assets.py'], capture_output=True, text=True)
ck('validate_assets sin errores (celdas, filas, sin recortes en el borde)', '0 errores' in r.stdout, r.stdout[-300:])

# ---- 2) inactividad: cada clase empieza reposos propios de forma natural (intervalo variable) y solo valores validos
intervals = set()
for i, c in enumerate(CLASSES):
    rows, bad = run(i, 'idle', 3300)
    ck(f'{c}: sin excepciones', not bad, str(bad[:2]))
    acts = [(x['f'], x['act']) for k, x in enumerate(rows) if x['act'] != 'null' and (k == 0 or rows[k - 1]['act'] == 'null')]
    names = [a for _, a in acts]
    ck(f'{c}: reproduce al menos 2 reposos distintos en 55 s quieto ({names})', len(set(names)) >= 2)
    ck(f'{c}: solo anima idle1-4', all(n in IDLES for n in names))
    if acts:
        ck(f'{c}: no empieza antes de 3 s quieto', acts[0][0] - rows[0]['f'] >= 170)
        intervals.add(acts[0][0] - rows[0]['f'])
    moving = [x for x in rows if x['act'] != 'null' and x['st'] != 0]
    ck(f'{c}: la animacion decorativa solo existe en estado de reposo', not moving)
ck('el primer reposo empieza en momentos distintos segun el personaje (intervalo variable)', len(intervals) >= 5)

# ---- 3) interrupcion inmediata: mover / atacar / saltar / esquivar cortan el reposo en el mismo fotograma
rows, _ = run(1, 'idle', 1500)
first = next((x for x in rows if x['act'] in IDLES), None)
ck('prueba de interrupcion: se encontro un reposo', first is not None)
if first:
    f0 = first['f']
    for key, label in (('D', 'moverse'), ('J', 'atacar'), ('W', 'saltar'), ('K', 'esquivar')):
        open('/tmp/pers_int.script', 'w').write(f'{f0 + 12} key {key} down\n{f0 + 40} key {key} up\n')
        rows2, _ = run(1, 'idle', 1500, '/tmp/pers_int.script')
        after = [x for x in rows2 if f0 + 12 <= x['f'] <= f0 + 30]
        before = [x for x in rows2 if f0 <= x['f'] < f0 + 12]
        ck(f'interrupcion al {label}: antes animaba {before[0]["act"] if before else "?"}, despues act=null',
           bool(before) and before[0]['act'] in IDLES and after and all(x['act'] == 'null' for x in after[1:]) and any(x['st'] != 0 for x in after))

# ---- 4) reacciones a sucesos (cofre, asombro, contacto, victoria, poca vida) y vuelta al reposo
rows, bad = run(2, 'react', 1000)
ck('reacciones: sin excepciones', not bad)
seen = [x['act'] for k, x in enumerate(rows) if x['act'] != 'null' and (k == 0 or rows[k - 1]['act'] != x['act'])]
for a in ('chest', 'awe', 'touch', 'victory'):
    ck(f'reaccion {a} se reproduce', a in seen)
ck('poca vida: postura cansada (weary) y vuelve a idle al curarse',
   any(x['anim'] == 'weary' and x['hp'] < 40 for x in rows) and rows[-1]['anim'] in ('idle', 'idle1', 'idle2', 'idle3', 'idle4'))
ck('weary solo con poca vida', all(x['hp'] < 40 for x in rows if x['anim'] == 'weary'))
ck('tras cada reaccion vuelve al reposo', rows[-1]['act'] == 'null' or rows[-1]['act'] in IDLES)

print('personality_test OK' if not fails else f'personality_test FALLOS: {fails}')
sys.exit(1 if fails else 0)
