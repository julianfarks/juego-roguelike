package com.julianfarks.roguelike.core;

/** Pantallas del centro de operaciones: estadisticas de la cuenta y trofeos. Solo muestran datos reales guardados en Save. */
final class OpsScreens {
    private OpsScreens() {}

    static String time(long ms) {
        long s = ms / 1000L;
        return String.format("%d:%02d:%02d", s / 3600, (s / 60) % 60, s % 60);
    }

    // =================================================================== estadisticas
    static final class Stats extends Screen {
    @Override boolean center270() { return true; }
        private final Screens.TitleBg bg = new Screens.TitleBg();
        Stats(Game g) { super(g); }

        private int page;
        @Override void layout() {
            hits.clear();
            add(W() / 2f - 90, 244, 80, 22, "Volver", () -> back());
            add(W() / 2f + 10, 244, 90, 22, page == 0 ? "Infinito" : "Cuenta", () -> { page = 1 - page; layout(); });
        }
        @Override boolean back() { game.go(new Ops(game)); return true; }
        @Override void update(float dt) { bg.update(dt, W()); t += dt; }

        static String[][] rows(Save s) {
            int best = -1, bn = 0;
            for (int i = 0; i < 10; i++) if (s.classRuns[i] > bn) { bn = s.classRuns[i]; best = i; }
            return new String[][]{
                    {"Partidas iniciadas", String.valueOf(s.started)},
                    {"Partidas terminadas", String.valueOf(s.runs)},
                    {"Victorias", String.valueOf(s.wins)},
                    {"Derrotas", String.valueOf(s.losses)},
                    {"Rondas completadas", String.valueOf(s.rounds)},
                    {"Mayor racha de rondas", String.valueOf(s.bestStreak)},
                    {"Mayor sala alcanzada", String.valueOf(s.bestRooms)},
                    {"Enemigos derrotados", String.valueOf(s.kills)},
                    {"Máx. enemigos en una ronda", String.valueOf(s.maxKillsRound)},
                    {"Rondas perfectas (sin daño)", String.valueOf(s.perfectRounds)},
                    {"Mejor racha de rondas perfectas", String.valueOf(s.bestPerfectStreak)},
                    {"Jefes derrotados", String.valueOf(s.bossKills)},
                    {"Cofres abiertos", s.chestsOpened + " (secretos: " + s.secretChests + ")"},
                    {"Trofeos desbloqueados", Trophies.count(s) + " / " + Trophies.ALL.length},
                    {"Espadachín más usado", best < 0 ? "ninguno aún" : ClassDef.ALL[best].name + " (" + bn + ")"},
                    {"Tiempo total de juego", time(s.playMs)},
            };
        }

        /** Pagina del modo infinito: acumulados y ultimos resultados guardados (los registros alterados se ignoran). */
        static String[][] infRows(Save s) {
            java.util.List<String[]> l = new java.util.ArrayList<>();
            l.add(new String[]{"Runs infinitas", String.valueOf(s.infRuns)});
            l.add(new String[]{"Récord de pisos completados", String.valueOf(s.infBestFloor)});
            l.add(new String[]{"Mejor puntaje", String.valueOf(s.infBestScore)});
            l.add(new String[]{"Pisos completados (total)", String.valueOf(s.infFloors)});
            l.add(new String[]{"Enemigos derrotados (infinito)", String.valueOf(s.infKills)});
            l.add(new String[]{"Jefes derrotados (infinito)", String.valueOf(s.infBosses)});
            l.add(new String[]{"Mayor tiempo de supervivencia", String.format("%d:%02d", s.infBestTimeS / 60, s.infBestTimeS % 60)});
            l.add(new String[]{"Últimas runs:", ""});
            int n = 0;
            for (int i = s.infLog.size() - 1; i >= 0 && n < 5; i--) {
                Infinite.Result r = Infinite.Result.parse(s.infLog.get(i));
                if (r == null) continue;
                l.add(new String[]{"  " + ClassDef.ALL[Math.max(0, Math.min(9, r.cls))].name + " · piso " + r.reached + (r.dev ? " [prueba]" : ""), r.floors + " completados · " + r.score + " pts"});
                n++;
            }
            if (n == 0) l.add(new String[]{"  (aún no has jugado el modo infinito)", ""});
            return l.toArray(new String[0][]);
        }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.65f);
            UI.big.center(g, page == 0 ? "ESTADISTICAS" : "MODO INFINITO", w / 2f, 6, page == 0 ? UI.GOLD : UI.PURPLE, 1f);
            UI.small.center(g, page == 0 ? "Datos reales de tu cuenta" : "Registro local de tus runs (criterio principal: pisos completados)", w / 2f, 24, UI.GREY, 1f);
            String[][] r = page == 0 ? rows(Save.S) : infRows(Save.S);
            float pw = Math.min(w - 24, 460), px = w / 2f - pw / 2f;
            UI.panel(g, 0, px, 36, pw, 204, 0.94f);
            for (int i = 0; i < r.length; i++) {
                float y = 42 + i * 12.2f;
                if (i % 2 == 0) g.rect(px + 4, y - 1, pw - 8, 12, 0x22FFFFFF, false);
                UI.small.draw(g, r[i][0], px + 10, y + 1, UI.WHITE, 1f);
                UI.small.right(g, r[i][1], px + pw - 10, y + 1, UI.GOLD, 1f);
            }
            drawButtons(g);
        }
    }

    // =================================================================== trofeos
    static final class Trophy extends Screen {
        private final Screens.TitleBg bg = new Screens.TitleBg();
        Trophy(Game g) { super(g); }

        @Override void layout() { hits.clear(); add(W() / 2f - 40, ViewSize.h - 26, 80, 22, "Volver", () -> back()); }
        @Override boolean back() { game.go(new Ops(game)); return true; }
        @Override void update(float dt) { bg.update(dt, W()); t += dt; }

        /** Tarjeta: nombre arriba a todo el ancho, filete, copa a la izquierda y descripcion a su lado, barra de progreso abajo.
         *  El alto de las tarjetas sale del alto real de la pantalla (270-320) y la descripcion nunca baja hasta la barra. */
        @Override void render(Platform.Gfx g) {
            int w = W(), h = ViewSize.h;
            bg.render(g, w, 0.65f);
            Save s = Save.S;
            UI.title(g, "TROFEOS", w / 2f, 6, UI.GOLD, 1f);
            UI.small.center(g, Trophies.count(s) + " de " + Trophies.ALL.length + " desbloqueados", w / 2f, 23, UI.GREY, 1f);
            int cols = 4, n = Trophies.ALL.length, rows = (n + cols - 1) / cols;
            float top = 35, bottom = h - 30, gap = 3;
            float cw = Math.min((w - 20) / cols - gap, 140), ch = Math.min(64, (bottom - top - (rows - 1) * gap) / rows), gx = w / 2f - (cols * (cw + gap) - gap) / 2f;
            int lh = I18n.lang() == I18n.ZH ? 13 : 9;
            for (int i = 0; i < n; i++) {
                Trophies.T tr = Trophies.ALL[i];
                float x = gx + (i % cols) * (cw + gap), y = top + (i / cols) * (ch + gap);
                boolean got = Trophies.has(s, i);
                UI.panel(g, got ? 1 : 0, x, y, cw, ch, got ? 1f : 0.8f);
                if (got) UI.light(g, x + cw / 2f, y + ch / 2f, cw * 0.45f, 0xFFD25A, 0.10f);
                int col = got ? 0xFFD25A : 0x4A4658;
                UI.small.draw(g, UI.fitLabel(UI.small, tr.name, cw - 10), x + 5, y + 3, got ? UI.GOLD : UI.GREY, 1f);
                g.rect(x + 5, y + 3 + lh + 1, cw - 10, 1, got ? 0x88B8A050 : 0x44B8A050, false);
                float cy = y + lh + (lh > 10 ? 5 : 7);
                g.rect(x + 6, cy, 10, 7, Mth.withAlpha(col, 255), false);
                g.rect(x + 9, cy + 7, 4, 5, Mth.withAlpha(col, 255), false);
                g.rect(x + 6, cy + 12, 10, 2, Mth.withAlpha(col, 255), false);
                float barY = y + ch - 5;                         // barra fina pegada al borde inferior: la descripcion usa todo el resto
                int maxL = Math.max(1, (int) ((barY - cy + 1) / lh));
                UI.small.drawWrappedMax(g, tr.desc, x + 20, cy - 1, (int) cw - 23, got ? 0xE8E0E0 : 0x9A98A8, 1f, lh, maxL);
                if (!got) {
                    int p = Math.min(tr.goal, tr.prog.applyAsInt(s));
                    float bw = cw - 12;
                    g.rect(x + 6, barY, bw, 2, 0xFF1A1620, false);
                    g.rect(x + 6, barY, bw * p / (float) tr.goal, 2, 0xFF7AF0FF, false);
                }
            }
            drawButtons(g);
        }
    }

    // =================================================================== estaciones aun por activar
    /** Estacion cuyo sistema todavia no esta implementado: lo dice con claridad y no simula contenido. */
    static final class Pending extends Screen {
    @Override boolean center270() { return true; }
        private final Screens.TitleBg bg = new Screens.TitleBg();
        private final String title; private final String[] lines;
        Pending(Game g, String title, String... lines) { super(g); this.title = title; this.lines = lines; }
        @Override void layout() { hits.clear(); add(W() / 2f - 40, 244, 80, 22, "Volver", () -> back()); }
        @Override boolean back() { game.go(new Ops(game)); return true; }
        @Override void update(float dt) { bg.update(dt, W()); t += dt; }
        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.65f);
            UI.big.center(g, title, w / 2f, 40, UI.GOLD, 1f);
            UI.panel(g, 0, w / 2f - 150, 90, 300, 20 + lines.length * 16, 0.95f);
            for (int i = 0; i < lines.length; i++) UI.small.center(g, lines[i], w / 2f, 100 + i * 16, i == 0 ? UI.WHITE : UI.GREY, 1f);
            drawButtons(g);
        }
    }
}
