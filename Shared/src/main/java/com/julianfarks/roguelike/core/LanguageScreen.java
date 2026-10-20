package com.julianfarks.roguelike.core;

/** Selector de idioma (menu principal). Cambia la interfaz al instante y guarda la preferencia; no toca ningun dato de la partida. */
final class LanguageScreen extends Screen {
    @Override boolean center270() { return true; }
    private final Screens.TitleBg bg = new Screens.TitleBg();
    private float flash;

    LanguageScreen(Game g) { super(g); }

    @Override void layout() {
        hits.clear();
        int w = W();
        float bw = Math.min(220, w - 60), x = w / 2f - bw / 2f;
        for (int i = 0; i < I18n.CODES.length; i++) {
            final int k = i;
            add(x, 66 + i * 34, bw, 28, null, () -> choose(k)).plain = true;
        }
        add(w / 2f - 45, 222, 90, 22, "Volver", () -> back());
    }

    private void choose(int k) {
        if (Save.S.lang == k && I18n.lang() == k) return;
        Save.S.lang = k;
        I18n.set(k);
        Save.S.write();
        flash = 1f;
        layout();
    }

    @Override boolean back() { game.go(new Screens.Title(game)); return true; }
    @Override void update(float dt) { bg.update(dt, W()); t += dt; if (flash > 0) flash -= dt * 2f; }

    @Override void render(Platform.Gfx g) {
        int w = W();
        bg.render(g, w, 0.55f);
        UI.big.center(g, "Idioma", w / 2f, 18, UI.GOLD, 1f);
        UI.small.center(g, "Elige el idioma del juego", w / 2f, 42, UI.GREY, 1f);
        float bw = Math.min(220, w - 60), x = w / 2f - bw / 2f;
        for (int i = 0; i < I18n.CODES.length; i++) {
            boolean on = I18n.lang() == i;
            boolean pressed = hits.size() > i && hits.get(i) == down;
            float y = 66 + i * 34;
            UI.panel(g, on ? 1 : 0, x, y, bw, 28, 0.96f);
            if (on) g.rect(x + 4, y + 4, 3, 20, 0xFF6AE08A, false);
            // el nombre de cada idioma se escribe siempre en su propia lengua y no se traduce
            UI.small.center(g, I18n.NATIVE[i], w / 2f, y + 9, on ? UI.GOLD : (pressed ? UI.WHITE : 0xDDDDEE), 1f);
            if (on) { g.rect(x + bw - 18, y + 14, 3, 3, 0xFF6AE08A, false); g.rect(x + bw - 15, y + 17, 3, 3, 0xFF6AE08A, false); g.rect(x + bw - 12, y + 14, 3, 3, 0xFF6AE08A, false); g.rect(x + bw - 9, y + 11, 3, 3, 0xFF6AE08A, false); g.rect(x + bw - 6, y + 8, 3, 3, 0xFF6AE08A, false); }
        }
        drawButtons(g);
    }
}
