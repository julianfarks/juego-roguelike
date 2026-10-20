package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Golpes cuerpo a cuerpo de las armas secundarias (Wpn.K_FAST / K_MID). Cada arma tiene su propia forma de golpe (tajo, estocada, barrido, mazazo, latigazo, puñetazo, cadena, zarpazo),
 * sus tiempos (anticipacion, impacto, recuperacion), su alcance y su altura de caja; el daño se aplica en el instante real del contacto y un golpe fallido no genera impacto.
 * El jugador conserva su estado (reposo/carrera/aire): el golpe es una accion de la mano de la secundaria (WeaponView dibuja el arma siguiendo el golpe).
 */
final class Melee {
    private Melee() {}

    /** Inicia un golpe del arma `id`. Los enfriamientos (secCd) ya los comprobo quien llama. */
    static void start(Level lv, Player p, int id) {
        RunState rs = lv.rs;
        Wpn.Def d = Wpn.of(id);
        WeaponFx.State s = p.wfx;
        if (s.sw) return;
        s.reset();
        s.sw = true; s.swId = id; s.swT = 0f; s.swDur = d.swingDur();
        s.swCount++; s.swAir = !p.onGround;
        // dirigir hacia el enemigo cercano (como el ataque principal) si no se esta moviendo
        Ent n = lv.nearestEnemy(p.x, p.y, 70, true);
        if (n != null && Math.abs(p.vx) < 20 && Math.abs(n.x - p.x) < 60) p.right = n.x >= p.x;
        s.swDir = p.dir();
        float rf = s.rhythmBoost > 0 ? 0.75f : 1f;
        p.secCd = d.cd * (1f - 0.12f * rs.secLvl) * rf;
        p.atkBuf = 0;
        p.wpnT = 0.22f; p.wpnId = id;
        p.vx = s.swDir * d.lunge * (p.onGround ? 1f : 0.5f);
        swingSound(d, s.swCount);
        swingFx(lv, p, d, s);
    }

    private static void swingSound(Wpn.Def d, int n) {
        String k;
        switch (d.swing) {
            case Wpn.S_STAB: k = "swing_stab_" + (1 + n % 3); break;
            case Wpn.S_SWEEP: k = "swing_scythe_" + (1 + n % 3); break;
            case Wpn.S_SMASH: k = d.dmg >= 2.5f ? "swing_hammer_" + (1 + n % 3) : "swing_great_" + (1 + n % 2); break;
            case Wpn.S_WHIP: k = "swing_air"; break;
            case Wpn.S_PUNCH: k = "swing_air"; break;
            case Wpn.S_CHAIN: k = "swing_dagger_3"; break;
            default: k = d.reach >= 32 ? "swing_sword_" + (1 + n % 3) : "swing_dagger_" + (1 + n % 3); break;
        }
        Snd.sfxv(k, 0.7f);
    }

    /** Estela del golpe (sprite de tajo de la hoja de efectos); el arma en la mano la dibuja WeaponView. */
    private static void swingFx(Level lv, Player p, Wpn.Def d, WeaponFx.State s) {
        String sheet, an; float sc = 0.85f, off = 22f;
        switch (d.swing) {
            case Wpn.S_STAB: case Wpn.S_WHIP: sheet = "fx_stab"; an = "s1"; off = Math.min(40f, d.reach * 0.6f); sc = d.swing == Wpn.S_WHIP ? 1.2f : 0.9f; break;
            case Wpn.S_SWEEP: case Wpn.S_SMASH: sheet = "fx_slash_big"; an = "s" + (1 + s.swCount % 3); sc = 0.8f; off = 24f; break;
            case Wpn.S_PUNCH: sheet = "fx_stab"; an = "s2"; sc = 0.7f; off = 20f; break;
            case Wpn.S_CLAW: sheet = "fx_slash_sword"; an = "s" + (1 + s.swCount % 3); sc = 0.8f; off = 22f; break;
            case Wpn.S_CHAIN: sheet = "fx_stab"; an = "s1"; off = 36f; sc = 1.1f; break;
            default: sheet = "fx_slash_sword"; an = "s" + (1 + s.swCount % 2); sc = d.reach >= 32 ? 0.9f : 0.7f; off = 20f; break;
        }
        // el efecto sale en el momento del impacto (tras la anticipacion), no al pulsar
        float delay = d.wind;
        float fx = p.x + s.swDir * off, fy = p.y - 18;
        FxObj f = lv.fxAdd(sheet, an, fx, fy, sc, d.col);
        if (f != null) { f.right = s.swDir > 0; f.alpha = 0.9f; f.delay = delay; }
    }

    static void update(Level lv, Player p, float dt) {
        WeaponFx.State s = p.wfx;
        if (!s.sw) return;
        if (!p.alive || lv.rs.sec != s.swId || !lv.rs.secActive) { s.reset(); return; }      // cambiar de arma o morir corta el golpe sin efectos
        Wpn.Def d = Wpn.of(s.swId);
        s.swT += dt;
        for (int i = 0; i < d.hits; i++) {
            float ti = d.wind + i * d.gap;
            if (s.swT >= ti && s.swT <= ti + Math.max(d.act, 0.05f) + dt) {
                hitPass(lv, p, d, s, i);
                s.swHitIdx = i + 1;
            }
        }
        if (p.onGround && s.swT < d.wind + d.act) p.vx *= 0.9f;
        if (s.swT >= s.swDur) { s.sw = false; }
    }

    private static void hitPass(Level lv, Player p, Wpn.Def d, WeaponFx.State s, int idx) {
        float dir = s.swDir;
        float rch = d.reach * BlessFx.reach(lv);
        float bx = dir > 0 ? p.x + 2 : p.x - 2 - rch;
        float by, bh;
        switch (d.swing) {
            case Wpn.S_SMASH: case Wpn.S_SWEEP: by = p.y - d.hgt - 2; bh = d.hgt + 2; break;
            default: by = p.y - 16 - d.hgt / 2f; bh = d.hgt; break;
        }
        lv.breakRect(bx, by, rch, bh, 1);
        List<Ent> list = new ArrayList<>(lv.enemiesInBox(bx, by, rch, bh));
        if ((d.passive & Wpn.P_BACK) != 0) {                      // golpe cruzado / barrido: tambien alcanza por detras
            float rb = Math.max(14f, rch * 0.6f);
            float bx2 = dir > 0 ? p.x - 2 - rb : p.x + 2;
            for (Ent e : lv.enemiesInBox(bx2, by, rb, bh)) if (!list.contains(e)) list.add(e);
        }
        if (list.isEmpty()) {
            for (Prop pr : lv.props) if (pr.kind.equals("pot") && !pr.open && Mth.overlap(pr.x - 6, pr.y - 14, 12, 14, bx, by, rch, bh)) lv.breakPot(pr);
            return;
        }
        final float px = p.x;
        list.sort((a, b) -> Float.compare(Math.abs(a.x - px), Math.abs(b.x - px)));
        int cap = (d.passive & Wpn.P_PIERCE) != 0 ? 3 : 5;
        int n = 0;
        RunState rs = lv.rs;
        float base = p.baseDmg(lv) * (1f + 0.25f * rs.secLvl);
        for (Ent e : list) {
            if (n >= cap) break;
            if (s.sets[Math.min(idx, 3)].contains(e)) continue;
            s.sets[Math.min(idx, 3)].add(e);
            n++;
            strike(lv, p, d, s, e, base, idx, n);
        }
        for (Prop pr : lv.props) if (pr.kind.equals("pot") && !pr.open && Mth.overlap(pr.x - 6, pr.y - 14, 12, 14, bx, by, rch, bh)) lv.breakPot(pr);
    }

    private static void strike(Level lv, Player p, Wpn.Def d, WeaponFx.State s, Ent e, float base, int idx, int nth) {
        int id = s.swId;
        float dir = s.swDir;
        float mul = d.dmg;
        if ((d.passive & Wpn.P_DOUBLE) != 0 && idx > 0) mul *= id == Items.SEC_TWINS ? 0.7f : 0.9f;
        if (nth > 1 && (d.passive & Wpn.P_PIERCE) != 0) mul *= 1f - 0.2f * (nth - 1);        // la lanza pierde fuerza con cada enemigo atravesado
        boolean heavy3 = false;
        if ((d.passive & Wpn.P_COMBO3) != 0 && idx == 0 && nth == 1) {
            s.c3N++; s.c3T = 1.2f;
            if (s.c3N % 3 == 0) { heavy3 = true; }
        } else if ((d.passive & Wpn.P_COMBO3) != 0 && s.c3N % 3 == 0 && s.c3N > 0) heavy3 = true;
        if (heavy3) mul *= 1.4f;
        float dmg = base * mul * WeaponFx.preMul(lv, id, e);
        boolean crit = lv.rollCrit(e) || ((d.passive & Wpn.P_CRIT) != 0 && lv.rng.chance(0.18f));
        if (crit) dmg *= lv.critMulOf(e);
        int kind = crit ? Impact.CRIT : (d.dmg >= 1.8f || heavy3 ? Impact.HEAVY : Impact.LIGHT);
        if (lv.counterT > 0) {                       // contraataque tras un parry perfecto: +50% (una sola vez)
            dmg *= 1.5f; lv.counterT = 0; if (kind < Impact.HEAVY) kind = Impact.HEAVY;
            lv.text(e.x, e.y - e.bh - 22, "¡Contra!", 0xFFFFFF, true);
            lv.fx("fx_ring", "pulse", e.cx(), e.cy(), 0.8f, 0xFFFFFF, Platform.ADD | Platform.TINT);
        }
        float kb = d.knock * (heavy3 ? 1.5f : 1f) * (kind == Impact.CRIT ? 1.15f : 1f);
        float ky = (d.swing == Wpn.S_SMASH && d.dmg >= 1.8f) || heavy3 ? -140f : -40f;
        float kx = dir * kb;
        if ((d.passive & Wpn.P_PULL) != 0) kx = -dir * 80f;            // el latigo atrae
        int pv = lv.dmgSrc;
        lv.dmgSrc = BlessFx.SRC_W;
        lv.hitKind = kind;
        try { lv.damageEnemy(e, dmg, crit, kx, ky); } finally { lv.hitKind = 0; lv.dmgSrc = pv; }
        lv.onWeaponHit(e, dmg, crit, 0);
        Impact.hit(lv, e, kind, dir, !e.alive, sfxFor(e, crit, d));
        if (!s.swLanded) {                           // primer contacto real del golpe: ritmo y pose de impacto
            s.swLanded = true;
            p.registerHitPose(lv, kind);
            if ((d.passive & Wpn.P_RHYTHM) != 0) {
                if (s.rhythmT <= 0) s.rhythmN = 0;
                s.rhythmN++; s.rhythmT = 1.2f;
                if (s.rhythmN >= 3 && s.rhythmBoost <= 0) { s.rhythmBoost = 1.5f; s.rhythmN = 0; lv.fx("fx_ring", "pulse", p.x, p.y - 16, 0.35f, d.col, Platform.ADD | Platform.TINT); }
            }
            if (id == Items.SEC_WARHAMMER) shockwave(lv, p, dir, base * d.dmg * 0.4f);
        }
        WeaponFx.afterHit(lv, id, e, dmg, crit, true, dir);
    }

    /** Onda de impacto del martillo: una onda corta pegada al suelo que alcanza a los demas enemigos delante. */
    private static void shockwave(Level lv, Player p, float dir, float dmg) {
        Proj w = lv.proj(p.x + dir * 20, p.y - 6, dir * 230, 0, dmg, true, "crescent", 0xD0A070);
        w.special = 1; w.pierce = 3; w.life = 0.45f; w.trail = true; w.scale = 0.9f; w.src = BlessFx.SRC_W;
        lv.shake(2.5f, 0.12f);
    }

    private static String sfxFor(Ent e, boolean crit, Wpn.Def d) {
        if (crit) return "hit_crit";
        if (d.swing == Wpn.S_SMASH || d.swing == Wpn.S_PUNCH) return "hit_metal_" + (1 + lv_i(2));
        if (e instanceof Enemy) {
            String di = ((Enemy) e).def.dieSfx;
            if (di.contains("bone")) return "hit_bone";
            if (di.contains("ghost") || di.contains("magic")) return "hit_magic";
        }
        return "hit_flesh_" + (1 + lv_i(3));
    }

    private static int lv_i(int n) { return (int) (Mth.rnd() * n); }
}
