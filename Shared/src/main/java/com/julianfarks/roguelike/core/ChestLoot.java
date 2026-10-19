package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Recompensas de cofre: al abrir uno se ofrecen exactamente 3 opciones distintas y se elige una.
 * Tres juegos de opciones: MEJORAS (estadisticas), ARMAS (principal/secundaria/escudo) y ARSENAL (granadas, municion, consumibles).
 * Todo se apoya en sistemas que ya existen: Stats, Items (secundarias, granadas, especiales, escudos), pociones, oro.
 */
final class ChestLoot {
    private ChestLoot() {}

    static final int MODE_STATS = 0, MODE_WEAPONS = 1, MODE_ARSENAL = 2;
    static final String[] MODE_TITLE = {"MEJORAS", "ARMAMENTO", "ARSENAL"};
    static final String[] MODE_SUB = {"Elige una mejora para toda la partida", "Elige un arma: las otras dos se pierden", "Elige un objeto: las otras dos se pierden"};

    // ---- rarezas
    static final String[] R_NAME = {"Común", "Poco común", "Rara", "Épica"};
    static final int[] R_COL = {0xFFB8B8C0, 0xFF5AD070, 0xFF4AA0FF, 0xFFC070FF};

    // ---- estadisticas permanentes de la run (rs.cb[]); unidad: % salvo indicacion
    static final int DMG = 0, HP = 1, SPD = 2, ASPD = 3, LUCK = 4, DEF = 5, CRIT = 6, CRITD = 7, CD = 8, ULT = 9, LS = 10, GOLD = 11, SOUL = 12,
            MAG = 13, BURN = 14, FREEZE = 15, SHOCK = 16, POISON = 17, SKILL = 18, POT = 19, REV = 20, N = 21;
    private static final String[] S_NAME = {"Filo afilado", "Corazón vigoroso", "Pies ligeros", "Golpes veloces", "Trébol de suerte", "Piel de hierro", "Ojo certero", "Golpe brutal", "Maestría arcana", "Sed de gloria",
            "Sed de sangre", "Bolsa de oro", "Cosecha de almas", "Imán de botín", "Brasas vivas", "Escarcha viva", "Chispa viva", "Veneno vivo", "Poder arcano", "Frasco extra", "Segunda oportunidad"};
    private static final String[] S_ICON = {"b_filo", "b_corazon", "b_alas", "b_furia", "b_fortuna", "b_piedra", "b_critico", "b_ejecutor", "b_enfriamiento", "b_sabio",
            "b_sangre", "b_fortuna", "b_alma", "b_iman", "b_brasas", "b_glacial", "b_chispa", "b_espinas", "b_habilidad", "potion", "b_segunda"};
    private static final String[] S_UNIT = {"% daño", " vida máx.", "% velocidad", "% vel. de ataque", " suerte", "% menos daño recibido", "% prob. crítico", "% daño crítico", "% menos recarga", "% carga de definitiva",
            "% robo de vida", "% oro", "% almas", " alcance del imán", "% prob. quemar", "% prob. congelar", "% prob. de descarga", "% prob. envenenar", "% daño de habilidades", " frasco máx.", "% de vida al revivir"};
    private static final String[] S_DESC = {"Tus armas y ataques hacen más daño.", "Aumenta tu vida máxima y te cura esa cantidad.", "Te mueves más rápido.", "Atacas más rápido.",
            "Mejora la rareza de las próximas recompensas.", "Recibes menos daño de todo.", "Más probabilidad de golpe crítico.", "Los críticos hacen mucho más daño.", "Tus habilidades se recargan antes.",
            "La definitiva se carga más rápido.", "Recuperas vida al golpear.", "Ganas más oro de todo.", "Ganas más almas de todo.", "Atrae el botín desde más lejos.", "Tus golpes pueden prender fuego.",
            "Tus golpes pueden congelar.", "Tus golpes pueden soltar una descarga.", "Tus golpes pueden envenenar.", "Tus habilidades hacen más daño.", "Llevas un frasco de vida más.",
            "Si mueres, reapareces una vez con parte de tu vida."};
    private static final int[][] S_VAL = {
            {6, 10, 16, 25}, {10, 18, 28, 45}, {4, 7, 10, 15}, {4, 7, 11, 16}, {1, 2, 3, 5}, {3, 5, 8, 12}, {4, 7, 10, 15}, {10, 20, 35, 55}, {4, 7, 11, 16}, {10, 18, 28, 40},
            {1, 2, 3, 5}, {10, 18, 28, 40}, {10, 18, 28, 40}, {20, 35, 55, 80}, {8, 14, 20, 30}, {8, 14, 20, 30}, {8, 14, 20, 30}, {8, 14, 20, 30}, {6, 11, 18, 28}, {0, 0, 1, 2}, {0, 0, 0, 30}};
    private static final int[] S_CAP = {160, 200, 40, 45, 25, 36, 45, 160, 40, 120, 15, 150, 150, 200, 60, 60, 60, 60, 120, 3, 30};
    private static final int[] S_MINRAR = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3};
    private static final int[] S_WEIGHT = {10, 9, 7, 7, 5, 8, 8, 6, 7, 5, 5, 5, 5, 4, 5, 5, 5, 5, 7, 3, 2};

    // ---- intercambios (mejora grande con un coste): {stat1, v1, stat2, v2}
    private static final String[] T_NAME = {"Pacto de sangre", "Piel de piedra", "Furia temeraria", "Mente fría", "Vidrio mortal"};
    private static final String[] T_ICON = {"b_sangre", "b_piedra", "b_furia", "b_enfriamiento", "b_critico"};
    private static final int[][] T_FX = {{DMG, 22, HP, -15}, {DEF, 14, SPD, -8}, {ASPD, 18, DEF, -6}, {CD, 18, DMG, -6}, {DMG, 40, HP, -25}};
    private static final int[] T_RAR = {2, 2, 2, 2, 3};

    // ---- tipos de recompensa
    static final int K_STAT = 0, K_TRADE = 1, K_HEAL = 2, K_GOLD = 3, K_POTION = 4, K_BARRIER = 5, K_RECHARGE = 6,
            K_GREN_NEW = 7, K_GREN_MORE = 8, K_GREN_UP = 9, K_SEC_NEW = 10, K_SEC_AMMO = 11, K_SEC_UP = 12, K_SPECIAL = 13, K_SHIELD = 14;

    static final class Reward {
        int kind, id, rar, val;
        String name, amount = "", desc = "", bad = "", replaces = "", icon = "";
        int col = 0xFFFFFFFF;
        String key() { return kind + ":" + id; }
    }

    // ---- armas extra (se suman a las especiales existentes en Items)
    static final int[] SP_RAR = {0, 1, 1, 1, 2, 2, 3, 2, 1};
    static final String[] SP_ICON = {"", "burn", "freeze", "poison", "bleed", "shock", "star", "b_gigante", "b_furia"};
    private static final int[] SEC_RAR = Items.SEC_RAR;   // las rarezas viven con el resto de datos del arma (Items)
    static final int[] SH_RAR = {0, 1, 2, 2};
    static final String[] SH_ICON = {"shield", "shield", "shield", "shield"};
    static final int[] GR_RAR = {0, 1, 1, 1, 2, 2};

    // ================================================================ estadisticas
    static void applyStats(RunState rs, Stats s) {
        int[] c = rs.cb;
        s.dmgMul *= 1 + c[DMG] / 100f;
        s.maxHp = Math.max(30, s.maxHp + c[HP]);
        s.speedMul *= 1 + c[SPD] / 100f;
        s.atkSpd *= 1 + c[ASPD] / 100f;
        s.dmgTaken = Math.max(0.2f, s.dmgTaken * (1 - c[DEF] / 100f));
        s.critChance += c[CRIT] / 100f;
        s.critMul += c[CRITD] / 100f;
        s.cdMul = Math.max(0.35f, s.cdMul * (1 - c[CD] / 100f));
        s.ultGain *= 1 + c[ULT] / 100f;
        s.lifesteal += c[LS] / 100f;
        s.goldMul *= 1 + c[GOLD] / 100f;
        s.soulMul *= 1 + c[SOUL] / 100f;
        s.magnet += c[MAG];
        s.burn += c[BURN] / 100f; s.freeze += c[FREEZE] / 100f; s.shock += c[SHOCK] / 100f; s.poison += c[POISON] / 100f;
        s.skillDmg *= 1 + c[SKILL] / 100f;
        s.potionsMax += c[POT];
        if (c[REV] > 0 && s.revive == 0) { s.revive = 1; s.revivePct = c[REV] / 100f; }
        s.luck = c[LUCK];
    }

    // ================================================================ generacion
    static int rollRarity(Rng r, int luck, int minR) {
        float[] w = {Math.max(16f, 62f - 3.2f * luck), 28f + 0.8f * luck, 9f + 1.5f * luck, 1.5f + 0.7f * luck};
        for (int i = 0; i < minR; i++) w[i] = 0;
        float tot = 0; for (float x : w) tot += x;
        float t = r.f() * tot;
        for (int i = 0; i < 4; i++) { t -= w[i]; if (t <= 0 && w[i] > 0) return i; }
        return 3;
    }

    private static int luckOf(RunState rs, int bonus) { return rs.cb[LUCK] + bonus + rs.stage; }

    /** Genera las 3 opciones del juego indicado. Siempre distintas entre si y todas con efecto real. */
    static Reward[] roll(RunState rs, int mode, int luckBonus) {
        Rng r = rs.rng;
        int luck = luckOf(rs, luckBonus);
        List<Reward> out = new ArrayList<>();
        List<String> keys = new ArrayList<>();
        int guard = 0;
        while (out.size() < 3 && guard++ < 60) {
            Reward x = mode == MODE_WEAPONS ? rollWeapon(rs, r, luck, out.size()) : mode == MODE_ARSENAL ? rollArsenal(rs, r, luck, out.size()) : rollStat(rs, r, luck);
            if (x == null || keys.contains(x.key())) continue;
            keys.add(x.key()); out.add(x);
        }
        // si el juego pedido no daba para 3 (p. ej. todo al maximo), completa con mejoras de estadisticas
        guard = 0;
        while (out.size() < 3 && guard++ < 80) {
            Reward x = rollStat(rs, r, luck);
            if (x == null || keys.contains(x.key())) continue;
            keys.add(x.key()); out.add(x);
        }
        // ultimo recurso (todo al maximo): oro
        while (out.size() < 3) { Reward x = simple(rs, K_GOLD, out.size(), Math.min(3, out.size() + 1)); if (keys.contains(x.key())) x.id += 10; keys.add(x.key()); out.add(x); }
        return out.toArray(new Reward[0]);
    }

    private static boolean ok(RunState rs, int id, int add) {
        int c = rs.cb[id];
        return add >= 0 ? c + add <= S_CAP[id] : c + add >= -40;
    }

    private static Reward rollStat(RunState rs, Rng r, int luck) {
        int roll = r.i(100);
        // instantaneas y de intercambio: de vez en cuando
        if (roll < 12) return rollInstant(rs, r, luck);
        if (roll < 22) {
            int t = r.i(T_NAME.length);
            return trade(rs, t);
        }
        int tot = 0;
        for (int i = 0; i < N; i++) tot += S_WEIGHT[i];
        int p = r.i(tot), id = 0;
        for (int i = 0; i < N; i++) { p -= S_WEIGHT[i]; if (p < 0) { id = i; break; } }
        if (id == REV && (rs.stats.revive > 0 || rs.cb[REV] > 0)) return null;
        int rar = rollRarity(r, luck, S_MINRAR[id]);
        int v = S_VAL[id][rar];
        if (v <= 0) return null;
        // si no cabe entero, recorta; si no cabe nada, no se ofrece
        if (rs.cb[id] + v > S_CAP[id]) v = S_CAP[id] - rs.cb[id];
        if (v <= 0) return null;
        return stat(id, rar, v);
    }

    static Reward stat(int id, int rar, int v) {
        Reward x = new Reward();
        x.kind = K_STAT; x.id = id; x.rar = rar; x.val = v;
        x.name = S_NAME[id]; x.icon = S_ICON[id]; x.desc = S_DESC[id];
        x.amount = "+" + v + S_UNIT[id];
        return x;
    }

    private static Reward trade(RunState rs, int t) {
        int[] f = T_FX[t];
        if (!ok(rs, f[0], f[1]) || !ok(rs, f[2], f[3])) return null;
        Reward x = new Reward();
        x.kind = K_TRADE; x.id = t; x.rar = T_RAR[t]; x.val = 1;
        x.name = T_NAME[t]; x.icon = T_ICON[t];
        x.amount = "+" + f[1] + S_UNIT[f[0]];
        x.bad = f[3] + S_UNIT[f[2]].replace("% menos daño recibido", "% resistencia").replace("% menos recarga", "% recarga");
        x.desc = "Una mejora fuerte con un coste. Elígela solo si te conviene.";
        return x;
    }

    private static final int[] HEAL_PCT = {30, 45, 65, 100}, BARR = {20, 30, 45, 70}, RECH = {30, 45, 70, 100}, POT_N = {1, 1, 2, 3};

    private static Reward simple(RunState rs, int kind, int rar, int dummy) {
        Reward x = new Reward();
        x.kind = kind; x.rar = rar; x.id = 0; x.val = 0;
        switch (kind) {
            case K_HEAL: x.val = HEAL_PCT[rar]; x.name = "Fuente de vida"; x.icon = "heart"; x.amount = "+" + x.val + "% de vida"; x.desc = "Recuperas esa parte de tu vida máxima ahora mismo."; break;
            case K_GOLD: { int g = Math.round((60 + 25 * rs.stage) * new float[]{1f, 1.6f, 2.4f, 3.6f}[rar]); x.val = g; x.name = "Botín de oro"; x.icon = "coin"; x.amount = "+" + g + " oro"; x.desc = "Un montón de monedas y algunas almas para gastar en la tienda."; break; }
            case K_POTION: x.val = POT_N[rar]; x.name = "Frascos de vida"; x.icon = "potion"; x.amount = "+" + x.val + (x.val == 1 ? " frasco" : " frascos"); x.desc = "Rellena tus frascos de vida (hasta tu máximo)."; break;
            case K_BARRIER: x.val = BARR[rar]; x.name = "Barrera de luz"; x.icon = "shield"; x.amount = "+" + x.val + " escudo"; x.desc = "Un escudo temporal que absorbe daño antes que tu vida."; break;
            case K_RECHARGE: x.val = RECH[rar]; x.name = "Recarga total"; x.icon = "star"; x.amount = "+" + x.val + "% definitiva"; x.desc = "Reinicia las recargas de tus habilidades y carga tu definitiva."; break;
            default: break;
        }
        return x;
    }

    private static Reward rollInstant(RunState rs, Rng r, int luck) {
        int rar = rollRarity(r, luck, 0);
        int k = r.i(5);
        switch (k) {
            case 0: if (rs.hp > rs.stats.maxHp * 0.85f) return null; return simple(rs, K_HEAL, rar, 0);
            case 1: return simple(rs, K_GOLD, rar, 0);
            case 2: if (rs.potions >= rs.stats.potionsMax) return null; return simple(rs, K_POTION, rar, 0);
            case 3: return simple(rs, K_BARRIER, rar, 0);
            default: if (rs.ult >= 80f) return null; return simple(rs, K_RECHARGE, rar, 0);
        }
    }

    // ---- armas
    private static Reward rollWeapon(RunState rs, Rng r, int luck, int slot) {
        // categorias: 0 arma principal especial, 1 secundaria, 2 escudo
        int cat = slot < 3 ? (slot + r.i(3)) % 3 : r.i(3);
        if (r.chance(0.2f)) cat = r.i(3);
        int rar = rollRarity(r, luck, 0);
        List<Integer> c = new ArrayList<>();
        if (cat == 0) { for (int i = 1; i < Items.SP_COUNT; i++) if (i != rs.special) c.add(i); }
        else if (cat == 1) { for (int i = 1; i < Items.SEC_COUNT; i++) if (i != rs.sec) c.add(i); }
        else { for (int i = 0; i < Items.SH_COUNT; i++) if (i != rs.shield) c.add(i); }
        if (cat == 1 && rs.sec != 0 && rs.secLvl < 3 && r.chance(0.18f)) return secUp(rs);   // arma repetida: en vez de un duplicado, mejora de nivel
        if (c.isEmpty()) return null;
        // elige entre los candidatos el de rareza mas cercana a la tirada
        int best = -1, bd = 99;
        List<Integer> shuffled = new ArrayList<>(c);
        for (int i = shuffled.size() - 1; i > 0; i--) { int j = r.i(i + 1); int t = shuffled.get(i); shuffled.set(i, shuffled.get(j)); shuffled.set(j, t); }
        for (int id : shuffled) {
            int rr = cat == 0 ? SP_RAR[id] : cat == 1 ? SEC_RAR[id] : SH_RAR[id];
            int d = Math.abs(rr - rar);
            if (d < bd) { bd = d; best = id; }
        }
        return cat == 0 ? special(rs, best) : cat == 1 ? secNew(rs, best, r) : shield(rs, best);
    }

    static Reward special(RunState rs, int id) {
        Reward x = new Reward();
        x.kind = K_SPECIAL; x.id = id; x.rar = SP_RAR[id]; x.name = Items.SP_NAME[id]; x.icon = SP_ICON[id]; x.col = Items.SP_COL[id] | 0xFF000000;
        x.amount = "Arma principal"; x.desc = Items.SP_DESC[id];
        if (rs.special != 0) x.replaces = "Sustituye a " + Items.SP_NAME[rs.special];
        return x;
    }

    static Reward secNew(RunState rs, int id, Rng r) {
        Reward x = new Reward();
        x.kind = K_SEC_NEW; x.id = id; x.rar = SEC_RAR[id]; x.name = Items.SEC_NAME[id]; x.icon = Items.SEC_ICON[id]; x.col = Items.SEC_COL[id] | 0xFF000000;
        x.amount = "Arma secundaria · " + Items.SEC_AMMO[id] + " usos"; x.desc = Items.SEC_DESC[id];
        if (rs.sec != 0) x.replaces = "Sustituye a " + Items.SEC_NAME[rs.sec];
        return x;
    }

    static Reward shield(RunState rs, int id) {
        Reward x = new Reward();
        x.kind = K_SHIELD; x.id = id; x.rar = SH_RAR[id]; x.name = Items.SH_NAME[id]; x.icon = SH_ICON[id]; x.col = Items.SH_COL[id] | 0xFF000000;
        x.amount = "Escudo"; x.desc = Items.SH_DESC[id];
        if (rs.shield != id) x.replaces = "Sustituye a " + Items.SH_NAME[rs.shield];
        return x;
    }

    // ---- arsenal: granadas, municion y consumibles
    private static Reward rollArsenal(RunState rs, Rng r, int luck, int slot) {
        int rar = rollRarity(r, luck, 0);
        int k = r.i(100);
        if (k < 38) { // granadas
            if (rs.gren == 0) return grenNew(rs, 1 + r.i(Items.GR_COUNT - 1), rar, r);
            int q = r.i(3);
            if (q == 0 && rs.grenCount < 12) return grenMore(rs, rar);
            if (q == 1 && rs.grenLvl < 3) return grenUp(rs);
            int t = 1 + r.i(Items.GR_COUNT - 1);
            if (t == rs.gren) return rs.grenCount < 12 ? grenMore(rs, rar) : null;
            return grenNew(rs, t, rar, r);
        }
        if (k < 62) { // secundaria
            if (rs.sec == 0) return secNew(rs, 1 + r.i(Items.SEC_COUNT - 1), r);
            if (r.chance(0.5f) && rs.secLvl < 3) return secUp(rs);
            if (rs.secAmmo < Items.SEC_AMMO[rs.sec] * 2 && !Items.infinite(rs.sec)) return secAmmo(rs, rar);
            return null;
        }
        return rollInstant(rs, r, luck);
    }

    static Reward grenNew(RunState rs, int t, int rar, Rng r) {
        int n = new int[]{4, 5, 6, 8}[rar];
        Reward x = new Reward();
        x.kind = K_GREN_NEW; x.id = t; x.val = n; x.rar = rar;
        x.name = Items.GR_NAME[t]; x.icon = Items.GR_ICON[t]; x.col = Items.GR_COL[t] | 0xFF000000;
        x.amount = n + " granadas"; x.desc = Items.GR_DESC[t];
        if (rs.gren != 0) x.replaces = "Sustituye a " + Items.GR_NAME[rs.gren].replace("Granada de ", "").replace("Granada ", "");
        return x;
    }

    static Reward grenMore(RunState rs, int rar) {
        int n = new int[]{3, 4, 5, 7}[rar];
        n = Math.min(n, 12 - rs.grenCount);
        Reward x = new Reward();
        x.kind = K_GREN_MORE; x.id = rs.gren; x.val = n; x.rar = rar;
        x.name = "Más granadas"; x.icon = Items.GR_ICON[rs.gren]; x.col = Items.GR_COL[rs.gren] | 0xFF000000;
        x.amount = "+" + n + " granadas"; x.desc = "Munición extra para tu " + Items.GR_NAME[rs.gren].toLowerCase() + ".";
        return x;
    }

    static Reward grenUp(RunState rs) {
        Reward x = new Reward();
        x.kind = K_GREN_UP; x.id = rs.gren; x.val = rs.grenLvl + 1; x.rar = rs.grenLvl == 0 ? 1 : (rs.grenLvl == 1 ? 2 : 3);
        x.name = "Granadas mejoradas"; x.icon = Items.GR_ICON[rs.gren]; x.col = Items.GR_COL[rs.gren] | 0xFF000000;
        x.amount = "Nivel " + rs.grenLvl + " > " + x.val; x.desc = "Tus granadas hacen +25% de daño y explotan en un radio +15% mayor.";
        return x;
    }

    static Reward secAmmo(RunState rs, int rar) {
        int a = Math.max(2, Items.SEC_AMMO[rs.sec] * new int[]{40, 60, 90, 130}[rar] / 100);
        Reward x = new Reward();
        x.kind = K_SEC_AMMO; x.id = rs.sec; x.val = a; x.rar = rar;
        x.name = "Munición"; x.icon = Items.SEC_ICON[rs.sec]; x.col = Items.SEC_COL[rs.sec] | 0xFF000000;
        x.amount = "+" + a + " usos"; x.desc = "Recarga tu " + Items.SEC_NAME[rs.sec].toLowerCase() + " (hasta el doble de la carga base).";
        return x;
    }

    static Reward secUp(RunState rs) {
        Reward x = new Reward();
        x.kind = K_SEC_UP; x.id = rs.sec; x.val = rs.secLvl + 1; x.rar = rs.secLvl == 0 ? 1 : (rs.secLvl == 1 ? 2 : 3);
        x.name = "Arma secundaria mejorada"; x.icon = Items.SEC_ICON[rs.sec]; x.col = Items.SEC_COL[rs.sec] | 0xFF000000;
        x.amount = "Nivel " + rs.secLvl + " > " + x.val; x.desc = "Tu arma secundaria hace +25% de daño y se dispara más rápido.";
        return x;
    }

    // ================================================================ aplicar
    /** Aplica la recompensa elegida al estado de la run. Devuelve texto de aviso. Los efectos sobre el jugador en pantalla (barrera) los hace quien llama. */
    static String apply(RunState rs, Reward x) {
        switch (x.kind) {
            case K_STAT:
                rs.cb[x.id] += x.val;
                rs.recalc();
                if (x.id == HP) rs.hp = Math.min(rs.stats.maxHp, rs.hp + x.val);
                if (x.id == POT) rs.potions = Math.min(rs.stats.potionsMax, rs.potions + 1);
                break;
            case K_TRADE: {
                int[] f = T_FX[x.id];
                rs.cb[f[0]] += f[1]; rs.cb[f[2]] += f[3];
                rs.recalc();
                rs.hp = Math.min(rs.stats.maxHp, rs.hp);
                break;
            }
            case K_HEAL: rs.hp = Math.min(rs.stats.maxHp, rs.hp + rs.stats.maxHp * x.val / 100f); break;
            case K_GOLD: rs.gold += x.val; rs.souls += x.val / 4; break;
            case K_POTION: rs.potions = Math.min(rs.stats.potionsMax, rs.potions + x.val); break;
            case K_BARRIER: break;   // lo aplica RunScreen sobre el jugador
            case K_RECHARGE: for (int i = 0; i < rs.cd.length; i++) rs.cd[i] = 0; rs.ult = Math.min(100f, rs.ult + x.val); break;
            case K_GREN_NEW: rs.gren = x.id; rs.grenCount = x.val; break;
            case K_GREN_MORE: rs.grenCount = Math.min(12, rs.grenCount + x.val); break;
            case K_GREN_UP: rs.grenLvl = Math.min(3, rs.grenLvl + 1); break;
            case K_SEC_NEW: Arsenal.equip(rs, x.id, 0); break;
            case K_SEC_AMMO: rs.secAmmo = Math.min(Items.SEC_AMMO[rs.sec] * 2, rs.secAmmo + x.val); break;
            case K_SEC_UP: rs.secLvl = Math.min(3, rs.secLvl + 1); break;
            case K_SPECIAL: rs.special = x.id; rs.markNew("o:sp" + x.id); rs.recalc(); break;
            case K_SHIELD: rs.shield = x.id; rs.markNew("o:sh" + x.id); break;
            default: break;
        }
        return x.name;
    }

    /** Que juego de opciones sale segun el tipo de cofre (0 normal, 1 tesoro/arsenal, 2 recompensa de mini-jefe, 3 secreto). */
    static int modeFor(Rng r, int chestArg) {
        String dbg = System.getenv("BOT_CHESTMODE");   // solo banco de pruebas de escritorio
        if (dbg != null) return Integer.parseInt(dbg);
        float p = r.f();
        switch (chestArg) {
            case 1: return p < 0.30f ? MODE_WEAPONS : (p < 0.70f ? MODE_ARSENAL : MODE_STATS);
            case 2: return p < 0.25f ? MODE_WEAPONS : (p < 0.40f ? MODE_ARSENAL : MODE_STATS);
            case 4: return p < 0.35f ? MODE_WEAPONS : (p < 0.70f ? MODE_ARSENAL : MODE_STATS);
            case 3: return p < 0.40f ? MODE_WEAPONS : (p < 0.80f ? MODE_ARSENAL : MODE_STATS);
            default: return p < 0.12f ? MODE_WEAPONS : (p < 0.25f ? MODE_ARSENAL : MODE_STATS);
        }
    }

    static int luckBonusFor(int chestArg) { if (System.getenv("BOT_LUCK") != null) return Integer.parseInt(System.getenv("BOT_LUCK")); return chestArg == 2 ? 6 : (chestArg == 4 ? 9 : chestArg == 3 ? 5 : (chestArg == 1 ? 2 : 0)); }
}
