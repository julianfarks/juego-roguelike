package com.julianfarks.roguelike.android;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.PorterDuff;
import android.graphics.PorterDuffColorFilter;
import android.graphics.PorterDuffXfermode;
import android.graphics.Rect;
import android.graphics.RectF;

import com.julianfarks.roguelike.core.Platform;

/**
 * Implementacion de Platform.Gfx sobre android.graphics.Canvas. Se dibuja en un Bitmap offscreen
 * (viewW x 270) cuyo Canvas se enlaza con {@link #bind(Canvas)} en cada frame. Sin asignaciones en el camino caliente.
 * Solo se usa desde el hilo de juego.
 */
public final class AndroidGfx implements Platform.Gfx {
    private static final int CACHE = 64; // filtros de color en cache (mapeo directo por hash del color)
    private static final float RAD2DEG = 57.29577951308232f;

    private Canvas canvas;

    private final Paint imgPaint = new Paint();
    private final Paint fillPaint = new Paint();
    private final Rect src = new Rect();
    private final RectF dst = new RectF();
    private final PorterDuffXfermode addMode = new PorterDuffXfermode(PorterDuff.Mode.ADD);

    private final int[] tintKeys = new int[CACHE];
    private final PorterDuffColorFilter[] tintFilters = new PorterDuffColorFilter[CACHE];
    private final int[] flashKeys = new int[CACHE];
    private final PorterDuffColorFilter[] flashFilters = new PorterDuffColorFilter[CACHE];

    public AndroidGfx() {
        imgPaint.setAntiAlias(false);
        imgPaint.setFilterBitmap(false);
        imgPaint.setDither(false);
        fillPaint.setAntiAlias(false);
        fillPaint.setFilterBitmap(false);
        fillPaint.setDither(false);
        fillPaint.setStyle(Paint.Style.FILL);
        fillPaint.setStrokeCap(Paint.Cap.BUTT);
    }

    /** Enlaza el canvas del bitmap offscreen para este frame y limpia pilas de save/restore desbalanceadas. */
    public void bind(Canvas c) {
        canvas = c;
        if (c != null) c.restoreToCount(1);
    }

    private static int alphaByte(float a) {
        int v = (int) (a * 255f + 0.5f);
        return v < 0 ? 0 : (v > 255 ? 255 : v);
    }

    private PorterDuffColorFilter tintFilter(int rgb) {
        int key = rgb | 0xFF000000;
        int slot = (key ^ (key >>> 11) ^ (key >>> 19)) & (CACHE - 1);
        PorterDuffColorFilter f = tintFilters[slot];
        if (f == null || tintKeys[slot] != key) {
            f = new PorterDuffColorFilter(key, PorterDuff.Mode.MULTIPLY);
            tintFilters[slot] = f;
            tintKeys[slot] = key;
        }
        return f;
    }

    private PorterDuffColorFilter flashFilter(int rgb) {
        int key = rgb | 0xFF000000;
        int slot = (key ^ (key >>> 11) ^ (key >>> 19)) & (CACHE - 1);
        PorterDuffColorFilter f = flashFilters[slot];
        if (f == null || flashKeys[slot] != key) {
            f = new PorterDuffColorFilter(key, PorterDuff.Mode.SRC_IN);
            flashFilters[slot] = f;
            flashKeys[slot] = key;
        }
        return f;
    }

    /** Configura imgPaint segun banderas; devuelve false si no hay nada que dibujar. */
    private boolean setupImagePaint(int flags, int tint, float alpha) {
        int a = alphaByte(alpha);
        if (a == 0) return false;
        imgPaint.setAlpha(a);
        imgPaint.setXfermode((flags & Platform.ADD) != 0 ? addMode : null);
        if ((flags & Platform.FLASH) != 0) {
            imgPaint.setColorFilter(flashFilter(tint));
        } else if ((flags & Platform.TINT) != 0) {
            imgPaint.setColorFilter(tintFilter(tint));
        } else {
            imgPaint.setColorFilter(null);
        }
        return true;
    }

    private static Bitmap bitmapOf(Platform.Img img) {
        if (img == null) return null;
        Object h = img.handle;
        if (!(h instanceof Bitmap)) return null;
        Bitmap b = (Bitmap) h;
        return b.isRecycled() ? null : b;
    }

    @Override
    public void clear(int argb) {
        if (canvas == null) return;
        canvas.drawColor(argb | 0xFF000000, PorterDuff.Mode.SRC);
    }

    @Override
    public void image(Platform.Img img, int sx, int sy, int sw, int sh,
                      float dx, float dy, float dw, float dh, int flags, int tint, float alpha) {
        Bitmap b = bitmapOf(img);
        Canvas c = canvas;
        if (b == null || c == null || sw <= 0 || sh <= 0) return;
        if (!setupImagePaint(flags, tint, alpha)) return;
        src.set(sx, sy, sx + sw, sy + sh);
        if ((flags & Platform.FLIP_X) != 0) {
            c.save();
            c.translate(dx + dw, dy);
            c.scale(-1f, 1f);
            dst.set(0f, 0f, dw, dh);
            c.drawBitmap(b, src, dst, imgPaint);
            c.restore();
        } else {
            dst.set(dx, dy, dx + dw, dy + dh);
            c.drawBitmap(b, src, dst, imgPaint);
        }
    }

    @Override
    public void imageRot(Platform.Img img, int sx, int sy, int sw, int sh,
                         float dx, float dy, float dw, float dh, float angle, int flags, int tint, float alpha) {
        Bitmap b = bitmapOf(img);
        Canvas c = canvas;
        if (b == null || c == null || sw <= 0 || sh <= 0) return;
        if (!setupImagePaint(flags, tint, alpha)) return;
        src.set(sx, sy, sx + sw, sy + sh);
        c.save();
        c.translate(dx + dw * 0.5f, dy + dh * 0.5f);
        c.rotate(angle * RAD2DEG); // positivo = sentido horario en pantalla
        if ((flags & Platform.FLIP_X) != 0) c.scale(-1f, 1f);
        dst.set(-dw * 0.5f, -dh * 0.5f, dw * 0.5f, dh * 0.5f);
        c.drawBitmap(b, src, dst, imgPaint);
        c.restore();
    }

    private void setupFill(int argb, boolean add) {
        fillPaint.setColor(argb);
        fillPaint.setXfermode(add ? addMode : null);
    }

    @Override
    public void rect(float x, float y, float w, float h, int argb, boolean add) {
        Canvas c = canvas;
        if (c == null) return;
        setupFill(argb, add);
        c.drawRect(x, y, x + w, y + h, fillPaint);
    }

    @Override
    public void line(float x1, float y1, float x2, float y2, float thick, int argb, boolean add) {
        Canvas c = canvas;
        if (c == null) return;
        setupFill(argb, add);
        fillPaint.setStrokeWidth(thick);
        c.drawLine(x1, y1, x2, y2, fillPaint);
    }

    @Override
    public void circle(float cx, float cy, float r, int argb, boolean add) {
        Canvas c = canvas;
        if (c == null) return;
        setupFill(argb, add);
        c.drawCircle(cx, cy, r, fillPaint);
    }

    @Override
    public void clipBegin(float x, float y, float w, float h) {
        Canvas c = canvas;
        if (c == null) return;
        c.save();
        c.clipRect(x, y, x + w, y + h);
    }

    @Override
    public void clipEnd() {
        Canvas c = canvas;
        if (c == null) return;
        if (c.getSaveCount() > 1) c.restore();
    }

    @Override
    public void pushTransform(float tx, float ty, float scale) {
        Canvas c = canvas;
        if (c == null) return;
        c.save();
        c.translate(tx, ty);
        c.scale(scale, scale);
    }

    @Override
    public void popTransform() {
        Canvas c = canvas;
        if (c == null) return;
        if (c.getSaveCount() > 1) c.restore();
    }
}
