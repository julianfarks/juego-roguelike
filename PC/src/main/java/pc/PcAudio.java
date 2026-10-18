package pc;

import com.julianfarks.roguelike.core.Platform;

import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.DataLine;
import javax.sound.sampled.SourceDataLine;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Audio real de PC: un mezclador por software (44,1 kHz, estereo, 16 bits) sobre una unica SourceDataLine de Java Sound.
 * - Efectos: se decodifican una vez (OGG) a memoria y se mezclan con volumen, tono (remuestreo lineal) y panoramica.
 * - Musica y ambiente: se decodifican en streaming; cambio de pista con fundido cruzado y bucle.
 * El OGG se lee con el SPI de Java Sound (vorbisspi + jorbis, dependencias de ejecucion); los WAV funcionan sin nada extra.
 * Si no hay dispositivo de audio el mezclador no arranca y todo es silencioso sin errores.
 */
final class PcAudio implements Platform.Audio {
    static final int RATE = 44100;
    private static final int CHUNK = 512;                        // fotogramas por pasada de mezcla (~11,6 ms)

    private final File sfxDir, musicDir;
    private final Object lock = new Object();
    private final Map<String, Pcm> cache = new ConcurrentHashMap<String, Pcm>();
    private final Set<String> loading = ConcurrentHashMap.newKeySet();
    private final Set<String> failed = ConcurrentHashMap.newKeySet();
    private final ExecutorService decoder = Executors.newSingleThreadExecutor(new java.util.concurrent.ThreadFactory() {
        @Override public Thread newThread(Runnable r) { Thread t = new Thread(r, "pc-audio-decode"); t.setDaemon(true); return t; }
    });
    private final List<Voice> voices = new ArrayList<Voice>();
    private final List<Stream> streams = new ArrayList<Stream>();   // musica y ambiente (activos o desvaneciendose)
    private Stream music, ambient;
    private volatile float musicVol = 1f, sfxVol = 1f;
    private volatile boolean paused;
    private SourceDataLine line;
    private volatile boolean running;
    volatile boolean available;

    PcAudio(File assets) {
        sfxDir = new File(assets, "audio/sfx");
        musicDir = new File(assets, "audio/music");
    }

    /** Abre el dispositivo y lanza el hilo de mezcla. Devuelve false si no hay audio (el juego sigue sin sonido). */
    boolean start() {
        try {
            AudioFormat fmt = new AudioFormat(RATE, 16, 2, true, false);
            DataLine.Info info = new DataLine.Info(SourceDataLine.class, fmt);
            if (!AudioSystem.isLineSupported(info)) { PcLog.info("audio: sin dispositivo de salida; el juego se ejecuta sin sonido"); return false; }
            line = (SourceDataLine) AudioSystem.getLine(info);
            line.open(fmt, CHUNK * 4 * 4);                       // ~46 ms de bufer
            line.start();
        } catch (Throwable t) {
            PcLog.err("audio: no se pudo abrir el dispositivo", t);
            line = null;
            return false;
        }
        running = true;
        available = true;
        Thread th = new Thread(new Runnable() { @Override public void run() { mixLoop(); } }, "pc-audio-mix");
        th.setDaemon(true);
        th.setPriority(Thread.MAX_PRIORITY - 1);
        th.start();
        return true;
    }

    void stop() {
        running = false;
        decoder.shutdownNow();
        SourceDataLine l = line;
        if (l != null) { try { l.stop(); l.close(); } catch (Throwable ignored) { } }
    }

    // ------------------------------------------------------------------ decodificacion
    static final class Pcm {
        final short[] data;      // intercalado si hay 2 canales
        final int ch;
        final int frames;
        final float rate;
        Pcm(short[] d, int ch, float rate) { data = d; this.ch = ch; frames = d.length / ch; this.rate = rate; }
    }

    /** Abre un archivo de audio y lo entrega como PCM 16 bits little endian (decodifica OGG con el SPI). */
    static AudioInputStream openPcm(File f) throws Exception {
        AudioInputStream raw = AudioSystem.getAudioInputStream(f);
        AudioFormat sf = raw.getFormat();
        if (sf.getEncoding() == AudioFormat.Encoding.PCM_SIGNED && sf.getSampleSizeInBits() == 16 && !sf.isBigEndian()) return raw;
        AudioFormat pcm = new AudioFormat(AudioFormat.Encoding.PCM_SIGNED, sf.getSampleRate(), 16, sf.getChannels(), sf.getChannels() * 2, sf.getSampleRate(), false);
        return AudioSystem.getAudioInputStream(pcm, raw);
    }

    static Pcm decode(File f) throws Exception {
        AudioInputStream in = openPcm(f);
        try {
            AudioFormat fm = in.getFormat();
            ByteArrayOutputStream bo = new ByteArrayOutputStream(1 << 16);
            byte[] buf = new byte[16384];
            int n, zeros = 0;
            while ((n = in.read(buf, 0, buf.length)) != -1) {      // el decodificador OGG puede devolver 0 sin haber terminado
                if (n > 0) { bo.write(buf, 0, n); zeros = 0; }
                else if (++zeros > 2000) break;
            }
            byte[] b = bo.toByteArray();
            short[] s = new short[b.length / 2];
            for (int i = 0; i < s.length; i++) s[i] = (short) ((b[2 * i] & 0xFF) | (b[2 * i + 1] << 8));
            return new Pcm(s, Math.max(1, Math.min(2, fm.getChannels())), fm.getSampleRate());
        } finally { in.close(); }
    }

    private Pcm sfxPcm(final String name) {
        Pcm p = cache.get(name);
        if (p != null || failed.contains(name)) return p;
        if (loading.add(name)) {
            decoder.execute(new Runnable() {
                @Override public void run() {
                    try {
                        File f = new File(sfxDir, name + ".ogg");
                        if (f.isFile()) cache.put(name, decode(f)); else failed.add(name);
                    } catch (Throwable t) { failed.add(name); PcLog.err("audio: no se pudo decodificar sfx " + name, t); }
                    loading.remove(name);
                }
            });
        }
        return null;
    }

    // ------------------------------------------------------------------ Platform.Audio
    @Override
    public void preloadSfx(String[] names) {
        if (names == null) return;
        for (String n : names) if (n != null) sfxPcm(n);
    }

    private static final class Voice {
        final Pcm pcm;
        double pos;
        final double step;
        final float l, r;
        Voice(Pcm p, float vol, float pitch, float pan) {
            pcm = p;
            step = (p.rate / RATE) * pitch;
            float pn = Math.max(-1f, Math.min(1f, pan));
            l = vol * (pn > 0 ? 1f - pn * 0.7f : 1f);
            r = vol * (pn < 0 ? 1f + pn * 0.7f : 1f);
        }
    }

    @Override
    public void sfx(String name, float vol, float pitch, float pan) {
        if (!available || name == null || paused) return;
        Pcm p = sfxPcm(name);
        if (p == null) return;                                   // aun decodificando: se pierde este disparo, el siguiente suena
        float v = Math.max(0f, Math.min(1f, vol)) * sfxVol;
        if (v <= 0.001f) return;
        synchronized (lock) {
            if (voices.size() >= 40) voices.remove(0);          // limite de voces simultaneas
            voices.add(new Voice(p, v, Math.max(0.5f, Math.min(2f, pitch)), pan));
        }
    }

    /** Pista en streaming (musica o ambiente) con fundido. */
    private final class Stream {
        final String name;
        final boolean loop, amb;
        final File file;
        float vol, gain, target, rate;           // gain 0..1 (fundido), rate = cambio de gain por segundo
        AudioInputStream in;
        int ch = 2;
        final byte[] bytes = new byte[CHUNK * 4];
        boolean dead;

        Stream(String name, File f, boolean loop, boolean amb, float vol, int fadeMs) {
            this.name = name; this.file = f; this.loop = loop; this.amb = amb; this.vol = vol;
            gain = fadeMs > 0 ? 0f : 1f; target = 1f; rate = fadeMs > 0 ? 1000f / fadeMs : 1000f;
            reopen();
        }

        void reopen() {
            try {
                if (in != null) in.close();
                in = openPcm(file);
                ch = Math.max(1, Math.min(2, in.getFormat().getChannels()));
                if (Math.abs(in.getFormat().getSampleRate() - RATE) > 1) PcLog.info("audio: " + file.getName() + " no esta a 44100 Hz (" + in.getFormat().getSampleRate() + ")");
            } catch (Throwable t) {
                PcLog.err("audio: no se pudo abrir " + file.getName(), t);
                dead = true;
            }
        }

        void fadeOut(int ms) { target = 0f; rate = ms > 0 ? 1000f / ms : 1000f; }

        /** Suma `frames` fotogramas al mezclador (mix estereo intercalado). */
        void mixInto(float[] mix, int frames, float master, float dt) {
            if (dead) return;
            // fundido
            if (gain < target) gain = Math.min(target, gain + rate * dt);
            else if (gain > target) gain = Math.max(target, gain - rate * dt);
            int need = frames * ch * 2, got = 0, reopens = 0, zeros = 0;
            try {
                while (got < need) {
                    int n = in.read(bytes, got, need - got);
                    if (n == 0) { if (++zeros > 2000) { dead = true; break; } continue; }   // sin datos aun (decodificador): reintenta
                    if (n < 0) {
                        if (loop && reopens++ < 2) { reopen(); if (dead) return; continue; }     // bucle: vuelve al principio
                        dead = true;
                        break;
                    }
                    got += n;
                }
            } catch (Throwable t) { dead = true; }
            float g = vol * gain * master / 32768f;
            int fr = got / (ch * 2);
            if (ch == 2) {
                for (int i = 0; i < fr; i++) {
                    int o = i * 4;
                    mix[2 * i] += (short) ((bytes[o] & 0xFF) | (bytes[o + 1] << 8)) * g;
                    mix[2 * i + 1] += (short) ((bytes[o + 2] & 0xFF) | (bytes[o + 3] << 8)) * g;
                }
            } else {
                for (int i = 0; i < fr; i++) {
                    int o = i * 2;
                    float s = (short) ((bytes[o] & 0xFF) | (bytes[o + 1] << 8)) * g;
                    mix[2 * i] += s; mix[2 * i + 1] += s;
                }
            }
            if (target == 0f && gain == 0f) dead = true;
        }

        void close() { try { if (in != null) in.close(); } catch (Throwable ignored) { } }
    }

    private File findAudio(String name, boolean preferMusic) {
        File a = new File(musicDir, name + ".ogg"), b = new File(sfxDir, name + ".ogg");
        File[] order = preferMusic ? new File[]{a, b} : new File[]{b, a};
        for (File f : order) if (f.isFile()) return f;
        return null;
    }

    @Override
    public void music(String name, boolean loop, float vol, int fadeMs) {
        if (!available || name == null) return;
        synchronized (lock) {
            if (music != null && !music.dead && music.name.equals(name) && music.loop == loop && music.target > 0f) { music.vol = vol; return; }
            File f = findAudio(name, true);
            if (music != null) music.fadeOut(fadeMs);
            music = null;
            if (f == null) return;
            Stream s = new Stream(name, f, loop, false, vol, fadeMs);
            if (!s.dead) { streams.add(s); music = s; }
        }
    }

    @Override
    public void stopMusic(int fadeMs) {
        synchronized (lock) { if (music != null) music.fadeOut(fadeMs); music = null; }
    }

    @Override
    public void ambient(String name, float vol) {
        if (!available) return;
        synchronized (lock) {
            if (name == null) { if (ambient != null) ambient.fadeOut(500); ambient = null; return; }
            if (ambient != null && !ambient.dead && ambient.name.equals(name) && ambient.target > 0f) { ambient.vol = vol; return; }
            File f = findAudio(name, false);
            if (ambient != null) ambient.fadeOut(500);
            ambient = null;
            if (f == null) return;
            Stream s = new Stream(name, f, true, true, vol, 600);
            if (!s.dead) { streams.add(s); ambient = s; }
        }
    }

    @Override public void setMusicVolume(float v) { musicVol = Math.max(0f, Math.min(1f, v)); }
    @Override public void setSfxVolume(float v) { sfxVol = Math.max(0f, Math.min(1f, v)); }
    @Override public void pauseAll() { paused = true; }
    @Override public void resumeAll() { paused = false; }

    // ------------------------------------------------------------------ mezcla
    private void mixLoop() {
        float[] mix = new float[CHUNK * 2];
        byte[] out = new byte[CHUNK * 4];
        final float dt = CHUNK / (float) RATE;
        while (running) {
            java.util.Arrays.fill(mix, 0f);
            if (!paused) {
                synchronized (lock) {
                    for (int v = voices.size() - 1; v >= 0; v--) {
                        Voice vo = voices.get(v);
                        Pcm p = vo.pcm;
                        double pos = vo.pos;
                        short[] d = p.data;
                        boolean mono = p.ch == 1;
                        int last = p.frames - 1;
                        boolean done = false;
                        for (int i = 0; i < CHUNK; i++) {
                            int ip = (int) pos;
                            if (ip >= last) { done = true; break; }
                            float fr = (float) (pos - ip);
                            float a, b;
                            if (mono) {
                                float s0 = d[ip], s1 = d[ip + 1];
                                a = b = (s0 + (s1 - s0) * fr) / 32768f;
                            } else {
                                float l0 = d[2 * ip], l1 = d[2 * ip + 2], r0 = d[2 * ip + 1], r1 = d[2 * ip + 3];
                                a = (l0 + (l1 - l0) * fr) / 32768f;
                                b = (r0 + (r1 - r0) * fr) / 32768f;
                            }
                            mix[2 * i] += a * vo.l;
                            mix[2 * i + 1] += b * vo.r;
                            pos += vo.step;
                        }
                        vo.pos = pos;
                        if (done) voices.remove(v);
                    }
                    for (int s = streams.size() - 1; s >= 0; s--) {
                        Stream st = streams.get(s);
                        st.mixInto(mix, CHUNK, st.amb ? sfxVol : musicVol, dt);
                        if (st.dead) { st.close(); streams.remove(s); if (music == st) music = null; if (ambient == st) ambient = null; }
                    }
                }
            }
            for (int i = 0; i < CHUNK * 2; i++) {
                float x = mix[i];
                int s = (int) (x * 32767f);
                if (s > 32767) s = 32767; else if (s < -32768) s = -32768;
                out[2 * i] = (byte) s;
                out[2 * i + 1] = (byte) (s >> 8);
            }
            try {
                line.write(out, 0, out.length);                  // bloquea al ritmo del dispositivo
            } catch (Throwable t) {
                PcLog.err("audio: fallo al escribir en el dispositivo", t);
                running = false;
                available = false;
            }
        }
    }
}
