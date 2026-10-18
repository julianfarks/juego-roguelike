package com.julianfarks.roguelike.core;

/** Generador pseudoaleatorio rapido (xorshift64*) con utilidades. */
public final class Rng {
    private long s;

    public Rng(long seed) { s = seed * 0x9E3779B97F4A7C15L + 0x1234567L; if (s == 0) s = 88172645463325252L; next(); next(); }

    public long next() {
        s ^= s >>> 12; s ^= s << 25; s ^= s >>> 27;
        return s * 0x2545F4914F6CDD1DL;
    }

    /** [0,n) */
    public int i(int n) { return n <= 0 ? 0 : (int) ((next() >>> 33) % n); }
    /** [a,b] inclusive */
    public int range(int a, int b) { return a + i(b - a + 1); }
    /** [0,1) */
    public float f() { return (next() >>> 40) / (float) (1L << 24); }
    public float f(float a, float b) { return a + (b - a) * f(); }
    public boolean chance(float p) { return f() < p; }
    public <T> T pick(java.util.List<T> l) { return l.get(i(l.size())); }
    public <T> T pick(T[] a) { return a[i(a.length)]; }
    public float sign() { return (next() & 1) == 0 ? -1f : 1f; }
}
