package com.julianfarks.roguelike.core;

/**
 * STUB: sera reemplazado por el motor real.
 * Dibuja un texto de prueba con un mini-font de rectangulos y reacciona a toques (circulo por puntero).
 */
public class Game implements Platform.GameLoop {
    private Platform p;
    private int viewW = 576;
    private float t;
    private final float[] tx = new float[32], ty = new float[32];
    private final boolean[] down = new boolean[32];

    // glifos 3x5 (filas de 3 bits) para: S W R T U B
    private static final String LETTERS = "SWRTUB";
    private static final int[][] GLYPH = {
            {7, 4, 7, 1, 7}, // S
            {5, 5, 5, 7, 5}, // W (aprox.)
            {6, 5, 6, 5, 5}, // R
            {7, 2, 2, 2, 2}, // T
            {5, 5, 5, 5, 7}, // U
            {6, 5, 6, 5, 6}, // B
    };

    @Override public void init(Platform p) { this.p = p; p.log("STUB Game.init"); }
    @Override public void resize(int viewW) { this.viewW = viewW; }
    @Override public void update(float dt) { t += dt; }

    @Override
    public void render(Platform.Gfx g) {
        g.clear(0xFF101020);
        for (int i = 0; i < 8; i++) {
            g.rect(0, 20 + i * 30, viewW, 1, 0x33FFFFFF, false);
        }
        text(g, "SWR STUB", viewW / 2f - 8 * 4 * 4 / 2f, 100 + (float) Math.sin(t * 3) * 6, 4, 0xFFFFFFFF);
        g.circle(viewW / 2f, 200, 14 + (float) Math.sin(t * 5) * 3, 0x88FFA020, true);
        for (int i = 0; i < 32; i++) {
            if (down[i]) g.circle(tx[i], ty[i], 20, 0xAA40FF80, false);
        }
    }

    private void text(Platform.Gfx g, String s, float x, float y, int sc, int argb) {
        for (int k = 0; k < s.length(); k++) {
            int gi = LETTERS.indexOf(s.charAt(k));
            if (gi >= 0) {
                for (int r = 0; r < 5; r++)
                    for (int c = 0; c < 3; c++)
                        if ((GLYPH[gi][r] >> (2 - c) & 1) != 0) g.rect(x + c * sc, y + r * sc, sc, sc, argb, false);
            }
            x += 4 * sc;
        }
    }

    @Override
    public void touch(int id, int action, float x, float y) {
        if (id < 0 || id >= 32) return;
        down[id] = action != Platform.ACTION_UP;
        tx[id] = x;
        ty[id] = y;
    }

    @Override public void key(int code, boolean down) { }
    @Override public boolean back() { return false; }
    @Override public void pause() { }
    @Override public void resume() { }
}
