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
        cur.touch(id, action, x, y);
    }

    @Override
    public void key(int code, boolean down) {
        keyboardUsed = true;
        input.key(code, down);
        if (fadeDir != 1) cur.key(code, down);
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
