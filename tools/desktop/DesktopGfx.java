package desktop;

import com.julianfarks.roguelike.core.Platform;

import java.awt.AlphaComposite;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Composite;
import java.awt.CompositeContext;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.Shape;
import java.awt.geom.AffineTransform;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Line2D;
import java.awt.geom.Rectangle2D;
import java.awt.image.BufferedImage;
import java.awt.image.ColorModel;
import java.awt.image.Raster;
import java.awt.image.WritableRaster;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.IdentityHashMap;

/** Platform.Gfx sobre Graphics2D (vecino mas cercano, sin antialias). */
public final class DesktopGfx implements Platform.Gfx {
    private BufferedImage screen;
    private Graphics2D g;
    private final ArrayList<Object[]> stack = new ArrayList<Object[]>(); // {AffineTransform, Shape}
    private final Rectangle2D.Float rectS = new Rectangle2D.Float();
    private final Ellipse2D.Float ellS = new Ellipse2D.Float();
    private final Line2D.Float lineS = new Line2D.Float();
    private float strokeW = -1;
    private BasicStroke stroke;

    private final IdentityHashMap<BufferedImage, HashMap<Long, BufferedImage>> derived =
            new IdentityHashMap<BufferedImage, HashMap<Long, BufferedImage>>();
    private int derivedCount;

    public void bind(BufferedImage img) {
        if (g != null) g.dispose();
        screen = img;
        g = img.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_NEAREST_NEIGHBOR);
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_OFF);
        g.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_SPEED);
        g.setRenderingHint(RenderingHints.KEY_STROKE_CONTROL, RenderingHints.VALUE_STROKE_PURE);
        stack.clear();
    }

    // ------------------------------------------------------------------ composite aditivo
    /** dst + src*alpha, saturado a 255 (equivalente a PorterDuff.ADD de Android). */
    static final class AddComposite implements Composite {
        final float alpha;
        AddComposite(float alpha) { this.alpha = alpha; }

        @Override
        public CompositeContext createContext(final ColorModel srcCM, ColorModel dstCM, RenderingHints hints) {
            return new CompositeContext() {
                @Override public void dispose() { }
                @Override
                public void compose(Raster src, Raster dstIn, WritableRaster dstOut) {
                    int w = Math.min(src.getWidth(), dstIn.getWidth());
                    int h = Math.min(src.getHeight(), dstIn.getHeight());
                    int sb = src.getNumBands(), db = dstIn.getNumBands();
                    boolean sAlpha = srcCM.hasAlpha() && sb >= 4;
                    boolean sPre = srcCM.isAlphaPremultiplied();
                    int[] sp = new int[sb * w];
                    int[] dp = new int[db * w];
                    for (int y = 0; y < h; y++) {
                        src.getPixels(src.getMinX(), src.getMinY() + y, w, 1, sp);
                        dstIn.getPixels(dstIn.getMinX(), dstIn.getMinY() + y, w, 1, dp);
                        for (int x = 0; x < w; x++) {
                            float k = alpha;
                            if (sAlpha && !sPre) k *= sp[x * sb + 3] / 255f;
                            int nc = Math.min(3, Math.min(sb, db));
                            for (int b = 0; b < nc; b++) {
                                int v = dp[x * db + b] + (int) (sp[x * sb + b] * k + 0.5f);
                                dp[x * db + b] = v > 255 ? 255 : v;
                            }
                        }
                        dstOut.setPixels(dstOut.getMinX(), dstOut.getMinY() + y, w, 1, dp);
                    }
                }
            };
        }
    }

    private void setComposite(boolean add, float alpha) {
        if (alpha > 1f) alpha = 1f;
        if (alpha < 0f) alpha = 0f;
        g.setComposite(add ? new AddComposite(alpha) : AlphaComposite.getInstance(AlphaComposite.SRC_OVER, alpha));
    }

    // ------------------------------------------------------------------ imagenes derivadas (TINT / FLASH)
    private BufferedImage derive(BufferedImage src, int color, boolean flash) {
        long key = (color & 0xFFFFFFL) | (flash ? (1L << 32) : 0L);
        HashMap<Long, BufferedImage> m = derived.get(src);
        if (m == null) {
            m = new HashMap<Long, BufferedImage>();
            derived.put(src, m);
        }
        BufferedImage out = m.get(key);
        if (out != null) return out;
        if (derivedCount > 600) {
            derived.clear();
            derivedCount = 0;
            m = new HashMap<Long, BufferedImage>();
            derived.put(src, m);
        }
        int w = src.getWidth(), h = src.getHeight();
        int tr = (color >> 16) & 255, tg = (color >> 8) & 255, tb = color & 255;
        out = new BufferedImage(w, h, BufferedImage.TYPE_INT_ARGB);
        int[] px = src.getRGB(0, 0, w, h, null, 0, w);
        for (int i = 0; i < px.length; i++) {
            int p = px[i];
            int a = p >>> 24;
            if (flash) {
                px[i] = (a << 24) | (tr << 16) | (tg << 8) | tb;
            } else {
                int r = (((p >> 16) & 255) * tr + 127) / 255;
                int gg = (((p >> 8) & 255) * tg + 127) / 255;
                int b = ((p & 255) * tb + 127) / 255;
                px[i] = (a << 24) | (r << 16) | (gg << 8) | b;
            }
        }
        out.setRGB(0, 0, w, h, px, 0, w);
        m.put(key, out);
        derivedCount++;
        return out;
    }

    private BufferedImage prepare(Platform.Img img, int flags, int tint) {
        BufferedImage b = (BufferedImage) img.handle;
        if ((flags & Platform.FLASH) != 0) return derive(b, tint, true);
        if ((flags & Platform.TINT) != 0) return derive(b, tint, false);
        return b;
    }

    // ------------------------------------------------------------------ Gfx
    @Override
    public void clear(int argb) {
        AffineTransform t = g.getTransform();
        Shape c = g.getClip();
        g.setTransform(new AffineTransform());
        g.setClip(null);
        g.setComposite(AlphaComposite.Src);
        g.setColor(new Color(argb | 0xFF000000, true));
        g.fillRect(0, 0, screen.getWidth(), screen.getHeight());
        g.setTransform(t);
        g.setClip(c);
    }

    @Override
    public void image(Platform.Img img, int sx, int sy, int sw, int sh,
                      float dx, float dy, float dw, float dh, int flags, int tint, float alpha) {
        if (img == null || sw <= 0 || sh <= 0 || alpha <= 0f) return;
        BufferedImage b = prepare(img, flags, tint);
        // recorta el origen a los limites de la imagen (ajustando el destino proporcionalmente)
        int x0 = Math.max(sx, 0), y0 = Math.max(sy, 0);
        int x1 = Math.min(sx + sw, b.getWidth()), y1 = Math.min(sy + sh, b.getHeight());
        if (x1 <= x0 || y1 <= y0) return;
        float fx = dw / sw, fy = dh / sh;
        dx += (x0 - sx) * fx;
        dy += (y0 - sy) * fy;
        dw = (x1 - x0) * fx;
        dh = (y1 - y0) * fy;
        BufferedImage sub = b.getSubimage(x0, y0, x1 - x0, y1 - y0);
        AffineTransform at = new AffineTransform();
        if ((flags & Platform.FLIP_X) != 0) {
            at.translate(dx + dw, dy);
            at.scale(-dw / sub.getWidth(), dh / sub.getHeight());
        } else {
            at.translate(dx, dy);
            at.scale(dw / sub.getWidth(), dh / sub.getHeight());
        }
        setComposite((flags & Platform.ADD) != 0, alpha);
        g.drawImage(sub, at, null);
    }

    @Override
    public void imageRot(Platform.Img img, int sx, int sy, int sw, int sh,
                         float dx, float dy, float dw, float dh, float angle, int flags, int tint, float alpha) {
        if (img == null || sw <= 0 || sh <= 0 || alpha <= 0f) return;
        BufferedImage b = prepare(img, flags, tint);
        if (sx < 0 || sy < 0 || sx + sw > b.getWidth() || sy + sh > b.getHeight()) return;
        BufferedImage sub = b.getSubimage(sx, sy, sw, sh);
        AffineTransform at = new AffineTransform();
        at.translate(dx + dw * 0.5, dy + dh * 0.5);
        at.rotate(angle);
        if ((flags & Platform.FLIP_X) != 0) at.scale(-1, 1);
        at.translate(-dw * 0.5, -dh * 0.5);
        at.scale(dw / sw, dh / sh);
        setComposite((flags & Platform.ADD) != 0, alpha);
        g.drawImage(sub, at, null);
    }

    @Override
    public void rect(float x, float y, float w, float h, int argb, boolean add) {
        setComposite(add, 1f);
        g.setColor(new Color(argb, true));
        rectS.setRect(x, y, w, h);
        g.fill(rectS);
    }

    @Override
    public void line(float x1, float y1, float x2, float y2, float thick, int argb, boolean add) {
        setComposite(add, 1f);
        g.setColor(new Color(argb, true));
        if (stroke == null || strokeW != thick) {
            stroke = new BasicStroke(thick, BasicStroke.CAP_BUTT, BasicStroke.JOIN_MITER);
            strokeW = thick;
        }
        g.setStroke(stroke);
        lineS.setLine(x1, y1, x2, y2);
        g.draw(lineS);
    }

    @Override
    public void circle(float cx, float cy, float r, int argb, boolean add) {
        setComposite(add, 1f);
        g.setColor(new Color(argb, true));
        ellS.setFrame(cx - r, cy - r, 2 * r, 2 * r);
        g.fill(ellS);
    }

    private void push() {
        stack.add(new Object[]{g.getTransform(), g.getClip()});
    }

    private void pop() {
        if (stack.isEmpty()) return;
        Object[] s = stack.remove(stack.size() - 1);
        g.setTransform((AffineTransform) s[0]);
        g.setClip((Shape) s[1]);
    }

    @Override
    public void clipBegin(float x, float y, float w, float h) {
        push();
        g.clip(new Rectangle2D.Float(x, y, w, h));
    }

    @Override public void clipEnd() { pop(); }

    @Override
    public void pushTransform(float tx, float ty, float scale) {
        push();
        g.translate(tx, ty);
        g.scale(scale, scale);
    }

    @Override public void popTransform() { pop(); }
}
