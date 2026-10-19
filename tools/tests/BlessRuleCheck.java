package com.julianfarks.roguelike.core;

/** Valida con el analizador real (BRule.parse) TODAS las reglas del catalogo y de las sinergias, listando cada error (no solo el primero). */
public class BlessRuleCheck {
    public static void main(String[] a) {
        int bad = 0, n = 0;
        for (String[] r : BlessData.NEW) for (String q : r[10].split("~")) { if (q.isEmpty()) continue; n++; try { BRule.parse(q, 0); } catch (RuntimeException e) { bad++; System.out.println("MALA " + r[0] + ": " + e.getMessage()); } }
        for (String[] r : BlessData.SYN) for (String q : r[6].split("~")) { if (q.isEmpty()) continue; n++; try { BRule.parse(q, -1); } catch (RuntimeException e) { bad++; System.out.println("MALA syn " + r[0] + ": " + e.getMessage()); } }
        System.out.println("reglas=" + n + " invalidas=" + bad);
        if (bad > 0) System.exit(1);
    }
}
