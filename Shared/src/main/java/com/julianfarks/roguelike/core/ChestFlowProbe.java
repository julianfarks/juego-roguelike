package com.julianfarks.roguelike.core;

/**
 * Prueba del flujo real del cofre con «Omitir» (BOT_CHESTFLOW=1; banco headless). Usa un cofre real de la sala y las entradas reales:
 * tecla de interactuar para abrirlo y TOQUES en las coordenadas de los botones/cartas.
 *  1) abrir -> tres ofertas; 2) omitir -> se cierra, el cofre sigue, equipo intacto, el jugador se mueve; 3) reabrir -> mismas ofertas,
 *  sin botin repetido; 4) omitir 3 veces mas; 5) elegir una carta -> se aplica y el cofre se consume (no se puede volver a abrir).
 *  Ademas comprueba la colocacion de los botones (Elegir centrado, Omitir abajo a la derecha, sin solapes ni fuera de pantalla).
 */
final class ChestFlowProbe {
    private ChestFlowProbe() {}
    static int step = -1, t0, fails, oks, skips, pick0;
    static Prop chest;
    static ChestLoot.Reward[] first;
    static String equip0 = "";
    static int pickups0, opened0;
    static float px0;

    static void ck(String n, boolean ok) { System.out.println("CF " + (ok ? "OK    " : "FALLA ") + n); if (ok) oks++; else fails++; }
    static boolean done() { return step >= 99; }

    private static Screen.Hit hit(RunScreen rs, String label, int tag) {
        for (Screen.Hit h : rs.hitsDbg()) if ((label != null && label.equals(h.label)) || (label == null && h.label == null && h.tag == tag)) return h;
        return null;
    }
    private static void tap(RunScreen rs, Screen.Hit h) { rs.touch(0, Platform.ACTION_DOWN, h.x + h.w / 2f, h.y + h.h / 2f); rs.touch(0, Platform.ACTION_UP, h.x + h.w / 2f, h.y + h.h / 2f); }
    private static String snap(RunState r) { return r.sec + "/" + r.secAmmo + "/" + r.shield + "/" + r.weaponLvl + "/" + r.special + "/" + java.util.Arrays.toString(r.bless) + "/" + r.gren + "/" + r.potions + "/" + java.util.Arrays.toString(r.cb) + "/" + r.grenCount + "/" + r.stats.maxHp + "/" + r.secLvl + "/" + r.grenLvl + "/" + r.secAmmo + "/" + r.gold + "/" + r.souls + "/" + r.ult; }

    private static void layoutCheck(RunScreen rs, int w) {
        Screen.Hit ok = null, sk = hit(rs, "Omitir", 0);
        for (Screen.Hit h : rs.hitsDbg()) if (h.label != null && (h.label.equals("Toca una carta") || h.label.equals("Elegir") || h.label.equals("Confirmar"))) ok = h;
        float cardBottom = 0; for (Screen.Hit h : rs.hitsDbg()) if (h.label == null && h.tag >= 0 && h.tag <= 2) cardBottom = Math.max(cardBottom, h.y + h.h);
        int H = ViewSize.h;
        boolean centered = ok != null && Math.abs(ok.x + ok.w / 2f - w / 2f) < 1f;
        boolean right = sk != null && sk.x + sk.w <= w - 8 && sk.x + sk.w >= w - 30 && sk.y + sk.h <= H - 4;
        boolean sep = ok != null && sk != null && sk.x - (ok.x + ok.w) >= 20;
        boolean noCard = sk != null && sk.y >= cardBottom && ok != null && ok.y >= cardBottom;
        ck("botones (" + w + "x" + H + "): «" + (ok == null ? "?" : ok.label) + "» centrado=" + centered + ", «Omitir» abajo a la derecha=" + right + ", separados " + (ok == null || sk == null ? -1 : Math.round(sk.x - ok.x - ok.w)) + " px, sin invadir las cartas=" + noCard,
                centered && right && sep && noCard);
    }

    static boolean step(Game g, RunScreen rs, Level lv, Player p, int frame) {
        RunState r = rs.rs;
        if (step < 0) {
            if (frame < 700) return false;
            for (int c : new int[]{'A', 'D', 'S', 'W', 'J', 'K', 'E'}) g.key(c, false);
            lv.enemies.clear(); lv.toKill = 0; lv.projs.clear();
            float[] sp = ChestSpot.find(lv, p.x + 30, p.y);
            chest = lv.addProp(new Room.PropSpec("chest", sp[0], sp[1], 2));
            chest.roundChest = true;
            p.x = sp[0] - 14; p.y = sp[1]; p.vx = 0; p.vy = 0; p.right = true;
            r.sec = 6; r.wState[6] = 1; r.secAmmo = 7; r.secActive = false;
            opened0 = Save.S.chestsOpened;
            step = 0; t0 = frame; return true;
        }
        lv.rs.hp = lv.rs.stats.maxHp;
        int t = frame - t0;
        switch (step) {
            case 0: if (t == 10) { g.key('E', true); } if (t == 12) { g.key('E', false); step = 1; t0 = frame; } return true;
            case 1: {   // esperar la ventana del cofre
                if (rs.debugOv() != RunScreen.OV_CHEST || rs.ovT < 0.5f) { if (t > 120) { ck("el cofre se abre con interactuar", false); step = 99; } return true; }
                first = rs.cOffer; equip0 = snap(r); pickups0 = lv.pickups.size();
                ck("abrir: 3 ofertas (" + first.length + ")", first.length == 3);
                ck("contador de cofres abiertos +1 (" + opened0 + " -> " + Save.S.chestsOpened + ")", Save.S.chestsOpened == opened0 + 1);
                layoutCheck(rs, g.viewW);
                Screen.Hit sk = hit(rs, "Omitir", 0);
                ck("el boton dice exactamente «Omitir»", sk != null);
                tap(rs, sk); step = 2; t0 = frame; return true;
            }
            case 2: {
                if (t == 1) {
                    ck("omitir cierra la ventana (ov=" + rs.debugOv() + ")", rs.debugOv() == RunScreen.OV_NONE);
                    ck("el cofre sigue en la sala, sin consumir (used=" + chest.used + ", en la sala=" + lv.props.contains(chest) + ")", !chest.used && !chest.dead && lv.props.contains(chest));
                    ck("el cofre guarda sus mismas ofertas", chest.pending == first);
                    ck("omitir no toca el equipo (" + equip0.equals(snap(r)) + ")", equip0.equals(snap(r)));
                    px0 = p.x; g.key('A', true);
                }
                if (t == 25) { g.key('A', false); ck("el jugador recupera el control tras omitir (se movio " + Math.round(px0 - p.x) + " px)", px0 - p.x > 10); }
                if (t == 26) { p.x = chest.x - 14; p.y = chest.y; p.vx = 0; p.vy = 0; }      // vuelve junto al cofre (al andar pudo bajar de una repisa)
                if (t == 40) { g.key('E', true); }
                if (t == 42) { g.key('E', false); step = 3; t0 = frame; }
                return true;
            }
            case 3: {   // reabrir
                if (rs.debugOv() != RunScreen.OV_CHEST || rs.ovT < 0.5f) { if (t > 120) { Prop n = lv.nearestInteractable(); ck("se puede volver a abrir el mismo cofre [cerca=" + (n == null ? "nada" : n.kind) + " cofre " + Math.round(chest.x) + "," + Math.round(chest.y) + " jugador " + Math.round(p.x) + "," + Math.round(p.y) + " lock " + chest.pickLock + " ov " + rs.debugOv() + "]", false); step = 99; } return true; }
                skips++;
                ck("reabrir (" + skips + "): mismas tres ofertas, sin sortear de nuevo", rs.cOffer == first);
                ck("reabrir (" + skips + "): sin botin ni contador repetidos (objetos en el suelo " + pickups0 + " -> " + lv.pickups.size() + ", cofres abiertos " + Save.S.chestsOpened + ")", lv.pickups.size() <= pickups0 && Save.S.chestsOpened == opened0 + 1);
                if (skips < 4) { tap(rs, hit(rs, "Omitir", 0)); step = 4; t0 = frame; return true; }
                // elegir la primera carta: un toque la marca, el segundo la confirma
                tap(rs, hit(rs, null, 0)); step = 5; t0 = frame; return true;
            }
            case 4: {
                if (t == 1) ck("omitir otra vez (" + skips + "): cerrado, cofre presente y sin consumir", rs.debugOv() == RunScreen.OV_NONE && !chest.used && lv.props.contains(chest) && chest.pending == first);
                if (t == 5) { g.key('E', true); }
                if (t == 7) { g.key('E', false); }
                if (t == 20) ck("pulsar interactuar justo al cerrar no reabre por accidente (ov=" + rs.debugOv() + ")", rs.debugOv() == RunScreen.OV_NONE);
                if (t == 35) { g.key('E', true); }       // tras el bloqueo breve (0,4 s) que evita reabrir con la misma pulsacion
                if (t == 37) { g.key('E', false); step = 3; t0 = frame; }
                return true;
            }
            case 5: {
                if (t == 2 && rs.debugOv() == RunScreen.OV_CHEST && hit(rs, null, 0) != null) tap(rs, hit(rs, null, 0));   // si la carta ya estaba marcada (teclado), el primer toque ya confirmo
                if (t == 6 && rs.debugOv() == RunScreen.OV_WCMP) { rs.dbgWcmp(true); }
                if (t == 10) {
                    ChestLoot.Reward x = first[0];
                    ck("elegir tras omitir 3 veces: la ventana se cierra (ov=" + rs.debugOv() + ")", rs.debugOv() == RunScreen.OV_NONE);
                    ck("la recompensa elegida se aplica (" + x.name + "; equipo cambio=" + !equip0.equals(snap(r)) + ")", !equip0.equals(snap(r)) || x.kind == ChestLoot.K_HEAL);
                    ck("solo ahora el cofre se consume (used=" + chest.used + ", ofertas=" + (chest.pending == null ? "ninguna" : "pendientes") + ")", chest.used && chest.pending == null);
                    g.key('E', true);
                }
                if (t == 12) g.key('E', false);
                if (t == 60) {
                    ck("un cofre consumido no se puede volver a abrir (ov=" + rs.debugOv() + ")", rs.debugOv() == RunScreen.OV_NONE);
                    System.out.println("CF FIN ok=" + oks + " fallos=" + fails);
                    step = 99;
                }
                return true;
            }
        }
        return true;
    }
}
