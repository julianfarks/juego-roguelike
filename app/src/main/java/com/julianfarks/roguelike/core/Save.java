package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Progreso permanente (Santuario) y opciones. Se guarda como JSON en Platform.Store. */
public final class Save {
    public static Save S = new Save();
    static Platform P;

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
    public int[] eqSec = {0};                        // (reservado)
    public float[] ctl = new float[Input.B_COUNT * 3]; // dx, dy, escala por boton (0 = por defecto)

    public Save() {
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
            Map<String, Object> d = Json.parseObj(p.store().get("save", ""));
            if (d != null) {
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
                int[] cl = Json.ints(d, "ctl");
                if (cl != null) for (int i = 0; i < Math.min(s.ctl.length, cl.length); i++) s.ctl[i] = cl[i] / 10f;
            }
        } catch (RuntimeException e) {
            p.log("save load error " + e);
        }
        S = s;
    }

    public void write() {
        if (P == null) return;
        try {
            Map<String, Object> d = new LinkedHashMap<>();
            d.put("souls", souls); d.put("totalSouls", totalSouls);
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
            P.store().put("save", Json.write(d));
            P.store().commit();
        } catch (RuntimeException e) {
            P.log("save error " + e);
        }
    }

    public void reset() {
        Save n = new Save();
        n.musicOn = musicOn; n.sfxOn = sfxOn; n.vibOn = vibOn; n.ctl = ctl;
        S = n;
        n.write();
    }

    static List<Object> list(int[] a) { List<Object> l = new ArrayList<>(); for (int v : a) l.add((double) v); return l; }
}
