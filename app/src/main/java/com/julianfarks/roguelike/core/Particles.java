package com.julianfarks.roguelike.core;

/** Sistema de particulas simple con arreglos planos. */
public final class Particles {
    private static final int MAX = 700;
    private final float[] x = new float[MAX], y = new float[MAX], vx = new float[MAX], vy = new float[MAX];
    private final float[] life = new float[MAX], maxLife = new float[MAX], size = new float[MAX], grav = new float[MAX];
    private final int[] color = new int[MAX];
    private final boolean[] add = new boolean[MAX];
    private int n;

    public void clear() { n = 0; }
    public int count() { return n; }

    public void spawn(float px, float py, float pvx, float pvy, float l, float s, float g, int c, boolean additive) {
        int i;
        if (n < MAX) i = n++;
        else i = (int) (Math.random() * MAX);
        x[i] = px; y[i] = py; vx[i] = pvx; vy[i] = pvy; life[i] = l; maxLife[i] = l; size[i] = s; grav[i] = g; color[i] = c; add[i] = additive;
    }

    /** Chorro radial de chispas. */
    public void burst(Rng r, float px, float py, int c, int count, float speed, float l, float s, float g, boolean additive) {
        for (int k = 0; k < count; k++) {
            float a = r.f() * 6.2831f, sp = speed * (0.35f + r.f() * 0.65f);
            spawn(px, py, (float) Math.cos(a) * sp, (float) Math.sin(a) * sp, l * (0.6f + r.f() * 0.6f), s * (0.7f + r.f() * 0.6f), g, c, additive);
        }
    }

    public void update(float dt) {
        for (int i = 0; i < n; ) {
            life[i] -= dt;
            if (life[i] <= 0) {
                n--;
                x[i] = x[n]; y[i] = y[n]; vx[i] = vx[n]; vy[i] = vy[n]; life[i] = life[n]; maxLife[i] = maxLife[n]; size[i] = size[n];
                grav[i] = grav[n]; color[i] = color[n]; add[i] = add[n];
                continue;
            }
            vy[i] += grav[i] * dt;
            vx[i] *= 1f - 1.5f * dt;
            x[i] += vx[i] * dt;
            y[i] += vy[i] * dt;
            i++;
        }
    }

    public void render(Platform.Gfx g, float camX, float camY) {
        for (int i = 0; i < n; i++) {
            float t = life[i] / maxLife[i];
            float s = Math.max(1f, size[i] * (0.4f + 0.6f * t));
            int a = (int) (255 * Math.min(1f, t * 1.6f));
            g.rect(Math.round(x[i] - camX - s / 2), Math.round(y[i] - camY - s / 2), Math.round(s), Math.round(s), Mth.withAlpha(color[i], a), add[i]);
        }
    }
}
