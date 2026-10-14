package com.julianfarks.roguelike.core;

/** Cargar partida: autoguardado y 3 ranuras. */
final class LoadScreen extends Screen {
    private final Screens.TitleBg bg = new Screens.TitleBg();
    private static final int[] IDS = {RunSave.AUTO, 0, 1, 2};

    LoadScreen(Game g) { super(g); }

    @Override void enter() { layout(); }

    @Override void layout() {
        hits.clear();
        int w = W();
        add(6, 4, 54, 18, "Atrás", () -> back());
        float bw = Math.min(400, w - 24), x = w / 2f - bw / 2f;
        for (int i = 0; i < IDS.length; i++) {
            final int slot = IDS[i];
            Hit h = add(x, 52 + i * 44, bw, 40, null, () -> {
                RunScreen r = RunSave.load(game, slot);
                if (r == null) { Snd.sfx("ui_error", 0.7f); return; }
                Snd.sfx("ui_start_run", 1f);
                game.go(r);
            });
            h.plain = true; h.tag = slot;
        }
    }

    @Override boolean back() { game.go(new Screens.Title(game)); return true; }

    @Override void update(float dt) { bg.update(dt, W()); t += dt; }

    @Override void render(Platform.Gfx g) {
        int w = W();
        bg.render(g, w, 0.6f);
        UI.big.center(g, "CARGAR PARTIDA", w / 2f, 8, UI.GOLD, 1f);
        float bw = Math.min(400, w - 24), x = w / 2f - bw / 2f;
        for (int i = 0; i < IDS.length; i++) {
            int slot = IDS[i];
            String info = RunSave.info(game.P, slot);
            float y = 52 + i * 44;
            UI.panel(g, info != null ? 1 : 0, x, y, bw, 40, 0.95f);
            UI.small.draw(g, slot == RunSave.AUTO ? "Autoguardado" : "Ranura " + (slot + 1), x + 8, y + 6, info != null ? UI.GOLD : UI.GREY, 1f);
            if (info == null) UI.small.draw(g, "Vacía", x + 8, y + 22, UI.GREY, 1f);
            else UI.small.drawWrapped(g, info, x + 8, y + 19, (int) bw - 16, 0xE8E0E0, 1f);
        }
        drawButtons(g);
        UI.small.center(g, "Toca una ranura para continuar donde la dejaste (empiezas al inicio de la sala).", w / 2f, 238, UI.GREY, 1f);
    }
}
