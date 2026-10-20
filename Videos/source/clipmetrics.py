"""Metricas por clip (10 muestras/s) para elegir planos limpios: fraccion de pixeles blancos (destellos de golpe que tapan al jefe)
y brillo medio (tintes de pantalla completa). Solo ayuda a elegir el inicio de cada plano; no modifica nada."""
import os, subprocess, sys, json
import numpy as np


def metrics(path, cache_dir='/tmp/metrics'):
    os.makedirs(cache_dir, exist_ok=True)
    key = os.path.join(cache_dir, os.path.basename(os.path.dirname(path)) + '_' + os.path.basename(path) + '.npy')
    if os.path.isfile(key) and os.path.getmtime(key) > os.path.getmtime(path):
        return np.load(key)
    W, H = 160, 90
    b = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-vf', 'fps=10,scale=%d:%d:flags=area' % (W, H), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                       capture_output=True).stdout
    a = np.frombuffer(b, np.uint8).reshape(-1, H, W, 3)[:, 8:76]      # sin la barra superior ni el HUD inferior
    white = ((a > 225).all(axis=3)).mean(axis=(1, 2))
    bright = a.mean(axis=(1, 2, 3)) / 255.0
    m = np.stack([white, bright], 1)
    np.save(key, m)
    return m


def score(m, ss, dur):
    i0, i1 = int(ss * 10), max(int(ss * 10) + 1, int((ss + dur) * 10))
    seg = m[i0:i1]
    if len(seg) == 0:
        return 9.0
    return float(seg[:, 0].mean() * 30 + seg[:, 0].max() * 6 + max(0.0, seg[:, 1].mean() - 0.22) * 3)


def best(path, ss, dur, search=0.6):
    m = metrics(path)
    cands = [ss + d / 10 for d in range(-int(search * 10), int(search * 10) + 1)]
    cands = [c for c in cands if c >= 0 and (c + dur) * 10 < len(m)]
    return min(cands, key=lambda c: (score(m, c, dur), abs(c - ss)))


if __name__ == '__main__':
    for p in sys.argv[1:]:
        m = metrics(p); print(p, len(m))
