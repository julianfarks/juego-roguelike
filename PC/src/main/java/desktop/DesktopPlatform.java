package desktop;

import com.julianfarks.roguelike.core.Platform;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Properties;

/** Platform de escritorio para validar el motor sin telefono. Audio simulado: solo registra nombres y comprueba archivos. */
public class DesktopPlatform implements Platform {
    public final File assets;
    public final DesktopGfx gfx = new DesktopGfx();
    public final LinkedHashSet<String> missing = new LinkedHashSet<String>();
    public final LinkedHashMap<String, Integer> sfxPlayed = new LinkedHashMap<String, Integer>();
    public final LinkedHashMap<String, Integer> musicPlayed = new LinkedHashMap<String, Integer>();
    public final LinkedHashMap<String, Integer> ambientPlayed = new LinkedHashMap<String, Integer>();
    public int vibrations;
    public boolean quitRequested;
    public long virtualMs = 1000;
    public boolean verboseAudio;
    /** Si no es null recibe cada sfx/musica pedido (para componer el audio de los trailers fuera del juego). */
    public static java.util.function.Consumer<String> audioHook;

    private final FileStore store;

    public DesktopPlatform(File assets, File storeFile) {
        this.assets = assets;
        this.store = new FileStore(storeFile);
    }

    private File f(String path) {
        return new File(assets, path);
    }

    private void miss(String what) {
        if (missing.add(what)) System.out.println("[desktop] " + what);
    }

    // ---------------------------------------------------------------- recursos
    @Override
    public Img loadImage(String path) {
        File file = f(path);
        if (!file.isFile()) {
            miss("MISSING asset: " + path);
            return null;
        }
        try {
            BufferedImage src = ImageIO.read(file);
            if (src == null) {
                miss("MISSING asset: " + path + " (no se pudo decodificar)");
                return null;
            }
            BufferedImage argb = new BufferedImage(src.getWidth(), src.getHeight(), BufferedImage.TYPE_INT_ARGB);
            argb.getGraphics().drawImage(src, 0, 0, null);
            return new Img(argb.getWidth(), argb.getHeight(), argb);
        } catch (IOException e) {
            miss("MISSING asset: " + path + " (" + e.getMessage() + ")");
            return null;
        }
    }

    @Override
    public Img createImage(int w, int h, int[] argbPixels) {
        BufferedImage b = new BufferedImage(w, h, BufferedImage.TYPE_INT_ARGB);
        b.setRGB(0, 0, w, h, argbPixels, 0, w);
        return new Img(w, h, b);
    }

    @Override
    public int[] pixels(Img img) {
        BufferedImage b = (BufferedImage) img.handle;
        return b.getRGB(0, 0, img.w, img.h, null, 0, img.w);
    }

    @Override
    public String loadText(String path) {
        File file = f(path);
        if (!file.isFile()) {
            miss("MISSING asset: " + path);
            return null;
        }
        try {
            String s = new String(Files.readAllBytes(file.toPath()), StandardCharsets.UTF_8);
            return s.startsWith("﻿") ? s.substring(1) : s;
        } catch (IOException e) {
            miss("MISSING asset: " + path + " (" + e.getMessage() + ")");
            return null;
        }
    }

    @Override
    public String[] list(String dir) {
        String d = dir == null ? "" : dir;
        while (d.endsWith("/")) d = d.substring(0, d.length() - 1);
        File[] fs = (d.isEmpty() ? assets : f(d)).listFiles();
        if (fs == null) return new String[0];
        String[] names = new String[fs.length];
        for (int i = 0; i < fs.length; i++) names[i] = fs[i].getName();
        Arrays.sort(names);
        return names;
    }

    // ---------------------------------------------------------------- servicios
    @Override public Gfx gfx() { return gfx; }
    @Override public Audio audio() { return audio; }
    @Override public Store store() { return store; }
    @Override public void log(String msg) { System.out.println("[log] " + msg); }
    @Override public long nowMs() { return virtualMs; }
    @Override public void vibrate(int ms) { vibrations++; }
    @Override public void quit() { quitRequested = true; }

    private static void count(Map<String, Integer> m, String k) {
        Integer c = m.get(k);
        m.put(k, c == null ? 1 : c + 1);
    }

    private final Audio audio = new Audio() {
        @Override
        public void preloadSfx(String[] names) {
            if (names == null) return;
            for (String n : names) if (n != null && !f("audio/sfx/" + n + ".ogg").isFile()) miss("MISSING audio: sfx/" + n);
        }

        @Override
        public void sfx(String name, float vol, float pitch, float pan) {
            if (name == null) return;
            count(sfxPlayed, name);
            if (!f("audio/sfx/" + name + ".ogg").isFile()) miss("MISSING audio: sfx/" + name);
            if (audioHook != null) audioHook.accept("sfx\t" + name + "\t" + vol + "\t" + pitch + "\t" + pan);
            if (verboseAudio) log("sfx " + name + " v=" + vol + " p=" + pitch + " pan=" + pan);
        }

        @Override
        public void music(String name, boolean loop, float vol, int fadeMs) {
            if (name == null) return;
            count(musicPlayed, name);
            if (!f("audio/music/" + name + ".ogg").isFile()) miss("MISSING audio: music/" + name);
            if (audioHook != null) audioHook.accept("music\t" + name + "\t" + (loop ? 1 : 0) + "\t" + vol + "\t" + fadeMs);
            if (verboseAudio) log("music " + name + " loop=" + loop + " v=" + vol + " fade=" + fadeMs);
        }

        @Override public void stopMusic(int fadeMs) { }

        @Override
        public void ambient(String name, float vol) {
            if (name == null) return;
            count(ambientPlayed, name);
            if (!f("audio/sfx/" + name + ".ogg").isFile() && !f("audio/music/" + name + ".ogg").isFile()) {
                miss("MISSING audio: ambient/" + name);
            }
        }

        @Override public void setMusicVolume(float v) { }
        @Override public void setSfxVolume(float v) { }
        @Override public void pauseAll() { }
        @Override public void resumeAll() { }
    };

    // ---------------------------------------------------------------- Store
    private static final class FileStore implements Store {
        private final File file;
        private final HashMap<String, String> map = new HashMap<String, String>();

        FileStore(File file) {
            this.file = file;
            if (file != null && file.getParentFile() != null) file.getParentFile().mkdirs();
            if (file != null && file.isFile()) {
                Properties p = new Properties();
                try (FileInputStream in = new FileInputStream(file)) {
                    p.load(in);
                    for (String k : p.stringPropertyNames()) map.put(k, p.getProperty(k));
                } catch (IOException ignored) { }
            }
        }

        @Override public String get(String key, String def) { String v = map.get(key); return v == null ? def : v; }
        @Override public void put(String key, String value) { if (key != null && value != null) map.put(key, value); }

        @Override
        public void commit() {
            if (file == null) return;
            Properties p = new Properties();
            p.putAll(map);
            // escritura atomica: primero a un temporal y luego se reemplaza (un cierre brusco no deja el archivo a medias)
            File tmp = new File(file.getPath() + ".tmp");
            try (FileOutputStream out = new FileOutputStream(tmp)) {
                p.store(out, "swr desktop store");
                out.getFD().sync();
            } catch (IOException e) { return; }
            try {
                Files.move(tmp.toPath(), file.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE);
            } catch (IOException e) {
                try { Files.move(tmp.toPath(), file.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING); } catch (IOException ignored) { }
            }
        }
    }
}
