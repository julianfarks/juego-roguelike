package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/** Simulacion de una sala: fisica, combate, entidades, camara y dibujo del mundo. */
public final class Level {
    /** Eventos hacia la pantalla de run. */
    public interface Listener {
        void onCleared(Level lv);
        void onPlayerDead(Level lv);
        void onBossDead(Level lv);
        void onTutorial(String msg);
    }

    public static final float GRAV = 1500f, FALL_MAX = 540f;

    public final Platform P;
    public final RunState rs;
    public final Room room;
    public final Rng rng;
    public final Input in;
    public Listener listener;
    public float viewW = 480;

    public Player pl;
    public Boss boss;
    public final List<Enemy> enemies = new ArrayList<>();
    final List<Proj> projs = new ArrayList<>();
    final List<Prop> props = new ArrayList<>();
    final List<Arsenal.Sticky> stickies = new ArrayList<>();      // bombas adhesivas y talismanes pegados (temporales)
    final List<Arsenal.Summon> summons = new ArrayList<>();      // espiritus del Cetro de invocacion (temporales, se pierden al salir de la sala)
    final List<Pickup> pickups = new ArrayList<>();
    final List<FxObj> fxs = new ArrayList<>();
    final List<DmgText> texts = new ArrayList<>();
    public final Particles ps = new Particles();

    public float time;
    public float hitstop;
    public float timeScale = 1f;
    // ---- sensacion de combate (ver Impact)
    float slowT, slowScale = 1f;         // ralentizacion breve (parry perfecto): no toca entradas ni temporizadores reales
    public int hitKind;                  // tipo del golpe que se esta aplicando (Impact.LIGHT/HEAVY/CRIT/SPECIAL); lo lee Enemy.onHit
    float hsWinT, hsUsed;                // presupuesto de pausas de impacto por segundo (evita sensacion de congelamiento)
    public float counterT;               // ventana de contraataque tras un parry/esquiva perfectos
    public float flowT;                  // recompensa temporal por encadenar acciones defensivas precisas
    public int defStreak; float defT;    // racha de parries/esquivas perfectas
    float dodgeFxT = -9f;                // antirrebote del efecto de esquiva perfecta
    public int dbgImpacts, dbgHitstops;  // contadores para pruebas
    public float freezeEnemies;         // detiene a los enemigos (Ejecucion Dimensional)
    public float camX, camY, camZoom = 1f;
    float shakeT, shakeMag, flashT, flashMax; int flashColor;
    public float cineBars;              // 0..1 barras de cine
    public boolean cinematic;           // el jugador no puede actuar
    public float camTargetX = Float.NaN, camTargetY = Float.NaN, camTargetZoom = 1f;
    public boolean cleared, bossFight;
    public int toKill;
    /** Rondas: golpes reales recibidos en esta sala, enemigos que habia y si ya se entrego la recompensa de ronda. */
    public int roomHits, roomEnemies;
    public boolean rewarded;
    public Biome biome;
    public Secrets secrets;
    public float darkness;
    final List<int[]> animDeco;
    private final Platform.Img[] bg = new Platform.Img[3];
    public String tutorial;
    final List<Runnable> delayed = new ArrayList<>();
    final List<Float> delayT = new ArrayList<>();
    public float bossBarShow;
    public String unlockTitle, unlockSub;
    private float moteT;

    public Level(Platform p, RunState rs, Room room, Input in) {
        this.P = p; this.rs = rs; this.room = room; this.in = in; this.rng = new Rng(rs.rng.next());
        this.biome = room.biome;
        this.darkness = biome.dark;
        animDeco = room.animated();
        secrets = new Secrets(this);
        for (int i = 0; i < 3; i++) bg[i] = Assets.img("bg/bg_" + biome.key + "_" + i + ".png");
    }

    // ------------------------------------------------------------------ construccion
    public void populate(Player player) {
        pl = player;
        pl.x = room.spawnX; pl.y = room.spawnY;
        pl.vx = pl.vy = 0;
        pl.safeX = pl.x; pl.safeY = pl.y;
        float hpMul = rs.enemyHpMul(), dmgMul = rs.enemyDmgMul();
        for (Room.Spawn s : room.spawns) {
            EnemyDef d = EnemyDef.get(s.enemy);
            if (d == null) continue;
            boolean el = s.elite || (rs.infinite && rng.chance(Infinite.eliteChance(rs.floor) + (Infinite.has(rs, Infinite.M_ELITE) ? 0.15f : 0f)))
                    || (!rs.infinite && rs.campaignEliteChance() > 0 && !s.optional && rng.chance(rs.campaignEliteChance()));
            Enemy e = new Enemy(d, el, hpMul, dmgMul);
            e.x = s.x; e.y = s.y;
            e.home = s.x;
            e.optional = s.optional;
            if (Infinite.has(rs, Infinite.M_FAST)) e.modSpeed = 1.2f;
            else if (rs.campaignSpeedMul() > 1f) e.modSpeed = rs.campaignSpeedMul();
            enemies.add(e);
        }
        toKill = 0;
        for (Enemy e : enemies) if (!e.optional) toKill++;
        roomEnemies = toKill; roomHits = 0; rewarded = false;
        for (Room.PropSpec ps : room.props) addProp(ps);
        secrets.init();
        // salidas
        cleared = toKill == 0 && room.type != Room.BOSS;
        camX = Mth.clamp(pl.x - viewW / 2, 0, Math.max(0, room.pixW - viewW));
        camY = Mth.clamp(pl.y - 160, 0, Math.max(0, room.pixH - ViewSize.h));
    }

    public Prop addProp(Room.PropSpec ps) {
        Prop p = new Prop(ps.kind, ps.x, ps.y);
        p.arg = ps.arg;
        switch (ps.kind) {
            case "altar": p.sheet = Assets.spr("prop_altar"); p.anim = "idle"; break;
            case "forge": p.sheet = Assets.spr("prop_forge"); break;
            case "merchant": p.sheet = Assets.spr("prop_merchant"); if (ps.arg == 1) { p.back = Assets.spr("ops_stall"); p.label = "Mercader errante"; } break;
            case "spirit": p.sheet = Assets.spr("ev_spirit"); p.label = "Espíritu del abismo"; break;
            case "cage": p.sheet = Assets.spr("ev_cage"); p.anim = "idle"; p.label = "Prisionero"; break;
            case "shrine": p.sheet = Assets.spr("ev_shrine"); p.label = ps.arg == 1 ? "Altar de riesgo" : "Santuario de pactos"; break;
            case "cursed": p.sheet = Assets.spr("prop_chest"); p.anim = "closed"; p.label = "Cofre maldito"; break;
            case "relic": p.sheet = Assets.spr("ev_relic"); p.anim = "idle"; p.label = "Reliquia"; break;
            case "fountain": p.sheet = Assets.spr("prop_fountain"); break;
            case "npc": p.sheet = Assets.spr("prop_npc_" + Math.max(0, Math.min(2, ps.arg))); p.anim = "idle"; break;
            case "chest": p.sheet = Assets.spr("prop_chest"); p.anim = "closed"; break;
            case "pot": p.sheet = Assets.spr("prop_pot"); p.anim = "closed"; p.hp = 1; break;
            case "portal": p.sheet = Assets.spr("prop_portal"); break;
            case "sanctuary": p.sheet = Assets.spr("prop_sanctuary"); break;
            case "door": p.sheet = Assets.spr("prop_door"); p.anim = "closed"; break;
            default: break;
        }
        props.add(p);
        return p;
    }

    /** Origen del dano que se esta aplicando (BlessFx.SRC_*): lo fijan el arma, las habilidades, los proyectiles y los efectos de bendicion. */
    public int dmgSrc;
    /** Contador de golpes recibidos por el jugador (lo usan las bendiciones de peligros esquivados). */
    public int hurtMark;

    public void later(float delay, Runnable r) {
        final int src = dmgSrc;
        delayed.add(src == 0 ? r : () -> { int pv = dmgSrc; dmgSrc = src; try { r.run(); } finally { dmgSrc = pv; } });
        delayT.add(delay);
    }

    // ------------------------------------------------------------------ utilidades de mundo
    public boolean solidAtPx(float px, float py) {
        return Room.isSolid(room.tile((int) Math.floor(px / Room.TS), (int) Math.floor(py / Room.TS)));
    }

    /** y del suelo (superficie solida) bajo (px,py), buscando hacia abajo. */
    public float groundBelow(float px, float py) {
        int tx = (int) Math.floor(px / Room.TS);
        for (int ty = Math.max(0, (int) Math.floor(py / Room.TS)); ty < room.h; ty++) {
            int t = room.tile(tx, ty);
            if (Room.isSolid(t) || t == Room.ONEWAY) return ty * Room.TS;
        }
        return room.pixH;
    }

    /** Mueve con colisiones. Devuelve true si toco el suelo este paso. */
    public void move(Ent e, float dt) {
        e.hitWall = false;
        float hw = e.bw / 2f;
        // eje X
        float nx = e.x + e.vx * dt;
        if (e.vx != 0) {
            float top = e.y - e.bh + 1, bot = e.y - 1;
            int ty0 = (int) Math.floor(top / Room.TS), ty1 = (int) Math.floor(bot / Room.TS);
            float edge = e.vx > 0 ? nx + hw : nx - hw;
            int tx = (int) Math.floor(edge / Room.TS);
            boolean hit = false;
            for (int ty = ty0; ty <= ty1; ty++) if (Room.isSolid(room.tile(tx, ty))) { hit = true; break; }
            if (hit) {
                nx = e.vx > 0 ? tx * Room.TS - hw - 0.01f : (tx + 1) * Room.TS + hw + 0.01f;
                e.vx = 0;
                e.hitWall = true;
            }
        }
        e.x = nx;
        // eje Y
        float prevBottom = e.y;
        float ny = e.y + e.vy * dt;
        e.onGround = false;
        e.onOneWay = false;
        if (e.vy >= 0) {
            float bottom = ny;
            int ty = (int) Math.floor(bottom / Room.TS);
            int tx0 = (int) Math.floor((e.x - hw + 1) / Room.TS), tx1 = (int) Math.floor((e.x + hw - 1) / Room.TS);
            float landY = Float.NaN;
            boolean oneway = false;
            for (int tx = tx0; tx <= tx1; tx++) {
                int t = room.tile(tx, ty);
                if (Room.isSolid(t) && bottom >= ty * Room.TS) { landY = ty * Room.TS; oneway = false; break; }
                if (t == Room.ONEWAY && !e.flying && e.dropT <= 0 && prevBottom <= ty * Room.TS + 1.5f && bottom >= ty * Room.TS) { landY = ty * Room.TS; oneway = true; }
            }
            if (!Float.isNaN(landY) && !e.flying) {
                ny = landY; e.vy = 0; e.onGround = true; e.onOneWay = oneway;
            } else if (!Float.isNaN(landY) && e.flying && !oneway) {
                ny = landY; e.vy = 0;
            }
        } else {
            float topY = ny - e.bh;
            int ty = (int) Math.floor(topY / Room.TS);
            int tx0 = (int) Math.floor((e.x - hw + 1) / Room.TS), tx1 = (int) Math.floor((e.x + hw - 1) / Room.TS);
            for (int tx = tx0; tx <= tx1; tx++) {
                if (Room.isSolid(room.tile(tx, ty))) { ny = (ty + 1) * Room.TS + e.bh + 0.01f; e.vy = 0; break; }
            }
        }
        e.y = ny;
        if (e.y > room.pixH + 60) e.y = room.pixH + 60;
    }

    public Ent nearestEnemy(float x, float y, float range, boolean aliveOnly) {
        Ent best = null; float bd = range;
        for (Enemy e : enemies) {
            if (!e.alive || e.untargetable()) continue;
            float d = Mth.dist(x, y, e.cx(), e.cy());
            if (d < bd) { bd = d; best = e; }
        }
        if (boss != null && boss.alive && !boss.invuln()) {
            float d = Mth.dist(x, y, boss.cx(), boss.cy());
            if (d < bd) { bd = d; best = boss; }
        }
        return best;
    }

    public List<Ent> enemiesIn(float x, float y, float r) {
        List<Ent> l = new ArrayList<>();
        for (Enemy e : enemies) if (e.alive && !e.untargetable() && Mth.dist(x, y, e.cx(), e.cy()) <= r + Math.max(e.bw, e.bh) / 3f) l.add(e);
        if (boss != null && boss.alive && Mth.dist(x, y, boss.cx(), boss.cy()) <= r + boss.bw / 2f) l.add(boss);
        return l;
    }

    public List<Ent> enemiesInBox(float rx, float ry, float rw, float rh) {
        List<Ent> l = new ArrayList<>();
        for (Enemy e : enemies) if (e.alive && !e.untargetable() && e.overlaps(rx, ry, rw, rh)) l.add(e);
        if (boss != null && boss.alive && boss.overlaps(rx, ry, rw, rh)) l.add(boss);
        return l;
    }

    public List<Ent> enemiesOnScreen() {
        List<Ent> l = new ArrayList<>();
        for (Enemy e : enemies) if (e.alive && e.x > camX - 20 && e.x < camX + viewW + 20) l.add(e);
        if (boss != null && boss.alive) l.add(boss);
        return l;
    }

    // ------------------------------------------------------------------ efectos
    public FxObj fx(String sheetName, String animName, float x, float y, float scale, int tint, int flags) {
        Sheet s = Assets.fx(sheetName);
        if (s == Sheet.EMPTY) return null;
        if (fxs.size() > 220) fxs.remove(0);   // tope: evita acumulacion en peleas enormes
        FxObj f = new FxObj();
        f.sheet = s; f.anim = s.anim(animName); f.x = x; f.y = y; f.scale = scale; f.tint = tint; f.flags = flags;
        if (f.anim.loop) { f.loop = true; f.life = 0.8f; }   // seguro: un efecto en bucle sin duracion nunca desaparecia
        fxs.add(f);
        return f;
    }

    public FxObj fx(String sheetName, String animName, float x, float y) { return fx(sheetName, animName, x, y, 1f, 0, 0); }

    /** Efecto con mezcla aditiva teñido. */
    public FxObj fxAdd(String sheetName, String animName, float x, float y, float scale, int color) {
        FxObj f = fx(sheetName, animName, x, y, scale, color, Platform.ADD | Platform.TINT);
        return f;
    }

    public void shake(float mag, float time) {
        if (Save.S.reduceFx) mag *= 0.35f;                     // accesibilidad: menos movimiento de camara
        if (mag >= shakeMag || shakeT <= 0) { shakeMag = mag; shakeT = time; }
    }
    public void flash(int rgb, float t) {
        if (Save.S.reduceFx) { if (t > 0.06f) t = 0.06f; }      // accesibilidad: destellos muy breves
        flashColor = rgb; flashT = t; flashMax = t;
    }
    public void hitstop(float t) { if (Save.S.reduceFx) t *= 0.5f; if (t > hitstop) hitstop = t; }

    /** Pausa de impacto de golpes normales: con presupuesto (max 0,30 s de pausa por segundo) para que una lluvia de golpes no congele el juego. */
    public void hitstopSoft(float t) {
        if (Save.S.reduceFx) t *= 0.5f;
        if (hsUsed + t > 0.30f) return;
        if (t > hitstop) { hsUsed += t - Math.max(0f, hitstop); hitstop = t; dbgHitstops++; }
    }

    /** Ralentizacion breve del mundo (no se acumula; desactivada con efectos reducidos). */
    public void slowmo(float dur, float scale) {
        if (Save.S.reduceFx || slowT > 0) return;
        slowT = dur; slowScale = scale;
    }

    public void text(float x, float y, String s, int color, boolean big) {
        DmgText d = new DmgText();
        d.x = x; d.y = y; d.vy = -34; d.life = d.maxLife = big ? 0.9f : 0.7f; d.text = s; d.color = color; d.big = big;
        if (texts.size() > 40) texts.remove(0);
        texts.add(d);
    }

    /** Numero de dano legible: los golpes rapidos al mismo enemigo se suman en un solo numero, el critico es mayor, dorado y con "!";
     *  sobre los jefes se desplaza a un lado para no taparlos. */
    void dmgText(Ent e, float dmg, boolean crit) {
        int amt = Math.round(dmg);
        for (int i = texts.size() - 1; i >= 0 && i >= texts.size() - 8; i--) {
            DmgText d = texts.get(i);
            if (d.target == e && !crit && !d.crit && d.life > d.maxLife - 0.22f) {
                d.amount += amt; d.text = String.valueOf(d.amount); d.life = Math.max(d.life, d.maxLife * 0.8f);
                return;
            }
        }
        boolean boss = e instanceof Boss;
        float ox = boss ? (rng.chance(0.5f) ? 1 : -1) * (e.bw * 0.5f + 12f) : rng.f(-6, 6);
        float oy = boss ? -e.bh * 0.55f : -e.bh - 4;
        DmgText d = new DmgText();
        d.x = e.x + ox; d.y = e.y + oy; d.vy = crit ? -46 : -34; d.life = d.maxLife = crit ? 1.0f : 0.7f;
        d.amount = amt; d.text = crit ? amt + "!" : String.valueOf(amt); d.color = crit ? 0xFFD25A : 0xFFFFFF; d.big = crit; d.crit = crit; d.target = e;
        if (texts.size() > 40) texts.remove(0);
        texts.add(d);
    }

    public void spawnProj(Proj p) { projs.add(p); }

    public Proj proj(float x, float y, float vx, float vy, float dmg, boolean friendly, String sprite, int color) {
        Proj p = new Proj();
        p.x = x; p.y = y; p.vx = vx; p.vy = vy; p.dmg = dmg; p.friendly = friendly; p.sprite = sprite; p.color = color;
        if (friendly) {
            p.src = dmgSrc == BlessFx.SRC_S || dmgSrc == BlessFx.SRC_X ? dmgSrc : BlessFx.SRC_P;
            BlessFx.tuneProj(this, p);
        }
        projs.add(p);
        return p;
    }

    // ------------------------------------------------------------------ daño
    /** Daño base a enemigo/jefe. Devuelve el daño aplicado. */
    /** Los pinchos tambien danan a los enemigos: 30% de su vida maxima (minimo 20) cada 0.6 s mientras sigan en contacto. */
    static final float SPIKE_CD = 0.6f;
    /** Contadores para pruebas: golpes de pinchos a enemigos y golpes al jugador. */
    public static int dbgTrapHits, dbgHurt;
    void trapDamage(Enemy e, float dt) {
        if (!e.alive || e.untargetable()) { e.prevY = e.y; return; }
        if (e.trapCd > 0) e.trapCd -= dt;
        if (Float.isNaN(e.prevY)) e.prevY = e.y;
        float y0 = Math.min(e.prevY, e.y), y1 = Math.max(e.prevY, e.y);
        e.prevY = e.y;
        if (e.trapCd > 0) return;
        boolean hit = false;
        float hw = Math.max(2, e.bw * 0.4f);
        // recorrido vertical completo desde el fotograma anterior (evita atravesar los pinchos al caer rapido)
        for (float yy = y0; yy <= y1 + 0.01f && !hit; yy += 4f) {
            for (int k = -1; k <= 1 && !hit; k++) {
                float xx = e.x + k * hw;
                if (room.hazardAt(xx, yy - 4) || room.hazardAt(xx, yy - e.bh * 0.5f)) hit = true;
            }
        }
        if (!hit && (room.hazardAt(e.x, y1 - 4) || room.hazardAt(e.x, y1 - e.bh + 3))) hit = true;
        if (!hit) return;
        e.trapCd = SPIKE_CD;
        dbgTrapHits++;
        float dmg = Math.max(20f, e.maxHp * 0.30f);
        Snd.sfxAt("spikes", e.x, camX + viewW / 2, 0.8f);
        ps.burst(rng, e.x, e.y - 6, 0xC03040, 8, 90, 0.4f, 2, 200, false);
        damageEnemy(e, dmg, false, 0, -120);
        if (e.alive && !e.flying) e.vy = Math.min(e.vy, -160f);   // rebote de dolor, para que no se quede clavado
        if (DebugBot.trace) System.out.println("PINCHOS: " + ((Enemy) e).def.id + " -" + Math.round(dmg) + " hp=" + Math.round(e.hp) + "/" + Math.round(e.maxHp));
    }

    public float damageEnemy(Ent e, float dmg, boolean crit, float kx, float ky) {
        if (e == null || !e.alive) return 0;
        if (e instanceof Boss) {
            Boss b = (Boss) e;
            if (b.invuln()) return 0;
        }
        if (e instanceof Enemy) {
            Enemy en = (Enemy) e;
            if (en.untargetable()) return 0;
            dmg = en.filterDamage(this, dmg, kx, ky);
        }
        if (rs.stats.exec > 0 && e.hp / e.maxHp < 0.3f) dmg *= 1 + rs.stats.exec;
        if (e.st[Ent.FREEZE] > 0) dmg *= 1.25f;
        final int src = dmgSrc;
        dmg = BlessFx.modDamage(this, e, dmg, crit, src);
        e.hp -= dmg;
        e.hitFlash = 0.1f;
        dmgText(e, dmg, crit);
        if (e instanceof Enemy) ((Enemy) e).onHit(this, kx, ky, dmg);
        else if (e instanceof Boss) ((Boss) e).onHit(this, dmg);
        rs.ult = Math.min(100f, rs.ult + dmg * 0.06f * rs.stats.ultGain);
        BlessFx.afterDamage(this, e, dmg, crit, src);
        if (e.hp <= 0 && e.alive) {
            e.hp = 0;
            if (e instanceof Enemy) ((Enemy) e).die(this);
            else if (e instanceof Boss) { ((Boss) e).die(this); BlessFx.onBossDead(this); }
            BlessFx.onKill(this, e, src);
        }
        return dmg;
    }

    /** Efectos al golpear con el arma. */
    public void onWeaponHit(Ent e, float dmg, boolean crit, int combo) {
        Stats s = rs.stats;
        if (rng.chance(s.burn)) e.applyStatus(Ent.BURN, 3f, 6f + rs.stats.dmgMul * 3f);
        if (rng.chance(s.freeze)) { if (rng.chance(0.25f)) e.applyStatus(Ent.FREEZE, 1.6f, 0); else e.applyStatus(Ent.SLOW, 3f, 0); }
        if (rng.chance(s.poison)) e.applyStatus(Ent.POISON, 4f, 5f + rs.stats.dmgMul * 2f);
        if (rng.chance(s.shock)) chain(e, dmg * 0.6f, 3);
        float ls = s.lifesteal + BlessFx.sumMod(this, BRule.M_LIFESTEAL, e, BlessFx.SRC_W);
        if (ls > 0) healPlayer(dmg * ls);
        rs.ult = Math.min(100f, rs.ult + 2.5f * s.ultGain);
        BlessFx.onHit(this, e, dmg, crit, combo);
    }

    /** Rayo encadenado desde un enemigo. */
    public void chain(Ent from, float dmg, int jumps) {
        jumps = Math.min(9, jumps + Math.round(BlessFx.sv(rs, BRule.M_CHAINJUMPS)));
        Ent cur = from;
        java.util.HashSet<Ent> hit = new java.util.HashSet<>();
        hit.add(from);
        float px = from.cx(), py = from.cy();
        for (int i = 0; i < jumps; i++) {
            Ent best = null; float bd = 110;
            for (Enemy e : enemies) if (e.alive && !hit.contains(e)) { float d = Mth.dist(px, py, e.cx(), e.cy()); if (d < bd) { bd = d; best = e; } }
            if (best == null) break;
            hit.add(best);
            lightning(px, py, best.cx(), best.cy());
            damageEnemy(best, dmg, false, 0, 0);
            best.applyStatus(Ent.SHOCK, 0.8f, 0);
            px = best.cx(); py = best.cy();
        }
        Snd.sfxv("hit_shock", 0.6f);
    }

    /** Tirada de critico del jugador contra e (probabilidad base + bendiciones). Un golpe marcado como critico seguro (NEXTHIT) lo fuerza. */
    public boolean rollCrit(Ent e) {
        int src = dmgSrc;
        float ch = rs.stats.critChance + BlessFx.critBonus(this, e, src);
        return BlessFx.forcedCrit(this, src) || rng.chance(Math.min(0.95f, ch));
    }

    public float critMulOf(Ent e) { return rs.stats.critMul + BlessFx.critMulBonus(this, e, dmgSrc); }

    /** Linea de rayo visual entre dos puntos. */
    public void lightning(float x1, float y1, float x2, float y2) {
        int n = 6;
        float lx = x1, ly = y1;
        for (int i = 1; i <= n; i++) {
            float t = i / (float) n;
            float nx = Mth.lerp(x1, x2, t) + (i == n ? 0 : rng.f(-6, 6)), ny = Mth.lerp(y1, y2, t) + (i == n ? 0 : rng.f(-6, 6));
            lines.add(new float[]{lx, ly, nx, ny, 0.18f, 0x9AE8FF});
            lx = nx; ly = ny;
        }
        ps.burst(rng, x2, y2, 0xBFF0FF, 8, 90, 0.3f, 2, 0, true);
    }

    final List<float[]> lines = new ArrayList<>();

    /** Multiplicador de curacion de la sala (1 = normal; los desafios de "curacion reducida" lo bajan). */
    public float healMul = 1f;
    /** Mientras sea true la sala no se da por despejada aunque no queden enemigos (desafio de resistencia). */
    public boolean holdClear;

    /** Anade un enemigo en mitad de la sala (emboscada, oleadas de desafio). Cuenta para despejar la sala. */
    public Enemy spawnEnemy(String id, boolean elite, float x, float y) {
        EnemyDef d = EnemyDef.get(id);
        if (d == null) return null;
        Enemy e = new Enemy(d, elite, rs.enemyHpMul(), rs.enemyDmgMul());
        e.x = x; e.y = y; e.home = x;
        enemies.add(e);
        toKill++; roomEnemies++;
        cleared = false;
        fxAdd("fx_ring", "pulse", x, y - 14, 0.8f, 0xA050E0);
        ps.burst(rng, x, y - 14, 0xA050E0, 10, 80, 0.5f, 2, -10, true);
        return e;
    }

    public void healPlayer(float amt) {
        if (amt <= 0 || pl == null || !pl.alive) return;
        amt *= Infinite.healMul(rs) * BlessFx.healMul(rs) * healMul;
        float before = rs.hp;
        rs.hp = Math.min(rs.stats.maxHp, rs.hp + amt);
        float got = rs.hp - before;
        if (got >= 1f) text(pl.x, pl.y - pl.bh - 6, "+" + Math.round(got), 0x6AE08A, false);
    }

    /** Daño por area con circulo. */
    public int explosion(float x, float y, float r, float dmg, float knock, int status, float sDur, float sPow, boolean fromPlayer) {
        int n = 0;
        if (fromPlayer) {
            breakCircle(x, y, r * 0.8f, 3);
            for (Ent e : enemiesIn(x, y, r)) {
                float dir = Mth.sign(e.x - x);
                if (dir == 0) dir = 1;
                boolean crit = rollCrit(e);
                float dd = dmg * (crit ? critMulOf(e) : 1f);
                damageEnemy(e, dd, crit, dir * knock, -knock * 0.4f);
                if (status >= 0) e.applyStatus(status, sDur, sPow);
                n++;
            }
        } else if (pl != null && pl.alive && Mth.dist(x, y, pl.cx(), pl.cy()) <= r + 8) {
            hurtPlayer(dmg, x, status, sDur);
            n++;
        }
        return n;
    }

    /** El jugador recibe daño. src_x = origen para el empuje. */
    public boolean hurtPlayer(float dmg, float srcX, int status, float sDur) {
        if (rs.sandbox) return false;
        Player p = pl;
        if (p == null || !p.alive || cinematic) return false;
        if (p.invuln > 0 || p.rolling()) { if (p.rolling()) { BlessFx.onDodge(this); Impact.perfectDodge(this, p); } return false; }
        dbgHurt++;
        Stats s = rs.stats;
        boolean blocked = false;
        if (p.guarding && (srcX - p.x) * p.dir() > -6) {
            if (p.parryT > 0) { parryFx(p, srcX, false); return false; }
            blocked = true;
            dmg *= Items.SH_BLK[rs.shield];
            status = -1;
        }
        dmg *= s.dmgTaken * (rs.asc > 0 ? 1 + 0.05f * rs.asc : 1f) * BlessFx.takenMul(this);
        if (p.skinT > 0) dmg *= 0.4f;
        if (p.shield > 0) {
            float ab = Math.min(p.shield, dmg);
            p.shield -= ab; dmg -= ab;
            text(p.x, p.y - p.bh - 8, "bloqueo", 0x7AF0FF, false);
            Snd.sfx("block", 0.8f);
            fxAdd("fx_hit", "magic", p.x, p.y - 14, 1f, 0x7AF0FF);
            BlessFx.onBlocked(this, ab);
            if (dmg <= 0.5f) { p.invuln = 0.35f; return false; }
        }
        rs.hp -= dmg;
        rs.damageTaken += Math.round(dmg);
        roomHits++;
        p.invuln = blocked ? 0.4f : 0.9f;
        p.hitFlash = 0.12f;
        float dir = p.x >= srcX ? 1 : -1;
        if (blocked) {
            p.vx = dir * 90;
            Snd.sfx("hit_metal_1", 0.9f);
            fx("fx_hit", "spark", p.x + p.dir() * 10, p.y - 16, 1f, 0, 0);
            ps.burst(rng, p.x + p.dir() * 10, p.y - 16, 0xB8C8E0, 8, 100, 0.3f, 2, 120, true);
            if (rs.shield == 3) explosion(p.x, p.y - 14, 40, p.baseDmg(this) * 1.2f, 160, Ent.BLEED, 3f, 4f, true);
        } else {
            p.vx = dir * 150; p.vy = -170;
            p.onGround = false;
            p.hurtT = 0.28f;
            p.cancelAction();
        }
        if (status >= 0) p.applyStatus(status, sDur, status == Ent.BURN || status == Ent.POISON || status == Ent.BLEED ? 4f : 0f);
        text(p.x, p.y - p.bh - 8, String.valueOf(Math.round(dmg)), 0xFF5A5A, true);
        Snd.sfx(rng.chance(0.5f) ? "hurt_1" : "hurt_2", 1f);
        hitstop(0.09f);
        shake(4f, 0.25f);
        flash(0xFF2030, 0.18f);
        if (Save.S.vibOn) P.vibrate(40);
        p.furia = 0;
        hurtMark++;
        if (rs.hp <= 0) playerDeath();
        else BlessFx.onHurt(this, dmg);
        return true;
    }

    public void playerDeath() {
        Player p = pl;
        if (rs.stats.revive > 0 && !rs.reviveUsed) {
            rs.reviveUsed = true;
            rs.hp = rs.stats.maxHp * rs.stats.revivePct;
            p.invuln = 2.5f;
            text(p.x, p.y - 40, "¡Segunda oportunidad!", 0xFFD25A, true);
            Snd.sfx("heal", 1f);
            fx("fx_heal", "rise", p.x, p.y - 14, 1.4f, 0, 0);
            explosion(p.x, p.cy(), 80, 40, 260, -1, 0, 0, true);
            ps.burst(rng, p.x, p.cy(), 0xFFD25A, 40, 160, 0.8f, 3, 0, true);
            flash(0xFFFFFF, 0.3f);
            return;
        }
        rs.hp = 0;
        p.die();
        Snd.sfx("death", 1f);
        Snd.stopMusic(600);
        shake(6f, 0.4f);
        hitstop(0.2f);
        timeScale = 0.45f;
    }

    // ------------------------------------------------------------------ botin
    public void drop(int type, float x, float y, int value) {
        Pickup p = new Pickup(type, x, y, value);
        p.vx = rng.f(-60, 60); p.vy = rng.f(-200, -120);
        pickups.add(p);
    }

    public void dropGold(float x, float y, int total) {
        int n = Math.min(6, Math.max(1, total / 6));
        for (int i = 0; i < n; i++) drop(Pickup.GOLD, x, y, Math.max(1, total / n));
    }

    public void dropSouls(float x, float y, int total) {
        int n = Math.min(4, Math.max(1, total / 2));
        for (int i = 0; i < n; i++) drop(Pickup.SOUL, x, y, Math.max(1, Math.round(total / (float) n)));
    }

    // ------------------------------------------------------------------ actualizacion
    public void update(float rawDt) {
        hsWinT += rawDt; if (hsWinT >= 1f) { hsWinT = 0; hsUsed = 0; }
        if (hitstop > 0) {
            hitstop -= rawDt;
            in.keep = true;                               // no perder pulsaciones durante la pausa de impacto
            // los efectos visuales siguen un poco
            updateFx(rawDt * 0.3f);
            updateCamera(rawDt);
            return;
        }
        float dt = rawDt * timeScale;
        if (slowT > 0) { slowT -= rawDt; dt *= slowScale; }
        if (counterT > 0) counterT -= rawDt;
        if (flowT > 0) flowT -= rawDt;
        if (defT > 0) { defT -= rawDt; if (defT <= 0) defStreak = 0; }
        time += dt;
        moteT -= dt;
        if (moteT <= 0) {
            moteT = 0.09f;
            ps.spawn(camX + rng.f(0, viewW), camY + rng.f(0, ViewSize.h), rng.f(-6, 6), -rng.f(4, 18), rng.f(2.2f, 4f), 1, 0, biome.color, true);
        }
        if (pl.alive || timeScale < 1f) pl.update(this, dt);
        secrets.update(dt);
        updateCompanion(dt);
        Arsenal.updateSummons(this, dt);
        Arsenal.tickReload(this, dt);
        if (!pl.alive && timeScale < 1f) timeScale = Math.min(1f, timeScale + rawDt * 0.0f);
        if (freezeEnemies > 0) freezeEnemies -= dt;
        long bt0 = System.nanoTime();
        BlessFx.update(this, dt);
        BlessFx.dbgNsUpdate += System.nanoTime() - bt0;
        if (freezeEnemies <= 0) {
            float edt = BlessFx.enemyDt(this, dt);
            for (Enemy e : enemies) e.update(this, edt);
            for (Enemy e : enemies) trapDamage(e, edt);
            if (boss != null) boss.update(this, edt);
        } else {
            for (Enemy e : enemies) e.animFrozen(dt);
        }
        separateEnemies(dt);
        for (int i = enemies.size() - 1; i >= 0; i--) if (enemies.get(i).remove) enemies.remove(i);
        updateProjs(dt);
        updatePickups(dt);
        for (Prop p : props) updateProp(p, dt);
        props.removeIf(p -> p.dead);
        updateFx(dt);
        // retardados
        for (int i = delayed.size() - 1; i >= 0; i--) {
            float t = delayT.get(i) - dt;
            if (t <= 0) { Runnable r = delayed.remove(i); delayT.remove(i); r.run(); }
            else delayT.set(i, t);
        }
        // fin de sala
        if (!cleared && !bossFight && !holdClear && room.type != Room.BOSS) {
            int alive = 0;
            for (Enemy e : enemies) if (e.alive || !e.remove && !e.deadAnimDone()) { if (e.alive && !e.optional) alive++; }
            if (alive == 0 && !pendingSpawns()) {
                cleared = true;
                if (listener != null) listener.onCleared(this);
            }
        }
        if (shakeT > 0) shakeT -= rawDt;
        if (flashT > 0) flashT -= rawDt;
        if (cinematic) cineBars = Math.min(1f, cineBars + rawDt * 2.5f);
        else cineBars = Math.max(0f, cineBars - rawDt * 2.5f);
        updateCamera(rawDt);
        ps.update(dt);
        for (Iterator<float[]> it = lines.iterator(); it.hasNext(); ) { float[] l = it.next(); l[4] -= dt; if (l[4] <= 0) it.remove(); }
    }

    /** Empuje suave entre enemigos terrestres solapados: evita que se apilen en un punto y se queden atascados. */
    private void separateEnemies(float dt) {
        int n = enemies.size();
        for (int i = 0; i < n; i++) {
            Enemy a = enemies.get(i);
            if (!a.alive || a.flying) continue;
            for (int j = i + 1; j < n; j++) {
                Enemy b = enemies.get(j);
                if (!b.alive || b.flying || Math.abs(a.y - b.y) > 10) continue;
                float min = (a.bw + b.bw) * 0.38f, d = b.x - a.x;
                if (Math.abs(d) >= min) continue;
                float push = (min - Math.abs(d)) * Math.min(1f, dt * 8f) * 0.5f;
                float dir = d == 0 ? (i % 2 == 0 ? 1 : -1) : Math.signum(d);
                shove(a, -dir * push);
                shove(b, dir * push);
            }
        }
    }

    private void shove(Enemy e, float dx) {
        float nx = e.x + dx, edge = nx + Math.signum(dx) * e.bw / 2f;
        for (int k = 1; k <= 2; k++) {
            if (Room.isSolid(room.tile((int) Math.floor(edge / Room.TS), (int) Math.floor((e.y - k * 8f) / Room.TS)))) return;
        }
        if (!e.flying) {                     // un empujon entre enemigos nunca los mete en pinchos ni los saca del suelo
            float hw = Math.max(2f, e.bw * 0.4f) + 3f, sg = Math.signum(dx);
            float fx = nx + sg * hw;
            int r0 = (int) Math.floor((e.y - e.bh + 1) / Room.TS), r1 = (int) Math.floor((e.y - 1) / Room.TS);
            int tx = (int) Math.floor(fx / Room.TS);
            for (int ty = r0; ty <= r1; ty++) if (EnemyNav.hazard(room.tile(tx, ty))) return;
            int below = room.tile((int) Math.floor((nx + sg * e.bw / 2f) / Room.TS), (int) Math.floor((e.y + 4) / Room.TS));
            if (!(Room.isSolid(below) || below == Room.ONEWAY) && e.onGround) return;
        }
        e.x = nx;
    }

    private boolean pendingSpawns() { return !delayed.isEmpty() && false; }

    void updateFx(float dt) {
        for (FxObj f : fxs) {
            if (f.delay > 0) { f.delay -= dt; continue; }
            f.t += dt;
            if (f.follow != null) { f.x = f.follow.x + f.fox; f.y = f.follow.y + f.foy; }
            if (f.life >= 0) { f.life -= dt; if (f.life <= 0) f.dead = true; }
            else if (!f.loop && f.anim.done(f.t)) f.dead = true;
        }
        fxs.removeIf(f -> f.dead);
        for (DmgText d : texts) { d.life -= dt; d.y += d.vy * dt; d.vy *= 0.94f; }
        texts.removeIf(d -> d.life <= 0);
    }

    void updateProp(Prop p, float dt) {
        p.t += dt;
        p.animT += dt;
        if (p.shakeT > 0) p.shakeT -= dt;
        if (p.pickLock > 0) p.pickLock -= dt;
        if (p.popT > 0) p.popT -= dt;
        if (p.kind.equals("pot") && p.open && p.sheet.anim("break").done(p.animT)) p.dead = true;
    }

    // ------------------------------------------------------------------ proyectiles
    private void updateProjs(float dt) {
        // por indice sobre el tamano inicial: los proyectiles nuevos (divisiones, explosiones) se anaden sin romper la iteracion
        // (se itera sobre una copia: matar a un jefe en mitad del bucle borra los proyectiles hostiles y rompia el indice)
        final Proj[] snap = projs.toArray(new Proj[0]);
        final int before = snap.length;
        for (int pi = 0; pi < before; pi++) {
            Proj p = snap[pi];
            if (p.dead) continue;
            if (projs.size() != before && !projs.contains(p)) continue;   // ya retirado durante este mismo cuadro
            p.t += dt;
            p.life -= dt;
            if (p.life <= 0) { projDie(p, false); continue; }
            if (p.ramp > 0) { if (p.dmg0 <= 0) p.dmg0 = p.dmg; p.dmg = p.dmg0 * Math.min(p.rampMax, 1f + p.ramp * p.t); }
            if (p.special == 3 && Arsenal.updateChakram(this, p, dt)) continue;
            if (p.special == 5 && Arsenal.updateReturnDagger(this, p, dt)) continue;
            if (p.homing > 0) {
                Ent tgt = p.friendly ? nearestEnemy(p.x, p.y, 200, true) : (pl.alive ? pl : null);
                if (tgt != null) {
                    float dx = tgt.cx() - p.x, dy = tgt.cy() - p.y;
                    float d = (float) Math.sqrt(dx * dx + dy * dy) + 0.001f;
                    float sp = (float) Math.sqrt(p.vx * p.vx + p.vy * p.vy);
                    p.vx += dx / d * p.homing * dt; p.vy += dy / d * p.homing * dt;
                    float ns = (float) Math.sqrt(p.vx * p.vx + p.vy * p.vy) + 0.001f;
                    p.vx = p.vx / ns * sp; p.vy = p.vy / ns * sp;
                }
            }
            p.vy += p.grav * dt;
            p.x += p.vx * dt;
            p.y += p.vy * dt;
            if (p.special == 1) { // onda pegada al suelo
                float gy = groundBelow(p.x, p.y - 10);
                p.y = gy - 6;
                if (solidAtPx(p.x + Mth.sign(p.vx) * 6, p.y - 4)) { projDie(p, true); continue; }
            } else if (!p.passWalls && solidAtPx(p.x, p.y)) {
                if (p.special == 2) { p.vy = -Math.abs(p.vy) * 0.6f; p.y -= 3; p.vx *= 0.7f; continue; }
                if (p.friendly) breakCircle(p.x, p.y, 6, 2);
                if (p.friendly && p.bounces > 0) { p.bounces--; p.vx = -p.vx; p.x += Mth.sign(p.vx) * 4; p.life = Math.max(p.life, 0.4f); continue; }
                projDie(p, true);
                continue;
            }
            if (p.trail && p.t > 0.02f && rng.chance(0.5f)) ps.spawn(p.x, p.y, rng.f(-10, 10), rng.f(-10, 10), 0.25f, 2, 0, p.color, true);
            if (p.friendly) {
                for (Ent e : enemiesIn(p.x, p.y, p.radius)) {
                    if (p.hit != null && p.hit.contains(e)) continue;
                    if (p.special == 6) { Arsenal.stick(this, p, e); p.dead = true; break; }        // bomba adhesiva / talisman: se pega al enemigo
                    if (p.boom) { projDie(p, false); break; }                                         // bomba: solo daña al estallar
                    int pvSrc = dmgSrc;
                    dmgSrc = p.src == 0 ? BlessFx.SRC_P : p.src;
                    try {
                        boolean crit = rollCrit(e);
                        float d = p.dmg * (crit ? critMulOf(e) : 1f);
                        if (p.wfx > 0) d *= WeaponFx.preMul(this, p.wfx, e);
                        damageEnemy(e, d, crit, Mth.sign(p.vx) * p.knock, -40);
                        if (p.status >= 0) e.applyStatus(p.status, p.statusDur, p.statusPow);
                        onWeaponHitLite(e, d);
                        if (p.wfx > 0) {
                            WeaponFx.afterHit(this, p.wfx, e, d, crit, false, Mth.sign(p.vx));
                            if (p.wfx == Items.SEC_ELEMWAND) WeaponFx.elemHit(this, p, e, d);
                        }
                    } finally { dmgSrc = pvSrc; }
                    Snd.sfxv("hit_magic", 0.55f);
                    fx("fx_hit", "magic", p.x, p.y, 1f, p.color, Platform.ADD | Platform.TINT);
                    if (p.pierce > 0) {
                        if (p.hit == null) p.hit = new java.util.HashSet<>(); p.hit.add(e); p.pierce--;
                        if (p.pierceGrow > 0) p.dmg *= 1f + p.pierceGrow;
                        if (p.explode > 0) explode(p);
                    } else if (p.bounces > 0) {
                        p.bounces--; if (p.hit == null) p.hit = new java.util.HashSet<>(); p.hit.add(e);
                        p.vx = -p.vx * 0.9f; p.vy = -Math.abs(p.vy) * 0.5f - 60f;
                        p.life = Math.max(p.life, 0.5f);
                    } else { projDie(p, false); break; }
                }
                // romper vasijas
                for (Prop pr : props) if (pr.kind.equals("pot") && !pr.open && Math.abs(pr.x - p.x) < 12 && Math.abs(pr.y - 8 - p.y) < 14) breakPot(pr);
            } else if (pl.alive && pl.overlaps(p.x - p.radius, p.y - p.radius, p.radius * 2, p.radius * 2)) {
                if (pl.guarding && pl.parryT > 0 && p.explode <= 0 && (p.x - pl.x) * pl.dir() > -6) {
                    parryFx(pl, p.x, true);
                    p.friendly = true; p.vx = -p.vx * 1.5f; p.vy = -p.vy * 0.3f; p.dmg = pl.baseDmg(this) * (2.5f + 0.5f * rs.shield);
                    p.hit = null; p.life = 2f; p.pierce = Math.max(p.pierce, 1); p.color = 0xFFE070; p.status = -1;
                    continue;
                }
                if (p.explode > 0) { projDie(p, false); }
                else {
                    if (hurtPlayer(p.dmg, p.x - Mth.sign(p.vx), p.status, p.statusDur)) { }
                    projDie(p, false);
                }
            }
        }
        projs.removeIf(p -> p.dead);
    }

    private void onWeaponHitLite(Ent e, float dmg) {
        if (rs.stats.lifesteal > 0) healPlayer(dmg * rs.stats.lifesteal * 0.5f);
    }

    private void explode(Proj p) {
        explosion(p.x, p.y, p.explode, p.dmg, 120, p.status, p.statusDur, p.statusPow, p.friendly);
        if (p.wfx > 0 && p.friendly) WeaponFx.blast(this, p.wfx, p.wmode, p.x, p.y, p.explode, p.dmg);
        String[] fx = p.explodeFx.split(":");
        if (fx.length == 2) fx(fx[0], fx[1], p.x, p.y, Math.max(0.5f, p.explode / 38f), p.color, Platform.ADD | Platform.TINT);
        ps.burst(rng, p.x, p.y, p.color, 14, 120, 0.4f, 3, 60, true);
        Snd.sfxv("explosion_small", 0.7f);
        shake(2f, 0.15f);
    }

    private void projDie(Proj p, boolean wall) {
        if (p.dead) return;
        if (p.special == 6 && p.friendly) { p.dead = true; Arsenal.stick(this, p, null); return; }       // sin enemigo: queda pegada al suelo / pared
        p.dead = true;
        if (p.friendly && p.src != BlessFx.SRC_X) { int pv = dmgSrc; dmgSrc = 0; try { BlessFx.onProjEnd(this, p.x, p.y, p.src); } finally { dmgSrc = pv; } }
        if (p.explode > 0) explode(p);
        else {
            ps.burst(rng, p.x, p.y, p.color, 6, 60, 0.25f, 2, 0, true);
            fx("fx_hit", "spark", p.x, p.y, 0.8f, p.color, Platform.ADD | Platform.TINT);
        }
    }

    // ------------------------------------------------------------------ companero y bestiario
    private float cmpX, cmpY, cmpCd = 3f, cmpT, scanT, cmpFlash;
    private boolean cmpInit;

    private void updateCompanion(float dt) {
        scanT -= dt;
        if (scanT <= 0) {                                   // bestiario: enemigos y jefes vistos
            scanT = 0.5f;
            for (Enemy e : enemies) Codex.see(rs, "e:" + e.def.id, Codex.pretty(e.def.id));
            if (boss != null) Codex.see(rs, "b:" + boss.def.idx, boss.def.name);
        }
        int c = rs.companion;
        if (c < 0 || pl == null) return;
        if (!cmpInit) { cmpX = pl.x - 20; cmpY = pl.y - 40; cmpInit = true; }
        cmpT += dt; if (cmpFlash > 0) cmpFlash -= dt;
        float tx = pl.x - pl.dir() * 24, ty = pl.y - 38 + (float) Math.sin(cmpT * 2.2f) * 4;
        float k = Math.min(1f, dt * 5f);
        cmpX += (tx - cmpX) * k; cmpY += (ty - cmpY) * k;
        if (Math.abs(cmpX - pl.x) > 260) { cmpX = tx; cmpY = ty; }   // teletransporte si se queda atras
        if (c == Companions.FIRE && pl.alive && !cinematic) {
            cmpCd -= dt;
            if (cmpCd <= 0) {
                Ent t = nearestEnemy(cmpX, cmpY, 150, true);
                if (t == null) { cmpCd = 0.5f; return; }
                cmpCd = 6f; cmpFlash = 0.25f;
                float tyc = t.y - 10;
                for (int i = 0; i < 8; i++) { float f = i / 7f; ps.spawn(cmpX + (t.x - cmpX) * f, cmpY + (tyc - cmpY) * f, rng.f(-8, 8), rng.f(-8, 8), 0.3f, 2, 0, 0xFFB43A, true); }
                fx("fx_hit", "spark", t.x, tyc, 0.9f, 0xFF8A30, Platform.ADD | Platform.TINT);
                dmgSrc = BlessFx.SRC_COMP;
                try { damageEnemy(t, pl.baseDmg(this) * (t instanceof Boss ? 0.10f : 0.25f), false, 0, 0); } finally { dmgSrc = 0; }
            }
        }
    }

    private void drawCompanion(Platform.Gfx g) {
        int c = rs.companion;
        if (c < 0 || !cmpInit) return;
        UI.light(g, cmpX, cmpY - 4, 22 + (cmpFlash > 0 ? 12 : 0), Companions.COLOR[c] | 0xFF000000, 0.30f);
        Sheet sh = Assets.spr(Companions.SHEET[c]);
        if (sh != null && sh != Sheet.EMPTY) sh.drawAt(g, "idle", cmpT, Math.round(cmpX), Math.round(cmpY + 16), pl.dir() > 0, 1f, 0, 0, 1f);
    }

    /** Umbra (sombra) marca lo oculto de la sala: cofres secretos y puertas de suceso. */
    private void drawSecretMarks(Platform.Gfx g) {
        if (rs.companion != Companions.SHADOW) return;
        for (Prop p : props) {
            boolean sec = p.kind.equals("chest") && p.arg >= 3 && !p.used;
            boolean door = p.kind.equals("door") && p.event > 0 && !p.done;
            if (!sec && !door) continue;
            float a = 0.5f + 0.4f * (float) Math.sin(time * 4);
            UI.light(g, p.x, p.y - 12, 20, 0xAA6EFF, 0.35f * a);
            if (UI.arrow != null) g.imageRot(UI.arrow, 0, 0, 8, 8, p.x - 5, p.y - 46 + (float) Math.sin(time * 5) * 2, 10, 10, 1.5708f, Platform.TINT, 0xAA6EFF, a);
        }
    }

    // ------------------------------------------------------------------ recogibles
    private void updatePickups(float dt) {
        for (Pickup p : pickups) {
            if (p.dead) continue;
            p.t += dt;
            if (p.delay > 0) { p.delay -= dt; continue; }
            float dx = pl.x - p.x, dy = pl.cy() - p.y;
            float d = (float) Math.sqrt(dx * dx + dy * dy);
            boolean mag = p.t > 0.35f && d < rs.stats.magnet && pl.alive;
            if (p.type == Pickup.RELIC) mag = false;
            if (mag) {
                float sp = 260 + (rs.stats.magnet - 56) * 2;
                p.vx = dx / (d + 0.01f) * sp; p.vy = dy / (d + 0.01f) * sp;
                p.x += p.vx * dt; p.y += p.vy * dt;
            } else {
                p.vy += 900 * dt;
                float nx = p.x + p.vx * dt, ny = p.y + p.vy * dt;
                if (solidAtPx(nx, p.y)) { p.vx *= -0.4f; nx = p.x; }
                if (p.vy > 0 && (solidAtPx(nx, ny + 2) || room.tile((int) (nx / 16), (int) ((ny + 2) / 16)) == Room.ONEWAY && p.vy > 0 && room.tile((int) (nx / 16), (int) (p.y / 16)) != Room.ONEWAY)) {
                    ny = (float) Math.floor((ny + 2) / 16) * 16 - 2;
                    p.vy *= -0.35f; p.vx *= 0.6f;
                    if (Math.abs(p.vy) < 25) p.vy = 0;
                }
                p.x = nx; p.y = ny;
            }
            float reach = p.type == Pickup.RELIC ? 22 : 12;
            if (d < reach && pl.alive && p.t > 0.25f) collect(p);
        }
        pickups.removeIf(p -> p.dead);
    }

    private void collect(Pickup p) {
        p.dead = true;
        switch (p.type) {
            case Pickup.GOLD:
                rs.gold += p.value;
                Snd.sfxv("coin", 0.55f);
                BlessFx.onPick(this, 0);
                break;
            case Pickup.SOUL:
                rs.souls += p.value;
                Snd.sfxv("soul", 0.5f);
                BlessFx.onPick(this, 1);
                break;
            case Pickup.HEART:
                if (rs.hp >= rs.stats.maxHp - 0.5f) BlessFx.onOverflow(this, 2); else BlessFx.onPick(this, 2);
                healPlayer(rs.stats.maxHp * 0.15f);
                Snd.sfx("heart", 0.9f);
                fx("fx_heal", "rise", pl.x, pl.y - 10, 0.8f, 0, 0);
                break;
            case Pickup.POTION:
                if (rs.potions >= rs.stats.potionsMax) BlessFx.onOverflow(this, 3); else BlessFx.onPick(this, 3);
                rs.potions = Math.min(rs.stats.potionsMax, rs.potions + 1);
                Snd.sfx("potion", 0.9f);
                break;
            case Pickup.RELIC:
                Snd.sfx("relic_get", 1f);
                flash(0xFFE8A0, 0.4f);
                if (p.relic >= 0 && p.relic < 8 && !rs.sandbox) { rs.relicsThisRun[p.relic] = true; Save.S.relics[p.relic] = true; Save.S.write(); }
                text(pl.x, pl.y - 50, "¡Reliquia obtenida!", 0xFFD25A, true);
                ps.burst(rng, p.x, p.y, 0xFFE8A0, 40, 160, 1f, 3, 0, true);
                if (relicListener != null) relicListener.run();
                break;
            default: break;
        }
        ps.burst(rng, p.x, p.y, p.type == Pickup.GOLD ? 0xFFD25A : (p.type == Pickup.SOUL ? 0x9FD8FF : 0xFF6A7C), 4, 50, 0.3f, 2, 0, true);
    }

    public Runnable relicListener;

    // ------------------------------------------------------------------ muros y suelos rompibles
    private byte[] breakHp;
    void clearBreakHp() { breakHp = null; }
    private float breakCd;
    public int brokenCount;

    /** Golpea las baldosas rompibles dentro de un rectangulo. Devuelve cuantas se rompieron. */
    public int breakRect(float rx, float ry, float rw, float rh, int dmg) {
        int n = 0;
        secrets.hit(rx, ry, rw, rh, dmg);
        if (dmg <= 1) { if (time - breakCd < 0.16f) return 0; breakCd = time; }
        int tx0 = (int) Math.floor(rx / Room.TS), tx1 = (int) Math.floor((rx + rw) / Room.TS);
        int ty0 = (int) Math.floor(ry / Room.TS), ty1 = (int) Math.floor((ry + rh) / Room.TS);
        for (int ty = ty0; ty <= ty1; ty++) for (int tx = tx0; tx <= tx1; tx++) {
            if (tx < 0 || ty < 0 || tx >= room.w || ty >= room.h) continue;
            if (room.t[ty * room.w + tx] != Room.BREAK && room.t[ty * room.w + tx] != Room.DOOR) continue;
            if (breakHp == null) breakHp = new byte[room.w * room.h];
            int i = ty * room.w + tx;
            if (breakHp[i] == 0) breakHp[i] = 3;
            breakHp[i] -= dmg;
            float cx = tx * Room.TS + 8, cy = ty * Room.TS + 8;
            if (breakHp[i] <= 0) {
                room.t[i] = Room.AIR; n++; brokenCount++;
                secrets.onBreak(tx, ty);
                ps.burst(rng, cx, cy, 0xB09A70, 14, 110, 0.6f, 3, 420, false);
                ps.burst(rng, cx, cy, 0x6A5A48, 8, 70, 0.7f, 2, 380, false);
                fx("fx_dust", "land", cx, cy + 6, 1f, 0, 0);
            } else {
                ps.burst(rng, cx, cy, 0xB09A70, 4, 60, 0.3f, 2, 300, false);
                Snd.sfxv("hit_stone", 0.6f);
            }
        }
        if (n > 0) {
            Snd.sfxv("break_pot", 0.9f); Snd.sfxv("explosion_small", 0.5f);
            shake(3f, 0.2f);
            text(rx + rw / 2, ry - 6, "¡Roto!", 0xFFD25A, false);
        }
        return n;
    }

    public int breakCircle(float cx, float cy, float r, int dmg) { return breakRect(cx - r, cy - r, r * 2, r * 2, dmg); }

    private void drawBreakTiles(Platform.Gfx g) {
        if (room.breakImg == null) return;
        int tx0 = Math.max(0, (int) camX / Room.TS), tx1 = Math.min(room.w - 1, (int) (camX + viewW) / Room.TS + 1);
        int ty0 = Math.max(0, (int) camY / Room.TS), ty1 = Math.min(room.h - 1, (int) (camY + ViewSize.h) / Room.TS + 1);
        for (int ty = ty0; ty <= ty1; ty++) for (int tx = tx0; tx <= tx1; tx++) {
            int i = ty * room.w + tx;
            if (room.t[i] != Room.BREAK && room.t[i] != Room.DOOR) continue;
            if (secrets.hides(tx, ty)) continue;
            float off = (breakHp != null && breakHp[i] > 0 && breakHp[i] < 3) ? (float) Math.sin(time * 60f) * 0.6f : 0f;
            g.image(room.t[i] == Room.DOOR ? room.doorImg : room.breakImg, 0, 0, 16, 16, tx * 16 + off, ty * 16, 16, 16, 0, 0, 1f);
            if (breakHp != null && breakHp[i] > 0 && breakHp[i] < 3) g.rect(tx * 16 + 3, ty * 16 + 3, 10, 1, 0xFF000000, false);
        }
    }

    /** Efectos de un parry exitoso. */
    public int parries;   // parries logrados en la sala (estadistica / pruebas)

    public void parryFx(Player p, float srcX, boolean proj) {
        int t = rs.shield;
        parries++; p.parryFlash = 0.3f;
        BlessFx.onParry(this);
        p.parryT = 0; p.invuln = Math.max(p.invuln, 0.5f);
        float fx = p.x + p.dir() * 12;
        text(p.x, p.y - p.bh - 14, "¡PARRY!", 0xFFE070, true);
        fx("fx_hit", "big", fx, p.y - 16, 1f, 0, 0);
        Impact.perfectParry(this, p, fx, p.y - 16);
        hitstop(0.12f); shake(3.5f, 0.2f); flash(0xFFE8A0, 0.12f);
        rs.ult = Math.min(100f, rs.ult + 8f);
        healPlayer(rs.stats.maxHp * 0.015f);
        if (Save.S.vibOn) P.vibrate(25);
        if (!proj) for (Ent e : enemiesIn(p.x + p.dir() * 24, p.y - 14, 56)) {
            if (e instanceof Enemy) e.applyStatus(Ent.STUN, 1.5f, 0);
            damageEnemy(e, p.baseDmg(this) * (1.6f + 0.4f * t), false, p.dir() * 220, -60);
        }
        if (t == 2) explosion(p.x, p.y - 14, 64, p.baseDmg(this) * 2f, 220, Ent.STUN, 0.8f, 0, true);
    }

    public void breakPot(Prop pr) {
        if (pr.open) return;
        pr.open = true; pr.animT = 0; pr.anim = "break";
        Snd.sfxv("break_pot", 0.8f);
        ps.burst(rng, pr.x, pr.y - 8, 0xA08060, 10, 90, 0.5f, 2, 400, false);
        int r = rng.i(100);
        if (r < 55) dropGold(pr.x, pr.y - 8, Math.round((6 + rng.i(8)) * rs.stats.goldMul));
        else if (r < 68) drop(Pickup.HEART, pr.x, pr.y - 8, 1);
    }

    // ------------------------------------------------------------------ camara
    private float anchorY = Float.NaN;

    private void updateCamera(float dt) {
        float w = viewW, h = ViewSize.h;
        float tx, ty;
        if (!Float.isNaN(camTargetX)) { tx = camTargetX - w / 2; ty = camTargetY - h / 2; }
        else {
            float look = pl.right ? 22 : -22;
            tx = pl.x + look - w / 2;
            // la camara solo sigue en vertical al pisar suelo o al salirse de una banda: los saltos ya no la sacuden
            if (Float.isNaN(anchorY) || pl.onGround) anchorY = pl.y;
            else if (pl.y > anchorY + 44) anchorY = pl.y - 44;
            else if (pl.y < anchorY - 70) anchorY = pl.y + 70;
            ty = anchorY - h * 0.62f;
        }
        float maxX = Math.max(0, room.pixW - w), maxY = Math.max(0, room.pixH - h);
        if (room.pixW <= w) tx = (room.pixW - w) / 2; else tx = Mth.clamp(tx, 0, maxX);
        ty = Mth.clamp(ty, 0, maxY);
        float k = 1f - (float) Math.pow(0.0025, dt);
        camX += (tx - camX) * k;
        camY += (ty - camY) * (1f - (float) Math.pow(0.004, dt));
        camZoom += (camTargetZoom - camZoom) * (1f - (float) Math.pow(0.02, dt));
    }

    public void snapCamera() {
        updateCamera(1f);
        camX = Mth.clamp(pl.x - viewW / 2, 0, Math.max(0, room.pixW - viewW));
        anchorY = pl.y;
        camY = Mth.clamp(pl.y - ViewSize.h * 0.62f, 0, Math.max(0, room.pixH - ViewSize.h));
    }

    // ------------------------------------------------------------------ dibujo
    public void render(Platform.Gfx g) {
        float w = viewW, h = ViewSize.h;
        float sx = 0, sy = 0;
        if (shakeT > 0) { sx = rng.f(-shakeMag, shakeMag); sy = rng.f(-shakeMag, shakeMag); }
        drawBackground(g, sx, sy);
        float z = camZoom;
        float tx = -camX * z + (1 - z) * w / 2f * 1f + sx, ty = -camY * z + (1 - z) * h / 2f + sy;
        if (z == 1f) { tx = Math.round(tx); ty = Math.round(ty); }
        g.pushTransform(tx, ty, z);
        // sala
        if (room.baked != null) {
            int vx0 = Math.max(0, (int) camX), vy0 = Math.max(0, (int) camY);
            int vw = (int) Math.min(room.pixW - vx0, w / z + 3), vh = (int) Math.min(room.pixH - vy0, h / z + 3);
            if (vw > 0 && vh > 0) g.image(room.baked, vx0, vy0, vw, vh, vx0, vy0, vw, vh, 0, 0, 1f);
        }
        secrets.renderBase(g);
        drawBreakTiles(g);
        secrets.renderScenery(g);
        drawAnimatedDeco(g);
        if (room.glow != 0) { float gp = 0.12f + 0.04f * (float) Math.sin(time * 1.7f); UI.light(g, room.pixW / 2f, room.exitY - 70, 190, room.glow, gp); UI.light(g, room.pixW / 2f - 150, room.exitY - 40, 90, room.glow, gp * 0.7f); UI.light(g, room.pixW / 2f + 150, room.exitY - 40, 90, room.glow, gp * 0.7f); }
        for (Prop p : props) drawProp(g, p);
        for (FxObj f : fxs) if (f.behind) drawFx(g, f);
        for (Pickup p : pickups) drawPickup(g, p);
        for (Enemy e : enemies) e.render(g, this);
        if (boss != null) boss.render(g, this);
        drawCompanion(g);
        Arsenal.drawSummons(g, this);
        Arsenal.drawStickies(g, this);
        pl.render(g, this);
        drawSecretMarks(g);
        for (Proj p : projs) drawProj(g, p);
        long bt1 = System.nanoTime();
        BlessFx.draw(this, g);
        BlessFx.dbgNsDraw += System.nanoTime() - bt1;
        for (FxObj f : fxs) if (!f.behind) drawFx(g, f);
        for (float[] l : lines) g.line(l[0], l[1], l[2], l[3], 2f, Mth.withAlpha((int) l[5], 255), true);
        ps.render(g, 0, 0);
        drawLights(g);
        for (DmgText d : texts) drawText(g, d);
        if (tutorial != null && UI.small != null) UI.small.center(g, tutorial, room.spawnX + 40, room.spawnY - 70, 0xFFFFFF, 0.9f);
        g.popTransform();
        // oscuridad ambiental y vineta
        if (darkness > 0) g.rect(0, 0, w, h, Mth.withAlpha(0x000008, (int) (darkness * 255)), false);
        if (UI.vignette != null && VideoCfg.vignette) g.image(UI.vignette, 0, 0, UI.vignette.w, UI.vignette.h, 0, 0, w, h, 0, 0, 0.55f);
        if (flashT > 0) g.rect(0, 0, w, h, Mth.withAlpha(flashColor, (int) (255 * 0.55f * Math.max(0, flashT / flashMax))), false);
    }

    private void drawBackground(Platform.Gfx g, float sx, float sy) {
        float w = viewW, h = ViewSize.h;
        float maxY = Math.max(1, room.pixH - h);
        float fy = Mth.clamp(camY / maxY, 0, 1);
        float[] fac = {0.12f, 0.30f, 0.62f};
        boolean any = false;
        for (int i = 0; i < 3; i++) {
            Platform.Img im = bg[i];
            if (im == null) continue;
            any = true;
            float ox = -((camX * fac[i]) % im.w);
            if (ox > 0) ox -= im.w;
            float oy = -(im.h - h) * (0.2f + 0.8f * fy) + sy * 0.3f;
            for (float x = ox + sx * 0.3f; x < w; x += im.w) g.image(im, 0, 0, im.w, im.h, Math.round(x), Math.round(oy), im.w, im.h, 0, 0, 1f);
        }
        if (!any) g.clear(0xFF101018);
    }

    private void drawAnimatedDeco(Platform.Gfx g) {
        Platform.Img ts = Assets.img("tiles/tiles_" + biome.key + ".png");
        if (ts == null) return;
        int frame = (int) (time * 8);
        float camR = camX + viewW + 16;
        for (int[] d : animDeco) {
            if (d[0] < camX - 16 || d[0] > camR) continue;
            int col = (d[2] == 5 ? 0 : 4) + ((d[3] + frame) & 3);
            g.image(ts, col * 16, 4 * 16, 16, 16, d[0], d[1], 16, 16, 0, 0, 1f);
        }
    }

    private void drawLights(Platform.Gfx g) {
        float fl = 0.85f + 0.15f * (float) Math.sin(time * 11);
        for (int[] d : animDeco) {
            if (d[0] < camX - 40 || d[0] > camX + viewW + 40) continue;
            UI.light(g, d[0] + 8, d[1] + 8, d[2] == 5 ? 46 : 36, biome.color == 0xF2E6B8 ? 0xFFE0A0 : (d[2] == 5 ? 0xFFB060 : biome.color), 0.28f * fl);
        }
        UI.light(g, pl.x, pl.cy(), 40, rs.cls.color1, 0.10f);
        for (Proj p : projs) UI.light(g, p.x, p.y, 28 * p.scale, p.color, 0.35f);
        for (FxObj f : fxs) if ((f.flags & Platform.ADD) != 0 && f.life < 0 && f.t < 0.2f) UI.light(g, f.x, f.y, 26 * f.scale, f.tint == 0 ? 0xFFFFFF : f.tint, 0.25f);
    }

    private void drawFx(Platform.Gfx g, FxObj f) {
        if (f.delay > 0) return;
        f.sheet.drawCentered(g, f.anim, f.anim.frameAt(f.t), Math.round(f.x), Math.round(f.y), f.rot, f.scale, f.right ? f.flags : (f.flags | Platform.FLIP_X), f.tint, f.alpha);
    }

    private void drawProj(Platform.Gfx g, Proj p) {
        Sheet s = Assets.fx("fx_proj");
        Anim a = s.anim(p.sprite);
        float rot = p.spin ? p.t * p.spinRate : (float) Math.atan2(p.vy, p.vx);
        float sp = (float) Math.hypot(p.vx, p.vy);
        if (!Save.S.reduceFx && p.special != 1 && p.t > 0.03f && (p.spin || sp > 220f)) {
            // estela / smear coherente con la velocidad y el elemento (color del proyectil): ecos tenues detras (o giro residual si rota). Solo visual.
            int n = sp > 420f ? 3 : 2;
            float gap = Mth.clamp(sp / 70f, 2.5f, 7f);
            float ux = sp > 1f ? p.vx / sp : 0f, uy = sp > 1f ? p.vy / sp : 0f;
            for (int i = n; i >= 1; i--) {
                float al = (p.spin ? 0.30f : 0.26f) * (1f - (i - 1) / (float) n);
                if (p.spin) s.drawCentered(g, a, a.frameAt(p.t), Math.round(p.x), Math.round(p.y), rot - p.spinRate * 0.012f * i * Math.signum(p.spinRate), p.scale, Platform.ADD | Platform.TINT, p.color, al);
                else s.drawCentered(g, a, a.frameAt(p.t), Math.round(p.x - ux * gap * i), Math.round(p.y - uy * gap * i), rot, p.scale * (1f - 0.08f * i), Platform.ADD | Platform.TINT, p.color, al);
            }
        }
        s.drawCentered(g, a, a.frameAt(p.t), Math.round(p.x), Math.round(p.y), rot, p.scale, 0, 0, 1f);
    }

    private void drawPickup(Platform.Gfx g, Pickup p) {
        String n = p.type == Pickup.GOLD ? "pick_gold" : p.type == Pickup.SOUL ? "pick_soul" : p.type == Pickup.HEART ? "pick_heart" : p.type == Pickup.POTION ? "pick_potion" : "pick_relic";
        Sheet s = Assets.spr(n);
        Anim a = s.anim("idle");
        float bob = p.type == Pickup.RELIC ? (float) Math.sin(p.t * 3) * 3 : 0;
        s.drawCentered(g, a, a.frameAt(p.t), Math.round(p.x), Math.round(p.y + bob), 0, 1f, 0, 0, 1f);
        if (p.type == Pickup.SOUL) UI.light(g, p.x, p.y, 14, 0x9FD8FF, 0.35f);
        else if (p.type == Pickup.RELIC) UI.light(g, p.x, p.y, 34, 0xFFD25A, 0.5f);
    }

    /** Color de ambiente de los objetos de suceso (0 = ninguno). */
    private int eventColor(Prop p) {
        switch (p.kind) {
            case "spirit": return Events.GLOW[Events.SPIRIT];
            case "shrine": return Events.GLOW[p.arg == 1 ? Events.ALTAR : Events.SANCTUARY];
            case "cursed": return Events.GLOW[Events.CURSED];
            case "cage": return Events.GLOW[Events.CAPTIVE];
            case "relic": return Events.GLOW[Events.SECRET];
            case "merchant": return p.arg == 1 ? Events.GLOW[Events.MERCHANT] : 0;
            default: return 0;
        }
    }

    private void drawProp(Platform.Gfx g, Prop p) {
        if (p.hidden) return;
        if (p.kind.equals("weapon")) { Arsenal.drawGround(g, this, p); return; }
        if (p.kind.equals("chest") && p.roundChest && !p.used) { UI.light(g, p.x, p.y - 10, 26 + 3 * (float) Math.sin(time * 5), 0xFFD25A, 0.35f); if (rng.chance(0.05f)) ps.spawn(p.x + rng.f(-8, 8), p.y - 4, rng.f(-6, 6), -rng.f(15, 35), 0.8f, 2, 0, 0xFFE9A0, true); }
        if (p.kind.equals("chest") && p.arg >= 3 && !p.used) { UI.light(g, p.x, p.y - 8, 30 + 4 * (float) Math.sin(time * 4), 0xB070FF, 0.40f); if (rng.chance(0.06f)) ps.spawn(p.x + rng.f(-8, 8), p.y - 4, rng.f(-6, 6), -rng.f(15, 35), 0.8f, 2, 0, 0xD8B0FF, true); }
        if (p.sheet == null) return;
        Anim a = p.sheet.anim(p.anim);
        int frame = a.frameAt(p.animT);
        float ox = p.shakeT > 0 ? rng.f(-1, 1) : 0;
        int ec = eventColor(p);
        if (ec != 0 && !p.done) UI.light(g, p.x, p.y - 26, 46 + 5 * (float) Math.sin(time * 3), ec, 0.30f);
        if (p.back != null) { Anim ba = p.back.anim("idle"); p.back.draw(g, ba, ba.frameAt(time), Math.round(p.x), Math.round(p.y), true, 1f, 0, 0, 1f); }
        boolean tinted = p.tint != 0;
        p.sheet.draw(g, a, frame, Math.round(p.x + ox), Math.round(p.y) + (p.kind.equals("spirit") ? Math.round((float) Math.sin(time * 2f) * 2) - 8 : 0), true, 1f, tinted ? Platform.TINT : 0, tinted ? p.tint : 0, 1f);
        if (ec != 0 && !p.done && rng.chance(0.08f)) ps.spawn(p.x + rng.f(-14, 14), p.y - rng.f(8, 40), rng.f(-4, 4), -rng.f(8, 20), 0.9f, 2, 0, ec, true);
        if (p.kind.equals("door") && p.doorIdx >= 0 && p.nextType >= 0 && UI.small != null) {
            // icono de recompensa sobre la puerta
            float bob = (float) Math.sin(time * 3 + p.doorIdx) * 2;
            UI.panel(g, 0, p.x - 12, p.y - 76 + bob, 24, 24, 0.9f);
            UI.iconC(g, p.icon != null ? p.icon : RunState.roomIcon(p.nextType), p.x, p.y - 64 + bob, 1f, p.locked ? 0.4f : 1f);
            if (p.event > 0) UI.light(g, p.x, p.y - 30, 34, Events.GLOW[p.event], 0.28f);
        }
        if (p.label != null && UI.small != null && (!p.kind.equals("door") || Math.abs(pl.x - p.x) < 40 && Math.abs(pl.y - p.y) < 40))
            UI.small.center(g, p.label, p.x, p.kind.equals("door") ? p.y - 92 : p.y - 62, p.locked ? 0x9AA0B0 : 0xFFD25A, 1f);
    }

    private void drawText(Platform.Gfx g, DmgText d) {
        Font f = UI.small;
        if (f == null) return;
        float a = Mth.clamp(d.life / 0.25f, 0, 1);
        float w = f.width(d.text);
        int x = Math.round(d.x - w / 2f), y = Math.round(d.y);
        // contorno oscuro (legibilidad sobre cualquier fondo) y, en criticos, doble trazo dorado: no depende solo del color
        int ol = 0x180818;
        f.draw(g, d.text, x - 1, y, ol, a * 0.85f); f.draw(g, d.text, x + 1, y, ol, a * 0.85f);
        f.draw(g, d.text, x, y - 1, ol, a * 0.85f); f.draw(g, d.text, x, y + 1, ol, a * 0.85f);
        f.draw(g, d.text, x, y, d.color, a);
        if (d.big) f.draw(g, d.text, x + 1, y, d.color, a * 0.7f);
    }

    // ------------------------------------------------------------------ interaccion
    public Prop nearestInteractable() {
        Prop best = null; float bd = 34;
        for (Prop p : props) {
            if (p.dead || p.hidden) continue;
            boolean can = false;
            switch (p.kind) {
                case "altar": case "forge": case "merchant": case "fountain": case "chest": case "portal": case "sanctuary": case "npc": can = !p.used || p.kind.equals("merchant"); break;
                case "weapon": can = !p.used && p.pickLock <= 0; break;
                case "spirit": case "shrine": case "cage": case "relic": case "cursed": can = !p.done && !p.used; break;
                case "door": can = !p.locked; break;
                default: break;
            }
            if (!can) continue;
            float d = Math.abs(p.x - pl.x) + Math.abs(p.y - pl.y) * 0.4f;
            if (d < bd) { bd = d; best = p; }
        }
        return best;
    }
}
