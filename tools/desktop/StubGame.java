package desktop;

import com.julianfarks.roguelike.core.Platform;

/**
 * Juego de prueba del banco de escritorio (NO forma parte del motor).
 * Dibuja una tarjeta de pruebas de Gfx (FLIP_X, ADD, TINT, FLASH, alpha, rotacion, clip, transform), un sprite real de
 * assets/sprites si existe, y reacciona a teclas/toques. Tecla Q lanza una excepcion; SPACE dispara sfx; ENTER musica.
 */
public final class StubGame implements Platform.GameLoop {
    private Platform p;
    private int viewW = 576;
    private int frame;
    private float px = 40, py = 230;
    private boolean left, right, up, down;
    private final float[] tx = new float[8], ty = new float[8];
    private final boolean[] td = new boolean[8];
    private Platform.Img test, glow, sprite, missing;
    private int spriteW, spriteH;

    @Override
    public void init(Platform p) {
        this.p = p;
        // sprite sintetico asimetrico 24x24: disco naranja con borde oscuro y una "F" blanca (para ver el espejo)
        int n = 24;
        int[] pix = new int[n * n];
        for (int y = 0; y < n; y++)
            for (int x = 0; x < n; x++) {
                float dx = x - 11.5f, dy = y - 11.5f, d = (float) Math.sqrt(dx * dx + dy * dy);
                int c = 0;
                if (d < 11.5f) c = d > 9.5f ? 0xFF402010 : 0xFFFF9030 - ((int) (d * 4) << 8);
                boolean f = (x == 8 && y >= 6 && y <= 17) || (y == 6 && x >= 8 && x <= 15) || (y == 11 && x >= 8 && x <= 13);
                if (f && c != 0) c = 0xFFFFFFFF;
                pix[y * n + x] = c;
            }
        test = p.createImage(n, n, pix);
        int[] gp = new int[32 * 32];
        for (int y = 0; y < 32; y++)
            for (int x = 0; x < 32; x++) {
                float dx = x - 15.5f, dy = y - 15.5f, d = (float) Math.sqrt(dx * dx + dy * dy) / 15.5f;
                int a = d >= 1 ? 0 : (int) ((1 - d) * (1 - d) * 255);
                gp[y * 32 + x] = (a << 24) | 0x4080FF;
            }
        glow = p.createImage(32, 32, gp);
        // busca un PNG real en assets/sprites
        String[] names = p.list("sprites");
        for (String s : names) {
            if (s.endsWith(".png")) {
                sprite = p.loadImage("sprites/" + s);
                if (sprite != null) { spriteW = sprite.w; spriteH = sprite.h; break; }
            }
        }
        missing = p.loadImage("sprites/no_existe_este.png"); // debe quedar registrado como MISSING asset
        p.audio().music("tema_inexistente", true, 0.8f, 500);
        p.log("StubGame.init ok; pixels[0]=" + Integer.toHexString(p.pixels(test)[11 * 24 + 11]));
    }

    @Override public void resize(int viewW) { this.viewW = viewW; }

    @Override
    public void update(float dt) {
        frame++;
        float s = 2f;
        if (left) px -= s;
        if (right) px += s;
        if (up) py -= s;
        if (down) py += s;
    }

    private void label(Platform.Gfx g, float x, float y) {
        g.rect(x, y, 3, 3, 0xFFFFFFFF, false);
    }

    @Override
    public void render(Platform.Gfx g) {
        g.clear(0xFF182030);
        // fondo con franjas de color para ver bien ADD / TINT / alpha
        for (int i = 0; i < 12; i++) {
            int c = 0xFF000000 | ((40 + i * 12) << 16) | ((80 + (i % 3) * 30) << 8) | (120 - i * 6);
            g.rect(i * (viewW / 12f), 0, viewW / 12f + 1, 140, c, false);
        }
        float x0 = 12, y0 = 12, dx = 46;
        int f = Platform.FLIP_X;
        g.image(test, 0, 0, 24, 24, x0 + dx * 0, y0, 24, 24, 0, 0, 1f);                          // normal
        g.image(test, 0, 0, 24, 24, x0 + dx * 1, y0, 24, 24, f, 0, 1f);                          // FLIP_X
        g.image(test, 0, 0, 24, 24, x0 + dx * 2, y0, 24, 24, Platform.TINT, 0xFFFF2020, 1f);     // TINT rojo
        g.image(test, 0, 0, 24, 24, x0 + dx * 3, y0, 24, 24, Platform.TINT, 0xFF40FF40, 1f);     // TINT verde
        g.image(test, 0, 0, 24, 24, x0 + dx * 4, y0, 24, 24, Platform.FLASH, 0xFFFFFFFF, 1f);    // FLASH blanco
        g.image(test, 0, 0, 24, 24, x0 + dx * 5, y0, 24, 24, Platform.FLASH, 0xFFFF0000, 1f);    // FLASH rojo
        g.image(test, 0, 0, 24, 24, x0 + dx * 6, y0, 24, 24, Platform.ADD, 0, 1f);               // ADD
        g.image(test, 0, 0, 24, 24, x0 + dx * 7, y0, 24, 24, 0, 0, 0.5f);                        // alpha .5
        g.imageRot(test, 0, 0, 24, 24, x0 + dx * 8, y0, 24, 24, (float) Math.PI / 4, 0, 0, 1f);  // rotacion 45
        g.imageRot(test, 0, 0, 24, 24, x0 + dx * 9, y0, 24, 24, frame * 0.05f, f | Platform.TINT, 0xFFFFC040, 1f);
        g.image(test, 0, 0, 24, 24, x0 + dx * 10, y0, 48, 48, 0, 0, 1f);                        // escala x2
        g.image(test, 4, 4, 12, 12, x0 + dx * 12 - 24, y0, 36, 36, 0, 0, 1f);                    // recorte
        // fila 2: glows aditivos solapados (deben sumar) + formas
        float y1 = 70;
        g.image(glow, 0, 0, 32, 32, 30, y1, 64, 64, Platform.ADD, 0, 1f);
        g.image(glow, 0, 0, 32, 32, 60, y1, 64, 64, Platform.ADD, 0, 1f);
        g.image(glow, 0, 0, 32, 32, 90, y1, 64, 64, Platform.ADD | Platform.TINT, 0xFFFF8040, 1f);
        g.rect(200, y1, 40, 30, 0x80FF0000, false);
        g.rect(220, y1 + 10, 40, 30, 0x8000FF00, true);
        g.line(280, y1, 340, y1 + 40, 3, 0xFFFFFF00, false);
        g.line(280, y1 + 40, 340, y1, 1, 0xFFFFFFFF, true);
        g.circle(380, y1 + 20, 16, 0xC0FF40FF, false);
        g.circle(395, y1 + 20, 16, 0xC040FFFF, true);
        // clip + transform anidados
        g.clipBegin(430, y1, 50, 40);
        g.pushTransform(430, y1, 2f);
        g.image(test, 0, 0, 24, 24, 4, 2, 24, 24, 0, 0, 1f);
        g.popTransform();
        g.clipEnd();
        g.rect(430, y1 + 44, 50, 2, 0xFFFFFFFF, false); // fuera del clip: debe verse completo
        g.pushTransform(500, y1, 0.5f);
        g.image(test, 0, 0, 24, 24, 0, 0, 24, 24, 0, 0, 1f);
        g.popTransform();
        // sprite real si hay
        if (sprite != null) {
            int fw = Math.min(spriteW, 64), fh = Math.min(spriteH, 64);
            g.image(sprite, 0, 0, fw, fh, 20, 150, fw, fh, 0, 0, 1f);
            g.image(sprite, 0, 0, fw, fh, 100, 150, fw, fh, f, 0, 1f);
            g.image(sprite, 0, 0, fw, fh, 180, 150, fw, fh, Platform.FLASH, 0xFFFFFFFF, 1f);
            g.image(sprite, 0, 0, fw, fh, 260, 150, fw, fh, Platform.TINT, 0xFFFF6060, 1f);
            g.image(sprite, 0, 0, fw, fh, 340, 150, fw, fh, Platform.ADD, 0, 1f);
        }
        // jugador (flechas) y toques
        g.rect(px - 6, py - 6, 12, 12, 0xFFFFFFFF, false);
        for (int i = 0; i < 8; i++) if (td[i]) g.circle(tx[i], ty[i], 14, 0xAA40FF80, false);
        // contador de frames en barritas
        for (int i = 0; i < (frame % 60); i++) g.rect(viewW - 62 + i, 262, 1, 6, 0xFFFFFFFF, false);
    }

    @Override
    public void touch(int id, int action, float x, float y) {
        if (id < 0 || id >= 8) return;
        td[id] = action != Platform.ACTION_UP;
        tx[id] = x;
        ty[id] = y;
        if (action == Platform.ACTION_DOWN) p.audio().sfx("golpe_prueba", 1f, 1f, 0f);
    }

    @Override
    public void key(int code, boolean d) {
        switch (code) {
            case 37: left = d; break;
            case 39: right = d; break;
            case 38: up = d; break;
            case 40: down = d; break;
            case 32: if (d) p.audio().sfx("golpe_prueba", 1f, 1.2f, -0.5f); break;
            case 10: if (d) p.audio().music("tema_inexistente", true, 1f, 300); break;
            case 'Q': if (d) throw new RuntimeException("stub boom (tecla Q)"); break;
            default: break;
        }
    }

    @Override public boolean back() { return false; }
    @Override public void pause() { }
    @Override public void resume() { }
}
