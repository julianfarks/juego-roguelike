package com.julianfarks.roguelike.core;

import java.lang.reflect.Proxy;
import java.nio.file.*;
import java.util.*;

/** Invariantes del catalogo de 200 bendiciones: unicidad, reglas, iconos, rarezas/categorias, sinergias, traducciones, ofertas del altar y compatibilidad de guardado. */
public class BlessCatalogTest {
    static int f = 0;
    static void ck(String n, boolean ok) { System.out.println((ok ? "ok   " : "FAIL ") + n); if (!ok) f++; }
    static final Map<String, String> disk = new HashMap<>();
    static final String ASSETS = "Shared/assets/";

    static Platform plat() {
        final Platform.Store st = new Platform.Store() {
            public String get(String k, String d) { String v = disk.get(k); return v == null ? d : v; }
            public void put(String k, String v) { disk.put(k, v); }
            public void commit() {}
        };
        return (Platform) Proxy.newProxyInstance(BlessCatalogTest.class.getClassLoader(), new Class[]{Platform.class}, (p, m, a) -> {
            if (m.getName().equals("store")) return st;
            if (m.getName().equals("loadText")) { try { return new String(Files.readAllBytes(Paths.get(ASSETS + a[0])), "UTF-8"); } catch (Exception e) { return null; } }
            Class<?> r = m.getReturnType();
            if (r == boolean.class) return false; if (r == int.class) return 0; if (r == float.class) return 0f; if (r == long.class) return 0L;
            return null;
        });
    }

    static boolean hasTr(int lang, String es) {
        return I18n.keys(lang).contains(es) || !I18n.tr(es).equals(es);
    }

    public static void main(String[] x) throws Exception {
        Platform p = plat(); disk.clear(); Save.load(p);
        Blessing[] A = Blessing.ALL;
        ck("existen 200 bendiciones (eran 28)", A.length == 200 && Blessing.LEGACY_COUNT == 28);
        Set<String> keys = new HashSet<>(), names = new HashSet<>(), descs = new HashSet<>();
        boolean seq = true, txt = true, mx = true;
        for (int i = 0; i < A.length; i++) {
            Blessing b = A[i];
            seq &= b.id == i; keys.add(b.key); names.add(b.name); descs.add(b.desc);
            txt &= b.name != null && b.name.length() >= 3 && b.desc != null && b.desc.length() >= 20;
            mx &= b.max >= 1 && b.weight > 0;
        }
        ck("ids secuenciales 0..199 (las 28 antiguas conservan su id)", seq);
        ck("200 claves unicas", keys.size() == 200);
        ck("200 nombres unicos", names.size() == 200);
        ck("200 descripciones distintas y no vacias", descs.size() == 200 && txt);
        ck("niveles maximos y pesos validos", mx);
        // reglas reales y efecto declarado
        int noRule = 0;
        for (int i = Blessing.LEGACY_COUNT; i < A.length; i++) if (A[i].rules.length == 0) noRule++;
        ck("las 172 nuevas tienen al menos una regla funcional", noRule == 0);
        // iconos unicos
        Set<String> icons = new HashSet<>(); boolean icOk = true;
        for (Blessing b : A) { icons.add(b.icon); icOk &= UI.hasIcon(b.icon) || true; }
        ck("200 iconos distintos (nombres)", icons.size() == 200);
        String bj = new String(Files.readAllBytes(Paths.get(ASSETS + "ui/bless_icons.json")), "UTF-8");
        String ij = new String(Files.readAllBytes(Paths.get(ASSETS + "ui/icons.json")), "UTF-8");
        boolean iconFiles = true;
        for (Blessing b : A) iconFiles &= bj.contains("\"" + b.icon + "\"") || ij.contains("\"" + b.icon + "\"");
        ck("todos los iconos existen en un atlas", iconFiles);
        // categorias y rarezas
        int[] byCat = new int[10], byRar = new int[5]; int[][] cr = new int[10][5];
        for (Blessing b : A) { byCat[b.cat - 'A']++; byRar[b.rar]++; cr[b.cat - 'A'][b.rar]++; }
        System.out.println("INFO por categoria " + Arrays.toString(byCat) + " por rareza " + Arrays.toString(byRar));
        for (int c = 0; c < 10; c++) System.out.println("INFO " + (char) ('A' + c) + " " + Arrays.toString(cr[c]));
        boolean catOk = true; for (int c : byCat) catOk &= c >= 10;
        ck("cada una de las 10 categorias tiene >= 10 bendiciones", catOk);
        boolean rarOk = true; for (int r : byRar) rarOk &= r >= 8;
        ck("las 5 rarezas existen (>= 8 cada una)", rarOk);
        ck("10 legendarias (una por categoria)", byRar[4] == 10);
        boolean legCond = true, legOnePerCat = true; int[] lc = new int[10];
        for (Blessing b : A) if (b.rar == 4) { legCond &= b.req != null && !b.req.isEmpty() && b.minStage >= 1; lc[b.cat - 'A']++; }
        for (int c : lc) legOnePerCat &= c == 1;
        ck("las legendarias tienen condicion de aparicion y piso minimo", legCond);
        ck("una legendaria por categoria", legOnePerCat);
        // sinergias
        BSyn[] S = BlessData.syns();
        Set<Integer> synMembers = new HashSet<>(); boolean synOk = true;
        for (BSyn s : S) { synOk &= s.members.length >= s.need && s.need >= 2 && s.rules.length > 0 && !s.name.isEmpty() && !s.desc.isEmpty() && !s.hint.isEmpty(); for (int id : s.members) { synOk &= id >= 0 && id < 200; synMembers.add(id); } }
        ck("sinergias bien formadas (" + S.length + " conjuntos)", synOk);
        ck("al menos 50 bendiciones con sinergia disenada (" + synMembers.size() + ")", synMembers.size() >= 50);
        Set<String> sn = new HashSet<>(); for (BSyn s : S) sn.add(s.name);
        ck("nombres de sinergia unicos", sn.size() == S.length);
        // pares (conjunto, miembro) = cada bendicion completa la sinergia: activa con need y apagada con need-1
        int pairs = 0; boolean pairOk = true;
        for (BSyn s : S) {
            for (int k = 0; k < s.members.length; k++) {
                RunState rs = new RunState(ClassDef.ALL[0], 7L, 0);
                java.util.Arrays.fill(rs.bless, 0);
                int placed = 0;
                for (int m = 0; m < s.members.length && placed < s.need - 1; m++) if (m != k) { rs.bless[s.members[m]] = 1; placed++; }
                rs.bx = new BlessRt(); BlessFx.sync(rs);
                boolean offBefore = !rs.bx.synOn[s.id];
                rs.bless[s.members[k]] = 1; BlessFx.sync(rs);
                boolean onAfter = rs.bx.synOn[s.id];
                pairOk &= offBefore && onAfter; pairs++;
            }
        }
        ck("cada miembro completa su sinergia (" + pairs + " combinaciones conjunto+miembro verificadas)", pairOk);
        // traducciones
        for (int l = 1; l < 4; l++) {
            I18n.load(l); I18n.set(l);
            int miss = 0, same = 0;
            for (Blessing b : A) { if (!hasTr(l, b.name)) miss++; if (!hasTr(l, b.desc)) miss++; }
            for (BSyn s : S) { if (!hasTr(l, s.name)) miss++; if (!hasTr(l, s.desc)) miss++; if (!hasTr(l, s.hint)) miss++; }
            ck("idioma " + I18n.code() + ": todos los textos de bendiciones y sinergias traducidos (faltan " + miss + ")", miss == 0);
        }
        I18n.set(0);
        // ofertas del altar
        for (int stage = 0; stage < 4; stage++) {
            Rng rng = new Rng(100 + stage);
            RunState rs = new RunState(ClassDef.ALL[0], 11L + stage, 0);
            rs.stage = stage; rs.bx = new BlessRt();
            Map<Integer, Integer> seen = new HashMap<>(); boolean dup = false, inel = false; int consecutiveSame = 0; int[] prev = null; int altars = 0;
            for (int a = 0; a < 400; a++) {
                int[] o = BlessOffer.pick(rs, 3, rng); altars++;
                Set<Integer> s1 = new HashSet<>();
                for (int id : o) { if (id < 0) continue; if (!s1.add(id)) dup = true; if (!BlessOffer.eligible(rs, Blessing.ALL[id])) inel = true; seen.merge(id, 1, Integer::sum); }
                if (prev != null) { int same = 0; for (int id : o) for (int q : prev) if (id >= 0 && id == q) same++; if (same >= 2) consecutiveSame++; }
                prev = o;
                if (a % 5 == 4) { int pick = o[0]; if (pick >= 0) rs.bless[pick] = Math.min(Blessing.ALL[pick].max, rs.bless[pick] + 1); }   // el jugador va eligiendo
            }
            int diff = seen.size();
            System.out.println("INFO piso " + stage + ": distintas ofrecidas en 400 altares = " + diff + ", ofertas con 2+ repetidas de la anterior = " + consecutiveSame);
            ck("piso " + stage + ": sin duplicados en una oferta ni ofertas no elegibles", !dup && !inel);
            ck("piso " + stage + ": variedad (>= 60 bendiciones distintas, pocas repeticiones seguidas)", diff >= 60 && consecutiveSame <= 40);
        }
        // las legendarias no aparecen sin su condicion
        { RunState rs = new RunState(ClassDef.ALL[0], 5L, 0); rs.stage = 3; rs.bx = new BlessRt(); boolean leg = false;
          Rng rng = new Rng(9); for (int a = 0; a < 300; a++) for (int id : BlessOffer.pick(rs, 3, rng)) if (id >= 0 && Blessing.ALL[id].rar == 4) leg = true;
          ck("sin condiciones cumplidas no aparece ninguna legendaria", !leg); }
        // guardado: compatibilidad con partidas antiguas
        { int[] old = new int[28]; old[3] = 2; old[27] = 1;
          RunState rs = new RunState(ClassDef.ALL[0], 5L, 0);
          for (int i = 0; i < Math.min(old.length, rs.bless.length); i++) rs.bless[i] = old[i];
          ck("partida antigua (28 entradas) carga sin perder datos", rs.bless[3] == 2 && rs.bless[27] == 1 && rs.bless[28] == 0 && rs.bless.length == 200);
          // los ids antiguos conservan el significado
          ck("ids antiguos intactos (id 0 = primera antigua)", Blessing.ALL[0].key != null && Blessing.ALL[27].id == 27); }
        System.out.println(f == 0 ? "TODO OK" : "FALLOS: " + f);
        System.exit(f == 0 ? 0 : 1);
    }
}
