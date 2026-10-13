"""Paneles, botones, barras, cursor, viñeta."""
from common import *

OUT = (20, 12, 22)


def save_ui(name, arr):
    ensure(A + '/ui')
    Image.fromarray(to_u8(arr), 'RGBA').save(A + '/ui/' + name + '.png', optimize=True)


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))


def panel(kind):
    W = H = 32
    P = {
        'n': dict(gold=((236, 200, 110), (186, 146, 72), (116, 84, 44)), stone=((72, 64, 84), (50, 44, 60), (36, 31, 44)), inner=(22, 16, 28), ctr=(14, 10, 20, 196), rivet=(255, 232, 160)),
        'l': dict(gold=((255, 230, 140), (214, 176, 92), (140, 104, 54)), stone=((120, 108, 128), (88, 78, 100), (62, 54, 74)), inner=(40, 32, 50), ctr=(42, 34, 52, 214), rivet=(255, 244, 190)),
        'r': dict(gold=((255, 120, 110), (196, 40, 56), (104, 14, 30)), stone=((82, 34, 44), (58, 22, 32), (40, 14, 24)), inner=(24, 6, 12), ctr=(30, 6, 12, 206), rivet=(255, 170, 150)),
    }[kind]
    g_hi, g_mid, g_lo = P['gold']
    s_hi, s_mid, s_lo = P['stone']
    img = np.zeros((H, W, 4))
    for y in range(H):
        for x in range(W):
            e = min(x, y, W - 1 - x, H - 1 - y)
            cx, cy = min(x, W - 1 - x), min(y, H - 1 - y)
            lit = (y <= x and y <= W - 1 - x) or (x < y and x <= H - 1 - y and x < W - 1 - x and False) or (x < y and x < H - 1 - y and x <= cy)
            top_left = (cy == y and y < H / 2 and cy <= cx) or (cx == x and x < W / 2 and cx < cy)
            lit_side = (y < H / 2 and cy <= cx) or (x < W / 2 and cx < cy)
            col = None
            if cx + cy < 2:
                continue  # esquina redondeada
            if e == 0 or cx + cy == 2 and cx < 2 and cy < 2:
                col = OUT
            elif e == 1:
                col = g_lo if not lit_side else g_mid
            elif e == 2:
                col = g_hi if lit_side else g_mid
            elif e == 3:
                col = g_mid if lit_side else g_lo
            elif e == 4:
                col = s_hi if lit_side else s_mid
            elif e == 5:
                col = s_mid if lit_side else s_lo
            elif e == 6:
                col = P['inner']
            else:
                img[y, x] = P['ctr']
                continue
            # soporte de esquina: ménsula dorada
            if cx < 8 and cy < 8 and e >= 3:
                if (cx <= 4 and cy <= 4):
                    col = g_mid if (cx + cy) % 2 == 0 else g_lo
                if (cx, cy) in ((4, 4),):
                    col = g_lo
            img[y, x, :3] = col
            img[y, x, 3] = 255
    # remaches de esquina
    for (cxx, cyy) in ((4, 4), (27, 4), (4, 27), (27, 27)):
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            xx, yy = cxx + dx - (1 if cxx > 16 else 0), cyy + dy - (1 if cyy > 16 else 0)
            c = P['rivet'] if (dx, dy) == (0, 0) else (g_mid if (dx + dy) == 1 else g_lo)
            img[yy, xx, :3] = c
    return img


def btn_state(state):
    W, H = 48, 20
    gold = {0: ((172, 132, 66), (122, 92, 48)), 1: ((255, 222, 130), (214, 170, 84)), 2: ((110, 82, 44), (78, 58, 34))}[state]
    top, bot = {0: ((86, 78, 98), (44, 38, 54)), 1: ((116, 104, 128), (62, 54, 76)), 2: ((30, 26, 38), (54, 48, 66))}[state]
    img = np.zeros((H, W, 4))
    for y in range(H):
        for x in range(W):
            cx, cy = min(x, W - 1 - x), min(y, H - 1 - y)
            if cx + cy < 2:
                continue
            e = min(cx, cy)
            t = y / (H - 1)
            if e == 0 or (cx + cy == 2 and cx < 3 and cy < 3 and False):
                col = OUT
            elif cx + cy == 2:
                col = OUT
            elif e == 1:
                col = gold[0] if (y < H / 2 or state == 2 and False) else gold[1]
                if state == 2:
                    col = gold[1] if y < H / 2 else gold[0]
            elif e == 2:
                if state == 2:
                    col = lerp(top, bot, t) if y > 3 else (18, 14, 24)
                else:
                    col = lerp(top, bot, t)
                    if y == 2 and cx >= 2:
                        col = lerp(top, (255, 255, 255), 0.18 + 0.12 * state)
            else:
                col = lerp(top, bot, t)
                if state == 2 and y in (3, 4):
                    col = lerp(col, (10, 8, 16), 0.55 if y == 3 else 0.25)
                if state != 2 and y == 2:
                    col = lerp(top, (255, 255, 255), 0.18 + 0.12 * state)
                if state != 2 and y == H - 3:
                    col = lerp(col, (10, 8, 16), 0.4)
            img[y, x, :3] = col
            img[y, x, 3] = 255
    for (rx, ry) in ((3, 3), (W - 4, 3), (3, H - 4), (W - 4, H - 4)):
        img[ry, rx, :3] = gold[0] if state != 2 else gold[1]
    return img


def btn():
    return np.concatenate([btn_state(0), btn_state(1), btn_state(2)], 1)


def round_state(state):
    W = H = 40
    img = np.zeros((H, W, 4))
    ys, xs = np.mgrid[0:H, 0:W]
    dx, dy = xs + 0.5 - 20, ys + 0.5 - 20
    d = np.hypot(dx, dy)
    bone = {0: [(96, 90, 88), (140, 134, 124), (186, 180, 164), (226, 220, 200)],
            1: [(60, 56, 58), (92, 88, 86), (126, 120, 112), (156, 150, 138)],
            2: [(54, 54, 60), (74, 74, 80), (96, 96, 102), (114, 114, 120)]}[state]
    ldot = np.where(d > 0, (-dx * 0.6 - dy * 0.8) / np.maximum(d, 1e-6), 0)
    if state == 1:
        ldot = -ldot * 0.8
    ti = np.clip(((ldot * 0.5 + 0.5) * 4).astype(int), 0, 3)
    ring_ = (d <= 19.4) & (d > 15.0)
    img[ring_, :3] = np.array(bone, float)[ti][ring_]
    img[ring_, 3] = 255
    inner = d <= 15.0
    t = np.clip((dy + 15) / 30, 0, 1)
    top, bot = ((66, 60, 74), (26, 22, 34)) if state == 0 else (((22, 18, 30), (50, 44, 62)) if state == 1 else ((44, 44, 52), (30, 30, 38)))
    for c in range(3):
        img[..., c] = np.where(inner, top[c] + (bot[c] - top[c]) * t, img[..., c])
    img[inner, 3] = 255
    # línea oscura entre aro y disco
    sep = (d <= 15.0) & (d > 13.8)
    img[sep, :3] = (24, 18, 28)
    # brillo interno arriba-izquierda
    if state != 1:
        hl = (d <= 12.4) & (d > 11.4) & (ldot > 0.55)
        img[hl, :3] = (150, 142, 170) if state == 0 else (92, 92, 100)
    edge = (d <= 20.0) & (d > 19.4)
    img[edge, :3] = OUT
    img[edge, 3] = 255
    if state == 2:
        img[..., 3] *= 0.72
    return img


def round_btn():
    return np.concatenate([round_state(0), round_state(1), round_state(2)], 1)


def frame_box(W, H, ix, iy, iw, ih, gold, trough):
    img = np.zeros((H, W, 4))
    for y in range(H):
        for x in range(W):
            if ix <= x < ix + iw and iy <= y < iy + ih:
                img[y, x] = trough
                continue
            cx, cy = min(x, W - 1 - x), min(y, H - 1 - y)
            if cx + cy < 1 and False:
                continue
            img[y, x, 3] = 255
            img[y, x, :3] = OUT
    return img


def hp_frame():
    W, H = 104, 14
    img = frame_box(W, H, 2, 2, 100, 10, None, (20, 6, 12, 150))
    gh, gm, gl = (236, 200, 110), (186, 146, 72), (116, 84, 44)
    for y in range(H):
        for x in range(W):
            if 2 <= x < 102 and 2 <= y < 12:
                continue
            cx, cy = min(x, W - 1 - x), min(y, H - 1 - y)
            if cx == 0 or cy == 0:
                if cx + cy == 0:
                    img[y, x] = 0
                continue
            top = y < H / 2
            left = x < 6
            right = x >= W - 6
            col = gh if (y == 1 and x > 1 and x < W - 2) else (gm if top else gl)
            if cx == 1 and not (cy == 1):
                col = gh if x == 1 else gl
            if cy == 1 and not top:
                col = gl
            img[y, x, :3] = col
    for (x, y) in ((1, 1), (W - 2, 1), (1, H - 2), (W - 2, H - 2)):
        img[y, x, :3] = (255, 236, 170)
    # tachuelas centrales
    for x in (26, 52, 78):
        img[0, x - 1:x + 2, :3] = (186, 146, 72)
        img[H - 1, x - 1:x + 2, :3] = (186, 146, 72)
    img[0, 0, 3] = 0
    img[0, W - 1, 3] = 0
    img[H - 1, 0, 3] = 0
    img[H - 1, W - 1, 3] = 0
    return img


def hp_fill():
    W, H = 100, 10
    rows = [(255, 150, 156), (246, 86, 100), (230, 48, 68), (210, 30, 54), (200, 26, 50), (186, 22, 46), (160, 16, 40), (132, 12, 34), (104, 8, 28), (78, 5, 22)]
    img = np.zeros((H, W, 4))
    for y in range(H):
        img[y, :, :3] = rows[y]
        img[y, :, 3] = 255
    for x in range(W):
        if x % 20 == 19:
            img[:, x, :3] *= 0.62
        if (x + 3 * 1) % 7 == 0:
            img[1, x, :3] = (255, 190, 190)
        if x % 4 == 0:
            img[6, x, :3] = rows[5]
    img[0, :, :3] = np.where((np.arange(W) % 20 == 19)[:, None], (200, 80, 90), rows[0])
    return img


def ult_frame():
    W, H = 84, 10
    img = frame_box(W, H, 2, 2, 80, 6, None, (10, 14, 28, 150))
    gh, gm, gl = (236, 200, 110), (186, 146, 72), (116, 84, 44)
    for y in range(H):
        for x in range(W):
            if 2 <= x < 82 and 2 <= y < 8:
                continue
            cx, cy = min(x, W - 1 - x), min(y, H - 1 - y)
            if cx == 0 or cy == 0:
                if cx + cy == 0:
                    img[y, x] = 0
                continue
            img[y, x, :3] = gh if (y == 1 or x == 1) else gl
            if y == H - 2:
                img[y, x, :3] = gl
    for x in (14, 28, 42, 56, 70):
        img[0, x, :3] = gm
        img[H - 1, x, :3] = gm
    return img


def ult_fill():
    W, H = 80, 6
    img = np.zeros((H, W, 4))
    for x in range(W):
        t = x / (W - 1)
        if t < 0.5:
            c = lerp((52, 110, 240), (150, 220, 255), t / 0.5)
        else:
            c = lerp((150, 220, 255), (255, 214, 96), (t - 0.5) / 0.5)
        for y in range(H):
            f = [1.25, 1.1, 1.0, 0.86, 0.7, 0.55][y]
            col = np.clip(np.array(c) * f + (30 if y == 0 else 0), 0, 255)
            img[y, x, :3] = col
            img[y, x, 3] = 255
        if x % 10 == 9:
            img[:, x, :3] *= 0.7
    return img


def boss_frame():
    W, H = 256, 18
    ix, iy, iw, ih = 6, 5, 244, 8
    img = np.zeros((H, W, 4))
    gh, gm, gl = (244, 206, 112), (190, 148, 74), (112, 80, 42)
    for y in range(H):
        for x in range(W):
            if ix <= x < ix + iw and iy <= y < iy + ih:
                img[y, x] = (18, 4, 10, 160)
                continue
            if y < 5:
                col = [OUT, gh, gm, gl, (46, 30, 28)][y]
            elif y >= 13:
                col = [(46, 30, 28), gl, gm, gl, OUT][y - 13]
                if y == 14:
                    col = gm
            else:
                col = None
            if col is None:
                # bandas laterales
                cx = min(x, W - 1 - x)
                col = [OUT, gh, gm, gl, gl, (46, 30, 28)][min(cx, 5)] if True else gm
            img[y, x, :3] = col
            img[y, x, 3] = 255
    # remates laterales: rombo con gema
    for side in (0, 1):
        for y in range(H):
            for x in range(6):
                X = x if side == 0 else W - 1 - x
                dxx = x
                dyy = abs(y - 8.5)
                if dxx + dyy * 0.6 < 6.5 and dxx < 6:
                    img[y, X, :3] = gm if (dxx + y) % 5 else gh
                    img[y, X, 3] = 255
        gx = 2 if side == 0 else W - 3
        img[8:10, gx:gx + 1, :3] = (200, 24, 48)
        img[7, gx, :3] = (255, 110, 120)
        for y in range(H):
            X = 0 if side == 0 else W - 1
            if abs(y - 8.5) > 7:
                img[y, X, 3] = 0
        img[0, 0 if side == 0 else W - 1, 3] = 0
        img[17, 0 if side == 0 else W - 1, 3] = 0
    # adorno central superior (diamante) y tachuelas
    for x in range(W):
        if abs(x - 127.5) < 9:
            hgt = int((9 - abs(x - 127.5)) / 9 * 2.2)
    for y in range(0, 5):
        for x in range(116, 140):
            if abs(x - 127.5) < 12 - y * 1.0 and y < 5:
                img[y, x, :3] = gh if y == 1 else (gm if y < 3 else gl)
    img[2, 126:130, :3] = (200, 24, 48)
    img[1, 127:129, :3] = (255, 120, 130)
    for x in range(32, 224, 32):
        if abs(x - 128) > 14:
            img[15, x - 1:x + 2, :3] = gh
            img[2, x - 1:x + 2, :3] = gh
    for x in (70, 186):
        img[1, x - 1:x + 2, :3] = (255, 236, 170)
    return img


def boss_fill():
    W, H = 244, 8
    rows = [(255, 130, 120), (240, 60, 70), (210, 30, 52), (190, 22, 46), (168, 16, 42), (138, 12, 36), (104, 8, 30), (70, 4, 22)]
    img = np.zeros((H, W, 4))
    for y in range(H):
        img[y, :, :3] = rows[y]
        img[y, :, 3] = 255
    for x in range(W):
        if x % 24 == 23:
            img[:, x, :3] *= 0.6
        if x % 6 == 2:
            img[1, x, :3] = (255, 170, 160)
    return img


def cursor():
    pc = PC(16, 16, 4)
    pc.poly([(14.5, 8), (5, 2), (7.2, 8), (5, 14)], (214, 170, 84))
    pc.poly([(14.5, 8), (5, 2), (7.2, 8)], (255, 232, 150))
    pc.poly([(14.5, 8), (7.2, 8), (5, 14)], (150, 108, 52))
    pc.poly([(5, 8), (1.5, 5.8), (0.3, 8), (1.5, 10.2)], (170, 128, 62))
    pc.poly([(5, 8), (1.5, 5.8), (0.3, 8)], (236, 200, 110))
    pc.px(11, 7, (255, 250, 220))
    return outline(pc.out(), 0.3, tint=(1, .8, .7))


def arrow():
    pc = PC(8, 8, 4)
    pc.poly([(6.4, 4), (2, 1.2), (2, 6.8)], (214, 170, 84))
    pc.poly([(6.4, 4), (2, 1.2), (2, 4)], (255, 232, 150))
    pc.poly([(6.4, 4), (2, 4), (2, 6.8)], (150, 108, 52))
    return outline(pc.out(), 0.3, tint=(1, .8, .7))


def vignette():
    W, H = 128, 72
    ys, xs = np.mgrid[0:H, 0:W]
    dx, dy = (xs + 0.5 - W / 2) / (W / 2), (ys + 0.5 - H / 2) / (H / 2)
    r = np.sqrt(dx * dx * 0.8 + dy * dy * 0.8)
    a = smooth((r - 0.55) / 0.75) ** 1.2 * 235
    img = np.zeros((H, W, 4))
    img[..., :3] = (8, 3, 12)
    img[..., 3] = a
    return img


def scanline():
    img = np.zeros((4, 4, 4))
    img[3, :, :3] = (0, 0, 0)
    img[3, :, 3] = 46
    return img


def build():
    save_ui('ui_panel', panel('n'))
    save_ui('ui_panel_light', panel('l'))
    save_ui('ui_panel_red', panel('r'))
    save_ui('ui_btn', btn())
    save_ui('ui_btn_round', round_btn())
    save_ui('ui_hp_frame', hp_frame())
    save_ui('ui_hp_fill', hp_fill())
    save_ui('ui_ult_frame', ult_frame())
    save_ui('ui_ult_fill', ult_fill())
    save_ui('ui_boss_frame', boss_frame())
    save_ui('ui_boss_fill', boss_fill())
    save_ui('ui_cursor', cursor())
    save_ui('ui_arrow', arrow())
    save_ui('ui_vignette', vignette())
    save_ui('ui_scanline', scanline())


def nine(im, corner, W, H):
    """Estira una imagen 9-slice a WxH."""
    w, h = im.size
    out = Image.new('RGBA', (W, H))
    c = corner
    xs = [(0, c, 0, c), (c, w - c, c, W - c), (w - c, w, W - c, W)]
    ys = [(0, c, 0, c), (c, h - c, c, H - c), (h - c, h, H - c, H)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            if dx1 <= dx0 or dy1 <= dy0:
                continue
            piece = im.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.NEAREST)
            out.paste(piece, (dx0, dy0))
    return out


def preview_hud():
    S = 3
    W, H = 480, 270
    bg = Image.new('RGBA', (W, H), (40, 36, 48, 255))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=(30 + y // 12, 22 + y // 20, 40 + y // 10, 255))
    def L(n):
        return Image.open(A + '/ui/' + n + '.png').convert('RGBA')
    bg.alpha_composite(L('ui_hp_frame'), (8, 8)); bg.alpha_composite(L('ui_hp_fill').crop((0, 0, 70, 10)), (10, 10))
    bg.alpha_composite(L('ui_ult_frame'), (8, 26)); bg.alpha_composite(L('ui_ult_fill').crop((0, 0, 50, 6)), (10, 28))
    bg.alpha_composite(L('ui_boss_frame'), (112, 240)); bg.alpha_composite(L('ui_boss_fill').crop((0, 0, 170, 8)), (118, 245))
    for i, (k, x) in enumerate((('ui_panel', 20), ('ui_panel_light', 120), ('ui_panel_red', 220))):
        bg.alpha_composite(nine(L(k), 8, 90, 60), (x, 60))
    b = L('ui_btn')
    for i in range(3):
        bg.alpha_composite(nine(b.crop((i * 48, 0, i * 48 + 48, 20)), 6, 80, 20), (330, 60 + i * 26))
    r = L('ui_btn_round')
    for i in range(3):
        bg.alpha_composite(r.crop((i * 40, 0, i * 40 + 40, 40)), (20 + i * 46, 140))
    bg.alpha_composite(L('ui_cursor'), (200, 150)); bg.alpha_composite(L('ui_arrow'), (230, 154))
    bg = bg.resize((W * S, H * S), Image.NEAREST)
    bg.convert('RGB').save(PREV + '/hud_mock.png')


if __name__ == '__main__':
    build()
    preview_hud()
