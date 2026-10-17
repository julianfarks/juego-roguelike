package com.julianfarks.roguelike.core;

import java.util.List;

/** Reproductor de cinematicas (Story.Cine): fondos procedurales con parallax, texto progresivo, saltable. */
final class Cinematic extends Screen {
    private final Story.Cine cine;
    private final Runnable done;
    private final Particles ps = new Particles();
    private final Rng rng = new Rng(11);
    private final Dlg dlg;
    private int slide;
    private float sceneT, slideT, holdT;
    private float fadeBlack = 1f;     // 1 = negro
    private int fadeDir = -1;         // -1 abriendo, 1 cerrando
    private int pendingSlide = -1;
    private boolean finished, skipping;
    private final boolean[] starInit = new boolean[1];
    private float[] sx = new float[70], sy = new float[70], sp = new float[70];

    Cinematic(Game g, Story.Cine cine, Runnable done) {
        super(g);
        this.cine = cine; this.done = done;
        dlg = new Dlg(UI.small, 400, 3);
        for (int i = 0; i < sx.length; i++) { sx[i] = rng.f() * 700; sy[i] = rng.f() * 150; sp[i] = rng.f() * 6.28f; }
    }

    @Override void enter() {
        Snd.music(cine.id.equals("final") ? "mus_final_3" : "mus_sanctuary", true);
        Snd.ambient(null, 0);
        loadSlide();
        layout();
    }

    @Override void layout() {
        hits.clear();
        int w = W();
        add(0, 0, w, Platform.VIEW_H, null, this::tap).plain = true;
        Hit sk = add(w - 62, 6, 56, 16, "Saltar", this::skip);
        sk.noSound = false;
    }

    private void loadSlide() {
        Story.Slide s = cine.slides[slide];
        dlg.set(s.who, s.text);
        slideT = 0; holdT = 0;
    }

    private void tap() {
        if (finished || fadeDir == 1) return;
        if (dlg.advance()) next();
    }

    private void next() {
        if (slide + 1 >= cine.slides.length) { end(); return; }
        pendingSlide = slide + 1;
        fadeDir = 1;
        // dentro de una misma escena el fundido es corto (solo el texto cambia)
    }

    private void skip() { if (!finished) end(); }

    private void end() {
        if (finished) return;
        finished = true;
        if (cine.id.equals("intro")) Story.mark(Story.S_INTRO);
        if (cine.id.equals("final")) Story.mark(Story.S_FINAL_SEEN);
        if (done != null) done.run();
    }

    @Override boolean back() { skip(); return true; }

    @Override void key(int code, boolean down) {
        if (!down) return;
        if (code == 10 || code == 32 || code == 'J' || code == 39 || code == 'D') tap();
        else if (code == 27 || code == 'K') skip();
    }

    @Override void update(float dt) {
        if (finished) return;
        sceneT += dt; slideT += dt;
        dlg.update(dt);
        ps.update(dt);
        int bg = cine.slides[slide].bg;
        if (rng.chance(dt * 14)) spawnAmbient(bg);
        // avance automatico: texto completo + tiempo de lectura segun longitud
        if (fadeDir == -1 && dlg.full()) {
            holdT += dt;
            int len = cine.slides[slide].text.length();
            if (holdT > 2.2f + len / 38f) { if (dlg.advance()) next(); }
        }
        if (fadeDir == 1) {
            boolean sameScene = pendingSlide >= 0 && pendingSlide < cine.slides.length && cine.slides[pendingSlide].bg == bg;
            fadeBlack += dt * (sameScene ? 4f : 2.4f);
            if (sameScene) fadeBlack = Math.min(fadeBlack, 0.55f);
            if (fadeBlack >= (sameScene ? 0.55f : 1f)) {
                int old = slide;
                slide = pendingSlide; pendingSlide = -1;
                if (cine.slides[slide].bg != cine.slides[old].bg) { sceneT = 0; ps.clear(); }
                loadSlide();
                fadeDir = -1;
            }
        } else if (fadeDir == -1) {
            fadeBlack = Math.max(0, fadeBlack - dt * 1.6f);
        }
    }

    private void spawnAmbient(int bg) {
        int w = W();
        switch (bg) {
            case Story.BG_ABYSS: case Story.BG_HUNTER:
                ps.spawn(rng.f(0, w), -4, rng.f(-8, 14), rng.f(10, 28), rng.f(5, 9), 1, 0, rng.chance(0.5f) ? 0xAA8890 : 0xD04050, false); break;
            case Story.BG_DESCENT: case Story.BG_TRUTH:
                ps.spawn(rng.f(0, w), Platform.VIEW_H + 3, rng.f(-10, 10), -rng.f(14, 40), rng.f(4, 8), rng.chance(0.3f) ? 2 : 1, 0, rng.chance(0.5f) ? 0xFF8A3A : 0xFFD070, true); break;
            case Story.BG_SEVEN: case Story.BG_RELICS:
                ps.spawn(rng.f(0, w), rng.f(40, 220), rng.f(-6, 6), -rng.f(6, 18), rng.f(3, 6), 1, 0, 0xFFE8A0, true); break;
            case Story.BG_SHATTER:
                if (sceneT > 3.2f) ps.spawn(w / 2f + rng.f(-60, 60), rng.f(30, 120), rng.f(-30, 30), rng.f(10, 60), rng.f(3, 6), rng.chance(0.4f) ? 3 : 2, 90, 0xE04050, false); break;
            default:
                ps.spawn(rng.f(0, w), Platform.VIEW_H + 3, rng.f(-6, 6), -rng.f(8, 24), rng.f(5, 9), 1, 0, 0xFFE8A0, true); break;
        }
    }

    @Override void render(Platform.Gfx g) {
        int w = W();
        int bg = cine.slides[slide].bg;
        CineArt.draw(g, w, bg, sceneT, sx, sy, sp);
        ps.render(g, 0, 0);
        // bandas de cine
        g.rect(0, 0, w, 26, 0xFF000000, false);
        g.rect(0, Platform.VIEW_H - 26, w, 26, 0xFF000000, false);
        if (UI.vignette != null) g.image(UI.vignette, 0, 0, UI.vignette.w, UI.vignette.h, 0, 0, w, Platform.VIEW_H, 0, 0, 0.6f);
        // titulo de la cinematica al inicio
        if (slide == 0 && slideT < 3.2f) {
            float a = Mth.clamp(Math.min(slideT / 0.8f, (3.2f - slideT) / 0.8f), 0, 1);
            UI.big.center(g, cine.title, w / 2f, 96, 0xF0E0D0, a);
            g.rect(w / 2f - 80 * a, 120, 160 * a, 1, 0x88FFD25A, false);
        }
        // cuadro de texto
        float bw = Math.min(w - 40, 430), bx = w / 2f - bw / 2f;
        dlg.draw(g, bx, 196, bw, 56, 1f - Mth.clamp(fadeBlack * 1.4f, 0, 1), time());
        // indicador de pagina y saltar
        for (Hit h : hits) if (!h.plain) drawButton(g, h);
        UI.small.center(g, "Toca para avanzar", w / 2f, 255, UI.GREY, 0.55f);
        if (fadeBlack > 0.001f) g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0x000000, (int) (Mth.clamp(fadeBlack, 0, 1) * 255)), false);
    }

    private float time() { return t; }
}
