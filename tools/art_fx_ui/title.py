"""Capas de la pantalla de título (ciudad gótica victoriana bajo luna roja)."""
from common import *

W, H = 512, 288
GROUND = 240


class Cv:
    def __init__(s):
        s.im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        s.d = ImageDraw.Draw(s.im)
        s.glow = np.zeros((H, W, 3))

    def poly(s, pts, col):
        xs = [p[0] for p in pts]
        for dx in (-W, 0, W):
            if max(xs) + dx < -2 or min(xs) + dx > W + 2:
                continue
            s.d.polygon([(x + dx, y) for x, y in pts], fill=col)

    def rect(s, x0, y0, x1, y1, col):
        s.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], col)

    def ell(s, cx, cy, rx, ry, col):
        for dx in (-W, 0, W):
            s.d.ellipse([cx - rx + dx, cy - ry, cx + rx + dx, cy + ry], fill=col)

    def line(s, p0, p1, col, w=1):
        for dx in (-W, 0, W):
            s.d.line([(p0[0] + dx, p0[1]), (p1[0] + dx, p1[1])], fill=col, width=w)

    def lines(s, pts, col, w=1):
        for a, b in zip(pts[:-1], pts[1:]):
            s.line(a, b, col, w)

    def px(s, x, y, col):
        for dx in (-W, 0, W):
            xx = int(x + dx)
            if 0 <= xx < W and 0 <= y < H:
                s.im.putpixel((xx, int(y)), col)

    def light(s, cx, cy, r, col, inten=1.0):
        for dx in (-W, 0, W):
            x0, x1 = int(cx + dx - r * 3), int(cx + dx + r * 3)
            if x1 < 0 or x0 >= W:
                continue
            ys, xs = np.mgrid[max(0, int(cy - r * 3)):min(H, int(cy + r * 3)), max(0, x0):min(W, x1)]
            dd = np.hypot(xs - cx - dx, ys - cy)
            v = np.exp(-(dd / r) ** 2) * inten
            for c in range(3):
                s.glow[ys, xs, c] += v * col[c]

    def arr(s):
        return np.array(s.im).astype(float)


def hsh(a, b=0):
    return ((a * 73856093) ^ (b * 19349663)) % 1000 / 1000.0


def finish_layer(cv, rim=(176, 54, 66), rim_amt=1.0, glow_gain=1.0):
    a = cv.arr()
    alpha = a[..., 3] > 128
    # luz de rebote en bordes superiores
    top = alpha & ~np.roll(alpha, 1, 0)
    top[0] = alpha[0]
    a[top, :3] = a[top, :3] * (1 - 0.7 * rim_amt) + np.array(rim) * 0.7 * rim_amt
    # resplandor de ventanas/lámparas (pantalla)
    g = ndi.gaussian_filter(cv.glow, (3.2, 3.2, 0)) * glow_gain
    g2 = ndi.gaussian_filter(cv.glow, (9, 9, 0)) * glow_gain * 0.8
    gl = np.clip(g + g2, 0, 400)
    gm = gl.max(-1, keepdims=True)
    # sobre edificios: mezcla aditiva; sobre vacío: añade alfa
    rgb = a[..., :3]
    add = np.clip(rgb + gl * 0.55, 0, 255)
    a[..., :3] = np.where(alpha[..., None], add, a[..., :3])
    ga = np.clip(gm[..., 0] / 255.0, 0, 1) * 0.85
    empty = ~alpha
    newa = np.where(empty, np.maximum(a[..., 3], ga * 255), a[..., 3])
    colg = np.clip(gl, 0, 255)
    a[..., :3] = np.where(empty[..., None] & (ga[..., None] > 0.01), colg, a[..., :3])
    a[..., 3] = newa
    return a


# ------------------------------------------------------------------ edificios
def house(c, x, base, w, h, pal, rs, lit=0.3, roof_h=None):
    wall, wall2, roof, trim, dark, litc = pal['wall'], pal['wall2'], pal['roof'], pal['trim'], pal['dark'], pal['lit']
    top = base - h
    c.rect(x, top, x + w, base, wall)
    # textura de ladrillo/piedra por franjas
    for yy in range(int(top) + 2, int(base), 4):
        off = int(hsh(int(x), yy) * 6)
        c.line((x, yy), (x + w - 1, yy), wall2, 1)
    # borde iluminado izq y sombra der
    c.line((x, top), (x, base), pal.get('edge', wall2), 1)
    c.line((x + w, top), (x + w, base), pal['dark'], 1)
    c.rect(x - 1, top - 2, x + w + 1, top, trim)
    rh = roof_h or w * rs.uniform(0.55, 0.9)
    apex = x + w / 2 + rs.uniform(-w * .15, w * .15)
    c.poly([(x - 2, top - 2), (apex, top - 2 - rh), (x + w + 2, top - 2)], roof)
    # tejas
    k = 0
    for yy in range(int(top - 2 - rh) + 3, int(top - 2), 3):
        t = (yy - (top - 2 - rh)) / rh
        xl = apex - (apex - (x - 2)) * t
        xr = apex + ((x + w + 2) - apex) * t
        c.line((xl + 1, yy), (xr - 1, yy), pal['roof2'], 1)
    c.line((apex, top - 2 - rh), (x + w + 2, top - 2), pal['roof2'], 1)
    # chimenea
    if rs.random_sample() < 0.7:
        cx_ = x + w * rs.uniform(0.15, 0.7)
        ch_top = top - 2 - rh * 0.55 - 7
        c.rect(cx_, ch_top, cx_ + 5, top - 2 - rh * 0.25, wall)
        c.rect(cx_ - 1, ch_top - 2, cx_ + 6, ch_top, trim)
    # ventanas
    cols = max(1, int((w - 4) // 10))
    rows = max(1, int((h - 14) // 15))
    gx = (w - cols * 10) / 2 + 2.5
    for r in range(rows):
        for q in range(cols):
            wx = x + gx + q * 10
            wy = top + 6 + r * 15
            if wy + 9 > base - 10:
                continue
            isl = rs.random_sample() < lit
            c.rect(wx - 1, wy - 1, wx + 6, wy + 10, pal['frame'])
            c.poly([(wx - 1, wy), (wx + 2.5, wy - 3), (wx + 6, wy)], pal['frame'])
            if isl:
                c.rect(wx, wy, wx + 5, wy + 9, litc[0])
                c.poly([(wx, wy), (wx + 2.5, wy - 2), (wx + 5, wy)], litc[0])
                c.rect(wx, wy + 4, wx + 5, wy + 9, litc[1])
                c.line((wx + 2, wy - 1), (wx + 2, wy + 9), pal['frame'], 1)
                c.line((wx, wy + 4), (wx + 5, wy + 4), pal['frame'], 1)
                c.light(wx + 2.5, wy + 5, 6, litc[1], 0.9)
            else:
                c.rect(wx, wy, wx + 5, wy + 9, dark)
                c.poly([(wx, wy), (wx + 2.5, wy - 2), (wx + 5, wy)], dark)
                c.line((wx - 1, wy + 10), (wx + 6, wy + 10), trim, 1)
    # puerta
    dx_ = x + w / 2 - 3
    c.rect(dx_, base - 11, dx_ + 7, base, dark)
    c.poly([(dx_, base - 11), (dx_ + 3.5, base - 15), (dx_ + 7, base - 11)], dark)


def tower(c, x, base, w, h, pal, rs, clock=False, spire=None):
    wall, wall2, roof, trim, dark = pal['wall'], pal['wall2'], pal['roof'], pal['trim'], pal['dark']
    top = base - h
    c.rect(x, top, x + w, base, wall)
    for yy in range(int(top) + 3, int(base), 5):
        c.line((x, yy), (x + w - 1, yy), wall2, 1)
    c.line((x, top), (x, base), pal.get('edge', wall2), 1)
    c.line((x + w, top), (x + w, base), dark, 1)
    sp = spire or w * 2.6
    c.rect(x - 2, top - 3, x + w + 2, top, trim)
    # aguja con pináculos
    c.poly([(x - 1, top - 3), (x + w / 2, top - 3 - sp), (x + w + 1, top - 3)], roof)
    c.line((x + w / 2, top - 3 - sp), (x + w + 1, top - 3), pal['roof2'], 1)
    for k in range(3):
        c.line((x + w / 2 - 1 + k * 0, top - 3 - sp * (0.2 + 0.25 * k)), (x + w / 2 - 3 + k, top - 3 - sp * (0.2 + 0.25 * k)), pal['roof2'], 1)
    c.rect(x - 2, top - 8, x, top - 3, wall)
    c.poly([(x - 3, top - 8), (x - 1, top - 14), (x + 1, top - 8)], roof)
    c.rect(x + w, top - 8, x + w + 2, top - 3, wall)
    c.poly([(x + w - 1, top - 8), (x + w + 1, top - 14), (x + w + 3, top - 8)], roof)
    # ventanas ojivales
    for k in range(int(h // 22)):
        wy = top + 10 + k * 22
        if wy > base - 22:
            break
        wx = x + w / 2 - 2
        c.rect(wx, wy, wx + 4, wy + 11, dark)
        c.poly([(wx, wy), (wx + 2, wy - 4), (wx + 4, wy)], dark)
        if rs.random_sample() < 0.4:
            c.rect(wx + 1, wy + 1, wx + 3, wy + 9, pal['lit'][1])
            c.light(wx + 2, wy + 5, 6, pal['lit'][1], 0.8)
    if clock:
        cy = top + 12
        c.ell(x + w / 2, cy, 6, 6, pal['trim'])
        c.ell(x + w / 2, cy, 4.6, 4.6, (255, 196, 110))
        c.line((x + w / 2, cy), (x + w / 2, cy - 3), dark, 1)
        c.line((x + w / 2, cy), (x + w / 2 + 2, cy), dark, 1)
        c.light(x + w / 2, cy, 9, (255, 160, 70), 1.0)


def cathedral(c, x, base, pal, rs, scale=1.0):
    wall, wall2, roof, trim, dark = pal['wall'], pal['wall2'], pal['roof'], pal['trim'], pal['dark']
    nave_w, nave_h = 90 * scale, 78 * scale
    # contrafuertes volantes
    for sg in (-1, 1):
        for k in range(3):
            bx = x + nave_w / 2 + sg * (nave_w / 2 + 16 + k * 22)
            c.rect(bx - 3, base - 46 + k * 8, bx + 3, base, wall)
            c.poly([(bx - 4, base - 46 + k * 8), (bx, base - 54 + k * 8), (bx + 4, base - 46 + k * 8)], roof)
            ax = x + nave_w / 2 + sg * (nave_w / 2 - 2 + k * 22)
            ptsA = [(ax, base - 62 + k * 4)]
            for t in range(1, 7):
                tt = t / 6
                ptsA.append((ax + (bx - ax) * tt, base - 62 + k * 4 + (base - 46 + k * 8 - (base - 62 + k * 4)) * (tt ** 2) - 6 * math.sin(math.pi * tt)))
            c.lines(ptsA, wall, 3)
    # nave
    c.rect(x, base - nave_h, x + nave_w, base, wall)
    for yy in range(int(base - nave_h) + 3, int(base), 5):
        c.line((x, yy), (x + nave_w - 1, yy), wall2, 1)
    # tejado
    c.poly([(x - 3, base - nave_h), (x + nave_w / 2, base - nave_h - 34 * scale), (x + nave_w + 3, base - nave_h)], roof)
    # torres
    for tx in (x - 8 * scale, x + nave_w - 18 * scale):
        tower(c, tx, base, 26 * scale, 118 * scale, pal, rs, clock=(tx < x), spire=48 * scale)
    # frontón central y rosetón
    cx = x + nave_w / 2
    c.poly([(cx - 22 * scale, base - nave_h + 4), (cx, base - nave_h - 22 * scale), (cx + 22 * scale, base - nave_h + 4)], wall)
    c.ell(cx, base - nave_h + 12 * scale, 13 * scale, 13 * scale, pal['trim'])
    c.ell(cx, base - nave_h + 12 * scale, 10.5 * scale, 10.5 * scale, (190, 60, 40))
    c.ell(cx, base - nave_h + 12 * scale, 6 * scale, 6 * scale, (255, 170, 70))
    for k in range(8):
        a = k * math.pi / 4
        c.line((cx, base - nave_h + 12 * scale), (cx + 10.5 * scale * math.cos(a), base - nave_h + 12 * scale + 10.5 * scale * math.sin(a)), pal['frame'], 1)
    c.ell(cx, base - nave_h + 12 * scale, 2.2 * scale, 2.2 * scale, (255, 230, 150))
    c.light(cx, base - nave_h + 12 * scale, 16 * scale, (255, 110, 50), 1.1)
    # portal ojival y vitrales
    c.rect(cx - 8 * scale, base - 30 * scale, cx + 8 * scale, base, dark)
    c.poly([(cx - 8 * scale, base - 30 * scale), (cx, base - 44 * scale), (cx + 8 * scale, base - 30 * scale)], dark)
    for k in (-1, 1):
        for j in range(2):
            wx = cx + k * (22 + j * 14) * scale
            wy = base - nave_h + 36 * scale
            c.rect(wx - 3, wy, wx + 3, wy + 16 * scale, dark)
            c.poly([(wx - 3, wy), (wx, wy - 6), (wx + 3, wy)], dark)
            c.rect(wx - 2, wy + 1, wx + 2, wy + 15 * scale, (230, 120, 56) if (j + (k > 0)) % 2 else (190, 50, 50))
            c.light(wx, wy + 8, 6, (255, 110, 50), .8)


def ruin(c, x, base, w, h, pal, rs):
    wall, wall2, trim, dark = pal['wall'], pal['wall2'], pal['trim'], pal['dark']
    top = base - h
    pts = [(x, base), (x, top + rs.uniform(0, 10))]
    n = max(3, int(w // 6))
    for k in range(1, n + 1):
        pts.append((x + w * k / n, top + rs.uniform(0, h * 0.35)))
    pts.append((x + w, base))
    c.poly(pts, wall)
    for yy in range(int(top) + 3, int(base), 4):
        c.line((x + 1, yy), (x + w - 2, yy), wall2, 1)
    for k in range(int(w // 14)):
        wx = x + 4 + k * 14
        wy = top + 12 + (k % 2) * 10
        c.rect(wx, wy, wx + 5, wy + 12, dark)
        c.poly([(wx, wy), (wx + 2.5, wy - 4), (wx + 5, wy)], dark)
    # vigas
    c.line((x + w * .3, top + 4), (x + w * .6, top - 6), pal['roof'], 2)


def lamp(c, x, base, rs, glow=True):
    c.rect(x, base - 42, x + 2, base, (12, 6, 14))
    c.rect(x - 3, base - 3, x + 5, base, (12, 6, 14))
    c.line((x + 1, base - 40), (x + 6, base - 44), (12, 6, 14), 2)
    c.rect(x + 3, base - 50, x + 10, base - 43, (12, 6, 14))
    c.rect(x + 4, base - 49, x + 9, base - 44, (255, 200, 110))
    c.poly([(x + 2, base - 50), (x + 6.5, base - 54), (x + 11, base - 50)], (12, 6, 14))
    if glow:
        c.light(x + 6.5, base - 46, 11, (255, 150, 60), 1.4)


PAL1 = dict(wall=(78, 24, 44), wall2=(70, 21, 40), roof=(60, 18, 36), roof2=(52, 15, 32), trim=(94, 32, 52), dark=(46, 13, 30), frame=(46, 13, 30), edge=(92, 30, 52), lit=[(220, 130, 70), (240, 160, 80)])
PAL2 = dict(wall=(34, 15, 28), wall2=(40, 19, 33), roof=(24, 10, 22), roof2=(31, 14, 28), trim=(58, 28, 44), dark=(12, 6, 15), frame=(18, 8, 18), edge=(62, 30, 46), lit=[(255, 204, 110), (240, 140, 56)])


# ------------------------------------------------------------------ capas
def layer0():
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    keys = [(0, (8, 3, 14)), (60, (26, 5, 22)), (130, (70, 10, 32)), (190, (122, 22, 38)), (232, (156, 36, 44)), (288, (70, 12, 28))]
    col = np.zeros((H, W, 3))
    for (y0, c0), (y1, c1) in zip(keys[:-1], keys[1:]):
        m = (ys >= y0) & (ys < y1)
        t = ((ys - y0) / (y1 - y0))[..., None]
        col = np.where(m[..., None], np.array(c0) * (1 - t) + np.array(c1) * t, col)
    mx, my, mr = 330.0, 108.0, 58.0
    d = np.hypot(xs + 0.5 - mx, ys + 0.5 - my)
    # halo escalonado
    halo = np.clip(1 - (d - mr) / 120, 0, 1) ** 2.2
    halo = np.where(d > mr, halo, 1)
    lv = np.floor(halo * 7 + bayer_field(H, W) * 0.9) / 7
    col = col + np.array([190, 34, 46]) * np.clip(lv, 0, 1)[..., None] * 0.62
    # estrellas
    rs = RS(5)
    for _ in range(70):
        sx, sy = rs.randint(0, W), rs.randint(0, 120)
        if np.hypot(sx - mx, sy - my) < mr + 30:
            continue
        b = rs.choice([0.5, 0.7, 1.0])
        col[sy, sx] = col[sy, sx] * (1 - b) + np.array([255, 180, 170]) * b
    # luna con textura
    nx, ny = (xs + 0.5 - mx) / mr, (ys + 0.5 - my) / mr
    r2 = nx * nx + ny * ny
    inside = r2 <= 1
    nz = np.sqrt(np.clip(1 - r2, 0, 1))
    lam = np.clip(nx * -0.5 + ny * -0.55 + nz * 0.67, 0, 1)
    tex = fbm(xs / 9.0, ys / 9.0, 11, 4)
    tex2 = fbm(xs / 3.2, ys / 3.2, 12, 2)
    maria = np.clip((tex - 0.5) * 2.2, -1, 1)
    sh = lam * 0.95 - 0.18 * maria + 0.06 * (tex2 - .5)
    # cráteres
    for (cx_, cy_, cr_) in ((-0.35, -0.2, 0.17), (0.25, 0.3, 0.2), (-0.1, 0.55, 0.12), (0.45, -0.35, 0.1), (-0.55, 0.25, 0.1), (0.1, -0.5, 0.08)):
        dc = np.hypot(nx - cx_, ny - cy_)
        sh -= np.where(dc < cr_, 0.22, 0) * (nx * 0 + 1)
        sh += np.where((dc >= cr_) & (dc < cr_ + 0.04) & (nx + ny < cx_ + cy_), 0.15, 0)
    sh = np.clip(sh, 0, 1)
    mramp = np.array([(58, 6, 20), (100, 12, 30), (150, 22, 40), (200, 40, 50), (236, 78, 66), (255, 130, 100)], float)
    idx = np.clip(((sh + bayer_field(H, W) * 0.1) * 6).astype(int), 0, 5)
    moon = mramp[idx]
    col = np.where(inside[..., None], moon, col)
    # borde brillante
    rim = (r2 > 0.93) & inside
    col[rim] = col[rim] * 0.7 + np.array([255, 120, 100]) * 0.3
    # nubes (periodicas)
    cn = fbm(xs / 128.0, ys / 34.0, 21, 4, px=4)
    cn2 = fbm(xs / 64.0 + 3, ys / 20.0, 22, 3, px=8)
    prof = smooth((ys - 20) / 40) * (1 - smooth((ys - 210) / 40))
    cm = smooth((cn * 0.7 + cn2 * 0.4 - 0.55) / 0.12) * prof
    cm_q = (cm + bayer_field(H, W) * 0.15) > 0.5
    cloud_dark = np.array([20, 4, 18])
    glowm = np.clip(1 - (d - mr * 0.8) / 150, 0, 1)
    edge = cm_q & ~ndi.binary_erosion(cm_q, iterations=1)
    cc = np.where(cm_q[..., None], cloud_dark + np.array([60, 14, 24]) * glowm[..., None] * (0.3 + 0.7 * smooth((cn - 0.45) / 0.2))[..., None], col)
    cc[edge] = np.array([140, 34, 44]) * (0.35 + glowm[edge][:, None] * 0.9)
    out = np.where(cm_q[..., None], cc, col)
    # una segunda capa de nubes finas
    thin = smooth((fbm(xs / 160.0, ys / 12.0, 31, 3, px=3) - 0.58) / 0.1) * prof * 0.5
    tq = (thin + bayer_field(H, W) * 0.2) > 0.4
    out = np.where(tq[..., None] & ~cm_q[..., None], out * 0.55 + np.array([60, 10, 26]) * 0.45, out)
    img = np.concatenate([np.clip(out, 0, 255), np.full((H, W, 1), 255.0)], -1)
    return img


def haze(a, y0, y1, color, amt, seed, px=4, sx=96.0):
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    n = fbm(xs / sx, ys / 18.0, seed, 3, px=int(W / sx) if W % sx == 0 else px)
    prof = smooth((ys - y0) / (y1 - y0)) * (1 - smooth((ys - y1) / 40))
    k = np.clip(prof * (0.4 + n * 0.9) * amt, 0, 1)
    k = np.floor(k * 5 + bayer_field(H, W) * 0.8) / 5
    k = np.clip(k, 0, 1)[..., None]
    rgb = a[..., :3] * (1 - k) + np.array(color) * k
    al = np.maximum(a[..., 3], k[..., 0] * 255 * 0.0 + np.where(a[..., 3] > 0, a[..., 3], k[..., 0] * 255 * 0.8))
    return np.concatenate([rgb, al[..., None]], -1)


def layer1():
    c = Cv()
    rs = RS(101)
    pal = PAL1
    base = 236
    # relleno de suelo lejano
    c.rect(0, base - 2, W, H, pal['wall2'])
    x = 0
    items = []
    while x < W:
        r = rs.random_sample()
        if r < 0.45:
            w = rs.randint(26, 46)
            items.append(('h', x, w))
        elif r < 0.7:
            w = rs.randint(10, 15)
            items.append(('t', x, w))
        elif r < 0.85:
            w = rs.randint(28, 40)
            items.append(('r', x, w))
        else:
            w = rs.randint(20, 30)
            items.append(('h', x, w))
        x += w + rs.randint(0, 5)
    cat_x = 120
    for kind, x, w in items:
        if cat_x - 20 < x < cat_x + 60:
            continue
        if kind == 'h':
            house(c, x, base, w, rs.randint(34, 64), pal, rs, lit=0.1)
        elif kind == 't':
            tower(c, x, base, w, rs.randint(80, 120), pal, rs, clock=rs.random_sample() < 0.3)
        else:
            ruin(c, x, base, w, rs.randint(30, 60), pal, rs)
    cathedral(c, cat_x - 5, base, pal, rs, scale=0.82)
    cathedral(c, 400, base, pal, rs, scale=0.6)
    a = finish_layer(c, rim=(190, 60, 72), glow_gain=0.7)
    # gradiente vertical (más claro hacia abajo: bruma)
    ys = np.mgrid[0:H, 0:W][0].astype(float)
    al = a[..., 3] > 0
    t = np.clip((ys - 90) / 150, 0, 1)[..., None]
    a[..., :3] = np.where(al[..., None], a[..., :3] * (0.85 + 0.0 * t) + np.array([60, 14, 28]) * t * 0.55, a[..., :3])
    a = haze(a, 170, 250, (120, 36, 50), 1.1, 61)
    return a


def layer2():
    c = Cv()
    rs = RS(202)
    pal = PAL2
    base = 252
    c.rect(0, base - 3, W, H, (16, 8, 16))
    # empedrado simple
    for yy in range(base, H, 6):
        for xx in range(0, W, 10):
            o = (xx + (yy // 6 % 2) * 5)
            c.line((o, yy), (o + 8, yy), (24, 12, 22), 1)
    spec = [
        ('h', 6, 44, 96), ('t', 54, 18, 150), ('h', 76, 36, 80), ('r', 116, 30, 70),
        ('cat', 160, 0, 0),
        ('h', 300, 40, 90), ('t', 346, 20, 140), ('h', 370, 38, 76), ('r', 412, 34, 66), ('h', 450, 44, 104), ('t', 497, 12, 110)]
    for kind, x, w, h in spec:
        if kind == 'h':
            house(c, x, base, w, h, pal, rs, lit=0.38)
        elif kind == 't':
            tower(c, x, base, w, h, pal, rs, clock=(x == 346))
        elif kind == 'r':
            ruin(c, x, base, w, h, pal, rs)
        else:
            cathedral(c, x - 18, base, pal, rs, scale=1.15)
    for lx in (20, 150, 288, 405, 478):
        lamp(c, lx, base, rs)
    a = finish_layer(c, rim=(170, 50, 62), glow_gain=1.0)
    a = haze(a, 214, 262, (130, 40, 54), 1.0, 71)
    return a


def crow(c, x, y, wings=0, col=(9, 4, 11), flip=False):
    s = -1 if flip else 1
    if wings == 0:  # posado
        c.ell(x, y - 4, 4.6, 3.2, col)
        c.ell(x + s * 4.5, y - 7, 2.4, 2.1, col)
        c.poly([(x + s * 6.4, y - 7.6), (x + s * 9.4, y - 6.6), (x + s * 6.4, y - 6)], col)
        c.poly([(x - s * 3, y - 3), (x - s * 9, y - 1), (x - s * 3, y - 1)], col)
        c.line((x, y - 1), (x, y), col, 1)
    else:  # en vuelo
        c.ell(x, y, 3.2, 2.2, col)
        c.ell(x + s * 3.2, y - 1, 1.8, 1.6, col)
        c.poly([(x + s * 4.6, y - 1.6), (x + s * 7, y - 0.8), (x + s * 4.6, y - .2)], col)
        up = wings == 1
        if up:
            c.poly([(x - 1, y - 1), (x - 6 * s, y - 9), (x - 11 * s, y - 7), (x - 7 * s, y - 2)], col)
            c.poly([(x + 1, y - 1), (x + 4 * s, y - 10), (x + 9 * s, y - 8), (x + 6 * s, y - 2)], col)
        else:
            c.poly([(x - 1, y), (x - 8 * s, y + 3), (x - 13 * s, y + 1), (x - 7 * s, y - 2)], col)
            c.poly([(x + 1, y), (x + 8 * s, y + 3), (x + 13 * s, y + 1), (x + 7 * s, y - 2)], col)
        c.poly([(x - 3 * s, y), (x - 8 * s, y + 3), (x - 3 * s, y + 2)], col)


def layer3():
    c = Cv()
    rs = RS(303)
    K = (10, 5, 13)
    base = 256
    # suelo
    c.rect(0, base, W, H, (14, 7, 15))
    for yy in range(base + 4, H, 8):
        for xx in range(0, W, 16):
            o = xx + (yy // 8 % 2) * 8
            c.line((o, yy), (o + 14, yy), (26, 13, 24), 1)
            c.line((o + 7, yy), (o + 7, yy + 7), (22, 11, 20), 1)
    # pilares
    for px_ in (64, 192, 320, 448):
        c.rect(px_ - 11, 186, px_ + 11, base, K)
        c.rect(px_ - 13, 180, px_ + 13, 187, K)
        c.poly([(px_ - 13, 180), (px_, 164), (px_ + 13, 180)], K)
        c.ell(px_, 161, 3.5, 3.5, K)
        c.rect(px_ - 13, base - 8, px_ + 13, base, K)
        for yy in range(192, base - 8, 8):
            c.line((px_ - 8, yy), (px_ + 8, yy), (22, 11, 22), 1)
        c.line((px_ - 11, 188), (px_ - 11, base - 10), (44, 18, 30), 1)
    # verja entre pilares
    for k in range(32):
        x = 8 + k * 16
        if min(abs(x - p) for p in (64, 192, 320, 448)) < 18:
            continue
        c.rect(x - 1.5, 208, x + 1.5, base, K)
        c.poly([(x - 2.6, 208), (x, 197), (x + 2.6, 208)], K)
        c.px(x, 197, (150, 46, 58))
        c.rect(x - 2.5, 214, x + 2.5, 216, K)
    for (yb, hh) in ((222, 3), (242, 3)):
        for seg in range(4):
            x0 = 64 + seg * 128 + 13
            c.rect(x0, yb, x0 + 102, yb + hh, K)
    for seg in range(4):
        x0 = 64 + seg * 128 + 13
        for q in range(5):
            cx = x0 + 11 + q * 20
            c.ell(cx, 232, 5, 5, K)
            c.ell(cx, 232, 3, 3, (0, 0, 0, 0))
        c.ell(x0 + 51, 232, 7, 7, K)
        c.ell(x0 + 51, 232, 4.5, 4.5, (0, 0, 0, 0))
    # pinchos en pilares y farol
    lx = 192
    c.rect(lx - 1, 140, lx + 1, 164, K)
    c.rect(lx - 5, 126, lx + 5, 140, K)
    c.rect(lx - 3.5, 128, lx + 3.5, 138, (255, 190, 100))
    c.line((lx, 128), (lx, 138), K, 1)
    c.poly([(lx - 6, 126), (lx, 119), (lx + 6, 126)], K)
    c.light(lx, 133, 14, (255, 150, 60), 1.5)
    # cuervos
    for (x, y, f) in ((64, 164, False), (448, 164, True), (110, 222, False), (350, 222, True), (410, 242, False), (240, 222, False)):
        crow(c, x, y, 0, K, f)
    for (x, y, wg, f) in ((120, 120, 1, False), (150, 98, 2, False), (230, 76, 1, True), (390, 132, 2, True), (440, 100, 1, False), (60, 150, 2, True)):
        crow(c, x, y, wg, K, f)
    # rama muerta colgante
    br = [(30, 0), (34, 14), (28, 28), (34, 44), (30, 60)]
    c.lines(br, K, 4)
    for (bx, by, ex, ey, w) in ((34, 14, 58, 22, 2), (28, 28, 8, 38, 2), (34, 44, 56, 50, 2), (58, 22, 72, 18, 1), (58, 22, 66, 34, 1), (8, 38, 2, 52, 1), (56, 50, 70, 60, 1)):
        c.line((bx, by), (ex, ey), K, w)
    br2 = [(470, 0), (466, 16), (472, 34), (466, 52)]
    c.lines(br2, K, 3)
    for (bx, by, ex, ey, w) in ((466, 16, 440, 24, 2), (472, 34, 496, 42, 2), (440, 24, 428, 18, 1), (440, 24, 432, 38, 1), (496, 42, 506, 54, 1)):
        c.line((bx, by), (ex, ey), K, w)
    a = finish_layer(c, rim=(160, 46, 58), rim_amt=0.9, glow_gain=1.0)
    a = haze(a, 232, 278, (140, 44, 58), 1.1, 81)
    # fina niebla delante del suelo
    return a


def save(name, arr):
    Image.fromarray(to_u8(arr), 'RGBA').save(A + '/ui/' + name + '.png', optimize=True)


def build():
    ensure(A + '/ui')
    save('ui_title_0', layer0())
    save('ui_title_1', layer1())
    save('ui_title_2', layer2())
    save('ui_title_3', layer3())


def preview():
    L = [Image.open(A + f'/ui/ui_title_{i}.png').convert('RGBA') for i in range(4)]
    # compuesto 480x270 con desfase por capa
    def comp(off):
        im = Image.new('RGBA', (480, 270), (0, 0, 0, 255))
        for i, l in enumerate(L):
            o = int(off * (i * 0.35))
            wide = Image.new('RGBA', (W * 3, H))
            for k in range(3):
                wide.paste(l, (k * W, 0))
            sx = (W + o) % W + 16
            im.alpha_composite(wide.crop((sx, 8, sx + 480, 8 + 270)))
        return im
    base = comp(0)
    logo = Image.open(A + '/ui/ui_logo.png').convert('RGBA')
    base.alpha_composite(logo, (90, 14))
    # botones y texto
    try:
        import fonts
        t = fonts.render_text('font_b', 'Nueva partida', 1, (255, 230, 170))
        btn = Image.open(A + '/ui/ui_btn.png').convert('RGBA')
        import ui_parts
        b = ui_parts.nine(btn.crop((0, 0, 48, 20)), 6, 110, 22)
        for i, nm in enumerate(('Nueva partida', 'Santuario', 'Opciones')):
            base.alpha_composite(b, (185, 150 + i * 26))
            t = fonts.render_text('font_s', nm, 1, (255, 230, 170))
            base.alpha_composite(t, (185 + (110 - t.width) // 2, 155 + i * 26))
    except Exception as e:
        print('prev', e)
    base.resize((480 * 3, 270 * 3), Image.NEAREST).convert('RGB').save(PREV + '/title_mock.png')
    # capas sueltas
    for i, l in enumerate(L):
        bg = Image.new('RGBA', l.size, (60, 60, 70, 255))
        bg.alpha_composite(l)
        bg.convert('RGB').save(PREV + f'/title_layer{i}.png')
    # tileado: dos copias
    wide = Image.new('RGBA', (W * 2, H), (0, 0, 0, 255))
    for l in L:
        for k in range(2):
            wide.alpha_composite(l, (k * W, 0))
    wide.convert('RGB').save(PREV + '/title_tile.png')


if __name__ == '__main__':
    build()
    preview()
