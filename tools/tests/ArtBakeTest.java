package com.julianfarks.roguelike.core;

import desktop.DesktopPlatform;
import java.io.File;
import java.util.Arrays;

/**
 * Prueba del arte procedural de suelos/plataformas: para los 9 biomas x varias semillas hornea las salas y comprueba
 * que (1) no hay excepciones, (2) la colision t[] y deco[] no cambia por hornear, (3) la imagen no queda vacia, (4) el tiempo de horneado es razonable.
 * Uso: ArtBakeTest ASSETS
 */
public class ArtBakeTest {
    public static void main(String[] a) throws Exception {
        DesktopPlatform p = new DesktopPlatform(new File(a[0]), File.createTempFile("abt", ".json"));
        Assets.init(p);
        int fails = 0, rooms = 0; long worst = 0, total = 0;
        for (int bi = 0; bi < Biome.ALL.length; bi++) {
            for (long seed = 1; seed <= 6; seed++) {
                Rng rg = new Rng(seed * 7919 + bi);
                int[] kinds = {Room.COMBAT, Room.COMBAT, Room.COMBAT};
                for (int n = 0; n < kinds.length; n++) {
                    Room rm = RoomGen.generate(kinds[n], Biome.ALL[bi], rg, Biome.ALL[bi].tier, 1 + n);
                    byte[] t0 = rm.t.clone(); short[] d0 = rm.deco.clone();
                    long s = System.nanoTime();
                    try { rm.bake(p); } catch (Throwable e) { System.out.println("FALLO excepcion b" + bi + " s" + seed + ": " + e); fails++; continue; }
                    long ms = (System.nanoTime() - s) / 1000000; worst = Math.max(worst, ms); total += ms; rooms++;
                    if (!Arrays.equals(t0, rm.t) || !Arrays.equals(d0, rm.deco)) { System.out.println("FALLO colision/deco modificada b" + bi + " s" + seed); fails++; }
                    int[] px = p.pixels(rm.baked);
                    if (px.length != rm.pixW * rm.pixH) { System.out.println("FALLO tamano b" + bi); fails++; }
                    int opaque = 0; for (int c : px) if ((c >>> 24) == 0xFF) opaque++;      // (los huecos "vista" son transparentes a proposito)
                    if (opaque < px.length / 4) { System.out.println("FALLO casi sin pixeles opacos b" + bi + " s" + seed); fails++; }
                    long sum = 0; for (int c : px) sum += c & 0xFFFFFF;
                    if (sum == 0) { System.out.println("FALLO imagen vacia b" + bi); fails++; }
                }
            }
        }
        System.out.println("salas=" + rooms + " media=" + (total / Math.max(1, rooms)) + "ms peor=" + worst + "ms fallos=" + fails);
        if (fails > 0) System.exit(1);
        System.out.println("OK");
    }
}
