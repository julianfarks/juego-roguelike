package com.julianfarks.roguelike.core;

import java.util.*;

/**
 * Prueba del combate terrestre de la Reina de la Escarcha (BOT_BOSSGROUND=1 con BOT_WARP=boss:2; banco headless).
 * Etapas: jugador en el suelo, en cada plataforma (de abajo a arriba), saltando junto a ella, fase 2 y, al final, sin invulnerabilidad para medir el dano.
 * En CADA fotograma comprueba: no vuela (flying=false, gravedad normal), los pies sobre el suelo cuando no esta cayendo (sin flotar), nunca dentro
 * de un bloque (ni hundida ni a traves de plataformas), que la animacion es una del suelo y que el combate sigue (ataques, conjuros, deslizamientos).
 */
final class BossGroundProbe {
    private BossGroundProbe() {}
    static int t0 = -1, fails = 0, oks = 0, stage = -1, stageT;
    static void ck(String n, boolean ok) { System.out.println("BG " + (ok ? "OK    " : "FALLA ") + n); if (ok) oks++; else fails++; }

    static List<float[]> plats = new ArrayList<>();
    static float floorY;
    static int frames, airFrames, maxAir, airRun, inSolid, flyFrames, floatFrames, attacks, casts, glides, prevState = -1, dmgHits, phase2Frames;
    static float lastHp, minFeet = 1e9f, maxFeet = -1e9f;
    static final Set<Integer> states = new HashSet<>();
    static final Set<String> anims = new TreeSet<>();
    static boolean wasGlide;

    static void scan(Level lv) {
        Room rm = lv.room; floorY = rm.spawnY;
        TreeMap<Integer, List<Integer>> byRow = new TreeMap<>();
        for (int tx = 2; tx <= rm.w - 3; tx++) for (int ty = 2; ty * Room.TS < floorY - 2 * Room.TS; ty++) {
            int t = rm.tile(tx, ty);
            if ((Room.isSolid(t) || t == Room.ONEWAY) && !Room.isSolid(rm.tile(tx, ty - 1)) && !Room.isSolid(rm.tile(tx, ty - 2)) && rm.tile(tx, ty - 1) != Room.ONEWAY) {
                byRow.computeIfAbsent(ty, k -> new ArrayList<>()).add(tx); break;
            }
        }
        for (Map.Entry<Integer, List<Integer>> e : byRow.descendingMap().entrySet()) {
            List<Integer> xs = e.getValue(); if (xs.size() < 3) continue;
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
            t0 = frame; scan(lv); lv.enemies.clear();
            System.out.println("BG jefe=" + b.def.key + " vuela=" + b.flying + " gravedad=" + b.gravity + " plataformas=" + plats.size() + " suelo=" + floorY + " pies=" + b.y + " enSuelo=" + b.onGround);
            boolean feetOnTile = Math.abs(b.y - Math.round(b.y / Room.TS) * Room.TS) < 0.6f && Room.isSolid(lv.room.tile((int) (b.x / Room.TS), (int) (b.y / Room.TS)));
            ck("tras la presentacion la reina esta apoyada en el suelo (pies " + (int) b.y + " sobre baldosa solida, suelo de la sala " + (int) floorY + ")", feetOnTile && !b.flying);
            stage = 0; stageT = 0; tp(p, lv.room.spawnX + 60, floorY);
            lastHp = rs.rs.hp;
            return false;
        }
        boolean dmgStage = stage == plats.size() + 3;
        if (!dmgStage) { rs.rs.hp = rs.rs.stats.maxHp; p.invuln = 999; }
        else {      // ultima etapa: el jugador recibe dano real (se cura despues de contarlo)
            if (rs.rs.hp < lastHp - 0.01f) dmgHits++;
            if (rs.rs.hp < rs.rs.stats.maxHp * 0.5f) rs.rs.hp = rs.rs.stats.maxHp;
            lastHp = rs.rs.hp;
        }
        stageT++;
        if (b.alive && b.state != Boss.INTRO && b.state != Boss.DEAD) {
            frames++;
            if (b.flying || !b.gravity) flyFrames++;
            Room rm = lv.room;
            // dentro de un bloque: cualquier baldosa solida dentro de la caja del cuerpo (con 2 px de margen)
            if (!lv.boxFree(b, b.x, b.y - 2, b.bh - 4)) inSolid++;
            if (b.onGround) {
                airRun = 0;
                int ty = (int) Math.floor(b.y / Room.TS);
                if (Math.abs(b.y - ty * Room.TS) > 0.6f) floatFrames++;       // apoyada exactamente sobre la superficie
                minFeet = Math.min(minFeet, b.y); maxFeet = Math.max(maxFeet, b.y);
            } else {
                airFrames++; airRun++; maxAir = Math.max(maxAir, airRun);
                if (Math.abs(b.vy) < 1f && b.state != Boss.PHASE) floatFrames++;  // en el aire sin caer = flotando
            }
            if (b.phase == 2) phase2Frames++;
            states.add(b.state); anims.add(b.animName);
            if (b.state == Boss.ATTACK && prevState != Boss.ATTACK) attacks++;
            if (b.state == Boss.CAST && prevState != Boss.CAST) casts++;
            boolean glide = b.state == Boss.IDLE && Math.abs(b.vx) > b.def.speed * 1.2f;
            if (glide && !wasGlide) glides++;
            wasGlide = glide;
            prevState = b.state;
        }
        if (stage == plats.size() + 1 && stageT % 40 == 0 && p.onGround) p.vy = -330f;
        if (stage == plats.size() + 1 && stageT % 20 == 0) p.x = Mth.approach(p.x, b.x - 50, 40f);
        if (stageT % 90 == 0) rs.in.key('J', true);
        if (stageT % 90 == 3) rs.in.key('J', false);
        int len = dmgStage ? 900 : 360;
        if (stageT >= len) {
            String nm = stage == 0 ? "suelo" : stage <= plats.size() ? "plataforma " + stage : stage == plats.size() + 1 ? "saltos junto a ella" : stage == plats.size() + 2 ? "fase 2" : "dano real";
            ck("etapa " + nm + ": nunca vuela, nunca flota, nunca dentro de un bloque (vuelo " + flyFrames + ", flotando " + floatFrames + ", en bloque " + inSolid + " fotogramas)", flyFrames == 0 && floatFrames == 0 && inSolid == 0);
            stage++; stageT = 0;
            if (stage <= plats.size()) { float[] pl = plats.get(stage - 1); tp(p, pl[0], pl[1]); }
            else if (stage == plats.size() + 1) tp(p, b.x - 60, floorY);
            else if (stage == plats.size() + 2) { b.hp = Math.min(b.hp, b.maxHp * 0.45f); tp(p, b.x - 70, floorY); }
            else if (stage == plats.size() + 3) { tp(p, b.x - 70, floorY); p.invuln = 0; lastHp = rs.rs.hp; }
            else {
                ck("pies siempre sobre una superficie: y de los pies en el suelo entre " + (int) minFeet + " y " + (int) maxFeet + " (suelo de la sala " + (int) floorY + ")", maxFeet <= floorY + 0.5f);
                ck("tiempo en el aire razonable (caidas reales): " + airFrames + " de " + frames + " fotogramas, racha maxima " + maxAir, maxAir < 90);
                ck("sigue atacando: " + attacks + " ataques cuerpo a cuerpo, " + casts + " abanicos de hielo, " + glides + " deslizamientos sobre el hielo", attacks >= 4 && casts >= 2 && glides >= 1);
                ck("usa sus animaciones terrestres " + anims, anims.contains("walk") && anims.contains("attack1") && anims.contains("cast"));
                ck("fase 2 alcanzada (" + phase2Frames + " fotogramas en fase 2) sin quedarse bloqueada", b.phase == 2 && phase2Frames > 200);
                ck("sus ataques siguen causando dano al jugador (" + dmgHits + " golpes recibidos en 15 s)", dmgHits >= 2);
                System.out.println("BG FIN ok=" + oks + " fallos=" + fails);
                return true;
            }
        }
        return false;
    }
}
