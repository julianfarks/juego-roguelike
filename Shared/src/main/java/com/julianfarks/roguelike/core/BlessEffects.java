package com.julianfarks.roguelike.core;

import java.util.List;

/** Ejecucion de los efectos de las reglas de bendicion (BRule.E_*), los espiritus invocados y los charcos de rastro. Todo con topes. */
final class BlessEffects {
    private BlessEffects() {}

    static final float HEAL_ROOM_CAP = 0.25f, HEAL_BOSS_CAP = 0.35f, GOLD_ROOM_CAP = 90f, SOUL_ROOM_CAP = 45f;
    private static final int[] ST_COL = {0xFF7A1A, 0x9AE0FF, 0x7AB8FF, 0x6AE08A, 0xF0F060, 0xD0203A, 0x6AA040, 0xFFFFFF, 0xB070FF};

    static int colorOf(int st) { return st >= 0 && st < ST_COL.length ? ST_COL[st] : 0xFFE8A0; }

    // ------------------------------------------------------------------ utilidades
    private static float base(Level lv) { return lv.pl.baseDmg(lv); }

    private static Ent topTarget(Level lv, Ent v, float x, float y) {
        if (v != null && v.alive) return v;
        return lv.nearestEnemy(x, y, 220f, true);
    }

    static void applyStatus(Level lv, Ent e, int st, float dur, float powMul) {
        if (e == null || !e.alive) return;
        if (e instanceof Boss && (st == Ent.FREEZE || st == Ent.STUN || st == Ent.ROOT)) {     // los jefes no se congelan ni se aturden: solo se ralentizan
            if (st == Ent.FREEZE) { e.applyStatus(Ent.SLOW, dur, 0); }
            return;
        }
        float pow = 0f;
        float dm = lv.rs.stats.dmgMul;
        if (st == Ent.BURN) pow = (6f + dm * 3f) * powMul * BlessFx.dotMul(lv.rs);
        else if (st == Ent.POISON) pow = (5f + dm * 2f) * powMul * BlessFx.dotMul(lv.rs);
        else if (st == Ent.BLEED) pow = (4f + dm * 1.5f) * powMul * BlessFx.dotMul(lv.rs);
        e.applyStatus(st, dur * BlessFx.statusDurMul(lv.rs), pow);
    }

    private static void ringFx(Level lv, float x, float y, float r, int color) {
        lv.fxAdd("fx_ring", "pulse", x, y, Math.max(0.35f, r / 44f), color);
        lv.ps.burst(lv.rng, x, y, color, 8, 100, 0.35f, 2, 0, true);
    }

    // ------------------------------------------------------------------ ejecucion
    static void run(Level lv, BlessRt bx, BRule r, float mag, Ent v, float amt, boolean crit, int src, float x, float y) {
        Player p = lv.pl;
        RunState rs = lv.rs;
        float vx = v != null ? v.cx() : x, vy = v != null ? v.cy() : y;
        float[] a = r.a;
        switch (r.eff) {
            case BRule.E_STATUS: {
                int st = (int) a[0];
                float dur = a[1];
                float pm = a[2] > 0 ? a[2] : 1f;
                if (r.aoe > 0) {
                    for (Enemy e : lv.enemies) if (e.alive && (r.aoe >= 900 || Mth.dist(p.x, p.cy(), e.cx(), e.cy()) <= r.aoe)) applyStatus(lv, e, st, dur, pm);
                    if (lv.boss != null && lv.boss.alive && (r.aoe >= 900 || Mth.dist(p.x, p.cy(), lv.boss.cx(), lv.boss.cy()) <= r.aoe)) applyStatus(lv, lv.boss, st, dur, pm);
                } else {
                    Ent t = topTarget(lv, v, x, y);
                    if (t == null) return;
                    applyStatus(lv, t, st, dur, pm);
                    lv.ps.burst(lv.rng, t.cx(), t.cy(), colorOf(st), 4, 60, 0.25f, 2, 0, true);
                }
                break;
            }
            case BRule.E_SPREAD: {
                if (v == null) return;
                int st = (int) a[0];
                if (v.st[st] <= 0) return;
                float rad = a[1];
                int n = 0;
                for (Enemy e : lv.enemies) {
                    if (e == v || !e.alive || n >= 6) continue;
                    if (Mth.dist(vx, vy, e.cx(), e.cy()) <= rad) {
                        float d = Math.max(1.5f, v.st[st] * 0.8f);
                        e.applyStatus(st, d, v.stPow[st]);
                        lv.ps.burst(lv.rng, e.cx(), e.cy(), colorOf(st), 4, 60, 0.25f, 2, 0, true);
                        n++;
                    }
                }
                if (n > 0) ringFx(lv, vx, vy, rad * 0.7f, colorOf(st));
                break;
            }
            case BRule.E_EXPLODE: {
                float rad = a[0];
                float dmg = base(lv) * a[1] * (r.scale ? mag : 1f);
                int st = r.na > 2 ? (int) a[2] : -1;
                float dur = r.na > 3 ? a[3] : 2f;
                float ex = r.aoe < 0 ? p.x : vx, ey = r.aoe < 0 ? p.cy() : vy;
                float pw = st == Ent.BURN ? 6f + rs.stats.dmgMul * 3f : st == Ent.POISON ? 5f + rs.stats.dmgMul * 2f : st == Ent.BLEED ? 4f + rs.stats.dmgMul * 1.5f : 0f;
                lv.explosion(ex, ey, rad, dmg, 140f, st, dur, pw, true);
                int col = st >= 0 ? colorOf(st) : 0xFFB060;
                lv.fxAdd("fx_explosion", "a", ex, ey, Math.max(0.45f, rad / 70f), col);
                ringFx(lv, ex, ey, rad, col);
                if (rad >= 60 || bx.perSecond < 12) Snd.sfxv("explosion_small", 0.45f);
                break;
            }
            case BRule.E_CHAIN: {
                Ent from = topTarget(lv, v, x, y);
                if (from == null) return;
                lv.chain(from, base(lv) * a[1] * (r.scale ? mag : 1f), (int) a[0]);
                break;
            }
            case BRule.E_NEXTHIT:
                bx.nextHitMul = Math.max(bx.nextHitMul, a[0]); bx.nextHitT = Math.max(bx.nextHitT, a[1]); if (a[2] > 0) bx.nextHitCrit = true;
                lv.ps.burst(lv.rng, p.x, p.cy(), 0xFFE070, 6, 70, 0.4f, 2, -20, true);
                break;
            case BRule.E_NEXTSKILL:
                bx.nextSkillMul = Math.max(bx.nextSkillMul, a[0]); bx.nextSkillT = Math.max(bx.nextSkillT, a[1]);
                lv.ps.burst(lv.rng, p.x, p.cy(), 0x9A7AFF, 8, 80, 0.45f, 2, -20, true);
                break;
            case BRule.E_BUFF: {
                int c = (int) a[0];
                int cap = a[3] >= 1 ? (int) a[3] : 1;
                if (bx.chT[c] <= 0) bx.chN[c] = 0;
                bx.chAmt[c] = a[1] * (r.scale ? mag : 1f);
                bx.chN[c] = Math.min(cap, bx.chN[c] + 1);
                bx.chT[c] = Math.max(bx.chT[c], a[2]);
                break;
            }
            case BRule.E_HEAL: {
                float cap = (lv.room.type == Room.BOSS ? HEAL_BOSS_CAP : HEAL_ROOM_CAP) * rs.stats.maxHp;
                float want = a[0] * (r.scale ? mag : 1f) * rs.stats.maxHp;
                float give = Math.min(want, Math.max(0f, cap - bx.healRoom));
                if (give <= 0.5f) return;
                bx.healRoom += give;
                lv.healPlayer(give);
                break;
            }
            case BRule.E_SHIELD: {
                float cap = a[1] > 0 ? a[1] : BlessFx.shieldCap(rs);
                float add = a[0] * (r.scale ? mag : 1f);
                if (p.shield >= cap) return;
                boolean fresh = p.shield <= 0;
                p.shield = Math.min(cap, p.shield + add);
                if (fresh) lv.fx("fx_shield", "bubble", p.x, p.y - 20, 0.8f, 0, 0);
                break;
            }
            case BRule.E_CDR: {
                float sec = a[0] * (r.scale ? mag : 1f);
                int which = (int) a[1];
                if (which == 1) {
                    int li = -1; float lm = 0;
                    for (int i = 0; i < 3; i++) if (rs.cd[i] > lm) { lm = rs.cd[i]; li = i; }
                    if (li >= 0) rs.cd[li] -= takeBucket(bx, Math.min(sec, rs.cd[li]));
                } else for (int i = 0; i < 3; i++) if (rs.cd[i] > 0) rs.cd[i] -= takeBucket(bx, Math.min(sec, rs.cd[i]));
                for (int i = 0; i < 3; i++) if (rs.cd[i] < 0) rs.cd[i] = 0;
                break;
            }
            case BRule.E_CDRPCT: {
                for (int i = 0; i < 3; i++) if (rs.cd[i] > 0) { float cut = rs.cd[i] * a[0]; rs.cd[i] -= takeBucket(bx, cut); }
                break;
            }
            case BRule.E_COOLDOWNALL:
                for (int i = 0; i < 3; i++) rs.cd[i] = 0f;
                lv.fxAdd("fx_ring", "pulse", p.x, p.cy(), 0.9f, 0x9A7AFF);
                break;
            case BRule.E_ULT:
                rs.ult = Math.min(100f, rs.ult + a[0] * (r.scale ? mag : 1f));
                break;
            case BRule.E_ULTPCT:
                rs.ult = Math.min(100f, rs.ult + amt * a[0]);
                break;
            case BRule.E_PROJ: proj(lv, r, p, v, vx, vy); break;
            case BRule.E_GOLD: {
                float n = a[0] * (r.scale ? mag : 1f);
                float give = Math.min(n, Math.max(0f, GOLD_ROOM_CAP - bx.goldRoom));
                if (give < 1f) return;
                bx.goldRoom += give; rs.gold += Math.round(give);
                lv.text(p.x, p.y - p.bh - 14, "+" + Math.round(give) + " oro", 0xFFD25A, false);
                break;
            }
            case BRule.E_SOULS: {
                float n = a[0] * (r.scale ? mag : 1f);
                float give = Math.min(n, Math.max(0f, SOUL_ROOM_CAP - bx.soulRoom));
                if (give < 1f) return;
                bx.soulRoom += give; rs.souls += Math.round(give);
                lv.text(p.x, p.y - p.bh - 14, "+" + Math.round(give) + " almas", 0x9FD8FF, false);
                break;
            }
            case BRule.E_ARC:
                bx.arc = Math.min(10f, bx.arc + a[0]);
                lv.ps.burst(lv.rng, p.x, p.cy(), 0xF0F060, 5, 70, 0.3f, 2, 0, true);
                break;
            case BRule.E_DISCHARGE: {
                int n = (int) bx.arc;
                if (n < 1) return;
                Ent from = topTarget(lv, v, x, y);
                if (from == null) return;
                bx.arc = 0;
                lv.chain(from, base(lv) * a[1] * n, (int) a[0]);
                lv.lightning(p.x, p.cy(), from.cx(), from.cy());
                lv.shake(2f, 0.12f);
                BlessFx.fireK(lv, BRule.T_DISCHARGED, -1, from, n, false, BlessFx.SRC_X, from.cx(), from.cy());
                break;
            }
            case BRule.E_INVULN: {
                float sec = Math.min(0.6f, a[0]);
                p.invuln = Math.max(p.invuln, sec);
                lv.fxAdd("fx_ring", "pulse", p.x, p.cy(), 0.7f, 0xFFFFFF);
                break;
            }
            case BRule.E_PUSH: case BRule.E_PULL: {
                float sgn = r.eff == BRule.E_PUSH ? 1f : -1f;
                for (Enemy e : lv.enemies) if (e.alive && Mth.dist(p.x, p.cy(), e.cx(), e.cy()) <= a[0]) { float d = Mth.sign(e.x - p.x); if (d == 0) d = 1; e.vx = d * sgn * a[1]; }
                break;
            }
            case BRule.E_TRAIL: {
                if (bx.patches.size() >= 14) bx.patches.remove(0);
                BlessRt.Patch pt = new BlessRt.Patch();
                pt.x = p.x; pt.y = p.y; pt.t = a[1]; pt.kind = (int) a[0]; pt.dmg = a[2];
                bx.patches.add(pt);
                break;
            }
            case BRule.E_POTION:
                rs.potions = Math.min(rs.stats.potionsMax, rs.potions + Math.max(1, (int) a[0]));
                lv.text(p.x, p.y - p.bh - 14, "+1 frasco", 0x6AE08A, false);
                break;
            case BRule.E_LOSEHP: {
                float floor = rs.stats.maxHp * 0.12f;
                float cost = rs.stats.maxHp * a[0];
                float nh = Math.max(Math.min(rs.hp, floor), rs.hp - cost);
                if (nh < rs.hp) { lv.text(p.x, p.y - p.bh - 8, "-" + Math.round(rs.hp - nh), 0xC04060, false); rs.hp = nh; }
                break;
            }
            case BRule.E_LOSEGOLD:
                rs.gold = Math.max(0, rs.gold - (int) a[0]);
                break;
            case BRule.E_TIMESLOW:
                bx.slowT = Math.max(bx.slowT, a[0]); bx.slowScale = a[1] > 0 ? a[1] : 0.5f;
                lv.fxAdd("fx_ring", "pulse", p.x, p.cy(), 1.4f, 0x9AD8FF);
                lv.flash(0x6090FF, 0.12f);
                break;
            case BRule.E_CLEANSE:
                for (int i = 0; i < Ent.ST_COUNT; i++) { p.st[i] = 0; p.stPow[i] = 0; }
                break;
            case BRule.E_MARKTOP: {
                Ent best = null; float bh = -1;
                for (Enemy e : lv.enemies) if (e.alive && e.st[Ent.CURSE] <= 0 && e.hp > bh) { bh = e.hp; best = e; }
                if (lv.boss != null && lv.boss.alive && lv.boss.st[Ent.CURSE] <= 0 && lv.boss.hp > bh) best = lv.boss;
                if (best == null) return;
                best.applyStatus(Ent.CURSE, a[0], 0);
                ringFx(lv, best.cx(), best.cy(), 20, colorOf(Ent.CURSE));
                break;
            }
            case BRule.E_REPEAT: {
                if (v == null) return;
                final Ent tv = v; final float dd = amt * a[0]; final float dirx = p.dir() * 60f;
                lv.later(0.15f, () -> {
                    if (!tv.alive) return;
                    BlessRt b2 = lv.rs.bx; if (b2 == null) return;
                    int prev = lv.dmgSrc; b2.depth++; lv.dmgSrc = BlessFx.SRC_X;
                    try { lv.damageEnemy(tv, dd, false, dirx, -30); lv.fx("fx_hit", "spark", tv.cx(), tv.cy(), 0.8f, 0xFFFFFF, Platform.ADD | Platform.TINT); }
                    finally { b2.depth--; lv.dmgSrc = prev; }
                });
                break;
            }
            case BRule.E_HEARTDROP:
                lv.drop(Pickup.HEART, vx, vy - 6, 1);
                break;
            case BRule.E_BURSTUP:
                bx.spiritBoostT = Math.max(bx.spiritBoostT, a[0]);
                break;
            case BRule.E_STRIKE: {
                int n = (int) a[0];
                List<Enemy> list = lv.enemies;
                int done = 0;
                for (int tries = 0; tries < 12 && done < n; tries++) {
                    if (list.isEmpty()) break;
                    Enemy e = list.get(lv.rng.i(list.size()));
                    if (!e.alive) continue;
                    lv.lightning(e.cx() + lv.rng.f(-6, 6), e.cy() - 140, e.cx(), e.cy());
                    lv.damageEnemy(e, base(lv) * a[1], false, 0, 0);
                    e.applyStatus(Ent.SHOCK, 0.8f, 0);
                    done++;
                }
                if (lv.boss != null && lv.boss.alive && done < n) { lv.lightning(lv.boss.cx(), lv.boss.cy() - 140, lv.boss.cx(), lv.boss.cy()); lv.damageEnemy(lv.boss, base(lv) * a[1], false, 0, 0); done++; }
                if (done > 0) Snd.sfxv("hit_shock", 0.6f);
                break;
            }
            default: break;      // modificadores (M_*) y espiritus no se ejecutan aqui
        }
    }

    /** Gasta del presupuesto de reduccion de reutilizacion (se recarga con el tiempo) y devuelve lo que realmente se puede reducir. */
    static float takeBucket(BlessRt bx, float want) {
        float give = Math.min(want, Math.max(0f, bx.cdrBucket));
        bx.cdrBucket -= give;
        return give;
    }

    // ------------------------------------------------------------------ proyectiles creados por bendiciones
    private static void proj(Level lv, BRule r, Player p, Ent v, float vx, float vy) {
        int kind = (int) r.a[0], n = Math.max(1, (int) r.a[1]);
        float dmg = base(lv) * r.a[2];
        int st = r.na > 3 ? (int) r.a[3] : -1;
        float dir = p.dir();
        int col = st >= 0 ? colorOf(st) : p.cls.color1;
        switch (kind) {
            case BRule.PK_WAVE: {
                Proj q = lv.proj(p.x + dir * 14, p.y - 18, dir * 290, 0, dmg, true, "crescent", p.cls.color1);
                q.pierce = 3; q.life = 0.9f; q.trail = true; q.scale = 1.2f; q.src = BlessFx.SRC_X;
                break;
            }
            case BRule.PK_BLADE: {
                for (int i = 0; i < n; i++) {
                    Proj q = lv.proj(p.x + dir * 12, p.y - 20 + (i - (n - 1) / 2f) * 6, dir * 340, 0, dmg, true, "blade", col);
                    q.pierce = 2; q.life = 0.8f; q.src = BlessFx.SRC_X;
                }
                break;
            }
            case BRule.PK_SHARD: {
                for (int i = 0; i < n; i++) {
                    float ang = (float) (-Math.PI / 2 + (i - (n - 1) / 2f) * 0.9f + (lv.rng.f() - 0.5f) * 0.3f) + (lv.rng.chance(0.5f) ? 0f : (float) Math.PI * 0.0f);
                    float sp = 230f;
                    Proj q = lv.proj(vx, vy, (float) Math.cos(ang) * sp * (i % 2 == 0 ? 1 : -1) * 0.9f, (float) Math.sin(ang) * sp * 0.6f, dmg, true, st == Ent.SLOW || st == Ent.FREEZE ? "iceshard" : "dagger", col);
                    q.life = 0.55f; q.scale = 0.75f; q.src = BlessFx.SRC_X; q.grav = 200f; q.knock = 40f;
                    if (st >= 0) { q.status = st; q.statusDur = 2f; q.statusPow = st == Ent.BURN ? 6f : st == Ent.POISON ? 5f : 0f; }
                }
                break;
            }
            case BRule.PK_ORB: case BRule.PK_STAR: case BRule.PK_HOLY: {
                String spr = kind == BRule.PK_HOLY ? "holy" : kind == BRule.PK_STAR ? "star" : "bolt";
                for (int i = 0; i < n; i++) {
                    float ang = (float) (Math.PI * 2 * i / n + lv.rng.f() * 0.6f);
                    Proj q = lv.proj(p.x, p.cy(), (float) Math.cos(ang) * 190f, (float) Math.sin(ang) * 190f - 40f, dmg, true, spr, 0xFFE070);
                    q.homing = 900f; q.life = 1.4f; q.scale = 0.9f; q.src = BlessFx.SRC_X; q.knock = 60f; q.pierce = 0;
                    if (st >= 0) { q.status = st; q.statusDur = 2f; q.statusPow = st == Ent.BURN ? 6f : 0f; }
                }
                break;
            }
            case BRule.PK_RING: {
                for (int i = 0; i < Math.max(6, n); i++) {
                    float ang = (float) (Math.PI * 2 * i / Math.max(6, n));
                    Proj q = lv.proj(p.x, p.cy(), (float) Math.cos(ang) * 210f, (float) Math.sin(ang) * 210f, dmg, true, "star", col);
                    q.life = 0.6f; q.pierce = 1; q.src = BlessFx.SRC_X; q.scale = 0.8f;
                    if (st >= 0) { q.status = st; q.statusDur = 2f; q.statusPow = st == Ent.BURN ? 6f : 0f; }
                }
                lv.fxAdd("fx_ring", "pulse", p.x, p.cy(), 0.8f, col);
                break;
            }
            case BRule.PK_RAIN: {
                int made = 0;
                List<Ent> vis = lv.enemiesOnScreen();
                for (int i = 0; i < n; i++) {
                    float tx, ty;
                    if (!vis.isEmpty()) { Ent e = vis.get(lv.rng.i(vis.size())); tx = e.cx() + lv.rng.f(-14, 14); ty = e.cy(); }
                    else { tx = p.x + dir * lv.rng.f(30, 140); ty = p.y; }
                    Proj q = lv.proj(tx, ty - 190 - lv.rng.f(0, 40), 0, 330f, dmg, true, "blade", col);
                    q.life = 0.9f; q.src = BlessFx.SRC_X; q.pierce = 0; q.scale = 1.1f; q.passWalls = true; q.knock = 30f;
                    made++;
                }
                if (made > 0) Snd.sfxv("swing_air", 0.4f);
                break;
            }
            default: break;
        }
    }

    // ------------------------------------------------------------------ sinergias
    static void synergyFound(Level lv, int s) {
        BSyn[] all = BlessData.syns();
        if (s < 0 || s >= all.length || lv.pl == null) return;
        Player p = lv.pl;
        lv.text(p.x, p.y - 74, all[s].name, 0xFFE070, true);
        lv.fxAdd("fx_ring", "pulse", p.x, p.cy(), 1.3f, 0xFFE070);
        lv.fx("fx_holy", "beam", p.x, p.y - 56, 0.7f, 0, 0);
        Snd.sfxv("ui_pick_upgrade", 0.5f);
    }

    /** Aviso al conseguir una sinergia (al elegir la ultima bendicion necesaria). */
    static void synergyActivated(Level lv, int s) {
        BSyn[] all = BlessData.syns();
        if (s < 0 || s >= all.length || lv.pl == null) return;
        Player p = lv.pl;
        lv.text(p.x, p.y - 86, "¡Sinergia activada!", 0xFFE070, true);
        lv.text(p.x, p.y - 74, all[s].name, 0xFFFFFF, false);
        lv.fxAdd("fx_ring", "pulse", p.x, p.cy(), 1.5f, 0xFFE070);
        lv.fx("fx_holy", "beam", p.x, p.y - 56, 0.9f, 0, 0);
        lv.ps.burst(lv.rng, p.x, p.cy(), 0xFFE070, 30, 150, 0.9f, 2, -20, true);
        Snd.sfxv("ui_pick_upgrade", 0.8f);
    }

    // ------------------------------------------------------------------ espiritus
    static void updateSpirits(Level lv, BlessRt bx, float dt) {
        Player p = lv.pl;
        if (bx.spirits.isEmpty() || p == null) return;
        float rate = BlessFx.spiritRate(lv);
        int n = bx.spirits.size();
        for (int i = 0; i < n; i++) {
            BlessRt.Spirit s = bx.spirits.get(i);
            float ang = bx.t * 1.7f + s.phase;
            float tx = p.x + (float) Math.cos(ang) * (22f + 6f * i), ty = p.cy() - 18f + (float) Math.sin(ang * 1.3f) * 9f;
            float k = Math.min(1f, dt * 6f);
            if (s.x == 0 && s.y == 0) { s.x = tx; s.y = ty; }
            s.x += (tx - s.x) * k; s.y += (ty - s.y) * k;
            if (s.flash > 0) s.flash -= dt;
            if (lv.cinematic || !p.alive) continue;
            s.cd -= dt * rate;
            if (s.cd > 0) continue;
            if (spiritAct(lv, bx, s, p)) s.cd = Math.max(0.6f, s.rule.a[0]); else s.cd = 0.4f;
        }
    }

    private static boolean spiritAct(Level lv, BlessRt bx, BlessRt.Spirit s, Player p) {
        BRule r = s.rule;
        RunState rs = lv.rs;
        bx.depth++;
        int prev = lv.dmgSrc; lv.dmgSrc = BlessFx.SRC_X;
        try {
            switch (r.eff) {
                case BRule.E_SPIRIT_WISP: {
                    Ent t = lv.nearestEnemy(s.x, s.y, 180f, true);
                    if (t == null) return false;
                    s.flash = 0.25f;
                    bolt(lv, s.x, s.y, t.cx(), t.cy(), s.color);
                    lv.damageEnemy(t, base(lv) * r.a[1], false, 0, 0);
                    if (r.na > 2 && r.a[2] >= 0) applyStatus(lv, t, (int) r.a[2], 2.5f, 1f);
                    lv.fx("fx_hit", "spark", t.cx(), t.cy(), 0.8f, s.color, Platform.ADD | Platform.TINT);
                    bx.fired[s.owner >= 0 ? s.owner : 0]++;
                    return true;
                }
                case BRule.E_SPIRIT_NOVA: {
                    if (lv.nearestEnemy(s.x, s.y, 90f, true) == null) return false;
                    s.flash = 0.3f;
                    float rad = r.na > 3 ? r.a[3] : 64f;
                    lv.explosion(s.x, s.y, rad, base(lv) * r.a[1], 60f, Ent.SLOW, 2.5f, 0f, true);
                    ringFx(lv, s.x, s.y, rad, s.color);
                    bx.fired[s.owner >= 0 ? s.owner : 0]++;
                    return true;
                }
                case BRule.E_SPIRIT_CHAIN: {
                    Ent t = lv.nearestEnemy(s.x, s.y, 180f, true);
                    if (t == null) return false;
                    s.flash = 0.3f;
                    lv.lightning(s.x, s.y, t.cx(), t.cy());
                    lv.damageEnemy(t, base(lv) * r.a[1], false, 0, 0);
                    lv.chain(t, base(lv) * r.a[1], (int) r.a[2]);
                    bx.fired[s.owner >= 0 ? s.owner : 0]++;
                    return true;
                }
                case BRule.E_SPIRIT_MARK: {
                    Ent best = null; float bh = -1;
                    for (Enemy e : lv.enemies) if (e.alive && e.st[Ent.CURSE] <= 0 && e.hp > bh) { bh = e.hp; best = e; }
                    if (lv.boss != null && lv.boss.alive && lv.boss.st[Ent.CURSE] <= 0 && lv.boss.hp > bh) best = lv.boss;
                    if (best == null) return false;
                    s.flash = 0.3f;
                    bolt(lv, s.x, s.y, best.cx(), best.cy(), s.color);
                    best.applyStatus(Ent.CURSE, 7f, 0);
                    bx.fired[s.owner >= 0 ? s.owner : 0]++;
                    return true;
                }
                case BRule.E_SPIRIT_HEAL: {
                    if (rs.hp >= rs.stats.maxHp * 0.92f) return false;
                    float cap = (lv.room.type == Room.BOSS ? HEAL_BOSS_CAP : HEAL_ROOM_CAP) * rs.stats.maxHp;
                    float give = Math.min(r.a[1] * rs.stats.maxHp, Math.max(0f, cap - bx.healRoom));
                    if (give < 0.5f) return false;
                    bx.healRoom += give; lv.healPlayer(give); s.flash = 0.4f;
                    bx.fired[s.owner >= 0 ? s.owner : 0]++;
                    return true;
                }
                case BRule.E_SPIRIT_GUARD: {
                    if (p.shield > 0) return false;
                    p.shield = Math.min(BlessFx.shieldCap(rs), p.shield + r.a[1]);
                    lv.fx("fx_shield", "bubble", p.x, p.y - 20, 0.8f, 0, 0);
                    s.flash = 0.4f;
                    bx.fired[s.owner >= 0 ? s.owner : 0]++;
                    return true;
                }
                default: return false;
            }
        } finally { lv.dmgSrc = prev; bx.depth--; }
    }

    private static void bolt(Level lv, float x1, float y1, float x2, float y2, int color) {
        for (int i = 0; i < 6; i++) { float f = i / 5f; lv.ps.spawn(x1 + (x2 - x1) * f, y1 + (y2 - y1) * f, lv.rng.f(-6, 6), lv.rng.f(-6, 6), 0.25f, 2, 0, color, true); }
    }

    // ------------------------------------------------------------------ charcos de rastro
    static void updatePatches(Level lv, BlessRt bx, float dt) {
        if (bx.patches.isEmpty()) return;
        for (int i = bx.patches.size() - 1; i >= 0; i--) {
            BlessRt.Patch pt = bx.patches.get(i);
            pt.t -= dt; pt.tick -= dt;
            int col = patchColor(pt.kind);
            if (lv.rng.chance(dt * 14f)) lv.ps.spawn(pt.x + lv.rng.f(-6, 6), pt.y - 2, lv.rng.f(-4, 4), -lv.rng.f(14, 36), 0.5f, 2, 0, col, true);
            if (pt.tick <= 0) {
                pt.tick = 0.25f;
                bx.depth++; int prev = lv.dmgSrc; lv.dmgSrc = BlessFx.SRC_X;
                try {
                    for (Ent e : lv.enemiesInBox(pt.x - 14, pt.y - 18, 28, 20)) {
                        lv.damageEnemy(e, base(lv) * pt.dmg * 0.25f, false, 0, 0);
                        applyStatus(lv, e, pt.kind == 0 ? Ent.BURN : pt.kind == 1 ? Ent.SLOW : pt.kind == 2 ? Ent.POISON : pt.kind == 3 ? Ent.CURSE : Ent.SHOCK, 2f, 0.7f);
                    }
                } finally { lv.dmgSrc = prev; bx.depth--; }
            }
            if (pt.t <= 0) bx.patches.remove(i);
        }
    }

    static int patchColor(int kind) { return kind == 0 ? 0xFF8A30 : kind == 1 ? 0x7AC8F0 : kind == 2 ? 0x6AE08A : kind == 3 ? 0x9A60E0 : 0xFFE8A0; }

    // ------------------------------------------------------------------ dibujo
    static void draw(Level lv, Platform.Gfx g) {
        BlessRt bx = lv.rs.bx;
        if (bx == null || !bx.any) return;
        for (BlessRt.Spirit s : bx.spirits) {
            UI.light(g, s.x, s.y, 14 + (s.flash > 0 ? 8 : 0), s.color | 0xFF000000, 0.35f);
            g.circle(s.x, s.y, 2.6f, 0xFF000000 | s.color, false);
            g.circle(s.x, s.y, 1.4f, 0xFFFFFFFF, true);
        }
        for (BlessRt.Patch pt : bx.patches) {
            float a = Math.min(1f, pt.t * 2f);
            UI.light(g, pt.x, pt.y - 2, 12, patchColor(pt.kind) | 0xFF000000, 0.35f * a);
        }
    }
}
