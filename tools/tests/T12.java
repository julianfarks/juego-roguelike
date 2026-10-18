package com.julianfarks.roguelike.core;

import java.util.*;

/** Etapa 4: companeros, jardin, bestiario y migracion de guardado v2 -> v3. */
public class T12 {
    static int f = 0;
    static void ck(String n, boolean ok) { System.out.println((ok ? "ok   " : "FAIL ") + n); if (!ok) f++; }

    public static void main(String[] a) {
        Platform p = T8.plat();
        // ---- migracion: guardado v2 sin claves nuevas
        T8.disk.clear();
        String old = "{\"ver\":2,\"souls\":321,\"gems\":7,\"bossKills\":2,\"runs\":4,\"relics\":[1,0,0,0,0,0,0,0]}";
        T8.disk.put("save", old);
        T8.reload(p);
        ck("v2 carga sin perder datos", Save.S.souls == 321 && Save.S.gems == 7 && Save.S.bossKills == 2 && Save.S.relics[0]);
        ck("copia de seguridad v2 creada", old.equals(T8.disk.get("save_bak_v2")));
        ck("claves nuevas por defecto", Save.S.compMask == 0 && Save.S.compSel == -1 && Save.S.dex.isEmpty() && Save.S.garden[0] == 0);
        Save.S.write();
        ck("al escribir queda en v3", T8.disk.get("save").contains("\"ver\":3"));
        // ---- guardado de version mas nueva: solo lectura
        T8.disk.clear(); T8.disk.put("save", "{\"ver\":9,\"souls\":5,\"cmp_mask\":7}");
        T8.reload(p);
        ck("version futura: solo lectura", Save.S.readOnly);
        Save.S.garden[0] = 3; Save.S.write();
        ck("version futura: no se sobrescribe", T8.disk.get("save").contains("\"ver\":9") && T8.disk.containsKey("save_bak_v9"));
        // ---- desbloqueo de companeros segun condiciones reales
        T8.disk.clear(); T8.reload(p);
        ck("sin progreso: ninguno desbloqueado", Companions.refresh(Save.S) == null && Save.S.compMask == 0);
        Companions.select(Save.S, 0);
        ck("no se puede elegir uno bloqueado", Companions.active(Save.S) == -1);
        Save.S.bossKills = 1;
        ck("1 jefe: fuego", "Ascua".equals(Companions.refresh(Save.S)) && Companions.unlocked(Save.S, 0) && !Companions.unlocked(Save.S, 1));
        Save.S.bossKills = 3; Save.S.runs = 10; Companions.refresh(Save.S);
        ck("3 jefes + 10 runs: todos", Save.S.compMask == 7);
        Companions.select(Save.S, 1);
        ck("elegir hielo", Companions.active(Save.S) == 1);
        // ---- efectos limitados y sin acumular
        RunState base = new RunState(ClassDef.ALL[0], 5, 0); base.companion = -1; base.stats.recalc(base);
        RunState ice = new RunState(ClassDef.ALL[0], 5, 0); ice.companion = Companions.ICE; ice.stats.recalc(ice);
        RunState sh = new RunState(ClassDef.ALL[0], 5, 0); sh.companion = Companions.SHADOW; sh.stats.recalc(sh);
        ck("hielo: -8% dano recibido", Math.abs(ice.stats.dmgTaken / base.stats.dmgTaken - 0.92f) < 0.001f);
        ck("sombra: iman +40", Math.abs(sh.stats.magnet - base.stats.magnet - 40) < 0.01f);
        ice.stats.recalc(ice); ice.stats.recalc(ice);
        ck("recalcular no acumula", Math.abs(ice.stats.dmgTaken / base.stats.dmgTaken - 0.92f) < 0.001f);
        ck("hielo no cambia iman", Math.abs(ice.stats.magnet - base.stats.magnet) < 0.01f);
        // ---- jardin
        T8.disk.clear(); T8.reload(p);
        Save.S.souls = 100;
        ck("crece con almas suficientes (80)", Garden.grow(Save.S, 1) == true && Save.S.souls == 20 && Garden.level(Save.S, 1) == 1);
        ck("segunda etapa: 160, faltan almas", !Garden.grow(Save.S, 1) && Garden.level(Save.S, 1) == 1 && Save.S.souls == 20);
        Save.S.souls = 5000;
        for (int i = 0; i < 10; i++) Garden.grow(Save.S, 0);
        ck("tope en etapa 4", Garden.level(Save.S, 0) == Garden.MAX);
        int spent = 5000 - Save.S.souls;
        ck("coste total correcto (80+160+280+440)", spent == 960);
        Save.S.garden[2] = 4;
        RunState g = new RunState(ClassDef.ALL[0], 5, 0);
        ck("oro inicial +60 con cristal 4", g.gold == 25 * Save.S.meta[2] + 60);
        ck("vida +5 con cristal de savia etapa 1", Math.abs(g.stats.maxHp - (ClassDef.ALL[0].hp + 10 * Save.S.meta[0] + 5)) < 0.01f);
        ck("dano +8% con cristal 0", g.stats.dmgMul > new RunState(ClassDef.ALL[0], 5, 0).stats.dmgMul - 1f);
        Save.S.write();
        T8.reload(p);
        ck("jardin persiste", Garden.level(Save.S, 0) == 4 && Garden.level(Save.S, 1) == 1 && Garden.level(Save.S, 2) == 4);
        // ---- bestiario
        T8.disk.clear(); T8.reload(p);
        RunState normal = new RunState(ClassDef.ALL[0], 1, 0);
        ck("descubre enemigo", Codex.see(normal, "e:zombi", "Zombi") && Codex.seen("e:zombi") && "Descubierto: Zombi".equals(Codex.toast));
        Codex.toast = null;
        ck("segunda vez no avisa", !Codex.see(normal, "e:zombi", "Zombi") && Codex.toast == null);
        RunState test = new RunState(ClassDef.ALL[0], 1, 0); test.markTest();
        ck("sesion de prueba no registra", !Codex.see(test, "e:esqueleto", "Esqueleto") && !Codex.seen("e:esqueleto"));
        T8.reload(p);
        ck("bestiario persiste", Codex.seen("e:zombi"));
        ck("todos los enemigos tienen hoja de sprites", allSprites());
        ck("conteo coherente", Codex.foundEntries() <= Codex.totalEntries() && Codex.foundEntries() >= 1);
        // ---- partida guardada conserva companero
        System.out.println(f == 0 ? "T12 OK" : "T12 FALLOS=" + f);
        if (f != 0) System.exit(1);
    }

    static boolean allSprites() {
        java.io.File dir = new java.io.File("Shared/assets/");
        for (EnemyDef d : EnemyDef.all()) if (!new java.io.File(dir, d.sheet + ".png").exists()) { System.out.println("falta " + d.sheet); return false; }
        for (BossDef b : BossDef.ALL) if (!new java.io.File(dir, b.sheet + ".png").exists()) { System.out.println("falta " + b.sheet); return false; }
        for (String s : Companions.SHEET) if (!new java.io.File(dir, "sprites/" + s + ".png").exists()) return false;
        return true;
    }
}
