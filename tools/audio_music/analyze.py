"""analyze.py - previews (waveform + espectrograma) y chequeos de calidad."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal
from dsp import SR, lufs, peak_db, loop_report

PREV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "previews", "audio_music")


def preview(name, x, loop=True):
    os.makedirs(PREV, exist_ok=True)
    x = np.asarray(x, dtype=np.float64)
    mono = x.mean(1) if x.ndim == 2 else x
    t = np.arange(len(mono)) / SR
    fig, ax = plt.subplots(3, 1, figsize=(13, 7.5), gridspec_kw={"height_ratios": [1, 1.6, 0.6]})
    ax[0].plot(t, x[:, 0] if x.ndim == 2 else x, lw=0.3, color="#2060c0")
    if x.ndim == 2:
        ax[0].plot(t, x[:, 1], lw=0.3, color="#c04020", alpha=0.6)
    ax[0].set_ylim(-1, 1)
    ax[0].axhline(10 ** (-2 / 20), color="r", lw=0.5)
    ax[0].axhline(-10 ** (-2 / 20), color="r", lw=0.5)
    ax[0].set_title(f"{name}  {len(mono)/SR:.1f}s  peak {peak_db(x):.1f} dBFS  {lufs(x if x.ndim==2 else np.stack([x,x],1)):.1f} LUFS")
    f, tt, S = signal.spectrogram(mono, SR, nperseg=2048, noverlap=1536)
    ax[1].pcolormesh(tt, f, 10 * np.log10(S + 1e-12), vmin=-120, vmax=-40, cmap="magma", shading="auto")
    ax[1].set_yscale("symlog", linthresh=500)
    ax[1].set_ylim(30, 20000)
    # envolvente RMS
    hop = int(0.05 * SR)
    n = len(mono) // hop
    rms = np.sqrt((mono[:n * hop].reshape(n, hop) ** 2).mean(1))
    ax[2].plot(np.arange(n) * 0.05, 20 * np.log10(rms + 1e-6), color="k", lw=0.8)
    ax[2].set_ylim(-60, 0)
    ax[2].set_ylabel("RMS dB")
    fig.tight_layout()
    fig.savefig(os.path.join(PREV, name + ".png"), dpi=80)
    plt.close(fig)


def checks(name, x, loop):
    x = np.asarray(x, dtype=np.float64)
    st = {"name": name, "dur": len(x) / SR, "peak": float(peak_db(x)), "lufs": float(lufs(x)),
          "nan": bool(np.isnan(x).any())}
    # clipping: muestras en el techo
    st["clip_frac"] = float((np.abs(x) > 0.99).mean())
    # silencios: ventanas de 0.5 s con RMS < -55 dB
    k = int(0.5 * SR)
    m = len(x) // k
    r = 20 * np.log10(np.sqrt((x[:m * k].reshape(m, k, -1) ** 2).mean((1, 2))) + 1e-9)
    st["min_rms_db"] = float(r.min())
    st["silences"] = int((r < -55).sum())
    # clics: salto de muestra enorme respecto a la mediana local
    d = np.abs(np.diff(x, axis=0)).max(1)
    med = np.median(d)
    st["max_step_over_p99.9"] = float(d.max() / (np.percentile(d, 99.9) + 1e-9))
    # balance espectral
    mono = x.mean(1)
    F = np.abs(np.fft.rfft(mono)) ** 2
    fr = np.fft.rfftfreq(len(mono), 1 / SR)
    tot = F.sum()
    st["bands"] = {k2: round(float(F[(fr >= a) & (fr < b)].sum() / tot), 3) for k2, (a, b) in
                   {"<80": (0, 80), "80-250": (80, 250), "250-1k": (250, 1000), "1-4k": (1000, 4000), ">4k": (4000, 22050)}.items()}
    if x.ndim == 2:
        mid = x.mean(1)
        side = (x[:, 0] - x[:, 1]) / 2
        st["side_db"] = float(10 * np.log10((side ** 2).mean() / ((mid ** 2).mean() + 1e-12) + 1e-12))
    if loop:
        st["loop"] = {k2: float(v) for k2, v in loop_report(x).items()}
    return st
