package com.julianfarks.roguelike.core;

/**
 * Moneda PREMIUM (gemas moradas). Es independiente de las almas y del oro: tiene su propio saldo y NO existe ninguna
 * operacion que mezcle ambas. Toda modificacion del saldo pasa por aqui:
 *  - spend(): nunca permite cantidades <= 0 ni saldo negativo.
 *  - credit(): SOLO con un recibo verificado y un id de transaccion que no se haya acreditado antes (anti-duplicado).
 *  - devGrant(): saldo de PRUEBA del Modo Desarrollador; vive en memoria, no se guarda y se gasta primero.
 * AVISO: el saldo se guarda en el almacen local del telefono; es editable por quien controle el dispositivo. Para dinero real
 * y competiciones el saldo definitivo debe vivir en un servidor (ver docs/INTEGRACIONES.md).
 */
public final class Wallet {
    private Wallet() {}
    public static final int MAX = 999_999;
    private static final int TX_KEEP = 500;

    /** Saldo disponible (real + de prueba de la sesion). */
    public static int gems() { return Save.S.gems + Save.devGems; }
    public static boolean canSpend(int n) { return n > 0 && gems() >= n; }
    /** Saldo REAL (el que se guarda y el unico valido para articulos oficiales y competiciones). */
    public static int realGems() { return Save.S.gems; }

    /** Gasta SOLO gemas reales (nunca las de prueba). Usar para articulos oficiales. */
    public static boolean spendReal(int n, boolean commit) {
        if (n <= 0 || Save.S.gems < n) return false;
        Save.S.gems -= n;
        Save.S.write(commit);
        return true;
    }

    /** Gasta n gemas. Devuelve false (sin cambiar nada) si n<=0 o no alcanza. */
    public static boolean spend(int n) { return spend(n, true); }

    /** commit=false: modifica el saldo y deja la escritura a medias para que el que llama la complete junto con otros datos. */
    public static boolean spend(int n, boolean commit) { return spend(n, commit, null); }

    /** usedDev (opcional, [0]) se pone a true si parte del gasto salio de gemas de prueba. */
    public static boolean spend(int n, boolean commit, boolean[] usedDev) {
        if (n <= 0 || gems() < n) return false;
        int fromDev = Math.min(Save.devGems, n);
        if (usedDev != null && fromDev > 0) usedDev[0] = true;
        Save.devGems -= fromDev;
        Save.S.gems -= n - fromDev;
        if (Save.S.gems < 0) Save.S.gems = 0;   // defensa: jamas negativo
        if (n - fromDev > 0) Save.S.write(commit);
        return true;
    }

    /** Acredita gemas de una compra verificada. Idempotente por orderId. */
    public static boolean credit(PurchaseReceipt r) {
        if (r == null || !r.verified || r.orderId == null || r.orderId.isEmpty() || r.gems <= 0) return false;
        Save s = Save.S;
        if (s.gemTx.contains(r.orderId)) return false;
        s.gems = Math.min(MAX, s.gems + r.gems);
        s.gemTx.add(r.orderId);
        while (s.gemTx.size() > TX_KEEP) s.gemTx.remove(0);
        s.write();
        return true;
    }

    /** Gemas de prueba (solo Modo Desarrollador desbloqueado; no se guardan; no es una compra). */
    public static boolean devGrant(int n) {
        if (!Save.S.devUnlocked || n <= 0) return false;
        Save.devGems = Math.min(MAX, Save.devGems + n);
        return true;
    }
}
