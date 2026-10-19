package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Una regla de bendicion: "cuando OCURRE <disparador> y se cumplen <condiciones>, hace <efecto>".
 * Las reglas se escriben como texto en el catalogo (tools/blessings/catalog.py -> BlessData.java) y se compilan una sola vez al iniciar:
 *
 *     DISPARADOR | condicion,condicion | EFECTO:arg,arg,arg | opcion=valor opcion=valor
 *
 * El lenguaje completo (disparadores, condiciones, efectos y opciones) esta descrito en docs/BENDICIONES.md y en las constantes de esta clase.
 * Esta clase solo contiene datos ya compilados; la logica que los ejecuta vive en BlessFx.
 */
final class BRule {
    // ---- disparadores
    static final int T_HIT = 0, T_CRIT = 1, T_FINISH = 2, T_STREAK = 3, T_KILL = 4, T_HURT = 5, T_BLOCKED = 6, T_PARRY = 7, T_DODGE = 8, T_ROLL = 9, T_ROLLEND = 10,
            T_SKILL = 11, T_ULT = 12, T_ULTEND = 13, T_DMGS = 14, T_PROJ = 15, T_PROJEND = 16, T_ROOM = 17, T_CLEAR = 18, T_BOSSDEAD = 19, T_PERFECT = 20,
            T_PICK = 21, T_POTION = 22, T_JUMP = 23, T_AIRJUMP = 24, T_LAND = 25, T_LOWHP = 26, T_TICK = 27, T_HAZARD = 28, T_DISCHARGED = 29,
            T_OVERFLOW = 30, T_MOD = 31, T_SPIRIT = 32, T_COUNT = 33;
    static final String[] T_NAME = {"HIT", "CRIT", "FINISH", "STREAK", "KILL", "HURT", "BLOCKED", "PARRY", "DODGE", "ROLL", "ROLLEND",
            "SKILL", "ULT", "ULTEND", "DMGS", "PROJ", "PROJEND", "ROOM", "CLEAR", "BOSSDEAD", "PERFECT",
            "PICK", "POTION", "JUMP", "AIRJUMP", "LAND", "LOWHP", "TICK", "HAZARD", "DISCHARGED",
            "OVERFLOW", "MOD", "SPIRIT"};

    // ---- condiciones (victima = v:, jugador = p:, sala = r:)
    static final int C_V_BURN = 0, C_V_FREEZE = 1, C_V_SLOW = 2, C_V_SHOCK = 3, C_V_POISON = 4, C_V_BLEED = 5, C_V_CURSE = 6, C_V_STUN = 7, C_V_STATUS = 8,
            C_V_MULTI = 9, C_V_LOW = 10, C_V_HIGH = 11, C_V_FULL = 12, C_V_ELITE = 13, C_V_BOSS = 14, C_V_AIR = 15, C_V_BACK = 16, C_V_ALONE = 17,
            C_V_CROWD = 18, C_V_FAR = 19, C_V_STUNNED = 20,
            C_P_LOW = 30, C_P_HIGH = 31, C_P_HALF = 32, C_P_SHIELD = 33, C_P_AIR = 34, C_P_ROLL = 35, C_P_GUARD = 36, C_P_MOVING = 37, C_P_STILL = 38,
            C_P_ARC = 39, C_P_STREAK = 40, C_P_BUFF = 41, C_P_CDALL = 42, C_P_ULT = 43, C_P_NOPOT = 44, C_P_POTFULL = 45, C_P_HPFULL = 46, C_P_NOROOMHIT = 47,
            C_P_COMBO = 48, C_P_GOLD = 49, C_P_SPIRIT = 50, C_P_CRITS = 51, C_P_PARRIES = 52, C_P_KILLS = 53,
            C_R_BOSS = 60, C_R_COMBAT = 61, C_S_W = 70, C_S_S = 71, C_S_P = 72, C_S_DOT = 73, C_S_ANY = 74, C_SYN = 80;
    static final String[] C_NAME = {"v:burn", "v:freeze", "v:slow", "v:shock", "v:poison", "v:bleed", "v:curse", "v:stun", "v:status", "v:multi", "v:low", "v:high", "v:full",
            "v:elite", "v:boss", "v:air", "v:back", "v:alone", "v:crowd", "v:far", "v:stunned"};

    // ---- efectos
    static final int E_STATUS = 0, E_SPREAD = 1, E_EXPLODE = 2, E_CHAIN = 3, E_NEXTHIT = 4, E_NEXTSKILL = 5, E_BUFF = 6, E_HEAL = 7, E_SHIELD = 8, E_CDR = 9,
            E_ULT = 10, E_ULTPCT = 11, E_PROJ = 12, E_GOLD = 13, E_SOULS = 14, E_ARC = 15, E_DISCHARGE = 16, E_INVULN = 17, E_PUSH = 18, E_PULL = 19, E_TRAIL = 20,
            E_POTION = 21, E_LOSEHP = 22, E_LOSEGOLD = 23, E_TIMESLOW = 24, E_CLEANSE = 25, E_MARKTOP = 26, E_REPEAT = 27, E_CDRPCT = 28, E_HEARTDROP = 29,
            E_SPIRIT_BOLT = 30, E_SPIRIT_NOVA = 31, E_SPIRIT_CHAIN = 32, E_SPIRIT_MARK = 33, E_SPIRIT_HEAL = 34, E_SPIRIT_GUARD = 35, E_SPIRIT_WISP = 36,
            E_COOLDOWNALL = 37, E_BURSTUP = 38, E_STRIKE = 39,
            // modificadores pasivos (disparador MOD)
            M_DMG = 60, M_CRIT = 61, M_CRITMUL = 62, M_TAKEN = 63, M_SPEED = 64, M_ATKSPD = 65, M_SKILLDMG = 66, M_CDMUL = 67, M_MAXHP = 68, M_HEALMUL = 69,
            M_GOLDMUL = 70, M_SOULMUL = 71, M_ENEMYDMG = 72, M_REACH = 73, M_PIERCE = 74, M_PROJSPEED = 75, M_PROJSIZE = 76, M_HOMING = 77, M_BOUNCE = 78,
            M_PIERCEDMG = 79, M_CHAINJUMPS = 80, M_SPIRITRATE = 81, M_SHOPDISC = 82, M_LUCK = 83, M_OFFER = 84, M_ULTGAIN = 85, M_POTMAX = 86, M_LIFESTEAL = 87,
            M_PCRIT = 88, M_DOT = 89, M_STATUSDUR = 90, M_SHIELDCAP = 91, M_PROJDMG = 92, M_ENEMYHP = 93, M_REWARD = 94, M_PSTATUS = 95, M_FOCUS = 96,
            M_FINISHMUL = 97, M_ROLLCDR = 98, M_NONCRIT = 99, M_EXTRAPOTION = 100, M_PROJDOUBLE = 101, M_WAVEDMG = 102;

    static final String[] ST_NAME = {"burn", "freeze", "slow", "poison", "shock", "bleed", "root", "stun", "curse"};   // = indices Ent.*
    static final String[] CH_NAME = {"dmg", "spd", "atk", "crit", "taken", "skill", "cdr", "magnet", "life"};
    static final int CH_DMG = 0, CH_SPD = 1, CH_ATK = 2, CH_CRIT = 3, CH_TAKEN = 4, CH_SKILL = 5, CH_CDR = 6, CH_MAGNET = 7, CH_LIFE = 8, CH_COUNT = 9;
    static final String[] PK_NAME = {"wave", "shard", "orb", "blade", "rain", "ring", "star", "holy"};
    static final int PK_WAVE = 0, PK_SHARD = 1, PK_ORB = 2, PK_BLADE = 3, PK_RAIN = 4, PK_RING = 5, PK_STAR = 6, PK_HOLY = 7;
    static final String[] TR_NAME = {"fire", "frost", "poison", "shadow", "holy"};

    // ---- datos compilados
    int trig;
    int[] cond = new int[0];
    float[] cval = new float[0];
    boolean[] neg = new boolean[0];
    int eff;
    float[] a = new float[6];
    float icd, ch, aoe;
    int na;                     // cantidad de argumentos del efecto realmente escritos
    int n = 1;                  // STREAK: cada n golpes; TICK: cada n segundos (float en every)
    float every;
    int k = -1;                 // habilidad concreta (0..2) para SKILL
    int what = -1;              // PICK: 0 oro, 1 alma, 2 corazon, 3 pocion
    int src;                    // 0 cualquiera, o BlessFx.SRC_*
    boolean scale;              // la magnitud a[0] se multiplica por el nivel de la bendicion
    int syn = -1;               // regla de sinergia: solo activa si esa sinergia esta activa
    int owner = -1;             // id de la bendicion duena (-1 = sinergia)
    int idx;                    // indice global (para tiempos de reutilizacion)
    String text;

    static int stIndex(String s) { for (int i = 0; i < ST_NAME.length; i++) if (ST_NAME[i].equals(s)) return i; throw new IllegalArgumentException("estado " + s); }
    static int chIndex(String s) { for (int i = 0; i < CH_NAME.length; i++) if (CH_NAME[i].equals(s)) return i; throw new IllegalArgumentException("canal " + s); }
    static int pkIndex(String s) { for (int i = 0; i < PK_NAME.length; i++) if (PK_NAME[i].equals(s)) return i; throw new IllegalArgumentException("proyectil " + s); }
    static int trIndex(String s) { for (int i = 0; i < TR_NAME.length; i++) if (TR_NAME[i].equals(s)) return i; throw new IllegalArgumentException("rastro " + s); }
    static int tIndex(String s) { for (int i = 0; i < T_NAME.length; i++) if (T_NAME[i].equals(s)) return i; throw new IllegalArgumentException("disparador " + s); }

    private static final String[] EFF_NAME = new String[128];
    static {
        String[][] m = {{"STATUS", "0"}, {"SPREAD", "1"}, {"EXPLODE", "2"}, {"CHAIN", "3"}, {"NEXTHIT", "4"}, {"NEXTSKILL", "5"}, {"BUFF", "6"}, {"HEAL", "7"}, {"SHIELD", "8"}, {"CDR", "9"},
                {"ULT", "10"}, {"ULTPCT", "11"}, {"PROJ", "12"}, {"GOLD", "13"}, {"SOULS", "14"}, {"ARC", "15"}, {"DISCHARGE", "16"}, {"INVULN", "17"}, {"PUSH", "18"}, {"PULL", "19"},
                {"TRAIL", "20"}, {"POTION", "21"}, {"LOSEHP", "22"}, {"LOSEGOLD", "23"}, {"TIMESLOW", "24"}, {"CLEANSE", "25"}, {"MARKTOP", "26"}, {"REPEAT", "27"}, {"CDRPCT", "28"},
                {"HEARTDROP", "29"}, {"BOLT", "30"}, {"NOVA", "31"}, {"SCHAIN", "32"}, {"SMARK", "33"}, {"SHEAL", "34"}, {"SGUARD", "35"}, {"WISP", "36"}, {"COOLDOWNALL", "37"},
                {"BURSTUP", "38"}, {"STRIKE", "39"},
                {"DMG", "60"}, {"CRIT", "61"}, {"CRITMUL", "62"}, {"TAKEN", "63"}, {"SPEED", "64"}, {"ATKSPD", "65"}, {"SKILLDMG", "66"}, {"CDMUL", "67"}, {"MAXHP", "68"}, {"HEALMUL", "69"},
                {"GOLDMUL", "70"}, {"SOULMUL", "71"}, {"ENEMYDMG", "72"}, {"REACH", "73"}, {"PIERCE", "74"}, {"PROJSPEED", "75"}, {"PROJSIZE", "76"}, {"HOMING", "77"}, {"BOUNCE", "78"},
                {"PIERCEDMG", "79"}, {"CHAINJUMPS", "80"}, {"SPIRITRATE", "81"}, {"SHOPDISC", "82"}, {"LUCK", "83"}, {"OFFER", "84"}, {"ULTGAIN", "85"}, {"POTMAX", "86"}, {"LIFESTEAL", "87"},
                {"PCRIT", "88"}, {"DOT", "89"}, {"STATUSDUR", "90"}, {"SHIELDCAP", "91"}, {"PROJDMG", "92"}, {"ENEMYHP", "93"}, {"REWARD", "94"}, {"PSTATUS", "95"}, {"FOCUS", "96"},
                {"FINISHMUL", "97"}, {"ROLLCDR", "98"}, {"NONCRIT", "99"}, {"EXTRAPOTION", "100"}, {"PROJDOUBLE", "101"}, {"WAVEDMG", "102"}};
        for (String[] e : m) EFF_NAME[Integer.parseInt(e[1])] = e[0];
    }
    static int eIndex(String s) { for (int i = 0; i < EFF_NAME.length; i++) if (s.equals(EFF_NAME[i])) return i; throw new IllegalArgumentException("efecto " + s); }
    static String eName(int e) { return EFF_NAME[e]; }

    /** Compila una regla desde su texto. Lanza IllegalArgumentException con el texto original si algo no existe (lo comprueba la prueba del catalogo). */
    static BRule parse(String s, int owner) {
        try {
            String[] f = s.split("\\|", -1);
            if (f.length < 3) throw new IllegalArgumentException("faltan campos");
            BRule r = new BRule();
            r.text = s; r.owner = owner;
            String t = f[0].trim();
            r.trig = tIndex(t);
            List<Integer> cc = new ArrayList<>(); List<Float> cv = new ArrayList<>(); List<Boolean> cn = new ArrayList<>();
            String cs = f[1].trim();
            if (!cs.isEmpty() && !cs.equals("-")) for (String c : cs.split(",")) parseCond(c.trim(), cc, cv, cn);
            r.cond = new int[cc.size()]; r.cval = new float[cc.size()]; r.neg = new boolean[cc.size()];
            for (int i = 0; i < cc.size(); i++) { r.cond[i] = cc.get(i); r.cval[i] = cv.get(i); r.neg[i] = cn.get(i); }
            String es = f[2].trim();
            String en = es, args = "";
            int ci = es.indexOf(':');
            if (ci >= 0) { en = es.substring(0, ci); args = es.substring(ci + 1); }
            r.eff = eIndex(en.trim());
            if (!args.isEmpty()) {
                String[] ar = args.split(",");
                r.na = Math.min(6, ar.length);
                for (int i = 0; i < ar.length && i < 6; i++) r.a[i] = parseArg(r.eff, i, ar[i].trim());
            }
            if (f.length > 3) for (String o : f[3].trim().split("\\s+")) {
                if (o.isEmpty()) continue;
                int q = o.indexOf('=');
                String key = q < 0 ? o : o.substring(0, q), val = q < 0 ? "1" : o.substring(q + 1);
                switch (key) {
                    case "icd": r.icd = Float.parseFloat(val); break;
                    case "ch": r.ch = Float.parseFloat(val); break;
                    case "n": r.n = Integer.parseInt(val); break;
                    case "every": r.every = Float.parseFloat(val); break;
                    case "k": r.k = Integer.parseInt(val); break;
                    case "aoe": r.aoe = Float.parseFloat(val); break;
                    case "what": r.what = val.equals("gold") ? 0 : val.equals("soul") ? 1 : val.equals("heart") ? 2 : val.equals("potion") ? 3 : -1; if (r.what < 0) throw new IllegalArgumentException("what=" + val); break;
                    case "src": r.src = val.equals("W") ? BlessFx.SRC_W : val.equals("S") ? BlessFx.SRC_S : val.equals("P") ? BlessFx.SRC_P : val.equals("DOT") ? BlessFx.SRC_DOT : val.equals("any") ? 0 : -9; if (r.src == -9) throw new IllegalArgumentException("src=" + val); break;
                    case "scale": r.scale = true; break;
                    default: throw new IllegalArgumentException("opcion " + key);
                }
            }
            if (r.trig == T_TICK && r.every <= 0) throw new IllegalArgumentException("TICK sin every");
            return r;
        } catch (RuntimeException ex) {
            throw new IllegalArgumentException("regla invalida [" + s + "]: " + ex.getMessage());
        }
    }

    private static float parseArg(int eff, int i, String t) {
        if (i == 0 && (eff == E_STATUS || eff == E_SPREAD)) return stIndex(t);
        if (i == 0 && eff == E_BUFF) return chIndex(t);
        if (i == 0 && eff == E_PROJ) return pkIndex(t);
        if (i == 0 && eff == E_TRAIL) return trIndex(t);
        if (i == 2 && eff == E_EXPLODE && !t.matches("-?[0-9.]+")) return stIndex(t);
        if (i == 2 && eff == E_PROJ && !t.matches("-?[0-9.]+")) return stIndex(t);
        if (i == 3 && eff == E_PROJ && !t.matches("-?[0-9.]+")) return stIndex(t);
        if (i == 2 && eff == E_SPIRIT_WISP && !t.matches("-?[0-9.]+")) return stIndex(t);
        if (eff == E_EXPLODE && i == 2) return stIndex(t);
        return Float.parseFloat(t);
    }

    private static void parseCond(String c, List<Integer> cc, List<Float> cv, List<Boolean> cn) {
        boolean ng = c.startsWith("!");
        if (ng) c = c.substring(1);
        float val = 0; int code = -1;
        for (int i = 0; i < C_NAME.length; i++) if (C_NAME[i].equals(c)) code = i;
        if (code < 0) {
            switch (c) {
                case "p:low": code = C_P_LOW; break;
                case "p:high": code = C_P_HIGH; break;
                case "p:half": code = C_P_HALF; break;
                case "p:shield": code = C_P_SHIELD; break;
                case "p:air": code = C_P_AIR; break;
                case "p:roll": code = C_P_ROLL; break;
                case "p:guard": code = C_P_GUARD; break;
                case "p:moving": code = C_P_MOVING; break;
                case "p:still": code = C_P_STILL; break;
                case "p:cdall": code = C_P_CDALL; break;
                case "p:ult": code = C_P_ULT; break;
                case "p:nopot": code = C_P_NOPOT; break;
                case "p:potfull": code = C_P_POTFULL; break;
                case "p:hpfull": code = C_P_HPFULL; break;
                case "p:noroomhit": code = C_P_NOROOMHIT; break;
                case "p:spirit": code = C_P_SPIRIT; break;
                case "r:boss": code = C_R_BOSS; break;
                case "r:combat": code = C_R_COMBAT; break;
                case "s:W": code = C_S_W; break;
                case "s:S": code = C_S_S; break;
                case "s:P": code = C_S_P; break;
                case "s:DOT": code = C_S_DOT; break;
                default:
                    if (c.startsWith("p:arc>=")) { code = C_P_ARC; val = Float.parseFloat(c.substring(7)); }
                    else if (c.startsWith("p:streak>=")) { code = C_P_STREAK; val = Float.parseFloat(c.substring(10)); }
                    else if (c.startsWith("p:combo>=")) { code = C_P_COMBO; val = Float.parseFloat(c.substring(9)); }
                    else if (c.startsWith("p:buff.")) { code = C_P_BUFF; val = chIndex(c.substring(7)); }
                    else if (c.startsWith("p:gold>=")) { code = C_P_GOLD; val = Float.parseFloat(c.substring(8)); }
                    else if (c.startsWith("p:crits>=")) { code = C_P_CRITS; val = Float.parseFloat(c.substring(9)); }
                    else if (c.startsWith("p:parries>=")) { code = C_P_PARRIES; val = Float.parseFloat(c.substring(11)); }
                    else if (c.startsWith("p:kills>=")) { code = C_P_KILLS; val = Float.parseFloat(c.substring(9)); }
                    else if (c.startsWith("v:multi>=")) { code = C_V_MULTI; val = Float.parseFloat(c.substring(9)); }
                    else if (c.startsWith("syn:")) { code = C_SYN; val = Float.parseFloat(c.substring(4)); }
                    else throw new IllegalArgumentException("condicion " + c);
            }
        }
        if (code == C_V_MULTI && val == 0) val = 2;
        cc.add(code); cv.add(val); cn.add(ng);
    }
}
