package com.julianfarks.roguelike.core;

import java.util.List;

/** Dibujo del arsenal: ranuras de arma en el HUD, tarjeta de arma del suelo y fichas con comparacion (se reutilizan en cofres e inventario). */
final class ArsenalUI {
    private ArsenalUI() {}

    static final int OK = 0xFF5AD070, BAD = 0xFFFF6A5A, EQ = 0xFFB8B8C0;

    /** Alto de linea de texto pequeño: el chino necesita mas que el alfabeto latino. */
    static int lh() { return I18n.lang() == I18n.ZH ? 13 : 9; }

    static int rarCol(int rar) { return ChestLoot.R_COL[Math.max(0, Math.min(3, rar))]; }

    /** Marca de comparacion que no depende solo del color: "+" mejor, "-" peor, "=" igual. */
    static void cmpMark(Platform.Gfx g, float x, float y, int cmp) {
        if (cmp == 2) return;
        String m = cmp > 0 ? "+" : cmp < 0 ? "-" : "=";
        UI.small.draw(g, m, x, y, cmp > 0 ? OK : cmp < 0 ? BAD : EQ, 1f);
    }

    /** Una ficha de arma dentro de (x,y,w): cabecera con icono/nombre/rareza, estadisticas (comparadas con `vs` si > 0), efecto y estilo. Devuelve la y final. */
    static float sheet(Platform.Gfx g, float x, float y, float w, int id, int vs, int ammo) {
        int rar = Items.SEC_RAR[id];
        int rc = rarCol(rar);
        UI.iconC(g, Items.SEC_ICON[id], x + 9, y + 9, 1f, 1f);
        String nm = UI.fitLabel(UI.small, Items.SEC_NAME[id], w - 40);
        UI.small.draw(g, nm, x + 22, y + 1, 0xFFF0E8E0, 1f);
        Arsenal.rarityMark(g, x + 26, y + 15, rar, rc & 0xFFFFFF);
        UI.small.draw(g, ChestLoot.R_NAME[rar], x + 34, y + 11, rc, 1f);
        float yy = y + 22;
        List<Arsenal.Line> ls = Arsenal.lines(id, vs);
        for (Arsenal.Line l : ls) {
            UI.small.draw(g, l.label, x + 2, yy, 0xFFB8B0B8, 1f);
            UI.small.right(g, l.val, x + w - 12, yy, 0xFFF0E8E0, 1f);
            cmpMark(g, x + w - 8, yy, l.cmp);
            yy += lh() + 1;
        }
        yy += 2;
        yy += UI.small.drawWrapped(g, "Efecto: " + Items.SEC_FX[id], x + 2, yy, (int) w - 4, 0xFFFFD25A, 1f, lh()) + 2;
        yy += UI.small.drawWrapped(g, Items.SEC_STYLE[id], x + 2, yy, (int) w - 4, 0xFFC8C0C8, 1f, lh() + 1);
        return yy;
    }

    /** Ranuras de arma en el HUD (arma principal y secundaria, con la activa resaltada y la municion). */
    /** Espacios de seleccion directa de arma. Se dibujan en la posicion de los botones B_WMAIN / B_WSEC (la misma zona que recibe el toque). */
    static void slots(Platform.Gfx g, Level lv, RunState rs, ClassDef cls, int w, Input in, String[] keyHint) {
        Player pl = lv.pl;
        boolean sec = rs.sec != 0;
        for (int k = 0; k < 2; k++) {
            boolean act = k == 0 ? !rs.secActive : rs.secActive;
            Input.Btn sb = in.btn[k == 0 ? Input.B_WMAIN : Input.B_WSEC];
            float sx = sb.cx, cy = sb.cy;
            float sk = sb.r / 17f;
            float pulse = pl.swapAnimT > 0 ? 1f + 0.18f * (pl.swapAnimT / 0.32f) : 1f;
            float r = (act ? 14f : 11.5f) * sk * (act ? pulse : 1f);
            if (k == 1 && !sec) { UI.roundButton(g, sx, cy, 10 * sk, 0, 0.3f); if (keyHint != null) hint(g, keyHint[k], sx, cy, 10 * sk); continue; }
            int col = k == 0 ? (cls.color1 & 0xFFFFFF) : Items.SEC_COL[rs.sec];
            UI.roundButton(g, sx, cy, r, act ? 1 : 0, act ? 0.92f : 0.55f);
            g.circle(sx, cy, r - 1, Mth.withAlpha(col, act ? 90 : 40), false);
            UI.iconC(g, k == 0 ? "c_" + cls.key : Items.SEC_ICON[rs.sec], sx, cy - 1, 1f, act ? 1f : 0.55f);
            if (act) g.rect(Math.round(sx - 8), Math.round(cy + r + 2), 16, 2, 0xFFFFE070, false);
            if (keyHint != null) hint(g, keyHint[k], sx, cy, r);    // barra dorada: arma activa (no depende solo del color: ademas es mayor y mas opaca)
            if (k == 1) {
                String n = String.valueOf(rs.secAmmo);
                g.rect(sx - UI.small.width(n) / 2f - 1, cy + r - 4, UI.small.width(n) + 2, 9, 0x99000010, false);
                UI.small.center(g, n, sx, cy + r - 3, rs.secAmmo > 0 ? UI.WHITE : UI.RED, act ? 1f : 0.7f);
            }
        }
    }

    /** Etiqueta de la tecla / boton de mando asignado, pegada sobre el espacio del arma (solo PC y mando). */
    private static void hint(Platform.Gfx g, String t, float sx, float cy, float r) {
        if (t == null || t.isEmpty() || t.equals("-")) return;
        float tw = UI.small.width(t);
        g.rect(sx - tw / 2f - 3, cy - r - 12, tw + 6, 10, 0xB0000010, false);
        UI.small.center(g, t, sx, cy - r - 11, 0xFFE8E0D0, 1f);
    }

    /** Tarjeta contextual del arma del suelo: nombre, rareza, estadisticas (comparadas con la equipada), efecto y la accion disponible. Compacta para no tapar el combate. */
    static void groundCard(Platform.Gfx g, Level lv, RunState rs, Prop p, int w, String actionLabel) {
        int id = p.arg;
        if (id <= 0 || id >= Items.SEC_COUNT) return;
        float cw = Math.min(252, w - 16);
        String fxs = "Efecto: " + Items.SEC_FX[id];
        int fxl = Math.min(2, UI.small.wrapLines(fxs, (int) cw - 16));
        boolean cmp = rs.sec != 0 && rs.sec != id;
        int L = lh();
        float ch = 6 + 20 + 2 * (L + 1) + 3 + fxl * L + 4 + (cmp ? L + 1 : 0) + L + 6;
        float x = w / 2f - cw / 2f, y = 36;
        UI.panel(g, 0, x, y, cw, ch, 0.94f);
        float ix = x + 8, yy = y + 6;
        int rar = Items.SEC_RAR[id], rc = rarCol(rar);
        UI.iconC(g, Items.SEC_ICON[id], ix + 9, yy + 9, 1f, 1f);
        UI.small.draw(g, UI.fitLabel(UI.small, Items.SEC_NAME[id], cw - 40), ix + 22, yy + 1, 0xFFF0E8E0, 1f);
        Arsenal.rarityMark(g, ix + 26, yy + 15, rar, rc & 0xFFFFFF);
        UI.small.draw(g, ChestLoot.R_NAME[rar] + " · " + (p.wAmmo > 0 ? p.wAmmo : Items.SEC_AMMO[id]) + " usos", ix + 34, yy + 11, rc, 1f);
        yy += 24;
        List<Arsenal.Line> ls = Arsenal.lines(id, rs.sec);
        float colW = (cw - 22) / 2f;
        for (int i = 0; i < ls.size() && i < 5; i++) {
            if (i == 3) { /* Municion ya va en la cabecera */ continue; }
            int k = i > 3 ? 3 : i;
            float cx = ix + (k % 2) * (colW + 6), cy = yy + (k / 2) * (L + 1);
            Arsenal.Line l = ls.get(i);
            String v = l.val.replace(" casillas", " cas.");
            UI.small.draw(g, l.label, cx, cy, 0xFFB8B0B8, 1f);
            UI.small.right(g, v, cx + colW - 12, cy, 0xFFF0E8E0, 1f);
            cmpMark(g, cx + colW - 9, cy, l.cmp);
        }
        yy += 2 * (L + 1) + 3;
        UI.small.drawWrappedMax(g, fxs, ix, yy, (int) cw - 16, 0xFFFFD25A, 1f, L, 2);
        yy += fxl * L + 3;
        if (cmp) { UI.small.center(g, "+ mejor · - peor que tu arma actual", x + cw / 2f, yy, 0xFF9890A0, 1f); yy += L + 1; }
        String foot = rs.sec == 0 ? actionLabel + " y equipar" : rs.sec == id ? actionLabel + " (misma arma: sube de nivel)" : actionLabel + " por " + Items.SEC_NAME[rs.sec];
        UI.small.center(g, UI.fitLabel(UI.small, foot, cw - 12), x + cw / 2f, yy + 2, UI.GOLD, 1f);
    }
}
