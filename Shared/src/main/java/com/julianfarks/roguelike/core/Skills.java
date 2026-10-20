package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** Las 30 habilidades y 10 definitivas de las clases, como lineas de tiempo de efectos. */
final class Skills {
    private Skills() {}

    // ------------------------------------------------------------------ utilidades
    private static float D(Level lv, Player p, float m) { return p.skillBase(lv) * m; }

    private static float gy(Level lv, Player p, float x) { return lv.groundBelow(x, p.y - 30); }

    private static float mx(Player p) {
        Anim a = p.sheet.anim("skill");
        return a.muzzleX(p.x, p.right);
    }

    private static float my(Player p) {
        Anim a = p.sheet.anim("skill");
        return a.muzzleY(p.y);
    }

    private static void aoe(Level lv, Player p, float x, float y, float r, float mult, float knock, int st, float sd, float sp) {
        lv.explosion(x, y, r, D(lv, p, mult), knock, st, sd, sp, true);
    }

    private static void pull(Level lv, float cx, float cy, float r, float strength) {
        for (Ent e : lv.enemiesIn(cx, cy, r)) {
            if (e instanceof Boss) continue;
            float d = cx - e.x;
            if (Math.abs(d) > 6) e.vx = Mth.sign(d) * strength;
        }
    }

    private static void rep(Level lv, int n, float interval, float first, java.util.function.IntConsumer c) {
        for (int i = 0; i < n; i++) {
            final int k = i;
            lv.later(first + i * interval, () -> c.accept(k));
        }
    }

    private static void beam(Level lv, String sheet, String anim, float x, float groundY, float cellH, float scale, int color) {
        lv.fxAdd(sheet, anim, x, groundY - cellH * scale / 2f + 2, scale, color);
    }

    private static Proj shot(Level lv, Player p, float x, float y, float ang, float spd, float dmg, String spr, int color) {
        Proj pr = lv.proj(x, y, (float) Math.cos(ang) * spd, (float) Math.sin(ang) * spd, dmg, true, spr, color);
        return pr;
    }

    private static Ent target(Level lv, Player p, float range) {
        Ent best = null; float bd = range;
        for (Ent e : lv.enemiesOnScreen()) {
            if (e instanceof Boss && ((Boss) e).invuln()) continue;
            float d = Mth.dist(p.x, p.cy(), e.cx(), e.cy());
            // preferir los del lado al que mira
            if ((e.x - p.x) * p.dir() < -20) d *= 1.6f;
            if (d < bd) { bd = d; best = e; }
        }
        return best;
    }

    private static List<Ent> screen(Level lv) { return new ArrayList<>(lv.enemiesOnScreen()); }

    private static float centerX(Level lv, Player p) {
        List<Ent> l = lv.enemiesOnScreen();
        if (l.isEmpty()) return p.x + p.dir() * 100;
        float s = 0; for (Ent e : l) s += e.x;
        return s / l.size();
    }

    // ------------------------------------------------------------------ politica de interrupcion
    /**
     * Habilidades de supervivencia/escape: su efecto se aplica en cuanto el jugador recibe un golpe durante la preparacion
     * (antes de calcular ese dano), asi la proteccion nunca se pierde por ser golpeado. Las demas habilidades (ofensivas) tienen una
     * preparacion interrumpible: si el golpe llega antes del momento de liberacion se cancelan y NO consumen enfriamiento.
     * Paladin: Alas de Egida · Sombra: Paso Sombra · Vegetal: Floracion · Tierra: Piel de Piedra · Astral: Paso Cosmico · Acero: Guardia de Acero.
     */
    static boolean committed(int cls, int idx) {
        switch (cls) {
            case 0: case 5: case 7: case 9: return idx == 1;
            case 1: return idx == 0;
            case 8: return idx == 2;
            default: return false;
        }
    }

    // ------------------------------------------------------------------ habilidades
    static void cast(Level lv, Player p, int idx) {
        switch (p.cls.id) {
            case 0: paladin(lv, p, idx); break;
            case 1: shadow(lv, p, idx); break;
            case 2: flame(lv, p, idx); break;
            case 3: storm(lv, p, idx); break;
            case 4: frost(lv, p, idx); break;
            case 5: verdant(lv, p, idx); break;
            case 6: blood(lv, p, idx); break;
            case 7: earth(lv, p, idx); break;
            case 8: astral(lv, p, idx); break;
            default: steel(lv, p, idx); break;
        }
    }

    static void ult(Level lv, Player p) {
        switch (p.cls.id) {
            case 0: ultPaladin(lv, p); break;
            case 1: ultShadow(lv, p); break;
            case 2: ultFlame(lv, p); break;
            case 3: ultStorm(lv, p); break;
            case 4: ultFrost(lv, p); break;
            case 5: ultVerdant(lv, p); break;
            case 6: ultBlood(lv, p); break;
            case 7: ultEarth(lv, p); break;
            case 8: ultAstral(lv, p); break;
            default: ultSteel(lv, p); break;
        }
    }

    // ---------------------------------------------------------------- Paladin
    private static void paladin(Level lv, Player p, int i) {
        int c = p.cls.color1;
        if (i == 0) {
            for (int k = -1; k <= 1; k++) {
                Proj pr = shot(lv, p, mx(p), my(p) + k * 3, k * 0.1f + (p.right ? 0 : (float) Math.PI), 320, D(lv, p, 1.0f), "holy", c);
                if (!p.right) { pr.vx = -(float) Math.abs(pr.vx); pr.vy = k * 30; } else pr.vy = k * 30;
                pr.pierce = 3; pr.life = 1.2f; pr.scale = 1.3f; pr.knock = 90;
            }
            lv.fxAdd("fx_ring", "pulse", mx(p), my(p), 0.4f, c);
        } else if (i == 1) {
            lv.healPlayer(lv.rs.stats.maxHp * 0.2f);
            p.shield = Math.min(70, p.shield + 35);
            lv.fxAdd("fx_shield", "bubble", p.x, p.y - 20, 1.5f, c);
            lv.fx("fx_heal", "rise", p.x, p.y - 14, 1.2f, 0, 0);
            lv.fxAdd("fx_ring", "pulse", p.x, p.y - 14, 0.9f, c);
            lv.ps.burst(lv.rng, p.x, p.y - 20, 0xFFF6C8, 24, 120, 0.7f, 2, -40, true);
        } else {
            p.vy = -380f; p.vx = p.dir() * 130f; p.onGround = false;
            lv.later(0.48f, () -> {
                float gyv = lv.groundBelow(p.x, p.y - 20);
                float px = p.x;
                aoe(lv, p, px, gyv - 12, 70, 2.1f, 200, -1, 0, 0);
                beam(lv, "fx_holy", "beam", px, gyv, 128, 1.1f, c);
                lv.fx("fx_dust", "land", px, gyv - 2, 2f, 0, 0);
                lv.shake(5f, 0.3f);
                for (int s = -1; s <= 1; s += 2) {
                    Proj w = lv.proj(px, gyv - 8, s * 250, 0, D(lv, p, 1.2f), true, "crescent", c);
                    w.special = 1; w.pierce = 5; w.life = 0.8f; w.scale = 1.5f;
                }
                Snd.sfx("sk_paladin_hit", 0.9f);
            });
        }
    }

    private static void ultPaladin(Level lv, Player p) {
        int c = p.cls.color1;
        float camCx = lv.camX + lv.viewW / 2;
        lv.flash(0xFFF6C8, 0.5f);
        lv.shake(4f, 1.2f);
        int n = 12;
        for (int i = 0; i < n; i++) {
            final int k = i;
            lv.later(i * 0.06f, () -> {
                float bx = lv.camX + (k + 0.5f) * lv.viewW / n;
                float g = lv.groundBelow(bx, p.y - 30);
                beam(lv, "fx_holy", "beam", bx, g, 128, 1.4f, c);
                lv.ps.burst(lv.rng, bx, g - 4, 0xFFF6C8, 5, 90, 0.5f, 2, 0, true);
            });
        }
        lv.later(0.55f, () -> {
            lv.flash(0xFFFFFF, 0.4f);
            for (Ent e : screen(lv)) {
                lv.damageEnemy(e, D(lv, p, 6f), false, Mth.sign(e.x - p.x) * 140, -120);
                lv.fx("fx_hit", "big", e.cx(), e.cy(), 1.3f, 0, 0);
                e.applyStatus(Ent.BURN, 3f, 6f);
            }
            lv.healPlayer(lv.rs.stats.maxHp * 0.3f);
            lv.fxAdd("fx_ring", "pulse", camCx, p.y - 40, 4f, 0xFFD25A);
            lv.shake(7f, 0.5f);
            Snd.sfx("sk_paladin_hit", 1f);
            lv.projs.removeIf(pr -> !pr.friendly);
        });
    }

    // ---------------------------------------------------------------- Asesino de sombras
    private static void shadow(Level lv, Player p, int i) {
        int c = p.cls.color1;
        if (i == 0) {
            Ent e = target(lv, p, 240);
            lv.fx("fx_tele", "out", p.x, p.y - 20, 1f, 0, 0);
            if (e != null) {
                float side = e.x >= p.x ? 1 : -1;
                float dest = e.x + side * 18;
                if (lv.solidAtPx(dest, e.y - 10)) dest = e.x - side * 18;
                if (lv.solidAtPx(dest, e.y - 10)) dest = e.x;
                p.x = dest; p.y = e.y - 0.5f; p.vy = 0; p.vx = 0;
                p.right = e.x >= p.x;
                float dmg = D(lv, p, 2.3f);
                boolean crit = lv.rng.chance(lv.rs.stats.critChance + 0.3f);
                if (crit) dmg *= lv.rs.stats.critMul;
                lv.damageEnemy(e, dmg * 1.5f, crit, p.dir() * 90, -60);
                lv.fx("fx_stab", "s1", e.cx() + (p.right ? -10 : 10), e.cy(), 1f, 0, 0).right = p.right;
                lv.fx("fx_hit", "crit", e.cx(), e.cy(), 1f, 0, 0);
                Snd.sfx("sk_shadow_hit", 0.9f);
                lv.hitstop(0.08f);
            } else {
                float d = 0;
                while (d < 90 && !lv.solidAtPx(p.x + p.dir() * (d + 8), p.y - 10)) d += 6;
                p.x += p.dir() * d;
            }
            p.invuln = Math.max(p.invuln, 0.45f);
            lv.fx("fx_tele", "in", p.x, p.y - 20, 1f, 0, 0);
            lv.ps.burst(lv.rng, p.x, p.y - 20, c, 18, 120, 0.5f, 2, 0, true);
        } else if (i == 1) {
            Ent e = target(lv, p, 160);
            float cx = e != null ? e.cx() : p.x + p.dir() * 40, cy = e != null ? e.cy() : p.y - 18;
            for (int k = 0; k < 5; k++) {
                final int kk = k;
                lv.later(k * 0.1f, () -> {
                    float ox = lv.rng.f(-14, 14), oy = lv.rng.f(-14, 14);
                    float ang = lv.rng.f(-0.6f, 0.6f);
                    FxObj f = lv.fxAdd("fx_shadow", "blade", cx + ox, cy + oy, 1.1f, c);
                    if (f != null) f.rot = ang + (kk % 2 == 0 ? 0 : 3.14f);
                    aoe(lv, p, cx + ox, cy + oy, 32, 0.95f, 70 * (kk % 2 == 0 ? 1 : -1), -1, 0, 0);
                    Snd.sfxv("swing_dagger_" + (1 + kk % 3), 0.7f);
                    lv.ps.burst(lv.rng, cx + ox, cy + oy, c, 5, 100, 0.25f, 2, 0, true);
                });
            }
        } else {
            FxObj f = lv.fxAdd("fx_whirl", "spin", p.x, p.y - 18, 1.0f, c);
            if (f != null) { f.loop = true; f.life = 1.3f; f.follow = p; f.foy = -18; }
            rep(lv, 6, 0.2f, 0.05f, k -> {
                aoe(lv, p, p.x, p.y - 16, 48, 0.75f, 100, -1, 0, 0);
                Snd.sfxv("swing_dagger_" + (1 + k % 3), 0.5f);
            });
        }
    }

    private static void ultShadow(Level lv, Player p) {
        int c = p.cls.color1;
        lv.freezeEnemies = 2.6f;
        Snd.sfx("time_stop", 1f);
        lv.flash(0x2A0A55, 0.7f);
        List<Ent> l = screen(lv);
        lv.fxAdd("fx_ring", "pulse", p.x, p.y - 20, 3f, c);
        for (int k = 0; k < l.size(); k++) {
            final Ent e = l.get(k);
            for (int j = 0; j < 3; j++) {
                final int jj = j;
                lv.later(0.35f + k * 0.12f + j * 0.12f, () -> {
                    FxObj f = lv.fxAdd("fx_shadow", "blade", e.cx() + lv.rng.f(-10, 10), e.cy() + lv.rng.f(-10, 10), 1.2f, c);
                    if (f != null) f.rot = lv.rng.f(0, 6.28f);
                    Snd.sfxv("swing_dagger_" + (1 + jj), 0.6f);
                });
            }
        }
        lv.later(2.0f, () -> {
            lv.flash(0xFFFFFF, 0.3f);
            for (Ent e : l) {
                if (!e.alive) continue;
                lv.damageEnemy(e, D(lv, p, 6f), true, Mth.sign(e.x - p.x) * 90, -80);
                lv.fx("fx_hit", "crit", e.cx(), e.cy(), 1.5f, 0, 0);
                lv.fx("fx_shadow", "puff", e.cx(), e.cy(), 1.4f, 0, 0);
            }
            lv.shake(6f, 0.5f);
            Snd.sfx("sk_shadow_hit", 1f);
        });
    }

    // ---------------------------------------------------------------- Llamas
    private static void flame(Level lv, Player p, int i) {
        int c = p.cls.color1;
        if (i == 0) {
            Proj pr = lv.proj(mx(p), my(p), p.dir() * 250, 0, D(lv, p, 1.9f), true, "fireball", c);
            pr.explode = 48; pr.status = Ent.BURN; pr.statusDur = 3.5f; pr.statusPow = 8f; pr.scale = 1.4f; pr.life = 1.6f;
            pr.explodeFx = "fx_explosion:a";
            lv.fxAdd("fx_fire", "burn", mx(p), my(p), 0.7f, c);
        } else if (i == 1) {
            for (int k = 0; k < 5; k++) {
                final int kk = k;
                lv.later(k * 0.07f, () -> {
                    float px = p.x + p.dir() * (34 + kk * 30);
                    float g = lv.groundBelow(px, p.y - 12);
                    beam(lv, "fx_fire", "pillar", px, g, 48, 1.15f, 0xFFFFFF);
                    Snd.sfxv("hit_fire", 0.5f);
                    for (int t = 0; t < 5; t++) lv.later(t * 0.3f, () -> aoe(lv, p, px, g - 14, 20, 0.45f, 20, Ent.BURN, 3f, 7f));
                });
            }
        } else {
            for (int k = 0; k < 8; k++) {
                final int kk = k;
                lv.later(k * 0.2f, () -> {
                    float px = p.x + p.dir() * (34 + kk * 12);
                    float g = lv.groundBelow(px, p.y - 12);
                    lv.fxAdd("fx_whirl", "spin", px, g - 26, 1.5f, c);
                    pull(lv, px, g - 20, 80, 110);
                    aoe(lv, p, px, g - 24, 42, 0.6f, 30, Ent.BURN, 3f, 7f);
                    Snd.sfxv("hit_fire", 0.4f);
                });
            }
        }
    }

    private static void ultFlame(Level lv, Player p) {
        int c = p.cls.color1;
        float dir = p.dir();
        lv.flash(0xFF8A2A, 0.4f);
        lv.shake(4f, 1.6f);
        Proj dr = lv.proj(p.x, p.y - 36, dir * 520, 0, D(lv, p, 1.5f), true, "fireball", 0xFFB040);
        dr.scale = 3.2f; dr.pierce = 999; dr.life = 1.4f; dr.passWalls = true; dr.status = Ent.BURN; dr.statusDur = 4f; dr.statusPow = 10f; dr.trail = true;
        Snd.sfx("explosion_big", 0.8f);
        for (int k = 0; k < 16; k++) {
            final int kk = k;
            lv.later(0.05f + k * 0.045f, () -> {
                float px = p.x + dir * (26 + kk * 32);
                if (px < 16 || px > lv.room.pixW - 16) return;
                float g = lv.groundBelow(px, p.y - 12);
                beam(lv, "fx_fire", "pillar", px, g, 48, 1.7f, 0xFFFFFF);
                aoe(lv, p, px, g - 24, 40, 2.0f, 140, Ent.BURN, 4f, 10f);
                if (kk % 2 == 0) { lv.shake(3f, 0.1f); Snd.sfxv("explosion_small", 0.4f); }
            });
        }
        lv.later(0.95f, () -> {
            float fx = Mth.clamp(p.x + dir * 520, 40, lv.room.pixW - 40);
            lv.fxAdd("fx_explosion", "b", fx, p.y - 40, 3.5f, c);
            lv.flash(0xFFE0A0, 0.35f);
            lv.shake(8f, 0.6f);
            for (Ent e : screen(lv)) { lv.damageEnemy(e, D(lv, p, 3f), false, Mth.sign(e.x - p.x) * 160, -100); e.applyStatus(Ent.BURN, 4f, 10f); }
            Snd.sfx("explosion_big", 1f);
        });
    }

    // ---------------------------------------------------------------- Tempestad
    private static void storm(Level lv, Player p, int i) {
        int c = p.cls.color1;
        if (i == 0) {
            p.dash(p.dir(), 600f, 0.2f, 2.0f, Ent.SHOCK, 2f, false);
            lv.fxAdd("fx_lightning", "ground", p.x, p.y - 14, 0.5f, c);
            lv.ps.burst(lv.rng, p.x, p.y - 16, c, 16, 160, 0.3f, 2, 0, true);
        } else if (i == 1) {
            Ent e = target(lv, p, 280);
            if (e == null) {
                float ex = p.x + p.dir() * 150;
                lv.lightning(mx(p), my(p), ex, p.y - 20);
                aoe(lv, p, ex, p.y - 20, 40, 1.4f, 80, Ent.SHOCK, 1.5f, 0);
            } else {
                lv.lightning(mx(p), my(p), e.cx(), e.cy());
                lv.damageEnemy(e, D(lv, p, 1.7f), false, p.dir() * 90, -50);
                e.applyStatus(Ent.SHOCK, 1.5f, 0);
                lv.chain(e, D(lv, p, 1.3f), 5);
            }
            Snd.sfx("hit_shock", 0.8f);
        } else {
            lv.fx("fx_smoke", "big", p.x, p.y - 120, 1.7f, 0x4060A0, Platform.TINT).life = 2.1f;
            rep(lv, 9, 0.22f, 0.15f, k -> {
                Ent e = k % 2 == 0 ? target(lv, p, 300) : null;
                float sx = e != null ? e.x : Mth.clamp(p.x + lv.rng.f(-150, 150), 40, lv.room.pixW - 40);
                float g = lv.groundBelow(sx, (e != null ? e.y : p.y) - 30);
                beam(lv, "fx_lightning", "bolt", sx, g, 128, 1.0f, c);
                aoe(lv, p, sx, g - 16, 30, 1.35f, 60, Ent.SHOCK, 1.5f, 0);
                lv.shake(2f, 0.1f);
                Snd.sfxv("hit_shock", 0.55f);
                lv.ps.burst(lv.rng, sx, g - 4, c, 8, 120, 0.3f, 2, 0, true);
            });
        }
    }

    private static void ultStorm(Level lv, Player p) {
        int c = p.cls.color1;
        lv.flash(0x6090FF, 0.4f);
        lv.fx("fx_smoke", "big", lv.camX + lv.viewW / 2, 40, 5f, 0x303860, Platform.TINT).life = 2.8f;
        rep(lv, 16, 0.12f, 0.2f, k -> {
            Ent e = k % 3 == 0 ? target(lv, p, 400) : null;
            float sx = e != null ? e.x : lv.camX + lv.rng.f(20, lv.viewW - 20);
            float g = lv.groundBelow(sx, (e != null ? e.y : p.y) - 30);
            beam(lv, "fx_lightning", "bolt", sx, g, 128, 1.2f, c);
            aoe(lv, p, sx, g - 16, 36, 1.6f, 80, Ent.SHOCK, 2f, 0);
            lv.shake(3f, 0.12f);
            Snd.sfxv("hit_shock", 0.5f);
        });
        lv.later(2.4f, () -> {
            float cx = centerX(lv, p);
            float g = lv.groundBelow(cx, p.y - 30);
            lv.flash(0xFFFFFF, 0.5f);
            beam(lv, "fx_lightning", "bolt", cx, g, 128, 3.2f, 0xFFFFFF);
            beam(lv, "fx_lightning", "bolt", cx, g, 128, 2.6f, c);
            lv.explosion(cx, g - 20, 130, D(lv, p, 7f), 220, Ent.SHOCK, 3f, 0, true);
            for (Ent e : screen(lv)) lv.damageEnemy(e, D(lv, p, 2f), false, 0, -60);
            lv.shake(9f, 0.7f);
            Snd.sfx("explosion_big", 1f);
        });
    }

    // ---------------------------------------------------------------- Escarcha
    private static void frost(Level lv, Player p, int i) {
        int c = p.cls.color1;
        if (i == 0) {
            for (int k = -2; k <= 2; k++) {
                float ang = (p.right ? 0 : (float) Math.PI) + (p.right ? k : -k) * 0.2f;
                Proj pr = shot(lv, p, mx(p), my(p), ang, 290, D(lv, p, 0.95f), "iceshard", c);
                pr.pierce = 1; pr.life = 1.1f;
                pr.status = k == 0 ? Ent.FREEZE : Ent.SLOW; pr.statusDur = k == 0 ? 1.5f : 3f; pr.statusPow = 0;
            }
            lv.fxAdd("fx_ring", "pulse", mx(p), my(p), 0.5f, c);
        } else if (i == 1) {
            Ent e = target(lv, p, 260);
            if (e == null) {
                float ex = p.x + p.dir() * 90;
                lv.fx("fx_ice", "burst", ex, p.y - 20, 1f, 0, 0);
                aoe(lv, p, ex, p.y - 20, 50, 1.5f, 40, Ent.FREEZE, 1.5f, 0);
            } else {
                e.applyStatus(Ent.FREEZE, 2.6f, 0);
                lv.fx("fx_ice", "burst", e.cx(), e.cy(), 1.1f, 0, 0);
                Snd.sfx("hit_ice", 0.9f);
                lv.later(2.6f, () -> {
                    if (!e.alive) return;
                    float ex = e.cx(), ey = e.cy();
                    lv.fx("fx_ice", "burst", ex, ey, 1.7f, 0, 0);
                    aoe(lv, p, ex, ey, 56, 3.2f, 130, Ent.SLOW, 3f, 0);
                    Snd.sfx("hit_ice", 1f);
                    lv.shake(3f, 0.15f);
                });
            }
        } else {
            final float bx = Mth.clamp(p.x + p.dir() * 70, 30, lv.room.pixW - 30);
            FxObj f = lv.fxAdd("fx_whirl", "spin", bx, p.y - 30, 1.7f, c);
            if (f != null) { f.loop = true; f.life = 2.2f; }
            rep(lv, 10, 0.21f, 0.1f, k -> {
                pull(lv, bx, p.y - 24, 95, 100);
                aoe(lv, p, bx, p.y - 24, 52, 0.45f, 20, k % 4 == 3 ? Ent.FREEZE : Ent.SLOW, 1.2f, 0);
                lv.ps.burst(lv.rng, bx + lv.rng.f(-20, 20), p.y - 24, 0xDFF8FF, 4, 80, 0.4f, 2, 0, true);
            });
            Snd.sfx("sk_frost_hit", 0.5f);
        }
    }

    private static void ultFrost(Level lv, Player p) {
        int c = p.cls.color1;
        lv.flash(0xBFEFFF, 0.6f);
        Snd.sfx("time_stop", 0.8f);
        lv.fxAdd("fx_ring", "pulse", p.x, p.y - 20, 4f, c);
        List<Ent> l = screen(lv);
        for (Ent e : l) {
            e.applyStatus(Ent.FREEZE, 3.4f, 0);
            e.applyStatus(Ent.SLOW, 6f, 0);
            lv.fx("fx_ice", "burst", e.cx(), e.cy(), 1.1f, 0, 0);
        }
        lv.projs.removeIf(pr -> !pr.friendly);
        lv.later(3.1f, () -> {
            lv.flash(0xFFFFFF, 0.4f);
            for (Ent e : l) {
                if (!e.alive) continue;
                lv.damageEnemy(e, D(lv, p, 6.5f), true, 0, -80);
                lv.fx("fx_ice", "burst", e.cx(), e.cy(), 1.8f, 0, 0);
            }
            lv.shake(7f, 0.5f);
            Snd.sfx("hit_ice", 1f);
            Snd.sfx("explosion_big", 0.7f);
        });
    }

    // ---------------------------------------------------------------- Esmeralda
    private static void verdant(Level lv, Player p, int i) {
        int c = p.cls.color1;
        if (i == 0) {
            for (int k = 0; k < 6; k++) {
                final int kk = k;
                lv.later(k * 0.07f, () -> {
                    float px = p.x + p.dir() * (28 + kk * 26);
                    float g = lv.groundBelow(px, p.y - 12);
                    beam(lv, "fx_thorn", "vine", px, g, 48, 1.1f, 0xFFFFFF);
                    aoe(lv, p, px, g - 18, 18, 0.85f, 40, Ent.SLOW, 3f, 0);
                    Snd.sfxv("hit_flesh_1", 0.4f);
                });
            }
        } else if (i == 1) {
            lv.healPlayer(lv.rs.stats.maxHp * 0.12f);
            p.regenT = 4.5f; p.regenRate = lv.rs.stats.maxHp * 0.07f;
            lv.fx("fx_thorn", "bloom", p.x, p.y - 22, 1.2f, 0, 0);
            lv.fx("fx_heal", "rise", p.x, p.y - 14, 1.2f, 0, 0);
            lv.ps.burst(lv.rng, p.x, p.y - 20, c, 24, 110, 0.9f, 2, -20, true);
        } else {
            List<Ent> l = lv.enemiesIn(p.x, p.cy(), 170);
            float fx = p.x + p.dir() * 36;
            for (Ent e : l) {
                e.applyStatus(Ent.ROOT, 2.6f, 0);
                float g = lv.groundBelow(e.x, e.y - 12);
                beam(lv, "fx_thorn", "vine", e.x, g, 48, 1.1f, 0xFFFFFF);
                lv.damageEnemy(e, D(lv, p, 1.0f), false, 0, 0);
            }
            rep(lv, 5, 0.08f, 0, k -> { for (Ent e : l) if (e.alive && !(e instanceof Boss)) e.x = Mth.approach(e.x, fx, 9f); });
            Snd.sfx("sk_verdant_hit", 0.8f);
        }
    }

    private static void ultVerdant(Level lv, Player p) {
        int c = p.cls.color1;
        float tx = Mth.clamp(p.x + p.dir() * 40, 40, lv.room.pixW - 40);
        float g = lv.groundBelow(tx, p.y - 30);
        lv.flash(0xC8FF9A, 0.4f);
        lv.shake(3f, 1.4f);
        FxObj f = lv.fx("fx_thorn", "bloom", tx, g - 70, 3.6f, 0, 0);
        if (f != null) { f.alpha = 0.95f; }
        for (Ent e : screen(lv)) e.applyStatus(Ent.ROOT, 4f, 0);
        rep(lv, 8, 0.15f, 0.1f, k -> {
            for (Ent e : lv.enemiesOnScreen()) {
                float eg = lv.groundBelow(e.x, e.y - 12);
                if (k % 3 == 0) beam(lv, "fx_thorn", "vine", e.x, eg, 48, 1.1f, 0xFFFFFF);
            }
        });
        lv.later(1.4f, () -> {
            lv.flash(0xFFFFFF, 0.4f);
            for (Ent e : screen(lv)) { lv.damageEnemy(e, D(lv, p, 4.5f), false, Mth.sign(e.x - tx) * 100, -90); lv.fx("fx_hit", "big", e.cx(), e.cy(), 1.2f, 0, 0); }
            lv.healPlayer(lv.rs.stats.maxHp * 0.4f);
            lv.fx("fx_heal", "rise", p.x, p.y - 14, 2f, 0, 0);
            lv.fxAdd("fx_ring", "pulse", tx, g - 40, 4f, c);
            lv.ps.burst(lv.rng, tx, g - 60, c, 60, 220, 1f, 3, 0, true);
            lv.shake(6f, 0.5f);
            Snd.sfx("heal", 1f);
        });
    }

    // ---------------------------------------------------------------- Segador carmesi
    private static void blood(Level lv, Player p, int i) {
        int c = p.cls.color1;
        if (i == 0) {
            p.dash(p.dir(), 520f, 0.18f, 1.3f, Ent.BLEED, 3f, true);
            for (int k = 0; k < 2; k++) {
                final int kk = k;
                lv.later(0.2f + k * 0.12f, () -> {
                    float fx = p.x + p.dir() * 26;
                    lv.fxAdd("fx_slash_big", "s" + (kk + 2), fx, p.y - 20, 0.9f, c).right = p.right;
                    int n = lv.explosion(fx, p.y - 18, 40, D(lv, p, 1.0f), 90 * p.dir(), Ent.BLEED, 3f, 5f, true);
                    if (n > 0) lv.healPlayer(lv.rs.stats.maxHp * 0.03f * n);
                    Snd.sfxv("swing_scythe_" + (kk + 2), 0.8f);
                });
            }
        } else if (i == 1) {
            float tot = 0;
            for (Ent e : lv.enemiesIn(p.x, p.cy(), 135)) {
                float dmg = D(lv, p, 1.6f);
                lv.lines.add(new float[]{p.x, p.cy(), e.cx(), e.cy(), 0.55f, 0xC4122C});
                lv.damageEnemy(e, dmg, false, 0, -30);
                e.applyStatus(Ent.BLEED, 3f, 5f);
                tot += dmg;
                for (int k = 0; k < 8; k++) lv.ps.spawn(e.cx(), e.cy(), (p.x - e.cx()) * 2.5f + lv.rng.f(-30, 30), (p.cy() - e.cy()) * 2.5f + lv.rng.f(-30, 30), 0.45f, 2, 0, 0xFF3050, true);
            }
            lv.healPlayer(tot * 0.25f + 2);
            lv.fx("fx_blood", "mist", p.x, p.y - 20, 1.3f, 0, 0);
            lv.fxAdd("fx_ring", "pulse", p.x, p.y - 20, 1.4f, c);
        } else {
            FxObj f = lv.fxAdd("fx_whirl", "spin", p.x, p.y - 18, 1.15f, c);
            if (f != null) { f.loop = true; f.life = 2.1f; f.follow = p; f.foy = -18; }
            rep(lv, 10, 0.2f, 0.05f, k -> {
                int n = lv.explosion(p.x, p.y - 18, 48, D(lv, p, 0.7f), 80, Ent.BLEED, 2.5f, 5f, true);
                if (n > 0) lv.healPlayer(lv.rs.stats.maxHp * 0.015f * n);
                Snd.sfxv("swing_scythe_" + (1 + k % 3), 0.5f);
            });
        }
    }

    private static void ultBlood(Level lv, Player p) {
        int c = p.cls.color1;
        lv.flash(0x500010, 0.8f);
        float camCx = lv.camX + lv.viewW / 2;
        lv.fxAdd("fx_ring", "pulse", camCx, 80, 5f, c);
        lv.shake(3f, 1.0f);
        Snd.sfx("heartbeat", 1f);
        lv.later(0.7f, () -> {
            lv.flash(0xFF2040, 0.4f);
            lv.fxAdd("fx_slash_big", "s3", p.x, p.y - 30, 3f, c);
            lv.fxAdd("fx_slash_big", "s2", p.x, p.y - 30, 3f, 0xFF6A7C).right = false;
            float heal = 0;
            for (Ent e : screen(lv)) {
                float dmg = D(lv, p, 5.5f);
                lv.damageEnemy(e, dmg, true, Mth.sign(e.x - p.x) * 120, -90);
                e.applyStatus(Ent.BLEED, 5f, 8f);
                lv.fx("fx_blood", "splat", e.cx(), e.cy(), 1.3f, 0, 0);
                heal += 0.03f * lv.rs.stats.maxHp;
            }
            lv.healPlayer(lv.rs.stats.maxHp * 0.2f + heal);
            lv.shake(8f, 0.5f);
            Snd.sfx("hit_blood", 1f);
        });
    }

    // ---------------------------------------------------------------- Roca
    private static void earth(Level lv, Player p, int i) {
        int c = p.cls.color1;
        if (i == 0) {
            for (int k = 0; k < 2; k++) {
                final int kk = k;
                lv.later(0.05f + k * 0.09f, () -> {
                    float px = p.x + p.dir() * (34 + kk * 34);
                    float g = lv.groundBelow(px, p.y - 12);
                    beam(lv, "fx_rock", "pillar", px, g, 64, 1.2f, 0xFFFFFF);
                    aoe(lv, p, px, g - 24, 30, 2.0f, 240 * p.dir(), -1, 0, 0);
                    for (Ent e : lv.enemiesIn(px, g - 24, 30)) if (!(e instanceof Boss)) e.vy = -280;
                    lv.shake(4f, 0.2f);
                    Snd.sfx("sk_earth_hit", 0.8f);
                    lv.ps.burst(lv.rng, px, g - 4, 0xA08060, 10, 130, 0.5f, 3, 300, false);
                });
            }
        } else if (i == 1) {
            p.skinT = 7f;
            p.shield = Math.min(60, p.shield + 20);
            lv.fxAdd("fx_shield", "bubble", p.x, p.y - 20, 1.5f, c);
            lv.fxAdd("fx_ring", "pulse", p.x, p.y - 12, 1f, c);
            lv.ps.burst(lv.rng, p.x, p.y - 16, 0xC98B3C, 24, 100, 0.6f, 3, 200, false);
        } else {
            p.vy = -340f; p.vx = p.dir() * 70f; p.onGround = false;
            lv.later(0.5f, () -> {
                float g = lv.groundBelow(p.x, p.y - 20);
                float px = p.x;
                aoe(lv, p, px, g - 10, 100, 2.0f, 220, Ent.STUN, 1.1f, 0);
                lv.shake(8f, 0.5f);
                Snd.sfx("sk_earth_hit", 1f);
                for (int k = 1; k <= 5; k++) {
                    final int kk = k;
                    lv.later(k * 0.05f, () -> {
                        for (int s = -1; s <= 1; s += 2) {
                            float ex = px + s * kk * 24;
                            if (ex < 20 || ex > lv.room.pixW - 20) continue;
                            beam(lv, "fx_rock", "debris", ex, lv.groundBelow(ex, p.y - 20), 64, 0.8f, 0xFFFFFF);
                        }
                    });
                }
                for (int s = -1; s <= 1; s += 2) {
                    Proj w = lv.proj(px, g - 8, s * 240, 0, D(lv, p, 1.1f), true, "spike", c);
                    w.special = 1; w.pierce = 5; w.life = 0.7f; w.scale = 1.3f;
                }
                lv.fx("fx_dust", "land", px, g - 2, 2.5f, 0, 0);
            });
        }
    }

    private static void ultEarth(Level lv, Player p) {
        lv.flash(0xFFB060, 0.4f);
        lv.shake(3f, 3f);
        Snd.sfx("explosion_big", 0.5f);
        rep(lv, 18, 0.14f, 0.3f, k -> {
            // objetivo: enemigos en pantalla (alternando); si no hay, un punto al azar de la vista
            List<Ent> tg = lv.enemiesOnScreen();
            float sx, ty;
            if (!tg.isEmpty() && k % 3 != 2) {
                Ent t = tg.get(lv.rng.i(tg.size()));
                sx = t.x + lv.rng.f(-10, 10); ty = t.cy();
            } else {
                sx = lv.camX + lv.rng.f(20, lv.viewW - 20); ty = p.y - 10;
            }
            sx = Mth.clamp(sx, 20, lv.room.pixW - 20);
            // nace bajo el techo (no contra el): sube desde el objetivo hasta el primer solido o el borde de la vista
            float sy = Math.max(ty, lv.camY - 30);
            float top = lv.camY - 30;
            while (sy > top && !lv.solidAtPx(sx, sy - 14)) sy -= 8;
            if (sy < 12) sy = 12;
            Proj pr = lv.proj(sx, sy, lv.rng.f(-20, 20), 240, D(lv, p, 2.4f), true, "magma", 0xFF8A2A);
            pr.grav = 350; pr.scale = 2.2f; pr.explode = 50; pr.radius = 10; pr.life = 4f; pr.passWalls = false; pr.spin = true; pr.spinRate = 6f; pr.knock = 160;
            pr.status = Ent.BURN; pr.statusDur = 3f; pr.statusPow = 7f;
            if (k % 4 == 0) lv.shake(3f, 0.15f);
        });
    }

    // ---------------------------------------------------------------- Vagabundo estelar
    private static void astral(Level lv, Player p, int i) {
        int c = p.cls.color1;
        if (i == 0) {
            Proj pr = lv.proj(mx(p), my(p), p.dir() * 440, 0, D(lv, p, 2.1f), true, "star", c);
            pr.pierce = 999; pr.life = 1.3f; pr.scale = 1.8f; pr.knock = 80; pr.spin = true; pr.spinRate = 10f;
            lv.fxAdd("fx_star", "burst", mx(p), my(p), 0.8f, c);
        } else if (i == 1) {
            final float bx = Mth.clamp(p.x + p.dir() * 105, 30, lv.room.pixW - 30), by = p.y - 34;
            FxObj f = lv.fxAdd("fx_void", "hole", bx, by, 1.4f, c);
            if (f != null) { f.loop = true; f.life = 2.7f; }
            rep(lv, 13, 0.2f, 0.1f, k -> {
                pull(lv, bx, by, 120, 140);
                aoe(lv, p, bx, by, 46, 0.5f, 0, -1, 0, 0);
                lv.ps.spawn(bx + lv.rng.f(-50, 50), by + lv.rng.f(-40, 40), 0, 0, 0.4f, 2, 0, 0xB0A0FF, true);
            });
        } else {
            float ox = p.x, oy = p.y - 20;
            float d = 0;
            while (d < 140) {
                float nx = p.x + p.dir() * (d + 6);
                if (lv.solidAtPx(nx, p.y - 8) || lv.solidAtPx(nx, p.y - p.bh + 4) || nx < 24 || nx > lv.room.pixW - 24) break;
                d += 6;
            }
            lv.fx("fx_tele", "out", ox, oy, 1f, c, Platform.ADD | Platform.TINT);
            lv.ps.burst(lv.rng, ox, oy, c, 16, 120, 0.6f, 2, 0, true);
            p.x += p.dir() * d;
            p.vx = 0; p.vy = Math.min(p.vy, 0);
            p.invuln = Math.max(p.invuln, 0.6f);
            lv.fx("fx_tele", "in", p.x, p.y - 20, 1f, c, Platform.ADD | Platform.TINT);
            lv.fxAdd("fx_star", "burst", p.x, p.y - 20, 1.1f, c);
            aoe(lv, p, p.x, p.y - 18, 44, 0.9f, 80, -1, 0, 0);
            // rastro de estrellas
            for (int k = 0; k < 8; k++) lv.ps.spawn(ox + (p.x - ox) * k / 8f, oy + lv.rng.f(-8, 8), 0, 0, 0.7f, 2, 0, 0xFFFFFF, true);
        }
    }

    private static void ultAstral(Level lv, Player p) {
        int c = p.cls.color1;
        float cx = Mth.clamp(centerX(lv, p), 40, lv.room.pixW - 40);
        float cy = p.y - 110;
        lv.flash(0x201040, 0.7f);
        FxObj star = lv.fxAdd("fx_star", "twinkle", cx, cy, 2.4f, 0xFFFFFF);
        if (star != null) { star.loop = true; star.life = 1.7f; }
        FxObj hole = lv.fxAdd("fx_void", "hole", cx, cy, 2.0f, c);
        if (hole != null) { hole.loop = true; hole.life = 1.7f; }
        rep(lv, 14, 0.1f, 0.1f, k -> {
            pull(lv, cx, cy, 700, 170);
            for (Ent e : lv.enemiesOnScreen()) if (e instanceof Boss) continue;
            lv.shake(1.5f + k * 0.2f, 0.12f);
        });
        lv.later(1.6f, () -> {
            lv.flash(0xFFFFFF, 0.6f);
            lv.fxAdd("fx_explosion", "b", cx, cy + 60, 3.6f, c);
            lv.fxAdd("fx_star", "burst", cx, cy + 60, 3.5f, 0xFFFFFF);
            for (Ent e : screen(lv)) { lv.damageEnemy(e, D(lv, p, 7f), true, Mth.sign(e.x - cx) * 160, -120); lv.fx("fx_hit", "big", e.cx(), e.cy(), 1.5f, 0, 0); }
            lv.shake(10f, 0.8f);
            Snd.sfx("explosion_big", 1f);
            lv.ps.burst(lv.rng, cx, cy + 60, c, 80, 300, 1.2f, 3, 0, true);
        });
    }

    // ---------------------------------------------------------------- Acero
    private static void steel(Level lv, Player p, int i) {
        int c = p.cls.color1;
        if (i == 0) {
            for (int k = -1; k <= 1; k++) {
                float ang = (p.right ? 0 : (float) Math.PI) + (p.right ? k : -k) * 0.2f;
                Proj pr = shot(lv, p, mx(p), my(p), ang, 380, D(lv, p, 1.15f), "blade", c);
                pr.pierce = 2; pr.life = 1.0f; pr.scale = 1.3f;
            }
            lv.fxAdd("fx_ring", "pulse", mx(p), my(p), 0.45f, c);
        } else if (i == 1) {
            p.guardT = 8f;
            lv.fxAdd("fx_ring", "pulse", p.x, p.y - 18, 1.0f, c);
            lv.ps.burst(lv.rng, p.x, p.y - 18, c, 16, 100, 0.5f, 2, 0, true);
        } else {
            p.dash(p.dir(), 480f, 0.28f, 2.3f, Ent.BURN, 3f, false);
            lv.fxAdd("fx_fire", "burn", p.x, p.y - 20, 1f, 0xFF9A3C);
            rep(lv, 5, 0.05f, 0.02f, k -> lv.fxAdd("fx_fire", "burn", p.x - p.dir() * 8, p.y - 8, 0.7f, 0xFF9A3C));
            lv.later(0.3f, () -> aoe(lv, p, p.x + p.dir() * 16, p.y - 18, 46, 1.0f, 150 * p.dir(), -1, 0, 0));
        }
    }

    private static void ultSteel(Level lv, Player p) {
        int c = p.cls.color1;
        lv.flash(0xC9D4E8, 0.4f);
        lv.fxAdd("fx_ring", "pulse", p.x, p.y - 60, 2.4f, c);
        // anillo de espadas que se eleva
        for (int k = 0; k < 12; k++) {
            final int kk = k;
            lv.later(k * 0.03f, () -> {
                float ang = kk * 6.2832f / 12f;
                lv.ps.burst(lv.rng, p.x + (float) Math.cos(ang) * 40, p.y - 70 + (float) Math.sin(ang) * 12, c, 4, 60, 0.6f, 2, -30, true);
                lv.fxAdd("fx_proj", "blade", p.x + (float) Math.cos(ang) * 40, p.y - 70 + (float) Math.sin(ang) * 12, 1f, c);
            });
        }
        rep(lv, 40, 0.055f, 0.6f, k -> {
            float sx = lv.camX + lv.rng.f(10, lv.viewW - 10);
            Proj pr = lv.proj(sx, lv.camY - 24, lv.rng.f(-20, 20), 380, D(lv, p, 1.35f), true, "blade", c);
            pr.grav = 500; pr.explode = 22; pr.radius = 9; pr.scale = 1.5f; pr.life = 3f; pr.knock = 60;
            pr.explodeFx = "fx_hit:spark";
            if (k % 6 == 0) { lv.shake(2.5f, 0.1f); Snd.sfxv("hit_metal_1", 0.5f); }
        });
        lv.later(3.0f, () -> { lv.shake(6f, 0.3f); lv.flash(0xFFFFFF, 0.2f); Snd.sfx("hit_metal_2", 0.9f); });
    }
}
