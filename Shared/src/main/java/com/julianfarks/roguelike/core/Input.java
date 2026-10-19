package com.julianfarks.roguelike.core;

import java.util.HashMap;
import java.util.Map;

/** Controles tactiles y de teclado -> acciones logicas. */
public final class Input {
    public static final int B_LEFT = 0, B_RIGHT = 1, B_DOWN = 2, B_JUMP = 3, B_ATTACK = 4, B_ROLL = 5, B_S1 = 6, B_S2 = 7, B_S3 = 8, B_ULT = 9,
            B_INTERACT = 10, B_PAUSE = 11, B_POTION = 12, B_SEC = 13, B_GREN = 14, B_GUARD = 15, B_SWAP = 16, B_INV = 17, B_COUNT = 18;

    public static final class Btn {
        public float cx, cy, r;
        public String icon;
        public boolean visible = true, hold;
        public int pointer = -1;
        public float cd = 0, cdMax = 1;   // para dibujar enfriamiento
        public boolean disabled;
        public boolean ready;
    }

    // ---- asignaciones: tecla por accion (Save.S.kb) y boton de mando por accion (Save.S.pb)
    public static int[] defaultKeys() { return new int[]{'A', 'D', 'S', 'W', 'J', 'K', 'U', 'I', 'O', 'P', 'E', 27, 'Q', 'L', 'G', 'C', 'R', 9}; }
    public static int[] defaultPad() { return new int[]{Pad.LS_L, Pad.LS_R, Pad.LS_D, Pad.A, Pad.X, Pad.B, Pad.RT, Pad.RB, Pad.LB, Pad.R3, Pad.Y, Pad.MENU, Pad.DUP, Pad.VIEW, Pad.L3, Pad.LT, Pad.RS_R, Pad.RS_U}; }
    /** Alternativas fijas: siguen funcionando mientras no las asignes tu a otra accion. */
    private static final int[] ALIAS_CODES = {37, 39, 40, 38, 32, 'Z', 'X', 16, '1', '2', '3', '4', 10, 'V', Pad.DLEFT, Pad.DRIGHT, Pad.DDOWN};
    private static final int[] ALIAS_ACT = {B_LEFT, B_RIGHT, B_DOWN, B_JUMP, B_JUMP, B_ATTACK, B_ROLL, B_ROLL, B_S1, B_S2, B_S3, B_ULT, B_INTERACT, B_GUARD, B_LEFT, B_RIGHT, B_DOWN};
    private final boolean[] codeDown = new boolean[2100];

    public final Btn[] btn = new Btn[B_COUNT];
    private final Map<Integer, Integer> ptrBtn = new HashMap<>();   // pointerId -> boton
    private final boolean[] held = new boolean[B_COUNT];
    private final boolean[] pressed = new boolean[B_COUNT];
    private final boolean[] keyHeld = new boolean[B_COUNT];
    public float viewW = 480;

    // ---- joystick flotante de movimiento
    private static final float DEAD = 9f, DEAD_OFF = 5f, FOLLOW_X = 40f, FOLLOW_UP = 30f, FOLLOW_DN = 40f, DOWN_ON = 24f, DOWN_OFF = 14f;
    private int stickId = -1;
    private float ax, ay, tx, ty;
    private boolean stkL, stkR, stkD;
    private final boolean[] stickHeld = new boolean[B_COUNT];

    public boolean stickActive() { return stickId >= 0; }
    public float stickCx() { return (btn[B_LEFT].cx + btn[B_RIGHT].cx) / 2f; }
    public float stickCy() { return btn[B_LEFT].cy; }
    public float stickR() { return 34f * btn[B_LEFT].r / 24f; }
    /** Centro actual de la base (se desplaza si el pulgar se aleja mucho) y posicion del pulgar. */
    public float anchorX() { return stickId >= 0 ? ax : stickCx(); }
    public float anchorY() { return stickId >= 0 ? ay : stickCy(); }
    public float thumbX() { return stickId >= 0 ? tx : stickCx(); }
    public float thumbY() { return stickId >= 0 ? ty : stickCy(); }
    public boolean stickL() { return stkL; }
    public boolean stickR_() { return stkR; }
    public boolean stickD() { return stkD; }

    private void recompute(int b) { held[b] = keyHeld[b] || stickHeld[b] || btn[b].pointer >= 0; }

    private boolean inStickZone(float x, float y) {
        float cx = stickCx(), r = stickR();
        float xmax = Math.max(viewW * 0.44f, cx + r + 40f);
        return x < xmax && y > 76f;
    }

    private void setStick(boolean l, boolean r, boolean d) {
        boolean[] nv = new boolean[B_COUNT];
        nv[B_LEFT] = l; nv[B_RIGHT] = r; nv[B_DOWN] = d;
        for (int b = B_LEFT; b <= B_DOWN; b++) {
            if (nv[b] && !stickHeld[b] && !held[b]) pressed[b] = true;
            stickHeld[b] = nv[b];
            recompute(b);
        }
        stkL = l; stkR = r; stkD = d;
    }

    private void updateStick(float x, float y) {
        float dx = x - ax;
        if (dx > FOLLOW_X) ax = x - FOLLOW_X; else if (dx < -FOLLOW_X) ax = x + FOLLOW_X;
        float dy = y - ay;
        if (dy > FOLLOW_DN) ay = y - FOLLOW_DN; else if (dy < -FOLLOW_UP) ay = y + FOLLOW_UP;
        dx = x - ax; dy = y - ay;
        tx = x; ty = y;
        boolean down = dy > (stkD ? DOWN_OFF : DOWN_ON) && dy > Math.abs(dx);
        float dead = (stkL || stkR) ? DEAD_OFF : DEAD;
        boolean l = !down && dx < -dead, r = !down && dx > dead;
        setStick(l, r, down);
    }

    private void endStick() { stickId = -1; setStick(false, false, false); }

    public Input() { for (int i = 0; i < B_COUNT; i++) btn[i] = new Btn(); layout(480); }

    public void layout(float w) {
        viewW = w;
        float W = w;
        // joystick de movimiento (izquierda): LEFT/RIGHT/DOWN definen su centro y tamaño
        set(B_LEFT, 40, 214, 24, "", true);
        set(B_RIGHT, 100, 214, 24, "", true);
        set(B_DOWN, 70, 252, 17, "", true);
        // grupo de accion (derecha), en arco alrededor del pulgar: ataque grande, salto y esquiva a su lado
        set(B_ATTACK, W - 46, 216, 31, "attack", false);
        set(B_JUMP, W - 112, 232, 26, "jump", false);
        set(B_ROLL, W - 100, 176, 22, "roll", false);
        set(B_S1, W - 28, 160, 16, "", false);
        set(B_S2, W - 62, 139, 16, "", false);
        set(B_S3, W - 100, 128, 16, "", false);
        set(B_ULT, W - 138, 140, 18, "", false);
        set(B_INTERACT, W - 166, 208, 18, "key", false);
        set(B_PAUSE, W - 18, 16, 12, "pause", false);
        set(B_POTION, 26, 62, 13, "potion", false);
        set(B_SEC, W - 198, 178, 15, "", false);
        set(B_GREN, W - 184, 140, 15, "", false);
        set(B_GUARD, W - 168, 252, 16, "parry", true);
        set(B_SWAP, W - 140, 104, 15, "swap", false);
        set(B_INV, W - 18, 44, 11, "bag", false);
        btn[B_INTERACT].visible = false;
        btn[B_LEFT].visible = btn[B_RIGHT].visible = btn[B_DOWN].visible = true;
        applyCustom();
    }

    /** Nombres para el editor de controles. */
    public static final String[] NAMES = {"Izquierda", "Derecha", "Abajo", "Saltar", "Atacar", "Rodar", "Habilidad 1", "Habilidad 2", "Habilidad 3", "Definitiva", "Interactuar", "Pausa", "Poción", "Arma secundaria", "Granada", "Escudo / Parry", "Cambiar arma", "Inventario"};

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
        stickId = -1; stkL = stkR = stkD = false;
        for (int i = 0; i < B_COUNT; i++) {
            pressed[i] = false; stickHeld[i] = false; btn[i].pointer = -1;
            keyHeld[i] = actionDown(i);          // teclas/botones fisicos que siguen pulsados se conservan
            held[i] = keyHeld[i];
        }
    }

    private int hit(float x, float y, boolean holdOnly) {
        int best = -1;
        float bd = 1e9f;
        for (int i = 0; i < B_COUNT; i++) {
            Btn b = btn[i];
            if (!b.visible) continue;
            if (i == B_LEFT || i == B_RIGHT || i == B_DOWN) continue;   // los maneja el joystick
            if (holdOnly && !b.hold) continue;
            float pad = b.hold ? 10 : 9;
            float d = Mth.dist(x, y, b.cx, b.cy);
            if (d <= b.r + pad && d < bd) { bd = d; best = i; }
        }
        return best;
    }

    public void touch(int id, int action, float x, float y) {
        if (action == Platform.ACTION_DOWN) {
            // los ids de puntero se reutilizan: limpia cualquier resto anterior de este id
            if (id == stickId) endStick();
            release(id);
            int b = hit(x, y, false);
            if (b >= 0) press(id, b);
            else if (stickId < 0 && inStickZone(x, y)) {
                stickId = id;
                ax = stickCx(); ay = stickCy();
                updateStick(x, y);
            }
        } else if (action == Platform.ACTION_MOVE) {
            if (id == stickId) { updateStick(x, y); return; }
            Integer cur = ptrBtn.get(id);
            if (cur != null && btn[cur].hold) {
                int nb = hit(x, y, true);
                if (nb != cur) {
                    release(id);
                    if (nb >= 0) press(id, nb);
                }
            }
        } else {
            if (id == stickId) endStick();
            else release(id);
        }
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
        for (Map.Entry<Integer, Integer> en : ptrBtn.entrySet()) if (en.getValue().equals(b)) btn[b].pointer = en.getKey();
        recompute(b);
    }

    /** Estado crudo de una tecla/boton (para atajos que no son acciones de juego). */
    public boolean rawDown(int code) { return isDown(code); }

    private boolean isDown(int code) { return code > 0 && code < codeDown.length && codeDown[code]; }

    /** Accion a la que apunta una tecla/boton: la asignada explicitamente (puede ser mas de una) o, si nadie la usa, su alternativa fija. */
    public boolean explicitlyBound(int code) {
        Save s = Save.S;
        for (int i = 0; i < B_COUNT; i++) if (s.kb[i] == code || s.pb[i] == code) return true;
        return false;
    }

    private boolean actionDown(int b) {
        Save s = Save.S;
        if (isDown(s.kb[b]) || isDown(s.pb[b])) return true;
        for (int k = 0; k < ALIAS_CODES.length; k++) if (ALIAS_ACT[k] == b && isDown(ALIAS_CODES[k]) && !explicitlyBound(ALIAS_CODES[k])) return true;
        return false;
    }

    private void refreshKeys() {
        for (int b = 0; b < B_COUNT; b++) {
            boolean nv = actionDown(b);
            if (nv && !keyHeld[b]) pressed[b] = true;
            keyHeld[b] = nv;
            recompute(b);
        }
    }

    /** Tecla de teclado (&lt; 1000) o boton de mando (codigo de Pad). */
    public void key(int code, boolean down) {
        if (code <= 0 || code >= codeDown.length) return;
        codeDown[code] = down;
        refreshKeys();
    }

    /** Suelta todos los botones de mando (mando desconectado). */
    public void releasePad() {
        for (int c = Pad.A; c < Pad.END; c++) codeDown[c] = false;
        refreshKeys();
    }

    /** Suelta los controles tactiles (se ocultan al usar mando). */
    public void releaseTouch() {
        ptrBtn.clear();
        for (int i = 0; i < B_COUNT; i++) btn[i].pointer = -1;
        if (stickId >= 0) endStick();
        for (int i = 0; i < B_COUNT; i++) recompute(i);
    }

    private boolean anyPointer(int b) { return btn[b].pointer >= 0; }

    public boolean held(int b) { return held[b]; }
    public boolean pressed(int b) { return pressed[b]; }
    public void consume(int b) { pressed[b] = false; }
    /** Durante una pausa de impacto (hitstop) el jugador no se actualiza: se conservan las pulsaciones para el primer fotograma real (no se pierden entradas). */
    public boolean keep;
    public void endFrame() { if (keep) { keep = false; return; } for (int i = 0; i < B_COUNT; i++) pressed[i] = false; }
    public float moveX() { return (held[B_RIGHT] ? 1 : 0) - (held[B_LEFT] ? 1 : 0); }
}
