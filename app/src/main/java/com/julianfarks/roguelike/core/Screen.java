package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** Pantalla base con botones tactiles (lista de zonas) y navegacion por teclado. */
abstract class Screen {
    static final class Hit {
        float x, y, w, h;
        String label, icon;
        Runnable act;
        boolean disabled, noSound, plain;
        int tag;
        Hit(float x, float y, float w, float h, String label, Runnable act) { this.x = x; this.y = y; this.w = w; this.h = h; this.label = label; this.act = act; }
        boolean inside(float px, float py) { return px >= x && px < x + w && py >= y && py < y + h; }
    }

    protected Game game;
    protected final List<Hit> hits = new ArrayList<>();
    protected Hit down;
    protected int downId = -1;
    protected int sel = 0;
    protected float t;

    Screen(Game g) { this.game = g; }

    void enter() { layout(); }
    void layout() { }
    void resize() { layout(); }
    abstract void update(float dt);
    abstract void render(Platform.Gfx g);
    boolean back() { return false; }
    boolean keepInput() { return false; }
    void pause() { }
    void resume() { }

    protected int W() { return game.viewW; }

    protected Hit add(float x, float y, float w, float h, String label, Runnable act) {
        Hit hh = new Hit(x, y, w, h, label, act);
        hits.add(hh);
        return hh;
    }

    protected void click(Hit h) {
        if (h.disabled) { Snd.sfx("ui_error", 0.7f); return; }
        if (!h.noSound) Snd.sfx("ui_click", 0.8f);
        if (h.act != null) h.act.run();
    }

    void touch(int id, int action, float x, float y) {
        if (action == Platform.ACTION_DOWN) {
            if (down != null) return;
            for (int i = hits.size() - 1; i >= 0; i--) {
                Hit h = hits.get(i);
                if (h.inside(x, y) && h.act != null) { down = h; downId = id; sel = i; break; }
            }
        } else if (action == Platform.ACTION_UP) {
            if (id == downId && down != null) {
                Hit h = down;
                down = null; downId = -1;
                if (h.inside(x, y)) click(h);
            }
        } else if (action == Platform.ACTION_MOVE) {
            if (id == downId && down != null && !down.inside(x, y)) { /* sigue pulsado hasta soltar */ }
        }
    }

    void key(int code, boolean isDown) {
        if (!isDown) return;
        List<Hit> act = new ArrayList<>();
        for (Hit h : hits) if (h.act != null && !h.plain) act.add(h);
        if (act.isEmpty()) return;
        int cur = act.indexOf(hits.size() > sel && sel >= 0 ? hits.get(sel) : null);
        if (cur < 0) cur = 0;
        if (code == 38 || code == 'W' || code == 37 || code == 'A') { cur = (cur + act.size() - 1) % act.size(); sel = hits.indexOf(act.get(cur)); Snd.sfx("ui_hover", 0.5f); }
        else if (code == 40 || code == 'S' || code == 39 || code == 'D') { cur = (cur + 1) % act.size(); sel = hits.indexOf(act.get(cur)); Snd.sfx("ui_hover", 0.5f); }
        else if (code == 10 || code == 32 || code == 'J') click(act.get(cur));
        else if (code == 27) back();
    }

    protected int state(Hit h) {
        if (h == down) return 2;
        if (hits.indexOf(h) == sel && game.keyboardUsed) return 1;
        return 0;
    }

    protected void drawButton(Platform.Gfx g, Hit h) {
        UI.button(g, h.label, h.x, h.y, h.w, h.h, state(h), h.disabled);
        if (h.icon != null) UI.iconC(g, h.icon, h.x + 14, h.y + h.h / 2f, 1f, h.disabled ? 0.5f : 1f);
    }

    protected void drawButtons(Platform.Gfx g) {
        for (Hit h : hits) if (!h.plain) drawButton(g, h);
    }

    /** Texto con sombra. */
    protected static void txt(Platform.Gfx g, Font f, String s, float x, float y, int c, float a) {
        if (f == null) return;
        f.draw(g, s, x, y, c, a);
    }

    protected static void ctr(Platform.Gfx g, Font f, String s, float cx, float y, int c) {
        if (f == null) return;
        f.center(g, s, cx, y, c, 1f);
    }
}
