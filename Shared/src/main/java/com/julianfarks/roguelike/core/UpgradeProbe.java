package com.julianfarks.roguelike.core;

import java.util.HashSet;
import java.util.Set;

/**
 * Pruebas automaticas de las mejoras acumulables, la generacion de recompensas segun la build y las sinergias
 * (solo banco headless; BOT_UPGRADES=1 desde DebugBot). NO son pruebas en un dispositivo Android ni en Windows real.
 * Usa el motor real (Level, RunScreen, ChestLoot, Stats) y termina el proceso con 0 si todo pasa.
 */
final class UpgradeProbe {
    private UpgradeProbe() {}
    static boolean done;
    static int fails, oks;
    static void ck(String n, boolean ok) { System.out.println("UP " + (ok ? "OK    " : "FALLA ") + n); if (ok) oks++; else fails++; }

    static Level lv; static Player p; static RunState rs; static RunScreen scr; static Input in; static Game game;

    static void fr(int n) { for (int i = 0; i < n; i++) { lv.update(1f / 60f); in.endFrame(); } }

    static boolean step(Game g, RunScreen r, Level l, Player pl, int frame) {
        if (done) return true;
        game = g; scr = r; lv = l; p = pl; rs = r.rs; in = l.in;
        done = true;
        for (int c : new int[]{'A', 'D', 'W', 'S', 37, 38, 39, 40, 'J', 'K', 'R', 'T', 'E', 'C', 'L', 'I', 'U', 32}) g.key(c, false);
        System.out.println("UP inicio mejoras");
        try { fr(120); run(); } catch (RuntimeException e) { e.printStackTrace(System.out); ck("sin excepciones durante las pruebas: " + e, false); }
        System.out.println("UP FIN ok=" + oks + " fallos=" + fails);
        return true;
    }

    static void clean() {
        java.util.Arrays.fill(rs.cb, 0); java.util.Arrays.fill(rs.cbLvl, 0); java.util.Arrays.fill(rs.spLvl, 0); rs.special = 0;
        java.util.Arrays.fill(rs.bless, 0); rs.bx = new BlessRt(); BlessFx.sync(rs);
        rs.recalc(); rs.hp = rs.stats.maxHp;
        lv.enemies.clear(); lv.projs.clear(); p.invuln = 99f; lv.toKill = 999; lv.cleared = false;
    }

    static void run() {
        upgradesStack();
        statLevels();
        generation();
        chestNoDup();
        inventoryUi();
        synergies();
    }

    static Enemy dummy(float dx) {
        Enemy e = new Enemy(EnemyDef.get("esqueleto"), false, 1f, 1f);
        e.hp = e.maxHp = 1e6f; e.x = p.x + dx; e.y = p.y; e.home = e.x; e.state = Enemy.PATROL;
        lv.enemies.add(e);
        return e;
    }

    // ---------------------------------------------------------------- etapa 6: sinergias entre mejoras (efectos reales)
    static void synergies() {
        clean();
        ChestLoot.apply(rs, ChestLoot.stat(rs, ChestLoot.BURN, 0, 8));
        ck("solo Fuego: Combustión tóxica inactiva", !Synergy.active(rs, Synergy.TOXIC));
        // sin sinergia: un enemigo quemado muere sin estallar
        Enemy a0 = dummy(200), b0 = dummy(212);
        a0.applyStatus(Ent.BURN, 3f, 4f);
        int t0 = Synergy.toxicN; float hb0 = b0.hp;
        a0.hp = 0; a0.die(lv);
        ck("sin la sinergia, morir quemado no provoca explosión", Synergy.toxicN == t0 && b0.hp == hb0);
        lv.enemies.clear();
        ChestLoot.apply(rs, ChestLoot.stat(rs, ChestLoot.POISON, 0, 8));
        ck("Fuego + Veneno: Combustión tóxica activa", Synergy.active(rs, Synergy.TOXIC));
        Enemy a = dummy(200), b = dummy(214), far = dummy(400);
        a.applyStatus(Ent.BURN, 3f, 4f);
        float hb = b.hp, hf = far.hp;
        a.hp = 0; a.die(lv);
        ck("Combustión tóxica: el enemigo quemado estalla, daña y envenena al de al lado (" + Math.round(hb - b.hp) + " de daño)", Synergy.toxicN == t0 + 1 && b.hp < hb && b.hasStatus(Ent.POISON));
        ck("la explosión no alcanza a los enemigos lejanos", far.hp == hf);
        Enemy c = dummy(240);
        int t1 = Synergy.toxicN; c.hp = 0; c.die(lv);
        ck("un enemigo sin quemar ni envenenar no estalla", Synergy.toxicN == t1);
        lv.enemies.clear();
        // Escarcha afilada: +50% de multiplicador critico contra congelados/ralentizados
        Enemy fz = dummy(200), nm = dummy(260);
        fz.applyStatus(Ent.SLOW, 3f, 0f);
        float off = lv.critMulOf(fz) - lv.critMulOf(nm);
        ChestLoot.apply(rs, ChestLoot.stat(rs, ChestLoot.FREEZE, 0, 8)); ChestLoot.apply(rs, ChestLoot.stat(rs, ChestLoot.CRIT, 0, 4));
        float on = lv.critMulOf(fz) - lv.critMulOf(nm);
        ck("Hielo + Críticos: los críticos contra ralentizados hacen +50% (" + off + " -> " + on + ")", Synergy.active(rs, Synergy.FROSTCRIT) && Math.abs(off) < 0.001f && Math.abs(on - Synergy.FROST_CRIT_BONUS) < 0.001f);
        lv.enemies.clear();
        // estadisticas
        float ls0 = rs.stats.lifesteal, as0 = rs.stats.atkSpd;
        ChestLoot.apply(rs, ChestLoot.stat(rs, ChestLoot.LS, 0, 1));
        float ls1 = rs.stats.lifesteal, as1 = rs.stats.atkSpd;
        ChestLoot.apply(rs, ChestLoot.stat(rs, ChestLoot.ASPD, 0, 4));
        ck("Robo de vida + Vel. de ataque: +4% de robo de vida extra (" + ls1 + " -> " + rs.stats.lifesteal + ")", Synergy.active(rs, Synergy.BLOODRUSH) && Math.abs(rs.stats.lifesteal - ls1 - 0.04f) < 0.001f && rs.stats.atkSpd > as1 * 1.04f * 1.07f);
        float d0 = rs.stats.dmgMul;
        ChestLoot.apply(rs, ChestLoot.stat(rs, ChestLoot.SHOCK, 0, 8));
        float d1 = rs.stats.dmgMul;
        ChestLoot.apply(rs, ChestLoot.stat(rs, ChestLoot.DMG, 0, 6));
        ck("Descarga + Daño: +10% de daño extra (x" + d1 + " -> x" + rs.stats.dmgMul + ")", Synergy.active(rs, Synergy.STORM) && Math.abs(rs.stats.dmgMul - d1 * 1.06f * 1.10f) < 0.01f);
        // inventario y aviso
        scr.openInventory(false); scr.inv.setCat(Inventory.C_UPGR);
        int ns = 0; for (Inventory.Item it : scr.inv.items) if (it.kind == 11) ns++;
        ck("pestaña Mejoras: muestra las 4 sinergias activas (" + ns + ")", ns == 4);
        scr.invClose();
        clean();
        int m0 = Synergy.mask(rs);
        Items.addSpecial(rs, 1); Items.addSpecial(rs, 3);
        String nm2 = Synergy.announce(lv, m0);
        ck("al activarse una sinergia se avisa (" + nm2 + ")", "Combustión tóxica".equals(nm2));
        ck("las mejoras del arma principal también cuentan para las sinergias", Synergy.active(rs, Synergy.TOXIC));
        clean();
    }

    // ---------------------------------------------------------------- etapa 3/4: las mejoras se acumulan y nunca sustituyen al arma
    static void upgradesStack() {
        clean();
        int sec0 = rs.sec, cls0 = rs.weaponLvl;
        float dmg0 = rs.stats.dmgMul, burn0 = rs.stats.burn, poison0 = rs.stats.poison;
        ChestLoot.Reward a = ChestLoot.special(rs, 1);
        ck("carta de mejora del arma: no dice «Sustituye a» (" + a.replaces + ")", a.replaces.isEmpty() && a.amount.contains("Nivel 1"));
        ChestLoot.apply(rs, a);
        ChestLoot.Reward b = ChestLoot.special(rs, 3);
        ck("con una mejora ya tomada, la siguiente tampoco sustituye nada", b.replaces.isEmpty());
        ChestLoot.apply(rs, b);
        ChestLoot.apply(rs, ChestLoot.special(rs, 6));
        ck("tres mejoras del arma a la vez: Filo Ígneo, Daga Venenosa y Hoja del Eclipse activas", rs.spLvl[1] == 1 && rs.spLvl[3] == 1 && rs.spLvl[6] == 1);
        ck("las mejoras no tocan el arma principal ni la secundaria", rs.sec == sec0 && rs.weaponLvl == cls0);
        ck("efectos reales sumados: más daño, quemar y envenenar (" + dmg0 + "->" + rs.stats.dmgMul + ")", rs.stats.dmgMul > dmg0 * 1.3f && rs.stats.burn > burn0 + 0.3f && rs.stats.poison > poison0 + 0.3f);
        float d1 = rs.stats.dmgMul, bn1 = rs.stats.burn;
        ChestLoot.Reward up = ChestLoot.special(rs, 1);
        ck("repetida: la carta muestra «Nivel 1 > 2» (" + up.amount + ")", up.amount.equals("Nivel 1 > 2"));
        ChestLoot.apply(rs, up);
        ck("repetida: sube a nivel 2 y el efecto crece (quemar " + bn1 + "->" + rs.stats.burn + ")", rs.spLvl[1] == 2 && rs.stats.burn > bn1 && rs.stats.dmgMul > d1);
        ChestLoot.apply(rs, ChestLoot.special(rs, 1));
        ck("nivel máximo 3", rs.spLvl[1] == Items.SP_MAXLVL);
        Items.addSpecial(rs, 1);
        ck("no pasa del máximo aunque se intente otra vez", rs.spLvl[1] == Items.SP_MAXLVL);
        boolean offered = false;
        for (int i = 0; i < 300; i++) for (ChestLoot.Reward x : ChestLoot.roll(rs, ChestLoot.MODE_WEAPONS, 2)) if (x.kind == ChestLoot.K_SPECIAL && x.id == 1) offered = true;
        ck("al máximo deja de ofrecerse (sale otra opción en su lugar)", !offered);
        // penalizaciones una sola vez: Mandoble Pesado nivel 3 sigue siendo -18% de vel. de ataque, no -45%
        clean(); float as0 = rs.stats.atkSpd;
        for (int k = 0; k < 3; k++) Items.addSpecial(rs, 7);
        ck("Mandoble Pesado Nv3: la penalización de velocidad se aplica una sola vez (" + as0 + "->" + rs.stats.atkSpd + ")", Math.abs(rs.stats.atkSpd - as0 * 0.82f) < 0.01f);
    }

    // ---------------------------------------------------------------- etapa 4: niveles de estadisticas, tope, efecto total
    static void statLevels() {
        clean();
        float d0 = rs.stats.dmgMul;
        int tot = 0;
        for (int k = 0; k < 4; k++) {
            ChestLoot.Reward x = ChestLoot.stat(rs, ChestLoot.DMG, 0, 6);
            if (k == 0) ck("Filo afilado nuevo: «Mejora nueva · Nivel 1» (" + x.note + ")", x.note.contains("Nivel 1"));
            if (k == 2) ck("Filo afilado: «Nivel 2 > 3 · total +18% daño» (" + x.note + ")", x.note.contains("Nivel 2 > 3") && x.note.contains("+18% daño"));
            ChestLoot.apply(rs, x); tot += 6;
        }
        ck("Filo afilado elegido 4 veces = nivel 4, +24% acumulado", rs.cbLvl[ChestLoot.DMG] == 4 && rs.cb[ChestLoot.DMG] == tot);
        ck("se aplica a la estadística real (daño x" + d0 + " -> x" + rs.stats.dmgMul + ")", Math.abs(rs.stats.dmgMul - d0 * 1.24f) < 0.02f);
        rs.cbLvl[ChestLoot.DMG] = ChestLoot.maxLvl(ChestLoot.DMG);
        boolean offered = false;
        for (int i = 0; i < 400; i++) for (ChestLoot.Reward x : ChestLoot.roll(rs, ChestLoot.MODE_STATS, 2)) if (x.kind == ChestLoot.K_STAT && x.id == ChestLoot.DMG) offered = true;
        ck("estadística al nivel máximo: no se vuelve a ofrecer", !offered);
        // mas de 20 mejoras distintas a la vez
        clean();
        for (int i = 0; i < ChestLoot.N; i++) if (i != ChestLoot.REV) ChestLoot.apply(rs, ChestLoot.stat(rs, i, 1, Math.max(1, ChestLoot.S_CAP[i] / 10)));
        for (int sp = 1; sp < Items.SP_COUNT; sp++) Items.addSpecial(rs, sp);
        int n = Inventory.upgradeCount(rs);
        ck("más de 20 mejoras distintas activas a la vez en una run (" + n + ")", n >= 20);
        Stats s = rs.stats;
        ck("todas se aplican sin romper las estadísticas (valores finitos y positivos)", Float.isFinite(s.dmgMul) && s.dmgMul > 0 && s.atkSpd > 0 && s.maxHp > 0 && s.dmgTaken > 0 && s.cdMul > 0);
    }

    // ---------------------------------------------------------------- etapa 5: generacion segun la build
    static void generation() {
        clean();
        for (int k = 0; k < 2; k++) ChestLoot.apply(rs, ChestLoot.stat(rs, ChestLoot.CRIT, 0, 4));
        int ownedSeen = 0, total = 0, lvlLabel = 0;
        for (int i = 0; i < 1500; i++) for (ChestLoot.Reward x : ChestLoot.roll(rs, ChestLoot.MODE_STATS, 0)) {
            if (x.kind != ChestLoot.K_STAT) continue;
            total++;
            if (x.id == ChestLoot.CRIT) { ownedSeen++; if (x.note.contains("Nivel 2 > 3")) lvlLabel++; }
        }
        float share = ownedSeen / (float) Math.max(1, total), base = 8f / 120f;       // peso base de Ojo certero entre todas
        ck("una mejora que ya tienes reaparece para subir de nivel (" + ownedSeen + " de " + total + ", " + Math.round(share * 100) + "%)", ownedSeen > 0 && lvlLabel == ownedSeen);
        ck("y sale más a menudo que si no la tuvieras (" + Math.round(share * 1000) / 10f + "% > " + Math.round(base * 1000) / 10f + "%)", share > base * 1.3f);
        // rareza ponderada: con mucha suerte salen mas raras
        clean();
        int hi0 = 0, hi1 = 0;
        for (int i = 0; i < 600; i++) for (ChestLoot.Reward x : ChestLoot.roll(rs, ChestLoot.MODE_STATS, 0)) if (x.rar >= 2) hi0++;
        rs.cb[ChestLoot.LUCK] = 20;
        for (int i = 0; i < 600; i++) for (ChestLoot.Reward x : ChestLoot.roll(rs, ChestLoot.MODE_STATS, 0)) if (x.rar >= 2) hi1++;
        ck("rareza ponderada por la suerte (raras+: " + hi0 + " -> " + hi1 + ")", hi1 > hi0 * 1.3f);
        rs.cb[ChestLoot.LUCK] = 0;
        // armas que tienes: se ofrecen como mejora de nivel (de cualquiera de tu bolsa), nunca como arma nueva duplicada
        clean();
        rs.bag.clear(); rs.sec = 0; Arsenal.grant(rs, Items.SEC_BOW, 0, -1, 0); Arsenal.grant(rs, Items.SEC_AXE, 0, -1, 0);
        int upStored = 0; boolean dup = false;
        for (int i = 0; i < 600; i++) for (ChestLoot.Reward x : ChestLoot.roll(rs, ChestLoot.MODE_WEAPONS, 0)) {
            if (x.kind == ChestLoot.K_SEC_UP && x.id == Items.SEC_AXE) upStored++;
            if (x.kind == ChestLoot.K_SEC_NEW && rs.owns(x.id)) dup = true;
        }
        ck("armas guardadas también pueden subir de nivel desde un cofre (" + upStored + ")", upStored > 0 && !dup);
        ChestLoot.apply(rs, ChestLoot.secUp(rs, Items.SEC_AXE));
        ck("mejorar una guardada sube SU nivel (no el de la equipada)", rs.bLvl[Items.SEC_AXE] == 1 && rs.secLvl == 0);
        // tres opciones siempre distintas
        boolean distinct = true;
        for (int i = 0; i < 400; i++) { ChestLoot.Reward[] o = ChestLoot.roll(rs, i % 3, 1); Set<String> k = new HashSet<>(); for (ChestLoot.Reward x : o) k.add(x.key()); if (k.size() != 3) distinct = false; }
        ck("cada cofre ofrece 3 opciones distintas (1200 cofres)", distinct);
    }

    // ---------------------------------------------------------------- abrir, omitir y reabrir no duplica niveles
    static void chestNoDup() {
        clean();
        float[] sp = ChestSpot.find(lv, p.x + 30, p.y);
        Prop c = lv.addProp(new Room.PropSpec("chest", sp[0], sp[1], 1));
        c.pending = new ChestLoot.Reward[]{ChestLoot.stat(rs, ChestLoot.DMG, 1, 10), ChestLoot.special(rs, 2), ChestLoot.stat(rs, ChestLoot.HP, 1, 18)};
        c.pendMode = ChestLoot.MODE_STATS; c.used = false;
        for (int k = 0; k < 4; k++) {
            scr.dbgOpenChest(c);
            if (scr.debugOv() != RunScreen.OV_CHEST) { ck("reabrir el cofre omitido (" + k + ")", false); return; }
            scr.dbgChest(RunScreen.SKIP_SEL); scr.dbgConfirm();
        }
        ck("abrir y omitir 4 veces: ningún nivel ni valor cambia", rs.cbLvl[ChestLoot.DMG] == 0 && rs.cb[ChestLoot.DMG] == 0 && rs.spLvl[2] == 0 && !c.used);
        scr.dbgOpenChest(c); scr.dbgChest(0); scr.dbgConfirm();
        ck("elegir: sube exactamente 1 nivel (" + rs.cbLvl[ChestLoot.DMG] + ") y el cofre se consume", rs.cbLvl[ChestLoot.DMG] == 1 && rs.cb[ChestLoot.DMG] == 10 && c.used && rs.spLvl[2] == 0);
        scr.dbgOpenChest(c);
        ck("un cofre consumido no se puede volver a abrir", scr.debugOv() != RunScreen.OV_CHEST && rs.cbLvl[ChestLoot.DMG] == 1);
        if (scr.debugOv() != RunScreen.OV_NONE) scr.closeOv();
        // guardado de los niveles
        Items.addSpecial(rs, 5); Items.addSpecial(rs, 5);
        boolean w = RunSave.write(game.P, scr, 1);
        RunScreen back = RunSave.load(game, 1);
        ck("guardado: conserva niveles de mejoras y de mejoras del arma", w && back != null && back.rs.cbLvl[ChestLoot.DMG] == 1 && back.rs.cb[ChestLoot.DMG] == 10 && back.rs.spLvl[5] == 2 && back.rs.special == 5);
        game.P.store().put(RunSave.key(1), "");
    }

    // ---------------------------------------------------------------- inventario: pestaña Mejoras con nivel y efecto total
    static void inventoryUi() {
        clean();
        for (int k = 0; k < 3; k++) ChestLoot.apply(rs, ChestLoot.stat(rs, ChestLoot.DMG, 0, 6));
        Items.addSpecial(rs, 2); Items.addSpecial(rs, 2); Items.addSpecial(rs, 4);
        scr.openInventory(false);
        Inventory iv = scr.inv;
        iv.setCat(Inventory.C_UPGR);
        Inventory.Item filo = null, gel = null;
        for (Inventory.Item it : iv.items) { if (it.kind == 10 && it.wid == ChestLoot.DMG) filo = it; if (it.kind == 4 && it.wid == 2) gel = it; }
        ck("pestaña Mejoras: Filo afilado Nv 3 y Colmillo Gélido Nv 2 (" + iv.items.size() + " mejoras)", filo != null && filo.lvl == 3 && gel != null && gel.lvl == 2 && iv.items.size() == 3);
        boolean noObj = true; iv.setCat(Inventory.C_OBJECTS); for (Inventory.Item it : iv.items) if (it.kind == 4) noObj = false;
        ck("las mejoras ya no se mezclan con los objetos", noObj);
        // la pestaña cabe en todos los tamaños (5 pestañas)
        boolean lay = true;
        for (int w : new int[]{480, 576, 640}) for (int h : new int[]{270, 320}) {
            int ow = game.viewW, oh = ViewSize.h; game.viewW = w; ViewSize.h = h;
            iv.setCat(Inventory.C_UPGR); scr.layoutOverlay();
            float right = 0; for (Screen.Hit hb : scr.hits) if (hb.tag >= 100 && hb.tag < 100 + Inventory.C_COUNT) right = Math.max(right, hb.x + hb.w);
            if (right > w - 90) lay = false;
            game.viewW = ow; ViewSize.h = oh;
        }
        ck("5 pestañas caben sin pisar el título en 480/576/640 x 270/320", lay);
        scr.layoutOverlay();
        scr.invClose();
    }
}
