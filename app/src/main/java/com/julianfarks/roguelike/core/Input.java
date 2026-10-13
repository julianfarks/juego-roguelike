package com.julianfarks.roguelike.core;

import java.util.HashMap;
import java.util.Map;

/** Controles tactiles y de teclado -> acciones logicas. */
public final class Input {
    public static final int B_LEFT = 0, B_RIGHT = 1, B_DOWN = 2, B_JUMP = 3, B_ATTACK = 4, B_ROLL = 5, B_S1 = 6, B_S2 = 7, B_S3 = 8, B_ULT = 9,
            B_INTERACT = 10, B_PAUSE = 11, B_POTION = 12, B_SEC = 13, B_GREN = 14, B_GUARD = 15, B_COUNT = 16;

    public static final class Btn {
        public float cx, cy, r;
        public String icon;
        public boolean visible = true, hold;
        public int pointer = -1;
        public float cd = 0, cdMax = 1;   // para dibujar enfriamiento
        public boolean disabled;
        public boolean ready;
    }

    public final Btn[] btn = new Btn[B_COUNT];
    private final Map<Integer, Integer> ptrBtn = new HashMap<>();   // pointerId -> boton
    private final boolean[] held = new boolean[B_COUNT];
    private final boolean[] pressed = new boolean[B_COUNT];
    private final boolean[] keyHeld = new boolean[B_COUNT];
    public float viewW = 480;

    public Input() { for (int i = 0; i < B_COUNT; i++) btn[i] = new Btn(); layout(480); }

    public void layout(float w) {
        viewW = w;
        float W = w;
        set(B_LEFT, 38, 232, 24, "", true);
        set(B_RIGHT, 98, 232, 24, "", true);
        set(B_DOWN, 68, 190, 17, "", true);
        set(B_ATTACK, W - 46, 220, 27, "attack", false);
        set(B_JUMP, W - 112, 238, 22, "jump", false);
        set(B_ROLL, W - 112, 190, 19, "roll", false);
        set(B_S1, W - 30, 168, 16, "", false);
        set(B_S2, W - 62, 150, 16, "", false);
        set(B_S3, W - 99, 143, 16, "", false);
        set(B_ULT, W - 138, 150, 17, "", false);
        set(B_INTERACT, W - 168, 218, 18, "key", false);
        set(B_PAUSE, W - 18, 16, 12, "pause", false);
        set(B_POTION, 30, 62, 12, "potion", false);
        set(B_SEC, W - 196, 186, 15, "", false);
        set(B_GREN, W - 178, 148, 15, "", false);
        set(B_GUARD, W - 150, 250, 16, "shield", true);
        btn[B_INTERACT].visible = false;
        btn[B_LEFT].visible = btn[B_RIGHT].visible = btn[B_DOWN].visible = true;
        applyCustom();
    }

    /** Nombres para el editor de controles. */
    public static final String[] NAMES = {"Izquierda", "Derecha", "Abajo", "Saltar", "Atacar", "Rodar", "Habilidad 1", "Habilidad 2", "Habilidad 3", "Definitiva", "Interactuar", "Pausa", "Poción", "Arma 2ª", "Granada", "Escudo / Parry"};

    private final float[] baseCx = new float[B_COUNT], baseCy = new float[B_COUNT], baseR = new float[B_COUNT];

    private void applyCustom() {
        float[] c = Save.S.ctl;
        for (int i = 0; i < B_COUNT; i++) {
            Btn b = btn[i];
            baseCx[i] = b.cx; baseCy[i] = b.cy; baseR[i] = b.r;
            float sc = c[i * 3 + 2] == 0 ? 1f : c[i * 3 + 2];
            b.cx = Mth.clamp(b.cx + c[i * 3], 8, viewW - 8);
            b.cy = Mth.clamp(b.cy + c[i * 3 + 1], 8, 262);
            b.r = baseR[i] * sc;
        }
    }

    /** Mueve un boton a una posicion absoluta (editor). */
    public void moveTo(int i, float x, float y) {
        float[] c = Save.S.ctl;
        x = Mth.clamp(x, 8, viewW - 8); y = Mth.clamp(y, 8, 262);
        c[i * 3] = x - baseCx[i]; c[i * 3 + 1] = y - baseCy[i];
        btn[i].cx = x; btn[i].cy = y;
    }

    public void scaleBtn(int i, float sc) {
        sc = Mth.clamp(sc, 0.6f, 1.8f);
        Save.S.ctl[i * 3 + 2] = Math.abs(sc - 1f) < 0.04f ? 0f : sc;
        btn[i].r = baseR[i] * sc;
    }

    public void resetCustom() { java.util.Arrays.fill(Save.S.ctl, 0f); layout(viewW); }

    private void set(int i, float cx, float cy, float r, String icon, boolean hold) {
        Btn b = btn[i];
        b.cx = cx; b.cy = cy; b.r = r; b.icon = icon; b.hold = hold;
    }

    public void reset() {
        ptrBtn.clear();
        for (int i = 0; i < B_COUNT; i++) { held[i] = false; pressed[i] = false; keyHeld[i] = false; btn[i].pointer = -1; }
    }

    private int hit(float x, float y, boolean holdOnly) {
        int best = -1;
        float bd = 1e9f;
        for (int i = 0; i < B_COUNT; i++) {
            Btn b = btn[i];
            if (!b.visible) continue;
            if (holdOnly && !b.hold) continue;
            float pad = b.hold ? 10 : 6;
            float d = Mth.dist(x, y, b.cx, b.cy);
            if (d <= b.r + pad && d < bd) { bd = d; best = i; }
        }
        return best;
    }

    public void touch(int id, int action, float x, float y) {
        if (action == Platform.ACTION_DOWN) {
            int b = hit(x, y, false);
            if (b >= 0) press(id, b);
        } else if (action == Platform.ACTION_MOVE) {
            Integer cur = ptrBtn.get(id);
            if (cur != null && btn[cur].hold) {
                int nb = hit(x, y, true);
                if (nb != cur) {
                    release(id);
                    if (nb >= 0) press(id, nb);
                }
            }
        } else release(id);
    }

    private void press(int id, int b) {
        ptrBtn.put(id, b);
        btn[b].pointer = id;
        if (!held[b]) pressed[b] = true;
        held[b] = true;
    }

    private void release(int id) {
        Integer b = ptrBtn.remove(id);
        if (b == null) return;
        btn[b].pointer = -1;
        held[b] = keyHeld[b];
        for (Integer other : ptrBtn.values()) if (other.equals(b)) held[b] = true;
    }

    public void key(int code, boolean down) {
        int b = -1;
        switch (code) {
            case 'A': case 37: b = B_LEFT; break;
            case 'D': case 39: b = B_RIGHT; break;
            case 'S': case 40: b = B_DOWN; break;
            case 'W': case 38: case 32: b = B_JUMP; break;
            case 'J': case 'Z': b = B_ATTACK; break;
            case 'K': case 'X': case 16: b = B_ROLL; break;
            case 'U': case '1': b = B_S1; break;
            case 'I': case '2': b = B_S2; break;
            case 'O': case '3': b = B_S3; break;
            case 'P': case '4': b = B_ULT; break;
            case 'E': case 10: b = B_INTERACT; break;
            case 'Q': b = B_POTION; break;
            case 'L': b = B_SEC; break;
            case 'G': b = B_GREN; break;
            case 'C': case 'V': b = B_GUARD; break;
            case 27: b = B_PAUSE; break;
            default: break;
        }
        if (b < 0) return;
        if (down && !keyHeld[b]) pressed[b] = true;
        keyHeld[b] = down;
        held[b] = down || anyPointer(b);
    }

    private boolean anyPointer(int b) { return btn[b].pointer >= 0; }

    public boolean held(int b) { return held[b]; }
    public boolean pressed(int b) { return pressed[b]; }
    public void consume(int b) { pressed[b] = false; }
    public void endFrame() { for (int i = 0; i < B_COUNT; i++) pressed[i] = false; }
    public float moveX() { return (held[B_RIGHT] ? 1 : 0) - (held[B_LEFT] ? 1 : 0); }
}
