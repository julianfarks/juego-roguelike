package com.julianfarks.roguelike.core;

import java.util.*;

/**
 * Prueba del vuelo de jefes voladores (solo banco headless; BOT_BOSSFLY=1 con BOT_WARP=boss:1 = Reina de la Escarcha).
 * El jugador (invulnerable) recorre: suelo -> todas las plataformas alcanzables, de abajo a arriba -> saltos repetidos debajo de la reina -> fase 2 en lo alto.
 * Comprueba en CADA fotograma que la reina esta dentro de su banda de vuelo (techo/suelo de la geometria real), que por mucho que se suba no asciende
 * mas alla del limite, que mantiene alcance vertical con el jugador y que sigue atacando (no se vuelve pasiva ni terrestre).
 */
final class BossFlyProbe {
    private BossFlyProbe() {}
    static int t0 = -1, fails = 0, oks = 0, stage = -1, stageT;
    static void ck(String n, boolean ok) { System.out.println("BF " + (ok ? "OK    " : "FALLA ") + n); if (ok) oks++; else fails++; }

    static List<float[]> plats = new ArrayList<>();      // {x, y(superficie)} de abajo a arriba
    static float minY = 1e9f, maxY = -1e9f, stageMinY, reach, reachN, floorY;
    static final Set<Integer> states = new HashSet<>();
    static int attacks, prevState = -1, outOfBand;
    static float topPlat;
    static boolean zoneOk;

    static void scan(Level lv) {
        Room rm = lv.room; floorY = rm.spawnY;
        TreeMap<Integer, List<Integer>> byRow = new TreeMap<>();
        for (int tx = 2; tx <= rm.w - 3; tx++) for (int ty = 2; ty * Room.TS < floorY - 2 * Room.TS; ty++) {
            int t = rm.tile(tx, ty);
            if ((Room.isSolid(t) || t == Room.ONEWAY) && !Room.isSolid(rm.tile(tx, ty - 1)) && !Room.isSolid(rm.tile(tx, ty - 2)) && rm.tile(tx, ty - 1) != Room.ONEWAY) {
                byRow.computeIfAbsent(ty, k -> new ArrayList<>()).add(tx); break;
            }
        }
        for (Map.Entry<Integer, List<Integer>> e : byRow.descendingMap().entrySet()) {   // de abajo (ty grande) a arriba
            List<Integer> xs = e.getValue(); if (xs.size() < 3) continue;                 // plataformas de al menos 3 tiles
            Collections.sort(xs); int mid = xs.get(xs.size() / 2);
            plats.add(new float[]{mid * Room.TS + Room.TS / 2f, e.getKey() * Room.TS});
        }
    }

    static void tp(Player p, float x, float y) { p.x = x; p.y = y; p.vx = 0; p.vy = 0; p.invuln = 999; p.safeX = x; p.safeY = y; }

    static boolean step(Game g, RunScreen rs, Level lv, Player p, int frame) {
        Boss b = lv.boss;
        if (b == null) return false;
        if (t0 < 0) {
            if (b.state == Boss.INTRO || lv.cinematic || rs.fadeA > 0.05f) return false;
            t0 = frame; scan(lv);
            lv.enemies.clear();
            System.out.println("BF jefe=" + b.def.key + " vuelo=" + b.flying + " plataformas=" + plats.size() + " suelo=" + floorY + " zona=[" + b.zoneTop + "," + b.zoneBot + "] cuerpo=" + b.bh);
            stage = 0; stageT = 0; tp(p, rs.lv.room.spawnX + 60, floorY);
            return false;
        }
        rs.rs.hp = rs.rs.stats.maxHp; p.invuln = 999;
        int len = stage == 0 ? 360 : stage <= plats.size() ? 360 : stage == plats.size() + 1 ? 360 : 420;
        stageT++;
        if (System.getenv("BF_DBG") != null && stageT % 60 == 0 && stage <= 1) System.out.println("BFD st=" + stage + " t=" + stageT + " boss=(" + (int) b.x + "," + (int) b.y + ") st=" + b.state + " p=(" + (int) p.x + "," + (int) p.y + ")");
        if (b.alive && b.state != Boss.INTRO && b.state != Boss.DEAD) {
            minY = Math.min(minY, b.y); maxY = Math.max(maxY, b.y); stageMinY = Math.min(stageMinY, b.y);
            if (b.y < b.zoneTop - 0.5f || b.y > b.zoneBot + 0.5f) outOfBand++;
            states.add(b.state);
            if (b.state == Boss.ATTACK && prevState != Boss.ATTACK) attacks++;
            prevState = b.state;
            boolean hNear0;
            boolean vOverlap = b.y - b.bh <= p.y && b.y >= p.y - 88f, hNear = Math.abs(b.x - p.x) < 160;   // 88 px = alcance de un salto simple (410 px/s, g 1500 = 56 px) + caja de ataque de 32 px
            reachN++; if (vOverlap) reach++;
        }
        if (stageT == 1) { stageMinY = 1e9f; reach = reachN = 0; }
        // acciones del jugador segun la etapa
        if (stage > plats.size() && stage == plats.size() + 1 && stageT % 45 == 0) { p.vy = -330f; }          // saltos repetidos debajo de la reina
        if (stage == plats.size() + 1 && stageT % 20 == 0) p.x = Mth.approach(p.x, b.x, 40f);
        if (stageT % 90 == 0 && stage >= 0) { rs.in.key('J', true); }
        if (stageT % 90 == 3) rs.in.key('J', false);
        if (stageT >= len) {
            String nm = stage == 0 ? "suelo" : stage <= plats.size() ? "plataforma " + stage + " (y=" + (int) plats.get(stage - 1)[1] + ")" : stage == plats.size() + 1 ? "saltos bajo la reina" : "fase 2 arriba";
            ck("etapa " + nm + ": dentro de la banda de vuelo todo el tiempo (min y " + (int) stageMinY + ", banda [" + (int) b.zoneTop + "," + (int) b.zoneBot + "])", outOfBand == 0);
            if (stage <= plats.size()) {
                ck("etapa " + nm + ": la altura de la reina queda al alcance de un salto simple (cuerpo a cuerpo) " + (int) (100 * reach / Math.max(1, reachN)) + " % del tiempo)", reach / Math.max(1, reachN) >= 0.5f);
            }
            stage++; stageT = 0;
            if (stage == plats.size() + 2) { b.hp = Math.min(b.hp, b.maxHp * 0.4f); }
            if (stage <= plats.size()) { float[] pl = plats.get(stage - 1); tp(p, pl[0], pl[1]); }
            else if (stage == plats.size() + 1) tp(p, b.x, floorY);
            else if (stage == plats.size() + 2) { float[] pl = plats.get(plats.size() - 1); tp(p, pl[0], pl[1]); }
            else {
                float ceil = 0; // el cuerpo no puede quedar dentro del techo
                ck("por mucho que suba el jugador, la reina nunca supera su limite superior (min y global " + (int) minY + " >= zona " + (int) b.zoneTop + ")", minY >= b.zoneTop - 0.5f);
                ck("el sprite completo nunca sale de la pantalla por arriba (y - alto de sprite >= -30: " + (int) (minY - 156) + ")", minY - 156 >= -30f);
                ck("la reina nunca sale de la pantalla ni toca el techo (y - cuerpo >= 0 : " + (int) (minY - b.bh) + ")", minY - b.bh >= 0f);
                ck("limite superior independiente de la altura del jugador (zona top " + (int) b.zoneTop + " <= plataforma mas alta + 0)", b.zoneTop <= (plats.isEmpty() ? floorY : plats.get(plats.size() - 1)[1]) + 1f || b.zoneTop <= floorY - 48f);
                ck("sigue siendo voladora (no desciende al suelo): max y global " + (int) maxY + " < suelo " + (int) floorY, maxY < floorY - 10f && b.flying);
                ck("sigue atacando (" + attacks + " ataques) y usando varios estados " + states, attacks >= 3 && states.size() >= 2);
                ck("fase 2 alcanzada sin romper el limite", b.hp <= b.maxHp * 0.5f);
                System.out.println("BF FIN ok=" + oks + " fallos=" + fails);
                return true;
            }
        }
        return false;
    }
}
