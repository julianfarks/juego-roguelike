package com.julianfarks.roguelike.core;

/**
 * Menu "Video y graficos" (solo PC). Tres paginas: Pantalla, Rendimiento y Calidad.
 * Los cambios se preparan en {@link #pend} y se aplican con "Aplicar"; si cambia el modo o la resolucion de pantalla
 * se pide confirmacion durante 10 s y, si no se confirma (o la pantalla queda mal), se vuelve a la configuracion anterior.
 */
final class VideoScreen extends Screen {
    private static final float CONFIRM_SECS = 10f;
    private final Platform.Video vid;
    private final VideoCfg pend;           // lo que se esta editando
    private VideoCfg applied;              // lo que esta aplicado y guardado
    private int tab;
    private float confirmT;                // >0 = esperando confirmacion
    private VideoCfg before;               // configuracion a la que se vuelve si no se confirma
    private String toast = "";
    private float toastT;
    private final Screens.TitleBg bg = new Screens.TitleBg();

    VideoScreen(Game g) {
        super(g);
        vid = g.P.video();
        applied = VideoCfg.cur.copy();
        pend = applied.copy();
    }

    private static String modeName(int m) { return m == VideoCfg.MODE_FULL ? "Pantalla completa" : (m == VideoCfg.MODE_BORDERLESS ? "Ventana sin bordes" : "Ventana"); }
    private static String qName(int q) { return q == VideoCfg.Q_LOW ? "Baja" : (q == VideoCfg.Q_MED ? "Media" : (q == VideoCfg.Q_HIGH ? "Alta" : "Personalizada")); }
    private static String onOff(boolean b) { return b ? "SÍ" : "NO"; }

    /** Indice de la resolucion actual dentro de la lista del monitor (o la mas parecida). */
    private int resIndex(int[][] rs) {
        int best = 0, bd = Integer.MAX_VALUE;
        for (int i = 0; i < rs.length; i++) {
            int d = Math.abs(rs[i][0] - pend.resW) + Math.abs(rs[i][1] - pend.resH);
            if (d < bd) { bd = d; best = i; }
        }
        return best;
    }

    @Override void layout() {
        hits.clear();
        int w = W();
        float cx = w / 2f, bw = 236, x = cx - bw / 2f;
        if (confirmT > 0) {
            add(cx - 104, 160, 100, 22, "Mantener", this::keep);
            add(cx + 4, 160, 100, 22, "Revertir", this::revert);
            sel = 0;
            return;
        }
        String[] tn = {"Pantalla", "Rendimiento", "Calidad"};
        float tw = 76;
        for (int i = 0; i < 3; i++) {
            final int ti = i;
            Hit h = add(cx - tw * 1.5f - 4 + i * (tw + 4), 40, tw, 18, tn[i], () -> { tab = ti; layout(); });
            h.noSound = false;
        }
        float y = 66, st = 24;
        int r = 0;
        if (tab == 0) {
            add(x, y + st * r++, bw, 20, "Modo: " + modeName(pend.mode), () -> { pend.mode = (pend.mode + 1) % 3; layout(); });
            int[][] rs = vid.resolutions();
            String rl = pend.mode == VideoCfg.MODE_BORDERLESS ? "Resolución: nativa (" + vid.nativeRes()[0] + "x" + vid.nativeRes()[1] + ")"
                    : "Resolución: " + pend.resW + "x" + pend.resH;
            Hit rh = add(x, y + st * r++, bw, 20, rl, () -> {
                int[][] l = vid.resolutions();
                int i = (resIndex(l) + 1) % l.length;
                pend.resW = l[i][0]; pend.resH = l[i][1];
                layout();
            });
            rh.disabled = pend.mode == VideoCfg.MODE_BORDERLESS || rs.length == 0;
        } else if (tab == 1) {
            add(x, y + st * r++, bw, 20, "Límite de FPS: " + pend.fps, () -> { pend.fps = pend.fps == 30 ? 60 : 30; layout(); });
            add(x, y + st * r++, bw, 20, "V-Sync: " + onOff(pend.vsync), () -> { pend.vsync = !pend.vsync; layout(); });
            add(x, y + st * r++, bw, 20, "Mostrar FPS: " + onOff(pend.showFps), () -> { pend.showFps = !pend.showFps; layout(); });
            add(x, y + st * r++, bw, 20, "Escalado: " + (pend.scaleMode == 0 ? "Entero (nítido)" : "Ajustado a la ventana"), () -> { pend.scaleMode ^= 1; layout(); });
        } else {
            add(x, y + st * r++, bw, 20, "Calidad: " + qName(pend.quality), () -> { pend.applyPreset(pend.quality >= VideoCfg.Q_HIGH ? VideoCfg.Q_LOW : pend.quality + 1); layout(); });
            add(x, y + st * r++, bw, 20, "Partículas: " + pend.particles + "%", () -> {
                int i = 0;
                for (int k = 0; k < VideoCfg.PARTICLE_OPTIONS.length; k++) if (VideoCfg.PARTICLE_OPTIONS[k] == pend.particles) i = k;
                pend.particles = VideoCfg.PARTICLE_OPTIONS[(i + 1) % VideoCfg.PARTICLE_OPTIONS.length];
                pend.syncPreset(); layout();
            });
            add(x, y + st * r++, bw, 20, "Brillos e iluminación: " + onOff(pend.light), () -> { pend.light = !pend.light; pend.syncPreset(); layout(); });
            add(x, y + st * r++, bw, 20, "Viñeta: " + onOff(pend.vig), () -> { pend.vig = !pend.vig; pend.syncPreset(); layout(); });
        }
        float by = 226;
        Hit ap = add(cx - 122, by, 78, 22, "Aplicar", this::apply);
        ap.disabled = pend.same(applied);
        add(cx - 39, by, 78, 22, "Predeterm.", this::restore);
        add(cx + 44, by, 78, 22, "Volver", () -> back());
        if (sel >= hits.size()) sel = 0;
    }

    private void apply() {
        if (pend.same(applied)) return;
        before = applied.copy();
        boolean displayChanged = !pend.sameDisplay(applied) || pend.vsync != applied.vsync;
        boolean ok = vid.apply(pend);
        if (!ok) {
            vid.apply(before);
            say("No se pudo aplicar; se mantiene la configuración anterior.");
            return;
        }
        pend.pushEffects();
        if (displayChanged && !pend.sameDisplay(before)) {
            confirmT = CONFIRM_SECS;           // espera confirmacion; hasta entonces no se guarda
            VideoCfg.cur = pend.copy();
        } else {
            commit();
        }
        layout();
    }

    private void commit() {
        applied = pend.copy();
        VideoCfg.save(game.P, applied);
        confirmT = 0;
        before = null;
        say("Configuración guardada.");
    }

    private void keep() { commit(); layout(); }

    private void revert() {
        if (before != null) {
            vid.apply(before);
            pend.set(before);
            before.pushEffects();
            VideoCfg.cur = before.copy();
            applied = before.copy();
        }
        confirmT = 0;
        before = null;
        say("Se restauró la configuración anterior.");
        layout();
    }

    private void restore() {
        pend.set(VideoCfg.defaults());
        int[] dr = vid.defaultRes();
        pend.resW = dr[0]; pend.resH = dr[1];
        apply();
        if (confirmT <= 0 && pend.same(applied)) say("Ajustes predeterminados restaurados.");
        layout();
    }

    private void say(String s) { toast = s; toastT = 3f; }

    @Override boolean back() {
        if (confirmT > 0) { revert(); return true; }
        game.go(new Screens.Options(game, false));
        return true;
    }

    @Override void update(float dt) {
        bg.update(dt, W());
        if (toastT > 0) toastT -= dt;
        if (confirmT > 0) {
            confirmT -= dt;
            if (confirmT <= 0) revert();
        }
    }

    @Override void render(Platform.Gfx g) {
        int w = W();
        float cx = w / 2f;
        bg.render(g, w, 0.45f);
        UI.panel(g, 0, cx - 136, 14, 272, 238, 0.95f);
        UI.big.center(g, "VÍDEO Y GRÁFICOS", cx, 22, UI.GOLD, 1f);
        if (confirmT > 0) {
            UI.panel(g, 0, cx - 120, 96, 240, 96, 1f);
            UI.small.center(g, "¿Mantener esta configuración?", cx, 106, UI.WHITE, 1f);
            UI.small.center(g, "Se revertirá automáticamente en {} s".replace("{}", String.valueOf((int) Math.ceil(confirmT))), cx, 126, UI.GOLD, 1f);
            drawButtons(g);
            return;
        }
        // pestana activa resaltada
        for (int i = 0; i < 3 && i < hits.size(); i++) if (i == tab) g.rect(hits.get(i).x, hits.get(i).y + hits.get(i).h, hits.get(i).w, 2, 0xFFFFD25A, false);
        drawButtons(g);
        float ty = 66 + 24 * (tab == 0 ? 2 : 4) + 4;
        int[] nr = vid.nativeRes();
        if (tab == 0) {
            UI.small.center(g, "Monitor: {}x{} · {} Hz".replaceFirst("\\{\\}", String.valueOf(nr[0])).replaceFirst("\\{\\}", String.valueOf(nr[1])).replaceFirst("\\{\\}", String.valueOf(vid.refreshHz())), cx, ty, UI.GREY, 1f);
            UI.small.center(g, "Completa cambia la resolución del monitor.", cx, ty + 14, UI.GREY, 1f);
            UI.small.center(g, "Sin bordes usa la resolución nativa.", cx, ty + 26, UI.GREY, 1f);
        } else if (tab == 1) {
            UI.small.center(g, "El juego simula a 60 pasos por segundo:", cx, ty, UI.GREY, 1f);
            UI.small.center(g, "más de 60 FPS no añadirían fluidez.", cx, ty + 12, UI.GREY, 1f);
            UI.small.center(g, "Escalado entero = píxeles perfectos.", cx, ty + 28, UI.GREY, 1f);
        } else {
            UI.small.center(g, "El motor no usa sombras dinámicas,", cx, ty, UI.GREY, 1f);
            UI.small.center(g, "así que no hay opción de sombras.", cx, ty + 12, UI.GREY, 1f);
            UI.small.center(g, "Los píxeles nunca se suavizan.", cx, ty + 24, UI.GREY, 1f);
        }
        if (toastT > 0) UI.small.center(g, toast, cx, 212, UI.GREEN, Math.min(1f, toastT));
    }
}
