package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** Trofeos y logros de la cuenta. Se calculan a partir de las estadisticas reales guardadas (Save); la mascara persistida solo sirve para avisar una vez. */
final class Trophies {
    private Trophies() {}

    static final class T {
        final String name, desc; final java.util.function.Predicate<Save> test; final java.util.function.ToIntFunction<Save> prog; final int goal;
        T(String n, String d, java.util.function.ToIntFunction<Save> prog, int goal) { name = n; desc = d; this.prog = prog; this.goal = goal; this.test = s -> prog.applyAsInt(s) >= goal; }
    }

    static final T[] ALL = {
            new T("Primera sangre", "Derrota 1 enemigo", s -> s.kills, 1),
            new T("Cazador", "Derrota 100 enemigos", s -> s.kills, 100),
            new T("Matanza", "Derrota 1000 enemigos", s -> s.kills, 1000),
            new T("Rey caído", "Derrota a un jefe", s -> s.bossKills, 1),
            new T("Cazajefes", "Derrota a 8 jefes", s -> s.bossKills, 8),
            new T("Ronda perfecta", "Ronda sin recibir daño", s -> s.perfectRounds, 1),
            new T("Intocable", "5 perfectas seguidas", s -> s.bestPerfectStreak, 5),
            new T("Imparable", "10 rondas seguidas", s -> s.bestStreak, 10),
            new T("Victoria", "Gana una partida", s -> s.wins, 1),
            new T("Coleccionista", "Desbloquea 5 clases", s -> { int n = 0; for (boolean b : s.classUnlocked) if (b) n++; return n; }, 5),
            new T("Maestro", "Desbloquea los 10", s -> { int n = 0; for (boolean b : s.classUnlocked) if (b) n++; return n; }, 10),
            new T("Explorador", "3 cofres secretos", s -> s.secretChests, 3),
            new T("Sello forjado", "Reúne 8 reliquias", s -> s.relicCount(), 8),
            new T("Caza al Cazador", "Vence al Cazador", s -> s.finalBeaten ? 1 : 0, 1),
            new T("Almas sin fin", "5000 almas en total", s -> s.totalSouls, 5000),
            new T("Veterano", "Juega 1 hora", s -> (int) (s.playMs / 60000L), 60),
    };

    static boolean has(Save s, int i) { return ALL[i].test.test(s); }
    static int count(Save s) { int n = 0; for (int i = 0; i < ALL.length; i++) if (has(s, i)) n++; return n; }

    /** Devuelve los trofeos recien ganados (y los marca como avisados). */
    static List<String> check(Save s) {
        List<String> out = new ArrayList<>();
        int m = s.trophyMask;
        for (int i = 0; i < ALL.length; i++) if (has(s, i) && (m & (1 << i)) == 0) { m |= 1 << i; out.add(ALL[i].name); }
        if (m != s.trophyMask) { s.trophyMask = m; s.write(); }
        return out;
    }
}
