package com.julianfarks.roguelike.core;

/** Pantalla "Codigos": campo de texto + teclado en pantalla (tactil) o teclado fisico/mando. */
final class CodesScreen extends Screen {
    @Override boolean center270() { return true; }
    private final Screens.TitleBg bg = new Screens.TitleBg();
    private final StringBuilder text = new StringBuilder();
    private String msg = "";
    private int msgColor = 0xFFE8E0E0;
    private Codes.Res last;
    private static final int MAX = 32;
    private static final String[] ROWS = {"1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm"};

    CodesScreen(Game g) { super(g); }

    @Override void enter() { Snd.music(Snd.MENU_MUSIC, true); layout(); }

    @Override void layout() {
        hits.clear();
        int w = W();
        float kw = Math.min(30, (w - 24) / 10f - 3), kh = 20, gap = 3, y0 = 86;
        for (int r = 0; r < ROWS.length; r++) {
            String row = ROWS[r];
            int n = row.length() + (r == 3 ? 2 : 0);
            float x0 = w / 2f - (n * (kw + gap) - gap) / 2f;
            for (int i = 0; i < row.length(); i++) {
                final char ch = row.charAt(i);
                Hit h = add(x0 + i * (kw + gap), y0 + r * (kh + gap), kw, kh, String.valueOf(ch), () -> type(ch));
                h.noSound = true;
            }
            if (r == 3) {
                add(x0 + row.length() * (kw + gap), y0 + r * (kh + gap), kw * 2 + gap, kh, "Borrar", this::backspace);
            }
        }
        float by = y0 + 4 * (kh + gap) + 6;
        add(w / 2f - 130, by, 80, 22, "Atrás", () -> back());
        Hit ok = add(w / 2f - 40, by, 170, 22, "Canjear", this::redeem);
        ok.disabled = false;
    }

    private void type(char c) { if (text.length() < MAX) { text.append(c); Snd.sfx("ui_hover", 0.5f); } }
    private void backspace() { if (text.length() > 0) text.setLength(text.length() - 1); }

    private void redeem() {
        Codes.Result r = Codes.redeem(text.toString());
        last = r.res; msg = r.msg;
        switch (r.res) {
            case OK: msgColor = 0xFF7AF0A0; Snd.sfx("ui_unlock", 0.9f); text.setLength(0); break;
            case USED: msgColor = 0xFFFFD25A; Snd.sfx("ui_error", 0.7f); break;
            case UNDELIVERABLE: msgColor = 0xFFFFA05A; Snd.sfx("ui_error", 0.7f); break;
            default: msgColor = 0xFFFF6A6A; Snd.sfx("ui_error", 0.8f); break;
        }
    }

    @Override boolean back() { game.go(Screens.home(game)); return true; }

    @Override void key(int code, boolean down) {
        if (!down) return;
        if (code >= 'A' && code <= 'Z') { type((char) (code + 32)); return; }
        if (code >= '0' && code <= '9') { type((char) code); return; }
        if (code == 8 || code == 127) { backspace(); return; }
        if (code == 10 && game.lastDevice != 2) { redeem(); return; }
        super.key(code, down);
    }

    @Override void update(float dt) { bg.update(dt, W()); }

    @Override void render(Platform.Gfx g) {
        int w = W();
        bg.render(g, w, 0.6f);
        UI.big.center(g, "CÓDIGOS", w / 2f, 12, UI.GOLD, 1f);
        UI.small.center(g, "Escribe un código y pulsa Canjear", w / 2f, 34, UI.GREY, 1f);
        float fw = Math.min(w - 40, 300);
        UI.panel(g, 1, w / 2f - fw / 2f, 46, fw, 22, 1f);
        String shown = text.toString();
        boolean cur = (int) (t * 2) % 2 == 0;
        UI.small.center(g, shown + (cur ? "_" : " "), w / 2f, 52, 0xFFF0E8E0, 1f);
        if (!msg.isEmpty()) UI.small.center(g, msg, w / 2f, 72, msgColor, 1f);
        drawButtons(g);
    }
}
