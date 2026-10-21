package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Escalado CENTRAL de las hordas: tras cada jefe derrotado las salas de combate traen progresivamente mas enemigos,
 * combinaciones de tipos, variantes (elites) y, mas adelante, un mini-jefe ocasional. Todo se configura aqui (nada de numeros sueltos
 * en el resto del codigo). El modo Infinito escala por su cuenta (por piso), sin depender de los jefes de campaña.
 *
 * Rendimiento y jugabilidad: nunca hay mas de maxAlive() enemigos vivos a la vez. Los que sobran esperan en una reserva y entran poco a
 * poco (spawnGap() segundos entre refuerzos, en un punto de aparicion alejado del jugador y nunca encima de el). La reserva es de la sala:
 * al cambiar de sala se descarta (no se duplica en transiciones) y la sala no se da por despejada hasta vaciarla.
 */
final class Escalation {
    private Escalation() {}

    // ================================================================ configuracion (unico punto de ajuste)
    /** Enemigos extra por cada jefe derrotado en campaña, como fraccion de los de la sala (0,15 = +15% por jefe). */
    static final float EXTRA_PER_BOSS = 0.15f;
    /** Tope del extra de campaña (1,0 = como mucho el doble de la sala base). */
    static final float EXTRA_MAX = 1.0f;
    /** Infinito: extra por piso superado y tope propios (independiente de los jefes de campaña). */
    static final float EXTRA_PER_FLOOR = 0.12f, EXTRA_MAX_INF = 1.8f;
    /** Multiplicador del extra segun la dificultad elegida (facil, normal, dificil). */
    static final float[] DIFF_MUL = {0.6f, 1f, 1.3f};
    /** Enemigos vivos a la vez como maximo (rendimiento y legibilidad): base + por jefe, con tope absoluto. */
    static final int ALIVE_BASE = 7, ALIVE_PER_BOSS = 1, ALIVE_MAX = 13;
    /** Segundos entre refuerzos de la reserva; baja un poco con cada jefe (minimo SPAWN_GAP_MIN). */
    static final float SPAWN_GAP = 1.8f, SPAWN_GAP_STEP = 0.1f, SPAWN_GAP_MIN = 0.9f;
    /** Distancia minima al jugador para que aparezca un refuerzo (nunca encima de el). */
    static final float SPAWN_MIN_DIST = 110f;
    /** Variantes: a partir de VARIANT_FROM jefes, cada extra tiene esta probabilidad (por jefe) de ser elite, con tope. */
    static final int VARIANT_FROM = 2; static final float VARIANT_PER_BOSS = 0.05f, VARIANT_MAX = 0.3f;
    /** Mini-jefe ocasional en salas de combate a partir de MINIBOSS_FROM jefes (probabilidad por sala). */
    static final int MINIBOSS_FROM = 4; static final float MINIBOSS_CHANCE = 0.25f;
    /** Persecucion: el rango de deteccion crece con los jefes derrotados (los enemigos te ven antes y te siguen mas lejos). */
    static final float DETECT_PER_BOSS = 0.07f, DETECT_MAX = 1.6f;

    // ================================================================ calculo
    /** Jefes principales derrotados en esta partida (campaña) o pisos superados (Infinito). */
    static int bosses(RunState rs) { return rs.infinite ? Math.max(0, rs.floor - 1) : Math.max(0, rs.dungeonNo); }

    static float diffMul(RunState rs) { return DIFF_MUL[Math.max(0, Math.min(2, rs.diff))]; }

    /** Fraccion extra de enemigos (0 = sala base). */
    static float extraFactor(RunState rs) {
        int b = bosses(rs);
        float f = rs.infinite ? Math.min(EXTRA_MAX_INF, EXTRA_PER_FLOOR * b) : Math.min(EXTRA_MAX, EXTRA_PER_BOSS * b);
        return f * diffMul(rs);
    }

    /** Enemigos extra para una sala con `base` enemigos. */
    static int extraCount(RunState rs, int base) { return base <= 0 ? 0 : Math.round(base * extraFactor(rs)); }

    static int maxAlive(RunState rs) { return Math.min(ALIVE_MAX, ALIVE_BASE + ALIVE_PER_BOSS * bosses(rs)); }

    static float spawnGap(RunState rs) { return Math.max(SPAWN_GAP_MIN, SPAWN_GAP - SPAWN_GAP_STEP * bosses(rs)); }

    static float variantChance(RunState rs) { int b = bosses(rs); return b < VARIANT_FROM ? 0f : Math.min(VARIANT_MAX, VARIANT_PER_BOSS * (b - VARIANT_FROM + 1)); }

    static float detectMul(RunState rs) { return Math.min(DETECT_MAX, 1f + DETECT_PER_BOSS * bosses(rs)); }

    static boolean applies(Level lv) {
        int t = lv.room.type;
        return (t == Room.COMBAT || t == Room.ELITE) && !lv.rs.boss() && lv.rs.curEvent == 0;
    }

    // ================================================================ sala
    /**
     * Llamado al poblar la sala (Level.populate), tras los enemigos de la generacion. Añade los extras de este escalado mezclando los tipos
     * de la sala (combinaciones), con variantes elite y mini-jefe ocasional, y deja vivos como mucho maxAlive(): el resto va a la reserva.
     */
    static void populate(Level lv, float hpMul, float dmgMul) {
        RunState rs = lv.rs;
        lv.reserve.clear(); lv.reserveT = 0;
        if (!applies(lv)) return;
        List<Enemy> base = new ArrayList<>();
        for (Enemy e : lv.enemies) if (!e.optional && !e.guardian) base.add(e);
        float dm = detectMul(rs);
        for (Enemy e : lv.enemies) e.detectMul = dm;
        int extra = extraCount(rs, base.size());
        if (base.isEmpty()) return;
        Rng r = new Rng(rs.seed ^ (rs.dungeonNo * 92821L + rs.roomNo * 6151L + rs.floor * 337L + 777L));     // determinista por partida/sala
        List<Enemy> add = new ArrayList<>();
        float vch = variantChance(rs);
        for (int i = 0; i < extra; i++) {
            Enemy src = base.get(r.i(base.size()));            // tipos de la propia sala: combinaciones coherentes con el bioma
            boolean el = r.chance(vch);
            Enemy c = new Enemy(src.def, el, hpMul, dmgMul);
            c.x = src.x; c.y = src.y; c.home = src.x; c.detectMul = dm; c.hunter = true;
            if (src.modSpeed > 1f) c.modSpeed = src.modSpeed;
            add.add(c);
        }
        if (bosses(rs) >= MINIBOSS_FROM && lv.room.type == Room.COMBAT && r.chance(MINIBOSS_CHANCE)) {     // mini-jefe: el tipo mas duro de la sala, elite y reforzado
            Enemy src = base.get(0); for (Enemy e : base) if (e.def.hp > src.def.hp) src = e;
            Enemy mb = new Enemy(src.def, true, hpMul * 2.2f, dmgMul * 1.15f);
            mb.x = src.x; mb.y = src.y; mb.home = src.x; mb.detectMul = dm; mb.hunter = true; mb.miniBoss = true;
            add.add(mb);
        }
        // vivos a la vez: los extra solo entran mientras haya hueco por debajo de maxAlive(); el resto espera en la reserva (entran poco a poco).
        // Los enemigos propios de la sala se quedan como estaban (sin escalado la sala es identica a la de siempre).
        int alive = 0; for (Enemy e : lv.enemies) if (e.alive && !e.optional) alive++;
        int cap = maxAlive(rs);
        for (Enemy e : add) {
            if (alive < cap) { float[] at = spawnPoint(lv, e); e.x = at[0] + r.f(-10, 10); e.y = at[1]; e.home = e.x; lv.enemies.add(e); alive++; }
            else lv.reserve.add(e);
        }
        lv.escExtra = add.size();
    }

    /** Cada fotograma: si hay hueco por debajo del tope, entra el siguiente refuerzo (con un respiro entre ellos). */
    static void update(Level lv, float dt) {
        if (lv.reserve.isEmpty() || lv.pl == null || !lv.pl.alive) return;
        lv.reserveT -= dt;
        if (lv.reserveT > 0) return;
        int alive = 0; for (Enemy e : lv.enemies) if (e.alive && !e.optional) alive++;
        if (alive >= maxAlive(lv.rs)) return;
        Enemy e = lv.reserve.remove(0);
        float[] at = spawnPoint(lv, e);
        e.x = at[0]; e.y = at[1]; e.home = at[0]; e.vx = 0; e.vy = 0;
        lv.enemies.add(e);
        lv.reserveT = spawnGap(lv.rs);
        lv.escSpawned++;
        lv.fxAdd("fx_ring", "pulse", e.x, e.y - 14, 0.7f, 0xD04040);
        lv.ps.burst(lv.rng, e.x, e.y - 12, 0xD04040, 10, 80, 0.5f, 2, -10, true);
    }

    /** Punto de aparicion: uno de los de la sala, lejos del jugador (>= SPAWN_MIN_DIST); se prefieren los del mismo tipo de enemigo
     *  (terreno adecuado: suelo para los de a pie, aire para los voladores). Si ninguno esta lejos, el mas alejado. */
    static float[] spawnPoint(Level lv, Enemy e) {
        float px = lv.pl.x, py = lv.pl.y;
        List<float[]> same = new ArrayList<>(), any = new ArrayList<>();
        float[] far = null; float fd = -1;
        for (Room.Spawn s : lv.room.spawns) {
            if (s.optional) continue;
            float d = Mth.dist(s.x, s.y, px, py);
            boolean st = s.enemy.equals(e.def.id);
            if (d >= SPAWN_MIN_DIST) { any.add(new float[]{s.x, s.y}); if (st) same.add(new float[]{s.x, s.y}); }
            if (d > fd && (st || far == null)) { fd = d; far = new float[]{s.x, s.y}; }
        }
        if (!same.isEmpty()) return same.get(lv.rng.i(same.size()));
        if (!any.isEmpty()) return any.get(lv.rng.i(any.size()));
        if (far != null) return far;
        return new float[]{e.x, e.y};
    }

    /** Enemigos totales de la sala (vivos + reserva): para pruebas y el HUD. */
    static int total(Level lv) { int n = lv.reserve.size(); for (Enemy e : lv.enemies) if (!e.optional) n++; return n; }
}
