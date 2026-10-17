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
        private final Screens.TitleBg bg = new Screens.TitleBg();
        Stats(Game g) { super(g); }

        @Override void layout() { hits.clear(); add(W() / 2f - 40, 244, 80, 22, "Volver", () -> back()); }
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

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.65f);
            UI.big.center(g, "ESTADISTICAS", w / 2f, 6, UI.GOLD, 1f);
            UI.small.center(g, "Datos reales de tu cuenta", w / 2f, 24, UI.GREY, 1f);
            String[][] r = rows(Save.S);
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

        @Override void layout() { hits.clear(); add(W() / 2f - 40, 244, 80, 22, "Volver", () -> back()); }
        @Override boolean back() { game.go(new Ops(game)); return true; }
        @Override void update(float dt) { bg.update(dt, W()); t += dt; }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.65f);
            Save s = Save.S;
            UI.big.center(g, "TROFEOS", w / 2f, 6, UI.GOLD, 1f);
            UI.small.center(g, Trophies.count(s) + " de " + Trophies.ALL.length + " desbloqueados", w / 2f, 24, UI.GREY, 1f);
            int cols = 4, n = Trophies.ALL.length;
            float cw = Math.min((w - 24) / cols - 4, 116), ch = 44, gx = w / 2f - (cols * (cw + 4) - 4) / 2f;
            for (int i = 0; i < n; i++) {
                Trophies.T tr = Trophies.ALL[i];
                float x = gx + (i % cols) * (cw + 4), y = 36 + (i / cols) * (ch + 4);
                boolean got = Trophies.has(s, i);
                UI.panel(g, got ? 1 : 0, x, y, cw, ch, got ? 1f : 0.8f);
                int col = got ? 0xFFD25A : 0x4A4658;
                g.rect(x + 6, y + 8, 10, 7, Mth.withAlpha(col, 255), false);
                g.rect(x + 9, y + 15, 4, 5, Mth.withAlpha(col, 255), false);
                g.rect(x + 6, y + 20, 10, 2, Mth.withAlpha(col, 255), false);
                UI.small.draw(g, tr.name, x + 20, y + 5, got ? UI.GOLD : UI.GREY, 1f);
                UI.small.drawWrapped(g, tr.desc, x + 20, y + 17, (int) cw - 24, got ? 0xE8E0E0 : 0x808090, 1f);
                if (!got) {
                    int p = Math.min(tr.goal, tr.prog.applyAsInt(s));
                    float bw = cw - 12;
                    g.rect(x + 6, y + ch - 7, bw, 3, 0xFF1A1620, false);
                    g.rect(x + 6, y + ch - 7, bw * p / (float) tr.goal, 3, 0xFF7AF0FF, false);
                }
            }
            drawButtons(g);
        }
    }
}
