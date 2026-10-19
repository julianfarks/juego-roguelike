package com.julianfarks.roguelike.core;

/**
 * Tutorial inicial de controles.
 * - Estado: UNICA fuente de verdad = Save.S.tutMask (bits por tutorial, persistido en el guardado del perfil).
 * - Panel: se coloca solo, en la franja libre entre vida / pausa / botones, sin pausar el juego.
 */
final class Tutorial {
    static final int CONTROLS = 1, PORTAL = 2, ALL = 3;

    static boolean done(int id) { return (Save.S.tutMask & id) == id; }

    static void complete(int id) {
        if (done(id)) return;
        Save.S.tutMask |= id;
        Save.S.write();
    }

    boolean active;
    float shown;                       // segundos con el panel visible (para el fundido)
    private boolean moved, jumped, attacked, rolled, prevKey;
    private float allT, stepT;
    private int lastShown = -1;
    float bx, by, bw, bh;              // boton "Entendido" (ultimo dibujo)
    float qx, qy, qw, qh;              // rectangulo del panel (ultimo dibujo; lo usan las pruebas)
    static int drawCount;              // paneles dibujados (prueba: exactamente 1 por fotograma)

    void start() { active = true; shown = 0; allT = 0; moved = jumped = attacked = rolled = false; prevKey = true; lastShown = -1; }

    /** Cierra y deja constancia permanente. */
    void close() { if (!active) return; active = false; complete(CONTROLS); }

    int step() { return !moved ? 0 : (!(jumped && attacked) ? 1 : (!rolled ? 2 : -1)); }

    void update(float dt, Input in, boolean visible) {
        if (!active) return;
        if (visible) shown += dt;
        if (!visible) return;
        if (shown > 3f) complete(CONTROLS);          // ya lo ha visto: queda guardado aunque cierre el juego sin pulsar nada
        moved |= in.held(Input.B_LEFT) || in.held(Input.B_RIGHT);
        jumped |= in.pressed(Input.B_JUMP);
        attacked |= in.pressed(Input.B_ATTACK);
        rolled |= in.pressed(Input.B_ROLL);
        boolean k = in.rawDown(10) || (padKeyFree() && in.rawDown(Pad.RS_D));
        if (k && !prevKey && shown > 0.4f) { close(); return; }
        prevKey = k;
        if (step() < 0) { allT += dt; if (allT > 1.6f) close(); }
    }

    private static boolean padKeyFree() { for (int c : Save.S.pb) if (c == Pad.RS_D) return false; return true; }

    boolean hitButton(float x, float y) {
        if (!active || shown < 0.4f) return false;
        return x >= bx - 5 && x <= bx + bw + 5 && y >= by - 5 && y <= by + bh + 5;
    }

    // ------------------------------------------------------------------ dibujo
    private static final String[] TITLE = {"MOVIMIENTO", "ACCIONES", "ESQUIVA"};

    void render(Platform.Gfx g, RunScreen sc, int w) {
        if (!active || shown <= 0.01f) return;
        Input in = sc.in;
        boolean touch = sc.game.touchUiVisible();
        boolean pad = !touch && sc.game.lastDevice == 2;
        float a = Mth.clamp(shown / 0.4f, 0, 1);
        int lh = ArsenalUI.lh();
        String[] text = {
            touch ? "Usa el joystick para moverte." : pad ? "Usa el stick izquierdo para moverte." : "Usa las teclas para moverte.",
            touch || pad ? "Usa los botones para saltar, rodar y atacar." : "Usa las teclas para saltar, rodar y atacar.",
            "Rodar te hace invulnerable durante un instante."};
        // ---- iconos / teclas de cada fila (acciones reales de Input)
        int[][] items = touch ? new int[][]{{-1}, {Input.B_JUMP, Input.B_ROLL, Input.B_ATTACK}, {Input.B_ROLL}}
                : new int[][]{pad ? new int[]{-2} : new int[]{Input.B_LEFT, Input.B_RIGHT}, {Input.B_JUMP, Input.B_ROLL, Input.B_ATTACK}, {Input.B_ROLL}};
        float[] rw = new float[3];
        float iconW = 0;
        for (int r = 0; r < 3; r++) {
            float x = 0;
            for (int it : items[r]) x += itemW(sc, it, touch) + 3;
            rw[r] = x - 3;
            iconW = Math.max(iconW, rw[r]);
        }
        // ---- franja libre: entre la vida (izq.) y los botones / pausa (der.). Se muestra UN paso cada vez (compacto: no tapa la accion)
        float top = 32;
        float left = Math.max(118, 8 + (UI.hpFrame != null ? UI.hpFrame.w : 90) + 10), right = w - 8;
        float pw = 200, ph = 80, rowH = 24;
        int maxLines = 3;
        for (int pass = 0; pass < 2; pass++) {
            if (touch) {                 // evita los botones tactiles visibles (posicion real, incluida la personalizada)
                float bot = top + ph;
                left = Math.max(118, 8 + (UI.hpFrame != null ? UI.hpFrame.w : 90) + 10); right = w - 8;
                for (int i = 0; i < Input.B_COUNT; i++) {
                    Input.Btn b = in.btn[i];
                    if (!b.visible || i == Input.B_LEFT || i == Input.B_RIGHT || i == Input.B_DOWN) continue;
                    if (b.cy - b.r > bot + 2 || b.cy + b.r < top - 2) continue;
                    if (b.cx > w / 2f) right = Math.min(right, b.cx - b.r - 6); else left = Math.max(left, b.cx + b.r + 6);
                }
            }
            pw = Math.min(330, right - left);
            float tw0 = pw - 16 - iconW - 8;
            rowH = 24;
            for (int r = 0; r < 3; r++) rowH = Math.max(rowH, lh * (1 + Math.min(maxLines, UI.small.wrapLines(text[r], (int) tw0))) + 4);
            ph = 6 + rowH + 5 + 17;
        }
        float px = Mth.clamp(w / 2f - pw / 2f, left, Math.max(left, right - pw));
        float py = top;
        float tw = pw - 16 - iconW - 8;
        qx = px; qy = py; qw = pw; qh = ph; drawCount++;
        PrepScreen.fitErr("tutorial ancho", pw, w - 16, 0);
        PrepScreen.fitErr("tutorial alto", py + ph, ViewSize.h * 0.55f, 0);
        PrepScreen.fitErr("tutorial borde", px + pw, w - 4, 0);
        PrepScreen.fitErr("tutorial ancho minimo", 200, pw, 0);
        for (int r = 0; r < 3; r++) PrepScreen.fitErr("tutorial texto " + r, UI.small.wrapLines(text[r], (int) tw), maxLines, 0);

        // ---- panel
        int cur = step();
        int sh = cur >= 0 ? cur : 2;                       // paso mostrado (al terminar queda el ultimo, con su marca)
        boolean fin = cur < 0;
        if (sh != lastShown) { lastShown = sh; stepT = 0; }
        stepT += 1f / 60f;
        float ta = a * Mth.clamp(stepT / 0.25f, 0.2f, 1f);
        float pulse = 0.5f + 0.5f * (float) Math.sin(sc.lv.time * 6f);
        g.rect(px - 1, py - 1, pw + 2, ph + 2, Mth.withAlpha(0x000008, (int) (150 * a)), false);
        UI.panel(g, 0, px, py, pw, ph, 0.94f * a);
        float yy = py + 6;
        float tx = px + 8 + iconW + 8;
        float cy = yy + rowH / 2f - 1;
        float x = px + 8 + (iconW - rw[sh]) / 2f;
        for (int it : items[sh]) { x += drawItem(g, sc, it, touch, x, cy, ta, fin ? 0f : pulse) + 3; }
        UI.small.draw(g, TITLE[sh], tx, yy + 1, fin ? 0xFF8FD98F : UI.GOLD, ta);
        UI.small.drawWrappedMax(g, text[sh], tx, yy + 1 + lh, (int) tw, 0xFFE8E0D0, ta, lh, maxLines);
        if (fin) {                       // marca de hecho (dibujada: no depende de la tipografia)
            float mx = px + pw - 15, my = yy + 3;
            g.line(mx, my + 3, mx + 3, my + 6, 2f, Mth.withAlpha(0x8FD98F, (int) (255 * a)), true);
            g.line(mx + 3, my + 6, mx + 8, my, 2f, Mth.withAlpha(0x8FD98F, (int) (255 * a)), true);
        }
        // ---- pie: progreso (3 pasos) + "Entendido"
        float fy = py + ph - 19;
        for (int i = 0; i < 3; i++) {
            boolean ok = i == 0 ? moved : i == 1 ? (jumped && attacked) : rolled;
            int c = ok ? 0xFFD25A : (i == sh ? 0xE8E0D0 : 0x808088);
            g.rect(px + 8 + i * 10, fy + 5, 8, 5, Mth.withAlpha(c, (int) ((ok || i == sh ? 255 : 150) * a)), false);
        }
        String lab = "Entendido";
        bw = Math.max(64, Math.min(pw * 0.45f, UI.small.width(lab) + 16));
        bh = 15;
        bx = px + pw - bw - 8; by = fy;
        UI.button(g, lab, bx, by, bw, bh, 0, false);
        if (!touch) {
            String kt = pad ? Pad.name(sc.game.padType, Pad.RS_D) : Pad.keyName(10);
            if (!pad || padKeyFree()) {
                float kw = UI.small.width(kt) + 6;
                float kx = bx - kw - 5;
                if (kx > px + 40) { g.rect(kx, by + 2, kw, 11, Mth.withAlpha(0x000010, (int) (176 * a)), false); UI.small.draw(g, kt, kx + 3, by + 4, 0xFFE8E0D0, a); }
            }
        }
        PrepScreen.fitErr("tutorial boton", bx + bw, px + pw, 0);

        // ---- indicacion sobre el control real (solo tactil): aro que late en el boton que toca usar
        if (touch && cur >= 0) {
            float k = 0.5f + 0.5f * (float) Math.sin(sc.lv.time * 7f);
            int col = Mth.withAlpha(0xFFE070, (int) ((120 + 120 * k) * a));
            if (cur == 0) {
                g.circle(in.stickCx(), in.stickCy(), in.stickR() + 2 + 2 * k, col, true);
            } else if (cur == 1) {
                if (!jumped) ring(g, in.btn[Input.B_JUMP], k, col);
                if (!attacked) ring(g, in.btn[Input.B_ATTACK], k, col);
            } else ring(g, in.btn[Input.B_ROLL], k, col);
        }
    }

    private static void ring(Platform.Gfx g, Input.Btn b, float k, int col) {
        if (!b.visible) return;
        g.circle(b.cx, b.cy, b.r + 2 + 2 * k, col, true);
        g.circle(b.cx, b.cy, b.r + 3.5f + 2 * k, Mth.withAlpha(col & 0xFFFFFF, 70), true);
    }

    private float itemW(RunScreen sc, int it, boolean touch) {
        if (touch) return 22;
        return UI.small.width(capText(sc, it)) + 6;
    }

    private String capText(RunScreen sc, int it) { return it == -2 ? "LS" : sc.glyphText(it); }

    /** Dibuja un icono de control (tactil: el mismo boton redondo que en juego; teclado/mando: etiqueta de la tecla). Devuelve su ancho. */
    private float drawItem(Platform.Gfx g, RunScreen sc, int it, boolean touch, float x, float cy, float a, float hl) {
        if (touch) {
            float cx = x + 11;
            UI.roundButton(g, cx, cy, 11, 0, a);
            if (it == -1) { g.circle(cx, cy, 5.5f, Mth.withAlpha(0x1C1C28, (int) (240 * a)), false); g.circle(cx, cy, 5.5f, Mth.withAlpha(0xD8D0C0, (int) (230 * a)), true);
                for (int k = -1; k <= 1; k += 2) { g.rect(cx + k * 8 - 1, cy - 1, 2, 2, Mth.withAlpha(0xFFD25A, (int) (220 * a)), false); } }
            else UI.iconC(g, it == Input.B_JUMP ? "jump" : it == Input.B_ROLL ? "roll" : "attack", cx, cy, 1f, a);
            return 22;
        }
        String t = capText(sc, it);
        float tw = UI.small.width(t);
        g.rect(x, cy - 6, tw + 6, 12, Mth.withAlpha(0x34344A, (int) (235 * a)), false);
        g.rect(x, cy - 6, tw + 6, 12, Mth.withAlpha(0xB8B0A0, (int) (200 * a)), true);
        if (hl > 0) g.rect(x, cy - 6, tw + 6, 12, Mth.withAlpha(0xFFD25A, (int) (70 * hl * a)), true);
        UI.small.draw(g, t, x + 3, cy - 3, sc.glyphColor(it == -2 ? Input.B_LEFT : it), a);
        return tw + 6;
    }
}
