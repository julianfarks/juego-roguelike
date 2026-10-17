package com.julianfarks.roguelike.core;

/** Recibo de una compra (futuro Google Play Billing). Solo un recibo con verified=true puede entregar productos. */
public final class PurchaseReceipt {
    public final String orderId;      // id unico de la transaccion (Google Play orderId): clave anti-duplicado
    public final String productId;
    public final int gems;            // gemas que otorga (0 si es un articulo)
    public final boolean verified;    // lo marca un verificador de servidor; NUNCA el propio cliente por defecto
    public PurchaseReceipt(String orderId, String productId, int gems, boolean verified) {
        this.orderId = orderId; this.productId = productId; this.gems = gems; this.verified = verified;
    }
}
