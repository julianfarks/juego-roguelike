"""Mezcla de audio del trailer a partir de los .ogg ORIGINALES del juego (nunca se modifican; todo ocurre en memoria / en el proyecto de video).
Los sfx de las escenas se leen del registro (.audio.tsv) que escribe el grabador al capturar el gameplay real."""
import os, subprocess, numpy as np

SR = 48000
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AUD = os.path.join(ROOT, 'Shared', 'assets', 'audio')
_cache = {}


def _decode(path, ch):
    out = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(out, np.float32)
    return a.reshape(-1, ch) if ch > 1 else a


def sfx(name):
    if name not in _cache:
        _cache[name] = _decode(os.path.join(AUD, 'sfx', name + '.ogg'), 1)
    return _cache[name]


def music(name):
    k = 'mus:' + name
    if k not in _cache:
        _cache[k] = _decode(os.path.join(AUD, 'music', name + '.ogg'), 2)
    return _cache[k]


class Mix:
    def __init__(self, dur):
        self.n = int(dur * SR)
        self.buf = np.zeros((self.n, 2), np.float32)

    def add(self, sig, t, vol=1.0, pan=0.0, pitch=1.0):
        if pitch != 1.0 and sig.ndim == 1:
            idx = np.arange(0, len(sig) - 1, pitch)
            sig = np.interp(idx, np.arange(len(sig)), sig).astype(np.float32)
        s0 = int(round(t * SR))
        if sig.ndim == 1:
            ang = (np.clip(pan, -1, 1) + 1) * np.pi / 4
            sig = np.stack([sig * np.cos(ang), sig * np.sin(ang)], 1) * 1.4142
        a, b = max(0, s0), min(self.n, s0 + len(sig))
        if b > a:
            self.buf[a:b] += sig[a - s0:b - s0] * vol

    def add_music(self, name, src_start, t0, dur, vol=1.0, fade_in=0.0, fade_out=0.0):
        m = music(name)
        seg = m[int(src_start * SR):int((src_start + dur) * SR)].copy()
        n = len(seg)
        if fade_in > 0:
            k = min(n, int(fade_in * SR)); seg[:k] *= np.linspace(0, 1, k)[:, None]
        if fade_out > 0:
            k = min(n, int(fade_out * SR)); seg[n - k:] *= np.linspace(1, 0, k)[:, None]
        self.add(seg, t0, vol)

    def add_scene_sfx(self, tsv, src_start, src_end, t0, vol=0.9, skip=()):
        """Anade los sfx registrados durante el gameplay de la escena [src_start,src_end) (segundos del clip) en t0 de la linea de tiempo."""
        if not os.path.isfile(tsv):
            return 0
        n = 0
        for ln in open(tsv):
            p = ln.rstrip('\n').split('\t')
            if len(p) < 6 or p[1] != 'sfx':
                continue
            t = int(p[0]) / 60.0
            if t < src_start or t >= src_end or p[2] in skip:
                continue
            try:
                self.add(sfx(p[2]), t0 + (t - src_start), vol * float(p[3]), float(p[5]), float(p[4]))
                n += 1
            except Exception:
                pass
        return n

    def write(self, path, limit=0.97):
        x = self.buf
        pk = np.abs(x).max()
        # limitador suave
        x = np.tanh(x * (1.0 / max(pk, 1e-6)) * 1.2) / np.tanh(1.2) * limit if pk > limit else x
        pcm = (np.clip(x, -1, 1) * 32767).astype('<i2')
        with open(path, 'wb') as f:
            f.write(pcm.tobytes())
