package com.julianfarks.roguelike.core;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/**
 * Codigos canjeables. Cada codigo se guarda solo como hash SHA-256 (no en claro) en la tabla ALL.
 * Para anadir uno: python3 tools/code_hash.py MICODIGO y agregar una linea a ALL.
 *
 * AVISO HONESTO: la validacion ocurre en el cliente. Los hashes evitan leer los codigos a simple vista, pero alguien con acceso al
 * APK puede probar codigos por fuerza bruta o modificar el juego; no es seguridad real. Para una version publica seria, sustituye
 * {@link #validator} por una implementacion que consulte un servidor (el resto del juego solo usa Codes.redeem).
 */
final class Codes {
    private Codes() {}

    enum Res { OK, INVALID, USED, UNDELIVERABLE }

    static final class Result {
        final Res res; final String msg;
        Result(Res r, String m) { res = r; msg = m; }
    }

    static final int K_DEV = 0, K_SOULS = 1;
    static final int SOULS_CAP = 999999;

    static final class Def {
        final String id, hash; final int kind, amount; final boolean oneUse;
        Def(String id, String hash, int kind, int amount, boolean oneUse) { this.id = id; this.hash = hash; this.kind = kind; this.amount = amount; this.oneUse = oneUse; }
    }

    /** Tabla de codigos. kind K_SOULS = almas (la moneda permanente del Santuario); amount = cantidad. */
    static final Def[] ALL = {
            new Def("dev", "b84127e1f5ac1d45e834dd36ca23f6e023484f0482cb0794bf93ed8e6b2f6ff2", K_DEV, 0, false),
            // ejemplo: new Def("promo1", "<hash de tools/code_hash.py>", K_SOULS, 500, true),
    };

    /** Punto de sustitucion para validar en un servidor en el futuro. */
    interface Validator { Result redeem(String raw); }
    static Validator validator = Codes::redeemLocal;

    static Result redeem(String raw) { return validator.redeem(raw); }

    static String hash(String raw) {
        try {
            String norm = raw == null ? "" : raw.toLowerCase().replace(" ", "").trim();
            byte[] d = MessageDigest.getInstance("SHA-256").digest(("swr1:" + norm).getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : d) sb.append(String.format("%02x", b));
            return sb.toString();
        } catch (Exception e) { return ""; }
    }

    static boolean used(int idx) { return idx >= 0 && idx < Save.S.codesUsed.length && Save.S.codesUsed[idx] != 0; }

    static Result redeemLocal(String raw) {
        if (raw == null || raw.trim().isEmpty()) return new Result(Res.INVALID, "Escribe un código.");
        String h = hash(raw);
        for (int i = 0; i < ALL.length; i++) {
            Def d = ALL[i];
            if (!d.hash.equals(h)) continue;
            if (d.kind == K_DEV) {
                if (Save.S.devUnlocked) return new Result(Res.USED, "El Modo Desarrollador ya estaba activado.");
                Save.S.devUnlocked = true;
                Save.S.write();
                return new Result(Res.OK, "Modo Desarrollador desbloqueado.");
            }
            if (d.oneUse && used(i)) return new Result(Res.USED, "Este código ya fue canjeado.");
            if (d.kind == K_SOULS) {
                if (Save.S.souls + d.amount > SOULS_CAP) return new Result(Res.UNDELIVERABLE, "Código válido, pero tienes demasiadas almas para recibir la recompensa.");
                if (i >= Save.S.codesUsed.length) return new Result(Res.UNDELIVERABLE, "Código válido, pero no se pudo registrar el canje. Inténtalo más tarde.");
                Save.S.souls += d.amount;
                Save.S.codesUsed[i] = 1;
                Save.S.write();
                return new Result(Res.OK, "¡Canjeado! +" + d.amount + " almas.");
            }
            return new Result(Res.UNDELIVERABLE, "Código válido, pero la recompensa no está disponible.");
        }
        return new Result(Res.INVALID, "Código incorrecto.");
    }
}
