#!/usr/bin/env python3
"""build_all.py - regenera TODA la musica y los ambientes.
Uso:  python3 tools/audio_music/build_all.py [--only nombre ...] [--jobs 2] [--no-preview]
Salida: app/src/main/assets/audio/music/*.ogg, audio/sfx/amb_*.ogg, tools/audio_music/music_manifest.json
"""
import argparse, json, os, subprocess, sys, tempfile, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT_MUSIC = os.path.join(ROOT, "app", "src", "main", "assets", "audio", "music")
OUT_SFX = os.path.join(ROOT, "app", "src", "main", "assets", "audio", "sfx")
PREV = os.path.join(ROOT, "tools", "previews", "audio_music")
NOLOOP = {"mus_victory", "mus_gameover"}


def registry():
    import tracks_a, tracks_b, tracks_c
    try:
        import ambience
    except ImportError:
        ambience = type("m", (), {"TRACKS": {}})
    reg = {}
    reg.update({k: ("music", v) for k, v in tracks_a.TRACKS.items()})
    reg.update({k: ("music", v) for k, v in tracks_b.TRACKS.items()})
    reg.update({k: ("music", v) for k, v in tracks_c.TRACKS.items()})
    reg.update({k: ("amb", v) for k, v in ambience.TRACKS.items()})
    return reg


def encode(x, path, ch):
    import scipy.io.wavfile as wf
    with tempfile.TemporaryDirectory() as td:
        w = os.path.join(td, "in.wav")
        wf.write(w, 44100, x.astype(np.float32))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", w, "-c:a", "libvorbis", "-q:a", "4", "-ar", "44100",
                        "-ac", str(ch), path], check=True)


def decode(path, ch):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", str(ch), "-ar", "44100", "-"],
                       capture_output=True, check=True)
    a = np.frombuffer(r.stdout, dtype=np.float32).astype(np.float64)
    return a.reshape(-1, ch) if ch > 1 else a.reshape(-1, 1)


def build_one(name, preview=True):
    import analyze
    from dsp import SR
    kind, fn = registry()[name]
    t0 = time.time()
    x = fn()
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        x = x[:, None]
    ch = x.shape[1]
    loop = name not in NOLOOP
    if kind == "music":
        os.makedirs(OUT_MUSIC, exist_ok=True)
        path = os.path.join(OUT_MUSIC, name + ".ogg")
    else:
        os.makedirs(OUT_SFX, exist_ok=True)
        path = os.path.join(OUT_SFX, name + ".ogg")
    encode(x, path, ch)
    y = decode(path, ch)
    st = analyze.checks(name, x if ch > 1 else np.repeat(x, 2, 1), loop)
    st["ogg_bytes"] = os.path.getsize(path)
    st["ogg_dur"] = len(y) / SR
    st["ogg_peak_db"] = float(20 * np.log10(np.abs(y).max() + 1e-9))
    if loop:
        # continuidad en la union tras codificar: salto muestra a muestra entre final y principio del OGG decodificado
        d = np.abs(np.diff(y, axis=0)).max(1)
        st["ogg_loop_jump_vs_p99.5"] = float(np.abs(y[0] - y[-1]).max() / (np.percentile(d, 99.5) + 1e-9))
    if preview:
        analyze.preview(name, x if ch > 1 else x[:, 0], loop)
    st["kind"] = kind
    st["loop"] = loop
    st["render_s"] = round(time.time() - t0, 1)
    return name, st


def _job(a):
    return build_one(*a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--no-preview", action="store_true")
    a = ap.parse_args()
    reg = registry()
    names = a.only if a.only else list(reg.keys())
    for n in names:
        if n not in reg:
            sys.exit("no existe: " + n)
    os.makedirs(PREV, exist_ok=True)
    # los mas pesados primero
    order = sorted(names, key=lambda n: (reg[n][0] == "amb", n))
    res = {}
    if a.jobs > 1 and len(order) > 1:
        import multiprocessing as mp
        with mp.Pool(a.jobs) as p:
            for n, st in p.imap_unordered(_job, [(n, not a.no_preview) for n in order]):
                res[n] = st
                print(f"[{n}] {st['dur']:.2f}s  {st['peak']:.1f} dBFS  {st['lufs']:.1f} LUFS  {st['ogg_bytes']/1e3:.0f} kB  ({st['render_s']}s)", flush=True)
    else:
        for n in order:
            _, st = build_one(n, not a.no_preview)
            res[n] = st
            print(f"[{n}] {st['dur']:.2f}s  {st['peak']:.1f} dBFS  {st['lufs']:.1f} LUFS  {st['ogg_bytes']/1e3:.0f} kB  ({st['render_s']}s)", flush=True)
    # manifest (fusiona con ejecuciones parciales previas)
    mpath = os.path.join(HERE, "music_manifest.json")
    man = {"music": {}, "sfx": {}}
    if os.path.exists(mpath):
        try:
            man = json.load(open(mpath))
        except Exception:
            pass
    for n, st in res.items():
        if st["kind"] == "music":
            man["music"][n] = {"dur": round(st["ogg_dur"], 3), "loop": bool(st["loop"])}
        else:
            man["sfx"][n] = round(st["ogg_dur"], 3)
    man["music"] = dict(sorted(man["music"].items()))
    man["sfx"] = dict(sorted(man["sfx"].items()))
    json.dump(man, open(mpath, "w"), indent=1)
    rp = os.path.join(PREV, "report.json")
    old = {}
    if os.path.exists(rp):
        try:
            old = json.load(open(rp))
        except Exception:
            pass
    old.update(res)
    json.dump(old, open(rp, "w"), indent=1, default=float)
    tot = sum(f["ogg_bytes"] for f in old.values())
    print(f"total OGG: {tot/1e6:.2f} MB en {len(old)} archivos")


if __name__ == "__main__":
    main()
