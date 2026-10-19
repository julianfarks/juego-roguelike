package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Arsenal: arma principal (la de la clase) + UNA arma secundaria equipada, cambio de arma, armas en el suelo e intercambio.
 * Extiende el sistema que ya existia (Items.SEC_*, RunState.sec/secAmmo/secLvl, ChestLoot): no crea uno paralelo.
 * Los datos de cada arma viven en Items (SEC_NAME, SEC_DMG, SEC_CD...); aqui estan el comportamiento de las armas nuevas y las reglas de suelo/cambio.
 */
final class Arsenal {
    private Arsenal() {}

    // ================================================================ disparo de las armas nuevas (ids 5..10)
    static float counterBoost(Level lv, float base) {
        if (lv.counterT > 0) { lv.counterT = 0; lv.text(lv.pl.x, lv.pl.y - lv.pl.bh - 14, "¡Contra a distancia!", 0xFFE070, true); return base * 1.5f; }
        return base;
    }

    static boolean chakramOut(Level lv) {
        for (Proj q : lv.projs) if (q.special == 3 && q.friendly && !q.dead) return true;
        return false;
    }

    /** Dispara el arma 2ª equipada (ids nuevos). Gasta 1 de municion y fija el enfriamiento; el daño ya incluye el nivel de mejora. */
    static void fire(Level lv, Player p, int id, float base) {
        RunState rs = lv.rs;
        if (id == Items.SEC_CHAKRAM && chakramOut(lv)) { p.secCd = 0.12f; return; }   // solo uno en vuelo: no gasta municion
        float d = p.dir();
        float x = p.x + d * 12, y = p.y - 17;
        base = counterBoost(lv, base);
        rs.secAmmo--; spendMag(rs);
        p.secCd = Items.SEC_CD[id] * (1f - 0.12f * rs.secLvl);
        p.wpnT = 0.22f; p.wpnId = id;
        float dm = base * Items.SEC_DMG[id];
        int col = Items.SEC_COL[id];
        switch (id) {
            case Items.SEC_BOW: {
                Proj pr = lv.proj(x, y, d * 460, -34, dm, true, "longarrow", 0xC8E890);
                pr.grav = 150; pr.life = 1.4f; pr.radius = 5; pr.knock = 110; pr.ramp = 0.9f; pr.rampMax = 1.9f; pr.trail = false;
                Snd.sfxv("arrow_shot", 0.8f);
                lv.fx("fx_ring", "pulse", x, y, 0.2f, col, Platform.ADD | Platform.TINT);
                break;
            }
            case Items.SEC_CHAKRAM: {
                Proj pr = lv.proj(x, y, d * 300, 0, dm, true, "chakram", 0xB8F4FF);
                pr.special = 3; pr.passWalls = true; pr.pierce = 999; pr.life = 5f; pr.radius = 9; pr.knock = 90; pr.spin = true; pr.spinRate = d * 22; pr.returnAt = 0.55f; pr.trail = true;
                Snd.sfxv("swing_dagger_2", 0.9f);
                break;
            }
            case Items.SEC_WAND: {
                int el = p.wandEl % 3; p.wandEl++;
                String sp = el == 0 ? "fireball" : el == 1 ? "iceshard" : "bolt";
                int c = el == 0 ? 0xFF8A30 : el == 1 ? 0x7AF0FF : 0xFFE860;
                Proj pr = lv.proj(x, y, d * 340, 0, dm * (el == 2 ? 1.15f : 1f), true, sp, c);
                pr.life = 1.2f; pr.radius = 5; pr.knock = 90;
                if (el == 0) { pr.status = Ent.BURN; pr.statusDur = 3f; pr.statusPow = 6f; }
                else if (el == 1) { pr.status = Ent.FREEZE; pr.statusDur = 1.2f; }
                else { pr.status = Ent.STUN; pr.statusDur = 0.6f; pr.pierce += 1; }
                Snd.sfxv(el == 0 ? "hit_fire" : el == 1 ? "hit_ice" : "magic_bolt", 0.5f);
                lv.fx("fx_ring", "pulse", x, y, 0.28f, c, Platform.ADD | Platform.TINT);
                break;
            }
            case Items.SEC_SPEAR: {
                Proj pr = lv.proj(x, y, d * 600, -10, dm, true, "spear", 0xE8D8B8);
                pr.grav = 40; pr.pierce += 5; pr.pierceGrow += 0.15f; pr.life = 1.0f; pr.radius = 7; pr.knock = 230; pr.trail = false;
                Snd.sfxv("swing_great_1", 0.85f);
                break;
            }
            case Items.SEC_EMBER: {
                for (int i = -1; i <= 1; i++) {
                    float ang = i * 0.17f + lv.rng.f(-0.04f, 0.04f);
                    float sp = 300f + lv.rng.f(-20, 20);
                    Proj pr = lv.proj(x, y, d * (float) Math.cos(ang) * sp, (float) Math.sin(ang) * sp, dm, true, "ember", 0xFF9A40);
                    pr.life = 0.45f; pr.radius = 5; pr.knock = 120; pr.status = Ent.BURN; pr.statusDur = 2.5f; pr.statusPow = 5f;
                }
                Snd.sfxv("hit_fire", 0.8f);
                lv.fx("fx_fire", "burst", x + d * 6, y, 0.5f, 0xFF9A40, Platform.ADD | Platform.TINT);
                break;
            }
            case Items.SEC_SUMMON:
                summon(lv, p, dm);
                break;
            default: fireNew(lv, p, id, dm, x, y, d, col); break;
        }
        p.vx -= d * (id == Items.SEC_SPEAR ? 22 : 10);
        lv.ps.burst(lv.rng, x, y, col, 4, 60, 0.2f, 2, 0, true);
    }

    // ================================================================ cargador / recarga
    static int mag(int id) { return id > 0 && id < Items.SEC_COUNT ? Items.SEC_MAG[id] : 0; }
    static boolean hasMag(int id) { return mag(id) > 0; }

    /** Deja coherente el cargador con el arma equipada y la municion total (arma distinta, partida cargada, municion recogida). */
    static void normMag(RunState rs) {
        if (!hasMag(rs.sec)) { rs.secMag = -1; rs.secMagId = rs.sec; rs.secReload = 0; return; }
        if (rs.secMagId != rs.sec) { rs.secMagId = rs.sec; rs.secMag = -1; rs.secReload = 0; }
        if (rs.secMag < 0) rs.secMag = Math.min(mag(rs.sec), rs.secAmmo);
        rs.secMag = Math.max(0, Math.min(rs.secMag, Math.min(mag(rs.sec), rs.secAmmo)));
    }

    /** true si el arma puede disparar ya (sin cargador: siempre; con cargador: hay disparos cargados y no se esta recargando). */
    static boolean ready(RunState rs) {
        normMag(rs);
        return !hasMag(rs.sec) || (rs.secMag > 0 && rs.secReload <= 0);
    }

    static boolean reloading(RunState rs) { return hasMag(rs.sec) && rs.secReload > 0; }

    /** Un disparo sale del cargador (la municion total ya la gasta quien dispara). */
    static void spendMag(RunState rs) {
        if (!hasMag(rs.sec)) return;
        normMag(rs);
        if (rs.secMag > 0) rs.secMag--;
    }

    /** Recarga automatica: al vaciarse el cargador (y quedar reserva) se recarga sola mientras el arma esta seleccionada. El arma nunca se suelta ni se pide recogerla de nuevo. */
    static void tickReload(Level lv, float dt) {
        RunState rs = lv.rs;
        tickRegen(lv, dt);
        updateSticky(lv, dt);
        normMag(rs);
        if (!hasMag(rs.sec) || !rs.secActive || !lv.pl.alive) return;
        int id = rs.sec;
        if (rs.secReload > 0) {
            rs.secReload -= dt;
            if (rs.secReload <= 0) {
                rs.secReload = 0;
                rs.secMag = Math.min(mag(id), rs.secAmmo);
                lv.pl.reloadDoneT = 0.25f;
                Snd.sfxv("cd_ready", 0.35f);
            }
            return;
        }
        if (rs.secMag <= 0 && rs.secAmmo > 0) {
            rs.secReload = Items.SEC_RELOAD[id] * (1f - 0.1f * rs.secLvl);
            lv.pl.reloadMax = rs.secReload;
            Snd.sfxv("hit_metal_1", 0.3f);
            lv.text(lv.pl.x, lv.pl.y - lv.pl.bh - 10, "recargando", 0xC8C8D0, false);
        }
    }

    /** Texto de municion para HUD/fichas: "cargador/reserva" en armas de cargador, o el total. */
    static String ammoLabel(RunState rs) {
        normMag(rs);
        if (Items.infinite(rs.sec)) return "—";
        if (!hasMag(rs.sec)) return String.valueOf(rs.secAmmo);
        return rs.secMag + "/" + Math.max(0, rs.secAmmo - rs.secMag);
    }

    // ================================================================ armas nuevas a distancia / magicas
    private static Proj orb(Level lv, int id, float x, float y, float vx, float vy, float dm, String spr, int col) {
        Proj pr = lv.proj(x, y, vx, vy, dm, true, spr, col);
        pr.wfx = id; pr.life = 1.2f; pr.radius = 5; pr.knock = 90;
        return pr;
    }

    private static void fireNew(Level lv, Player p, int id, float dm, float x, float y, float d, int col) {
        switch (id) {
            case Items.SEC_TDAGGER: {
                Proj pr = orb(lv, id, x, y, d * 520, 0, dm, "dagger", col);
                pr.life = 1.6f; pr.knock = 70; pr.special = 5; pr.returnAt = 0.6f;     // si no golpea a nadie, vuelve a la mano
                Snd.sfxv("swing_dagger_2", 0.75f);
                break;
            }
            case Items.SEC_SHURIKEN: {
                for (int i = -1; i <= 1; i++) {
                    float a = i * 0.10f;
                    Proj pr = orb(lv, id, x, y, d * (float) Math.cos(a) * 440, (float) Math.sin(a) * 440, dm, "star", col);
                    pr.spin = true; pr.spinRate = d * 28; pr.pierce += 1; pr.life = 0.75f; pr.radius = 4; pr.knock = 45;
                }
                Snd.sfxv("swing_dagger_1", 0.7f);
                break;
            }
            case Items.SEC_ALCHBOMB: {
                Proj g = orb(lv, id, x, y, d * 185 + p.vx * 0.3f, -240, dm, "magma", col);
                g.grav = 900; g.life = 1.2f; g.radius = 6; g.spin = true; g.spinRate = d * 14; g.knock = 160; g.explode = 46; g.explodeFx = "fx_fire:burst"; g.boom = true;
                Snd.sfxv("swing_air", 0.8f);
                break;
            }
            case Items.SEC_STICKYBOMB: {
                Proj g = orb(lv, id, x, y, d * 200 + p.vx * 0.3f, -190, dm, "poison", col);
                g.grav = 760; g.life = 1.4f; g.radius = 6; g.spin = true; g.spinRate = d * 10; g.special = 6; g.explode = 40;
                Snd.sfxv("swing_air", 0.8f);
                break;
            }
            case Items.SEC_ELEMWAND: {
                WeaponFx.State st = p.wfx;
                if (st.resonT <= 0) st.resonStep = 0;
                int step = st.resonStep;
                if (step >= 3) {                      // nova elemental: completar fuego -> hielo -> rayo
                    Proj pr = orb(lv, id, x, y, d * 300, 0, dm * 2.0f, "holy", 0xFFF0B0);
                    pr.wmode = 4; pr.explode = 50; pr.explodeFx = "fx_star:burst"; pr.scale = 1.3f; pr.life = 1.0f; pr.knock = 130;
                    st.resonStep = 0; st.resonT = 0;
                    Snd.sfxv("magic_bolt", 0.7f);
                    lv.fx("fx_ring", "pulse", x, y, 0.5f, 0xFFF0B0, Platform.ADD | Platform.TINT);
                } else {
                    String sp = step == 0 ? "fireball" : step == 1 ? "iceshard" : "bolt";
                    int c = step == 0 ? 0xFF8A30 : step == 1 ? 0x7AF0FF : 0xFFE860;
                    Proj pr = orb(lv, id, x, y, d * (step == 2 ? 600 : 360), 0, dm * (step == 2 ? 0.9f : 1f), sp, c);
                    pr.wmode = 1 + step; if (step == 1) pr.pierce += 1;
                    st.resonStep = step + 1; st.resonT = 3.0f;
                    Snd.sfxv(step == 0 ? "hit_fire" : step == 1 ? "hit_ice" : "magic_bolt", 0.5f);
                    lv.fx("fx_ring", "pulse", x, y, 0.28f, c, Platform.ADD | Platform.TINT);
                }
                break;
            }
            case Items.SEC_FIREWAND: {
                Proj pr = orb(lv, id, x, y, d * 360, 0, dm, "fireball", col);
                Snd.sfxv("hit_fire", 0.5f);
                lv.fx("fx_ring", "pulse", x, y, 0.28f, col, Platform.ADD | Platform.TINT);
                break;
            }
            case Items.SEC_ICEWAND: {
                Proj pr = orb(lv, id, x, y, d * 380, 0, dm, "iceshard", col);
                pr.pierce += 1;
                Snd.sfxv("hit_ice", 0.5f);
                lv.fx("fx_ring", "pulse", x, y, 0.28f, col, Platform.ADD | Platform.TINT);
                break;
            }
            case Items.SEC_STORMWAND: {
                Proj pr = orb(lv, id, x, y, d * 620, 0, dm, "bolt", col);
                pr.life = 0.8f; pr.knock = 60;
                Snd.sfxv("magic_bolt", 0.5f);
                break;
            }
            case Items.SEC_DARKORB: {
                Proj pr = orb(lv, id, x, y, d * 150, 0, dm, "voidorb", col);
                pr.pierce += 2; pr.ramp = 0.9f; pr.rampMax = 1.5f; pr.life = 2.0f; pr.radius = 8; pr.scale = 1.2f; pr.knock = 70;
                Snd.sfxv("hit_magic", 0.6f);
                lv.fx("fx_ring", "pulse", x, y, 0.3f, col, Platform.ADD | Platform.TINT);
                break;
            }
            case Items.SEC_VENOMCAT: {
                Proj pr = orb(lv, id, x, y, d * 280, -40, dm, "poison", col);
                pr.grav = 200; pr.explode = 26; pr.explodeFx = "fx_smoke:big"; pr.life = 1.3f;
                Snd.sfxv("spit", 0.6f);
                break;
            }
            case Items.SEC_BLOODSCEPTER: {
                Proj pr = orb(lv, id, x, y, d * 300, 0, dm, "bloodorb", col);
                Snd.sfxv("hit_blood", 0.6f);
                lv.fx("fx_ring", "pulse", x, y, 0.3f, col, Platform.ADD | Platform.TINT);
                break;
            }
            case Items.SEC_CRYSTAL: {
                for (int i = -1; i <= 1; i += 2) {
                    float a = i * 0.12f;
                    Proj pr = orb(lv, id, x, y, d * (float) Math.cos(a) * 330, (float) Math.sin(a) * 330, dm, "voidorb", col);
                    pr.homing = 380; pr.scale = 0.55f; pr.radius = 4; pr.life = 1.3f; pr.knock = 60;
                }
                Snd.sfxv("hit_magic", 0.55f);
                break;
            }
            case Items.SEC_TALISMAN: {
                Proj g = orb(lv, id, x, y, d * 300, -20, dm, "holy", col);
                g.special = 6; g.life = 1.0f; g.grav = 60; g.radius = 6; g.scale = 0.9f;
                Snd.sfxv("magic_bolt", 0.5f);
                break;
            }
            default: break;
        }
    }

    // ================================================================ daga arrojadiza que vuelve
    /** Si no golpea a nadie, la daga da la vuelta y regresa; al cogerla recuperas la municion. true = retirar. */
    static boolean updateReturnDagger(Level lv, Proj p, float dt) {
        Player pl = lv.pl;
        if (!pl.alive) { p.dead = true; return true; }
        if (!p.back && (p.t >= p.returnAt || lv.solidAtPx(p.x + Mth.sign(p.vx) * 7, p.y))) {
            p.back = true; p.passWalls = true; p.grav = 0; p.hit = null; p.life = Math.max(p.life, 1.2f);
            lv.fx("fx_ring", "pulse", p.x, p.y, 0.2f, p.color, Platform.ADD | Platform.TINT);
        }
        if (p.back) {
            float dx = pl.x - p.x, dy = pl.y - 16 - p.y;
            float dist = (float) Math.sqrt(dx * dx + dy * dy) + 0.001f;
            if (dist < 13f) {
                p.dead = true;
                RunState rs = lv.rs;
                if (rs.sec == Items.SEC_TDAGGER && rs.secAmmo < Items.SEC_AMMO[Items.SEC_TDAGGER] * 2) rs.secAmmo++;
                Snd.sfxv("swing_air", 0.4f);
                return true;
            }
            p.vx = dx / dist * 400f; p.vy = dy / dist * 400f;
        }
        return false;
    }

    // ================================================================ bombas adhesivas y talismanes
    static final class Sticky {
        float x, y, vy, t, fuse, dmg, r;
        Ent host; float ox, oy;
        int id, col;
    }

    /** Pega la bomba/talisman en (e) o, sin enemigo, donde esta. Explota tras la mecha. */
    static void stick(Level lv, Proj p, Ent e) {
        while (lv.stickies.size() >= 4) lv.stickies.remove(0);
        Sticky s = new Sticky();
        s.id = p.wfx; s.col = p.color; s.dmg = p.dmg; s.x = p.x; s.y = p.y;
        boolean tal = s.id == Items.SEC_TALISMAN;
        s.fuse = tal ? 0.9f : 1.0f; s.r = tal ? 52f : 40f;
        if (e != null) { s.host = e; s.ox = p.x - e.x; s.oy = p.y - e.y; }
        lv.stickies.add(s);
        lv.fx("fx_ring", "pulse", s.x, s.y, 0.25f, s.col, Platform.ADD | Platform.TINT);
        Snd.sfxv("hit_metal_1", 0.4f);
    }

    static void updateSticky(Level lv, float dt) {
        if (lv.stickies.isEmpty()) return;
        for (int i = lv.stickies.size() - 1; i >= 0; i--) {
            Sticky s = lv.stickies.get(i);
            s.t += dt;
            boolean boom = s.t >= s.fuse;
            if (s.host != null) {
                if (!s.host.alive) boom = true; else { s.x = s.host.x + s.ox; s.y = s.host.y + s.oy; }
            } else if (!lv.solidAtPx(s.x, s.y + 3)) { s.vy = Math.min(300f, s.vy + 700f * dt); s.y += s.vy * dt; }
            else s.vy = 0;
            if (boom) {
                lv.stickies.remove(i);
                lv.explosion(s.x, s.y, s.r, s.dmg, 150, -1, 0, 0, true);
                WeaponFx.blast(lv, s.id, 0, s.x, s.y, s.r, s.dmg);
                lv.fx(s.id == Items.SEC_TALISMAN ? "fx_fire" : "fx_ice", "burst", s.x, s.y, Math.max(0.6f, s.r / 38f), s.col, Platform.ADD | Platform.TINT);
                lv.ps.burst(lv.rng, s.x, s.y, s.col, 14, 120, 0.4f, 3, 60, true);
                Snd.sfxv("explosion_small", 0.75f);
                lv.shake(2f, 0.15f);
            }
        }
    }

    static void drawStickies(Platform.Gfx g, Level lv) {
        for (Sticky s : lv.stickies) {
            boolean on = ((int) (s.t * (6 + 14 * (s.t / s.fuse)))) % 2 == 0;
            UI.light(g, s.x, s.y, 14, s.col | 0xFF000000, on ? 0.55f : 0.25f);
            UI.iconC(g, Items.SEC_ICON[s.id], s.x, s.y, 0.75f, on ? 1f : 0.7f);
        }
    }

    // ================================================================ energia regenerable
    static void tickRegen(Level lv, float dt) {
        RunState rs = lv.rs;
        int id = rs.sec;
        if (id <= 0 || Items.SEC_REGEN[id] <= 0f) { rs.secRegenT = 0f; return; }
        if (rs.secAmmo >= Items.SEC_AMMO[id]) { rs.secRegenT = 0f; return; }
        rs.secRegenT += dt;
        float per = Items.SEC_REGEN[id] * (1f - 0.1f * rs.secLvl);
        if (rs.secRegenT >= per) { rs.secRegenT -= per; rs.secAmmo++; }
    }

    /** Sin municion con el arma 2ª activa: vuelve a la principal (el jugador no se queda sin poder atacar). */
    static void onEmpty(Level lv, Player p) {
        RunState rs = lv.rs;
        if (!rs.secActive) return;
        rs.secActive = false;
        p.swapAnimT = 0.3f; p.swapIcon = null;
        lv.text(p.x, p.y - p.bh - 20, "Arma principal", 0xE8E0E0, false);
    }

    // ================================================================ chakram
    /** Devuelve true si el chakram debe retirarse (ya lo recogio el jugador). */
    static boolean updateChakram(Level lv, Proj p, float dt) {
        Player pl = lv.pl;
        if (!pl.alive) { p.dead = true; return true; }
        if (!p.back && (p.t >= p.returnAt || lv.solidAtPx(p.x + Mth.sign(p.vx) * 7, p.y))) {
            p.back = true; p.hit = null; p.returnAt = p.t;          // da la vuelta: puede volver a golpear a los mismos enemigos
            lv.fx("fx_ring", "pulse", p.x, p.y, 0.25f, 0xB8F4FF, Platform.ADD | Platform.TINT);
        }
        if (p.back) {
            float dx = pl.x - p.x, dy = pl.y - 16 - p.y;
            float dist = (float) Math.sqrt(dx * dx + dy * dy) + 0.001f;
            if (dist < 13f) {
                p.dead = true;
                Snd.sfxv("swing_air", 0.5f);
                lv.fx("fx_ring", "pulse", pl.x, pl.y - 16, 0.3f, 0xB8F4FF, Platform.ADD | Platform.TINT);
                return true;
            }
            float sp = 330f + 160f * Math.min(1f, (p.t - p.returnAt) / 0.6f);
            p.vx = dx / dist * sp; p.vy = dy / dist * sp;
        }
        return false;
    }

    // ================================================================ invocacion
    static final class Summon {
        float x, y, t, life = 10f, cd = 0.5f, dmg;
        int slot;
    }

    static void summon(Level lv, Player p, float dmg) {
        while (lv.summons.size() >= 2) lv.summons.remove(0);                 // maximo 2: el mas antiguo se disipa
        Summon s = new Summon();
        s.x = p.x + p.dir() * 16; s.y = p.y - 30;
        if (lv.solidAtPx(s.x, s.y)) s.x = p.x; s.dmg = dmg; s.slot = lv.summons.isEmpty() ? 0 : 1 - lv.summons.get(0).slot;
        lv.summons.add(s);
        Snd.sfxv("hit_magic", 0.7f);
        lv.fx("fx_ring", "pulse", s.x, s.y, 0.5f, Items.SEC_COL[Items.SEC_SUMMON], Platform.ADD | Platform.TINT);
        lv.ps.burst(lv.rng, s.x, s.y, Items.SEC_COL[Items.SEC_SUMMON], 12, 70, 0.5f, 2, -10, true);
    }

    static void updateSummons(Level lv, float dt) {
        if (lv.summons.isEmpty()) return;
        Player pl = lv.pl;
        if (!pl.alive || lv.cinematic) { lv.summons.clear(); return; }
        for (int i = lv.summons.size() - 1; i >= 0; i--) {
            Summon s = lv.summons.get(i);
            s.t += dt; s.life -= dt;
            if (s.life <= 0) {
                lv.ps.burst(lv.rng, s.x, s.y, Items.SEC_COL[Items.SEC_SUMMON], 8, 60, 0.4f, 2, -10, true);
                lv.summons.remove(i); continue;
            }
            float tx = pl.x + (s.slot == 0 ? -26 : 26), ty = pl.y - 38 + (float) Math.sin(s.t * 2.4f + s.slot * 2f) * 5;
            if (lv.solidAtPx(tx, ty)) { tx = pl.x; ty = pl.y - 34; }       // junto a una pared: el espiritu se coloca sobre el jugador (nunca dentro del muro)
            float k = Math.min(1f, dt * 4f);
            s.x += (tx - s.x) * k; s.y += (ty - s.y) * k;
            if (Math.abs(s.x - pl.x) > 280) { s.x = tx; s.y = ty; }
            s.cd -= dt;
            if (s.cd <= 0) {
                Ent tg = lv.nearestEnemy(s.x, s.y, 230, true);
                if (tg == null) { s.cd = 0.2f; continue; }
                s.cd = 0.75f;
                float dx = tg.cx() - s.x, dy = tg.cy() - s.y, dist = (float) Math.sqrt(dx * dx + dy * dy) + 0.001f;
                Proj pr = lv.proj(s.x, s.y, dx / dist * 270, dy / dist * 270, s.dmg, true, "spiritbolt", Items.SEC_COL[Items.SEC_SUMMON]);
                pr.src = BlessFx.SRC_COMP; pr.homing = 260; pr.life = 1.1f; pr.radius = 5; pr.knock = 60;
                Snd.sfxv("hit_magic", 0.35f);
            }
        }
    }

    static void drawSummons(Platform.Gfx g, Level lv) {
        if (lv.summons.isEmpty()) return;
        Sheet sh = Assets.fx("fx_proj");
        Anim a = sh.anim("wisp");
        for (Summon s : lv.summons) {
            if (s.life < 1.5f && ((int) (s.t * 14) & 1) == 0) continue;     // parpadea al desvanecerse
            UI.light(g, s.x, s.y, 20, Items.SEC_COL[Items.SEC_SUMMON] | 0xFF000000, 0.35f);
            sh.drawCentered(g, a, a.frameAt(s.t), Math.round(s.x), Math.round(s.y), 0, 1f, 0, 0, 0.95f);
        }
    }

    // ================================================================ cambio de arma
    /** Cambia entre arma principal y secundaria. false si no se pudo (sin secundaria o en enfriamiento). */
    static boolean swap(Level lv, Player p) {
        RunState rs = lv.rs;
        if (p.swapCd > 0) return false;
        if (rs.sec == Items.SEC_NONE) {
            lv.text(p.x, p.y - p.bh - 10, "sin arma secundaria", 0xA0A0A8, false);
            Snd.sfx("ui_error", 0.5f); p.swapCd = 0.3f;
            return false;
        }
        rs.secActive = !rs.secActive;
        p.swapCd = 0.25f; p.atkBuf = 0; p.swapAnimT = 0.32f;
        p.swapIcon = rs.secActive ? Items.SEC_ICON[rs.sec] : "c_" + p.cls.key;
        int col = rs.secActive ? Items.SEC_COL[rs.sec] : (p.cls.color1 & 0xFFFFFF);
        lv.fx("fx_ring", "pulse", p.x, p.y - 18, 0.4f, col, Platform.ADD | Platform.TINT);
        lv.ps.burst(lv.rng, p.x, p.y - 18, col, 8, 70, 0.3f, 2, 0, true);
        Snd.sfxv("swing_air", 0.55f);
        Snd.sfxv("ui_hover", 0.5f);
        return true;
    }

    /** El arma pedida ya es la activa (o se pide la secundaria sin tener ninguna: no hay nada que seleccionar). */
    static boolean isSelected(RunState rs, boolean sec) { return sec ? rs.secActive : !rs.secActive; }

    /** Seleccion directa: true = secundaria, false = principal. No ataca, no gasta municion ni toca cooldowns; si ya esta elegida no hace nada. */
    static boolean select(Level lv, Player p, boolean sec) {
        RunState rs = lv.rs;
        if (isSelected(rs, sec)) return false;
        if (p.swapCd > 0) return false;
        if (sec && rs.sec == Items.SEC_NONE) {
            lv.text(p.x, p.y - p.bh - 10, "sin arma secundaria", 0xA0A0A8, false);
            Snd.sfx("ui_error", 0.5f); p.swapCd = 0.3f;
            return false;
        }
        return swap(lv, p);
    }

    // ================================================================ armas en el suelo
    static boolean freeSpot(Level lv, float x, float gy) {
        if (x < 14 || x > lv.room.pixW - 14 || gy >= lv.room.pixH - 6) return false;
        if (lv.solidAtPx(x, gy - 6) || lv.solidAtPx(x - 5, gy - 6) || lv.solidAtPx(x + 5, gy - 6)) return false;          // dentro de una pared
        for (int dx = -6; dx <= 6; dx += 6) if (lv.room.hazardAt(x + dx, gy - 3) || lv.room.hazardAt(x + dx, gy + 2)) return false;   // sobre pinchos
        if (!Room.isSolid(lv.room.tile((int) Math.floor(x / Room.TS), (int) Math.floor((gy + 2) / Room.TS))) && lv.room.tile((int) Math.floor(x / Room.TS), (int) Math.floor((gy + 2) / Room.TS)) != Room.ONEWAY) return false;
        for (Prop q : lv.props) if (q.kind.equals("weapon") && !q.dead && Math.abs(q.x - x) < 16 && Math.abs(q.y - gy) < 16) return false;
        return true;
    }

    /** Comprobacion de pruebas: el arma ya colocada esta en un punto valido (ignorandose a si misma). */
    static boolean spotOk(Level lv, Prop q) {
        boolean d = q.dead; q.dead = true;
        boolean ok = freeSpot(lv, q.x, q.y);
        q.dead = d; return ok;
    }

    /** Punto seguro cerca de (x,y): suelo firme, sin pinchos, dentro del escenario y sin pisar otra arma. Nunca devuelve null. */
    static float[] safeSpot(Level lv, float x, float y) {
        Player pl = lv.pl;
        float d = pl.dir();
        float[] xs = {x, x + d * 18, x - d * 18, x + d * 34, x - d * 34, x + d * 52, x - d * 52, pl.safeX, pl.safeX + 18, pl.safeX - 18, pl.safeX + 36, pl.safeX - 36};
        for (float cx : xs) {
            float gy = lv.groundBelow(cx, y - 14);
            if (Math.abs(gy - y) > 48 && cx != pl.safeX && cx != pl.safeX + 18 && cx != pl.safeX - 18 && cx != pl.safeX + 36 && cx != pl.safeX - 36) continue;
            if (freeSpot(lv, cx, gy)) return new float[]{cx, gy};
        }
        for (int k = 1; k < 40; k++) {                                   // ultimo recurso: barrido desde el ultimo punto seguro
            for (int sgn = -1; sgn <= 1; sgn += 2) {
                float cx = pl.safeX + sgn * k * 12;
                float gy = lv.groundBelow(cx, pl.safeY - 14);
                if (freeSpot(lv, cx, gy)) return new float[]{cx, gy};
            }
        }
        return new float[]{pl.safeX, pl.safeY};
    }

    /** Coloca un arma en el suelo (hallazgo o arma soltada). Devuelve el objeto. */
    static Prop dropWeapon(Level lv, int id, int ammo, float x, float y, boolean dropped, boolean exact) { return dropWeapon(lv, id, ammo, -1, x, y, dropped, exact); }

    static Prop dropWeapon(Level lv, int id, int ammo, int mag, float x, float y, boolean dropped, boolean exact) {
        float[] s = exact ? new float[]{x, y} : safeSpot(lv, x, y);
        Prop p = new Prop("weapon", s[0], s[1]);
        p.arg = id; p.wAmmo = ammo; p.wMag = mag; p.wRar = Items.SEC_RAR[id]; p.dropped = dropped;
        p.pickLock = dropped ? 0.7f : 0f; p.popT = 0.5f;
        lv.props.add(p);
        lv.rs.wState[id] = 2; lv.rs.markNew("w:" + id);
        int col = Items.SEC_COL[id];
        lv.ps.burst(lv.rng, p.x, p.y - 10, col, 14, 80, 0.5f, 2, 40, true);
        Snd.sfxv("ui_hover", 0.6f);
        return p;
    }

    static void drawGround(Platform.Gfx g, Level lv, Prop p) {
        int id = p.arg;
        if (id <= 0 || id >= Items.SEC_COUNT) return;
        float near = Math.abs(lv.pl.x - p.x) + Math.abs(lv.pl.y - p.y) * 0.4f;
        float pop = p.popT > 0 ? (float) Math.sin(Math.min(1f, p.popT / 0.5f) * Math.PI) * 14f : 0f;
        float bob = (float) Math.sin(p.t * 3.2f) * 2f;
        int rc = ChestLoot.R_COL[Items.SEC_RAR[id]] & 0xFFFFFF;
        UI.light(g, p.x, p.y - 12, 20 + 3 * (float) Math.sin(p.t * 4), rc | 0xFF000000, 0.42f + (near < 34 ? 0.2f : 0f));
        g.rect(Math.round(p.x - 6), Math.round(p.y - 1), 12, 2, 0x55000000, false);                                  // sombra
        UI.iconC(g, Items.SEC_ICON[id], p.x, p.y - 11 + bob - pop, 1f, 1f);
        if (lv.rng.chance(0.03f)) lv.ps.spawn(p.x + lv.rng.f(-7, 7), p.y - 6, lv.rng.f(-4, 4), -lv.rng.f(10, 24), 0.8f, 2, 0, rc, true);
        if (near < 60 && UI.small != null) UI.small.center(g, Items.SEC_NAME[id] + (p.dropped ? " (soltada)" : ""), p.x, p.y - 34, rc, 1f);
    }

    /** Equipa un arma como secundaria (sin comprobaciones). Conserva su municion. */
    static void equip(RunState rs, int id, int ammo) { equip(rs, id, ammo, -1); }

    /** `mag` = cargador que tenia el arma al soltarla (-1 = nueva: viene cargada). Cambiar de arma no regala municion ni acorta la recarga. */
    static void equip(RunState rs, int id, int ammo, int mag) {
        if (rs.sec != 0 && rs.sec != id && rs.wState[rs.sec] == 1) rs.wState[rs.sec] = 3;   // la anterior deja de estar equipada (quien la suelta la marca en el suelo)
        rs.wState[id] = 1;
        rs.sec = id;
        rs.secAmmo = ammo > 0 ? ammo : Items.SEC_AMMO[id];
        rs.secMagId = id; rs.secMag = mag; rs.secReload = 0;
        normMag(rs);
        rs.markNew("w:" + id);
    }

    /**
     * El jugador pulsa INTERACTUAR sobre un arma del suelo. Atomico: la nueva se equipa y la anterior queda en el suelo en un punto seguro.
     * Mismo arma que la equipada: mejora de nivel (o municion si ya esta al maximo). Devuelve el texto de resultado.
     */
    static String takeGround(Level lv, Prop w) {
        RunState rs = lv.rs;
        Player pl = lv.pl;
        if (w == null || w.used || w.dead || w.pickLock > 0) return null;
        int id = w.arg;
        w.used = true; w.dead = true;
        String msg;
        int col = Items.SEC_COL[id];
        if (rs.sec == Items.SEC_NONE) {
            equip(rs, id, w.wAmmo, w.wMag);
            msg = "¡" + Items.SEC_NAME[id] + " equipada!";
        } else if (rs.sec == id) {
            if (rs.secLvl < 3) { rs.secLvl++; msg = "¡" + Items.SEC_NAME[id] + " mejorada! Nivel " + rs.secLvl; }
            else { rs.secAmmo = Math.min(Items.SEC_AMMO[id] * 2, rs.secAmmo + Math.max(2, w.wAmmo)); msg = "Munición de " + Items.SEC_NAME[id]; }
        } else {
            int old = rs.sec, oldAmmo = rs.secAmmo; normMag(rs); int oldMag = rs.secMag;
            dropWeapon(lv, old, oldAmmo, oldMag, pl.x, pl.y, true, false);
            equip(rs, id, w.wAmmo, w.wMag);
            msg = "Intercambio: " + Items.SEC_NAME[id];
            lv.text(pl.x, pl.y - pl.bh - 26, "soltaste " + Items.SEC_NAME[old], 0xB8B8C0, false);
        }
        lv.text(pl.x, pl.y - pl.bh - 12, msg, col, true);
        lv.ps.burst(lv.rng, pl.x, pl.y - 16, col, 18, 100, 0.6f, 3, 40, true);
        lv.fx("fx_star", "burst", pl.x, pl.y - 18, 0.9f, col, Platform.ADD | Platform.TINT);
        Snd.sfx("secret", 0.8f);
        return msg;
    }

    /** Al abandonar la sala: las armas que quedaron en el suelo pasan a "dejadas atras" (politica de limpieza: no se acumulan entre salas). Devuelve el aviso o null. */
    static String leaveRoom(RunState rs, Level lv) {
        if (lv == null) return null;
        StringBuilder sb = new StringBuilder();
        for (Prop q : lv.props) if (q.kind.equals("weapon") && !q.dead && !q.used) {
            if (rs.wState[q.arg] == 2) rs.wState[q.arg] = 3;
            sb.append(sb.length() > 0 ? ", " : "").append(Items.SEC_NAME[q.arg]);
        }
        return sb.length() > 0 ? "Dejaste atrás: " + sb : null;
    }

    // ================================================================ comparacion y fichas
    static final class Line {
        String label, val;
        int cmp = 2;      // -1 peor, 0 igual, 1 mejor, 2 sin comparar
        Line(String l, String v, int c) { label = l; val = v; cmp = c; }
    }

    static float dps(int id) { return id <= 0 ? 0 : Items.SEC_DMG[id] * Items.SEC_SHOTS[id] / Items.SEC_CD[id]; }

    private static int cmp(float a, float b) { return Math.abs(a - b) < 0.02f * Math.max(1f, Math.abs(b)) ? 0 : (a > b ? 1 : -1); }

    private static String f1(float v) { return String.format(java.util.Locale.ROOT, "%.1f", v); }

    /** Lineas de ficha del arma `id`; si `vs` > 0 se compara con esa arma (equipada). Mayor es mejor salvo en el enfriamiento. */
    static List<Line> lines(int id, int vs) {
        List<Line> l = new ArrayList<>();
        boolean c = vs > 0 && vs != id;
        float dmgTot = Items.SEC_DMG[id] * Items.SEC_SHOTS[id];
        String dmg = Items.SEC_SHOTS[id] > 1 ? f1(Items.SEC_DMG[id]) + "x · " + Items.SEC_SHOTS[id] + " proy." : f1(Items.SEC_DMG[id]) + "x";
        l.add(new Line("Daño", dmg, c ? cmp(dmgTot, Items.SEC_DMG[vs] * Items.SEC_SHOTS[vs]) : 2));
        l.add(new Line("Cadencia", f1(1f / Items.SEC_CD[id]) + "/s", c ? cmp(1f / Items.SEC_CD[id], 1f / Items.SEC_CD[vs]) : 2));
        l.add(new Line("Alcance", Math.max(1, Math.round(Items.SEC_RANGE[id] / 16f)) + " casillas", c ? cmp(Items.SEC_RANGE[id], Items.SEC_RANGE[vs]) : 2));
        String am = Items.infinite(id) ? "Ilimitada" : (Items.SEC_REGEN[id] > 0 ? Items.SEC_AMMO[id] + " (regenera)" : Items.SEC_MAG[id] > 0 ? Items.SEC_AMMO[id] + " (carg. " + Items.SEC_MAG[id] + ")" : String.valueOf(Items.SEC_AMMO[id]));
        l.add(new Line("Munición", am, c ? cmp(Items.infinite(id) ? 99 : Items.SEC_AMMO[id], Items.infinite(vs) ? 99 : Items.SEC_AMMO[vs]) : 2));
        l.add(new Line("Potencia", f1(dps(id)) + "x/s", c ? cmp(dps(id), dps(vs)) : 2));
        return l;
    }

    /** Dibuja un marcador de rareza que no depende solo del color: 1 punto, 2 puntos, rombo, estrella. */
    static void rarityMark(Platform.Gfx g, float cx, float cy, int rar, int rgb) {
        int c = 0xFF000000 | rgb;
        int x = Math.round(cx), y = Math.round(cy);
        switch (rar) {
            case 0: g.rect(x - 1, y - 1, 3, 3, c, false); break;
            case 1: g.rect(x - 4, y - 1, 3, 3, c, false); g.rect(x + 1, y - 1, 3, 3, c, false); break;
            case 2: g.rect(x, y - 3, 1, 1, c, false); g.rect(x - 1, y - 2, 3, 1, c, false); g.rect(x - 2, y - 1, 5, 3, c, false); g.rect(x - 1, y + 2, 3, 1, c, false); g.rect(x, y + 3, 1, 1, c, false); break;
            default: g.rect(x - 1, y - 3, 3, 7, c, false); g.rect(x - 3, y - 1, 7, 3, c, false); g.rect(x - 2, y - 2, 1, 1, c, false); g.rect(x + 2, y - 2, 1, 1, c, false); g.rect(x - 2, y + 2, 1, 1, c, false); g.rect(x + 2, y + 2, 1, 1, c, false); break;
        }
    }

    /** Elige un arma para el suelo/recompensa que no sea `exclude`, con rareza segun suerte. */
    static int rollWeapon(RunState rs, Rng r, int exclude) {
        int rar = ChestLoot.rollRarity(r, rs.cb[ChestLoot.LUCK] + rs.stage, 0);
        List<Integer> c = new ArrayList<>();
        for (int pass = 0; pass < 2 && c.isEmpty(); pass++)
            for (int i = 1; i < Items.SEC_COUNT; i++) if (i != exclude && (pass == 1 || Items.SEC_RAR[i] == rar)) c.add(i);
        return c.get(r.i(c.size()));
    }
}
