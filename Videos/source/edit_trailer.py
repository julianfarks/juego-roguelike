#!/usr/bin/env python3
"""Monta y renderiza un trailer (ES o EN) de exactamente 30 s, 1920x1080, 60 fps, H.264 + AAC estereo.
Uso:  python3 edit_trailer.py es|en SALIDA.mp4 [--clips DIR] [--audio-only] [--preview]
Entrada: clips de gameplay real grabados con capture_clips.sh (carpeta --clips, por defecto ./clips) y storyboard.py.
Los pixeles se escalan SIEMPRE por vecino mas cercano. Nada de los .ogg ni de los sprites originales se modifica."""
import os, sys, subprocess, math, random
import numpy as np
from PIL import Image
import pixtext, mixer
import storyboard as SB

W, H, FPS, DUR = 1920, 1080, 60, 30.0
NF = int(round(DUR * FPS))


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def zoom_crop(fr, z, fx, fy, dx=0, dy=0):
    """Recorta centrado en el foco (fx,fy en 0..1) con zoom z y reescala a 1920x1080 con vecino mas cercano."""
    if abs(z - 1.0) < 1e-4 and dx == 0 and dy == 0:
        return fr
    cw, ch = W / z, H / z
    x0 = min(max(fx * W - cw / 2 + dx, 0), W - cw)
    y0 = min(max(fy * H - ch / 2 + dy, 0), H - ch)
    xs = (x0 + (np.arange(W) + 0.5) * cw / W).astype(np.int32).clip(0, W - 1)
    ys = (y0 + (np.arange(H) + 0.5) * ch / H).astype(np.int32).clip(0, H - 1)
    return fr[ys][:, xs]


class ShotReader:
    def __init__(self, clip, ss, dur, clips):
        self.p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-ss', '%.4f' % ss, '-i', os.path.join(clips, clip + '.mp4'), '-t', '%.4f' % (dur + 0.05),
                                   '-vf', 'fps=60', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        self.last = np.zeros((H, W, 3), np.uint8)

    def read(self):
        b = self.p.stdout.read(W * H * 3)
        if len(b) == W * H * 3:
            self.last = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
        return self.last

    def close(self):
        try:
            self.p.stdout.close(); self.p.kill()
        except Exception:
            pass


def text_cache():
    return {}


_tc = {}


def get_text(txt, scale, glow):
    k = (txt, scale, glow)
    if k not in _tc:
        _tc[k] = pixtext.render(txt, scale, glow_r=glow)
    return _tc[k]


def draw_texts(fr, t, lang):
    for tx in SB.TEXTS:
        s = tx['t0']; e = tx['t1']
        if not (s <= t < e):
            continue
        txt = tx[lang]
        lt = t - s
        a_in = min(lt / 0.12, 1.0)
        a_out = min((e - t) / 0.18, 1.0)
        alpha = a_in * a_out
        sc = 1.0; dx = dy = 0
        if tx.get('anim', 'slam') == 'slam':
            sc = 1.0 + 0.55 * (1 - ease_out(lt / 0.22))
            if lt < 0.18:
                amp = 14 * (1 - lt / 0.18)
                dx = random.randint(-int(amp), int(amp)); dy = random.randint(-int(amp), int(amp))
        elif tx.get('anim') == 'rise':
            dy = int(40 * (1 - ease_out(lt / 0.35)))
        rgba = get_text(txt, tx['scale'], tx.get('glow', 10))
        # maximo ancho de pantalla
        if rgba.shape[1] * sc > W - 80:
            sc = (W - 80) / rgba.shape[1]
        pixtext.blit(fr, rgba, W // 2 + tx.get('x', 0), tx['y'], alpha, sc, dx, dy)


def build_frame(src, lt, shot, tl):
    z0, z1 = shot.get('zoom', (1.0, 1.0))
    z = z0 + (z1 - z0) * min(lt / max(shot['dur'], 1e-3), 1.0)
    dx = dy = 0
    sh = shot.get('shake', 0)
    if sh and lt < shot.get('shake_t', 0.35):
        a = sh * (1 - lt / shot.get('shake_t', 0.35))
        dx = random.uniform(-a, a); dy = random.uniform(-a, a)
        z = max(z, 1.06)
    fx, fy = shot.get('focus', (0.5, 0.5))
    fr = zoom_crop(src, z, fx, fy, dx, dy)
    fl = shot.get('flash')
    if fl and lt < 0.12:
        col, amt = fl
        k = amt * (1 - lt / 0.12)
        fr = (fr * (1 - k) + np.array(col, np.float32) * k).astype(np.uint8)
    fd = shot.get('fade_in')
    if fd and lt < fd:
        k = 0.25 + 0.75 * (lt / fd)       # nunca llega a negro puro
        fr = (fr * k).astype(np.uint8)
    return fr


def render_audio(lang, clips, out_raw):
    mx = mixer.Mix(DUR)
    SB.audio(mx, lang, clips)
    mx.write(out_raw)


def main():
    lang = sys.argv[1]; out = sys.argv[2]
    clips = './clips'
    if '--clips' in sys.argv:
        clips = sys.argv[sys.argv.index('--clips') + 1]
    random.seed(7)
    raw = out + '.audio.raw'
    render_audio(lang, clips, raw)
    if '--audio-only' in sys.argv:
        return
    vf = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
          '-f', 's16le', '-ar', '48000', '-ac', '2', '-i', raw,
          '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', str(FPS),
          '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-t', '%.3f' % DUR, '-movflags', '+faststart', out]
    if '--preview' in sys.argv:
        vf[vf.index('-crf') + 1] = '28'; vf[vf.index('slow')] = 'veryfast'
    enc = subprocess.Popen(vf, stdin=subprocess.PIPE)
    shots = SB.SHOTS
    f = 0
    for si, shot in enumerate(shots):
        n = int(round(shot['dur'] * FPS))
        if si == len(shots) - 1:
            n = NF - f
        rd = ShotReader(shot['clip'], shot['ss'], shot['dur'], clips)
        for i in range(n):
            if f >= NF:
                break
            t = f / FPS
            src = rd.read()
            lt = i / FPS
            fr = build_frame(src, lt, shot, t)
            if shot.get('overlay'):
                fr = shot['overlay'](fr, lt, t, lang)
            draw_texts(fr, t, lang)
            enc.stdin.write(fr.tobytes())
            f += 1
        rd.close()
    enc.stdin.close(); enc.wait()
    print('listo', out, f, 'frames')


if __name__ == '__main__':
    main()
