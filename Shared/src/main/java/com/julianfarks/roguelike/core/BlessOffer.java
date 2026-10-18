package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Seleccion de las bendiciones que ofrecen los altares, tiendas y sucesos. Logica pura (sin pantalla), probada por tools/tests.
 *
 * Reglas:
 *  - solo se ofrecen bendiciones que aun puedan subir de nivel y cuyo piso minimo y requisito de aparicion se cumplan
 *    (las epicas aparecen desde el 2.o bioma; las legendarias exigen ademas tener varias bendiciones de su categoria o de su familia);
 *  - el peso base de cada una sale de su rareza; subir una que ya tienes pesa un poco mas;
 *  - afinidad: las que forman sinergia con lo que ya tienes pesan un poco mas (nunca se garantiza una sinergia);
 *  - variedad: no se repiten categorias dentro de la misma oferta (la 2.a de una categoria pesa la mitad) y las ya ofrecidas hace poco pesan menos;
 *  - como mucho una legendaria por oferta.
 */
final class BlessOffer {
    private BlessOffer() {}

    private static int[][] memberOf;

    /** Indices de sinergia de cada bendicion. */
    static int[][] memberOf() {
        if (memberOf == null) {
            BSyn[] syns = BlessData.syns();
            int n = Blessing.ALL.length;
            int[] cnt = new int[n];
            for (BSyn s : syns) for (int id : s.members) cnt[id]++;
            int[][] m = new int[n][];
            for (int i = 0; i < n; i++) m[i] = new int[cnt[i]];
            java.util.Arrays.fill(cnt, 0);
            for (int si = 0; si < syns.length; si++) for (int id : syns[si].members) m[id][cnt[id]++] = si;
            memberOf = m;
        }
        return memberOf;
    }

    /** Piso efectivo para las condiciones de aparicion (0..3). */
    static int stageIdx(RunState rs) { return rs.infinite ? Math.min(3, rs.floor) : Math.min(3, Math.max(0, rs.stage)); }

    static int ownedInCat(RunState rs, char cat) {
        int n = 0;
        for (Blessing b : Blessing.ALL) if (b.cat == cat && rs.bless[b.id] > 0) n++;
        return n;
    }

    static boolean reqOk(RunState rs, Blessing b) {
        String r = b.req;
        if (r == null || r.isEmpty()) return true;
        String[] p = r.split(":");
        if (p[0].equals("cat")) return ownedInCat(rs, p[1].charAt(0)) >= Integer.parseInt(p[2]);
        if (p[0].equals("has")) {
            int need = Integer.parseInt(p[1]), have = 0;
            for (String s : p[2].split(",")) if (rs.bless[Integer.parseInt(s)] > 0) have++;
            return have >= need;
        }
        return true;
    }

    /** Texto corto (espanol, clave de traduccion) del requisito para el panel de informacion. */
    static String reqText(Blessing b) {
        if (b.req == null || b.req.isEmpty()) return "";
        String[] p = b.req.split(":");
        if (p[0].equals("cat")) return "Aparece con {} bendiciones de su categoria".replace("{}", p[2]);
        return "Aparece con {} bendiciones de su familia".replace("{}", p[1]);
    }

    static boolean eligible(RunState rs, Blessing b) {
        if (rs.bless[b.id] >= b.max) return false;
        if (rs.bless[b.id] == 0) {
            if (b.minStage > stageIdx(rs)) return false;
            if (!reqOk(rs, b)) return false;
        }
        return true;
    }

    /** Sinergias en las que participa b y cuantos miembros tendrias al elegirla: {indiceSinergia, tendras, necesarias, activaAhora(0/1)}. */
    static List<int[]> synergyInfo(RunState rs, Blessing b) {
        List<int[]> out = new ArrayList<>();
        BSyn[] syns = BlessData.syns();
        for (int si : memberOf()[b.id]) {
            int have = 0;
            for (int id : syns[si].members) if (rs.bless[id] > 0 || id == b.id) have++;
            int already = 0;
            for (int id : syns[si].members) if (rs.bless[id] > 0) already++;
            if (already >= 1 || have >= syns[si].need) out.add(new int[]{si, have, syns[si].need, already >= syns[si].need ? 1 : 0});
        }
        return out;
    }

    private static float weight(RunState rs, Blessing b, int[] catPicked, int luck) {
        float w = b.weight;
        if (rs.bless[b.id] > 0) w *= 1.25f;
        // afinidad: comparte sinergia con lo que ya tienes (sin garantizar nada)
        int aff = 0;
        BSyn[] syns = BlessData.syns();
        for (int si : memberOf()[b.id]) {
            int already = 0;
            for (int id : syns[si].members) if (id != b.id && rs.bless[id] > 0) already++;
            if (already >= 1 && already < syns[si].need) aff++;
        }
        w *= 1f + 0.3f * Math.min(2, aff);
        // variedad dentro de la oferta y respecto a ofertas recientes
        int ci = b.cat - 'A';
        if (catPicked[ci] > 0) w *= 0.45f;
        BlessRt bx = rs.bx;
        if (bx != null) w /= 1f + 0.5f * Math.min(4, bx.offered[b.id]);
        // suerte: mejora un poco las raras
        if (b.rar >= 2 && luck > 0) w *= 1f + 0.12f * luck * (b.rar - 1);
        return Math.max(0.05f, w);
    }

    /** Elige hasta n bendiciones distintas para una oferta. Devuelve un arreglo de n ids (-1 = hueco vacio). */
    static int[] pick(RunState rs, int n, Rng rng) {
        List<Integer> pool = new ArrayList<>();
        for (Blessing b : Blessing.ALL) if (eligible(rs, b)) pool.add(b.id);
        int[] out = new int[n];
        java.util.Arrays.fill(out, -1);
        int[] catPicked = new int[Blessing.ALL.length > 0 ? 10 : 0];
        boolean legendary = false;
        int luck = rs.stats == null ? 0 : rs.stats.luck;
        for (int i = 0; i < n && !pool.isEmpty(); i++) {
            float tot = 0;
            float[] ws = new float[pool.size()];
            for (int k = 0; k < ws.length; k++) {
                Blessing b = Blessing.ALL[pool.get(k)];
                ws[k] = legendary && b.rar == Blessing.LEGENDARY ? 0f : weight(rs, b, catPicked, luck);
                tot += ws[k];
            }
            if (tot <= 0) break;
            float r = rng.f() * tot;
            int chosenK = ws.length - 1;
            for (int k = 0; k < ws.length; k++) { r -= ws[k]; if (r <= 0 && ws[k] > 0) { chosenK = k; break; } }
            int id = pool.remove(chosenK);
            out[i] = id;
            Blessing b = Blessing.ALL[id];
            catPicked[b.cat - 'A']++;
            if (b.rar == Blessing.LEGENDARY) legendary = true;
        }
        BlessRt bx = rs.bx;
        if (bx != null) for (int id : out) if (id >= 0) bx.offered[id]++;
        return out;
    }

    /** Una sola bendicion para tiendas y sucesos. */
    static int pickOne(RunState rs, Rng rng) {
        int[] r = pick(rs, 1, rng);
        return r[0];
    }
}
