package pc;

import com.julianfarks.roguelike.core.Platform;
import desktop.DesktopPlatform;

import java.io.File;

/**
 * Platform de Windows/PC. Reutiliza la carga de recursos y el almacen de claves del banco de pruebas de escritorio
 * (DesktopPlatform) y cambia lo que debe ser real: audio con sonido, reloj real, deteccion de PC y ajustes de video.
 */
public final class PcPlatform extends DesktopPlatform {
    private final Platform.Audio audio;
    private final Platform.Video video;

    public PcPlatform(File assets, File storeFile, Platform.Audio audio, Platform.Video video) {
        super(assets, storeFile);
        this.audio = audio;
        this.video = video;
    }

    /** Plataforma de PC sin ventana ni audio (banco de pruebas: capturas, bot y scripts con el comportamiento de PC). */
    public static PcPlatform headless(File assets, File storeFile) {
        PcWindow w = new PcWindow(new PcWindow.Host() {
            @Override public Object lock() { return this; }
            @Override public Platform.GameLoop game() { return null; }
            @Override public void requestClose() { }
            @Override public void toggleFullscreen() { }
        }, true);
        PcPlatform p = new PcPlatform(assets, storeFile, null, new PcVideo(w));
        com.julianfarks.roguelike.core.VideoCfg c = com.julianfarks.roguelike.core.VideoCfg.load(p);
        try { w.open(c); } catch (Exception ignored) { }
        return p;
    }

    @Override public boolean isDesktop() { return true; }
    @Override public Platform.Video video() { return video; }
    @Override public Platform.Audio audio() { return audio != null ? audio : super.audio(); }
    @Override public long nowMs() { return System.nanoTime() / 1_000_000L; }
    @Override public void vibrate(int ms) { /* PC: sin vibracion */ }
    @Override public void log(String msg) { PcLog.info(msg); }
}
