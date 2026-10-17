package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Progreso permanente (Santuario) y opciones. Se guarda como JSON en Platform.Store. */
public final class Save {
    public static Save S = new Save();
    /** Modo Desarrollador: si >= 0, las almas actuales son TEMPORALES y en disco se guarda este valor (el perfil real no cambia). */
    public static int devSoulsBackup = -1;
    /** Oro inicial de la arena/tienda de prueba del Modo Desarrollador (no existe en partidas normales). */
    public static int devGold = 5000;

    /** Devuelve las almas reales del perfil (descarta el saldo de prueba). */
    public static void devRevert() { if (devSoulsBackup >= 0) { S.souls = devSoulsBackup; devSoulsBackup = -1; } }
    /** Convierte el saldo de prueba en saldo real del perfil. */
    public static void devCommit() { devSoulsBackup = -1; S.write(); }
    static Platform P;
    /** Version del formato de guardado. 1 = original (sin campo "ver"); 2 = gemas, inventario, modo infinito. Solo se AÑADEN claves: nunca se borran ni se renombran. */
    public static final int VERSION = 2;
    /** true si el guardado en disco es de una version MAS NUEVA que esta app: no se sobrescribe (se conserva intacto). */
    public boolean readOnly = false;
    /** Gemas de prueba del Modo Desarrollador: solo existen en memoria durante la sesion, jamas se guardan. */
    public static int devGems = 0;

    public int souls = 0;
    public int totalSouls = 0;
    public boolean[] classUnlocked = new boolean[10];
    public int[] meta = new int[Meta.COUNT];
    public boolean[] relics = new boolean[8];       // reliquias de jefe conseguidas
    public boolean finalBeaten = false;
    public int runs = 0, wins = 0, kills = 0, bestRooms = 0, bossKills = 0;
    public int[] classWins = new int[10];
    public int ascension = 0;                        // nivel de dificultad desbloqueado
    public int ascensionSel = 0;
    public boolean musicOn = true, sfxOn = true, vibOn = true;
    public boolean tutorialDone = false;
    public int lastClass = 0;
    public int diffSel = 1;                          // 0 facil, 1 normal, 2 dificil
    public boolean[] unlocked = new boolean[Unlocks.COUNT];   // desbloqueos por enemigos derrotados
    public int[] story = new int[8];                 // progreso narrativo (ver Story)
    public boolean devUnlocked = false;              // Modo Desarrollador (se activa con un codigo)
    // ---- estadisticas de la cuenta (persistentes)
    public int started = 0, rounds = 0, losses = 0, bestStreak = 0, maxKillsRound = 0, perfectRounds = 0, bestPerfectStreak = 0, chestsOpened = 0, secretChests = 0, trophyMask = 0;
    public int[] classRuns = new int[10];
    public int[] events = new int[Events.COUNT];     // sucesos especiales completados (por tipo)
    public long playMs = 0;                          // tiempo total jugado (ms)
    // ---- moneda premium (independiente de almas/oro) e inventario cosmetico
    public int gems = 0;                             // saldo premium (solo via Wallet)
    public final List<String> gemTx = new ArrayList<>();   // ids de transacciones ya acreditadas (anti-duplicado)
    public final List<String> owned = new ArrayList<>();   // ids de articulos cosmeticos poseidos
    public final String[] equip = new String[10];    // skin equipada por espadachin ("" = aspecto original)
    // ---- modo infinito (registro local de resultados)
    public int infRuns = 0, infBestFloor = 0, infBestScore = 0, infFloors = 0, infKills = 0, infBosses = 0, infBestTimeS = 0;
    public final List<String> infLog = new ArrayList<>();  // ultimos resultados (JSON compacto por entrada)
    public int[] codesUsed = new int[16];            // codigos de un solo uso ya canjeados (indice en Codes.ALL)
    public int[] eqSec = {0};                        // (reservado)
    public int inputMode = 0;                        // 0 automatico, 1 tactil, 2 mando
    public int[] kb = Input.defaultKeys();           // tecla de teclado por accion (0 = sin asignar)
    public int[] pb = Input.defaultPad();            // boton de mando por accion (codigo virtual de Pad, 0 = sin asignar)
    public float[] ctl = new float[Input.B_COUNT * 3]; // dx, dy, escala por boton (0 = por defecto)

    public Save() {
        java.util.Arrays.fill(equip, "");
        classUnlocked[0] = true; // paladin
        classUnlocked[1] = true; // shadow
        classUnlocked[2] = true; // flame
    }

    public int relicCount() { int n = 0; for (boolean b : relics) if (b) n++; return n; }
    public boolean sealForged() { return relicCount() >= 8; }

    public static void load(Platform p) {
        P = p;
        Save s = new Save();
        try {
            String raw = p.store().get("save", "");
            Map<String, Object> d = Json.parseObj(raw);
            if (d != null) {
                int ver = Json.i(d, "ver", 1);
                if (ver > VERSION) {                      // guardado de una app mas nueva: no lo tocamos
                    s.readOnly = true;
                    if (p.store().get("save_bak_v" + ver, "").isEmpty()) { p.store().put("save_bak_v" + ver, raw); p.store().commit(); }
                } else if (ver < VERSION && p.store().get("save_bak_v" + ver, "").isEmpty()) {   // copia de seguridad antes de migrar
                    p.store().put("save_bak_v" + ver, raw); p.store().commit();
                }
                s.gems = Math.max(0, Json.i(d, "gems", 0));
                for (Object o : arrOf(d, "gemTx")) if (o instanceof String) s.gemTx.add((String) o);
                for (Object o : arrOf(d, "owned")) if (o instanceof String && !s.owned.contains(o)) s.owned.add((String) o);
                String[] eq = Json.str(d, "equip", "").split("\\|", -1);
                for (int i = 0; i < Math.min(eq.length, s.equip.length); i++) s.equip[i] = eq[i];
                s.infRuns = Json.i(d, "inf_runs", 0); s.infBestFloor = Json.i(d, "inf_bestFloor", 0); s.infBestScore = Json.i(d, "inf_bestScore", 0);
                s.infFloors = Json.i(d, "inf_floors", 0); s.infKills = Json.i(d, "inf_kills", 0); s.infBosses = Json.i(d, "inf_bosses", 0);
                s.infBestTimeS = Json.i(d, "inf_bestTime", 0);
                for (Object o : arrOf(d, "inf_log")) if (o instanceof String) s.infLog.add((String) o);
                s.souls = Json.i(d, "souls", 0);
                s.totalSouls = Json.i(d, "totalSouls", 0);
                int[] cu = Json.ints(d, "cu");
                if (cu != null) for (int i = 0; i < Math.min(10, cu.length); i++) s.classUnlocked[i] = cu[i] != 0;
                int[] mt = Json.ints(d, "meta");
                if (mt != null) for (int i = 0; i < Math.min(Meta.COUNT, mt.length); i++) s.meta[i] = mt[i];
                int[] rl = Json.ints(d, "relics");
                if (rl != null) for (int i = 0; i < Math.min(8, rl.length); i++) s.relics[i] = rl[i] != 0;
                s.finalBeaten = Json.bool(d, "finalBeaten", false);
                s.runs = Json.i(d, "runs", 0); s.wins = Json.i(d, "wins", 0); s.kills = Json.i(d, "kills", 0);
                s.bestRooms = Json.i(d, "bestRooms", 0); s.bossKills = Json.i(d, "bossKills", 0);
                int[] cw = Json.ints(d, "cw");
                if (cw != null) for (int i = 0; i < Math.min(10, cw.length); i++) s.classWins[i] = cw[i];
                s.ascension = Json.i(d, "asc", 0); s.ascensionSel = Json.i(d, "ascSel", 0);
                s.musicOn = Json.bool(d, "music", true); s.sfxOn = Json.bool(d, "sfx", true); s.vibOn = Json.bool(d, "vib", true);
                s.tutorialDone = Json.bool(d, "tut", false);
                s.lastClass = Json.i(d, "last", 0);
                s.diffSel = Math.max(0, Math.min(2, Json.i(d, "diff", 1)));
                int[] un = Json.ints(d, "unl");
                if (un != null) for (int i = 0; i < Math.min(Unlocks.COUNT, un.length); i++) s.unlocked[i] = un[i] != 0;
                s.devUnlocked = Json.bool(d, "dev", false);
                s.started = Json.i(d, "st_started", 0); s.rounds = Json.i(d, "st_rounds", 0); s.losses = Json.i(d, "st_losses", 0);
                s.bestStreak = Json.i(d, "st_streak", 0); s.maxKillsRound = Json.i(d, "st_killsRound", 0); s.perfectRounds = Json.i(d, "st_perfect", 0);
                s.bestPerfectStreak = Json.i(d, "st_perfStreak", 0); s.chestsOpened = Json.i(d, "st_chests", 0); s.secretChests = Json.i(d, "st_secret", 0);
                s.trophyMask = Json.i(d, "st_trophies", 0); s.playMs = Json.i(d, "st_playS", 0) * 1000L;
                int[] cru = Json.ints(d, "st_classRuns");
                if (cru != null) for (int i = 0; i < Math.min(10, cru.length); i++) s.classRuns[i] = cru[i];
                int[] evs = Json.ints(d, "st_events");
                if (evs != null) for (int i = 0; i < Math.min(Events.COUNT, evs.length); i++) s.events[i] = Math.max(0, evs[i]);
                int[] cdu = Json.ints(d, "codes");
                if (cdu != null) for (int i = 0; i < Math.min(s.codesUsed.length, cdu.length); i++) s.codesUsed[i] = cdu[i];
                int[] sty = Json.ints(d, "story");
                if (sty != null) for (int i = 0; i < Math.min(s.story.length, sty.length); i++) s.story[i] = sty[i];
                s.inputMode = Math.max(0, Math.min(2, Json.i(d, "imode", 0)));
                int[] kk = Json.ints(d, "kb");
                if (kk != null) for (int i = 0; i < Math.min(s.kb.length, kk.length); i++) s.kb[i] = kk[i];
                int[] pp = Json.ints(d, "pb");
                if (pp != null) for (int i = 0; i < Math.min(s.pb.length, pp.length); i++) s.pb[i] = pp[i];
                int[] cl = Json.ints(d, "ctl");
                if (cl != null) for (int i = 0; i < Math.min(s.ctl.length, cl.length); i++) s.ctl[i] = cl[i] / 10f;
            }
        } catch (RuntimeException e) {
            p.log("save load error " + e);
        }
        if (!s.devUnlocked && !s.readOnly) {          // nada de pruebas sobrevive sin el Modo Desarrollador
            s.owned.removeIf(id -> id.startsWith("dev_"));
            for (int i = 0; i < s.equip.length; i++) if (s.equip[i] != null && s.equip[i].startsWith("dev_")) s.equip[i] = "";
        }
        S = s;
    }

    public void write() { write(true); }

    /** commit=false deja los datos en el almacen sin vaciarlos al disco (para escribir varias claves de forma atomica: el que llama hace commit). */
    public void write(boolean commit) {
        if (P == null || readOnly) return;
        try {
            Map<String, Object> d = new LinkedHashMap<>();
            d.put("ver", VERSION);
            d.put("gems", gems); d.put("gemTx", new ArrayList<Object>(gemTx)); d.put("owned", new ArrayList<Object>(owned));
            StringBuilder eqs = new StringBuilder();
            for (int i = 0; i < equip.length; i++) { if (i > 0) eqs.append('|'); eqs.append(equip[i] == null ? "" : equip[i]); }
            d.put("equip", eqs.toString());
            d.put("inf_runs", infRuns); d.put("inf_bestFloor", infBestFloor); d.put("inf_bestScore", infBestScore); d.put("inf_floors", infFloors);
            d.put("inf_kills", infKills); d.put("inf_bosses", infBosses); d.put("inf_bestTime", infBestTimeS); d.put("inf_log", new ArrayList<Object>(infLog));
            d.put("souls", devSoulsBackup >= 0 ? devSoulsBackup : souls); d.put("totalSouls", totalSouls);
            int[] cu = new int[10]; for (int i = 0; i < 10; i++) cu[i] = classUnlocked[i] ? 1 : 0;
            d.put("cu", cu); d.put("meta", meta);
            int[] rl = new int[8]; for (int i = 0; i < 8; i++) rl[i] = relics[i] ? 1 : 0;
            d.put("relics", rl);
            d.put("finalBeaten", finalBeaten);
            d.put("runs", runs); d.put("wins", wins); d.put("kills", kills); d.put("bestRooms", bestRooms); d.put("bossKills", bossKills);
            d.put("cw", classWins);
            d.put("asc", ascension); d.put("ascSel", ascensionSel);
            d.put("music", musicOn); d.put("sfx", sfxOn); d.put("vib", vibOn); d.put("tut", tutorialDone); d.put("last", lastClass); d.put("diff", diffSel);
            int[] un = new int[Unlocks.COUNT]; for (int i = 0; i < un.length; i++) un[i] = unlocked[i] ? 1 : 0;
            d.put("unl", un);
            int[] cl = new int[ctl.length]; for (int i = 0; i < cl.length; i++) cl[i] = Math.round(ctl[i] * 10f);
            d.put("ctl", cl);
            d.put("story", story);
            d.put("dev", devUnlocked); d.put("codes", codesUsed);
            d.put("st_started", started); d.put("st_rounds", rounds); d.put("st_losses", losses); d.put("st_streak", bestStreak); d.put("st_killsRound", maxKillsRound);
            d.put("st_perfect", perfectRounds); d.put("st_perfStreak", bestPerfectStreak); d.put("st_chests", chestsOpened); d.put("st_secret", secretChests);
            d.put("st_trophies", trophyMask); d.put("st_playS", (int) (playMs / 1000L)); d.put("st_classRuns", classRuns); d.put("st_events", events);
            d.put("imode", inputMode); d.put("kb", kb); d.put("pb", pb);
            P.store().put("save", Json.write(d));
            if (commit) P.store().commit();
        } catch (RuntimeException e) {
            P.log("save error " + e);
        }
    }

    public void reset() {
        Save n = new Save();
        n.musicOn = musicOn; n.sfxOn = sfxOn; n.vibOn = vibOn; n.ctl = ctl; n.kb = kb; n.pb = pb; n.inputMode = inputMode;
        n.story[Story.S_INTRO] = story[Story.S_INTRO];
        n.devUnlocked = devUnlocked; n.codesUsed = codesUsed;
        // la moneda premium, lo comprado y los registros competitivos NO se borran al reiniciar el progreso del juego
        n.gems = gems; n.gemTx.addAll(gemTx); n.owned.addAll(owned); System.arraycopy(equip, 0, n.equip, 0, equip.length);
        n.infRuns = infRuns; n.infBestFloor = infBestFloor; n.infBestScore = infBestScore; n.infFloors = infFloors; n.infKills = infKills;
        n.infBosses = infBosses; n.infBestTimeS = infBestTimeS; n.infLog.addAll(infLog);
        S = n;
        n.write();
    }

    static List<Object> arrOf(Map<String, Object> d, String k) { List<Object> l = Json.arr(d, k); return l == null ? new ArrayList<>() : l; }

    static List<Object> list(int[] a) { List<Object> l = new ArrayList<>(); for (int v : a) l.add((double) v); return l; }
}
