package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Guardado de partidas en curso: 3 ranuras manuales + autoguardado. Se reanuda al inicio de la sala actual. */
final class RunSave {
    private RunSave() {}
    static final int SLOTS = 3;
    static final int AUTO = -1;

    static String key(int slot) { return slot == AUTO ? "run_auto" : "run_" + slot; }

    static Map<String, Object> read(Platform p, int slot) {
        try {
            String s = p.store().get(key(slot), "");
            if (s == null || s.isEmpty()) return null;
            Map<String, Object> d = Json.parseObj(s);
            return d == null || d.isEmpty() ? null : d;
        } catch (RuntimeException e) { return null; }
    }

    static void write(Platform p, RunScreen r, int slot) {
        RunState rs = r.rs;
        if (rs.sandbox) return;
        r.mySlots.add(slot);
        try {
            Map<String, Object> d = new LinkedHashMap<>();
            d.put("cls", r.cls.id);
            d.put("room", r.lv != null ? r.lv.room.type : Room.HUB);
            d.put("biome", rs.biome == null ? -1 : rs.biome.id);
            d.put("stage", rs.stage); d.put("roomNo", rs.roomNo); d.put("roomsDone", rs.roomsDone);
            int[] vis = new int[rs.visited.size()]; for (int i = 0; i < vis.length; i++) vis[i] = rs.visited.get(i);
            d.put("visited", vis);
            d.put("gold", rs.gold); d.put("souls", rs.souls); d.put("kills", rs.kills); d.put("bossKills", rs.bossKills);
            d.put("potions", rs.potions); d.put("weaponLvl", rs.weaponLvl);
            d.put("hp", (int) Math.ceil(rs.hp)); d.put("ult", (int) rs.ult);
            d.put("revive", rs.reviveUsed); d.put("time", (int) rs.time);
            d.put("asc", rs.asc); d.put("diff", rs.diff);
            d.put("blessTaken", rs.blessingTaken); d.put("dmgTaken", rs.damageTaken);
            int[] rl = new int[8]; for (int i = 0; i < 8; i++) rl[i] = rs.relicsThisRun[i] ? 1 : 0;
            d.put("relics", rl);
            d.put("finalRun", rs.finalRun);
            d.put("bless", rs.bless);
            d.put("sec", rs.sec); d.put("secAmmo", rs.secAmmo); d.put("gren", rs.gren); d.put("grenCount", rs.grenCount);
            d.put("special", rs.special); d.put("shield", rs.shield); d.put("secrets", rs.secretsFound);
            d.put("devAsst", rs.devAssisted); d.put("inf", rs.infinite); d.put("infCamp", rs.infFromCampaign); d.put("floor", rs.floor); d.put("floorsDone", rs.floorsDone); d.put("revs", rs.revivesUsed);
            d.put("infRooms", rs.infRooms); d.put("infBK", rs.infBaseKills); d.put("infBB", rs.infBaseBoss); d.put("infT0", (int) rs.infT0);
            d.put("credK", rs.credKills); d.put("credB", rs.credBoss); d.put("seed", (double) rs.seed); d.put("streak", rs.streak); d.put("pstreak", rs.perfectStreak);
            d.put("cb", rs.cb); d.put("grenLvl", rs.grenLvl); d.put("secLvl", rs.secLvl);
            d.put("ts", (double) System.currentTimeMillis());
            p.store().put(key(slot), Json.write(d));
            p.store().commit();
        } catch (RuntimeException e) {
            p.log("run save error " + e);
        }
    }

    /** Reconstruye la partida; null si la ranura esta vacia o corrupta. */
    static RunScreen load(Game g, int slot) {
        Map<String, Object> d = read(g.P, slot);
        if (d == null) return null;
        try {
            int ci = Math.max(0, Math.min(ClassDef.ALL.length - 1, Json.i(d, "cls", 0)));
            RunScreen scr = new RunScreen(g, ClassDef.ALL[ci], Json.i(d, "asc", 0));
            RunState rs = scr.rs;
            rs.diff = Json.i(d, "diff", 1);
            int b = Json.i(d, "biome", -1);
            rs.biome = b >= 0 && b < Biome.ALL.length ? Biome.ALL[b] : null;
            rs.stage = Json.i(d, "stage", 0); rs.roomNo = Json.i(d, "roomNo", 0); rs.roomsDone = Json.i(d, "roomsDone", 0);
            int[] vis = Json.ints(d, "visited");
            rs.visited.clear(); if (vis != null) for (int v : vis) rs.visited.add(v);
            rs.gold = Json.i(d, "gold", 0); rs.souls = Json.i(d, "souls", 0); rs.kills = Json.i(d, "kills", 0); rs.bossKills = Json.i(d, "bossKills", 0);
            rs.potions = Json.i(d, "potions", 2); rs.weaponLvl = Json.i(d, "weaponLvl", 0);
            rs.ult = Json.i(d, "ult", 0);
            rs.reviveUsed = Json.bool(d, "revive", false); rs.time = Json.i(d, "time", 0);
            rs.blessingTaken = Json.bool(d, "blessTaken", false); rs.damageTaken = Json.i(d, "dmgTaken", 0);
            int[] rl = Json.ints(d, "relics"); if (rl != null) for (int i = 0; i < Math.min(8, rl.length); i++) rs.relicsThisRun[i] = rl[i] != 0;
            rs.finalRun = Json.bool(d, "finalRun", false);
            int[] bl = Json.ints(d, "bless"); if (bl != null) for (int i = 0; i < Math.min(bl.length, rs.bless.length); i++) rs.bless[i] = bl[i];
            rs.sec = Json.i(d, "sec", 0); rs.secAmmo = Json.i(d, "secAmmo", 0); rs.gren = Json.i(d, "gren", 0); rs.grenCount = Json.i(d, "grenCount", 0);
            rs.special = Json.i(d, "special", 0); rs.shield = Json.i(d, "shield", 0); rs.secretsFound = Json.i(d, "secrets", 0);
            int[] cbv = Json.ints(d, "cb"); if (cbv != null) for (int i = 0; i < Math.min(cbv.length, rs.cb.length); i++) rs.cb[i] = cbv[i];
            rs.grenLvl = Json.i(d, "grenLvl", 0); rs.secLvl = Json.i(d, "secLvl", 0);
            rs.devAssisted = Json.bool(d, "devAsst", false); rs.infinite = Json.bool(d, "inf", false); rs.infFromCampaign = Json.bool(d, "infCamp", false);
            rs.floor = Math.max(1, Json.i(d, "floor", 1)); rs.floorsDone = Json.i(d, "floorsDone", 0);
            rs.revivesUsed = Math.max(0, Math.min(rs.ruleset.maxRevives, Json.i(d, "revs", 0)));
            rs.infRooms = Json.i(d, "infRooms", 0); rs.infBaseKills = Json.i(d, "infBK", 0); rs.infBaseBoss = Json.i(d, "infBB", 0); rs.infT0 = Json.i(d, "infT0", 0);
            rs.credKills = Json.i(d, "credK", 0); rs.credBoss = Json.i(d, "credB", 0);
            rs.streak = Json.i(d, "streak", 0); rs.perfectStreak = Json.i(d, "pstreak", 0);
            if (rs.infinite) rs.stage = 2;
            rs.stats.recalc(rs);
            rs.hp = Math.max(1, Math.min(rs.stats.maxHp, Json.i(d, "hp", (int) rs.stats.maxHp)));
            scr.resumeType = Json.i(d, "room", Room.HUB);
            scr.mySlots.add(slot);
            return scr;
        } catch (RuntimeException e) {
            g.P.log("run load error " + e);
            return null;
        }
    }

    /** Al morir: borra las partidas guardadas de esta run (ranuras usadas/cargadas y el autoguardado). */
    static void clearRun(Platform p, RunScreen r) {
        try {
            r.mySlots.add(AUTO);
            for (int sl : r.mySlots) p.store().put(key(sl), "");
            p.store().commit();
        } catch (RuntimeException e) { p.log("run clear error " + e); }
    }

    static String info(Platform p, int slot) {
        Map<String, Object> d = read(p, slot);
        if (d == null) return null;
        int ci = Math.max(0, Math.min(ClassDef.ALL.length - 1, Json.i(d, "cls", 0)));
        int b = Json.i(d, "biome", -1);
        String where = b >= 0 && b < Biome.ALL.length ? Biome.ALL[b].name + " · sala " + Math.min(5, Json.i(d, "roomNo", 0) + 1) + "/5" : "Santuario del Viajero";
        if (Json.bool(d, "inf", false)) where = "Infinito · piso " + Math.max(1, Json.i(d, "floor", 1)) + " · " + where;
        int t = Json.i(d, "time", 0);
        String when = "";
        double ts = Json.num(d, "ts", 0);
        if (ts > 0) when = new java.text.SimpleDateFormat("dd/MM HH:mm").format(new java.util.Date((long) ts));
        return ClassDef.ALL[ci].name + " · " + where + " · " + t / 60 + ":" + (t % 60 < 10 ? "0" : "") + t % 60 + (when.isEmpty() ? "" : " · " + when);
    }

    static boolean any(Platform p) {
        if (read(p, AUTO) != null) return true;
        for (int i = 0; i < SLOTS; i++) if (read(p, i) != null) return true;
        return false;
    }
}
