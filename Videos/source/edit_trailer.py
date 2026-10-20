#!/usr/bin/env python3
"""Monta y renderiza un trailer (ES o EN) de exactamente 40 s, 1920x1080, 60 fps, H.264 + AAC estereo.
Uso:  python3 edit_trailer.py es|en|nt SALIDA.mp4 [--clips DIR] [--audio-only] [--preview]
  es / en: textos en ese idioma sobre el gameplay grabado con el juego en ese idioma (clips/es, clips/en).
  nt: sin textos promocionales (gameplay en espanol), para futuras traducciones.
Entrada: clips de gameplay real grabados con capture_clips.sh (carpeta --clips, por defecto ./clips) y storyboard.py.
Los pixeles se escalan SIEMPRE por vecino mas cercano y solo a escalas enteras del pixel nativo (x4, x5, x6, x8): nunca se deforman. Nada de los .ogg ni de los sprites originales se modifica."""
import os, sys, subprocess, math, random
import numpy as np
from PIL import Image
import pixtext, mixer
import storyboard as SB

W, H, FPS, DUR = 1920, 1080, 60, 40.0
NF = int(round(DUR * FPS))


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


ZOOMS = (1.0, 1.25, 1.5, 2.0)      # pixel nativo a x4, x5, x6, x8: siempre un numero entero de pixeles de pantalla


def snap_zoom(z):
    return min(ZOOMS, key=lambda q: abs(q - z))


def zoom_crop(fr, z, fx, fy, dx=0, dy=0):
    """Recorta centrado en el foco (fx,fy en 0..1) con zoom z (ajustado a una escala entera del pixel nativo) y reescala a 1920x1080
    con vecino mas cercano. dx, dy desplazan la camara (paneo/temblor) en pixeles de pantalla."""
    z = snap_zoom(z)
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


def draw_band(fr, cy, h, k):
    """Placa oscura con bordes suaves (fundido vertical) detras del texto: separa el mensaje del juego sin tapar la interfaz."""
    y0 = max(0, int(cy - h / 2)); y1 = min(H, int(cy + h / 2))
    if y1 <= y0 or k <= 0:
        return
    n = y1 - y0
    prof = np.minimum(np.linspace(0, 1, n), np.linspace(1, 0, n)) * 5
    prof = np.clip(prof, 0, 1)[:, None, None] * k
    reg = fr[y0:y1].astype(np.float32)
    fr[y0:y1] = (reg * (1 - prof)).astype(np.uint8)


def draw_texts(fr, t, lang):
    if lang == 'nt':
        return
    for tx in SB.TEXTS:
        s = tx['t0']; e = tx['t1']
        if not (s <= t < e):
            continue
        parts = tx[lang].split('|')
        lt = t - s
        a_in = min(lt / 0.15, 1.0)
        a_out = min((e - t) / 0.25, 1.0)
        alpha = a_in * a_out
        sc = 1.0; dx = dy = 0
        bump = 0
        if tx.get('anim', 'slam') == 'slam':
            bump = 2 if lt < 0.05 else 1 if lt < 0.1 else 0     # entrada: escala entera +2, +1 y la definitiva (pixeles nitidos)
            if lt < 0.14:
                amp = 7 * (1 - lt / 0.14)
                dx = random.randint(-int(amp), int(amp)); dy = random.randint(-int(amp), int(amp))
        elif tx.get('anim') == 'rise':
            dy = int(40 * (1 - ease_out(lt / 0.35)))
        imgs = []
        for pi, part in enumerate(parts):
            base = tx['scale'] if pi == 0 else tx.get('ss', 3)
            sc_i = base + (bump if pi == 0 else 0)
            while sc_i > 2 and pixtext.width_px(part, sc_i) > W - 120:     # nunca se sale: baja a la escala entera que cabe
                sc_i -= 1
            r = get_text(part, sc_i, tx.get('glow', 10) if pi == 0 else 4)
            imgs.append((r, 1.0))
        gap = 14
        hs = [int(r.shape[0] * sc * f) for r, f in imgs]
        total = sum(hs) + gap * (len(imgs) - 1)
        if tx.get('band', 0) > 0:
            draw_band(fr, tx['y'] + dy, total + 90, tx['band'] * alpha)
        yy = tx['y'] - total / 2
        for (r, f), h in zip(imgs, hs):
            pixtext.blit(fr, r, W // 2 + tx.get('x', 0), yy + h / 2, alpha, sc * f, dx, dy)
            yy += h + gap


def build_frame(src, lt, shot, tl):
    z0, z1 = shot.get('zoom', (1.0, 1.0))
    k = min(lt / max(shot['dur'], 1e-3), 1.0)
    z = z0 if k < shot.get('zoom_at', 0.5) else z1          # acercamiento por corte (escala entera), nunca un zoom continuo que deforme
    dx = dy = 0
    px0, px1 = shot.get('pan', (0, 0))                       # paneo de camara en pixeles nativos (multiplos de 4 en pantalla)
    dx += int(round(px0 + (px1 - px0) * k)) * 4
    sh = shot.get('shake', 0)
    if sh and lt < shot.get('shake_t', 0.35):
        a = sh * (1 - lt / shot.get('shake_t', 0.35))
        dx += random.randint(-int(a), int(a)); dy += random.randint(-int(a), int(a))
    fx, fy = shot.get('focus', (0.5, 0.5))
    fr = zoom_crop(src, z, fx, fy, dx, dy)
    fl = shot.get('flash')
    if fl and lt < 0.08 and shot['dur'] > 0.5:          # destello corto y suave en el corte (no tapa el gameplay)
        col, amt = fl
        k = 0.5 * amt * (1 - lt / 0.08)
        fr = (fr * (1 - k) + np.array(col, np.float32) * k).astype(np.uint8)
    fd = shot.get('fade_in')
    if fd and lt < fd:
        k = (lt / fd) ** 1.5              # el trailer abre desde negro
        fr = (fr * k).astype(np.uint8)
    dk = shot.get('dark')
    if dk:
        fr = (fr * (1.0 - dk)).astype(np.uint8)
    return fr


def render_audio(lang, clips, out_raw):
    mx = mixer.Mix(DUR)
    SB.audio(mx, lang, clips)
    mx.write(out_raw)


def main():
    lang = sys.argv[1]; out = sys.argv[2]
    root = './clips'
    if '--clips' in sys.argv:
        root = sys.argv[sys.argv.index('--clips') + 1]
    clips = os.path.join(root, 'en' if lang == 'en' else 'es')      # el trailer ingles usa el juego grabado en ingles
    random.seed(7)
    raw = out + '.audio.raw'
    render_audio(lang, os.path.join(root, 'es'), raw)                # misma mezcla en todas las versiones (partidas identicas)
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
            for o0, o1, fn in getattr(SB, 'OVERLAYS', []):
                if o0 <= t < o1:
                    fr = fn(fr, t)
            draw_texts(fr, t, lang)
            enc.stdin.write(fr.tobytes())
            f += 1
        rd.close()
    enc.stdin.close(); enc.wait()
    print('listo', out, f, 'frames')


if __name__ == '__main__':
    main()
