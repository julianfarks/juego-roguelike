package com.julianfarks.roguelike.core;

/** Sinergia: grupo de bendiciones que, al tener {@code need} o mas de sus miembros, activa reglas extra (ver BlessData / tools/blessings/catalog.py). */
public final class BSyn {
    public final int id;
    public final String name, desc, hint;
    public final int need;
    public final int[] members;
    final BRule[] rules;
    BSyn(int id, String name, String desc, String hint, int need, int[] members, BRule[] rules) {
        this.id = id; this.name = name; this.desc = desc; this.hint = hint; this.need = need; this.members = members; this.rules = rules;
    }
}
