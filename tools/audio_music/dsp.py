"""dsp.py - nucleo de sintesis / mezcla / masterizacion (numpy + scipy)."""
import numpy as np
from scipy import signal
from scipy.ndimage import minimum_filter1d, uniform_filter1d

SR = 44100
TS = 4096
NB = 12


def tarr(n):
    return np.arange(n, dtype=np.float64) / SR


def mtof(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=np.float64) - 69.0) / 12.0)


def dbv(x):
    return 10.0 ** (x / 20.0)


# ---------------------------------------------------------------- wavetables
_TABLES = {}


def _build_tables():
    x = np.arange(TS) / TS
    for kind in ("saw", "square", "tri"):
        arr = []
        for b in range(NB):
            top = 16.0 * 2 ** (b + 1)
            nh = int(max(1, min(TS // 2 - 1, 19800.0 / top)))
            h = np.arange(1, nh + 1, dtype=np.float64)
            if kind == "saw":
                a = 1.0 / h
            elif kind == "square":
                a = np.where(h % 2 == 1, 1.0 / h, 0.0)
            else:
                a = np.where(h % 2 == 1, (1.0 / h ** 2) * np.where(((h - 1) // 2) % 2 == 0, 1, -1), 0.0)
            w = (np.sin(2 * np.pi * np.outer(x, h)) * a[None, :]).sum(1)
            w /= np.abs(w).max() + 1e-12
            arr.append(np.concatenate([w, w[:1]]))
        _TABLES[kind] = arr


_build_tables()


def osc(kind, f, n, phase0=0.0):
    f = np.asarray(f, dtype=np.float64)
    if f.ndim == 0:
        fmax = float(f)
        ph = phase0 + (fmax / SR) * np.arange(n)
    else:
        fmax = float(f.max())
        ph = phase0 + np.cumsum(f[:n]) / SR
    b = int(np.clip(np.floor(np.log2(max(fmax, 16.0) / 16.0)), 0, NB - 1))
    tbl = _TABLES[kind][b]
    ph = ph - np.floor(ph)
    idx = ph * TS
    i0 = idx.astype(np.int64)
    fr = idx - i0
    return tbl[i0] * (1 - fr) + tbl[i0 + 1] * fr


def sine(f, n, phase0=0.0):
    f = np.asarray(f, dtype=np.float64)
    if f.ndim == 0:
        ph = phase0 + (float(f) / SR) * np.arange(n)
    else:
        ph = phase0 + np.cumsum(f[:n]) / SR
    return np.sin(2 * np.pi * ph)


# ---------------------------------------------------------------- filtros
_SOS = {}


def _get(btype, wn, order):
    key = (btype, tuple(np.round(wn, 1)) if isinstance(wn, (list, tuple)) else round(wn, 1), order)
    s = _SOS.get(key)
    if s is None:
        if isinstance(wn, (list, tuple)):
            w = [min(max(v, 8.0), 0.46 * SR) / (SR / 2) for v in wn]
            if w[1] <= w[0]:
                w[1] = min(w[0] * 1.2, 0.99)
        else:
            w = min(max(wn, 8.0), 0.46 * SR) / (SR / 2)
        s = signal.butter(order, w, btype=btype, output="sos")
        _SOS[key] = s
    return s


def lp(x, fc, order=2):
    if fc >= 0.46 * SR:
        return x
    return signal.sosfilt(_get("lowpass", float(fc), order), x, axis=0)


def hp(x, fc, order=2):
    return signal.sosfilt(_get("highpass", float(fc), order), x, axis=0)


def bp(x, f1, f2, order=2):
    f2 = min(f2, 0.45 * SR)
    return signal.sosfilt(_get("bandpass", [float(f1), float(f2)], order), x, axis=0)


def bpq(x, fc, q=4.0, order=2):
    bw = fc / q
    return bp(x, max(fc - bw / 2, 10), fc + bw / 2, order)


def csos(sos, x):
    n = len(x)
    y = np.concatenate([x, x, x], 0)
    y = signal.sosfilt(sos, y, axis=0)
    return y[n:2 * n]


def clp(x, fc, order=2):
    return csos(_get("lowpass", float(fc), order), x)


def chp(x, fc, order=2):
    return csos(_get("highpass", float(fc), order), x)


def cbp(x, f1, f2, order=2):
    return csos(_get("bandpass", [float(f1), float(f2)], order), x)


# ---------------------------------------------------------------- envolventes
def adsr(n, dur, a, d, s, r, curve=1.0):
    t = tarr(n)
    a = max(a, 0.002)
    p1 = a
    p2 = a + max(d, 1e-4)
    p3 = max(dur, p2 + 1e-4)
    p4 = p3 + max(r, 0.005)
    e = np.interp(t, [0, p1, p2, p3, p4], [0, 1, s, s, 0])
    if curve != 1.0:
        e = e ** curve
    return e


def expdec(n, tau, a=0.001):
    t = tarr(n)
    return np.exp(-t / tau) * np.minimum(1.0, t / max(a, 1e-4))


def fade_edges(x, ms_in=2.0, ms_out=6.0):
    n = len(x)
    a = min(int(ms_in * SR / 1000), n // 2)
    b = min(int(ms_out * SR / 1000), n // 2)
    x = x.copy()
    if a > 0:
        r = np.linspace(0, 1, a)
        x[:a] *= r[:, None] if x.ndim == 2 else r
    if b > 0:
        r = np.linspace(1, 0, b)
        x[-b:] *= r[:, None] if x.ndim == 2 else r
    return x


def pan2(x, p):
    th = (np.clip(p, -1, 1) + 1) * np.pi / 4
    return np.stack([x * np.cos(th), x * np.sin(th)], axis=1)


def balance(st, p):
    th = (np.clip(p, -1, 1) + 1) * np.pi / 4
    return st * np.array([np.sqrt(2) * np.cos(th), np.sqrt(2) * np.sin(th)])[None, :]


def softclip(x, d=1.0):
    return np.tanh(x * d) / d


def smooth_noise(n, rng, cutoff_hz):
    """ruido de baja frecuencia en [-1,1] aprox (modulacion organica)."""
    w = rng.standard_normal(n + 2000)
    sos = _get("lowpass", float(cutoff_hz), 2)
    y = signal.sosfilt(sos, w)[2000:]
    return y / (np.abs(y).max() + 1e-9)


# ---------------------------------------------------------------- reverb
IR_PRESETS = {
    # rt_low, rt_mid, rt_high, predelay, lp, seed
    "cathedral": (7.2, 5.6, 2.6, 0.030, 7000, 11),
    "hall": (3.8, 3.0, 1.5, 0.020, 9000, 12),
    "cave": (5.2, 3.6, 1.0, 0.015, 4500, 13),
    "room": (0.9, 0.7, 0.4, 0.006, 11000, 14),
    "plate": (2.3, 2.1, 1.9, 0.004, 14000, 15),
    "ice": (4.6, 4.2, 3.6, 0.020, 15000, 16),
    "void": (9.0, 7.0, 3.5, 0.040, 6000, 17),
    "chamber": (1.9, 1.5, 0.8, 0.010, 10000, 18),
    "short": (0.45, 0.35, 0.2, 0.003, 9000, 19),
}
_IRS = {}


def make_ir(kind):
    if kind in _IRS:
        return _IRS[kind]
    rl, rm, rh, pre, lpc, seed = IR_PRESETS[kind]
    rng = np.random.default_rng(seed)
    n = int(max(rl, rm) * 1.12 * SR)
    t = tarr(n)
    out = np.zeros((n, 2))
    ln = 6.9078
    for ch in range(2):
        w = rng.standard_normal(n)
        low = lp(w, 320)
        mid = bp(w, 320, 3200)
        hi = hp(w, 3200)
        sig = (low * 1.6 * np.exp(-ln * t / rl) + mid * np.exp(-ln * t / rm) + hi * np.exp(-ln * t / rh))
        sig *= 1 - np.exp(-t / 0.015)
        # reflexiones tempranas
        for k in range(14):
            tau = rng.uniform(0.004, 0.11)
            i = int(tau * SR)
            sig[i] += rng.choice([-1, 1]) * rng.uniform(0.6, 2.2) * (1 - tau * 6)
        sig = lp(sig, lpc)
        p = int(pre * SR)
        out[:, ch] = np.concatenate([np.zeros(p), sig])[:n]
    out /= np.sqrt((out ** 2).sum(0))[None, :]
    _IRS[kind] = out.astype(np.float32)
    return _IRS[kind]


def reverb(send, kind, loop=True):
    """send: (N,2). Devuelve la cola humeda (N,2). loop=True -> convolucion circular."""
    ir = make_ir(kind)
    n = len(send)
    if loop:
        S = np.fft.rfft(send, n=n, axis=0)
        if len(ir) > n:
            irc = np.zeros((n, 2))
            for i in range(0, len(ir), n):
                seg = ir[i:i + n]
                irc[:len(seg)] += seg
        else:
            irc = ir
        H = np.fft.rfft(irc, n=n, axis=0)
        return np.fft.irfft(S * H, n=n, axis=0)
    out = np.empty((n, 2))
    for c in range(2):
        out[:, c] = signal.fftconvolve(send[:, c], ir[:, c])[:n]
    return out


# ---------------------------------------------------------------- dinamica
def compress(x, thr=-20.0, ratio=2.5, att=0.015, rel=0.3, block=256, circular=True):
    n = len(x)
    nb = -(-n // block)
    pk = np.abs(x).max(axis=1)
    pk = np.pad(pk, (0, nb * block - n)).reshape(nb, block).max(1)
    lvl = 20 * np.log10(pk + 1e-9)
    target = (-(np.maximum(lvl - thr, 0.0)) * (1 - 1 / ratio)).tolist()
    ac = float(np.exp(-block / (att * SR)))
    rc = float(np.exp(-block / (rel * SR)))
    g = [0.0] * nb
    s = 0.0
    for p in range(2 if circular else 1):
        for i in range(nb):
            tg = target[i]
            if tg < s:
                s = ac * s + (1 - ac) * tg
            else:
                s = rc * s + (1 - rc) * tg
            g[i] = s
    g = np.array(g)
    ext = np.concatenate([g[-2:], g, g[:2]]) if circular else np.concatenate([g[:1], g[:1], g, g[-1:], g[-1:]])
    cen = (np.arange(-2, nb + 2) + 0.5) * block
    gs = np.interp(np.arange(n), cen, ext)
    return x * (10 ** (gs / 20.0))[:, None]


def limiter(x, ceil=0.794, look=0.004, circular=True):
    w = 2 * int(look * SR) + 1
    pk = np.abs(x).max(axis=1)
    g = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
    mode = "wrap" if circular else "nearest"
    m = minimum_filter1d(g, size=w, mode=mode)
    gs = uniform_filter1d(m, size=w, mode=mode)
    y = x * gs[:, None]
    return np.clip(y, -ceil, ceil)


def _kw(fs):
    f0 = 1681.974450955533
    G = 3.999843853973347
    Q = 0.7071752369554196
    K = np.tan(np.pi * f0 / fs)
    Vh = 10 ** (G / 20)
    Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    b = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]
    a = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    f1 = 38.13547087602444
    Q1 = 0.5003270373238773
    K1 = np.tan(np.pi * f1 / fs)
    a0 = 1 + K1 / Q1 + K1 * K1
    b2 = [1, -2, 1]
    a2 = [1, 2 * (K1 * K1 - 1) / a0, (1 - K1 / Q1 + K1 * K1) / a0]
    return (b, a), (b2, a2)


def lufs(x):
    (b, a), (b2, a2) = _kw(SR)
    y = signal.lfilter(b, a, x, axis=0)
    y = signal.lfilter(b2, a2, y, axis=0)
    blk = int(0.4 * SR)
    hop = int(0.1 * SR)
    if len(y) < blk:
        ms = (y ** 2).mean(0).sum()
        return -0.691 + 10 * np.log10(ms + 1e-12)
    p = np.concatenate([np.zeros((1, y.shape[1])), np.cumsum(y ** 2, axis=0)])
    starts = np.arange(0, len(y) - blk + 1, hop)
    z = ((p[starts + blk] - p[starts]) / blk).sum(1)
    l = -0.691 + 10 * np.log10(z + 1e-12)
    keep = z[l > -70]
    if len(keep) == 0:
        return -70.0
    rel = -0.691 + 10 * np.log10(keep.mean()) - 10
    keep2 = z[l > rel]
    if len(keep2) == 0:
        keep2 = keep
    return -0.691 + 10 * np.log10(keep2.mean() + 1e-12)


def peak_db(x):
    return 20 * np.log10(np.abs(x).max() + 1e-12)


def normalize(x, target_lufs=-14.0, peak=-2.0, circular=True):
    ceil = dbv(peak)
    y = x
    gain = dbv(target_lufs - lufs(x))
    for _ in range(5):
        y = limiter(x * gain, ceil, circular=circular)
        err = target_lufs - lufs(y)
        if abs(err) < 0.25:
            break
        gain *= dbv(err * 0.9)
    return y


def master(x, loop=True, comp=(-18.0, 2.0), sat=1.25, target=-14.0, peak=-2.0, lowcut=24.0):
    if loop:
        x = csos(_get("highpass", lowcut, 2), x)
    else:
        x = hp(x, lowcut)
    x = compress(x, comp[0], comp[1], circular=loop)
    m = np.abs(x).max()
    x = x / (m + 1e-9) * 0.8
    x = softclip(x, sat)
    x = compress(x, -12.0, 1.5, att=0.005, rel=0.12, circular=loop)
    return normalize(x, target, peak, circular=loop)


def loop_report(x):
    """continuidad en la union: RMS de los ultimos/primeros 50 ms y salto de muestra."""
    k = int(0.05 * SR)
    rl = np.sqrt((x[-k:] ** 2).mean())
    rf = np.sqrt((x[:k] ** 2).mean())
    jump = np.abs(x[0] - x[-1]).max()
    d = np.abs(np.diff(x, axis=0)).max(1)
    typical = np.percentile(d, 99.5)
    return dict(rms_end_db=20 * np.log10(rl + 1e-9), rms_start_db=20 * np.log10(rf + 1e-9),
                jump=float(jump), p995_step=float(typical))
