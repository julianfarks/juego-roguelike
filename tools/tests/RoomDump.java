package com.julianfarks.roguelike.core;

import desktop.DesktopPlatform;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;

/**
 * Vuelca a PNG la imagen horneada de salas generadas (para comparar el arte de suelos/plataformas antes y despues).
 * Uso: RoomDump ASSETS SALIDA BIOMA SEMILLA[,SEMILLA..] [ESCALA] [overlay]
 * 'overlay' marca la colision real (rojo = solido, azul = plataforma de una via, amarillo = pinchos) para comprobar que no cambia.
 */
public class RoomDump {
    public static void main(String[] a) throws Exception {
        DesktopPlatform p = new DesktopPlatform(new File(a[0]), File.createTempFile("rdump", ".json"));
        Assets.init(p);
        new File(a[1]).mkdirs();
        int bi = Integer.parseInt(a[2]);
        int scale = a.length > 4 ? Integer.parseInt(a[4]) : 2;
        boolean overlay = a.length > 5 && a[5].equals("overlay");
        for (String s : a[3].split(",")) {
            long seed = Long.parseLong(s);
            Rng rg = new Rng(seed);
            for (int n = 0; n < 2; n++) {
                Room rm = RoomGen.generate(Room.COMBAT, Biome.ALL[bi], rg, Biome.ALL[bi].tier, 1 + n);
                long t0 = System.nanoTime();
                rm.bake(p);
                long ms = (System.nanoTime() - t0) / 1000000;
                if (System.getenv("RD_TIMING") != null) {
                    long best = Long.MAX_VALUE;
                    for (int q = 0; q < 8; q++) { long t1 = System.nanoTime(); rm.bake(p); best = Math.min(best, System.nanoTime() - t1); }
                    System.out.println("  tiempo en caliente (mejor de 8): " + best / 1000000 + " ms  (" + rm.pixW * rm.pixH / 1000 + " kpx)");
                }
                int[] px = p.pixels(rm.baked);
                int w = rm.baked.w, h = rm.baked.h;
                BufferedImage out = new BufferedImage(w * scale, h * scale, BufferedImage.TYPE_INT_ARGB);
                for (int y = 0; y < h * scale; y++) for (int x = 0; x < w * scale; x++) out.setRGB(x, y, 0xFF000000 | px[(y / scale) * w + x / scale]);
                if (overlay) {
                    for (int ty = 0; ty < rm.h; ty++) for (int tx = 0; tx < rm.w; tx++) {
                        int t = rm.t[ty * rm.w + tx];
                        int c = t == Room.SOLID ? 0x80FF0000 : t == Room.ONEWAY ? 0xA00060FF : (t == Room.SPIKE || t == Room.SPIKE_DOWN) ? 0xA0FFFF00 : 0;
                        if (c == 0) continue;
                        for (int j = 0; j < 16 * scale; j++) for (int i = 0; i < 16 * scale; i++) {
                            int ox = tx * 16 * scale + i, oy = ty * 16 * scale + j;
                            boolean border = i == 0 || j == 0 || i == 16 * scale - 1 || j == 16 * scale - 1;
                            if (border) out.setRGB(ox, oy, c | 0xFF000000);
                        }
                    }
                }
                File f = new File(a[1], "b" + bi + "_s" + seed + "_r" + n + (overlay ? "_col" : "") + ".png");
                ImageIO.write(out, "png", f);
                System.out.println(f + " " + w + "x" + h + " bake=" + ms + "ms");
            }
        }
    }
}
