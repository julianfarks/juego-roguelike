package pc;

import com.julianfarks.roguelike.core.Pad;
import com.julianfarks.roguelike.core.Platform;
import com.julianfarks.roguelike.core.VideoCfg;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.PrintWriter;
import java.util.concurrent.locks.LockSupport;

/**
 * Punto de entrada de SwordsmanMagic: Eternal Abyss para PC (Windows).
 *
 *   SwordsmanMagic.exe                 juego normal
 *   SwordsmanMagic.exe --selftest      prueba de arranque sin ventana (CI): recursos, decodificacion OGG, motor 300 fotogramas
 *   opciones: --assets DIR  --data DIR  --windowed  --no-audio  --no-pad
 *
 * El motor (paquete core) es el mismo que en Android: simula a 60 pasos por segundo fijos. El limite de FPS decide cuantos de esos
 * fotogramas se dibujan (60 o 30).
 */
public final class PcMain implements PcWindow.Host {
    private static final long TICK_NS = 1_000_000_000L / 60L;

    private final Object lock = new Object();
    private Platform.GameLoop game;
    private PcWindow window;
    private volatile boolean running = true;

    @Override public Object lock() { return lock; }
    @Override public Platform.GameLoop game() { return game; }
    @Override public void requestClose() { running = false; }

    @Override
    public void toggleFullscreen() {
        VideoCfg c = VideoCfg.cur.copy();
        c.mode = c.mode == VideoCfg.MODE_WINDOW ? VideoCfg.MODE_BORDERLESS : VideoCfg.MODE_WINDOW;
        if (window.apply(c)) VideoCfg.cur = c;
        if (plat != null) VideoCfg.save(plat, c);
    }

    private PcPlatform plat;

    public static void main(String[] args) {
        String assets = null, data = null;
        boolean selftest = false, windowed = false, noAudio = false, noPad = false;
        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "--assets": assets = args[++i]; break;
                case "--data": data = args[++i]; break;
                case "--selftest": selftest = true; break;
                case "--windowed": windowed = true; break;
                case "--no-audio": noAudio = true; break;
                case "--no-pad": noPad = true; break;
                default: break;
            }
        }
        File dataDir = data != null ? new File(data) : defaultDataDir();
        PcLog.toFile(dataDir);
        PcLog.info("SwordsmanMagic: Eternal Abyss (PC) · java " + System.getProperty("java.version") + " · " + System.getProperty("os.name"));
        // el exe no tiene consola: cualquier fallo queda en log.txt y se muestra en un cuadro
        try {
            if (selftest) System.setProperty("java.awt.headless", "true");
            // pixel art: sin escalado por DPI del sistema (la ventana trabaja en pixeles reales)
            if (System.getProperty("sun.java2d.uiScale") == null) System.setProperty("sun.java2d.uiScale", "1");
            File assetsDir = findAssets(assets);
            if (assetsDir == null) throw new IllegalStateException("No se encuentra la carpeta de recursos (assets).");
            PcMain m = new PcMain();
            if (selftest) System.exit(m.selfTest(assetsDir, dataDir));
            m.run(assetsDir, dataDir, windowed, noAudio, noPad);
            System.exit(0);
        } catch (Throwable t) {
            PcLog.err("fallo fatal", t);
            try {
                if (!selftest) javax.swing.JOptionPane.showMessageDialog(null, "No se pudo iniciar el juego:\n" + t + "\n\nDetalles en: " + new File(dataDir, "log.txt"),
                        "SwordsmanMagic: Eternal Abyss", javax.swing.JOptionPane.ERROR_MESSAGE);
            } catch (Throwable ignored) { }
            System.exit(1);
        }
    }

    static File defaultDataDir() {
        String os = System.getProperty("os.name", "").toLowerCase();
        String appData = System.getenv("APPDATA");
        if (os.contains("win") && appData != null) return new File(appData, "SwordsmanMagic-EternalAbyss");
        return new File(System.getProperty("user.home", "."), ".swordsmanmagic-eternal-abyss");
    }

    /** Carpeta de recursos: argumento, "assets" junto al programa (instalado) o Shared/assets (desarrollo). */
    static File findAssets(String arg) {
        if (arg != null) return new File(arg);
        try {
            File jar = new File(PcMain.class.getProtectionDomain().getCodeSource().getLocation().toURI());
            File dir = jar.isFile() ? jar.getParentFile() : jar;
            for (File d = dir; d != null; d = d.getParentFile()) {
                File a = new File(d, "assets");
                if (new File(a, "audio/manifest.json").isFile()) return a;
                File s = new File(d, "Shared/assets");
                if (new File(s, "audio/manifest.json").isFile()) return s;
            }
        } catch (Throwable ignored) { }
        File a = new File("assets"), s = new File("Shared/assets");
        if (new File(a, "audio/manifest.json").isFile()) return a;
        if (new File(s, "audio/manifest.json").isFile()) return s;
        return null;
    }

    // ------------------------------------------------------------------ juego normal
    void run(File assetsDir, File dataDir, boolean forceWindowed, boolean noAudio, boolean noPad) throws Exception {
        final File storeFile = new File(dataDir, "pc_settings.properties");
        window = new PcWindow(this, false);
        PcAudio audio = noAudio ? null : new PcAudio(assetsDir);
        plat = new PcPlatform(assetsDir, storeFile, audio, new PcVideo(window));

        VideoCfg cfg = VideoCfg.load(plat);
        if (plat.store().get("pc_video", "").isEmpty()) {            // primer arranque: ventana del mayor multiplo entero que cabe
            int[] d = window.defaultRes();
            cfg.resW = d[0]; cfg.resH = d[1];
            VideoCfg.cur = cfg.copy();
        }
        if (forceWindowed) cfg.mode = VideoCfg.MODE_WINDOW;
        game = new com.julianfarks.roguelike.core.Game();
        window.open(cfg);
        if (audio != null) audio.start();
        final PcXInput pad = noPad ? null : PcXInput.tryCreate();
        final Pad.Sink padSink = new Pad.Sink() {
            @Override public void key(int code, boolean down) { synchronized (lock) { game.key(code, down); } }
        };
        Runtime.getRuntime().addShutdownHook(new Thread(new Runnable() { @Override public void run() { window.restoreDisplay(); } }));

        synchronized (lock) {
            game.init(plat);
            window.layoutSize();
            game.resize(window.viewW());
        }

        long next = System.nanoTime();
        long tick = 0;
        int errors = 0;
        while (running && !plat.quitRequested) {
            if (pad != null) pad.poll(padSink);
            boolean render;
            synchronized (lock) {
                try {
                    if (window.layoutSize()) game.resize(window.viewW());
                    game.update(1f / 60f);
                    render = VideoCfg.cur.fps >= 60 || (tick & 1) == 0;
                    if (render) {
                        plat.gfx.bind(window.screen());
                        game.render(plat.gfx);
                    }
                } catch (Throwable t) {
                    render = false;
                    if (errors++ < 20) PcLog.err("excepcion en el bucle del juego", t);
                }
            }
            if (render) window.present();
            tick++;

            next += TICK_NS;
            long wait = next - System.nanoTime();
            if (wait > 0) sleepUntil(next);
            else if (wait < -TICK_NS * 6) next = System.nanoTime();     // si se atraso mucho (ventana arrastrada, etc.) no intenta recuperar
        }
        synchronized (lock) {
            try { game.pause(); plat.store().commit(); } catch (Throwable t) { PcLog.err("al guardar", t); }
        }
        if (audio != null) audio.stop();
        window.close();
    }

    private static void sleepUntil(long deadlineNs) {
        long ms;
        while ((ms = (deadlineNs - System.nanoTime()) / 1_000_000L) > 1) {
            try { Thread.sleep(ms - 1); } catch (InterruptedException e) { return; }
        }
        while (System.nanoTime() < deadlineNs) LockSupport.parkNanos(50_000L);
    }

    // ------------------------------------------------------------------ prueba de arranque (CI)
    int selfTest(File assetsDir, File dataDir) {
        StringBuilder rep = new StringBuilder();
        boolean ok = true;
        try {
            // 1. recursos
            String[] must = {"audio/manifest.json", "i18n/en.tsv", "sprites", "tiles", "font"};
            for (String s : must) {
                boolean e = new File(assetsDir, s).exists();
                rep.append(e ? "ok   " : "FAIL ").append("recurso ").append(s).append('\n');
                ok &= e;
            }
            // 2. decodificacion OGG (efectos y musica)
            File sfx = new File(assetsDir, "audio/sfx/ui_click.ogg"), mus = new File(assetsDir, "audio/music/mus_menu.ogg");
            try {
                PcAudio.Pcm a = PcAudio.decode(sfx), b = PcAudio.decode(mus);
                boolean g = a.frames > 100 && b.frames > 44100 && b.ch == 2;
                rep.append(g ? "ok   " : "FAIL ").append("OGG decodificado: sfx ").append(a.frames).append(" fotogramas, musica ").append(b.frames).append(" (").append(b.ch).append(" canales)\n");
                ok &= g;
            } catch (Throwable t) {
                rep.append("FAIL decodificar OGG: ").append(t).append('\n');
                ok = false;
            }
            // 3. mezclador: abrir dispositivo es opcional (el runner de CI no tiene tarjeta de sonido)
            PcAudio au = new PcAudio(assetsDir);
            rep.append("info audio: dispositivo ").append(au.start() ? "disponible" : "no disponible (ok en CI)").append('\n');
            au.stop();
            // 4. XInput
            rep.append("info XInput: ").append(PcXInput.tryCreate() != null ? "cargado" : "no disponible (ok fuera de Windows)").append('\n');
            // 5. motor sin ventana
            window = new PcWindow(this, true);
            File store = new File(dataDir, "selftest_store.properties");
            store.delete();
            PcPlatform p = new PcPlatform(assetsDir, store, null, new PcVideo(window));
            plat = p;
            VideoCfg c = VideoCfg.load(p);
            c.fps = 30; c.applyPreset(VideoCfg.Q_LOW); c.showFps = true;
            window.open(c);
            VideoCfg.save(p, c);
            VideoCfg back = VideoCfg.parse(p.store().get("pc_video", ""));
            boolean rt = back.same(c);
            rep.append(rt ? "ok   " : "FAIL ").append("configuracion de video se guarda y se recupera\n");
            ok &= rt;
            game = new com.julianfarks.roguelike.core.Game();
            BufferedImage screen = new BufferedImage(480, Platform.VIEW_H, BufferedImage.TYPE_INT_ARGB);
            game.init(p);
            game.resize(480);
            boolean touchHidden = !((com.julianfarks.roguelike.core.Game) game).touchUiVisible();
            rep.append(touchHidden ? "ok   " : "FAIL ").append("controles tactiles ocultos en PC\n");
            ok &= touchHidden;
            int errs = 0;
            for (int f = 0; f < 300; f++) {
                try {
                    game.update(1f / 60f);
                    p.gfx.bind(screen);
                    game.render(p.gfx);
                } catch (Throwable t) { if (errs++ < 5) { rep.append("EXC frame ").append(f).append(": ").append(t).append('\n'); PcLog.err("selftest", t); } }
            }
            rep.append(errs == 0 ? "ok   " : "FAIL ").append("motor: 300 fotogramas sin excepciones\n");
            ok &= errs == 0;
            rep.append("info recursos que faltan: ").append(p.missing.size()).append(p.missing.isEmpty() ? "" : " " + p.missing).append('\n');
            ok &= p.missing.isEmpty();
            store.delete();
        } catch (Throwable t) {
            rep.append("FAIL excepcion: ").append(t).append('\n');
            PcLog.err("selftest", t);
            ok = false;
        }
        rep.append(ok ? "SELFTEST OK\n" : "SELFTEST FALLO\n");
        System.out.print(rep);
        try (PrintWriter w = new PrintWriter(new File(dataDir, "selftest.txt"), "UTF-8")) { w.print(rep); } catch (Throwable ignored) { }
        return ok ? 0 : 1;
    }
}
