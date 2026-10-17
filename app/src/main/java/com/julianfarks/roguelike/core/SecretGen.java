package com.julianfarks.roguelike.core;

import java.util.*;

/**
 * Generador de camaras secretas: elige entrada, reto y recompensa, construye la geometria y comprueba (RoomCheck) que
 * la entrada, los mecanismos y la recompensa son alcanzables y que la ruta principal sigue libre. Si algo falla se
 * prueba una entrada mas sencilla; si nada vale, la sala se queda sin camara (nunca una camara imposible).
 */
final class SecretGen {
    private SecretGen() {}

    /** Solo banco de pruebas: fuerza entrada / recompensa / reto (-1 = al azar). */
    static final boolean DBG = System.getenv("SECRET_DBG") != null;
    static String why = "";
    private static int startG;
    static int dbgEntrance = -1, dbgReward = -1, dbgChallenge = -1, dbgFamily = -1;
    static {   // BOT_SECRET="familia:entrada:recompensa:reto" (-1 = al azar); solo banco de pruebas
        try {
            String v = System.getenv("BOT_SECRET");
            if (v != null) { String[] a = v.split(":"); dbgFamily = Integer.parseInt(a[0]); dbgEntrance = Integer.parseInt(a[1]); dbgReward = Integer.parseInt(a[2]); dbgChallenge = Integer.parseInt(a[3]); }
        } catch (RuntimeException e) { /* ignorar */ }
    }

    static Secret build(Room rm, int W, int fy, int mf, int[] ground, boolean[] blocked, boolean[] slab, Rng r, int stage, int family) {
        if (dbgFamily >= 0) family = dbgFamily;
        List<Integer> tries = new ArrayList<>();
        int e = dbgEntrance >= 0 ? dbgEntrance : rollEntrance(family, r, rm.biome.key);
        tries.add(e);
        if (dbgEntrance < 0) tries.add(family == 0 ? Secret.E_FLOOR : Secret.E_WALL);
        startG = fy;
        Set<Integer> base = RoomCheck.reach(rm, 4, fy);
        byte[] bt = rm.t.clone();
        boolean[] bv = rm.vista.clone();
        for (int ent : tries) {
            for (int att = 0; att < 14; att++) {
                Secret s = new Secret();
                s.family = family; s.entrance = ent;
                s.challenge = dbgChallenge >= 0 ? dbgChallenge : rollChallenge(family, ent, r);
                if (family == 0 && s.challenge == Secret.C_PLAT && ent == Secret.E_ILLUSION) s.challenge = Secret.C_NONE;
                boolean mech = ent >= Secret.E_LEVER;
                s.tier = Math.min(2, (mech ? 1 : 0) + (s.challenge != Secret.C_NONE ? 1 : 0));
                s.reward = dbgReward >= 0 ? dbgReward : rollReward(s.tier, r);
                boolean ok = family == 0 ? geomFloor(rm, s, W, fy, ground, blocked, r) : geomVault(rm, s, W, fy, mf, slab, r);
                why = "geom";
                if (ok) { ok = fixtures(rm, s, W, fy, mf, r); why = "fixtures"; }
                if (ok) { ok = check(rm, s, base); why = "check"; }
                if (DBG && !ok) System.out.println("secretgen fail fam=" + family + " ent=" + ent + " stage=" + why);
                if (ok) { place(rm, s, W); rm.secrets.add(s); return s; }
                System.arraycopy(bt, 0, rm.t, 0, bt.length);
                System.arraycopy(bv, 0, rm.vista, 0, bv.length);
                rm.props.removeIf(p -> p.arg >= 3 && (p.kind.equals("chest") || p.kind.equals("relic")) || p.kind.equals("shrine"));
            }
        }
        return null;
    }

    private static int pick(Rng r, int[] w) {
        int t = 0; for (int v : w) t += v;
        int x = r.i(Math.max(1, t));
        for (int i = 0; i < w.length; i++) { x -= w[i]; if (x < 0) return i; }
        return 0;
    }

    /** Entradas coherentes con cada bioma: las cascadas solo donde hay agua, hielo, lava o sangre; las cortinas y estatuas encajan en ruinas y templos. */
    static boolean allowed(int ent, String biome) {
        switch (ent) {
            case Secret.E_WATERFALL: return !(biome.equals("catacumbas") || biome.equals("eclipse") || biome.equals("vacio"));
            case Secret.E_CURTAIN: return !(biome.equals("forja") || biome.equals("tormenta") || biome.equals("helado"));
            default: return true;
        }
    }

    static int rollEntrance(int family, Rng r, String biome) {
        int e = rollEntrance(family, r);
        for (int k = 0; k < 8 && !allowed(e, biome); k++) e = rollEntrance(family, r);
        return allowed(e, biome) ? e : (family == 0 ? Secret.E_FLOOR : Secret.E_WALL);
    }

    static int rollEntrance(int family, Rng r) {
        if (family == 0) {   // bajo el suelo
            int[] w = new int[Secret.E_COUNT];
            w[Secret.E_FLOOR] = 36; w[Secret.E_ILLUSION] = 14; w[Secret.E_LEVER] = 18; w[Secret.E_SYMBOLS] = 14; w[Secret.E_RUNES] = 10; w[Secret.E_SKILL] = 8;
            return pick(r, w);
        }
        int[] w = new int[Secret.E_COUNT];
        w[Secret.E_WALL] = 18; w[Secret.E_ILLUSION] = 16; w[Secret.E_WATERFALL] = 9; w[Secret.E_CURTAIN] = 12; w[Secret.E_STATUE] = 12;
        w[Secret.E_LEVER] = 10; w[Secret.E_SYMBOLS] = 9; w[Secret.E_RUNES] = 7; w[Secret.E_SKILL] = 7;
        return pick(r, w);
    }

    static int rollChallenge(int family, int ent, Rng r) {
        float p = r.f();
        if (family == 0) return p < 0.20f ? Secret.C_PLAT : (p < 0.35f ? Secret.C_GUARD : Secret.C_NONE);
        return p < 0.20f ? Secret.C_GUARD : Secret.C_NONE;
    }

    static int rollReward(int tier, Rng r) {
        int[] w;
        switch (tier) {
            case 0: w = new int[]{58, 0, 0, 14, 0, 28}; break;
            case 1: w = new int[]{0, 38, 20, 16, 20, 6}; break;
            default: w = new int[]{0, 28, 36, 16, 20, 0}; break;
        }
        return pick(r, w);
    }

    // ------------------------------------------------------------------ geometria: camara bajo el suelo
    private static boolean geomFloor(Room rm, Secret s, int W, int fy, int[] ground, boolean[] blocked, Rng r) {
        boolean wide = s.challenge == Secret.C_PLAT;
        int L = wide ? 7 : 3, R = wide ? 8 : 4, span = wide ? 12 : 9;
        int x0 = -1;
        for (int tries = 0; tries < 60 && x0 < 0; tries++) {
            int x = r.range(span + 8, W - span - 12);
            boolean ok = true;
            for (int i = -span; i <= span + 1 && ok; i++) { int xx = x + i; if (xx < 4 || xx >= W - 4 || ground[xx] != fy || blocked[xx] || rm.tile(xx, fy - 1) != Room.AIR || rm.tile(xx, fy - 2) != Room.AIR) ok = false; }
            if (ok) x0 = x;
        }
        if (x0 < 0) return false;
        s.rx0 = x0 - L - 1; s.rx1 = x0 + R + 1; s.ry0 = fy; s.ry1 = fy + 6;
        for (int x = x0 - L; x <= x0 + R; x++) for (int y = fy + 2; y <= fy + 5; y++) { rm.set(x, y, Room.AIR); rm.vista[y * W + x] = false; }
        for (int x = x0 - L - 1; x <= x0 + R + 1; x++) rm.set(x, fy + 6, Room.SOLID);
        int doorT = s.entrance == Secret.E_FLOOR ? Room.BREAK : (s.entrance == Secret.E_ILLUSION ? Room.FAKE : Room.HWALL);
        for (int x = x0; x <= x0 + 1; x++) for (int y = fy; y <= fy + 1; y++) { rm.set(x, y, doorT); s.door.add(new int[]{x, y}); }
        // aterrizaje justo bajo la entrada (con hueco encima para saltar fuera)
        for (int x = x0; x <= x0 + 1; x++) rm.set(x, fy + 3, Room.ONEWAY);
        s.horizontalDoor = true;
        s.cx = (x0 + 1) * Room.TS; s.cy = fy * Room.TS + 8;
        if (wide) {   // seccion de plataformas sobre un suelo de pinchos
            for (int x = x0 - L; x <= x0 + R; x++) rm.set(x, fy + 5, Room.SPIKE);
            for (int x = x0 - 3; x <= x0 - 2; x++) rm.set(x, fy + 4, Room.ONEWAY);
            for (int x = x0 - 7; x <= x0 - 6; x++) rm.set(x, fy + 4, Room.ONEWAY);
            for (int x = x0 + 3; x <= x0 + 4; x++) rm.set(x, fy + 4, Room.ONEWAY);   // rama sin salida (cebo)
            s.rwX = (x0 - 7) * Room.TS + 8; s.rwY = (fy + 4) * Room.TS;
        } else {
            for (int x = x0 + 2; x <= x0 + 4; x++) rm.set(x, fy + 4, Room.ONEWAY);
            s.rwX = (x0 - 2) * Room.TS + 8; s.rwY = (fy + 6) * Room.TS;
        }
        return true;
    }

    // ------------------------------------------------------------------ geometria: camara de piedra sobre el piso superior
    private static boolean geomVault(Room rm, Secret s, int W, int fy, int mf, boolean[] slab, Rng r) {
        int a = -1;
        for (int tries = 0; tries < 60 && a < 0; tries++) {
            int x = r.range(14, W - 26);
            boolean ok = true;
            for (int i = -4; i <= 12 && ok; i++) { int xx = x + i; if (xx < 4 || xx >= W - 4 || !slab[xx] || rm.tile(xx, mf - 1) != Room.AIR || rm.tile(xx, mf - 2) != Room.AIR) ok = false; }
            if (ok) a = x;
        }
        if (a < 0) return false;
        boolean left = r.chance(0.5f);
        s.rx0 = a; s.rx1 = a + 8; s.ry0 = mf - 5; s.ry1 = mf - 1;
        for (int x = a; x <= a + 8; x++) for (int y = mf - 5; y <= mf - 1; y++) { rm.set(x, y, Room.SOLID); rm.vista[y * W + x] = false; }
        for (int x = a + 1; x <= a + 7; x++) for (int y = mf - 3; y <= mf - 1; y++) rm.set(x, y, Room.AIR);
        int bx = left ? a : a + 8;
        int doorT = s.entrance == Secret.E_ILLUSION || s.entrance == Secret.E_WATERFALL || s.entrance == Secret.E_CURTAIN ? Room.FAKE : Room.HWALL;
        for (int y = mf - 2; y <= mf - 1; y++) { rm.set(bx, y, doorT); s.door.add(new int[]{bx, y}); }
        rm.vaultA = a;
        s.cx = bx * Room.TS + 8; s.cy = (mf - 1) * Room.TS;
        s.horizontalDoor = false;
        s.rwX = (a + 4) * Room.TS + 8; s.rwY = mf * Room.TS;
        return true;
    }

    // ------------------------------------------------------------------ mecanismos (palanca, piedras, cristal) y recompensa
    private static boolean fixtures(Room rm, Secret s, int W, int fy, int mf, Rng r) {
        int g = s.family == 0 ? fy : mf;
        Set<Integer> reach = RoomCheck.reach(rm, 4, startG);
        int nSw = s.entrance == Secret.E_LEVER ? 1 : (s.entrance == Secret.E_SYMBOLS || s.entrance == Secret.E_RUNES ? 3 : 0);
        int doorTx = (int) (s.cx / Room.TS);
        if (nSw > 0 || s.entrance == Secret.E_SKILL) {
            List<Integer> cand = new ArrayList<>();
            int lo = s.entrance == Secret.E_LEVER ? 8 : 4, hi = s.entrance == Secret.E_LEVER ? 22 : 14;
            for (int x = doorTx - hi; x <= doorTx + hi; x++) {
                if (Math.abs(x - doorTx) < lo || x < 6 || x >= W - 6) continue;
                if (s.contains(x, g) || s.contains(x - 1, g) || s.contains(x + 1, g)) continue;
                if (!reach.contains(g * 1000 + x) || !RoomCheck.node(rm, x, g)) continue;
                if (rm.tile(x, g - 1) != Room.AIR || rm.tile(x, g - 2) != Room.AIR || rm.tile(x, g - 3) != Room.AIR) continue;
                cand.add(x);
            }
            if (s.entrance == Secret.E_SKILL) {
                List<Integer> near = new ArrayList<>();
                for (int x : cand) if (Math.abs(x - doorTx) <= 7) near.add(x);
                if (near.isEmpty()) return false;
                int x = near.get(r.i(near.size()));
                s.crX = x * Room.TS + 8; s.crY = g * Room.TS;
            } else {
                // piedras separadas entre si (al menos 3 baldosas)
                Collections.shuffle(cand, new Random(r.next()));
                List<Integer> chosen = new ArrayList<>();
                for (int x : cand) { boolean far = true; for (int c : chosen) if (Math.abs(c - x) < 3) far = false; if (far) chosen.add(x); if (chosen.size() == nSw) break; }
                if (chosen.size() < nSw) return false;
                if (nSw > 1) Collections.sort(chosen);
                for (int k = 0; k < nSw; k++) s.sw.add(new float[]{chosen.get(k) * Room.TS + 8, g * Room.TS, k});
                if (nSw == 3) {   // orden correcto: permutacion de los tres simbolos
                    int[] o = {0, 1, 2};
                    for (int i = 2; i > 0; i--) { int j = r.i(i + 1); int t = o[i]; o[i] = o[j]; o[j] = t; }
                    s.order = o;
                }
            }
        }
        // recompensa
        switch (s.reward) {
            case Secret.R_CHEST -> rm.props.add(new Room.PropSpec("chest", s.rwX, s.rwY, 3));
            case Secret.R_RICH -> rm.props.add(new Room.PropSpec("chest", s.rwX, s.rwY, 4));
            case Secret.R_RELIC -> rm.props.add(new Room.PropSpec("relic", s.rwX, s.rwY, 4));
            case Secret.R_SHRINE -> rm.props.add(new Room.PropSpec("shrine", s.rwX, s.rwY, 0));
            default -> { }
        }
        return true;
    }

    /** La entrada, los mecanismos y la recompensa deben ser alcanzables con la camara abierta y la ruta principal no debe depender de ella. */
    private static boolean check(Room rm, Secret s, Set<Integer> base) {
        int sx = 4, sg = startG;
        Set<Integer> closed = RoomCheck.reach(rm, sx, sg);
        for (int n : base) if (!s.contains(n % 1000, n / 1000) && !s.contains(n % 1000, n / 1000 - 1) && !closed.contains(n)) { if (DBG) System.out.println("  chk: ruta principal rota " + n % 1000 + "," + n / 1000); return false; }
        byte[] save = rm.t.clone();
        for (int[] d : s.door) if (rm.tile(d[0], d[1]) != Room.SOLID) rm.set(d[0], d[1], Room.AIR);
        Set<Integer> open = RoomCheck.reach(rm, sx, sg);
        int rgx = (int) (s.rwX / Room.TS), rgy = Math.round(s.rwY / Room.TS);
        boolean ok = true;
        for (int n : base) if (!s.contains(n % 1000, n / 1000) && !s.contains(n % 1000, n / 1000 - 1) && !open.contains(n)) ok = false;
        if (!ok && DBG) System.out.println("  chk: ruta rota con camara abierta");
        boolean prop = s.reward <= Secret.R_RELIC || s.reward == Secret.R_SHRINE;
        if (ok && prop) { ok = open.contains(rgy * 1000 + rgx) && RoomCheck.node(rm, rgx, rgy); if (!ok && DBG) dump(rm, s, open, "recompensa inalcanzable rg=" + rgx + "," + rgy); }
        if (ok) {   // desde dentro hay que poder volver a la sala (no encerrar al jugador)
            Set<Integer> inside = RoomCheck.reach(rm, rgx, rgy);
            boolean out = false;
            for (int n : base) if (!s.contains(n % 1000, n / 1000) && !s.contains(n % 1000, n / 1000 - 1) && inside.contains(n)) { out = true; break; }
            ok = out || !prop;
            if (!ok && DBG) System.out.println("  chk: no se puede volver");
        }
        System.arraycopy(save, 0, rm.t, 0, save.length);
        return ok;
    }

    private static void dump(Room rm, Secret s, Set<Integer> open, String msg) {
        System.out.println("  chk: " + msg + " fam=" + s.family + " ch=" + s.challenge);
        for (int yy = s.ry0 - 1; yy <= s.ry1 + 1; yy++) {
            StringBuilder sb = new StringBuilder();
            for (int xx = s.rx0 - 2; xx <= s.rx1 + 2; xx++) sb.append(open.contains(yy * 1000 + xx) ? 'o' : ".#=~SBDHF^v".charAt(Math.max(0, rm.tile(xx, yy))));
            System.out.println("  |" + sb);
        }
    }

    private static void place(Room rm, Secret s, int W) {
        // el recuadro no aloja enemigos ni decoracion
        for (int y = s.ry0; y <= s.ry1; y++) for (int x = s.rx0; x <= s.rx1; x++) { if (x >= 0 && x < W) { rm.deco[y * W + x] = 0; } }
    }

    /** La columna esta reservada (mecanismos, entrada o recuadro de una camara): no se colocan trampas ni apariciones encima. */
    static boolean reserved(Room rm, int tx) {
        for (Secret s : rm.secrets) {
            if (tx >= s.rx0 - 2 && tx <= s.rx1 + 2) return true;
            for (float[] w : s.sw) if (Math.abs(tx - (int) (w[0] / Room.TS)) <= 2) return true;
            if (s.entrance == Secret.E_SKILL && Math.abs(tx - (int) (s.crX / Room.TS)) <= 2) return true;
        }
        return false;
    }

    /** Quita de la lista de apariciones los enemigos que hayan quedado dentro de una camara. */
    static void clearSpawns(Room rm) {
        if (rm.secrets.isEmpty()) return;
        rm.spawns.removeIf(sp -> { int tx = (int) (sp.x / Room.TS), ty = (int) (sp.y / Room.TS); for (Secret s : rm.secrets) if (s.contains(tx, ty - 1)) return true; return false; });
    }
}
