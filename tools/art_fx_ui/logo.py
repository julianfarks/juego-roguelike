"""Logotipo SwordsmanMagic / ETERNAL ABYSS."""
from common import *
import fonts

W, H = 300, 84
BASE, XT, CAP, ASC = 46.0, 24.0, 8.0, 5.0


def E(cx, cy, rx, ry, a0=0, a1=360, n=36):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def pen(strokes, SS=4, L=6.2, ang=42, base=1.6):
    im = Image.new('L', (W * SS, H * SS), 0)
    dr = ImageDraw.Draw(im)
    nx, ny = math.cos(math.radians(ang)) * L / 2, -math.sin(math.radians(ang)) * L / 2
    for pts in strokes:
        for a, b in zip(pts[:-1], pts[1:]):
            P = lambda p, s: ((p[0] + s * nx) * SS, (p[1] + s * ny) * SS)
            dr.polygon([P(a, 1), P(a, -1), P(b, -1), P(b, 1)], fill=255)
            dr.line([(a[0] * SS, a[1] * SS), (b[0] * SS, b[1] * SS)], fill=255, width=int(base * SS))
    arr = np.array(im).reshape(H, SS, W, SS).mean((1, 3)) / 255
    return arr >= 0.5


def st(x, y0, y1):
    return [(x, y0), (x, y1)]


def hz(x0, x1, y):
    return [(x0, y), (x1, y)]


def letters():
    """Devuelve lista de (ancho, strokes) en coordenadas locales."""
    b, x0 = BASE, XT
    G = {}
    G['S'] = (21, [E(11, 17, 7.5, 9.0, -35, -255), E(11, 36, 8.6, 10, -115, 150), hz(4, 15, CAP - .5)])
    G['w'] = (27, [[(2, x0), (8, b - 1), (14, x0)], [(13, x0), (19, b - 1), (25, x0)], hz(0, 6, x0), hz(11, 17, x0), hz(21, 27, x0)])
    G['o'] = (16, [E(8, 35, 7.0, 10.8)])
    G['r'] = (13, [st(3, x0, b), E(8.5, 30, 5.5, 6.5, 195, 335), hz(0, 6, x0), hz(0, 7, b), [(12, 26), (13, 29)]])
    G['d'] = (21, [E(8, 35, 7.2, 10.8), st(16, ASC, b), hz(11, 18, ASC), hz(14, 21, b)])
    G['m'] = (28, [st(3, x0, b), E(8, 30, 5, 6.5, 180, 360), st(13, 30, b), E(18, 30, 5, 6.5, 180, 360), st(23, 30, b), hz(0, 6, x0), hz(0, 6, b), hz(10, 16, b), hz(20, 27, b)])
    G['a'] = (21, [E(8, 35, 7.2, 10.8), st(15.5, x0, b), hz(13, 20, b), hz(12, 18, x0)])
    G['n'] = (21, [st(3, x0, b), E(10, 30.5, 7, 7.5, 180, 360), st(17, 30.5, b), hz(0, 6, x0), hz(0, 6, b), hz(14, 21, b)])
    G['M'] = (38, [st(3, CAP, b), E(12, 25, 8.5, 14, 180, 360), st(20.5, 25, b), E(28.5, 25, 8.5, 14, 180, 360), st(37, 25, b), hz(0, 8, CAP), hz(0, 7, b), hz(16, 24, b), hz(32, 40, b)])
    G['g'] = (21, [E(8, 35, 7.2, 10.8), st(15.5, x0, 53), E(8.5, 53, 7.2, 4.8, 0, 175), hz(12, 19, x0)])
    G['i'] = (9, [st(4, x0, b), st(4, 13.5, 17), hz(1, 5, x0), hz(1, 8, b)])
    G['s'] = (17, [E(8.5, 29.5, 6.6, 5.6, -35, -255), E(8.5, 40.4, 7.2, 5.6, -115, 150)])
    G['c'] = (17, [E(8.5, 35, 7.4, 10.8, -45, -318), hz(9, 15, x0 - .5), [(15, 26), (15.5, 29)]])
    return G


def logo_text_mask():
    G = letters()
    word = 'SwordsmanMagic'
    sp = {'S': 3, 'w': 1, 'o': 1, 'r': 1, 'd': 2, 'm': 1, 'a': 1, 'n': 2, 'M': 3, 'g': 1, 'i': 1, 'c': 0, 's': 1}
    f = 0.9
    total = sum((G[c][0] + sp.get(c, 1)) * f for c in word) - 1
    x = (W - total) / 2 + 1
    strokes = []
    for c in word:
        w, st_ = G[c]
        for s in st_:
            strokes.append([(px * f + x, py) for px, py in s])
        x += (w + sp.get(c, 1)) * f
    return pen(strokes)


def shift(m, dx, dy):
    return np.roll(np.roll(m, dy, 0), dx, 1)


def gold_fill(m):
    ys = np.arange(H)[:, None] * np.ones((1, W))
    t = np.clip((ys - 6) / 50.0, 0, 1)
    ramp = np.array([(255, 244, 178), (255, 214, 104), (230, 170, 58), (190, 124, 40), (138, 84, 30), (96, 56, 24)], float)
    idx = np.clip(((t + bayer_field(H, W) * 0.10) * len(ramp)).astype(int), 0, len(ramp) - 1)
    return ramp[idx]


def build_logo():
    m = logo_text_mask()
    img = np.zeros((H, W, 4))
    # resplandor rojo
    glow = ndi.gaussian_filter(m.astype(float), 4.0)
    gl = np.zeros((H, W, 4))
    gl[..., :3] = (150, 16, 34)
    gl[..., 3] = np.clip(glow * 1.6, 0, 1) * 150
    img = over(img, gl)
    # sombra roja 3D
    for k in range(1, 4):
        sh = shift(m, k, k)
        c = np.zeros((H, W, 4))
        c[..., :3] = (150, 16, 34) if k < 3 else (96, 8, 26)
        c[..., 3] = sh * 255
        img = over(img, c)
    # contorno
    dil = ndi.binary_dilation(m, np.ones((3, 3), bool))
    o = np.zeros((H, W, 4))
    o[..., :3] = (30, 8, 14)
    o[..., 3] = dil * 255
    img = over(img, o)
    # relleno dorado
    fill = gold_fill(m)
    f = np.zeros((H, W, 4))
    f[..., :3] = fill
    f[..., 3] = m * 255
    # bisel
    hi_l = m & ~shift(m, 1, 0)
    hi_t = m & ~shift(m, 0, 1)
    lo_r = m & ~shift(m, -1, 0)
    lo_b = m & ~shift(m, 0, -1)
    f[hi_l | hi_t, :3] = (255, 248, 206)
    f[lo_r | lo_b, :3] = f[lo_r | lo_b, :3] * 0.62
    rs = RS(7)
    nz = rs.random_sample((H, W)) < 0.07
    f[m & nz, :3] *= 0.8
    # veta interior: línea oscura en el centro de trazos gruesos
    er = ndi.binary_erosion(m, np.ones((3, 3), bool))
    er2 = ndi.binary_erosion(er, np.ones((3, 3), bool))
    f[er2, :3] = np.clip(f[er2, :3] * 1.1 + 12, 0, 255)
    img = over(img, f)
    # espada integrada
    sw = PC(W, H, 4)
    cx, cy = 150, 61
    steel_l = (230, 232, 244)
    steel_m = (160, 168, 196)
    steel_d = (86, 92, 122)
    blade = np.zeros((H, W, 4))
    for sg in (-1, 1):
        for dd in range(14, 124):
            half = 2.4 * (1 - (dd - 14) / 112) + 0.4
            t = max(1, int(round(half * 2)))
            x = int(cx + sg * dd - (1 if sg < 0 else 0))
            for r in range(t):
                y = cy - t // 2 + r
                col = steel_l if r == 0 else (steel_d if r == t - 1 and t > 1 else steel_m)
                blade[y, x] = col + (255,)
    gold, goldd, goldl = (236, 178, 66), (140, 90, 32), (255, 236, 150)
    sw.poly([(cx - 17, cy - 5), (cx - 9, cy - 3), (cx + 9, cy - 3), (cx + 17, cy - 5), (cx + 14, cy + 1), (cx + 7, cy + 3), (cx - 7, cy + 3), (cx - 14, cy + 1)], gold)
    sw.poly([(cx - 17, cy - 5), (cx - 9, cy - 3), (cx + 9, cy - 3), (cx + 17, cy - 5), (cx + 9, cy - 4), (cx - 9, cy - 4)], goldl)
    sw.poly([(cx - 14, cy + 1), (cx - 7, cy + 3), (cx + 7, cy + 3), (cx + 14, cy + 1), (cx, cy + 1.6)], goldd)
    sw.poly([(cx, cy - 3.6), (cx + 3.2, cy), (cx, cy + 3.6), (cx - 3.2, cy)], (206, 24, 48))
    sw.poly([(cx, cy - 3.6), (cx + 3.2, cy), (cx, cy - .4), (cx - 3.2, cy)], (255, 120, 130))
    sword = over(blade, sw.out())
    sword = outline(sword, 0.25, tint=(1, .6, .6))
    # sombra roja de la espada
    ss = np.zeros((H, W, 4))
    ss[..., :3] = (110, 10, 28)
    ss[..., 3] = shift(sword[..., 3] > 100, 1, 2) * 255
    img = over(img, ss)
    img = over(img, sword)
    # subtítulo con la fuente grande
    sub = 'ETERNAL ABYSS'
    fj = json.load(open(A + '/font/font_b.json'))
    fim = np.array(Image.open(A + '/font/font_b.png').convert('RGBA')).astype(float)
    cw, ch, cols = fj['cellW'], fj['cellH'], fj['cols']
    track = 2
    tw = sum(fj['widths'][fj['chars'].index(c)] + track for c in sub) - track
    x = (W - tw) // 2
    y0 = 67
    layer = np.zeros((H, W, 4))
    for c in sub:
        k = fj['chars'].index(c)
        cell = fim[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw]
        wh = (cell[..., 0] > 200) & (cell[..., 3] > 0)
        tgt = layer[y0 - 3:y0 - 3 + ch, x:x + cw]
        yy = np.arange(ch)[:, None] * np.ones((1, cw))
        t = np.clip((yy - 3) / 10.0, 0, 1)
        gcol = np.array([(255, 238, 170), (240, 190, 84), (196, 130, 44)], float)
        gi = np.clip((t * 3).astype(int), 0, 2)
        col = gcol[gi]
        sub_ol = (cell[..., 3] > 0) & ~wh
        # sombra roja
        shd = np.zeros_like(tgt)
        sh_mask = np.roll(np.roll(cell[..., 3] > 0, 1, 0), 1, 1)
        layer[y0 - 3 + 1:y0 - 3 + 1 + ch - 1, x + 1:x + cw - 1][..., :3] += 0
        tgt_alpha = tgt[..., 3] > 0
        block = np.zeros_like(tgt)
        block[sh_mask & ~tgt_alpha] = (120, 14, 30, 255)
        block[sub_ol] = (28, 8, 14, 255)
        block[wh, :3] = col[wh]
        block[wh, 3] = 255
        sel = block[..., 3] > 0
        tgt[sel] = block[sel]
        x += fj['widths'][k] + track
    img = over(img, layer)
    ensure(A + '/ui')
    Image.fromarray(to_u8(img), 'RGBA').save(A + '/ui/ui_logo.png', optimize=True)
    return img


def build():
    build_logo()


if __name__ == '__main__':
    build()
    im = Image.open(A + '/ui/ui_logo.png').convert('RGBA')
    bg = Image.new('RGBA', im.size, (40, 12, 24, 255))
    bg.alpha_composite(im)
    bg.resize((im.width * 4, im.height * 4), Image.NEAREST).convert('RGB').save(PREV + '/logo.png')
