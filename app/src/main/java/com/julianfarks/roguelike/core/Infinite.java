package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Modo infinito: reglas, puntuacion, revividas y registro local de resultados.
 * Un "piso" = un bioma completo (5 salas + jefe). Criterio principal de clasificacion: PISOS COMPLETADOS;
 * desempate: puntaje, enemigos derrotados y menor tiempo. Los valores de la formula son provisionales y ajustables.
 */
public final class Infinite {
    private Infinite() {}

    public static final int SCORE_VERSION = 1;
    public static final int LOG_KEEP = 20;

    /** Conjunto de reglas de una run. NORMAL: 3 revividas (anuncio o gemas). COMPETITIVE: reservado para el futuro (sin gemas ni ventajas de pago). */
    public static final class Ruleset {
        public final String id; public final int maxRevives; public final boolean gemRevives, adRevives;
        Ruleset(String id, int maxRevives, boolean gemRevives, boolean adRevives) { this.id = id; this.maxRevives = maxRevives; this.gemRevives = gemRevives; this.adRevives = adRevives; }
    }
    public static final Ruleset NORMAL = new Ruleset("normal", 3, true, true);
    /** Reglas uniformes para una futura clasificacion con premios: sin revividas compradas. NO esta activo ni es seleccionable todavia. */
    public static final Ruleset COMPETITIVE = new Ruleset("competitive_v1", 0, false, false);

    // ------------------------------------------------------------------ dificultad
    /** "power" de enemigos: el piso 1 equivale al final de la campana (~18) y sube 5 por piso. */
    public static int power(int floor, int roomNo) { return 18 + 5 * (Math.max(1, floor) - 1) + roomNo; }
    public static float bossHpMul(int floor) { return 1f + 0.18f * (Math.max(1, floor) - 1); }
    public static float bossDmgMul(int floor) { return 1f + 0.08f * (Math.max(1, floor) - 1); }
    /** Probabilidad de que un enemigo normal aparezca como elite (desde el piso 3). */
    public static float eliteChance(int floor) { return floor < 3 ? 0f : Math.min(0.5f, 0.08f * (floor - 2)); }

    // ------------------------------------------------------------------ puntuacion
    public static int score(int floorsDone, int kills, int bosses, int rooms) {
        return floorsDone * 10000 + kills * 10 + bosses * 250 + rooms * 20;
    }

    // ------------------------------------------------------------------ revividas
    public enum Method { AD_STANDARD, AD_LONG, GEMS }
    /** Coste en gemas de cada revivida (indice 0..2). PROVISIONAL: decision de diseno pendiente. */
    public static final int[] GEM_COST = {5, 10, 15};

    public static final class Offer {
        public final Method method; public final boolean available; public final int cost; public final String why;
        Offer(Method m, boolean ok, int cost, String why) { method = m; available = ok; this.cost = cost; this.why = why; }
    }

    /** Se puede ofrecer otra revivida (queda alguna segun las reglas de la run). */
    public static boolean hasRevivesLeft(RunState rs) { return rs.infinite && rs.revivesUsed < rs.ruleset.maxRevives; }

    /** Opciones segun la revivida que toca: 1a anuncio|gemas, 2a anuncio largo|gemas, 3a solo gemas. */
    public static List<Offer> offers(RunState rs) {
        List<Offer> l = new ArrayList<>();
        if (!hasRevivesLeft(rs)) return l;
        int n = rs.revivesUsed;
        Ruleset r = rs.ruleset;
        if (r.adRevives && n < 2) {
            Services.AdPlacement p = n == 0 ? Services.AdPlacement.REVIVE_STANDARD : Services.AdPlacement.REVIVE_LONG;
            boolean ok = Services.ads != null && Services.ads.isReady(p);
            l.add(new Offer(n == 0 ? Method.AD_STANDARD : Method.AD_LONG, ok, 0, ok ? "" : "Anuncio no disponible"));
        }
        if (r.gemRevives) {
            int c = GEM_COST[Math.min(n, GEM_COST.length - 1)];
            boolean ok = Wallet.canSpend(c);
            l.add(new Offer(Method.GEMS, ok, c, ok ? "" : "Gemas insuficientes"));
        }
        return l;
    }

    /** Hay al menos una forma real de revivir ahora mismo (si no, se pasa directo a los resultados). */
    public static boolean anyAvailable(RunState rs) { for (Offer o : offers(rs)) if (o.available) return true; return false; }

    /**
     * Intenta consumir una revivida con ese metodo. Para gemas descuenta el saldo y marca la revivida en UNA escritura.
     * Para anuncios, el que llama debe haber confirmado COMPLETED antes (ver Services.requestRewardedAd).
     * Devuelve true solo si la revivida queda concedida; nunca concede mas de maxRevives.
     */
    public static boolean consume(RunState rs, Method m, Platform p) {
        if (!hasRevivesLeft(rs)) return false;
        int n = rs.revivesUsed;
        if (m == Method.GEMS) {
            if (!rs.ruleset.gemRevives) return false;
            boolean[] dev = {false};
            if (!Wallet.spend(GEM_COST[Math.min(n, GEM_COST.length - 1)], false, dev)) return false;
            if (dev[0]) rs.devAssisted = true;     // la run uso gemas de prueba: su resultado queda marcado y no es valido para clasificacion
        } else {
            if (!rs.ruleset.adRevives || n >= 2) return false;
            if ((m == Method.AD_STANDARD) != (n == 0)) return false;     // el formato debe corresponder a la revivida
        }
        rs.revivesUsed++;
        return true;
    }

    // ------------------------------------------------------------------ resultados
    public static final class Result {
        public String ruleset = "normal"; public boolean dev; public int cls, floors, reached, kills, bosses, rooms, timeS, revives, score, ver = SCORE_VERSION;
        public long seed, ts;
        /** Comparacion de clasificacion: pisos, puntaje, enemigos, menos tiempo. >0 si a es mejor que b. */
        public static int compare(Result a, Result b) {
            if (a.floors != b.floors) return Integer.compare(a.floors, b.floors);
            if (a.score != b.score) return Integer.compare(a.score, b.score);
            if (a.kills != b.kills) return Integer.compare(a.kills, b.kills);
            return Integer.compare(b.timeS, a.timeS);
        }
        public String toJson() {
            Map<String, Object> d = new LinkedHashMap<>();
            d.put("v", ver); d.put("rules", ruleset); d.put("cls", cls); d.put("fl", floors); d.put("hi", reached); d.put("k", kills);
            d.put("b", bosses); d.put("r", rooms); d.put("t", timeS); d.put("rev", revives); d.put("sc", score);
            d.put("seed", (double) seed); d.put("ts", (double) ts);
            d.put("dev", dev); d.put("chk", check());
            return Json.write(d);
        }
        /** Suma de control para detectar ediciones torpes del registro local. NO es seguridad: una clasificacion con premios necesita validacion en servidor. */
        int check() {
            long h = 1125899906842597L;
            for (long v : new long[]{dev ? 1 : 0, ver, cls, floors, reached, kills, bosses, rooms, timeS, revives, score, seed, ts}) h = 31 * h + v;
            for (char c : ruleset.toCharArray()) h = 31 * h + c;
            return (int) (h ^ (h >>> 32));
        }
        public static Result parse(String s) {
            try {
                Map<String, Object> d = Json.parseObj(s);
                if (d == null) return null;
                Result r = new Result();
                r.ver = Json.i(d, "v", 1); r.ruleset = Json.str(d, "rules", "normal"); r.cls = Json.i(d, "cls", 0); r.floors = Json.i(d, "fl", 0);
                r.reached = Json.i(d, "hi", 0); r.kills = Json.i(d, "k", 0); r.bosses = Json.i(d, "b", 0); r.rooms = Json.i(d, "r", 0);
                r.dev = Json.bool(d, "dev", false); r.timeS = Json.i(d, "t", 0); r.revives = Json.i(d, "rev", 0); r.score = Json.i(d, "sc", 0);
                r.seed = (long) Json.num(d, "seed", 0); r.ts = (long) Json.num(d, "ts", 0);
                return Json.i(d, "chk", 0) == r.check() ? r : null;
            } catch (RuntimeException e) { return null; }
        }
    }

    /** Resultado final de una run infinita (a partir del estado de la run). */
    public static Result resultOf(RunState rs) {
        Result r = new Result();
        r.ruleset = rs.ruleset.id; r.cls = rs.cls.id; r.dev = rs.devAssisted;
        r.floors = rs.floorsDone; r.reached = rs.floor;
        r.kills = rs.kills - rs.infBaseKills; r.bosses = rs.bossKills - rs.infBaseBoss;
        r.rooms = rs.infRooms;
        r.timeS = Math.max(0, (int) (rs.time - rs.infT0));
        r.revives = rs.revivesUsed; r.seed = rs.seed; r.ts = System.currentTimeMillis();
        r.score = score(r.floors, r.kills, r.bosses, r.rooms);
        return r;
    }

    /** Guarda el resultado en el perfil (una sola vez por run; el que llama controla 'ended'). Devuelve true si es un record de pisos. */
    public static boolean record(Save s, Result r) {
        s.infRuns++;
        if (r.dev) {                                   // run con gemas de prueba: queda en el historial marcada, pero no cuenta para records ni totales
            s.infLog.add(r.toJson());
            while (s.infLog.size() > LOG_KEEP) s.infLog.remove(0);
            return false;
        }
        s.infFloors += r.floors; s.infKills += r.kills; s.infBosses += r.bosses;
        boolean rec = r.floors > s.infBestFloor || (r.floors == s.infBestFloor && r.score > s.infBestScore);
        s.infBestFloor = Math.max(s.infBestFloor, r.floors);
        s.infBestScore = Math.max(s.infBestScore, r.score);
        s.infBestTimeS = Math.max(s.infBestTimeS, r.timeS);
        s.infLog.add(r.toJson());
        while (s.infLog.size() > LOG_KEEP) s.infLog.remove(0);
        return rec;
    }
}
