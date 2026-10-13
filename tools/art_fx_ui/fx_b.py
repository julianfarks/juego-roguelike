from common import *
from fx_a import NEUT, FIRE, arc_field, sweep_state, rays_field

ICE_P = {'d': (28, 62, 140), 'm': (70, 140, 220), 'l': (130, 206, 250), 'h': (206, 246, 255), 'w': (255, 255, 255), 'o': (22, 40, 100)}
ROCK_P = [(40, 28, 30), (74, 54, 46), (116, 86, 62), (160, 122, 82), (206, 168, 112), (240, 214, 160)]
LIGHTN = [(50, 80, 200), (90, 140, 255), (160, 205, 255), (235, 248, 255), (255, 255, 255)]


def facet_tri(pc, base_l, base_r, tip, P, ridge_off=-0.15):
    """Púa facetada: lado izq claro, der oscuro, arista blanca."""
    bx = (base_l[0] + base_r[0]) / 2
    by = (base_l[1] + base_r[1]) / 2
    rx = bx + (base_r[0] - base_l[0]) * ridge_off
    pc.poly([base_l, base_r, tip], P['m'])
    pc.poly([base_l, (rx, by), tip], P['l'])
    pc.poly([(rx, by), base_r, tip], P['m'])
    pc.poly([(rx + (base_r[0] - rx) * .55, by), base_r, tip], P['d'])
    pc.line((rx, by - 1), (tip[0], tip[1] + 2), P['h'], 0.9)
    pc.line((tip[0] - 0.3, tip[1] + 1.5), (tip[0], tip[1] + 3.5), P['w'], 1.0)


def ice_frames(kind):
    P = ICE_P
    W, H = 48, 64
    frames = []
    if kind == 'spike':
        hs = [8, 28, 54, 50, 50, 49, 40]
        for i, h in enumerate(hs):
            pc = PC(W, H, 4)
            by = 60
            for (dx, wd, k, tl) in ((-11, 6, 0.55, -6), (11, 7, 0.7, 7), (0, 11, 1.0, 0)):
                hh = max(3, h * k)
                if i == 0:
                    hh = max(3, h * k * 0.6)
                x = 24 + dx
                facet_tri(pc, (x - wd / 2, by), (x + wd / 2, by), (x + tl * hh / 40, by - hh), P)
            pc.poly([(10, by + 1), (38, by + 1), (36, by - 2), (12, by - 2)], P['m'])
            for dx in (-14, 14):
                pc.poly([(24 + dx - 3, by), (24 + dx + 3, by), (24 + dx, by - 5)], P['l'])
            im = outline(pc.out(), 0.3)
            if i == 6:
                im[..., 3] *= 0.7
            if i >= 2 and i <= 5:
                spark = blank(W, H)
                rs = RS(i)
                X, Y = grid(W, H)
                hh = star4(X, Y, rs.uniform(-6, 6), -18 + rs.uniform(-10, 10) , 3, 3) * 1.2
                spark = heat_rgba(hh, [(160, 230, 255), (230, 252, 255), (255, 255, 255)], thr=0.2, dith=0)
                im = over(im, spark)
            frames.append(im)
    elif kind == 'burst':
        X, Y = grid(W, H)
        rs = RS(61)
        shards = [(rs.uniform(0, 6.28), rs.uniform(14, 26), rs.uniform(3, 6)) for _ in range(11)]
        for i in range(8):
            u = i / 7
            pc = PC(W, H, 4)
            for (a, v, sz) in shards:
                t = u * 1.0
                x = 24 + v * math.cos(a) * ease_out(t * 1.3)
                y = 32 + v * math.sin(a) * ease_out(t * 1.3) * 0.9 + 14 * t * t
                s = sz * (1 - 0.65 * u) + 0.8
                ang = a + u * 2
                ca, sa = math.cos(ang), math.sin(ang)
                pts = [(x + ca * s * 1.3, y + sa * s * 1.3), (x - sa * s * .45, y + ca * s * .45), (x - ca * s * 1.3, y - sa * s * 1.3), (x + sa * s * .45, y - ca * s * .45)]
                pc.poly(pts, P['l'])
                pc.poly([pts[0], pts[1], pts[3]], P['h'])
                pc.poly([pts[1], pts[2], pts[3]], P['m'])
            im = outline(pc.out(), 0.3)
            if u < 0.5:
                h = disc(X, Y, 0, 0, 16 * (1 - u * 1.3) + 2) * 1.2 + ring(X, Y, 0, 0, 6 + 24 * u, 1.5) * (1 - u) + star4(X, Y, 0, 0, 20 * (1 - u), 4 + 4 * (1 - u)) + star4(X, Y, 0, 0, 4 + 4 * (1 - u), 20 * (1 - u))
                im = over(heat_rgba(np.clip(h, 0, 1.2), [(90, 170, 240), (160, 226, 255), (230, 252, 255), (255, 255, 255)], thr=0.15, dith=0.1), im)
            frames.append(im)
    else:
        pc = PC(W, H, 4)
        pts = [(8, 12), (14, 6), (34, 6), (40, 12), (41, 54), (36, 60), (12, 60), (7, 54)]
        pc.poly(pts, (120, 190, 240, 150))
        pc.poly([(10, 13), (15, 8), (33, 8), (37, 13), (37, 52), (11, 52)], (170, 225, 255, 120))
        pc.poly([(14, 10), (20, 10), (12, 30), (10, 30)], (235, 252, 255, 220))
        pc.poly([(8, 12), (14, 6), (34, 6), (40, 12), (36, 11), (14, 11)], (230, 250, 255, 255))
        pc.line((8, 14), (8, 54), (200, 238, 255, 255), 1.2)
        pc.line((40, 14), (40, 54), (70, 140, 215, 255), 1.4)
        pc.line((12, 60), (36, 60), (60, 120, 200, 255), 1.4)
        pc.line((12, 40), (30, 22), (240, 252, 255, 160), 0.9)
        pc.line((20, 52), (36, 34), (240, 252, 255, 110), 0.8)
        im = pc.out()
        # contorno: sólo sobre píxeles muy opacos (el borde)
        im = outline(im, 0.3, alpha_min=100)
        frames.append(im)
    return frames


def f_ice():
    save_sheet('fx', 'fx_ice', 48, 64, [('spike', ice_frames('spike'), 16, False), ('burst', ice_frames('burst'), 20, False), ('frozen', ice_frames('frozen'), 1, False)], (24, 60), [24, 44])


# ---------------- rayo ----------------
def bolt_path(seed, x0, y0, x1, y1, seg=9, jit=5.5):
    rs = RS(seed)
    pts = [(x0, y0)]
    n = int((y1 - y0) / seg)
    x = x0
    for k in range(1, n + 1):
        t = k / n
        x = x0 + (x1 - x0) * t + rs.uniform(-jit, jit) * (1 - 0.3 * t)
        pts.append((x, y0 + (y1 - y0) * t))
    pts[-1] = (x1, y1)
    return pts


def draw_path(X, Y, pts, r_core, upto=1.0):
    h = np.zeros_like(X)
    m = max(1, int(len(pts) * upto))
    for a, b in zip(pts[:m - 1], pts[1:m]):
        h = np.maximum(h, capsule(X, Y, a[0], a[1], b[0], b[1], r_core))
    return h


def lightning_frames(kind):
    W, H = 32, 128
    X, Y = grid(W, H, 16, 127)  # origen en la base
    frames = []
    if kind == 'bolt':
        for i in range(5):
            main = bolt_path(100 + (i if i != 3 else 1), 3, -126, 0, -3)
            br1 = bolt_path(210 + i % 2, main[5][0], main[5][1], 11, -70, 8, 4)
            br2 = bolt_path(230 + i % 2, main[10][0], main[10][1], -11, -40, 8, 3.5)
            up = [0.55, 1.0, 1.0, 1.0, 0.8][i]
            core = [0.9, 2.4, 2.9, 1.9, 1.1][i]
            h = draw_path(X, Y, main, core * 1.3, up) * 0.75 + draw_path(X, Y, main, core * 0.55, up) * 0.5
            if i >= 1:
                h = np.maximum(h, draw_path(X, Y, br1, core * .6) * .7)
                h = np.maximum(h, draw_path(X, Y, br2, core * .5) * .65)
            if i in (1, 2):
                h = np.maximum(h, np.clip(1 - np.abs(X) / 12, 0, 1) * 0.22 * (Y < 0))
            if i == 0:
                h *= 0.7
            h = np.clip(h, 0, 1.2)
            frames.append(heat_rgba(h, LIGHTN, thr=0.13, glow=0.35, dith=0.1, mul=[0.8, 1, 1, 0.95, 0.6][i]))
    else:
        rs = RS(300)
        sp = [(rs.uniform(-1.2, 1.2), rs.uniform(10, 20)) for _ in range(7)]
        for i in range(5):
            u = i / 4
            h = disc(X, Y, 0, -4, 10 * (1 - u) ** 0.8 + 1.5) * 1.3 * (u < .85)
            h = np.maximum(h, ring(X, Y * 4, 0, -2 * 4, 3 + 13 * u, 1.8 + 1.5 * (1 - u)) * (1 - u * .8))
            h = np.maximum(h, np.clip(1 - np.abs(X) / (3 * (1 - u) + 1), 0, 1) * (Y < 0) * (Y > -14 * (1 - u) - 6) * .7)
            for (vx, v) in sp:
                t = u * 0.9 + 0.08
                px_ = vx * v * t * 1.2
                py_ = -v * t * 1.1 + 22 * t * t - 2
                h = np.maximum(h, capsule(X, Y, px_, py_, px_ - vx * 2, py_ + 3 - 5 * t, 0.9, 0.3) * (1 - u * .7))
            for k in range(4):
                a = math.pi * (k + .5) / 4 + math.pi
                pts = bolt_path(400 + k * 7 + i, 0, -2, 0, -2, 9, 2)
                L = (4 + 12 * ease_out(u)) * (0.7 + 0.3 * (k % 2))
                p0 = (0, -2)
                p1 = (L * math.cos(a) * 1.2, -2 + L * math.sin(a) * .8)
                pm = ((p0[0] + p1[0]) / 2 + rs.uniform(-2, 2), (p0[1] + p1[1]) / 2 + rs.uniform(-2, 2))
                h = np.maximum(h, capsule(X, Y, *p0, *pm, 0.8) * (1 - u * .6))
                h = np.maximum(h, capsule(X, Y, *pm, *p1, 0.7) * (1 - u * .6))
            frames.append(heat_rgba(np.clip(h, 0, 1.2), LIGHTN, thr=0.13, glow=0.3, dith=0.1))
    return frames


def f_lightning():
    save_sheet('fx', 'fx_lightning', 32, 128, [('bolt', lightning_frames('bolt'), 28, False), ('ground', lightning_frames('ground'), 28, False)], (16, 127), [8, 120])


# ---------------- espinas ----------------
VINE = {'o': (14, 40, 24), 'd': (30, 90, 44), 'm': (58, 150, 62), 'l': (120, 214, 90), 'h': (200, 255, 150), 't': (236, 226, 170), 'p': (150, 60, 90)}


def vine_pts(x0, y0, h, amp, ph, n=14):
    pts = []
    for k in range(n + 1):
        t = k / n
        pts.append((x0 + amp * math.sin(t * 5.0 + ph) * t, y0 - h * t))
    return pts


def thorn_frames(kind):
    W, H = 32, 48
    P = VINE
    frames = []
    if kind == 'vine':
        grow = [0.2, 0.5, 0.82, 1.0, 1.0, 0.9, 0.6]
        for i, g in enumerate(grow):
            pc = PC(W, H, 4)
            for (x0, hh, amp, ph, wd) in ((16, 40, 5, 0.0, 3.2), (9, 24, 3.5, 2.0, 2.2), (23, 28, 4, 4.0, 2.4)):
                pts = vine_pts(x0, 46, hh * g, amp, ph + i * 0.12)
                if len(pts) < 2:
                    continue
                pc.lines(pts, P['o'], wd + 1.6)
                pc.lines(pts, P['m'], wd)
                pc.lines([(x - 0.5, y) for x, y in pts], P['l'], wd * .45)
                for k in range(2, len(pts) - 1, 2):
                    x, y = pts[k]
                    s = 1 if (k // 2) % 2 == 0 else -1
                    pc.poly([(x + s * 1, y - 1), (x + s * 1, y + 1.2), (x + s * (wd / 2 + 3.2), y - 2.2)], P['t'])
                if g > 0.7:
                    x, y = pts[-1]
                    pc.circ(x, y - 1, 1.8 * (wd / 3), P['p'])
                    pc.poly([(x, y - 3), (x + 1, y), (x - 1, y)], P['t'])
                for k in (5, 9):
                    if k < len(pts):
                        x, y = pts[k]
                        s = 1 if k == 5 else -1
                        pc.poly([(x, y), (x + s * 6, y - 3), (x + s * 3, y + 1)], P['l'])
                        pc.poly([(x, y), (x + s * 6, y - 3), (x + s * 3, y - 0.5)], P['h'])
            pc.ell(16, 46, 11, 2.2, P['d'])
            pc.ell(15, 45.4, 8, 1.2, P['m'])
            frames.append(outline(pc.out(), 0.3, tint=(0.8, 1, 0.8)))
    else:
        for i in range(8):
            u = i / 7
            pc = PC(W, H, 4)
            sh = 22 * min(1, u * 2.2)
            pc.lines([(16, 46), (16.5, 46 - sh * .5), (15.5, 46 - sh)], P['o'], 3.2)
            pc.lines([(16, 46), (16.5, 46 - sh * .5), (15.5, 46 - sh)], P['m'], 1.8)
            if u > 0.1:
                pc.poly([(16, 38), (8, 33), (12, 38.5)], P['l'])
                pc.poly([(16, 34), (24, 30), (20, 35.5)], P['l'])
            if u > 0.3:
                op = min(1, (u - 0.3) / 0.5)
                cy = 46 - sh
                for k in range(8):
                    a = -math.pi / 2 + (k - 3.5) * (0.32 + 0.12 * op)
                    L = 4 + 7 * op
                    ca, sa = math.cos(a), math.sin(a)
                    pc.poly([(15.5 + ca * 1, cy + sa * 1), (15.5 + ca * L - sa * 2.4, cy + sa * L + ca * 2.4), (15.5 + ca * (L + 1.6), cy + sa * (L + 1.6)), (15.5 + ca * L + sa * 2.4, cy + sa * L - ca * 2.4)], (255, 160, 196) if k % 2 else (255, 205, 224))
                    pc.line((15.5 + ca * 2, cy + sa * 2), (15.5 + ca * (L + .5), cy + sa * (L + .5)), (255, 240, 246), 0.8)
                pc.circ(15.5, cy, 2.6, (255, 214, 90))
                pc.circ(15.0, cy - .5, 1.2, (255, 244, 170))
            im = pc.out()
            im = outline(im, 0.28, tint=(1.0, .7, .9))
            X, Y = grid(W, H)
            if u > 0.4:
                h = ring(X, Y, 0, -6, 4 + 14 * (u - .4), 1.5) * (1 - (u - .4) / .6) * .9
                for k in range(5):
                    rr = RS(k + 8)
                    ph = (u * 1.3 + k * .2) % 1
                    h = np.maximum(h, star4(X, Y, rr.uniform(-9, 9), -2 - ph * 24, 1.8, 1.8) * (1 - ph))
                im = over(im, heat_rgba(h, [(110, 230, 140), (190, 255, 190), (255, 255, 255)], thr=0.15, dith=0.0))
            frames.append(im)
    return frames


def f_thorn():
    save_sheet('fx', 'fx_thorn', 32, 48, [('vine', thorn_frames('vine'), 16, False), ('bloom', thorn_frames('bloom'), 12, False)], (16, 46), [16, 40])


# ---------------- roca ----------------
def rock_pillar(pc, cx, base, h, w, seed, crumble=0.0):
    rs = RS(seed)
    P = ROCK_P
    # contorno de columna con corona irregular
    nt = 5
    tops = [h * (0.88 + rs.uniform(0, 0.12)) for _ in range(nt)]
    tops[2] = h
    pts_l = [(cx - w / 2 - 1, base), (cx - w / 2, base - h * 0.5), (cx - w / 2 + 0.6, base - tops[0])]
    xs = np.linspace(cx - w / 2 + 0.6, cx + w / 2 - 0.6, nt)
    top_pts = [(x, base - t - (3 if k % 2 == 0 else 0)) for k, (x, t) in enumerate(zip(xs, tops))]
    pts = [(cx - w / 2 - 1.5, base)] + [(cx - w / 2, base - h * .55)] + top_pts + [(cx + w / 2, base - h * .55), (cx + w / 2 + 1.5, base)]
    pc.poly(pts, P[2])
    # franja iluminada izq, oscura der
    pc.poly([(cx - w / 2 - 1.5, base), (cx - w / 2, base - h * .55)] + top_pts[:3] + [(cx - 1, base - h * 0.5), (cx - 2, base)], P[3])
    pc.poly([(cx - w / 2 - 1.5, base), (cx - w / 2, base - h * .55)] + top_pts[:2] + [(cx - w / 2 + 1.6, base - h * .6), (cx - w / 2 + 1.5, base)], P[4])
    pc.poly([(cx + w * .15, base), (cx + w * .1, base - h * .6)] + top_pts[3:] + [(cx + w / 2, base - h * .55), (cx + w / 2 + 1.5, base)], P[1])
    pc.poly([(cx + w * .34, base), (cx + w * .3, base - h * .55), (cx + w / 2, base - h * .55), (cx + w / 2 + 1.5, base)], P[0])
    # estratos y grietas
    for k in range(1, int(h // 9)):
        y = base - k * 9 - rs.uniform(-1, 1)
        pc.line((cx - w / 2 + 1, y), (cx + w / 2 - 1, y + rs.uniform(-1.5, 1.5)), P[0], 0.9)
        pc.line((cx - w / 2 + 1, y - 1), (cx - w * .1, y - 1), P[4], 0.8)
    pc.lines([(cx + 1, base - h * .7), (cx + 3, base - h * .55), (cx + 1.5, base - h * .4)], P[0], 0.9)


def rock_frames(kind):
    W, H = 32, 64
    frames = []
    P = ROCK_P
    if kind == 'pillar':
        hs = [10, 34, 60, 56, 56, 56, 40, 14]
        for i, h in enumerate(hs):
            pc = PC(W, H, 4)
            by = 61
            rock_pillar(pc, 16, by, h, 15 if i < 6 else 15, 7)
            if i >= 6:
                pass
            # montículo de tierra
            pc.ell(16, by + 1, 13, 3, P[1])
            pc.ell(14, by, 9, 2, P[2])
            for k in range(5):
                rs = RS(k + i * 3)
                if 1 <= i <= 4:
                    t = min(1, i / 3)
                    pc.poly([(5 + k * 5, by - 8 * t - rs.uniform(0, 12) * (i == 2 or i == 1)), (7.5 + k * 5, by - 10 * t - rs.uniform(0, 12) * (i == 2 or i == 1)), (6 + k * 5, by - 4 * t - 1)], P[3]) if False else None
            im = outline(pc.out(), 0.3, tint=(1.0, .85, .8))
            if i == 7:
                im[..., 3] *= 0.8
            frames.append(im)
    else:
        rs = RS(77)
        chunks = [(rs.uniform(-2.6, -0.5), rs.uniform(14, 26), rs.uniform(2.5, 5)) for _ in range(9)]
        for i in range(6):
            u = i / 5
            pc = PC(W, H, 4)
            for (a, v, sz) in chunks:
                x = 16 + v * math.cos(a) * u * 0.9 + (a % 2 - 1) * 2
                y = 56 + v * math.sin(a) * u * 1.8 + 40 * u * u
                s = sz * (1 - 0.5 * u)
                ang = u * 4 + a * 3
                ca, sa = math.cos(ang), math.sin(ang)
                q = [(x + ca * s - sa * s * .5, y + sa * s + ca * s * .5), (x - sa * s, y + ca * s), (x - ca * s, y - sa * s), (x + sa * s * .7, y - ca * s * .7)]
                pc.poly(q, P[2])
                pc.poly([q[2], q[3], q[0]], P[4])
                pc.poly([q[0], q[1], q[2]], P[1])
            im = outline(pc.out(), 0.3, tint=(1, .85, .8))
            X, Y = grid(W, H)
            nz = fbm(X * .2, Y * .2, 5, 2)
            d = np.clip(1 - np.hypot((X) / (10 + 8 * u), (Y - 26) / (4 + 3 * u)) + (nz - .5), 0, 1) * (1.3 - 1.2 * u)
            im = over(heat_rgba(d, [(98, 78, 66), (140, 112, 88), (186, 156, 120)], thr=0.25, dith=.1), im)
            frames.append(im)
    return frames


def f_rock():
    save_sheet('fx', 'fx_rock', 32, 64, [('pillar', rock_frames('pillar'), 16, False), ('debris', rock_frames('debris'), 18, False)], (16, 61), [16, 56])


# ---------------- estrella ----------------
STAR = [(140, 90, 220), (190, 140, 250), (230, 190, 255), (252, 232, 255), (255, 255, 255)]


def star_frames(kind):
    W = H = 48
    X, Y = grid(W, H)
    frames = []
    if kind == 'burst':
        rs = RS(81)
        sp = [(rs.uniform(0, 6.28), rs.uniform(10, 21), rs.uniform(1.6, 3.0)) for _ in range(8)]
        for i in range(7):
            u = i / 6
            sz = 22 * math.sin(math.pi * min(1, .2 + u * .85)) ** .8 + 2
            h = star4(X, Y, 0, 0, sz, sz * 0.17 + 1, 0.7)
            h = np.maximum(h, star4(X, Y, 0, 0, sz * .17 + 1, sz, 0.7))
            d = np.maximum(star4((X + Y) * .7071, (X - Y) * .7071, 0, 0, sz * .6, sz * .14 + .8, .7), star4((X + Y) * .7071, (X - Y) * .7071, 0, 0, sz * .14 + .8, sz * .6, .7))
            h = np.maximum(h, d * .85)
            h = np.maximum(h, disc(X, Y, 0, 0, 7 * (1 - u) + 2) * 1.3)
            h = np.maximum(h, ring(X, Y, 0, 0, 4 + 18 * u, 1.3) * (1 - u) * .8)
            for (a, v, s) in sp:
                dd = v * ease_out(u * 1.1)
                h = np.maximum(h, star4(X, Y, dd * math.cos(a), dd * math.sin(a), s * (1 - u * .6), s * (1 - u * .6)) * .95)
            frames.append(heat_rgba(np.clip(h, 0, 1.2), STAR, thr=0.12, dith=0.12, mul=1 - .4 * max(0, u - .8) / .2))
    else:
        for i in range(4):
            u = i / 4
            sz = [7, 12, 15, 10][i]
            h = np.maximum(star4(X, Y, 0, 0, sz, sz * .2 + 1, .7), star4(X, Y, 0, 0, sz * .2 + 1, sz, .7))
            h = np.maximum(h, disc(X, Y, 0, 0, sz * .45) * 1.2)
            for k in range(3):
                a = u * 2 * math.pi * 0.5 + k * 2.09
                h = np.maximum(h, disc(X, Y, 12 * math.cos(a), 10 * math.sin(a), 1.1) * .9)
            frames.append(heat_rgba(np.clip(h, 0, 1.2), STAR, thr=.12, dith=.1))
    return frames


def f_star():
    save_sheet('fx', 'fx_star', 48, 48, [('burst', star_frames('burst'), 20, False), ('twinkle', star_frames('twinkle'), 10, True)], (24, 24), [24, 24])


# ---------------- vacío ----------------
VOID = [(44, 14, 86), (84, 34, 156), (132, 64, 224), (186, 122, 255), (240, 214, 255)]


def void_frames(kind):
    W = H = 64
    X, Y = grid(W, H)
    frames = []
    r = np.hypot(X, Y)
    a = np.arctan2(Y, X)
    if kind == 'hole':
        for i in range(8):
            ph = math.pi * i / 8
            arms = 0.5 + 0.5 * np.cos(2 * (a - 0.32 * r + ph))
            body = np.clip(1 - r / 30, 0, 1) ** 0.9 * arms
            body += np.clip(1 - r / 30, 0, 1) * 0.25
            body = np.where(r > 9, body, 0)
            hh = body * 1.3
            hh = np.maximum(hh, ring(X, Y, 0, 0, 10.5, 1.8) * 1.2)
            hh = np.maximum(hh, ring(X, Y, 0, 0, 20 + 2 * math.sin(2 * math.pi * i / 8), 1.0) * .5)
            img = heat_rgba(np.clip(hh, 0, 1.2), VOID, thr=0.2, glow=0.25, dith=0.14)
            core = r < 9.2
            img[core] = [10, 3, 20, 255]
            sh = (r >= 8.2) & (r < 9.4)
            img[sh & (img[..., 3] > 0), :3] = (60, 24, 110)
            frames.append(img)
    else:
        rs = RS(91)
        pts = [(0, -27)]
        for k in range(1, 9):
            pts.append((rs.uniform(-4.5, 4.5), -27 + k * 6.75))
        pts[-1] = (0, 27)
        stars = [(rs.uniform(-6, 6), rs.uniform(-20, 20)) for _ in range(10)]
        wid = [0.6, 2.5, 4.5, 6.2, 7.0, 6.4, 3.0, 0.8]
        for i in range(8):
            w = wid[i]
            L = 1.0 if i < 6 else 0.9 - 0.3 * (i - 6)
            d = np.full(X.shape, 99.0)
            for p0, p1 in zip(pts[:-1], pts[1:]):
                q0 = (p0[0], p0[1] * L)
                q1 = (p1[0], p1[1] * L)
                vx, vy = q1[0] - q0[0], q1[1] - q0[1]
                L2 = vx * vx + vy * vy + 1e-9
                t = np.clip(((X - q0[0]) * vx + (Y - q0[1]) * vy) / L2, 0, 1)
                dd = np.hypot(X - (q0[0] + t * vx), Y - (q0[1] + t * vy))
                d = np.minimum(d, dd)
            taper = np.clip(1 - (np.abs(Y) / (27 * L + 1e-3)) ** 2, 0, 1)
            wy = w * taper + 0.01
            inner = d < wy * 0.7
            edge = (d < wy * 1.0 + 1.2) & ~inner
            glow = np.clip(1 - d / (wy + 7), 0, 1)
            hh = glow * 0.75
            img = heat_rgba(hh, VOID, thr=0.2, glow=0.2, dith=0.14)
            e = np.clip(1 - (d - wy * .7) / (wy * .3 + 1.5), 0, 1)
            img2 = heat_rgba(e * 1.2 * (d > wy * .7), VOID[2:] + [(255, 255, 255)], thr=0.2, dith=0.05)
            img = over(img, img2)
            fill = np.zeros_like(img)
            fill[inner] = [14, 5, 28, 255]
            img = over(img, fill)
            for (sx, sy) in stars:
                if inner[min(63, max(0, int(sy + 32))), min(63, max(0, int(sx + 32)))]:
                    xx, yy = int(sx + 32), int(sy + 32)
                    img[yy, xx] = [255, 240, 255, 255]
            frames.append(img)
    return frames


def f_void():
    save_sheet('fx', 'fx_void', 64, 64, [('hole', void_frames('hole'), 12, True), ('rift', void_frames('rift'), 14, False)], (32, 32), [32, 32])


# ---------------- sagrado ----------------
HOLY = [(200, 150, 56), (244, 206, 106), (255, 238, 168), (255, 251, 224), (255, 255, 255)]


def holy_frames():
    W, H = 48, 128
    X, Y = grid(W, H, 24, 127)
    frames = []
    ws = [1.8, 6, 13, 16, 14.5, 11, 7, 2.5]
    ints = [0.8, 1.0, 1.3, 1.3, 1.2, 1.0, .8, .5]
    for i in range(8):
        w = ws[i]
        prof = np.clip(1 - np.abs(X) / w, 0, 1)
        shim = 0.5 + 0.5 * np.sin(X * 0.9 + Y * 0.07 + i * 1.3)
        prof = prof ** 0.7 * (0.8 + 0.3 * shim)
        h = prof * (1 - np.clip(-Y / 140, 0, 1) ** 2 * 0.8) * ints[i]
        h = np.maximum(h, np.clip(1 - np.abs(X) / (w * .3 + .5), 0, 1) * 1.2)
        # base
        h = np.maximum(h, disc(X, Y * 2.4, 0, -4 * 2.4, 14 * min(1, w / 14) + 2) * 1.2 * (i > 0))
        h = np.maximum(h, ring(X, Y * 3, 0, -2 * 3, 4 + i * 2.6, 1.8) * (1 - i / 9) * .9 * (i > 0))
        for k in range(7):
            rr = RS(k + 20)
            ph = (i / 8.0 * 1.0 + rr.uniform()) % 1
            px_ = rr.uniform(-1, 1) * w * .8
            h = np.maximum(h, star4(X, Y, px_, -ph * 100 - 4, 1.8, 1.8) * (1 - ph) * (w > 6))
        frames.append(heat_rgba(np.clip(h, 0, 1.3), HOLY, thr=0.12, glow=0.25, dith=0.12))
    return frames


def f_holy():
    save_sheet('fx', 'fx_holy', 48, 128, [('beam', holy_frames(), 18, False)], (24, 127), [20, 120])


# ---------------- sombra ----------------
def shadow_frames(kind):
    W = H = 48
    X, Y = grid(W, H)
    frames = []
    if kind == 'puff':
        nz = fbm(X * 0.14, Y * 0.14, 12, 3)
        SM = [(150, 90, 235), (110, 56, 190), (74, 30, 130), (46, 14, 90), (30, 8, 62)]
        for i in range(7):
            u = i / 6
            R = 6 + 16 * ease_out(u * 1.3)
            yy = Y + 6 * u
            h = np.clip(1 - np.hypot(X, yy) / R + (nz - 0.5) * 1.0, 0, 1.0)
            h = h * (1.15 - 0.9 * u ** 1.4)
            frames.append(heat_rgba(np.clip(h, 0, 1), SM, thr=0.14, glow=0.0, dith=0.18))
    else:
        SB = [(70, 26, 130), (120, 60, 200), (186, 130, 255), (232, 210, 255)]
        nzf = fbm(X * 0.3, Y * 0.3, 14, 2)
        for i in range(5):
            u = i / 4
            hf, tf, fade = sweep_state(u)
            h = arc_field(X, Y, -14, 0, 24, -62 + 124 * tf, -62 + 124 * hf, 9, nz=nzf) * fade
            h2 = arc_field(X, Y, -10, 3, 20, -50 + 100 * tf, -50 + 100 * max(.1, hf - .2), 4, nz=nzf) * fade * .8
            h = np.maximum(h, h2)
            frames.append(heat_rgba(np.clip(h, 0, 1), SB, thr=0.12, glow=0.3, dith=0.1))
    return frames


def f_shadow():
    save_sheet('fx', 'fx_shadow', 48, 48, [('puff', shadow_frames('puff'), 18, False), ('blade', shadow_frames('blade'), 26, False)], (24, 24), [24, 24])


def build():
    f_ice(); f_lightning(); f_thorn(); f_rock(); f_star(); f_void(); f_holy(); f_shadow()


if __name__ == '__main__':
    build()
    preview_sheets('fx', ['fx_ice', 'fx_lightning', 'fx_thorn', 'fx_rock', 'fx_star', 'fx_void', 'fx_holy', 'fx_shadow'], PREV + '/fx_b.png', scale=2, maxw=2200)
