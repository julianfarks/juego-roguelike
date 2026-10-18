package com.julianfarks.roguelike.core;

/**
 * Configuracion de controles: modo de entrada (auto / tactil / mando) y reasignacion de teclas y botones de mando por accion.
 * Se maneja con pantalla tactil, teclado o mando (arriba/abajo/izq/der + aceptar). Los cambios se aplican al instante; "Guardar" los conserva.
 */
final class ControlsScreen extends Screen {
    private static final String[] MODE_NAME = {"Automática", "Táctil", "Mando"};
    private static final int VIS = 8, RH = 17, TOP = 62, ROWS = Input.B_COUNT;

    private final Screens.TitleBg bg = new Screens.TitleBg();
    private final int[] origK, origP;
    private int origMode;
    private int scroll, selR = 0, selC = 0;      // selR: -1 modo, 0..ROWS-1 tabla, ROWS botones de abajo
    // modales
    private int capR = -1;                       // reasignando esta accion
    private float capT;
    private boolean conflict;
    private int cfCode, cfOther, cfCol, cfSel;
    private boolean leaveAsk;
    private int leaveSel;
    private String toast = "";
    private float toastT;

    ControlsScreen(Game g) {
        super(g);
        origK = Save.S.kb.clone(); origP = Save.S.pb.clone(); origMode = Save.S.inputMode;
    }

    private boolean dirty() { return !java.util.Arrays.equals(origK, Save.S.kb) || !java.util.Arrays.equals(origP, Save.S.pb) || origMode != Save.S.inputMode; }
    private boolean modal() { return capR >= 0 || conflict || leaveAsk; }

    // ---------------------------------------------------------------- geometria
    private float pw() { return Math.min(500, W() - 12); }
    private float px() { return (W() - pw()) / 2f; }
    private float cellX(int col) { float pw = pw(); return px() + (col == 0 ? pw * 0.31f : pw * 0.65f); }
    private float cellW() { return pw() * 0.31f - 6; }
    private float rowY(int row) { return TOP + (row - scroll) * RH; }

    @Override boolean wantsRawKeys() { return true; }

    @Override void layout() {
        hits.clear();
        int w = W();
        float pw = pw(), px = px();
        if (conflict) {
            float bw = 112, x0 = w / 2f - (3 * bw + 8) / 2f;
            add(x0, 160, bw, 22, "Intercambiar", () -> resolve(0));
            add(x0 + bw + 4, 160, bw, 22, "Reemplazar", () -> resolve(1));
            add(x0 + 2 * (bw + 4), 160, bw, 22, "Cancelar", () -> resolve(2));
            return;
        }
        if (leaveAsk) {
            float bw = 116, x0 = w / 2f - (3 * bw + 8) / 2f;
            add(x0, 160, bw, 22, "Guardar y salir", () -> leave(0));
            add(x0 + bw + 4, 160, bw, 22, "Descartar", () -> leave(1));
            add(x0 + 2 * (bw + 4), 160, bw, 22, "Seguir editando", () -> leave(2));
            return;
        }
        if (capR >= 0) {
            add(w / 2f - 50, 168, 100, 22, "Cancelar", this::cancelCapture);
            return;
        }
        add(px + 10, 26, 190, 18, "Entrada: " + MODE_NAME[Save.S.inputMode], this::cycleMode);
        for (int r = scroll; r < Math.min(ROWS, scroll + VIS); r++) {
            for (int c = 0; c < 2; c++) {
                final int rr = r, cc = c;
                Hit h = add(cellX(c), rowY(r), cellW(), RH - 1, null, () -> { selR = rr; selC = cc; startCapture(rr); });
                h.plain = true; h.noSound = true;
            }
        }
        float sx = px + pw - 30;
        Hit up = add(sx, TOP, 22, 20, "^", () -> scrollBy(-1)); up.disabled = scroll <= 0;
        Hit dn = add(sx, TOP + VIS * RH - 20, 22, 20, "v", () -> scrollBy(1)); dn.disabled = scroll >= ROWS - VIS;
        float bw = 110, y = 206, x0 = w / 2f - (3 * bw + 12) / 2f;
        add(x0, y, bw, 20, "Restaurar", this::restore);
        add(x0 + bw + 6, y, bw, 20, dirty() ? "Guardar *" : "Guardar", this::save);
        add(x0 + 2 * (bw + 6), y, bw, 20, "Atrás", this::goBack);
    }

    // ---------------------------------------------------------------- acciones
    private void scrollBy(int d) { scroll = Math.max(0, Math.min(ROWS - VIS, scroll + d)); layout(); }

    private void cycleMode() { Save.S.inputMode = (Save.S.inputMode + 1) % 3; Snd.sfx("ui_click", 0.8f); layout(); }

    private void startCapture(int row) {
        capR = row; capT = 8f;
        Snd.sfx("ui_click", 0.8f);
        layout();
    }

    private void cancelCapture() { capR = -1; layout(); }

    private void assign(int code) {
        int col = Pad.isPad(code) ? 1 : 0;
        int[] arr = col == 0 ? Save.S.kb : Save.S.pb;
        int act = capR;
        if (arr[act] == code) { capR = -1; layout(); return; }
        int other = -1;
        for (int i = 0; i < ROWS; i++) if (i != act && arr[i] == code) other = i;
        if (other >= 0) {
            conflict = true; cfCode = code; cfOther = other; cfCol = col; cfSel = 0;
            layout();
            Snd.sfx("ui_error", 0.6f);
            return;
        }
        arr[act] = code;
        capR = -1;
        toast = Input.NAMES[act] + " > " + (col == 0 ? Pad.keyName(code) : Pad.name(game.padType, code));
        toastT = 2f;
        Snd.sfx("ui_confirm", 0.9f);
        layout();
    }

    /** 0 intercambiar, 1 reemplazar (la otra accion queda sin asignar), 2 cancelar. */
    private void resolve(int how) {
        int[] arr = cfCol == 0 ? Save.S.kb : Save.S.pb;
        int act = capR;
        if (how == 0) { arr[cfOther] = arr[act]; arr[act] = cfCode; }
        else if (how == 1) { arr[cfOther] = 0; arr[act] = cfCode; }
        if (how != 2) {
            toast = Input.NAMES[act] + " > " + (cfCol == 0 ? Pad.keyName(cfCode) : Pad.name(game.padType, cfCode));
            toastT = 2f;
            Snd.sfx("ui_confirm", 0.9f);
        }
        conflict = false; capR = -1;
        layout();
    }

    private void restore() {
        System.arraycopy(Input.defaultKeys(), 0, Save.S.kb, 0, ROWS);
        System.arraycopy(Input.defaultPad(), 0, Save.S.pb, 0, ROWS);
        Save.S.inputMode = 0;
        toast = "Controles restaurados"; toastT = 2f;
        Snd.sfx("ui_confirm", 0.9f);
        layout();
    }

    private void save() {
        Save.S.write();
        System.arraycopy(Save.S.kb, 0, origK, 0, ROWS);
        System.arraycopy(Save.S.pb, 0, origP, 0, ROWS);
        origMode = Save.S.inputMode;
        toast = "Guardado"; toastT = 2f;
        layout();
    }

    private void goBack() {
        if (dirty()) { leaveAsk = true; leaveSel = 0; layout(); return; }
        game.go(new Screens.Options(game, false));
    }

    private void leave(int how) {
        if (how == 2) { leaveAsk = false; layout(); return; }
        if (how == 0) save();
        else {
            System.arraycopy(origK, 0, Save.S.kb, 0, ROWS);
            System.arraycopy(origP, 0, Save.S.pb, 0, ROWS);
            Save.S.inputMode = origMode;
        }
        game.go(new Screens.Options(game, false));
    }

    @Override boolean back() {
        if (capR >= 0 && !conflict) { cancelCapture(); return true; }
        if (conflict) { resolve(2); return true; }
        if (leaveAsk) { leave(2); return true; }
        goBack();
        return true;
    }

    // ---------------------------------------------------------------- entrada de teclado / mando
    @Override void rawKey(int code, boolean down) {
        if (!down) return;
        if (capR >= 0 && !conflict) {
            if (code == 27) { cancelCapture(); return; }
            assign(code);
            return;
        }
        int nk = Pad.isPad(code) ? Pad.menuKey(code) : code;
        if (nk > 0) key(nk, true);
    }

    private static boolean isUp(int c) { return c == 38 || c == 'W'; }
    private static boolean isDn(int c) { return c == 40 || c == 'S'; }
    private static boolean isLt(int c) { return c == 37 || c == 'A'; }
    private static boolean isRt(int c) { return c == 39 || c == 'D'; }
    private static boolean isOk(int c) { return c == 10 || c == 32 || c == 'J'; }

    @Override void key(int code, boolean isDown) {
        if (!isDown) return;
        if (conflict) {
            if (isLt(code)) cfSel = (cfSel + 2) % 3; else if (isRt(code)) cfSel = (cfSel + 1) % 3;
            else if (isOk(code)) resolve(cfSel); else if (code == 27) resolve(2);
            return;
        }
        if (leaveAsk) {
            if (isLt(code)) leaveSel = (leaveSel + 2) % 3; else if (isRt(code)) leaveSel = (leaveSel + 1) % 3;
            else if (isOk(code)) leave(leaveSel); else if (code == 27) leave(2);
            return;
        }
        if (capR >= 0) { if (code == 27) cancelCapture(); return; }
        if (isUp(code)) { selR = Math.max(-1, selR - 1); Snd.sfx("ui_hover", 0.5f); }
        else if (isDn(code)) { selR = Math.min(ROWS, selR + 1); Snd.sfx("ui_hover", 0.5f); if (selR == ROWS) selC = Math.max(0, Math.min(2, selC)); }
        else if (isLt(code)) { if (selR >= 0 && selR < ROWS) selC = 0; else if (selR == ROWS) selC = Math.max(0, selC - 1); Snd.sfx("ui_hover", 0.5f); }
        else if (isRt(code)) { if (selR >= 0 && selR < ROWS) selC = 1; else if (selR == ROWS) selC = Math.min(2, selC + 1); Snd.sfx("ui_hover", 0.5f); }
        else if (isOk(code)) {
            if (selR == -1) cycleMode();
            else if (selR < ROWS) startCapture(selR);
            else { Snd.sfx("ui_click", 0.8f); if (selC == 0) restore(); else if (selC == 1) save(); else goBack(); }
            return;
        }
        else if (code == 27) { goBack(); return; }
        else return;
        if (selR >= 0 && selR < ROWS) {
            if (selR < scroll) scroll = selR;
            else if (selR >= scroll + VIS) scroll = selR - VIS + 1;
        }
        layout();
    }

    // ---------------------------------------------------------------- actualizacion / dibujo
    @Override void update(float dt) {
        t += dt;
        bg.update(dt, W());
        if (toastT > 0) toastT -= dt;
        if (capR >= 0 && !conflict) { capT -= dt; if (capT <= 0) cancelCapture(); }
    }

    private static void frame(Platform.Gfx g, float x, float y, float w, float h, int c) {
        g.rect(x, y, w, 1, c, false); g.rect(x, y + h - 1, w, 1, c, false);
        g.rect(x, y, 1, h, c, false); g.rect(x + w - 1, y, 1, h, c, false);
    }

    @Override void render(Platform.Gfx g) {
        int w = W();
        float pw = pw(), px = px();
        bg.render(g, w, 0.45f);
        UI.panel(g, 0, px, 4, pw, 262, 0.97f);
        UI.big.center(g, "CONTROLES", w / 2f, 8, UI.GOLD, 1f);
        // estado del mando
        String st = game.padConn ? Pad.typeName(game.padType) + " conectado" : "Sin mando detectado";
        UI.small.right(g, st, px + pw - 12, 31, game.padConn ? UI.GREEN : UI.GREY, 1f);
        // cabecera
        UI.small.draw(g, "Acción", px + 14, 50, UI.GREY, 1f);
        UI.small.draw(g, "Teclado", cellX(0) + 4, 50, UI.GREY, 1f);
        UI.small.draw(g, "Mando", cellX(1) + 4, 50, UI.GREY, 1f);
        boolean kbd = game.keyboardUsed;
        // filas
        for (int r = scroll; r < Math.min(ROWS, scroll + VIS); r++) {
            float y = rowY(r);
            if ((r & 1) == 0) g.rect(px + 8, y, pw - 44, RH - 1, 0x22FFFFFF, false);
            UI.small.draw(g, Input.NAMES[r], px + 14, y + 4, UI.WHITE, 1f);
            for (int c = 0; c < 2; c++) {
                float x = cellX(c), cw = cellW();
                boolean sel = kbd && selR == r && selC == c;
                g.rect(x, y, cw, RH - 1, sel ? 0x55FFD25A : 0x33000000, false);
                frame(g, x, y, cw, RH - 1, sel ? 0xFFFFD25A : 0x55808090);
                int code = c == 0 ? Save.S.kb[r] : Save.S.pb[r];
                String txt = c == 0 ? Pad.keyName(code) : (code <= 0 ? "-" : Pad.name(game.padType, code));
                int col = code <= 0 ? UI.GREY : (c == 1 && Pad.faceColor(game.padType, code) != 0 ? 0xFF000000 | Pad.faceColor(game.padType, code) : UI.WHITE);
                UI.small.center(g, txt, x + cw / 2f, y + 4, col, 1f);
            }
        }
        if (scroll > 0) UI.small.center(g, "...", px + pw - 19, TOP + 22, UI.GREY, 1f);
        if (scroll < ROWS - VIS) UI.small.center(g, "...", px + pw - 19, TOP + VIS * RH - 28, UI.GREY, 1f);
        UI.small.center(g, "Toca una casilla o elige con el mando y pulsa " + Pad.name(game.padType, Pad.A) + ". Se aplica al instante.", w / 2f, 232, UI.GREY, 1f);
        UI.small.center(g, "Flechas, Espacio y cruceta siguen activas si no las usas en otra acción.", w / 2f, 243, 0xFF707890, 1f);
        if (toastT > 0) UI.small.center(g, toast, w / 2f, 254, UI.GOLD, Math.min(1f, toastT));
        // seleccion de la fila de modo / botones (con teclado o mando)
        if (!modal()) {
            drawButtons(g);
            if (kbd && selR == -1) { Hit h = hits.get(0); frame(g, h.x - 2, h.y - 2, h.w + 4, h.h + 4, 0xFFFFD25A); }
            if (kbd && selR == ROWS) {
                int bi = hits.size() - 3 + selC;
                Hit h = hits.get(bi); frame(g, h.x - 2, h.y - 2, h.w + 4, h.h + 4, 0xFFFFD25A);
            }
        }
        if (modal()) renderModal(g, w);
    }

    private void renderModal(Platform.Gfx g, int w) {
        g.rect(0, 0, w, ViewSize.h, 0xB0000008, false);
        float bw = Math.min(360, w - 30), bx = w / 2f - bw / 2f;
        UI.panel(g, 1, bx, 70, bw, 130, 1f);
        if (conflict) {
            String n = Input.NAMES[cfOther];
            String k = cfCol == 0 ? Pad.keyName(cfCode) : Pad.name(game.padType, cfCode);
            UI.big.center(g, "CONFLICTO", w / 2f, 78, UI.RED, 1f);
            UI.small.center(g, "«" + k + "» ya lo usa «" + n + "».", w / 2f, 104, UI.WHITE, 1f);
            UI.small.center(g, "Intercambiar: «" + n + "» recibe el botón que tenía «" + Input.NAMES[capR] + "».", w / 2f, 118, UI.GREY, 1f);
            UI.small.center(g, "Reemplazar: «" + n + "» se queda sin asignar.", w / 2f, 130, UI.GREY, 1f);
            drawButtons(g);
            Hit h = hits.get(cfSel); if (kbd()) frame(g, h.x - 2, h.y - 2, h.w + 4, h.h + 4, 0xFFFFD25A);
        } else if (leaveAsk) {
            UI.big.center(g, "¿SALIR?", w / 2f, 78, UI.GOLD, 1f);
            UI.small.center(g, "Hay cambios sin guardar.", w / 2f, 110, UI.WHITE, 1f);
            drawButtons(g);
            Hit h = hits.get(leaveSel); if (kbd()) frame(g, h.x - 2, h.y - 2, h.w + 4, h.h + 4, 0xFFFFD25A);
        } else {
            UI.big.center(g, "REASIGNAR", w / 2f, 78, UI.GOLD, 1f);
            UI.small.center(g, Input.NAMES[capR], w / 2f, 102, UI.WHITE, 1f);
            float a = 0.6f + 0.4f * (float) Math.sin(t * 6);
            UI.small.center(g, "Pulsa una tecla o botón para asignarlo", w / 2f, 122, UI.CYAN, a);
            UI.small.center(g, "Esc o «Cancelar» para salir · " + (int) Math.ceil(capT) + " s", w / 2f, 140, UI.GREY, 1f);
            drawButtons(g);
        }
    }

    private boolean kbd() { return game.keyboardUsed; }
}
