package com.julianfarks.roguelike.core;

import java.util.List;

/**
 * Colocacion validada de cofres de recompensa. Causa del fallo anterior: los cofres de fin de ronda se ponian en coordenadas fijas
 * respecto a la puerta (exitX - 70 - i * 38, exitY) sin mirar el escenario: si en ese punto el suelo cambia de altura, hay un pozo, un
 * pilar, una repisa o pinchos, el cofre quedaba medio enterrado, dentro de una pared o sin acceso. Aqui se busca un punto que cumpla:
 * suelo firme bajo todo el ancho del cofre, 2 baldosas libres encima, sin pinchos al lado, un lado libre para que el jugador se acerque,
 * dentro de la sala y sin solaparse con otros objetos. Si no hay ninguno cerca se amplia la busqueda y, como ultimo recurso, se usa el
 * punto firme del jugador (nunca se elimina la recompensa).
 */
final class ChestSpot {
    private ChestSpot() {}
    static final int HALF = 10;               // medio ancho del cofre (px)
    static final float GAP_X = 32, GAP_Y = 26; // separacion minima con otros objetos
    /** Contadores para pruebas. */
    static int dbgPlaced, dbgMoved, dbgFallback, dbgForced;

    private static boolean standable(Room rm, int tx, int gy) {
        int g = rm.tile(tx, gy);
        return (g == Room.SOLID || g == Room.ONEWAY) && rm.tile(tx, gy - 1) == Room.AIR && rm.tile(tx, gy - 2) == Room.AIR;
    }

    /** Un cofre con los pies en (x, y) cabe en la geometria de la sala (sin mirar otros objetos). */
    static boolean validGeometry(Room rm, float x, float y) {
        if (x < Room.TS * 1.5f || x > rm.pixW - Room.TS * 1.5f || y < Room.TS * 3 || y >= rm.pixH) return false;
        int t0 = (int) Math.floor((x - HALF) / Room.TS), t1 = (int) Math.floor((x + HALF - 1) / Room.TS), gy = (int) Math.floor(y / Room.TS);
        if (Math.abs(y - gy * Room.TS) > 1.5f) return false;                 // los pies deben estar sobre la superficie
        for (int t = t0; t <= t1; t++) if (!standable(rm, t, gy)) return false;
        if (rm.tile(t0 - 1, gy - 1) == Room.SPIKE || rm.tile(t1 + 1, gy - 1) == Room.SPIKE) return false;
        // acceso: al menos un lado donde el jugador pueda ponerse (suelo y 2 baldosas libres)
        int l = (int) Math.floor((x - HALF - 8) / Room.TS), r = (int) Math.floor((x + HALF + 8) / Room.TS);
        return standable(rm, l, gy) || standable(rm, r, gy);
    }

    static boolean free(List<Prop> props, float x, float y) {
        if (props == null) return true;
        for (Prop p : props) {
            if (p.kind.equals("pot") || p.kind.equals("break")) continue;
            if (Math.abs(p.x - x) < GAP_X && Math.abs(p.y - y) < GAP_Y) return false;
        }
        return true;
    }

    static boolean valid(Level lv, float x, float y) { return validGeometry(lv.room, x, y) && free(lv.props, x, y); }

    /** Busca el punto valido mas cercano a (px, py). Siempre devuelve un punto: {x, y, nivel} (nivel 0 = junto a lo pedido, 1 = ampliado, 2 = ultimo recurso). */
    static float[] find(Level lv, float px, float py) { return find(lv.room, lv.props, lv.pl.safeX, lv.pl.safeY, px, py); }

    static float[] find(Room rm, List<Prop> props, float safeX, float safeY, float px, float py) {
        int gy0 = (int) Math.floor(py / Room.TS);
        // 1) misma fila, abriendose hacia ambos lados
        for (int d = 0; d <= 240; d += 4) {
            for (int s = 0; s < 2; s++) {
                if (d == 0 && s == 1) continue;
                float x = px + (s == 0 ? -d : d);
                if (validGeometry(rm, x, gy0 * Room.TS) && free(props, x, gy0 * Room.TS)) return new float[]{x, gy0 * Room.TS, 0};
            }
        }
        // 2) cualquier superficie cercana, por distancia creciente
        float bx = 0, by = 0, best = Float.MAX_VALUE;
        for (int gy = Math.max(3, gy0 - 14); gy <= Math.min(rm.h - 1, gy0 + 14); gy++) {
            for (float x = Room.TS * 2; x <= rm.pixW - Room.TS * 2; x += 4) {
                float dist = Math.abs(x - px) + 2.5f * Math.abs(gy * Room.TS - py);
                if (dist >= best || dist > 900) continue;
                if (validGeometry(rm, x, gy * Room.TS) && free(props, x, gy * Room.TS)) { best = dist; bx = x; by = gy * Room.TS; }
            }
        }
        if (best < Float.MAX_VALUE) return new float[]{bx, by, 1};
        // 3) ultimo recurso: junto al ultimo punto firme del jugador (suelo comprobado por el propio juego)
        for (int k = 0; k < 40; k++) for (int s = -1; s <= 1; s += 2) {
            float x = safeX + s * k * 8;
            if (validGeometry(rm, x, safeY)) return new float[]{x, safeY, 2};
        }
        return new float[]{safeX, safeY, 3};
    }

    /** Prueba: genera muchas salas y compara la colocacion antigua (desplazamientos fijos desde la puerta) con la validada. */
    static void probe() {
        int rooms = 0, oldBad = 0, newBad = 0, fb = 0, forced = 0, preBad = 0, preTotal = 0, noAccess = 0;
        int[] types = {Room.COMBAT, Room.ELITE, Room.TREASURE, Room.BOSS, Room.EVENT, Room.REST, Room.SHOP};
        for (Biome b : Biome.ALL) for (int ty : types) for (int st = 1; st <= 6; st++) for (int sd = 0; sd < 6; sd++) {
            Room rm;
            try { rm = RoomGen.generate(ty, b, new Rng(1000L * st + sd * 7 + ty), st, 1 + sd, 0); } catch (RuntimeException e) { continue; }
            rooms++;
            for (Room.PropSpec ps : rm.props) if (ps.kind.equals("chest")) { preTotal++; if (!validGeometry(rm, ps.x, ps.y)) preBad++; }
            java.util.ArrayList<Prop> placed = new java.util.ArrayList<>();
            for (int i = 0; i < 3; i++) {
                float ox = rm.exitX - 70 - i * 38;
                if (!validGeometry(rm, ox, rm.exitY)) oldBad++;
                float[] s = find(rm, placed, rm.spawnX, rm.spawnY, ox, rm.exitY);
                Prop c = new Prop("chest", s[0], s[1]);
                if (!validGeometry(rm, s[0], s[1])) { newBad++; if (s[2] >= 3) forced++; }
                if (s[2] >= 2) fb++;
                placed.add(c);
            }
            for (int i = 0; i < placed.size(); i++) for (int j = i + 1; j < placed.size(); j++)
                if (Math.abs(placed.get(i).x - placed.get(j).x) < GAP_X && Math.abs(placed.get(i).y - placed.get(j).y) < GAP_Y) noAccess++;
        }
        System.out.println("CHESTPOS salas=" + rooms + " cofres de ronda: antiguo invalido=" + oldBad + " nuevo invalido=" + newBad + " ultimo recurso=" + fb + " forzado=" + forced + " solapados=" + noAccess
            + " | cofres de generacion=" + preTotal + " invalidos(antes de reubicar)=" + preBad);
    }
}
