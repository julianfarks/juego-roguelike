package com.julianfarks.roguelike.core;

import java.util.*;

/**
 * Pruebas de animacion de combate (solo banco headless; BOT_ANIMTEST=1 desde DebugBot):
 *  hojas : las 10 clases tienen smear frames y pesos de duracion coherentes; el golpe cae en los mismos fotogramas de contacto, nunca en el smear;
 *  tiempo: duracion y fotograma dependen solo del tiempo (no de los FPS), fotogramas monotonos y la animacion termina;
 *  vivo  : combo real 1-2-3 contra un maniqui: el smear se muestra antes del contacto, el impacto solo ocurre en fotogramas de golpe,
 *          un ataque que falla no genera impacto, la pose de impacto es solo visual y dura ~0,16 s, y el sonido de impacto tiene presupuesto.
 */
final class AnimProbe {
    private AnimProbe() {}
    static int t0 = -1, fails = 0, oks = 0;
    static void ck(String n, boolean ok) { System.out.println("AN " + (ok ? "OK    " : "FALLA ") + n); if (ok) oks++; else fails++; }

    static final String[] CLASSES = {"astral", "blood", "earth", "flame", "frost", "paladin", "shadow", "steel", "storm", "verdant"};
    static final String[] SM = {"attack1", "attack2", "attack3", "airatk", "roll"};

    static Enemy dummy;
    static final Map<String, Set<Integer>> seen = new HashMap<>(), hitAt = new HashMap<>();
    static int lastImp, impMiss;
    static float hp0;

    static boolean step(Game g, RunScreen rs, Level lv, Player p, int frame) {
        if (t0 < 0) {
            t0 = frame;
            for (int c : new int[]{'A', 'D', 'W', 'S', 37, 38, 39, 40, 'J', 'K', 'R', 'T', 'E', 32}) g.key(c, false);
            lv.enemies.clear(); lv.projs.clear(); lv.toKill = 0; lv.cleared = true; p.invuln = 999;
            p.state = Player.IDLE; p.animName = "idle"; p.vx = 0;
            sheets();
            return false;
        }
        int t = frame - t0;
        Input in = rs.in;
        if (t == 5) {
            dummy = new Enemy(EnemyDef.get("esqueleto"), false, 1f, 1f);
            dummy.hp = dummy.maxHp = 1e7f; dummy.x = p.x + 26; dummy.y = p.y; dummy.home = dummy.x; dummy.state = Enemy.PATROL;
            lv.enemies.add(dummy); lv.toKill = 999; lv.cleared = false; p.right = true; hp0 = dummy.hp; lastImp = lv.dbgImpacts;
        }
        // combo: pulsaciones repetidas durante 70 fotogramas
        if (t >= 10 && t < 80) {
            if (t % 3 == 0) in.key('J', true); else in.key('J', false);
            dummy.x = p.x + 26; dummy.vx = 0; dummy.hp = Math.max(dummy.hp, dummy.maxHp * 0.5f);
            if (p.state == Player.ATK && p.animName.startsWith("attack")) {
                Anim a = p.anim(); int f = a.frameAt(p.animT);
                seen.computeIfAbsent(p.animName, k -> new TreeSet<>()).add(f);
                if (lv.dbgImpacts > lastImp) hitAt.computeIfAbsent(p.animName, k -> new TreeSet<>()).add(f);
            }
            lastImp = lv.dbgImpacts;
        }
        if (t == 80) {
            in.key('J', false);
            for (String n : new String[]{"attack1", "attack2", "attack3"}) {
                Anim a = p.sheet.anim(n);
                Set<Integer> s = seen.getOrDefault(n, Set.of()), h = hitAt.getOrDefault(n, Set.of());
                ck("vivo " + n + ": se muestra el fotograma smear (" + a.smear + ") antes del contacto " + s, s.contains(a.smear));
                ck("vivo " + n + ": hubo impactos y solo en fotogramas de golpe [" + a.h0 + "," + a.h1 + "] -> " + h, !h.isEmpty() && h.stream().allMatch(f -> f >= a.h0 && f <= a.h1));
                ck("vivo " + n + ": el smear no es un fotograma de golpe", a.smear < a.h0);
            }
            // pose de impacto: instante de contacto, solo visual, dura ~0,16 s
            lv.enemies.clear(); dummy = new Enemy(EnemyDef.get("esqueleto"), false, 1f, 1f); dummy.x = p.x + 20; dummy.y = p.y; lv.enemies.add(dummy);
            float bw = dummy.bw, bh = dummy.bh; Impact.hit(lv, dummy, Impact.HEAVY, 1f, false, null);
            float[] o = new float[3];
            ck("impacto: la pose arranca en el instante del contacto", Impact.react(lv, dummy, o) && o[0] < 1f && o[1] > 1f);
            ck("impacto: es solo visual (no cambia las cajas de colision) y esta acotada", dummy.bw == bw && dummy.bh == bh && o[0] > 0.7f && o[1] < 1.3f);
            lv.time += 0.2f;
            ck("impacto: termina a los 0,16 s (sin pose permanente)", !Impact.react(lv, dummy, o));
            Impact.hit(lv, dummy, Impact.LIGHT, 1f, false, null); float[] l = new float[3]; Impact.react(lv, dummy, l);
            Impact.hit(lv, dummy, Impact.CRIT, 1f, false, null); Impact.react(lv, dummy, o);
            ck("impacto: ligero distinto de critico (el critico exagera mas)", o[0] < l[0]);
            // sin impactos fantasma: ataque al aire
            lv.enemies.clear(); lv.toKill = 0; lv.cleared = true; impMiss = lv.dbgImpacts;
        }
        if (t >= 85 && t < 130) {                    // ataques sin objetivo
            if (t % 4 == 0) in.key('J', true); else in.key('J', false);
        }
        if (t == 130) {
            in.key('J', false);
            ck("fallo: un ataque que no conecta no genera impactos", lv.dbgImpacts == impMiss);
            // presupuesto de sonido: 20 golpes en el mismo instante -> como mucho 3 capas
            int ok = 0; for (int i = 0; i < 20; i++) if (Impact.sfxOkForTest()) ok++;
            ck("sonido: 20 impactos simultaneos dejan pasar como mucho 3 capas (pasaron " + ok + ")", ok <= 3);
            System.out.println("AN FIN ok=" + oks + " fallos=" + fails);
            return true;
        }
        return false;
    }

    static void sheets() {
        for (String c : CLASSES) {
            Sheet s = Assets.spr("pl_" + c);
            boolean allSm = true, wOk = true, hitOk = true, timeOk = true; String why = "";
            for (String n : SM) {
                Anim a = s.anim(n);
                if (a.smear < 0) { allSm = false; why += " sin smear:" + n; continue; }
                if (a.n > 10) { wOk = false; why += " n>10:" + n; }
                if (a.h0 >= 0 && !(a.smear < a.h0)) { hitOk = false; why += " smear>=h0:" + n; }
                // duracion y fotogramas dependen solo del tiempo
                float d = a.duration(); int prev = -1; boolean mono = true;
                for (float tt = 0; tt < d + 0.2f; tt += 0.001f) { int f = a.frameAt(tt); if (f < prev) mono = false; prev = f; }
                if (!(mono && prev == a.n - 1 && a.frameAt(d - 0.0005f) == a.n - 1 && a.done(d) && !a.done(d - 0.01f))) { timeOk = false; why += " tiempo:" + n; }
                if (a.frameAt(0) != 0) { timeOk = false; why += " f0:" + n; }
            }
            ck("hoja " + c + ": smear en ataques 1-3, aereo y esquiva" + why, allSm && wOk && hitOk && timeOk);
        }
        Sheet s = Assets.spr("pl_steel");
        Anim a1 = s.anim("attack1"), a3 = s.anim("attack3");
        ck("anticipacion: el fotograma de golpe llega despues de la anticipacion (ataque pesado mas tarde que el rapido)", a3.duration() > a1.duration() && a3.frameAt(0.10f) < a3.h0);
        ck("recuperacion: tras el golpe quedan fotogramas de recuperacion con peso", a1.n - 1 > a1.h1 && a3.n - 1 > a3.h1);
        // misma duracion sin importar el FPS del dispositivo: simular 30 y 60 fps de paso y llegar al mismo fotograma
        float t30 = 0, t60 = 0; for (int i = 0; i < 12; i++) t30 += 1f / 30f; for (int i = 0; i < 24; i++) t60 += 1f / 60f;
        ck("independiente de FPS: 0,4 s a 30 fps y a 60 fps dan el mismo fotograma", a3.frameAt(t30) == a3.frameAt(t60));
    }
}
