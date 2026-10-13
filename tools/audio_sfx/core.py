import subprocess, os
import numpy as np
from scipy.ndimage import maximum_filter1d, uniform_filter1d
from dsp import SR, hp
import reg

OUT = '/home/claude/juego-roguelike/app/src/main/assets/audio/sfx'
PEAK_DB = -3.0


def maxdur_for(name):
    import re
    if name.startswith('ult_'):
        return 5.0
    if re.match(r'sk_\w+_[123]$', name):
        return 1.5
    if name.endswith('_hit') and name.startswith('sk_'):
        return 0.8
    if re.match(r'bs_\w+_intro$', name):
        return 4.0
    if re.match(r'bs_\w+_death$', name):
        return 5.0
    return 8.0


def finish(x, lvl=0.0, comp=0.5, maxdur=8.0):
    x = np.nan_to_num(np.asarray(x, float))
    x = hp(x, 18, 1)
    pk = np.max(np.abs(x)) + 1e-12
    x = x / pk
    # recorte de silencio inicial / final
    idx = np.where(np.abs(x) > 0.0015)[0]
    if len(idx) == 0:
        raise ValueError('silencio')
    a = max(0, idx[0] - int(0.0005 * SR))
    # cola: se corta donde la envolvente suavizada cae bajo -46 dB
    env = np.sqrt(np.maximum(uniform_filter1d(x ** 2, int(0.03 * SR)), 0))
    ib = np.where(env > 0.005)[0]
    b = min(len(x), ib[-1] + int(0.03 * SR)) if len(ib) else len(x)
    x = x[a:b]
    if len(x) > int(maxdur * SR):
        x = x[:int(maxdur * SR)]
        k = int(min(0.35, maxdur * .15) * SR)
        x[-k:] *= 0.5 + 0.5 * np.cos(np.pi * np.arange(k) / k)
    # compresion suave con lookahead (sube la energia de transitorios muy agudos)
    if comp:
        env = maximum_filter1d(np.abs(x), int(0.006 * SR))
        env = uniform_filter1d(env, int(0.006 * SR))
        thr = 0.4
        g = np.where(env > thr, (thr / (env + 1e-9)) ** comp, 1.0)
        g = uniform_filter1d(g, int(0.003 * SR))
        x = x * g
    # fundidos
    n = len(x)
    fi = min(int(0.002 * SR), n // 4)
    fo = min(int(0.012 * SR), n // 3)
    if fi:
        x[:fi] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(fi) / fi)
    if fo:
        x[-fo:] *= 0.5 + 0.5 * np.cos(np.pi * np.arange(fo) / fo)
    x = x / (np.max(np.abs(x)) + 1e-12) * 10 ** ((PEAK_DB + lvl) / 20)
    return x.astype(np.float32)


def render(name):
    fn, lvl = reg.REG[name]
    r = reg.rng_for(name)
    x = fn(r)
    return finish(x, lvl, maxdur=maxdur_for(name))


def encode(x, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    p = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                        '-c:a', 'libvorbis', '-q:a', '4', '-ar', str(SR), '-ac', '1', path],
                       input=x.tobytes(), capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode())


def build_one(name):
    x = render(name)
    encode(x, os.path.join(OUT, name + '.ogg'))
    return name, len(x) / SR
