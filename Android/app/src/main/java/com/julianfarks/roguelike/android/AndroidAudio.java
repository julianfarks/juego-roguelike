package com.julianfarks.roguelike.android;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.content.res.AssetManager;
import android.media.AudioAttributes;
import android.media.MediaPlayer;
import android.media.SoundPool;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Log;

import com.julianfarks.roguelike.core.Platform;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

/**
 * Audio Android: SoundPool para efectos y MediaPlayer para musica / ambiente.
 * Los metodos publicos pueden llamarse desde cualquier hilo (normalmente el de juego); todo el estado de
 * MediaPlayer se toca solo en el hilo principal (via Handler), asi que no hay carreras.
 */
public final class AndroidAudio implements Platform.Audio {
    private static final String TAG = "SWR";
    private static final long MIN_REPEAT_MS = 35;
    private static final long TICK_MS = 33;

    private final AssetManager assets;
    private final Handler main = new Handler(Looper.getMainLooper());

    // ---- efectos
    private SoundPool pool;
    private final Object sfxLock = new Object();
    private final HashMap<String, Sfx> sfxByName = new HashMap<String, Sfx>();
    private final HashMap<Integer, Sfx> sfxById = new HashMap<Integer, Sfx>();
    private volatile float sfxVol = 1f;

    private static final class Sfx {
        int id;                 // id de SoundPool (0 = no cargado/inexistente)
        volatile boolean loaded;
        boolean missing;
        long lastMs = -1000;
    }

    // ---- musica y ambiente (solo hilo principal)
    private static final class Track {
        MediaPlayer mp;
        String name;
        boolean ambient;
        float vol = 1f;   // volumen pedido
        float fade = 1f;  // 0..1 multiplicador del fundido
        int dir;          // +1 entrando, -1 saliendo, 0 estable
        float perMs;      // velocidad del fundido (1/fadeMs)
        boolean prepared;
        boolean released;
    }

    private final ArrayList<Track> tracks = new ArrayList<Track>(); // todos los vivos (incluye los que salen)
    private Track curMusic;
    private Track curAmbient;
    private float musicVol = 1f;
    private float sfxVolMain = 1f; // copia para el hilo principal (ambiente usa volumen de sfx)
    private boolean paused;
    private boolean tickScheduled;
    private long lastTickMs;
    private boolean destroyed;

    private final Runnable tick = new Runnable() {
        @Override public void run() {
            tickScheduled = false;
            doTick();
        }
    };

    public AndroidAudio(Context ctx) {
        assets = ctx.getAssets();
        try {
            AudioAttributes attrs = new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_GAME)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build();
            pool = new SoundPool.Builder().setMaxStreams(24).setAudioAttributes(attrs).build();
            pool.setOnLoadCompleteListener(new SoundPool.OnLoadCompleteListener() {
                @Override
                public void onLoadComplete(SoundPool sp, int sampleId, int status) {
                    synchronized (sfxLock) {
                        Sfx s = sfxById.get(sampleId);
                        if (s != null) {
                            if (status == 0) s.loaded = true; else s.missing = true;
                        }
                    }
                }
            });
        } catch (Throwable t) {
            Log.w(TAG, "SoundPool no disponible", t);
            pool = null;
        }
    }

    // ================================================================ efectos

    @Override
    public void preloadSfx(String[] names) {
        if (names == null) return;
        for (int i = 0; i < names.length; i++) {
            try {
                if (names[i] != null) obtain(names[i]);
            } catch (Throwable t) {
                Log.w(TAG, "preloadSfx", t);
            }
        }
    }

    /** Devuelve (creando y cargando si hace falta) el registro del efecto. */
    private Sfx obtain(String name) {
        synchronized (sfxLock) {
            Sfx s = sfxByName.get(name);
            if (s != null) return s;
            s = new Sfx();
            sfxByName.put(name, s);
            if (pool == null) { s.missing = true; return s; }
            AssetFileDescriptor afd = null;
            try {
                afd = assets.openFd("audio/sfx/" + name + ".ogg");
                int id = pool.load(afd, 1);
                if (id == 0) {
                    s.missing = true;
                } else {
                    s.id = id;
                    sfxById.put(id, s);
                }
            } catch (IOException e) {
                s.missing = true;
            } catch (Throwable t) {
                s.missing = true;
                Log.w(TAG, "sfx load " + name, t);
            } finally {
                if (afd != null) {
                    try { afd.close(); } catch (IOException ignored) { }
                }
            }
            return s;
        }
    }

    @Override
    public void sfx(String name, float vol, float pitch, float pan) {
        if (name == null || pool == null) return;
        try {
            Sfx s = obtain(name);
            if (s.missing || !s.loaded) return; // aun cargando (la primera vez se pierde) o inexistente
            long now = SystemClock.uptimeMillis();
            synchronized (sfxLock) {
                if (now - s.lastMs < MIN_REPEAT_MS) return;
                s.lastMs = now;
            }
            float v = clamp(vol, 0f, 1f) * sfxVol;
            if (v <= 0.001f) return;
            float p = clamp(pan, -1f, 1f);
            float left = v * (p > 0f ? 1f - p : 1f);
            float right = v * (p < 0f ? 1f + p : 1f);
            float rate = clamp(pitch, 0.5f, 2f);
            pool.play(s.id, left, right, 1, 0, rate);
        } catch (Throwable t) {
            Log.w(TAG, "sfx " + name, t);
        }
    }

    @Override
    public void setSfxVolume(final float v) {
        sfxVol = clamp(v, 0f, 1f);
        main.post(new Runnable() {
            @Override public void run() {
                sfxVolMain = sfxVol;
                for (int i = 0; i < tracks.size(); i++) if (tracks.get(i).ambient) applyVolume(tracks.get(i));
            }
        });
    }

    // ================================================================ musica

    @Override
    public void music(final String name, final boolean loop, final float vol, final int fadeMs) {
        main.post(new Runnable() {
            @Override public void run() {
                try { doMusic(name, loop, vol, fadeMs); } catch (Throwable t) { Log.w(TAG, "music " + name, t); }
            }
        });
    }

    @Override
    public void stopMusic(final int fadeMs) {
        main.post(new Runnable() {
            @Override public void run() {
                try {
                    if (curMusic != null) { fadeOut(curMusic, fadeMs); curMusic = null; }
                } catch (Throwable t) { Log.w(TAG, "stopMusic", t); }
            }
        });
    }

    @Override
    public void ambient(final String name, final float vol) {
        main.post(new Runnable() {
            @Override public void run() {
                try { doAmbient(name, vol); } catch (Throwable t) { Log.w(TAG, "ambient " + name, t); }
            }
        });
    }

    @Override
    public void setMusicVolume(final float v) {
        main.post(new Runnable() {
            @Override public void run() {
                musicVol = clamp(v, 0f, 1f);
                for (int i = 0; i < tracks.size(); i++) if (!tracks.get(i).ambient) applyVolume(tracks.get(i));
            }
        });
    }

    @Override
    public void pauseAll() {
        try { if (pool != null) pool.autoPause(); } catch (Throwable ignored) { }
        main.post(new Runnable() {
            @Override public void run() {
                paused = true;
                for (int i = 0; i < tracks.size(); i++) {
                    Track t = tracks.get(i);
                    try { if (t.prepared && t.mp.isPlaying()) t.mp.pause(); } catch (Throwable ignored) { }
                }
            }
        });
    }

    @Override
    public void resumeAll() {
        try { if (pool != null) pool.autoResume(); } catch (Throwable ignored) { }
        main.post(new Runnable() {
            @Override public void run() {
                if (destroyed) return;
                paused = false;
                for (int i = 0; i < tracks.size(); i++) {
                    Track t = tracks.get(i);
                    try { if (t.prepared && !t.mp.isPlaying()) t.mp.start(); } catch (Throwable ignored) { }
                }
                lastTickMs = SystemClock.uptimeMillis();
            }
        });
    }

    /** Libera todo. Llamar desde onDestroy (hilo principal). */
    public void release() {
        destroyed = true;
        main.removeCallbacksAndMessages(null);
        for (int i = tracks.size() - 1; i >= 0; i--) releaseTrack(tracks.get(i));
        tracks.clear();
        curMusic = null;
        curAmbient = null;
        synchronized (sfxLock) {
            try { if (pool != null) pool.release(); } catch (Throwable ignored) { }
            pool = null;
            sfxByName.clear();
            sfxById.clear();
        }
    }

    // ---------------------------------------------------------------- internos (hilo principal)

    private void doMusic(String name, boolean loop, float vol, int fadeMs) {
        if (destroyed || name == null) return;
        vol = clamp(vol, 0f, 1f);
        if (curMusic != null && !curMusic.released && curMusic.name.equals(name)) {
            curMusic.vol = vol; // misma pista: no reinicia
            applyVolume(curMusic);
            return;
        }
        Track old = curMusic;
        curMusic = null;
        if (old != null) fadeOut(old, fadeMs);
        Track t = open(name, false, loop, vol, fadeMs, "audio/music/" + name + ".ogg", null);
        curMusic = t;
    }

    private void doAmbient(String name, float vol) {
        if (destroyed) return;
        vol = clamp(vol, 0f, 1f);
        if (name == null) {
            if (curAmbient != null) { fadeOut(curAmbient, 400); curAmbient = null; }
            return;
        }
        if (curAmbient != null && !curAmbient.released && curAmbient.name.equals(name)) {
            curAmbient.vol = vol;
            applyVolume(curAmbient);
            return;
        }
        Track old = curAmbient;
        curAmbient = null;
        if (old != null) fadeOut(old, 400);
        curAmbient = open(name, true, true, vol, 500,
                "audio/sfx/" + name + ".ogg", "audio/music/" + name + ".ogg");
    }

    /** Crea y prepara un reproductor. Devuelve null si el archivo no existe o falla. */
    private Track open(String name, boolean ambient, boolean loop, float vol, int fadeMs, String path1, String path2) {
        AssetFileDescriptor afd = null;
        try {
            try {
                afd = assets.openFd(path1);
            } catch (IOException e) {
                if (path2 == null) throw e;
                afd = assets.openFd(path2);
            }
        } catch (IOException e) {
            return null; // no existe: se ignora
        }
        final Track t = new Track();
        t.name = name;
        t.ambient = ambient;
        t.vol = vol;
        if (fadeMs > 0) {
            t.fade = 0f;
            t.dir = 1;
            t.perMs = 1f / fadeMs;
        }
        MediaPlayer mp = null;
        try {
            mp = new MediaPlayer();
            t.mp = mp;
            mp.setAudioAttributes(new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_GAME)
                    .setContentType(ambient ? AudioAttributes.CONTENT_TYPE_SONIFICATION : AudioAttributes.CONTENT_TYPE_MUSIC)
                    .build());
            mp.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getLength());
            mp.setLooping(loop);
            mp.setOnPreparedListener(new MediaPlayer.OnPreparedListener() {
                @Override public void onPrepared(MediaPlayer m) {
                    if (t.released) return;
                    t.prepared = true;
                    applyVolume(t);
                    if (!paused) {
                        try { m.start(); } catch (Throwable ignored) { }
                    }
                }
            });
            mp.setOnErrorListener(new MediaPlayer.OnErrorListener() {
                @Override public boolean onError(MediaPlayer m, int what, int extra) {
                    Log.w(TAG, "MediaPlayer error " + what + "/" + extra + " en " + t.name);
                    dropTrack(t);
                    return true;
                }
            });
            if (!loop) {
                mp.setOnCompletionListener(new MediaPlayer.OnCompletionListener() {
                    @Override public void onCompletion(MediaPlayer m) { dropTrack(t); }
                });
            }
            applyVolume(t);
            mp.prepareAsync();
            tracks.add(t);
            if (t.dir != 0) scheduleTick();
            return t;
        } catch (Throwable e) {
            Log.w(TAG, "open " + name, e);
            t.released = true;
            if (mp != null) { try { mp.release(); } catch (Throwable ignored) { } }
            return null;
        } finally {
            try { afd.close(); } catch (IOException ignored) { }
        }
    }

    private void dropTrack(Track t) {
        if (curMusic == t) curMusic = null;
        if (curAmbient == t) curAmbient = null;
        tracks.remove(t);
        releaseTrack(t);
    }

    private void fadeOut(Track t, int fadeMs) {
        if (t == null || t.released) return;
        if (fadeMs <= 0) {
            dropTrack(t);
            return;
        }
        t.dir = -1;
        t.perMs = 1f / fadeMs;
        scheduleTick();
    }

    private void releaseTrack(Track t) {
        if (t.released) return;
        t.released = true;
        MediaPlayer mp = t.mp;
        if (mp == null) return;
        try { mp.setOnPreparedListener(null); } catch (Throwable ignored) { }
        try { mp.setOnErrorListener(null); } catch (Throwable ignored) { }
        try { mp.setOnCompletionListener(null); } catch (Throwable ignored) { }
        try { mp.release(); } catch (Throwable ignored) { }
    }

    private void applyVolume(Track t) {
        if (t.released || t.mp == null) return;
        float v = t.vol * t.fade * (t.ambient ? sfxVolMain : musicVol);
        v = clamp(v, 0f, 1f);
        try { t.mp.setVolume(v, v); } catch (Throwable ignored) { }
    }

    private void scheduleTick() {
        if (tickScheduled || destroyed) return;
        tickScheduled = true;
        lastTickMs = SystemClock.uptimeMillis();
        main.postDelayed(tick, TICK_MS);
    }

    private void doTick() {
        long now = SystemClock.uptimeMillis();
        float dt = now - lastTickMs;
        lastTickMs = now;
        boolean more = false;
        for (int i = tracks.size() - 1; i >= 0; i--) {
            Track t = tracks.get(i);
            if (t.released) { tracks.remove(i); continue; }
            if (t.dir == 0) continue;
            t.fade += t.dir * dt * t.perMs;
            if (t.dir > 0 && t.fade >= 1f) {
                t.fade = 1f;
                t.dir = 0;
                applyVolume(t);
            } else if (t.dir < 0 && t.fade <= 0f) {
                t.fade = 0f;
                if (curMusic == t) curMusic = null;
                if (curAmbient == t) curAmbient = null;
                tracks.remove(i);
                releaseTrack(t);
            } else {
                applyVolume(t);
                more = true;
            }
        }
        if (more) scheduleTick();
    }

    private static float clamp(float v, float lo, float hi) {
        if (v != v) return lo; // NaN
        return v < lo ? lo : (v > hi ? hi : v);
    }
}
