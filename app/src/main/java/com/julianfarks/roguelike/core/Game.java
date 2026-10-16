package com.julianfarks.roguelike.core;

/** Punto de entrada del motor: gestiona pantallas, transiciones y entrada. */
public class Game implements Platform.GameLoop {
    Platform P;
    public int viewW = 576;
    public final Input input = new Input();
    public boolean keyboardUsed;
    public Screen cur, next;
    float fade = 1f;
    int fadeDir = -1;
    float fadeSpeed = 4f;
    float time;

    // ---- dispositivo de entrada (tactil / teclado / mando)
    public int padType = Pad.TYPE_GENERIC;
    public boolean padConn, usingPad;
    public int lastDevice;                       // 0 tactil, 1 teclado, 2 mando (para mostrar los botones correctos)
    private float lastPadT = -99, lastTouchT = -99;
    private int touchStreak;
    private boolean lastTouchVis = true;

    /** Los controles tactiles de la partida estan visibles? Tactil: siempre. Mando: ocultos mientras haya un mando conectado. Auto: ocultos mientras se use el mando. */
    public boolean touchUiVisible() {
        int m = Save.S.inputMode;
        if (m == 1 || !padConn) return true;
        if (m == 2) return false;
        return !usingPad;
    }

    private void padActivity() {
        padConn = true;
        lastPadT = time;
        lastDevice = 2;
        if (Save.S.inputMode == 0) usingPad = true;
    }

    private void padConnected(boolean on) {
        padConn = on;
        if (on) { if (Save.S.inputMode == 0) usingPad = true; lastPadT = time; lastDevice = 2; }
        else { usingPad = false; input.releasePad(); if (lastDevice == 2) lastDevice = 0; }
    }

    /** Nombre de la tecla/boton de una accion para el dispositivo en uso (null si se juega con la pantalla tactil). */
    public String hintFor(int action) {
        if (lastDevice == 2 && padConn) return Pad.name(padType, Save.S.pb[action]);
        if (lastDevice == 1) return Pad.keyName(Save.S.kb[action]);
        return null;
    }

    /** Pulsaciones de la pantalla estando activo el mando: no cambian a tactil por un toque accidental; hacen falta 3 toques seguidos con el mando quieto. */
    private void noteTouch() {
        lastDevice = 0;
        if (!(usingPad && Save.S.inputMode == 0 && padConn)) return;
        if (time - lastTouchT > 2f) touchStreak = 0;
        lastTouchT = time;
        touchStreak++;
        if (touchStreak >= 3 && time - lastPadT > 1f) { usingPad = false; touchStreak = 0; }
    }

    @Override
    public void init(Platform p) {
        P = p;
        Assets.init(p);
        Save.load(p);
        Snd.init(p);
        cur = new Screens.Boot(this);
        cur.enter();
    }

    @Override
    public void resize(int w) {
        viewW = Math.max(480, Math.min(640, w));
        input.layout(viewW);
        if (cur != null) cur.resize();
    }

    /** Cambia de pantalla con fundido a negro. */
    public void go(Screen s) {
        if (next != null) return;
        next = s;
        fadeDir = 1;
        fadeSpeed = 5f;
    }

    /** Cambio inmediato (sin fundido) para la pantalla de carga. */
    void swap(Screen s) {
        cur = s;
        cur.enter();
        fade = 1f; fadeDir = -1;
    }

    @Override
    public void update(float dt) {
        time += dt;
        if (fadeDir == 1) {
            fade += dt * fadeSpeed;
            if (fade >= 1f) {
                fade = 1f;
                cur = next; next = null;
                input.reset();
                cur.enter();
                fadeDir = -1;
            }
        } else if (fadeDir == -1) {
            fade -= dt * 3.5f;
            if (fade <= 0f) { fade = 0f; fadeDir = 0; }
        }
        boolean vis = touchUiVisible();
        if (vis != lastTouchVis) { lastTouchVis = vis; input.releaseTouch(); }
        cur.t += dt;
        cur.update(dt);
        if (!cur.keepInput()) input.endFrame();
    }

    @Override
    public void render(Platform.Gfx g) {
        cur.render(g);
        if (fade > 0.001f) g.rect(0, 0, viewW, Platform.VIEW_H, Mth.withAlpha(0x000000, (int) (Mth.clamp(fade, 0, 1) * 255)), false);
    }

    @Override
    public void touch(int id, int action, float x, float y) {
        if (fadeDir == 1) return;
        keyboardUsed = false;
        if (action == Platform.ACTION_DOWN) noteTouch();
        cur.touch(id, action, x, y);
    }

    @Override
    public void key(int code, boolean down) {
        if (code == Pad.EV_CONNECTED) { padConnected(down); return; }
        if (code >= Pad.EV_TYPE_BASE && code < Pad.EV_TYPE_BASE + 3) { if (down) padType = code - Pad.EV_TYPE_BASE; return; }
        keyboardUsed = true;
        if (Pad.isPad(code)) {
            if (down) padActivity();
            input.key(code, down);
            if (cur.wantsRawKeys()) { cur.rawKey(code, down); return; }
            if (fadeDir != 1 && !cur.gameplayInput()) { int mk = Pad.menuKey(code); if (mk > 0) cur.key(mk, down); }
            return;
        }
        if (down) lastDevice = 1;
        input.key(code, down);
        if (fadeDir == 1) return;
        if (cur.wantsRawKeys()) cur.rawKey(code, down); else cur.key(code, down);
    }

    @Override
    public boolean back() {
        if (cur == null) return false;
        return cur.back();
    }

    @Override
    public void pause() {
        if (cur != null) cur.pause();
        if (P != null) { P.audio().pauseAll(); Save.S.write(); }
    }

    @Override
    public void resume() {
        if (P != null) P.audio().resumeAll();
        if (cur != null) cur.resume();
    }
}
