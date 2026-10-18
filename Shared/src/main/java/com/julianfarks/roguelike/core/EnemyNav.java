package com.julianfarks.roguelike.core;

/**
 * Navegacion local y barata para enemigos terrestres: una busqueda de costes (Dijkstra) sobre las celdas "de pie" de la sala (suelo firme debajo,
 * cuerpo libre y sin pinchos). Solo se ejecuta cuando el camino directo al jugador esta cortado por pinchos o un borde, como mucho unas 2-3 veces por
 * segundo y por enemigo, en una ventana de 81x21 celdas (sin asignar memoria: buffers estaticos; el juego es de un solo hilo).
 *
 * Aristas: andar (WALK), caer a una plataforma inferior segura (DROP) y saltar (HOP: escalon de 1 celda o hueco de pinchos/vacio que el salto del
 * enemigo salva de verdad). Nunca se pasa por una celda con pinchos ni se aterriza sobre ellos. Si el jugador no es alcanzable se elige la celda
 * alcanzable mas cercana a el (normalmente el borde del peligro) y, si es la propia, el enemigo espera alli sin suicidarse.
 */
final class EnemyNav {
    private EnemyNav() {}

    static final int T_WALK = 0, T_DROP = 1, T_HOP = 2;
    private static final int HX = 40, HY = 10, W = 2 * HX + 1, H = 2 * HY + 1, N = W * H;
    private static final int INF = Integer.MAX_VALUE / 2;
    private static final int[] cost = new int[N], prev = new int[N], ptype = new int[N];
    private static final long[] heap = new long[N * 8];
    private static int heapN;

    // resultado del ultimo plan()
    static boolean ok;          // hay un primer paso util (false = quedarse donde esta)
    static int dir, type;       // direccion (+-1) y tipo del primer paso
    static int plans;           // contador (pruebas de rendimiento)

    static boolean hazard(int t) { return t == Room.SPIKE || t == Room.SPIKE_DOWN; }

    /** Celda de pie: suelo firme o plataforma debajo, y las `c` filas del cuerpo libres de bloques y pinchos. */
    static boolean stand(Room r, int tx, int ty, int c) {
        int below = r.tile(tx, ty + 1);
        if (!(Room.isSolid(below) || below == Room.ONEWAY)) return false;
        for (int k = 0; k < c; k++) {
            int t = r.tile(tx, ty - k);
            if (Room.isSolid(t) || hazard(t)) return false;
        }
        return true;
    }

    private static boolean open(Room r, int tx, int ty, int c) {     // el cuerpo cabe y no hay pinchos (en el aire tambien)
        for (int k = 0; k < c; k++) {
            int t = r.tile(tx, ty - k);
            if (Room.isSolid(t) || hazard(t)) return false;
        }
        return true;
    }

    private static boolean passable(Room r, int tx, int ty) { int t = r.tile(tx, ty); return !Room.isSolid(t) && !hazard(t); }

    private static void push(int c, int idx) {
        long k = ((long) c << 20) | idx;
        int i = heapN++;
        heap[i] = k;
        while (i > 0) { int p = (i - 1) >> 1; if (heap[p] <= heap[i]) break; long t = heap[p]; heap[p] = heap[i]; heap[i] = t; i = p; }
    }

    private static long pop() {
        long top = heap[0];
        heap[0] = heap[--heapN];
        int i = 0;
        while (true) {
            int l = 2 * i + 1, rr = l + 1, m = i;
            if (l < heapN && heap[l] < heap[m]) m = l;
            if (rr < heapN && heap[rr] < heap[m]) m = rr;
            if (m == i) break;
            long t = heap[m]; heap[m] = heap[i]; heap[i] = t; i = m;
        }
        return top;
    }

    /**
     * Planifica desde la celda (sx,sy) hacia el punto (px,py) en pixeles. c = filas del cuerpo, hop = puede saltar, maxGap = huecos (en celdas)
     * que su salto salva con seguridad. Deja el primer paso en ok/dir/type.
     */
    static void plan(Room r, int sx, int sy, int c, float px, float py, boolean hop, int maxGap) {
        plans++;
        ok = false;
        int ox = sx - HX, oy = sy - HY;
        for (int i = 0; i < N; i++) { cost[i] = INF; prev[i] = -1; }
        heapN = 0;
        int s0 = (sy - oy) * W + (sx - ox);
        cost[s0] = 0;
        push(0, s0);
        int best = s0;
        float bestScore = score(sx, sy, px, py);
        while (heapN > 0) {
            long k = pop();
            int idx = (int) (k & 0xFFFFF), cc = (int) (k >> 20);
            if (cc > cost[idx]) continue;
            int tx = ox + idx % W, ty = oy + idx / W;
            float sc = score(tx, ty, px, py) + cc * 0.05f;
            if (sc < bestScore) { bestScore = sc; best = idx; }
            for (int d = -1; d <= 1; d += 2) {
                int nx = tx + d;
                if (nx - ox < 0 || nx - ox >= W) continue;
                // andar
                if (stand(r, nx, ty, c)) relax(idx, cc + 1, nx - ox, ty - oy, T_WALK);
                else if (passable(r, nx, ty) && open(r, nx, ty, c)) {
                    // caer a una plataforma inferior segura
                    for (int ly = ty + 1; ly <= ty + 5; ly++) {
                        if (ly - oy >= H) break;
                        if (stand(r, nx, ly, c)) { relax(idx, cc + 2 + (ly - ty), nx - ox, ly - oy, T_DROP); break; }
                        if (!passable(r, nx, ly)) break;
                    }
                }
                if (!hop) continue;
                // escalon de una celda
                if (ty - 1 - oy >= 0 && stand(r, nx, ty - 1, c) && open(r, tx, ty - c, 1) && open(r, nx, ty - c, 1)) relax(idx, cc + 4, nx - ox, ty - 1 - oy, T_HOP);
                // hueco (pinchos o vacio) de g celdas que el salto salva
                for (int g = 1; g <= maxGap; g++) {
                    int lx = tx + d * (g + 1);
                    if (lx - ox < 0 || lx - ox >= W) break;
                    boolean clear = true;                                   // por encima de las celdas del hueco no hay bloques
                    for (int j = 1; j <= g && clear; j++) if (Room.isSolid(r.tile(tx + d * j, ty)) || Room.isSolid(r.tile(tx + d * j, ty - 1))) clear = false;
                    if (!clear) break;
                    if (stand(r, lx, ty, c)) { relax(idx, cc + 4 + 2 * g, lx - ox, ty - oy, T_HOP); break; }
                }
            }
        }
        if (best == s0) return;
        int cur = best;
        while (prev[cur] != s0) cur = prev[cur];
        dir = (ox + cur % W) > sx ? 1 : -1;
        type = ptype[cur];
        ok = true;
    }

    private static void relax(int from, int c, int lx, int ly, int t) {
        int idx = ly * W + lx;
        if (ly < 0 || ly >= H || c >= cost[idx]) return;
        cost[idx] = c; prev[idx] = from; ptype[idx] = t;
        push(c, idx);
    }

    private static float score(int tx, int ty, float px, float py) {
        return Math.abs(tx * Room.TS + 8 - px) + 2.5f * Math.abs((ty + 1) * Room.TS - py);
    }

    /**
     * Cuantas celdas de hueco (0..3) salva con seguridad un salto sobre suelo plano: simulacion con las mismas leyes de movimiento y los mismos
     * puntos de contacto que usan los pinchos (Level.trapDamage): por encima de 12 px de altura el cuerpo ya no toca una tira de pinchos.
     */
    static int maxGap(float bw, float bh, float hopVx, float vy0) {
        int best = 0;
        float hw = Math.max(2f, bw * 0.4f);
        for (int g = 1; g <= 3; g++) {
            float s0 = Room.TS, s1 = Room.TS + g * Room.TS;          // tira de g celdas justo despues de la celda de salida
            float x = HOP_U + 3f, y = 0, vy = vy0;     // +3 px: margen por si el salto se inicia un fotograma tarde
            boolean safe = true, landed = false;
            for (int i = 0; i < 120 && !landed; i++) {
                vy = Math.min(Level.FALL_MAX, vy + Level.GRAV / 60f);
                x += hopVx / 60f; y += vy / 60f;
                if (y >= 0 && vy > 0) { landed = true; if (x - hw <= s1) safe = false; break; }
                if (-y < 12f && x + hw > s0 && x - hw < s1) safe = false;   // cuerpo a menos de 12 px del suelo sobre los pinchos
            }
            if (safe && landed) best = g; else break;
        }
        return best;
    }

    /** Posicion (px dentro de la celda de salida, en el sentido del salto) a la que el enemigo inicia el salto. */
    static final float HOP_U = 2f;
}
