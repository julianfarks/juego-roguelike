package com.julianfarks.roguelike.core;

/**
 * Alto de la pantalla virtual EN USO. Vale {@link Platform#VIEW_H} (270) salvo en PC cuando el monitor es mas "alto" que 16:9
 * (16:10, 3:2...) o cuando un multiplo entero del tamano permite rellenar toda la pantalla: entonces la plataforma pide
 * una pantalla virtual un poco mas alta (hasta {@link #MAX}) para no dejar franjas negras. Android nunca lo cambia.
 */
public final class ViewSize {
    private ViewSize() { }
    public static final int BASE = 270;     // = Platform.VIEW_H
    /** Las salas mas bajas miden 20 baldosas = 320 px: mas alto que eso dejaria ver fuera de la sala. */
    public static final int MAX = 320;
    public static volatile int h = BASE;

    public static int clamp(int v) { return Math.max(BASE, Math.min(MAX, v)); }
}
