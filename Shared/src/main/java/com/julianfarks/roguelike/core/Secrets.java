package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Logica y dibujo en partida de las camaras secretas (ver Secret / SecretGen).
 * Mientras una camara esta cerrada su interior se dibuja como roca (Room.baked) y su recompensa esta oculta;
 * al descubrirla se anima la apertura y se muestra Room.bakedOpen.
 */
final class Secrets {
    private final Level lv;
    private final Room room;
    private final List<Secret> list;
    private final List<List<int[]>> torches = new ArrayList<>();
    private final int[][] box;   // por camara: bbox px de la entrada {x0,y0,x1,y1}
    private float t;

    Secrets(Level lv) {
        this.lv = lv; this.room = lv.room; this.list = lv.room.secrets;
        box = new int[list.size()][];
        for (int i = 0; i < list.size(); i++) {
            Secret s = list.get(i);
            int x0 = 1 << 20, y0 = 1 << 20, x1 = -1, y1 = -1;
            for (int[] d : s.door) { x0 = Math.min(x0, d[0]); y0 = Math.min(y0, d[1]); x1 = Math.max(x1, d[0]); y1 = Math.max(y1, d[1]); }
            box[i] = new int[]{x0 * Room.TS, y0 * Room.TS, (x1 + 1) * Room.TS, (y1 + 1) * Room.TS};
            // las antorchas de dentro no se ven hasta abrir
            List<int[]> mine = new ArrayList<>();
            for (int k = lv.animDeco.size() - 1; k >= 0; k--) {
                int[] d = lv.animDeco.get(k);
                if (s.contains(d[0] / Room.TS, d[1] / Room.TS)) { mine.add(d); lv.animDeco.remove(k); }
            }
            torches.add(mine);
        }
    }

    boolean any() { return !list.isEmpty(); }

    /** Tras crear las propiedades: oculta recompensas. */
    void init() {
        for (Secret s : list) {
            s.rewardProp = null;
            for (Prop p : lv.props) if (Math.abs(p.x - s.rwX) < 1 && Math.abs(p.y - s.rwY) < 1 && (p.kind.equals("chest") || p.kind.equals("relic") || p.kind.equals("shrine"))) { s.rewardProp = p; p.hidden = true; }
        }
    }

    // ------------------------------------------------------------------ entrada de golpes
    /** Un ataque, proyectil o explosion golpea el rectangulo. */
    void hit(float rx, float ry, float rw, float rh, int dmg) {
        for (int i = 0; i < list.size(); i++) {
            Secret s = list.get(i);
            if (s.open || s.revealing) continue;
            int[] b = box[i];
            switch (s.entrance) {
                case Secret.E_WALL, Secret.E_STATUE -> {
                    if (overlap(rx, ry, rw, rh, b[0] - 4, b[1] - 4, b[2] - b[0] + 8, b[3] - b[1] + 8) && lv.time - s.hitT > 0.2f) {
                        s.hitT = lv.time; s.progress++;
                        int need = s.entrance == Secret.E_WALL ? 3 : 4;
                        float px = (b[0] + b[2]) / 2f, py = (b[1] + b[3]) / 2f;
                        lv.ps.burst(lv.rng, px, py, 0x9A927E, 7, 70, 0.5f, 2, 380, false);
                        Snd.sfxv("hit_stone", 0.7f);
                        lv.shake(1.5f, 0.1f);
                        if (s.progress >= need) reveal(s);
                        else if (s.progress == need - 1) lv.text(px, b[1] - 8, "...", 0xC8C0B0, false);
                    }
                }
                case Secret.E_FLOOR -> {
                    if (overlap(rx, ry, rw, rh, b[0], b[1] - 2, b[2] - b[0], b[3] - b[1] + 2) && lv.time - s.hitT > 0.15f) { s.hitT = lv.time; s.progress = Math.min(3, s.progress + 1); }
                }
                case Secret.E_LEVER -> {
                    float[] w = s.sw.get(0);
                    if (overlap(rx, ry, rw, rh, w[0] - 11, w[1] - 28, 22, 30) && lv.time - s.hitT > 0.3f) {
                        s.hitT = lv.time; s.lit[0] = 1f; s.progress = 1;
                        Snd.sfx("block", 0.8f);
                        reveal(s);
                    }
                }
                case Secret.E_SYMBOLS, Secret.E_RUNES -> {
                    if (s.seqT > 0) break;
                    for (float[] w : s.sw) if (overlap(rx, ry, rw, rh, w[0] - 11, w[1] - 28, 22, 30) && lv.time - s.hitT > 0.25f) { s.hitT = lv.time; press(s, (int) w[2]); break; }
                }
                default -> { }
            }
        }
    }

    /** La baldosa es parte de una entrada de suelo aun sin descubrir: se dibuja como roca normal con grietas (no como losa rompible). */
    boolean hides(int tx, int ty) {
        for (Secret s : list) {
            if (s.open || s.revealing || s.entrance != Secret.E_FLOOR) continue;
            for (int[] d : s.door) if (d[0] == tx && d[1] == ty) return true;
        }
        return false;
    }

    /** Se ha roto una baldosa rompible: si era la entrada de una camara, se descubre. */
    void onBreak(int tx, int ty) {
        for (Secret s : list) {
            if (s.open || s.revealing || s.entrance != Secret.E_FLOOR) continue;
            for (int[] d : s.door) if (d[0] == tx && d[1] == ty) { reveal(s); return; }
        }
    }

    private static boolean overlap(float ax, float ay, float aw, float ah, float bx, float by, float bw, float bh) {
        return ax < bx + bw && ax + aw > bx && ay < by + bh && ay + ah > by;
    }

    private void press(Secret s, int k) {
        s.lit[k] = 1f;
        if (s.order[s.progress] == k) {
            s.progress++;
            Snd.sfxv("altar_bless", 0.5f + 0.15f * s.progress);
            float[] w = s.sw.get(k);
            lv.ps.burst(lv.rng, w[0], w[1] - 12, symCol(s, k), 8, 60, 0.5f, 2, -20, true);
            if (s.progress >= s.order.length) reveal(s);
        } else {
            s.progress = 0; s.failT = 0.7f;
            Snd.sfx("ui_error", 0.6f);
            float[] w = s.sw.get(k);
            lv.ps.burst(lv.rng, w[0], w[1] - 12, 0x884444, 8, 60, 0.4f, 2, 200, false);
            if (s.entrance == Secret.E_RUNES) s.seqT = 0.02f;   // vuelve a mostrar la secuencia
        }
    }

    static int symCol(Secret s, int k) { return s.entrance == Secret.E_RUNES ? (k == 0 ? 0xFF6A5A : k == 1 ? 0x6AFF8A : 0x6AA8FF) : 0xFFD25A; }

    // ------------------------------------------------------------------ actualizacion
    void update(float dt) {
        t += dt;
        Player pl = lv.pl;
        for (int i = 0; i < list.size(); i++) {
            Secret s = list.get(i);
            for (int k = 0; k < 4; k++) if (s.lit[k] > 0) s.lit[k] = Math.max(s.entrance == Secret.E_RUNES || s.open ? 0.0f : 0f, s.lit[k] - dt * 1.4f);
            if (s.failT > 0) s.failT -= dt;
            if (s.seqT > 0) {
                s.seqT += dt;
                int step = (int) ((s.seqT - 0.5f) / 0.6f);
                if (s.seqT > 0.5f && step >= 0 && step < s.order.length && ((s.seqT - 0.5f) % 0.6f) < dt + 0.001f) { s.lit[s.order[step]] = 1f; Snd.sfxv("altar_bless", 0.45f + 0.1f * step); }
                if (s.seqT > 0.5f + 0.6f * s.order.length + 0.3f) s.seqT = 0;
            }
            if (s.revealing) {
                s.openT = Math.min(1f, s.openT + dt / 0.9f);
                if (s.openT >= 0.45f && s.rewardProp != null && s.rewardProp.hidden && (s.challenge != Secret.C_GUARD || s.rewardOut)) { s.rewardProp.hidden = false; sparkle(s.rwX, s.rwY - 10); }
                if (s.openT >= 1f) { s.revealing = false; s.open = true; }
            }
            if (!s.open && !s.revealing) {
                int[] b = box[i];
                float mx = (b[0] + b[2]) / 2f;
                switch (s.entrance) {
                    case Secret.E_ILLUSION, Secret.E_WATERFALL, Secret.E_CURTAIN -> {
                        boolean near = s.family == 0 ? Math.abs(pl.x - mx) < 40 && pl.y > b[1] - 6 && pl.y < b[1] + 26
                                : Math.abs(pl.x - mx) < 15 && pl.y > b[1] && pl.y <= b[3] + 4;
                        if (near) reveal(s);
                    }
                    case Secret.E_SKILL -> {
                        float dx = pl.x - s.crX, dy = pl.y - s.crY;
                        if ((pl.state == Player.SKILL || pl.state == Player.ULT) && dx * dx + dy * dy < 120 * 120) reveal(s);
                        else if (!s.hinted && dx * dx + dy * dy < 56 * 56) { s.hinted = true; lv.text(s.crX, s.crY - 46, "¿Reaccionará a una habilidad?", 0xA8E0FF, false); }
                    }
                    case Secret.E_RUNES -> {
                        if (s.seqT <= 0 && s.progress == 0 && s.failT <= 0 && !s.seqShown) {
                            for (float[] w : s.sw) if (Math.abs(pl.x - w[0]) < 70 && Math.abs(pl.y - w[1]) < 40) { s.seqT = 0.02f; s.seqShown = true; break; }
                        }
                    }
                    default -> { }
                }
            }
            if (s.open || s.revealing) inside(s, pl);
        }
    }

    private void inside(Secret s, Player pl) {
        int tx = (int) (pl.x / Room.TS), ty = (int) ((pl.y - 2) / Room.TS);
        boolean in = s.contains(tx, ty) && s.openT >= 0.7f;
        if (!s.entered && in) {
            s.entered = true;
            if (s.challenge == Secret.C_GUARD && s.reward != Secret.R_TREASURE && s.guardian == null) spawnGuardian(s);
            else if (s.challenge == Secret.C_NONE || s.reward == Secret.R_TREASURE) claim(s);
        }
        if (s.guardian != null && !s.rewardOut && !s.guardian.alive) { s.rewardOut = true; if (s.rewardProp != null) { s.rewardProp.hidden = false; sparkle(s.rwX, s.rwY - 10); } claimLoot(s); lv.text(s.rwX, s.rwY - 40, "¡Guardián vencido!", 0xFFD25A, true); Snd.sfx("secret", 0.9f); }
        if (s.challenge == Secret.C_NONE || s.challenge == Secret.C_PLAT) s.rewardOut = true;
    }

    private void claim(Secret s) {
        if (s.reward == Secret.R_TREASURE || s.reward == Secret.R_STASH) claimLoot(s);
    }

    /** Sala del tesoro / provisiones: lluvia de recursos. */
    private void claimLoot(Secret s) {
        if (s.looted) return;
        int stage = lv.rs.stage;
        float x = (s.rx0 + s.rx1 + 1) * Room.TS / 2f, y = (s.family == 1 ? (s.ry1 + 1) : s.ry1) * Room.TS - 24;
        if (s.reward == Secret.R_TREASURE) {
            s.looted = true;
            lv.rs.secretsFound++;
            lv.text(x, y - 30, "¡Sala del tesoro!", 0xFFD25A, true);
            lv.flash(0xFFE8A0, 0.25f);
            for (int k = 0; k < 4; k++) {
                final int kk = k;
                lv.later(0.12f + 0.25f * k, () -> {
                    lv.dropGold(x + (kk - 1.5f) * 10, y, Math.round((60 + 18 * stage) * lv.rs.stats.goldMul));
                    Snd.sfxv("pick_gold", 0.8f);
                    lv.ps.burst(lv.rng, x, y, 0xFFD25A, 12, 90, 0.7f, 2, 100, true);
                });
            }
            lv.later(1.2f, () -> lv.dropSouls(x, y, 8 + 3 * stage));
            if (lv.rng.chance(0.5f)) lv.later(1.4f, () -> lv.drop(Pickup.POTION, x, y, 1));
        } else if (s.reward == Secret.R_STASH) {
            s.looted = true;
            lv.rs.secretsFound++;
            lv.text(x, y - 30, "¡Provisiones olvidadas!", 0x9FE0A0, true);
            lv.drop(Pickup.HEART, x - 8, y, 1);
            lv.later(0.2f, () -> lv.drop(Pickup.HEART, x + 8, y, 1));
            lv.later(0.4f, () -> lv.drop(Pickup.POTION, x, y, 1));
            lv.later(0.6f, () -> lv.dropSouls(x, y, 14 + 4 * stage));
            lv.later(0.8f, () -> lv.dropGold(x, y, Math.round((40 + 10 * stage) * lv.rs.stats.goldMul)));
            lv.ps.burst(lv.rng, x, y, 0x9FE0A0, 14, 80, 0.8f, 2, -20, true);
        }
    }

    private void spawnGuardian(Secret s) {
        String name = null;
        List<String> pool = new ArrayList<>();
        for (Room.Spawn sp : room.spawns) if (!RoomCheck.isFlyer(sp.enemy) && EnemyDef.get(sp.enemy) != null) pool.add(sp.enemy);
        if (pool.isEmpty()) for (String n : lv.biome.enemies) if (!RoomCheck.isFlyer(n) && EnemyDef.get(n) != null) pool.add(n);
        if (!pool.isEmpty()) name = pool.get(lv.rng.i(pool.size()));
        if (name == null) { s.guardian = null; s.challenge = Secret.C_NONE; s.rewardOut = true; claim(s); return; }
        Enemy e = new Enemy(EnemyDef.get(name), true, lv.rs.enemyHpMul() * 1.15f, lv.rs.enemyDmgMul());
        e.guardian = true;
        e.x = (s.rx0 + s.rx1 + 1) * Room.TS / 2f + 20; e.y = (s.family == 1 ? (s.ry1 + 1) : s.ry1) * Room.TS;
        e.home = e.x;
        lv.enemies.add(e);
        s.guardian = e;
        lv.text(e.x, e.y - 60, "¡Un guardián!", 0xFF8A6A, true);
        Snd.sfx("secret", 0.7f);
        lv.shake(3f, 0.25f);
    }

    private void sparkle(float x, float y) {
        lv.ps.burst(lv.rng, x, y, 0xFFE8A0, 18, 90, 0.8f, 2, -30, true);
        lv.fx("fx_star", "burst", x, y, 0.8f, 0xFFE8A0, Platform.ADD | Platform.TINT);
    }

    // ------------------------------------------------------------------ revelado
    void reveal(Secret s) {
        if (s.open || s.revealing) return;
        s.revealing = true; s.openT = 0;
        int idx = list.indexOf(s);
        int[] b = box[idx];
        float px = (b[0] + b[2]) / 2f, py = (b[1] + b[3]) / 2f;
        for (int[] d : s.door) room.set(d[0], d[1], Room.AIR);
        lv.clearBreakHp();
        for (int[] d : torches.get(idx)) lv.animDeco.add(d);
        Snd.sfx("secret", 1f);
        Snd.sfxv("explosion_small", 0.5f);
        lv.shake(4f, 0.4f);
        lv.ps.burst(lv.rng, px, py, 0xB09A70, 22, 120, 0.8f, 3, 420, false);
        lv.ps.burst(lv.rng, px, py, 0x6A5A48, 12, 80, 0.9f, 2, 380, false);
        lv.fx("fx_dust", "land", px, b[3] - 2, 1.4f, 0, 0);
        for (int k = 0; k < 8; k++) lv.ps.spawn(px + lv.rng.f(-10, 10), b[1] - 4, lv.rng.f(-14, 14), lv.rng.f(0, 30), 0.9f, 3, 400, 0x8A8478, false);
        for (float[] w : s.sw) { /* piedras de simbolos: brillan todas */ s.lit[(int) w[2]] = 1f; }
        lv.text(px, b[1] - 18, "¡Pasadizo secreto!", 0xE8D8FF, true);
        lv.rs.secretsFound += 0;
    }

    // ------------------------------------------------------------------ dibujo
    /** Sobre la sala horneada: camara abierta + losa que se aparta. */
    void renderBase(Platform.Gfx g) {
        if (room.bakedOpen == null) return;
        for (int i = 0; i < list.size(); i++) {
            Secret s = list.get(i);
            if (!s.open && !s.revealing) continue;
            int[] r = s.drawRect(room, 1);
            int sx = r[0] * Room.TS, sy = r[1] * Room.TS, w = (r[2] - r[0] + 1) * Room.TS, h = (r[3] - r[1] + 1) * Room.TS;
            float a = s.open ? 1f : s.openT * s.openT * (3 - 2 * s.openT);
            g.image(room.bakedOpen, sx, sy, w, h, sx, sy, w, h, 0, 0, a);
            if (s.revealing && s.openT < 1f) {   // la losa se aparta y se desvanece
                int[] b = box[i];
                float k = s.openT;
                float ox = s.horizontalDoor ? k * 22f : 0f, oy = s.horizontalDoor ? 0f : -k * 26f;
                g.image(room.baked, b[0], b[1], b[2] - b[0], b[3] - b[1], b[0] + ox, b[1] + oy, b[2] - b[0], b[3] - b[1], 0, 0, 1f - k);
            }
        }
    }

    /** Decorado de las entradas, pistas e interruptores (detras de jugador y props). */
    void renderScenery(Platform.Gfx g) {
        for (int i = 0; i < list.size(); i++) {
            Secret s = list.get(i);
            int[] b = box[i];
            float w = b[2] - b[0], h = b[3] - b[1], mx = b[0] + w / 2f;
            boolean closed = !s.open && !s.revealing;
            float fade = closed ? 1f : (s.revealing ? 1f - s.openT : 0f);
            switch (s.entrance) {
                case Secret.E_WALL -> { if (closed) drawCracks(g, b, s.progress, 0.55f); }
                case Secret.E_ILLUSION -> { if (closed) shimmer(g, b); }
                case Secret.E_STATUE -> { if (fade > 0) drawStatue(g, mx, b[3], s.progress, fade); }
                case Secret.E_CURTAIN -> { if (fade > 0) drawCurtain(g, b, fade); }
                case Secret.E_WATERFALL -> drawWaterfall(g, b, closed ? 1f : 0.55f);
                case Secret.E_FLOOR -> { if (closed) drawFloorCracks(g, b, s.progress); }
                default -> { }
            }
            if (s.entrance == Secret.E_LEVER) drawLever(g, s);
            if (s.entrance == Secret.E_SYMBOLS || s.entrance == Secret.E_RUNES) drawStones(g, s, b);
            if (s.entrance == Secret.E_SKILL && (closed || s.revealing)) drawCrystal(g, s);
        }
    }

    private void drawCracks(Platform.Gfx g, int[] b, int hits, float a) {
        float x = b[0], y = b[1];
        int dark = ((int) (a * 150) << 24), light = ((int) (a * 55) << 24) | 0xFFFFFF;
        float[][] pts = {{3, 2}, {7, 9}, {5, 15}, {10, 22}, {8, 30}};
        for (int k = 0; k + 1 < pts.length; k++) {
            g.line(x + pts[k][0], y + pts[k][1], x + pts[k + 1][0], y + pts[k + 1][1], 1f, dark, false);
            g.line(x + pts[k][0] + 1, y + pts[k][1], x + pts[k + 1][0] + 1, y + pts[k + 1][1], 1f, light, false);
        }
        if (hits > 0) for (int k = 0; k < hits; k++) {
            g.line(x + 7, y + 9 + k * 5, x + 14 - k, y + 11 + k * 6, 1f, dark, false);
            g.line(x + 5, y + 15, x + 1, y + 20 + k * 3, 1f, dark, false);
        }
        if (lv.rng.chance(0.012f)) lv.ps.spawn(x + lv.rng.f(2, 14), y + lv.rng.f(4, 28), lv.rng.f(-3, 3), lv.rng.f(6, 14), 0.9f, 1, 60, 0xA09880, false);
    }

    private void drawFloorCracks(Platform.Gfx g, int[] b, int hits) {
        float x = b[0], y = b[1];
        int dark = 0x99000000, light = 0x36FFFFFF;
        float[][] a = {{4, 0}, {8, 6}, {6, 12}, {11, 19}};
        float[][] c = {{22, 0}, {18, 8}, {24, 15}, {20, 23}};
        for (float[][] pts : new float[][][]{a, c}) for (int k = 0; k + 1 < pts.length; k++) {
            g.line(x + pts[k][0], y + pts[k][1], x + pts[k + 1][0], y + pts[k + 1][1], 1f, dark, false);
            g.line(x + pts[k][0] + 1, y + pts[k][1], x + pts[k + 1][0] + 1, y + pts[k + 1][1], 1f, light, false);
        }
        g.line(x + 8, y + 6, x + 18, y + 8, 1f, dark, false);
        for (int k = 0; k < hits; k++) { g.line(x + 11, y + 19 - k * 2, x + 14 + k * 3, y + 27, 1f, dark, false); g.line(x + 18, y + 8, x + 16 - k * 2, y + 14 + k * 4, 1f, dark, false); }
        if (lv.rng.chance(0.01f)) lv.ps.spawn(x + lv.rng.f(2, 30), y + 1, lv.rng.f(-3, 3), lv.rng.f(6, 14), 0.9f, 1, 60, 0xA09880, false);
    }

    private void shimmer(Platform.Gfx g, int[] b) {
        float k = 0.5f + 0.5f * (float) Math.sin(t * 1.6f);
        int a = (int) (6 + 14 * k);
        g.rect(b[0], b[1], b[2] - b[0], b[3] - b[1], (a << 24) | 0xB0C0FF, true);
        float sy = b[1] + ((t * 14) % (b[3] - b[1]));
        g.rect(b[0] + 2, sy, b[2] - b[0] - 4, 1, ((int) (26 * k) << 24) | 0xD0E0FF, true);
    }

    private void drawStatue(Platform.Gfx g, float cx, float by, int hits, float a) {
        int A = (int) (255 * a) << 24;
        int base = A | 0x6E6C74, lit = A | 0x8C8A94, dk = A | 0x4A4850;
        g.rect(cx - 10, by - 5, 20, 5, dk, false);
        g.rect(cx - 8, by - 7, 16, 3, base, false);
        g.rect(cx - 6, by - 17, 12, 10, base, false);
        g.rect(cx - 7, by - 27, 14, 11, lit, false);
        g.rect(cx - 4, by - 35, 8, 8, lit, false);
        g.rect(cx - 2, by - 33, 1, 2, dk, false); g.rect(cx + 1, by - 33, 1, 2, dk, false);
        g.rect(cx - 11, by - 26, 4, 14, base, false);        // brazo / escudo
        g.rect(cx + 7, by - 40, 2, 30, A | 0x9A98A4, false); // lanza
        g.rect(cx - 7, by - 27, 14, 1, A | 0xB0AEBA, false);
        for (int k = 0; k < hits; k++) g.line(cx - 5 + k * 3, by - 26 + k * 2, cx - 1 + k * 3, by - 12 + k * 3, 1f, A | 0x2A2830, false);
    }

    /** Color de la cascada segun el bioma: agua, hielo, lava o sangre. */
    private int fallCol() {
        switch (lv.biome.key) { case "forja": return 0xFF8A2A; case "sangre": return 0xC02838; case "helado": return 0xBFEFFF; default: return 0x3A78B0; }
    }

    private int[] curtainCols() {
        switch (lv.biome.key) {
            case "bosque": return new int[]{0x3E7A3A, 0x2C5A2E};
            case "sangre": return new int[]{0x9A2230, 0x701A26};
            case "eclipse": return new int[]{0x4A3C9A, 0x362C7A};
            case "vacio": return new int[]{0x5A2C7A, 0x40205A};
            case "cazador": return new int[]{0x8A6A2F, 0x6B5022};
            default: return new int[]{0x8A2F3C, 0x6B2230};
        }
    }

    private void drawCurtain(Platform.Gfx g, int[] b, float a) {
        int A = (int) (255 * a) << 24;
        float x0 = b[0] - 2, w = b[2] - b[0] + 4, top = b[1] - 3, bot = b[3];
        g.rect(x0 - 1, top - 2, w + 2, 3, A | 0x4A3A2A, false);
        for (int k = 0; k < (int) w; k += 3) {
            float sway = (float) Math.sin(t * 1.4f + k * 0.6f) * 1.2f;
            int c = curtainCols()[(k / 3) & 1];
            g.rect(x0 + k + sway * 0.4f, top + 1, 3, bot - top - 1 + sway * 0.5f, A | c, false);
        }
        g.rect(x0, bot - 2, w, 2, A | 0xC8A050, false);
    }

    private void drawWaterfall(Platform.Gfx g, int[] b, float a) {
        float x0 = b[0] - 1, w = b[2] - b[0] + 2, top = b[1] - 22, bot = b[3];
        int fc = fallCol();
        g.rect(x0, top, w, bot - top, ((int) (80 * a) << 24) | fc, false);
        for (int k = 0; k < (int) w; k += 2) {
            float ph = (t * 90 + k * 17) % 28;
            for (int n = 0; n < 3; n++) {
                float y = top + ((ph + n * 28) % (bot - top));
                g.rect(x0 + k, y, 1, 7, ((int) (150 * a) << 24) | (fc | 0x707070), true);
            }
        }
        g.circle((b[0] + b[2]) / 2f, bot - 1, 7 + 2 * (float) Math.sin(t * 5), ((int) (60 * a) << 24) | (fc | 0x909090), true);
    }

    private void drawLever(Platform.Gfx g, Secret s) {
        float[] w = s.sw.get(0);
        float x = w[0], y = w[1];
        g.rect(x - 5, y - 20, 10, 12, 0xFF3C3A44, false);
        g.rect(x - 4, y - 19, 8, 10, 0xFF58565F, false);
        float ang = s.progress > 0 || s.open ? 0.9f : -0.9f;
        float hx = x + (float) Math.sin(ang) * 11, hy = y - 14 - (float) Math.cos(ang) * 11;
        g.line(x, y - 14, hx, hy, 2f, 0xFF9A7A4A, false);
        g.circle(hx, hy, 2.2f, s.progress > 0 ? 0xFF7AFF9A : 0xFFD04A4A, false);
    }

    private void drawStones(Platform.Gfx g, Secret s, int[] b) {
        boolean runes = s.entrance == Secret.E_RUNES;
        for (float[] w : s.sw) {
            int k = (int) w[2];
            float x = w[0], y = w[1];
            boolean got = s.open;
            if (s.order != null) for (int q = 0; q < s.progress; q++) if (s.order[q] == k) got = true;
            float lit = Math.max(s.lit[k], got ? 0.4f : 0f);
            if (s.failT > 0 && !runes) lit = 0;
            g.rect(x - 8, y - 22, 16, 22, 0xFF34323C, false);
            g.rect(x - 7, y - 21, 14, 20, 0xFF4E4C58, false);
            g.rect(x - 7, y - 21, 14, 2, 0xFF6A6876, false);
            int col = symCol(s, k);
            if (lit > 0) { UI.light(g, x, y - 12, 18 + 6 * lit, col, 0.55f * lit); }
            int gc = ((int) (60 + 195 * lit) << 24) | col;
            glyph(g, runes ? 3 : k, x, y - 12, 4.2f, gc, lit > 0);
        }
        // tablilla con el orden correcto (solo simbolos)
        if (!runes && s.order != null) {
            float tx = s.family == 1 ? (b[0] + b[2]) / 2f : s.cx - 42, ty = s.family == 1 ? b[1] - 26 : s.cy - 4;
            if (s.family == 0) { g.rect(tx - 14, ty - 22, 28, 22, 0xFF34323C, false); g.rect(tx - 13, ty - 21, 26, 20, 0xFF4A4854, false); }
            else g.rect(tx - 14, ty - 8, 28, 16, 0x44000000, false);
            for (int k = 0; k < s.order.length; k++) glyph(g, s.order[k], tx - 8 + k * 8, s.family == 0 ? ty - 11 : ty, 2.6f, s.open ? 0xFFD8C080 : 0xCC9A9AB0, false);
        }
    }

    static void glyph(Platform.Gfx g, int id, float x, float y, float r, int argb, boolean add) {
        switch (id) {
            case 0 -> { g.circle(x, y, r, argb, add); g.circle(x, y, r * 0.5f, (argb & 0xFF000000) >>> 1 << 0 & 0xFF000000 | 0x202028, false); }
            case 1 -> { g.line(x, y - r, x + r, y + r, 1.4f, argb, add); g.line(x + r, y + r, x - r, y + r, 1.4f, argb, add); g.line(x - r, y + r, x, y - r, 1.4f, argb, add); }
            case 2 -> { g.line(x, y - r, x + r, y, 1.4f, argb, add); g.line(x + r, y, x, y + r, 1.4f, argb, add); g.line(x, y + r, x - r, y, 1.4f, argb, add); g.line(x - r, y, x, y - r, 1.4f, argb, add); }
            default -> { g.line(x - r, y, x + r, y, 1.6f, argb, add); g.line(x, y - r, x, y + r, 1.6f, argb, add); g.circle(x, y, r * 0.45f, argb, add); }
        }
    }

    private void drawCrystal(Platform.Gfx g, Secret s) {
        float a = s.revealing ? 1f - s.openT : 1f;
        float x = s.crX, y = s.crY - 18 + (float) Math.sin(t * 2.2f) * 2;
        UI.light(g, x, y, 22 + 4 * (float) Math.sin(t * 3), 0x6EC8FF, 0.5f * a);
        int A = (int) (255 * a) << 24;
        g.line(x, y - 8, x + 5, y, 3f, A | 0x8AD8FF, false);
        g.line(x + 5, y, x, y + 8, 3f, A | 0x5AA8E8, false);
        g.line(x, y + 8, x - 5, y, 3f, A | 0x4A88C8, false);
        g.line(x - 5, y, x, y - 8, 3f, A | 0xB8F0FF, false);
        g.rect(x - 4, s.crY - 4, 8, 4, A | 0x4E4C58, false);
        if (lv.rng.chance(0.03f)) lv.ps.spawn(x + lv.rng.f(-6, 6), y + 6, lv.rng.f(-4, 4), -lv.rng.f(10, 24), 0.9f, 1, 0, 0xB8F0FF, true);
    }
}
