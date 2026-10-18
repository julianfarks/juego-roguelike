package pc;

import com.julianfarks.roguelike.core.Platform;
import com.julianfarks.roguelike.core.VideoCfg;

import javax.swing.JFrame;
import javax.swing.SwingUtilities;
import java.awt.Canvas;
import java.awt.Color;
import java.awt.Cursor;
import java.awt.DisplayMode;
import java.awt.Graphics2D;
import java.awt.GraphicsConfiguration;
import java.awt.GraphicsDevice;
import java.awt.GraphicsEnvironment;
import java.awt.Rectangle;
import java.awt.RenderingHints;
import java.awt.Toolkit;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.image.BufferStrategy;
import java.awt.image.BufferedImage;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Ventana del juego en PC: modo ventana, pantalla completa (exclusiva), ventana sin bordes, resolucion, escalado de pixeles
 * (entero = nitido / ajustado), teclado y raton. En modo headless (pruebas) no crea ninguna ventana: aplica la configuracion en memoria.
 *
 * Hilos: los eventos de entrada llegan en el EDT y entran al motor con {@code synchronized(lock)}; el bucle principal (PcMain)
 * actualiza y dibuja dentro del mismo lock y luego llama a {@link #present} fuera de el.
 */
final class PcWindow {
    interface Host {
        Object lock();
        Platform.GameLoop game();
        /** El usuario cerro la ventana. */
        void requestClose();
        /** F11 / Alt+Enter. */
        void toggleFullscreen();
    }

    static final int VIEW_H = Platform.VIEW_H;

    private final Host host;
    private final boolean headless;
    private final GraphicsDevice dev;
    private final DisplayMode origMode;
    private final ReentrantLock winLock = new ReentrantLock();

    private JFrame frame;
    private Canvas canvas;
    private BufferStrategy bs;
    private VideoCfg cfg = new VideoCfg();
    private boolean fullscreenActive;

    // rectangulo de dibujo (en pixeles del lienzo) y tamano virtual; los lee el hilo de entrada y el de render
    private volatile int dstX, dstY, dstW = 1, dstH = 1, viewW = 480;
    private volatile float scale = 1f;
    private BufferedImage screen;

    private final Set<Integer> down = new HashSet<Integer>();
    private int fpsCount, fpsShown;
    private long fpsT;

    PcWindow(Host host, boolean headless) {
        this.host = host;
        this.headless = headless;
        GraphicsDevice d = null;
        DisplayMode m = null;
        if (!headless) {
            try {
                d = GraphicsEnvironment.getLocalGraphicsEnvironment().getDefaultScreenDevice();
                m = d.getDisplayMode();
            } catch (Throwable t) { /* sin pantalla */ }
        }
        dev = d;
        origMode = m;
    }

    // ------------------------------------------------------------------ informacion del monitor
    int[] nativeRes() {
        if (origMode != null) return new int[]{origMode.getWidth(), origMode.getHeight()};
        return new int[]{1920, 1080};
    }

    int refreshHz() {
        if (origMode != null && origMode.getRefreshRate() != DisplayMode.REFRESH_RATE_UNKNOWN) return origMode.getRefreshRate();
        return headless ? 60 : 0;
    }

    /** Ventana por defecto: el mayor multiplo entero de 480x270 que cabe holgado en el monitor (3x = 1440x810 en un 1080p). */
    int[] defaultRes() {
        int[] n = nativeRes();
        int best = 1;
        for (int k = 1; k <= 8; k++) if (480 * k <= n[0] * 0.92 && 270 * k <= n[1] * 0.88) best = k;
        return new int[]{480 * best, 270 * best};
    }

    /** Resoluciones ofrecidas, de menor a mayor: las del monitor (>= 640x360) mas los multiplos de 480x270 y 1280x720/1600x900 que quepan. */
    int[][] resolutions() {
        int[] n = nativeRes();
        TreeSet<long[]> set = new TreeSet<long[]>(new java.util.Comparator<long[]>() {
            @Override public int compare(long[] a, long[] b) { return a[0] != b[0] ? Long.compare(a[0], b[0]) : Long.compare(a[1], b[1]); }
        });
        List<int[]> cand = new ArrayList<int[]>();
        if (dev != null) {
            try {
                for (DisplayMode m : dev.getDisplayModes()) cand.add(new int[]{m.getWidth(), m.getHeight()});
            } catch (Throwable ignored) { }
        }
        for (int k = 2; k <= 8; k++) cand.add(new int[]{480 * k, 270 * k});
        cand.add(new int[]{1280, 720});
        cand.add(new int[]{1600, 900});
        cand.add(new int[]{n[0], n[1]});
        for (int[] c : cand) {
            if (c[0] < 640 || c[1] < 360 || c[0] > n[0] || c[1] > n[1]) continue;
            set.add(new long[]{c[0], c[1]});
        }
        int[][] out = new int[set.size()][];
        int i = 0;
        for (long[] c : set) out[i++] = new int[]{(int) c[0], (int) c[1]};
        return out;
    }

    int fps() { return fpsShown; }

    VideoCfg config() { return cfg; }

    int viewW() { return viewW; }

    // ------------------------------------------------------------------ crear / aplicar
    /** Crea la ventana con la configuracion dada (hilo principal, antes del bucle). */
    void open(final VideoCfg c) throws Exception {
        if (headless) { cfg = c.copy(); viewW = 480; screen = new BufferedImage(480, VIEW_H, BufferedImage.TYPE_INT_ARGB); return; }
        if (SwingUtilities.isEventDispatchThread()) build(c); else SwingUtilities.invokeAndWait(new Runnable() { @Override public void run() { build(c); } });
    }

    /** Aplica una configuracion a la ventana en marcha. No bloquea al hilo del juego; devuelve false si es evidentemente imposible. */
    boolean apply(final VideoCfg c) {
        if (headless) { cfg = c.copy(); return true; }
        if (c.mode == VideoCfg.MODE_FULL && dev != null && !dev.isFullScreenSupported()) return false;
        final VideoCfg copy = c.copy();
        SwingUtilities.invokeLater(new Runnable() {
            @Override public void run() {
                try { build(copy); } catch (Throwable t) { PcLog.err("No se pudo aplicar el video", t); }
            }
        });
        return true;
    }

    /** (Re)construye la ventana segun la configuracion. Solo en el EDT. */
    private void build(VideoCfg c) {
        winLock.lock();
        try {
            boolean first = frame == null;
            Rectangle oldBounds = frame != null && !fullscreenActive && frame.isDisplayable() ? frame.getBounds() : null;
            if (fullscreenActive && dev != null) {
                try { dev.setFullScreenWindow(null); } catch (Throwable ignored) { }
                try { if (origMode != null && dev.isDisplayChangeSupported()) dev.setDisplayMode(origMode); } catch (Throwable ignored) { }
                fullscreenActive = false;
            }
            if (frame != null) { frame.dispose(); }
            bs = null;

            cfg = c.copy();
            canvas = new Canvas();
            canvas.setIgnoreRepaint(true);
            canvas.setFocusable(true);
            canvas.setBackground(Color.BLACK);
            canvas.setFocusTraversalKeysEnabled(false);
            installInput(canvas);

            final JFrame f = new JFrame("SwordsmanMagic: Eternal Abyss");
            f.setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
            f.setIgnoreRepaint(true);
            f.getContentPane().setBackground(Color.BLACK);
            f.getContentPane().add(canvas);
            f.setFocusTraversalKeysEnabled(false);
            try {
                InputStream in = PcWindow.class.getResourceAsStream("/icon_256.png");
                if (in != null) { f.setIconImage(javax.imageio.ImageIO.read(in)); in.close(); }
            } catch (Throwable ignored) { }
            f.addWindowListener(new WindowAdapter() {
                @Override public void windowClosing(WindowEvent e) { host.requestClose(); }
                @Override public void windowDeactivated(WindowEvent e) { focusLost(); }
                @Override public void windowActivated(WindowEvent e) { focusGained(); }
            });

            int[] n = nativeRes();
            if (c.mode == VideoCfg.MODE_WINDOW) {
                f.setUndecorated(false);
                f.setResizable(true);
                canvas.setPreferredSize(new java.awt.Dimension(c.resW, c.resH));
                f.pack();
                if (oldBounds != null && !first) f.setLocation(Math.max(0, oldBounds.x + (oldBounds.width - f.getWidth()) / 2), Math.max(0, oldBounds.y + (oldBounds.height - f.getHeight()) / 2));
                else f.setLocationRelativeTo(null);
                f.setVisible(true);
            } else if (c.mode == VideoCfg.MODE_BORDERLESS || dev == null || !dev.isFullScreenSupported()) {
                f.setUndecorated(true);
                f.setResizable(false);
                Rectangle b = dev != null ? dev.getDefaultConfiguration().getBounds() : new Rectangle(0, 0, n[0], n[1]);
                f.setBounds(b);
                f.setVisible(true);
            } else {
                f.setUndecorated(true);
                f.setResizable(false);
                f.setVisible(true);
                try {
                    dev.setFullScreenWindow(f);
                    fullscreenActive = true;
                    if (dev.isDisplayChangeSupported()) {
                        DisplayMode want = pickMode(c.resW, c.resH);
                        if (want != null) dev.setDisplayMode(want);
                    }
                } catch (Throwable t) {
                    PcLog.err("Pantalla completa no disponible; se usa ventana sin bordes", t);
                    try { dev.setFullScreenWindow(null); } catch (Throwable ignored) { }
                    fullscreenActive = false;
                    f.setBounds(dev.getDefaultConfiguration().getBounds());
                }
            }
            frame = f;
            canvas.requestFocusInWindow();
            canvas.createBufferStrategy(2);
            bs = canvas.getBufferStrategy();
            canvas.setCursor(Cursor.getDefaultCursor());
        } finally {
            winLock.unlock();
        }
    }

    private DisplayMode pickMode(int w, int h) {
        DisplayMode best = null;
        for (DisplayMode m : dev.getDisplayModes()) {
            if (m.getWidth() != w || m.getHeight() != h) continue;
            if (best == null) { best = m; continue; }
            int bb = best.getBitDepth() == DisplayMode.BIT_DEPTH_MULTI ? 32 : best.getBitDepth();
            int mb = m.getBitDepth() == DisplayMode.BIT_DEPTH_MULTI ? 32 : m.getBitDepth();
            if (mb > bb || (mb == bb && m.getRefreshRate() > best.getRefreshRate())) best = m;
        }
        return best;
    }

    /** Restaura el modo de pantalla original (salida del juego). */
    void restoreDisplay() {
        if (dev == null) return;
        try { if (fullscreenActive) dev.setFullScreenWindow(null); } catch (Throwable ignored) { }
        try { if (origMode != null && dev.isDisplayChangeSupported()) dev.setDisplayMode(origMode); } catch (Throwable ignored) { }
    }

    void close() {
        restoreDisplay();
        if (frame != null) frame.dispose();
    }

    // ------------------------------------------------------------------ entrada
    private void installInput(Canvas c) {
        c.addKeyListener(new KeyAdapter() {
            @Override public void keyPressed(KeyEvent e) {
                int k = e.getKeyCode();
                if (k == KeyEvent.VK_F11 || (k == KeyEvent.VK_ENTER && e.isAltDown())) { host.toggleFullscreen(); return; }
                if (k == KeyEvent.VK_UNDEFINED || k == KeyEvent.VK_ALT_GRAPH) return;
                synchronized (down) { if (!down.add(k)) return; }      // sin repeticion automatica del teclado
                synchronized (host.lock()) { host.game().key(k, true); }
            }
            @Override public void keyReleased(KeyEvent e) {
                int k = e.getKeyCode();
                synchronized (down) { if (!down.remove(k)) return; }
                synchronized (host.lock()) { host.game().key(k, false); }
            }
        });
        MouseAdapter ma = new MouseAdapter() {
            @Override public void mousePressed(MouseEvent e) { if (e.getButton() == MouseEvent.BUTTON1) mouse(Platform.ACTION_DOWN, e); }
            @Override public void mouseDragged(MouseEvent e) { mouse(Platform.ACTION_MOVE, e); }
            @Override public void mouseReleased(MouseEvent e) { if (e.getButton() == MouseEvent.BUTTON1) mouse(Platform.ACTION_UP, e); }
        };
        c.addMouseListener(ma);
        c.addMouseMotionListener(ma);
    }

    private void mouse(int action, MouseEvent e) {
        float s = scale <= 0 ? 1f : scale;
        float x = (e.getX() - dstX) / s, y = (e.getY() - dstY) / s;
        synchronized (host.lock()) { host.game().touch(0, action, x, y); }
    }

    private boolean inactive;

    private void focusLost() {
        Integer[] ks;
        synchronized (down) { ks = down.toArray(new Integer[0]); down.clear(); }
        synchronized (host.lock()) {
            for (int k : ks) host.game().key(k, false);
            if (!inactive) { inactive = true; host.game().pause(); }
        }
    }

    private void focusGained() {
        if (canvas != null) canvas.requestFocusInWindow();
        synchronized (host.lock()) {
            if (inactive) { inactive = false; host.game().resume(); }
        }
    }

    // ------------------------------------------------------------------ tamano / presentacion
    /** Calcula tamano virtual y rectangulo de dibujo segun el lienzo. Devuelve true si cambio el ancho virtual (hay que llamar a game.resize). */
    boolean layoutSize() {
        if (headless) return false;
        Canvas c = canvas;
        if (c == null) return false;
        int cw = c.getWidth(), ch = c.getHeight();
        if (cw < 16 || ch < 16) return false;
        int vw;
        float s;
        if (cfg.scaleMode == 0) {
            int k = Math.max(1, (int) Math.floor(Math.min(cw / 480f, ch / (float) VIEW_H)));
            vw = Math.max(480, Math.min(640, cw / k));
            s = k;
        } else {
            vw = Math.max(480, Math.min(640, Math.round(VIEW_H * (float) cw / ch)));
            s = Math.min(cw / (float) vw, ch / (float) VIEW_H);
        }
        int dw = Math.round(vw * s), dh = Math.round(VIEW_H * s);
        dstW = dw; dstH = dh; dstX = (cw - dw) / 2; dstY = (ch - dh) / 2; scale = s;
        boolean changed = vw != viewW || screen == null;
        viewW = vw;
        return changed;
    }

    /** Imagen virtual donde dibuja el motor (se recrea si cambia el ancho virtual). */
    BufferedImage screen() {
        if (screen == null || screen.getWidth() != viewW) screen = new BufferedImage(viewW, VIEW_H, BufferedImage.TYPE_INT_ARGB);
        return screen;
    }

    /** Muestra la imagen virtual en la ventana (escalado vecino mas cercano, barras negras). */
    void present() {
        if (headless) return;
        if (!winLock.tryLock()) return;
        try {
            BufferStrategy b = bs;
            if (b == null || canvas == null || !canvas.isDisplayable()) return;
            int guard = 0;
            do {
                do {
                    Graphics2D g = (Graphics2D) b.getDrawGraphics();
                    try {
                        g.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_NEAREST_NEIGHBOR);
                        g.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_SPEED);
                        g.setColor(Color.BLACK);
                        g.fillRect(0, 0, canvas.getWidth(), canvas.getHeight());
                        g.drawImage(screen, dstX, dstY, dstX + dstW, dstY + dstH, 0, 0, screen.getWidth(), screen.getHeight(), null);
                    } finally { g.dispose(); }
                } while (b.contentsRestored() && ++guard < 4);
                b.show();
            } while (b.contentsLost() && ++guard < 8);
            if (cfg.vsync) Toolkit.getDefaultToolkit().sync();
        } catch (Throwable t) {
            // la superficie puede perderse al cambiar de modo; se recrea en el siguiente build()
        } finally {
            winLock.unlock();
        }
        long now = System.nanoTime();
        fpsCount++;
        if (now - fpsT >= 1_000_000_000L) { fpsShown = fpsCount; fpsCount = 0; fpsT = now; }
    }

    /** Cuenta un fotograma en modo headless (para el contador de FPS). */
    void countHeadlessFrame() {
        long now = System.nanoTime();
        fpsCount++;
        if (now - fpsT >= 1_000_000_000L) { fpsShown = fpsCount; fpsCount = 0; fpsT = now; }
    }
}
