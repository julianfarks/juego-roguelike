package com.julianfarks.roguelike.core;

import java.util.List;

/** Dibujo del arsenal: ranuras de arma en el HUD, tarjeta de arma del suelo y fichas con comparacion (se reutilizan en cofres e inventario). */
final class ArsenalUI {
    private ArsenalUI() {}

    static final int OK = 0xFF5AD070, BAD = 0xFFFF6A5A, EQ = 0xFFB8B8C0;

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
            yy += 10;
        }
        yy += 2;
        UI.small.draw(g, "Efecto: " + Items.SEC_FX[id], x + 2, yy, 0xFFFFD25A, 1f);
        yy += 11;
        yy += UI.small.drawWrapped(g, Items.SEC_STYLE[id], x + 2, yy, (int) w - 4, 0xFFC8C0C8, 1f);
        return yy;
    }

    /** Ranuras de arma en el HUD (arma principal y secundaria, con la activa resaltada y la municion). */
    static void slots(Platform.Gfx g, Level lv, RunState rs, ClassDef cls, int w) {
        Player pl = lv.pl;
        float cx = w / 2f, cy = ViewSize.h - 17;
        boolean sec = rs.sec != 0;
        for (int k = 0; k < 2; k++) {
            boolean act = k == 0 ? !rs.secActive : rs.secActive;
            float sx = cx + (k == 0 ? -16 : 16);
            float pulse = pl.swapAnimT > 0 ? 1f + 0.18f * (pl.swapAnimT / 0.32f) : 1f;
            float r = (act ? 12f : 10f) * (act ? pulse : 1f);
            if (k == 1 && !sec) { UI.roundButton(g, sx, cy, 9, 0, 0.3f); continue; }
            int col = k == 0 ? (cls.color1 & 0xFFFFFF) : Items.SEC_COL[rs.sec];
            UI.roundButton(g, sx, cy, r, act ? 1 : 0, act ? 0.92f : 0.55f);
            g.circle(sx, cy, r - 1, Mth.withAlpha(col, act ? 90 : 40), false);
            UI.iconC(g, k == 0 ? "c_" + cls.key : Items.SEC_ICON[rs.sec], sx, cy - 1, 1f, act ? 1f : 0.55f);
            if (act) g.rect(Math.round(sx - 7), Math.round(cy + r + 2), 14, 2, 0xFFFFE070, false);    // barra dorada: arma activa (no depende solo del color: ademas es mayor y mas opaca)
            if (k == 1) {
                String n = String.valueOf(rs.secAmmo);
                g.rect(sx - UI.small.width(n) / 2f - 1, cy + r - 4, UI.small.width(n) + 2, 9, 0x99000010, false);
                UI.small.center(g, n, sx, cy + r - 3, rs.secAmmo > 0 ? UI.WHITE : UI.RED, act ? 1f : 0.7f);
            }
        }
    }

    /** Tarjeta contextual del arma del suelo: nombre, rareza, estadisticas comparadas con la equipada, efecto y estilo, y la accion disponible. */
    static void groundCard(Platform.Gfx g, Level lv, RunState rs, Prop p, int w, String actionLabel) {
        int id = p.arg;
        if (id <= 0 || id >= Items.SEC_COUNT) return;
        float cw = 196, ch = 126;
        float x = w / 2f - cw / 2f, y = 30;
        UI.panel(g, 0, x, y, cw, ch, 0.94f);
        float yy = sheet(g, x + 8, y + 7, cw - 16, id, rs.sec, p.wAmmo > 0 ? p.wAmmo : Items.SEC_AMMO[id]);
        String foot;
        if (rs.sec == 0) foot = "Recoger y equipar";
        else if (rs.sec == id) foot = "Misma arma: mejora de nivel";
        else foot = "Intercambiar con " + Items.SEC_NAME[rs.sec];
        UI.small.center(g, UI.fitLabel(UI.small, actionLabel + " · " + foot, cw - 12), x + cw / 2f, y + ch - 12, UI.GOLD, 1f);
        if (rs.sec != 0 && rs.sec != id) UI.small.center(g, "(+ mejor, - peor que tu arma actual)", x + cw / 2f, y + ch - 22, 0xFF9890A0, 1f);
    }
}
