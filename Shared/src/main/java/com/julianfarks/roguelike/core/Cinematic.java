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
    private int transType;           // 0 negro, 1 destello, 2 rojo en diagonal, 3 persianas, 4 iris
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
        int nb = cine.slides[pendingSlide].bg;
        transType = nb == cine.slides[slide].bg ? 0 : transFor(nb);
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
        CineArt.update(dt, ps, rng, w(), bg, sceneT, subIndex(), slideT);
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
                else if (fadeBlack > 0.55f) fadeBlack = 0.55f;
                loadSlide();
                fadeDir = -1;
            }
        } else if (fadeDir == -1) {
            fadeBlack = Math.max(0, fadeBlack - dt * 1.6f);
        }
    }

    private static int transFor(int bg) {
        switch (bg) { case Story.BG_HUNTER: return 2; case Story.BG_SEVEN: return 3; case Story.BG_SHATTER: return 1; case Story.BG_DESCENT: return 4; case Story.BG_TRUTH: return 4; default: return 0; }
    }

    private int w() { return W(); }

    /** Indice de la diapositiva dentro de su escena (para sincronizar eventos visuales con el texto). */
    private int subIndex() { int k = 0, bg = cine.slides[slide].bg; for (int i = slide - 1; i >= 0 && cine.slides[i].bg == bg; i--) k++; return k; }

    private void transition(Platform.Gfx g, int w, float p) {
        int H = Platform.VIEW_H;
        p = Mth.clamp(p, 0, 1);
        switch (transType) {
            case 1: g.rect(0, 0, w, H, Mth.withAlpha(0xFFFFFF, (int) (p * 255)), false); break;                         // destello blanco
            case 2: {                                                                                                   // tajo rojo
                float edge = (w + 80) * p - 40;
                for (int y = 0; y < H; y += 3) { float xx = edge + (y - H / 2f) * 0.35f; g.rect(0, y, Math.max(0, xx), 3, 0xFF050206, false); g.rect(Math.max(0, xx), y, 3, 3, 0xFFE02040, true); }
                break;
            }
            case 3: { int n = 12; float sw = w / (float) n; for (int i = 0; i < n; i++) { float hh = H * Mth.clamp(p * 1.5f - (i % 4) * 0.08f, 0, 1); g.rect(i * sw, (i % 2 == 0) ? 0 : H - hh, sw + 1, hh, 0xFF000000, false); } break; }   // persianas
            case 4: {                                                                                                   // iris
                float r = (1 - p) * (w * 0.62f);
                g.clipBegin(0, 0, w, H);
                for (int y = 0; y < H; y += 2) { float dy = y - H / 2f; float hw = r * r - dy * dy; float half = hw > 0 ? (float) Math.sqrt(hw) : 0; g.rect(0, y, w / 2f - half, 2, 0xFF000000, false); g.rect(w / 2f + half, y, w / 2f - half + 1, 2, 0xFF000000, false); }
                g.clipEnd();
                break;
            }
            default: g.rect(0, 0, w, H, Mth.withAlpha(0x000000, (int) (p * 255)), false);
        }
    }

    @Override void render(Platform.Gfx g) {
        int w = W();
        int bg = cine.slides[slide].bg;
        CineArt.draw(g, w, bg, sceneT, subIndex(), slideT, sx, sy, sp);
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
        if (fadeBlack > 0.001f) transition(g, w, fadeBlack);
    }

    private float time() { return t; }
}
