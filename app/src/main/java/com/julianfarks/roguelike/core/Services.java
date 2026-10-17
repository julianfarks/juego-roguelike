package com.julianfarks.roguelike.core;

import java.util.HashSet;
import java.util.Set;
import java.util.function.Consumer;

/**
 * Puntos de integracion con servicios externos. Por ahora TODOS estan DESACTIVADOS (no hay SDK de anuncios ni de pagos):
 * el nucleo del juego solo habla con estas interfaces, asi que conectar AdMob / Google Play Billing mas adelante consiste
 * en escribir un adaptador Android que implemente la interfaz y asignarlo aqui al arrancar, sin tocar revividas ni recompensas.
 */
public final class Services {
    private Services() {}

    public enum AdPlacement { REVIVE_STANDARD, REVIVE_LONG, REWARD_SOULS }
    public enum AdResult { COMPLETED, DISMISSED, FAILED }

    public interface AdProvider {
        /** true solo si hay un anuncio cargado y listo para ese formato. */
        boolean isReady(AdPlacement p);
        /** Muestra el anuncio y avisa UNA vez del resultado (COMPLETED solo si el usuario gano la recompensa). */
        void show(AdPlacement p, Consumer<AdResult> done);
    }

    public interface BillingProvider {
        boolean isAvailable();
        /** Lanza la compra; entrega el recibo (verificado o no) o null si se cancelo/fallo. */
        void purchase(String productId, Consumer<PurchaseReceipt> done);
        /** Recupera compras permanentes (restaurar). */
        void restore(Consumer<java.util.List<PurchaseReceipt>> done);
    }

    /** Proveedor por defecto: sin anuncios. */
    public static final AdProvider NO_ADS = new AdProvider() {
        @Override public boolean isReady(AdPlacement p) { return false; }
        @Override public void show(AdPlacement p, Consumer<AdResult> done) { done.accept(AdResult.FAILED); }
    };
    /** Proveedor por defecto: sin pagos. */
    public static final BillingProvider NO_BILLING = new BillingProvider() {
        @Override public boolean isAvailable() { return false; }
        @Override public void purchase(String productId, Consumer<PurchaseReceipt> done) { done.accept(null); }
        @Override public void restore(Consumer<java.util.List<PurchaseReceipt>> done) { done.accept(new java.util.ArrayList<>()); }
    };

    public static AdProvider ads = NO_ADS;
    public static BillingProvider billing = NO_BILLING;

    // ------------------------------------------------------------------ recompensa por anuncio (una sola vez)
    private static final Set<Long> pending = new HashSet<>();
    private static long nextToken = 1;

    /** Hay un anuncio de recompensa en curso. */
    public static boolean adInFlight() { return !pending.isEmpty(); }

    /**
     * Pide un anuncio recompensado. 'grant' se ejecuta como mucho UNA vez y solo si el proveedor confirma COMPLETED.
     * Devuelve false si no hay anuncio disponible o ya hay otro en curso (evita reclamar varias veces con toques repetidos).
     */
    public static boolean requestRewardedAd(AdPlacement p, Runnable grant) {
        if (!pending.isEmpty() || ads == null || !ads.isReady(p)) return false;
        final long token = nextToken++;
        pending.add(token);
        ads.show(p, r -> {
            boolean first = pending.remove(token);      // un segundo aviso del mismo anuncio ya no encuentra el token
            if (first && r == AdResult.COMPLETED) grant.run();
        });
        return true;
    }

    // ------------------------------------------------------------------ entrega de compras (idempotente)
    /** Entrega un recibo VERIFICADO. Devuelve true solo la primera vez que se entrega ese orderId. */
    public static boolean fulfill(PurchaseReceipt r) {
        if (r == null || !r.verified || r.orderId == null || r.orderId.isEmpty()) return false;
        if (r.gems > 0) return Wallet.credit(r);
        Cosmetics.Item it = Cosmetics.find(r.productId);
        if (it == null || Save.S.gemTx.contains(r.orderId)) return false;
        Save.S.gemTx.add(r.orderId);
        return Cosmetics.grant(it.id);
    }
}
