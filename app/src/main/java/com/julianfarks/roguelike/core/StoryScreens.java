package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** Pantallas de historia: menu "Historia" (rever cinematicas y dialogos) y visor de dialogos. */
final class StoryScreens {
    private StoryScreens() {}

    static void play(Game g, Story.Cine c, Screen back) {
        g.go(new Cinematic(g, c, () -> g.go(back)));
    }

    // =================================================================== menu Historia
    static final class Historia extends Screen {
        private final Screens.TitleBg bg = new Screens.TitleBg();
        private final boolean devAll;

        Historia(Game g, boolean devAll) { super(g); this.devAll = devAll; }

        @Override void enter() { Snd.music("mus_title", true); layout(); }

        @Override void layout() {
            hits.clear();
            int w = W();
            float bw = 170, bh = 23, x = w / 2f - bw / 2f, y = 78;
            int i = 0;
            for (Story.Cine c : Story.CINES) {
                final Story.Cine cc = c;
                boolean locked = !devAll && ((c.id.equals("final") && !Story.finalUnlocked()) || (c.id.equals("intro") && false));
                Hit h = add(x, y + i * 27, bw, bh, locked ? "??? (bloqueado)" : c.title, () -> play(game, cc, new Historia(game, devAll)));
                h.disabled = locked;
                i++;
            }
            Hit d = add(x, y + i * 27, bw, bh, "Diálogos", () -> game.go(new DialogList(game, devAll)));
            d.disabled = !devAll && !anyNpcMet();
            i++;
            add(x, y + i * 27 + 6, bw, bh, "Volver", () -> back());
        }

        static boolean anyNpcMet() { for (int n = 0; n < 3; n++) if (Save.S.story[Story.S_NPC0 + n] > 0) return true; return false; }

        @Override boolean back() { game.go(new Screens.Title(game)); return true; }
        @Override void update(float dt) { bg.update(dt, W()); }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.45f);
            UI.big.center(g, "HISTORIA", w / 2f, 30, UI.GOLD, 1f);
            UI.small.center(g, "Las Siete Espadas del Fin", w / 2f, 52, UI.GREY, 1f);
            drawButtons(g);
            if (!Story.finalUnlocked() && !devAll) UI.small.center(g, "Algunas escenas se desbloquean al avanzar.", w / 2f, 236, UI.GREY, 0.8f);
        }
    }

    // =================================================================== lista de dialogos
    static final class DialogList extends Screen {
        private final Screens.TitleBg bg = new Screens.TitleBg();
        private final boolean devAll;
        private final List<Story.Dialog> list = new ArrayList<>();

        DialogList(Game g, boolean devAll) {
            super(g); this.devAll = devAll;
            for (Story.Dialog d : Story.DIALOGS.values()) if (devAll || (d.npc >= 0 && Save.S.story[Story.S_NPC0 + d.npc] > 0)) list.add(d);
        }

        @Override void layout() {
            hits.clear();
            int w = W();
            float bw = 190, bh = 19, x = w / 2f - bw / 2f, y = 54;
            int cols = list.size() > 7 ? 2 : 1;
            float cw = cols == 2 ? 150 : bw;
            for (int i = 0; i < list.size(); i++) {
                final Story.Dialog d = list.get(i);
                float px = cols == 2 ? w / 2f - cw - 3 + (i % 2) * (cw + 6) : x;
                float py = y + (cols == 2 ? i / 2 : i) * 22;
                add(px, py, cw, bh, Story.NPC_NAMES[Math.max(0, d.npc)] + ": " + d.id.substring(d.id.indexOf('_') + 1), () -> game.go(new DialogView(game, d, devAll)));
            }
            add(w / 2f - 50, 236, 100, 20, "Volver", () -> back());
        }

        @Override boolean back() { game.go(new Historia(game, devAll)); return true; }
        @Override void update(float dt) { bg.update(dt, W()); }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.5f);
            UI.big.center(g, "DIÁLOGOS", w / 2f, 24, UI.GOLD, 1f);
            drawButtons(g);
            if (list.isEmpty()) UI.small.center(g, "Aún no has hablado con nadie.", w / 2f, 120, UI.GREY, 1f);
        }
    }

    // =================================================================== visor de un dialogo (sin efectos sobre la partida)
    static final class DialogView extends Screen {
        private final Screens.TitleBg bg = new Screens.TitleBg();
        private final Story.Dialog d;
        private final Dlg dlg = new Dlg(UI.small, 400, 3);
        private final boolean devAll;
        private int phase;   // 0 lineas, 1 opciones, 2 resultado, 3 fin

        DialogView(Game g, Story.Dialog d, boolean devAll) { super(g); this.d = d; this.devAll = devAll; dlg.set(d.lines); }

        @Override void layout() {
            hits.clear();
            int w = W();
            float bw = Math.min(w - 40, 430), bx = w / 2f - bw / 2f;
            add(0, 0, w, Platform.VIEW_H, null, this::tap).plain = true;
            if (phase == 1) {
                for (int i = 0; i < d.choices.size(); i++) {
                    final Story.Choice c = d.choices.get(i);
                    add(bx, 120 + i * 22, bw, 19, c.label, () -> { phase = 2; dlg.set(d.who, c.res); layout(); });
                }
            }
            Hit sk = add(w - 62, 6, 56, 16, "Salir", () -> back());
            sk.noSound = false;
        }

        private void tap() {
            if (phase == 0 && dlg.advance()) { phase = d.choices.isEmpty() ? 3 : 1; layout(); if (phase == 3) back(); }
            else if (phase == 2 && dlg.advance()) back();
        }

        @Override boolean back() { game.go(new DialogList(game, devAll)); return true; }

        @Override void key(int code, boolean down) {
            if (!down) return;
            if (phase == 1) { super.key(code, down); return; }
            if (code == 10 || code == 32 || code == 'J') tap();
            else if (code == 27) back();
        }

        @Override void update(float dt) { bg.update(dt, W()); dlg.update(dt); }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.6f);
            UI.small.center(g, d.title, w / 2f, 30, UI.GOLD, 1f);
            float bw = Math.min(w - 40, 430), bx = w / 2f - bw / 2f;
            if (phase != 1) dlg.draw(g, bx, 190, bw, 56, 1f, t);
            for (Hit h : hits) if (!h.plain) drawButton(g, h);
        }
    }
}
