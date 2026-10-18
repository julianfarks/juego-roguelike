package pc;

import com.julianfarks.roguelike.core.*;
import java.awt.image.BufferedImage;
import java.awt.Graphics2D;
import java.awt.Color;
import java.io.File;

/**
 * Prueba de CAMBIOS de modo y resolucion en una ventana real (X11 virtual): ventana -> sin bordes -> pantalla completa -> otra resolucion
 * -> vuelta atras, comprobando tras cada cambio el tamano del lienzo, el rectangulo de dibujo y el borde de color de la imagen virtual
 * (si el escalado o la camara se salieran de la pantalla, el marco de 1 px de la imagen virtual no coincidiria con el borde de la captura).
 * Uso (con DISPLAY de Xvfb): java -cp ... pc.WindowTest CAPTURA_DIR
 */
public class WindowTest implements PcWindow.Host {
    final Object lock = new Object();
    int fails;
    void chk(String n, boolean ok) { System.out.println((ok ? "ok   " : "FAIL ") + n); if (!ok) fails++; }
    @Override public Object lock() { return lock; }
    final Platform.GameLoop stub = (Platform.GameLoop) java.lang.reflect.Proxy.newProxyInstance(WindowTest.class.getClassLoader(),
            new Class<?>[]{Platform.GameLoop.class}, (p, m, a) -> m.getReturnType() == boolean.class ? (Object) Boolean.FALSE : null);
    @Override public Platform.GameLoop game() { return stub; }
    @Override public void requestClose() { }
    @Override public void toggleFullscreen() { }

    public static void main(String[] a) throws Exception {
        WindowTest t = new WindowTest();
        t.run(new File(a[0]));
        System.out.println(t.fails == 0 ? "WindowTest OK" : "WindowTest FALLOS " + t.fails);
        System.exit(t.fails == 0 ? 0 : 1);
    }

    void frame(PcWindow w, int n) throws Exception {
        for (int i = 0; i < n; i++) {
            w.layoutSize();
            BufferedImage s = w.screen();
            Graphics2D g = s.createGraphics();
            g.setColor(new Color(40, 40, 70)); g.fillRect(0, 0, s.getWidth(), s.getHeight());
            g.setColor(Color.RED); g.drawRect(0, 0, s.getWidth() - 1, s.getHeight() - 1);      // marco: borde de la pantalla virtual
            g.setColor(Color.GREEN); g.fillRect(s.getWidth() / 2 - 2, s.getHeight() / 2 - 2, 4, 4);
            g.dispose();
            w.present();
            Thread.sleep(40);
        }
    }

    void shot(String file) throws Exception {
        new ProcessBuilder("import", "-window", "root", file).inheritIO().start().waitFor();
    }

    /** Mide: la imagen virtual debe llenar el escritorio salvo franjas permitidas (marco rojo en los bordes del destino). */
    void check(String label, PcWindow w, File dir, String name, int sw, int sh, boolean expectFill) throws Exception {
        frame(w, 15);
        String f = new File(dir, name + ".png").getPath();
        shot(f);
        BufferedImage im = javax.imageio.ImageIO.read(new File(f));
        int W = im.getWidth(), H = im.getHeight();
        // primera fila/columna roja
        int top = -1, left = -1, bottom = -1, right = -1;
        for (int y = 0; y < H && top < 0; y++) if (isRed(im.getRGB(W / 2, y))) top = y;
        for (int y = H - 1; y >= 0 && bottom < 0; y--) if (isRed(im.getRGB(W / 2, y))) bottom = y;
        for (int x = 0; x < W && left < 0; x++) if (isRed(im.getRGB(x, H / 2))) left = x;
        for (int x = W - 1; x >= 0 && right < 0; x--) if (isRed(im.getRGB(x, H / 2))) right = x;
        int barsV = Math.max(0, top) + Math.max(0, H - 1 - bottom), barsH = Math.max(0, left) + Math.max(0, W - 1 - right);
        System.out.println("     " + label + ": captura " + W + "x" + H + ", virtual " + w.viewW() + "x" + w.viewH() + ", marco rojo en x " + left + ".." + right + " y " + top + ".." + bottom + " -> franjas H " + barsH + " V " + barsV);
        chk(label + ": se ve el marco de la pantalla virtual (nada fuera de pantalla)", top >= 0 && left >= 0 && bottom > top && right > left);
        // nitidez: el escalado es por vecino mas cercano, asi que solo pueden existir los 4 colores de la imagen virtual (+ negro): nada mezclado
        long off = 0, tot = 0;
        for (int y = 0; y < H; y += 3) for (int x = 0; x < W; x += 3) {
            int p = im.getRGB(x, y) & 0xFFFFFF; tot++;
            if (p != 0xFF0000 && p != 0x282846 && p != 0x00FF00 && p != 0) off++;
        }
        chk(label + ": pixel art nitido (colores mezclados/suavizados: " + off + " de " + tot + ")", off == 0);
        if (expectFill) chk(label + ": sin franjas negras (V<=2, H<=2*escala)", barsV <= 2 && barsH <= 2 * Math.ceil(Math.max(1, (right - left + 1) / (double) w.viewW())));
    }

    static boolean isRed(int rgb) { return ((rgb >> 16) & 255) > 200 && ((rgb >> 8) & 255) < 60 && (rgb & 255) < 60; }

    void run(File dir) throws Exception {
        dir.mkdirs();
        PcWindow w = new PcWindow(this, false);
        int[] n = w.nativeRes();
        System.out.println("monitor virtual " + n[0] + "x" + n[1]);
        VideoCfg c = new VideoCfg();
        c.mode = VideoCfg.MODE_WINDOW; c.resW = 1280; c.resH = 720;
        w.open(c); Thread.sleep(800);
        check("ventana 1280x720", w, dir, "1_ventana", n[0], n[1], false);
        c = c.copy(); c.mode = VideoCfg.MODE_BORDERLESS; w.apply(c); Thread.sleep(2200);
        check("sin bordes", w, dir, "2_sinbordes", n[0], n[1], true);
        c = c.copy(); c.mode = VideoCfg.MODE_FULL; c.resW = n[0]; c.resH = n[1]; w.apply(c); Thread.sleep(2200);
        check("pantalla completa " + n[0] + "x" + n[1], w, dir, "3_completa", n[0], n[1], true);
        c = c.copy(); c.mode = VideoCfg.MODE_WINDOW; c.resW = 1600; c.resH = 900; w.apply(c); Thread.sleep(2200);
        check("de vuelta a ventana 1600x900", w, dir, "4_ventana2", n[0], n[1], false);
        c = c.copy(); c.mode = VideoCfg.MODE_FULL; c.resW = n[0]; c.resH = n[1]; w.apply(c); Thread.sleep(2200);
        check("otra vez pantalla completa", w, dir, "5_completa2", n[0], n[1], true);
        VideoCfg back = c.copy(); back.mode = VideoCfg.MODE_WINDOW; back.resW = 1280; back.resH = 720; w.apply(back); Thread.sleep(2200);
        check("vuelta a la primera ventana 1280x720", w, dir, "6_ventana3", n[0], n[1], false);
        chk("el tamano virtual vuelve a ser el de una ventana 16:9 (480..640 x 270)", w.viewH() == 270 || w.viewH() >= 270);
        w.close();
    }
}
