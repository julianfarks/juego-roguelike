package com.julianfarks.roguelike.core;

import java.util.List;

/**
 * Pruebas de la actualizacion de interfaz (solo banco headless; BOT_UISCENE=1 desde DebugBot): seleccion directa de armas,
 * controles tactiles sin solapes, menu de pausa y boton contextual de interaccion. Usa el motor real. NO es un Android ni un Windows real.
 */
final class UiProbe {
    private UiProbe() {}
    static int fails, oks, start = -1;
    static void ck(String n, boolean ok) { System.out.println("AT " + (ok ? "OK    " : "FALLA ") + n); if (ok) oks++; else fails++; }

    static final String[] KINDS = {"altar", "merchant", "fountain", "forge", "door", "weapon", "chest"};
    static final String[] LABEL = {"Rezar", "Comerciar", "Beber", "Forjar", "Entrar", "Recoger", "Abrir"};
    static Prop prop;
    static int ammo0;

    static boolean circleRect(float cx, float cy, float r, float x, float y, float w, float h) {
        float qx = Math.max(x, Math.min(cx, x + w)), qy = Math.max(y, Math.min(cy, y + h));
        return (cx - qx) * (cx - qx) + (cy - qy) * (cy - qy) < r * r;
    }

    static void touch(RunScreen sc, float x, float y) { sc.touch(0, Platform.ACTION_DOWN, x, y); }
    static void release(RunScreen sc, float x, float y) { sc.touch(0, Platform.ACTION_UP, x, y); }

    static void scene(Game g, RunScreen sc, Level lv, Player p, int frame) {
        if (start < 0) {
            start = frame;
            for (int c : new int[]{'A', 'D', 'W', 'S', 37, 38, 39, 40, 'J', 'K', 'R', 'T', 'E', 32}) g.key(c, false);
            sc.rs.sec = Items.SEC_BOW; sc.rs.secAmmo = 12; sc.rs.wState[Items.SEC_BOW] = 1; sc.rs.secActive = false; sc.rs.gren = 1; sc.rs.grenCount = 3;
            lv.enemies.clear(); lv.toKill = 0; lv.cleared = true; p.invuln = 999;
            p.state = Player.IDLE; p.animName = "idle"; p.animT = 0; p.vx = 0; lv.projs.clear();
            System.out.println("AT escena ui frame=" + frame + " ancho=" + sc.W() + " alto=" + ViewSize.h + " touchUi=" + g.touchUiVisible());
            return;
        }
        int f = frame - start;
        Input in = sc.in;
        RunState rs = sc.rs;
        boolean touchUi = g.touchUiVisible();
        // ------------------------------------------------ A. controles y seleccion directa
        if (f == 3 && touchUi) {
            boolean swapIcon = false; for (Input.Btn b : in.btn) if ("swap".equals(b.icon)) swapIcon = true;
            ck("1 ningun boton con el icono celeste de cambio de arma", !swapIcon);
            ck("1b el boton de disparo secundario y el de interaccion pequeno ya no se muestran", !in.btn[Input.B_SEC].visible && !in.btn[Input.B_INTERACT].visible);
            ck("1c espacios de arma principal y secundaria visibles", in.btn[Input.B_WMAIN].visible && in.btn[Input.B_WSEC].visible);
            String bad = "";
            for (int i = 0; i < Input.B_COUNT; i++) for (int j = i + 1; j < Input.B_COUNT; j++) {
                Input.Btn a = in.btn[i], b = in.btn[j];
                if (!a.visible || !b.visible) continue;
                if (Mth.dist(a.cx, a.cy, b.cx, b.cy) < a.r + b.r) bad += " " + Input.NAMES[i] + "/" + Input.NAMES[j];
            }
            ck("11 sin solapes entre botones tactiles visibles (" + sc.W() + "x" + ViewSize.h + ")" + (bad.isEmpty() ? "" : ":" + bad), bad.isEmpty());
            String small = "";
            for (int i = 0; i < Input.B_COUNT; i++) if (in.btn[i].visible && in.btn[i].r < 11 && i != Input.B_INV) small += " " + Input.NAMES[i];
            ck("botones con tamano tactil razonable (r>=11)" + small, small.isEmpty());
        }
        if (f < 22 && System.getenv("UI_DBG") != null) System.out.println("DBG f=" + f + " st=" + p.state + " anim=" + p.animName + " projs=" + lv.projs.size() + " ammo=" + rs.secAmmo + " sec=" + rs.secActive);
        if (f == 5) { Input.Btn b = in.btn[Input.B_WSEC]; touch(sc, b.cx, b.cy); }
        if (f == 7) { Input.Btn b = in.btn[Input.B_WSEC]; release(sc, b.cx, b.cy); }
        if (f == 20) {
            ck("2 tocar el espacio de la secundaria la selecciona" + (touchUi ? "" : " (clic)") + " [ov=" + sc.ov + " cin=" + lv.cinematic + " fade=" + sc.fadeMode + " alive=" + p.alive + " st=" + p.state + " swapCd=" + p.swapCd + " sel=" + p.selWant + " buf=" + p.swapBuf + " tut=" + Tutorial.done(Tutorial.CONTROLS) + "]", rs.secActive);
            ck("2b seleccionar no dispara ni gasta municion [ammo=" + rs.secAmmo + " projs=" + lv.projs.size() + " own=" + !noOwnShots(lv) + " st=" + p.state + " anim=" + p.animName + "]", rs.secAmmo == 12);
        }
        if (f == 22) { Input.Btn b = in.btn[Input.B_WMAIN]; touch(sc, b.cx, b.cy); }
        if (f == 24) { Input.Btn b = in.btn[Input.B_WMAIN]; release(sc, b.cx, b.cy); }
        if (f == 40) ck("2c tocar el espacio de la principal la selecciona", !rs.secActive && rs.secAmmo == 12);
        if (f == 41) { Input.Btn b = in.btn[Input.B_WMAIN]; touch(sc, b.cx, b.cy); }
        if (f == 43) { Input.Btn b = in.btn[Input.B_WMAIN]; release(sc, b.cx, b.cy); }
        if (f == 50) ck("2d volver a tocar la ya seleccionada no reinicia animacion ni ataca", !rs.secActive && p.swapAnimT <= 0 && p.swapCd <= 0 && rs.secAmmo == 12 && p.state != Player.ATK);
        if (f == 51) { Input.Btn b = in.btn[Input.B_WSEC]; touch(sc, b.cx, b.cy); }
        if (f == 53) { Input.Btn b = in.btn[Input.B_WSEC]; release(sc, b.cx, b.cy); }
        if (f == 70) { ammo0 = rs.secAmmo; ck("3a secundaria seleccionada de nuevo", rs.secActive); }
        if (f == 71) { if (touchUi) { Input.Btn b = in.btn[Input.B_ATTACK]; touch(sc, b.cx, b.cy); } else g.key('J', true); }
        if (f == 76) { if (touchUi) { Input.Btn b = in.btn[Input.B_ATTACK]; release(sc, b.cx, b.cy); } else g.key('J', false); }
        if (f == 90) ck("3 el boton de ataque ejecuta el arma seleccionada (secundaria: municion " + ammo0 + " -> " + rs.secAmmo + ")", rs.secAmmo < ammo0 && rs.secActive);
        if (f == 92) { rs.secActive = false; }
        // ------------------------------------------------ B. pausa
        if (f == 100) sc.debugOpenPause();
        if (f == 112) {
            boolean red = false; String names = "";
            for (Screen.Hit h : sc.hits) { String l = h.label == null ? "" : h.label; names += "[" + l + "]"; if (l.contains("Inventario") || l.contains("Bendiciones")) red = true; }
            ck("6 la pausa ya no tiene Inventario ni 'Bendiciones y sinergias' " + names, !red && sc.hits.size() >= 6);
            String ov = ""; float px = sc.W() / 2f - 220;
            for (int i = 0; i < sc.hits.size(); i++) {
                Screen.Hit a = sc.hits.get(i);
                if (a.x < px || a.x + a.w > px + 440 || a.y < 14 || a.y + a.h > 252) ov += " fuera:" + a.label;
                for (int j = i + 1; j < sc.hits.size(); j++) { Screen.Hit b = sc.hits.get(j); if (a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) ov += " solape:" + a.label + "/" + b.label; }
            }
            ck("6b botones de la pausa alineados, dentro del panel y sin solaparse" + ov, ov.isEmpty());
            float x0 = sc.hits.get(0).x; boolean al = true; for (Screen.Hit h : sc.hits) if (Math.abs(h.x - x0) > 0.5f) al = false;
            ck("6c botones de la pausa en una sola columna alineada", al);
        }
        if (f == 125) {
            boolean bad = false;
            for (String s : PrepScreen.fitErrors) if (s.contains("pausa") || s.contains("boton contextual") || s.contains("tutorial")) { System.out.println("AT ENCAJE " + s); bad = true; }
            ck("6d textos de la pausa sin cortes (" + I18n.code() + ")", !bad);
        }
        if (f == 130) sc.closeOv();
        // ------------------------------------------------ C. boton contextual (un bloque de 80 fotogramas por objeto)
        int c0 = 160;
        if (f >= c0 && f < c0 + 80 * KINDS.length) {
            int k = (f - c0) / 80, sub = (f - c0) % 80;
            String kind = KINDS[k];
            if (sub == 0) {
                closeAll(sc); lv.props.clear(); lv.pickups.clear(); lv.enemies.clear(); p.x = lv.room.spawnX + 40; p.y = lv.room.spawnY; p.vx = 0; p.vy = 0; p.invuln = 999; p.safeX = p.x; p.safeY = p.y;
                Room.PropSpec ps = new Room.PropSpec(kind, p.x + 6, p.y, kind.equals("weapon") ? Items.SEC_CHAKRAM : 0);
                prop = lv.addProp(ps);
                if (kind.equals("door")) { prop.nextType = Room.COMBAT; prop.locked = false; }
                if (kind.equals("weapon")) { prop.wAmmo = Items.SEC_AMMO[Items.SEC_CHAKRAM]; rs.sec = 0; rs.secActive = false; }
            }
            if (sub == 25) {
                ck("8/10 " + kind + ": aparece el boton contextual '" + LABEL[k].toUpperCase() + "' al estar en rango (near=" + (lv.nearestInteractable() == null ? "null" : lv.nearestInteractable().kind) + " cur=" + (sc.ctx.cur == null ? "null" : sc.ctx.cur.kind) + " vis=" + sc.ctx.vis + " ov=" + sc.ov + " px=" + (int) p.x + " py=" + (int) p.y + " prop=" + (int) prop.x + "," + (int) prop.y + ")", lv.nearestInteractable() == prop && sc.ctx.cur == prop && sc.ctx.vis && sc.hintFor(prop).equals(LABEL[k]));
            }
            if (sub == 30) geometry(sc, lv, p, kind);
            if (sub == 40) { g.key('J', true); g.key('K', true); }
            if (sub == 44) { g.key('J', false); g.key('K', false); }
            if (sub == 46) { p.x = prop.x - 6; p.y = prop.y; p.vx = 0; p.vy = 0; }
            if (sub == 50) ck("13 " + kind + ": atacar/esquivar cerca no activa la interaccion", sc.ov == RunScreen.OV_NONE && !prop.used && !prop.dead && rs.sec == 0 || !kind.equals("weapon") && sc.ov == RunScreen.OV_NONE && !prop.used);
            if (sub == 52 && !kind.equals("door")) {
                ctxTap(sc);
            }
            if (sub == 54 && !kind.equals("door")) {
                boolean done;
                switch (kind) {
                    case "altar": done = sc.ov == RunScreen.OV_BLESS; break;
                    case "chest": done = prop.used || prop.open || sc.ov != RunScreen.OV_NONE; break;
                    case "merchant": done = sc.ov == RunScreen.OV_SHOP; break;
                    case "fountain": done = prop.used; break;
                    case "forge": done = sc.ov == RunScreen.OV_FORGE; break;
                    default: done = rs.sec == Items.SEC_CHAKRAM; break;
                }
                ck("8 " + kind + ": tocar el boton contextual ejecuta la accion del objeto (ov=" + sc.ov + " used=" + prop.used + " dead=" + prop.dead + " cd=" + sc.ctx.cd + " vis=" + sc.ctx.vis + ")", done);
                ck("13 " + kind + ": una pulsacion = una sola interaccion (enfriamiento activo)", sc.ctx.cd > 0);
            }
            if (sub == 60) closeAll(sc);
            if (sub == 62) { p.safeX = p.x; p.safeY = p.y; float r = Math.min(lv.room.pixW - 40, prop.x + 260), l = Math.max(40, prop.x - 260); p.x = Math.abs(r - prop.x) >= Math.abs(prop.x - l) ? r : l; p.vx = 0; p.safeX = p.x; p.safeY = p.y; }
            if (sub == 78) ck("9 " + kind + ": al alejarse el boton desaparece [px=" + (int) p.x + " prop=" + (int) prop.x + " pw=" + lv.room.pixW + " cur=" + (sc.ctx.cur == null ? "null" : sc.ctx.cur.kind) + " ov=" + sc.ov + "]", !sc.ctx.vis && sc.ctx.cur == null);
        }
        if (f == c0 + 80 * KINDS.length + 2) {
            boolean bad = false;
            for (String s : PrepScreen.fitErrors) if (s.contains("boton contextual")) { System.out.println("AT ENCAJE " + s); bad = true; }
            ck("14 boton contextual sin errores de encaje (" + I18n.code() + ", " + sc.W() + "x" + ViewSize.h + ")", !bad);
            System.out.println("AT FIN ok=" + oks + " fallos=" + fails);
            System.exit(fails == 0 ? 0 : 1);
        }
    }

    static void closeAll(RunScreen sc) { sc.closeOv(); if (sc.ov != RunScreen.OV_NONE) { sc.ov = RunScreen.OV_NONE; sc.hits.clear(); sc.in.reset(); } }

    static void ctxTap(RunScreen sc) {
        ContextBtn c = sc.ctx;
        if (touchUi(sc)) { touch(sc, c.x + c.w / 2f, c.y + c.h / 2f); release(sc, c.x + c.w / 2f, c.y + c.h / 2f); }
        else { touch(sc, c.x + c.w / 2f, c.y + c.h / 2f); release(sc, c.x + c.w / 2f, c.y + c.h / 2f); }
    }
    static boolean noOwnShots(Level lv) { for (Proj q : lv.projs) if (q.friendly && !q.dead) return false; return true; }
    static boolean touchUi(RunScreen sc) { return sc.game.touchUiVisible(); }

    /** El boton debe estar dentro de la pantalla, abajo/centro, sin pisar botones tactiles, espacios de arma, vida ni al personaje. */
    static void geometry(RunScreen sc, Level lv, Player p, String kind) {
        ContextBtn c = sc.ctx; Input in = sc.in;
        int w = sc.W(); float H = ViewSize.h;
        ck("11 " + kind + ": boton contextual dentro de la pantalla [" + (int) c.x + "," + (int) c.y + " " + (int) c.w + "x" + (int) c.h + " en " + w + "x" + (int) H + "]", c.x >= 0 && c.y >= 40 && c.x + c.w <= w && c.y + c.h <= H);
        ck("11 " + kind + ": tamano comodo (alto >= 28, ancho >= 100)", c.h >= 28 && c.w >= 100);
        String bad = "";
        if (sc.game.touchUiVisible()) {
            for (int i = 0; i < Input.B_COUNT; i++) {
                Input.Btn b = in.btn[i];
                if (!b.visible) continue;
                if (circleRect(b.cx, b.cy, b.r, c.x, c.y, c.w, c.h)) bad += " " + Input.NAMES[i];
            }
        }
        for (int i : new int[]{Input.B_WMAIN, Input.B_WSEC}) { Input.Btn b = in.btn[i]; if (circleRect(b.cx, b.cy, b.r, c.x, c.y, c.w, c.h)) bad += " " + Input.NAMES[i]; }
        ck("11 " + kind + ": no se superpone con controles de combate ni espacios de arma" + bad, bad.isEmpty());
        float z = lv.camZoom;
        float psx = (p.x - lv.camX) * z + (1 - z) * w / 2f, psy = (p.y - lv.camY) * z + (1 - z) * H / 2f;
        boolean hitPl = c.x < psx + 14 && c.x + c.w > psx - 14 && c.y < psy + 2 && c.y + c.h > psy - p.bh;
        ck("11 " + kind + ": no tapa al personaje (pies y=" + (int) psy + ", boton " + (int) c.y + ".." + (int) (c.y + c.h) + ")", !hitPl);
        ck("12 " + kind + ": sin hp/ultimate debajo (esquina superior izquierda libre)", c.y > 40 || c.x > 130);
    }
}
