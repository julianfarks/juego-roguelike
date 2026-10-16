package com.julianfarks.roguelike.core;

/** Editor de controles tactiles: arrastra cada boton donde quieras y cambia su tamaño. */
final class ControlsEditor extends Screen {
    private final boolean fromRun;
    private final Input in;
    private int selB = Input.B_ATTACK;
    private int dragId = -1, dragB = -1;
    private float offX, offY;
    private Hit minus, plus, reset, done;
    private static final String[] ICONS = {"", "", "", "jump", "attack", "roll", "", "", "", "", "key", "pause", "potion", "attack", "burn", "shield"};

    ControlsEditor(Game g, boolean fromRun) { super(g); this.fromRun = fromRun; this.in = g.input; }

    @Override void enter() { in.layout(W()); layout(); }

    @Override void layout() {
        hits.clear();
        int w = W();
        float y = 6, bw = 46, bh = 20, x = w / 2f - 110;
        minus = add(x, y, bw, bh, "Menos", () -> in.scaleBtn(selB, curScale() - 0.1f));
        plus = add(x + 50, y, bw, bh, "Más", () -> in.scaleBtn(selB, curScale() + 0.1f));
        reset = add(x + 100, y, 60, bh, "Reiniciar", () -> { in.resetCustom(); Save.S.write(); });
        done = add(x + 164, y, 56, bh, "Listo", () -> back());
    }

    private float curScale() { float s = Save.S.ctl[selB * 3 + 2]; return s == 0 ? 1f : s; }

    @Override boolean back() {
        Save.S.write();
        in.layout(W());
        if (fromRun) return false;
        game.go(new Screens.Options(game, false));
        return true;
    }

    @Override void update(float dt) { t += dt; }

    private int pick(float x, float y) {
        int best = -1; float bd = 1e9f;
        for (int i = 0; i < Input.B_COUNT; i++) {
            Input.Btn b = in.btn[i];
            float d = Mth.dist(x, y, b.cx, b.cy);
            if (d <= b.r + 10 && d < bd) { bd = d; best = i; }
        }
        return best;
    }

    @Override void touch(int id, int action, float x, float y) {
        if (action == Platform.ACTION_DOWN) {
            boolean onUi = false;
            for (Hit h : hits) if (h.inside(x, y)) onUi = true;
            if (!onUi) {
                int b = pick(x, y);
                if (b >= 0 && dragId < 0) {
                    selB = b; dragId = id; dragB = b;
                    offX = in.btn[b].cx - x; offY = in.btn[b].cy - y;
                    Snd.sfx("ui_hover", 0.5f);
                    return;
                }
            }
        } else if (action == Platform.ACTION_MOVE) {
            if (id == dragId && dragB >= 0) { in.moveTo(dragB, x + offX, y + offY); return; }
        } else if (action == Platform.ACTION_UP) {
            if (id == dragId) { dragId = -1; dragB = -1; Save.S.write(); return; }
        }
        super.touch(id, action, x, y);
    }

    @Override void render(Platform.Gfx g) {
        int w = W();
        g.rect(0, 0, w, Platform.VIEW_H, 0xFF0C0A12, false);
        for (int x = 0; x < w; x += 24) g.rect(x, 0, 1, Platform.VIEW_H, 0x14FFFFFF, false);
        for (int y = 0; y < Platform.VIEW_H; y += 24) g.rect(0, y, w, 1, 0x14FFFFFF, false);
        UI.small.center(g, "Arrastra los botones donde quieras (izq+der = centro del joystick)", w / 2f, 34, UI.GREY, 1f);
        UI.small.center(g, "Toca uno para elegirlo y cambia su tamaño", w / 2f, 46, UI.GREY, 1f);
        for (int i = 0; i < Input.B_COUNT; i++) {
            Input.Btn b = in.btn[i];
            boolean sel = i == selB;
            UI.roundButton(g, b.cx, b.cy, b.r, sel ? 1 : 0, 0.85f);
            String ic = ICONS[i];
            if (i >= Input.B_S1 && i <= Input.B_ULT) ic = i == Input.B_ULT ? "star" : "burn";
            if (i == Input.B_SEC) ic = "attack";
            if (ic == null) ic = "";
            if (i <= Input.B_DOWN) {
                if (UI.arrow != null) {
                    float ang = i == Input.B_LEFT ? 3.1416f : (i == Input.B_RIGHT ? 0 : 1.5708f);
                    g.imageRot(UI.arrow, 0, 0, 8, 8, b.cx - 8, b.cy - 8, 16, 16, ang, 0, 0, 0.9f);
                }
            } else if (!ic.isEmpty()) UI.iconC(g, ic, b.cx, b.cy, 1f, 1f);
            if (sel) {
                g.circle(b.cx, b.cy, b.r + 3 + (float) Math.sin(t * 6), 0xCCFFD25A, true);
                UI.small.center(g, Input.NAMES[i], b.cx, b.cy - b.r - 12, UI.GOLD, 1f);
            }
        }
        drawButtons(g);
    }
}
