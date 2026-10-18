package desktop;

import com.julianfarks.roguelike.core.Platform;

import javax.imageio.ImageIO;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Banco de pruebas de escritorio.
 *
 *   Main --headless --assets DIR --w 576 --frames N --script FILE --shots DIR [--game CLASE] [--bot] [--keep-going] [--store FILE] [--audio-log]
 *   Main (sin --headless) abre una ventana: flechas/WASD/espacio/enter/esc al motor, raton = toque id 0.
 *
 * Guion (una instruccion por linea, # comenta):
 *   frame key CODIGO|nombre down|up      frame touch ID down|move|up X Y      frame shot NOMBRE
 *   frame tap X Y  (down y, 3 frames despues, up)                            frame hold CODIGO FRAMES
 */
public final class Main {
    static final class Ev {
        final int frame;
        final String type; // key, touch, shot
        int code, id, action;
        float x, y;
        String name;
        Ev(int frame, String type) { this.frame = frame; this.type = type; }
    }

    // ------------------------------------------------------------------ argumentos
    static String assetsDir = "Shared/assets";
    static int viewW = 576;
    static int viewH = 270;          // --h N: alto virtual 270..320 (pruebas de monitores 16:10 / escala entera ampliada)
    static int frames = 600;
    static String scriptFile;
    static String shotsDir = "/tmp/swr_shots";
    static String gameClass = "com.julianfarks.roguelike.core.Game";
    static boolean headless, bot, keepGoing, audioLog, pcMode;
    static String storeFile;
    static String recFile;                 // --record FILE.mp4 : graba el juego (sin entradas tactiles ni depuracion) via ffmpeg
    static int recFrom = 0, recTo = Integer.MAX_VALUE;
    static int curFrame = 0;

    public static void main(String[] args) throws Exception {
        for (int i = 0; i < args.length; i++) {
            String a = args[i];
            switch (a) {
                case "--headless": headless = true; break;
                case "--bot": bot = true; break;
                case "--record": recFile = args[++i]; break;
                case "--rec-from": recFrom = Integer.parseInt(args[++i]); break;
                case "--rec-to": recTo = Integer.parseInt(args[++i]); break;
                case "--pc": pcMode = true; break;      // plataforma de PC (isDesktop, menu de video, sin controles tactiles)
                case "--keep-going": keepGoing = true; break;
                case "--audio-log": audioLog = true; break;
                case "--assets": assetsDir = args[++i]; break;
                case "--w": viewW = Integer.parseInt(args[++i]); break;
                case "--h": viewH = Integer.parseInt(args[++i]); break;
                case "--frames": frames = Integer.parseInt(args[++i]); break;
                case "--script": scriptFile = args[++i]; break;
                case "--shots": shotsDir = args[++i]; break;
                case "--game": gameClass = args[++i]; break;
                case "--store": storeFile = args[++i]; break;
                default:
                    System.err.println("Argumento desconocido: " + a);
                    System.exit(64);
            }
        }
        if (viewW < 480) viewW = 480;
        if (viewW > 640) viewW = 640;
        if (viewH < 270) viewH = 270;
        if (viewH > 320) viewH = 320;
        if (headless) System.setProperty("java.awt.headless", "true");

        File sf = storeFile == null ? null : new File(storeFile);
        DesktopPlatform plat = pcMode ? pc.PcPlatform.headless(new File(assetsDir), sf) : new DesktopPlatform(new File(assetsDir), sf);
        plat.verboseAudio = audioLog;
        Platform.GameLoop game;
        try {
            game = (Platform.GameLoop) Class.forName(gameClass).getDeclaredConstructor().newInstance();
        } catch (Throwable t) {
            Throwable c = t instanceof InvocationTargetException && t.getCause() != null ? t.getCause() : t;
            System.err.println("No se pudo crear el juego '" + gameClass + "':");
            c.printStackTrace();
            System.exit(2);
            return;
        }
        if (headless) System.exit(runHeadless(plat, game));
        else runWindow(plat, game);
    }

    // ------------------------------------------------------------------ guion
    static int keyCode(String s) {
        switch (s.toUpperCase()) {
            case "LEFT": return 37;
            case "UP": return 38;
            case "RIGHT": return 39;
            case "DOWN": return 40;
            case "SPACE": return 32;
            case "ENTER": return 10;
            case "ESC": return 27;
            case "SHIFT": return 16;
            default:
        }
        if (s.length() == 1) return Character.toUpperCase(s.charAt(0)); // letras A-Z y digitos
        return Integer.parseInt(s);
    }

    static List<Ev> parseScript(String file) throws IOException {
        List<Ev> out = new ArrayList<Ev>();
        if (file == null) return out;
        List<String> lines = Files.readAllLines(new File(file).toPath(), StandardCharsets.UTF_8);
        for (int n = 0; n < lines.size(); n++) {
            String ln = lines.get(n);
            int h = ln.indexOf('#');
            if (h >= 0) ln = ln.substring(0, h);
            ln = ln.trim();
            if (ln.isEmpty()) continue;
            String[] t = ln.split("\\s+");
            try {
                int fr = Integer.parseInt(t[0]);
                switch (t[1].toLowerCase()) {
                    case "key": {
                        Ev e = new Ev(fr, "key");
                        e.code = keyCode(t[2]);
                        e.action = t[3].equalsIgnoreCase("down") ? 1 : 0;
                        out.add(e);
                        break;
                    }
                    case "touch": {
                        Ev e = new Ev(fr, "touch");
                        e.id = Integer.parseInt(t[2]);
                        String a = t[3].toLowerCase();
                        e.action = a.equals("down") ? Platform.ACTION_DOWN : a.equals("move") ? Platform.ACTION_MOVE : Platform.ACTION_UP;
                        e.x = Float.parseFloat(t[4]);
                        e.y = Float.parseFloat(t[5]);
                        out.add(e);
                        break;
                    }
                    case "shot": {
                        Ev e = new Ev(fr, "shot");
                        e.name = t[2];
                        out.add(e);
                        break;
                    }
                    case "tap": {
                        float x = Float.parseFloat(t[2]), y = Float.parseFloat(t[3]);
                        Ev d = new Ev(fr, "touch");
                        d.id = 0; d.action = Platform.ACTION_DOWN; d.x = x; d.y = y;
                        Ev u = new Ev(fr + 3, "touch");
                        u.id = 0; u.action = Platform.ACTION_UP; u.x = x; u.y = y;
                        out.add(d);
                        out.add(u);
                        break;
                    }
                    case "hold": {
                        int code = keyCode(t[2]);
                        int len = Integer.parseInt(t[3]);
                        Ev d = new Ev(fr, "key");
                        d.code = code; d.action = 1;
                        Ev u = new Ev(fr + len, "key");
                        u.code = code; u.action = 0;
                        out.add(d);
                        out.add(u);
                        break;
                    }
                    default:
                        throw new IllegalArgumentException("instruccion desconocida '" + t[1] + "'");
                }
            } catch (RuntimeException ex) {
                System.err.println("Guion linea " + (n + 1) + " ignorada (" + ex + "): " + lines.get(n));
            }
        }
        Collections.sort(out, new Comparator<Ev>() { // estable: conserva el orden del guion dentro de un mismo frame
            @Override public int compare(Ev a, Ev b) { return Integer.compare(a.frame, b.frame); }
        });
        return out;
    }

    // ------------------------------------------------------------------ ejecucion headless
    static final class Stats {
        long updNs, rndNs, updMax, rndMax;
        int errors;
        final Map<String, Integer> errCount = new HashMap<String, Integer>();
    }

    static boolean report(Stats st, int frame, String phase, Throwable t) {
        Throwable c = t instanceof InvocationTargetException && t.getCause() != null ? t.getCause() : t;
        st.errors++;
        StackTraceElement[] ste = c.getStackTrace();
        String sig = phase + ":" + c.getClass().getName() + ":" + (ste.length > 0 ? ste[0].toString() : "");
        Integer n = st.errCount.get(sig);
        st.errCount.put(sig, n == null ? 1 : n + 1);
        if (n == null) {
            System.err.println("EXCEPTION en frame " + frame + " (" + phase + "):");
            c.printStackTrace();
        }
        return keepGoing && (n == null || n < 50);
    }

    static int runHeadless(DesktopPlatform plat, Platform.GameLoop game) throws Exception {
        List<Ev> script = parseScript(scriptFile);
        new File(shotsDir).mkdirs();
        BufferedImage screen = new BufferedImage(viewW, viewH, BufferedImage.TYPE_INT_ARGB);
        Stats st = new Stats();
        int done = 0;
        boolean aborted = false;

        try {
            game.init(plat);
            game.resize(viewW, viewH);
        } catch (Throwable t) {
            report(st, -1, "init", t);
            printSummary(plat, st, 0, true);
            return 2;
        }

        Object botObj = null;
        Method botTick = null;
        if (bot) {
            try {
                Class<?> bc = Class.forName("com.julianfarks.roguelike.core.DebugBot");
                botObj = bc.getDeclaredConstructor().newInstance();
                for (Method m : bc.getMethods()) {
                    if (m.getName().equals("tick") && m.getParameterTypes().length == 2) botTick = m;
                }
                if (botTick == null) System.out.println("[desktop] DebugBot sin metodo tick(Game,int): ignorado");
            } catch (ClassNotFoundException e) {
                System.out.println("[desktop] --bot: no existe core.DebugBot, ignorado");
            } catch (Throwable t) {
                report(st, -1, "bot-init", t);
            }
        }

        List<Ev> inputs = new ArrayList<Ev>(), shots = new ArrayList<Ev>();
        for (Ev e : script) (e.type.equals("shot") ? shots : inputs).add(e);
        int si = 0;
        Process ff = null; java.io.OutputStream ffo = null; java.io.PrintWriter aud = null;
        if (recFile != null) {
            ff = new ProcessBuilder("ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", viewW + "x" + viewH,
                    "-r", "60", "-i", "-", "-vf", "scale=1920:1080:flags=neighbor", "-c:v", "libx264", "-preset", "fast", "-crf", "8", "-pix_fmt", "yuv420p", recFile)
                    .redirectError(ProcessBuilder.Redirect.INHERIT).start();
            ffo = new java.io.BufferedOutputStream(ff.getOutputStream(), 1 << 20);
            final java.io.PrintWriter aw = new java.io.PrintWriter(new java.io.FileWriter(recFile + ".audio.tsv"));
            aud = aw;
            DesktopPlatform.audioHook = ev -> aw.println((curFrame - recFrom) + "\t" + ev);
        }
        byte[] rec = new byte[viewW * viewH * 3];
        for (int fr = 0; fr < frames; fr++) {
            curFrame = fr;
            plat.virtualMs = 1000L + fr * 1000L / 60L;
            // entradas del guion
            while (si < inputs.size() && inputs.get(si).frame <= fr) {
                Ev e = inputs.get(si++);
                try {
                    if (e.type.equals("key")) game.key(e.code, e.action == 1);
                    else game.touch(e.id, e.action, e.x, e.y);
                } catch (Throwable t) {
                    if (!report(st, fr, "input", t)) { aborted = true; break; }
                }
            }
            if (aborted) break;
            if (botTick != null) {
                try {
                    botTick.invoke(botObj, game, fr);
                } catch (Throwable t) {
                    if (!report(st, fr, "bot", t)) { aborted = true; break; }
                }
            }
            long t0 = System.nanoTime();
            try {
                game.update(1f / 60f);
            } catch (Throwable t) {
                if (!report(st, fr, "update", t)) { aborted = true; break; }
            }
            long t1 = System.nanoTime();
            try {
                plat.gfx.bind(screen);
                game.render(plat.gfx);
            } catch (Throwable t) {
                if (!report(st, fr, "render", t)) { aborted = true; break; }
            }
            long t2 = System.nanoTime();
            st.updNs += t1 - t0;
            st.rndNs += t2 - t1;
            st.updMax = Math.max(st.updMax, t1 - t0);
            st.rndMax = Math.max(st.rndMax, t2 - t1);
            done = fr + 1;

            if (ffo != null && fr >= recFrom && fr < recTo) {
                int[] px = screen.getRGB(0, 0, viewW, viewH, null, 0, viewW);
                for (int i = 0, o = 0; i < px.length; i++) { rec[o++] = (byte) px[i]; rec[o++] = (byte) (px[i] >> 8); rec[o++] = (byte) (px[i] >> 16); }
                try { ffo.write(rec); } catch (IOException ioe) { ffo = null; }
            }
            if (fr >= recTo) break;
            // capturas de este frame (despues del render)
            for (Ev e : shots) if (e.frame == fr) saveShot(screen, e.name);
            if (plat.quitRequested) {
                System.out.println("[desktop] el juego pidio quit() en el frame " + fr);
                break;
            }
        }
        if (ff != null) { try { ffo.close(); ff.waitFor(); } catch (Throwable ignored) { } aud.close(); }
        try { plat.store().commit(); } catch (Throwable ignored) { }
        saveShot(screen, "final");
        printSummary(plat, st, done, aborted);
        return st.errors > 0 ? 2 : 0;
    }

    static void saveShot(BufferedImage screen, String name) {
        int w = screen.getWidth(), h = screen.getHeight();
        BufferedImage big = new BufferedImage(w * 2, h * 2, BufferedImage.TYPE_INT_RGB);
        int[] px = screen.getRGB(0, 0, w, h, null, 0, w);
        int[] row = new int[w * 2];
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                int p = px[y * w + x] | 0xFF000000;
                row[x * 2] = p;
                row[x * 2 + 1] = p;
            }
            big.setRGB(0, y * 2, w * 2, 1, row, 0, w * 2);
            big.setRGB(0, y * 2 + 1, w * 2, 1, row, 0, w * 2);
        }
        try {
            File f = new File(shotsDir, name.replaceAll("[^A-Za-z0-9_.-]", "_") + ".png");
            ImageIO.write(big, "png", f);
        } catch (IOException e) {
            System.err.println("No se pudo guardar la captura " + name + ": " + e);
        }
    }

    static void printSummary(DesktopPlatform plat, Stats st, int done, boolean aborted) {
        System.out.println();
        System.out.println("================ RESUMEN ================");
        System.out.println("frames ejecutados : " + done + (aborted ? "  (ABORTADO)" : "") + " de " + frames);
        if (done > 0) {
            System.out.printf("update            : %.3f ms medio, %.3f ms max%n", st.updNs / 1e6 / done, st.updMax / 1e6);
            System.out.printf("render            : %.3f ms medio, %.3f ms max%n", st.rndNs / 1e6 / done, st.rndMax / 1e6);
        }
        System.out.println("excepciones       : " + st.errors);
        System.out.println("vibraciones       : " + plat.vibrations);
        System.out.println("MISSING (" + plat.missing.size() + "):");
        for (String m : plat.missing) System.out.println("  " + m);
        System.out.println("sfx unicos (" + plat.sfxPlayed.size() + "): " + plat.sfxPlayed);
        System.out.println("musica unica (" + plat.musicPlayed.size() + "): " + plat.musicPlayed);
        if (!plat.ambientPlayed.isEmpty()) System.out.println("ambiente: " + plat.ambientPlayed);
        System.out.println("capturas en       : " + shotsDir);
    }

    // ------------------------------------------------------------------ ventana
    static void runWindow(final DesktopPlatform plat, final Platform.GameLoop game) throws Exception {
        final BufferedImage screen = new BufferedImage(viewW, viewH, BufferedImage.TYPE_INT_ARGB);
        game.init(plat);
        game.resize(viewW, viewH);
        final int zoom = 2;
        final javax.swing.JPanel panel = new javax.swing.JPanel() {
            @Override protected void paintComponent(Graphics g) {
                g.drawImage(screen, 0, 0, viewW * zoom, viewH * zoom, null);
            }
        };
        panel.setPreferredSize(new Dimension(viewW * zoom, viewH * zoom));
        panel.setFocusable(true);
        panel.addKeyListener(new KeyAdapter() {
            @Override public void keyPressed(KeyEvent e) { synchronized (game) { game.key(e.getKeyCode(), true); } }
            @Override public void keyReleased(KeyEvent e) { synchronized (game) { game.key(e.getKeyCode(), false); } }
        });
        MouseAdapter ma = new MouseAdapter() {
            @Override public void mousePressed(MouseEvent e) { synchronized (game) { game.touch(0, Platform.ACTION_DOWN, e.getX() / (float) zoom, e.getY() / (float) zoom); } }
            @Override public void mouseDragged(MouseEvent e) { synchronized (game) { game.touch(0, Platform.ACTION_MOVE, e.getX() / (float) zoom, e.getY() / (float) zoom); } }
            @Override public void mouseReleased(MouseEvent e) { synchronized (game) { game.touch(0, Platform.ACTION_UP, e.getX() / (float) zoom, e.getY() / (float) zoom); } }
        };
        panel.addMouseListener(ma);
        panel.addMouseMotionListener(ma);
        final javax.swing.JFrame frame = new javax.swing.JFrame("SWR desktop");
        frame.setDefaultCloseOperation(javax.swing.JFrame.EXIT_ON_CLOSE);
        frame.add(panel);
        frame.pack();
        frame.setVisible(true);
        panel.requestFocus();

        final long step = 1_000_000_000L / 60;
        long next = System.nanoTime();
        long start = System.nanoTime();
        while (!plat.quitRequested) {
            plat.virtualMs = (System.nanoTime() - start) / 1_000_000L;
            try {
                synchronized (game) {
                    game.update(1f / 60f);
                    plat.gfx.bind(screen);
                    game.render(plat.gfx);
                }
            } catch (Throwable t) {
                t.printStackTrace();
            }
            panel.repaint();
            next += step;
            long wait = next - System.nanoTime();
            if (wait > 0) Thread.sleep(wait / 1_000_000L, (int) (wait % 1_000_000L));
            else if (wait < -step * 5) next = System.nanoTime();
        }
        frame.dispose();
        System.exit(0);
    }
}
