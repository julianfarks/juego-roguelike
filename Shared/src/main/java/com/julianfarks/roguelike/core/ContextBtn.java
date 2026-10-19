package com.julianfarks.roguelike.core;

/**
 * Boton contextual de interaccion (REZAR, ABRIR, COMERCIAR...). Aparece solo dentro del rango de un objeto interactivo,
 * grande y centrado abajo (por encima de los controles inferiores). Se coloca solo: esquiva los botones tactiles visibles,
 * los espacios de arma y al personaje. En PC muestra la tecla asignada; con mando, su boton; en Android se toca.
 * Usa la accion que el objeto ya tiene (RunScreen.interact): no inventa acciones ni cambia costes ni condiciones.
 */
final class ContextBtn {
    static final float H = 30;

    Prop cur;
    float t;                       // segundos desde que entro en rango (animacion de aparicion)
    float cd;                      // anti doble pulsacion
    float x, y, w, h;              // rectangulo del ultimo dibujo (area de toque)
    boolean vis;
    private String lastLab = "", up = "";

    void update(float dt, Prop near) {
        if (near != cur) { cur = near; t = 0; vis = near != null && vis; }
        else if (near != null) t += dt;
        if (near == null) vis = false;
        if (cd > 0) cd -= dt;
    }

    boolean hit(float px, float py) {
        return vis && cur != null && t > 0.12f && cd <= 0 && px >= x - 4 && px <= x + w + 4 && py >= y - 4 && py <= y + h + 4;
    }

    static String iconFor(Prop p) {
        switch (p.kind) {
            case "altar": return "altar";
            case "chest": return "chest";
            case "merchant": return "shop";
            case "door": return "door";
            case "portal": return "map";
            case "forge": return "forge";
            case "fountain": return "fountain";
            case "spirit": return "soul";
            case "shrine": return "crown";
            case "cursed": return "curse";
            case "cage": return "lock";
            case "relic": return "relic";
            case "npc": return "heart";
            case "weapon": return p.arg > 0 && p.arg < Items.SEC_COUNT ? Items.SEC_ICON[p.arg] : "attack";
            default: return "key";
        }
    }

    /** Franja libre a la altura [top, top+H]: limitada por los botones tactiles visibles y el joystick. {izq, der} */
    private float[] band(RunScreen sc, int w, float top, boolean touch) {
        float left = 8, right = w - 8;
        if (!touch) return new float[]{left, right};
        Input in = sc.in;
        for (int i = 0; i < Input.B_COUNT; i++) {
            Input.Btn b = in.btn[i];
            if (!b.visible || i == Input.B_INTERACT) continue;
            if (b.cy + b.r < top - 2 || b.cy - b.r > top + H + 2) continue;
            if (b.cx > w / 2f) right = Math.min(right, b.cx - b.r - 6); else left = Math.max(left, b.cx + b.r + 6);
        }
        if (in.stickActive()) {
            float ax = in.anchorX(), ay = in.anchorY(), R = in.stickR() + 6;
            if (ay + R >= top - 2 && ay - R <= top + H + 2) { if (ax > w / 2f) right = Math.min(right, ax - R); else left = Math.max(left, ax + R); }
        }
        return new float[]{left, right};
    }

    void render(Platform.Gfx g, RunScreen sc, int w) {
        if (cur == null) { vis = false; return; }
        Level lv = sc.lv;
        boolean touch = sc.game.touchUiVisible();
        String lab = sc.hintFor(cur);
        if (!lab.equals(lastLab)) { lastLab = lab; up = I18n.tr(lab).toUpperCase(java.util.Locale.ROOT); I18n.pin(up); }
        String icon = iconFor(cur);
        String cap = touch ? null : sc.glyphText(Input.B_INTERACT);
        float capW = cap == null ? 0 : UI.small.width(cap) + 8;
        float tw = UI.big.width(up);
        float want = 10 + 22 + 6 + (cap == null ? 0 : capW + 6) + tw + (touch ? 22 : 12);
        float H0 = ViewSize.h;
        // jugador en pantalla (pies y cabeza)
        float z = lv.camZoom;
        float psx = (lv.pl.x - lv.camX) * z + (1 - z) * w / 2f, psy = (lv.pl.y - lv.camY) * z + (1 - z) * H0 / 2f;
        float pl = psx - 18, pr = psx + 18, pt = psy - lv.pl.bh - 8, pb = psy + 3;
        float slotTop = H0 - 17 - 14 - (touch ? 3 : 14);
        // candidatas: debajo de los pies (suelo), zona inferior habitual, encima de la cabeza
        float[] cand = {psy + 8, H0 - 17 - 14 - (touch ? 3 : 14) - 6 - H, pt - H - 4};
        float bx = 0, by = 0, bw = 0; boolean ok = false;
        for (int k = 0; k < cand.length && !ok; k++) {
            float cy = cand[k];
            if (cy < 44 || cy + H > slotTop - 2 + (k == 2 ? 80 : 0)) continue;
            if (k < 2 && cy + H > slotTop - 2) continue;
            float[] bd = band(sc, w, cy, touch);
            float ww = Math.min(want, bd[1] - bd[0]);
            if (ww < Math.min(want, 118)) continue;
            float xx = Mth.clamp(w / 2f - ww / 2f, bd[0], bd[1] - ww);
            boolean hitPl = xx < pr && xx + ww > pl && cy < pb && cy + H > pt;
            if (hitPl) continue;
            bx = xx; by = cy; bw = ww; ok = true;
        }
        if (!ok) {   // sin hueco ideal: zona inferior habitual, recortada a la franja libre
            float cy = Math.max(44, cand[1]);
            float[] bd = band(sc, w, cy, touch);
            bw = Math.max(100, Math.min(want, bd[1] - bd[0]));
            bx = Mth.clamp(w / 2f - bw / 2f, 4, w - 4 - bw); by = cy;
        }
        // aparicion: sube y se aclara
        float e = Mth.clamp(t / 0.22f, 0, 1); e = 1f - (1f - e) * (1f - e);
        float a = e, oy = (1f - e) * 8f;
        x = bx; y = by; this.w = bw; h = H; vis = true;
        float pulse = 0.5f + 0.5f * (float) Math.sin(lv.time * 5f);
        PrepScreen.fitErr("boton contextual ancho", bw, w - 8, 0);
        PrepScreen.fitErr("boton contextual texto", 10 + 22 + 6 + (cap == null ? 0 : capW + 6) + tw + 6, bw, 0);
        float yy = by + oy;
        g.rect(bx - 1, yy - 1, bw + 2, H + 2, Mth.withAlpha(0x000008, (int) (150 * a)), false);
        UI.panel(g, 1, bx, yy, bw, H, 0.96f * a);
        g.rect(bx + 2, yy + 2, bw - 4, H - 4, Mth.withAlpha(0xFFD25A, (int) ((22 + 30 * pulse) * a)), true);     // borde que late: se puede pulsar
        float ix = bx + 8;
        if (cap != null) {          // PC / mando: la tecla o boton realmente asignado
            g.rect(ix, yy + H / 2f - 7, capW, 14, Mth.withAlpha(0x34344A, (int) (240 * a)), false);
            g.rect(ix, yy + H / 2f - 7, capW, 14, Mth.withAlpha(0xFFD25A, (int) (220 * a)), true);
            UI.small.center(g, cap, ix + capW / 2f, yy + H / 2f - 4, sc.glyphColor(Input.B_INTERACT), a);
            ix += capW + 6;
        }
        UI.roundButton(g, ix + 11, yy + H / 2f, 11, 0, a);
        UI.iconC(g, icon, ix + 11, yy + H / 2f, 1f, a);
        g.circle(ix + 11, yy + H / 2f, 12 + 2 * pulse, Mth.withAlpha(0xFFE070, (int) (120 * (1 - pulse) * a)), true);
        ix += 28;
        UI.big.drawCenterRaw(g, up, ix + (bx + bw - (touch ? 20 : 10) - ix) / 2f, yy + H / 2f - UI.big.ch / 2f, 0xFFFFF0D0, a);
        if (touch) {                // indicador de toque: flecha que se desplaza
            float ax = bx + bw - 14 + 2 * (float) Math.sin(lv.time * 7f), ay = yy + H / 2f;
            int c = Mth.withAlpha(0xFFE070, (int) (255 * a));
            g.line(ax - 2, ay - 4, ax + 2, ay, 2f, c, true);
            g.line(ax + 2, ay, ax - 2, ay + 4, 2f, c, true);
        }
    }
}
