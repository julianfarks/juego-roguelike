import os, json, subprocess
import numpy as np
from dsp import SR
import core

PREV = '/home/claude/juego-roguelike/tools/previews/audio_sfx'


def decode(path):
    p = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True)
    return np.frombuffer(p.stdout, np.float32).astype(float)


def stats(name):
    x = decode(os.path.join(core.OUT, name + '.ogg'))
    pk = np.max(np.abs(x))
    act = x[np.abs(x) > 0.01 * pk]
    rms = np.sqrt(np.mean(act ** 2)) if len(act) else 0
    lead = np.argmax(np.abs(x) > 0.02 * pk) / SR * 1000
    src = core.render(name)  # el click se juzga sobre la senal antes de Vorbis (el codec anade pre-eco)
    head = abs(float(src[0])) / (np.max(np.abs(src)) + 1e-12)
    tail = abs(float(src[-1])) / (np.max(np.abs(src)) + 1e-12)
    pre = float(np.max(np.abs(x[:int(0.001 * SR)])) / pk)
    X = np.abs(np.fft.rfft(x * np.hanning(len(x)))) + 1e-9
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    cen = float((fr * X).sum() / X.sum())
    d = dict(name=name, dur=len(x) / SR, peak_db=20 * np.log10(pk + 1e-12), rms_db=20 * np.log10(rms + 1e-12),
             dc=float(np.mean(x)), lead_ms=lead, head=head, tail=tail, clip=int(np.sum(np.abs(x) > 0.995)), cent=cen, pre=pre)
    flags = []
    if d['peak_db'] > -1.5:
        flags.append('PICO')
    if abs(d['dc']) > 0.005:
        flags.append('DC')
    if head > 0.003:
        flags.append('CLIC_INI')
    if tail > 0.003:
        flags.append('CLIC_FIN')
    if lead > 200:
        flags.append('SILENCIO_INI')
    if d['clip']:
        flags.append('CLIP')
    d['flags'] = flags
    return d, x


def sheets(names, per=12):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    os.makedirs(PREV, exist_ok=True)
    allnames = sorted(n[:-4] for n in os.listdir(core.OUT) if n.endswith('.ogg'))
    touched = set()

    def grp(n):
        return '_'.join(n.split('_')[:2]) if n.startswith('bs_') else n.split('_')[0]
    for n in names:
        touched.add(grp(n))
    names = [n for n in allnames if grp(n) in touched]
    groups = {}
    for n in names:
        g = n.split('_')[0] if not n.startswith(('bs_', 'sk_', 'ult_', 'swing_', 'hit_', 'en_')) else '_'.join(n.split('_')[:2]) if n.startswith('bs_') else n.split('_')[0]
        groups.setdefault(g, []).append(n)
    pages = {}
    for g, lst in groups.items():
        pages.setdefault(g, []).extend(lst)
    for g, lst in pages.items():
        for pi in range(0, len(lst), per):
            chunk = lst[pi:pi + per]
            cols = 4
            rows = (len(chunk) + cols - 1) // cols
            fig = plt.figure(figsize=(20, 3.6 * rows), dpi=55)
            for k, n in enumerate(chunk):
                x = decode(os.path.join(core.OUT, n + '.ogg'))
                c, r_ = k % cols, k // cols
                w = 0.23
                x0 = 0.02 + c * 0.245
                y0 = 1 - (r_ + 1) / rows
                axs = fig.add_axes([x0, y0 + 0.30 / rows, w, 0.50 / rows])
                axs.specgram(x, NFFT=1024, Fs=SR, noverlap=768, cmap='magma', vmin=-120, vmax=-20)
                axs.set_ylim(0, 16000)
                axs.set_xticks([])
                axs.tick_params(labelsize=6)
                axs.set_title(n, fontsize=9)
                axw = fig.add_axes([x0, y0 + 0.08 / rows, w, 0.20 / rows])
                axw.plot(np.arange(len(x)) / SR, x, lw=.4, color='k')
                axw.set_ylim(-1, 1)
                axw.set_xlim(0, len(x) / SR)
                axw.tick_params(labelsize=6)
            fig.savefig(os.path.join(PREV, f'sheet_{g}_{pi // per + 1}.png'))
            plt.close(fig)


def run(names, make_sheets=True):
    os.makedirs(PREV, exist_ok=True)
    rows = []
    for n in names:
        try:
            d, _ = stats(n)
            rows.append(d)
        except Exception as e:  # noqa
            rows.append(dict(name=n, flags=['ERR ' + str(e)], dur=0, peak_db=0, rms_db=0, cent=0))
    json.dump(rows, open(os.path.join(PREV, 'report.json'), 'w'), indent=1, default=float)
    bad = [r for r in rows if r['flags']]
    for r in bad:
        print('  AVISO', r['name'], r['flags'], f"pk={r['peak_db']:.1f} lead={r.get('lead_ms',0):.0f}ms head={r.get('head',0):.3f} tail={r.get('tail',0):.3f}")
    tot = sum(os.path.getsize(os.path.join(core.OUT, n + '.ogg')) for n in names if os.path.exists(os.path.join(core.OUT, n + '.ogg')))
    print(f'analisis: {len(rows)} sonidos, {len(bad)} con aviso, {tot/1e6:.2f} MB')
    if make_sheets:
        sheets(names)
