package com.julianfarks.roguelike.core;

/** Animacion de una hoja de sprites (una fila). */
public final class Anim {
    public static final Anim NONE = new Anim("none", 0, 1, 1f, true);
    public final String name;
    public final int row, n;
    public final float fps;
    public final boolean loop;
    public int h0 = -1, h1 = -1;       // fotogramas de golpe (inclusive); -1 = sin golpe
    public int[] box;                   // [x,y,w,h] relativo al pivote mirando a la derecha
    public int rel = -1;                // fotograma de liberacion
    public int[] muzzle;                // [x,y] relativo al pivote
    public int smear = -1;              // indice del fotograma smear (deformacion intencional de velocidad); -1 = ninguno
    private float[] cum;                // tiempos acumulados por fotograma (peso de duracion "ft"); null = fotogramas uniformes

    /** Peso de duracion por fotograma (anticipacion lenta, golpe rapido, recuperacion con peso). Duracion total = suma / fps. */
    public void setWeights(float[] w) {
        if (w == null || w.length != n) { cum = null; return; }
        cum = new float[n + 1];
        for (int i = 0; i < n; i++) cum[i + 1] = cum[i] + Math.max(0.1f, w[i]) / fps;
    }

    public Anim(String name, int row, int n, float fps, boolean loop) {
        this.name = name; this.row = row; this.n = Math.max(1, n); this.fps = Math.max(0.1f, fps); this.loop = loop;
    }

    public float duration() { return cum != null ? cum[n] : n / fps; }

    public int frameAt(float t) {
        if (cum != null) {
            if (t < 0) t = 0;
            if (loop) t %= cum[n];
            int i = 0;
            while (i < n - 1 && t >= cum[i + 1]) i++;
            return i;
        }
        int f = (int) (t * fps);
        if (f < 0) f = 0;
        return loop ? f % n : Math.min(f, n - 1);
    }

    public boolean done(float t) { return !loop && (cum != null ? t >= cum[n] : t * fps >= n); }

    public boolean hitActive(float t) {
        if (h0 < 0) return false;
        int f = frameAt(t);
        return f >= h0 && f <= h1;
    }

    /** Escribe en out [x,y,w,h] la caja de golpe en coordenadas de mundo. px,py = pivote del cuerpo. */
    public boolean worldBox(float px, float py, boolean right, float[] out) {
        if (box == null) return false;
        out[0] = right ? px + box[0] : px - box[0] - box[2];
        out[1] = py + box[1];
        out[2] = box[2];
        out[3] = box[3];
        return true;
    }

    public float muzzleX(float px, boolean right) {
        if (muzzle == null) return px + (right ? 12 : -12);
        return right ? px + muzzle[0] : px - muzzle[0];
    }

    public float muzzleY(float py) { return muzzle == null ? py - 16 : py + muzzle[1]; }
}
