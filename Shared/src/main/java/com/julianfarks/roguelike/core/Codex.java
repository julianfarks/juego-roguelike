package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** Coleccion y bestiario. Guarda enemigos (e:id), jefes (b:idx) y sucesos (v:k) vistos; reliquias y espadachines se derivan del guardado. */
public final class Codex {
    private Codex() {}

    /** Aviso discreto pendiente de mostrar (lo recoge RunScreen). */
    public static String toast;

    public static boolean seen(String key) { return Save.S != null && Save.S.dex.contains(key); }

    /** Registra un descubrimiento. Las sesiones de prueba no registran nada. */
    public static boolean see(RunState rs, String key, String label) {
        Save s = Save.S;
        if (s == null || s.readOnly || (rs != null && rs.isTest()) || s.dex.contains(key)) return false;
        s.dex.add(key);
        s.write();
        toast = "Descubierto: " + label;
        return true;
    }

    /** Enemigos normales y elites ordenados (normales por vida, luego elites). */
    public static List<EnemyDef> enemies() {
        List<EnemyDef> l = new ArrayList<>(EnemyDef.all());
        l.sort((a, b) -> a.elite != b.elite ? (a.elite ? 1 : -1) : a.id.compareTo(b.id));
        return l;
    }

    public static String roleName(int r) {
        String[] n = {"Cuerpo a cuerpo", "A distancia", "Volador", "Volador picado", "Embestidor", "Saltador", "Hechicero", "Pesado",
                "Escudero", "Apoyo", "Explosivo", "Torreta", "Acechador", "Francotirador", "Potenciador", "Teletransportador", "Élite"};
        return r >= 0 && r < n.length ? n[r] : "?";
    }

    public static String pretty(String id) {
        String s = id.replace('_', ' ');
        return Character.toUpperCase(s.charAt(0)) + s.substring(1);
    }

    public static int totalEntries() { return EnemyDef.all().size() + BossDef.ALL.length + Events.COUNT - 1 + 8 + 10; }

    public static int foundEntries() {
        Save s = Save.S; int n = 0;
        for (EnemyDef d : EnemyDef.all()) if (s.dex.contains("e:" + d.id)) n++;
        for (int i = 0; i < BossDef.ALL.length; i++) if (s.dex.contains("b:" + i)) n++;
        for (int k = 1; k < Events.COUNT; k++) if (s.dex.contains("v:" + k)) n++;
        for (boolean b : s.relics) if (b) n++;
        for (int i = 0; i < 10; i++) if (s.classUnlocked[i]) n++;
        return n;
    }
}
