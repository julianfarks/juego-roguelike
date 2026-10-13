from common import *
from fx_a import NEUT, FIRE, arc_field, sweep_state, rays_field
from fx_b import bolt_path

DUST = [(150, 142, 152), (196, 188, 182), (236, 228, 214)]


def puff(pc, x, y, r, a=235):
    c0 = (150, 142, 152, a)
    c1 = (196, 188, 182, a)
    c2 = (238, 230, 216, a)
    pc.circ(x, y, r, c0)
    pc.circ(x - r * .15, y - r * .2, r * .8, c1)
    pc.circ(x - r * .3, y - r * .38, r * .45, c2)


def dust_frames(kind):
    W, H = 32, 16
    frames = []
    if kind == 'run':
        for i in range(5):
            u = i / 4
            pc = PC(W, H, 4)
            r = 3.0 + 3.2 * math.sin(math.pi * min(1, .25 + u * .75)) * (1 - u * .5)
            a = int(235 * (1 - u * .85))
            puff(pc, 14 - 7 * u, 13.2 - 2.5 * u, r, a)
            if u < .8:
                puff(pc, 19 - 4 * u, 14 - 1 * u, r * .55, a)
            frames.append(pc.out())
    elif kind == 'land':
        for i in range(6):
            u = i / 5
            pc = PC(W, H, 4)
            r = 2.8 + 3.4 * math.sin(math.pi * min(1, .2 + u * .8)) * (1 - u * .4)
            a = int(235 * (1 - u * .85))
            for s in (-1, 1):
                x = 16 + s * (3 + 11 * ease_out(u))
                puff(pc, x, 13.4 - u * 2, r, a)
                if u > .2:
                    puff(pc, 16 + s * (2 + 7 * ease_out(u)), 14, r * .6, a)
            frames.append(pc.out())
    else:
        for i in range(5):
            u = i / 4
            pc = PC(W, H, 4)
            for k in range(3):
                age = u - k * 0.22
                if age < 0:
                    continue
                r = 1.8 + 2.4 * math.sin(math.pi * min(1, .3 + age * .8))
                puff(pc, 24 - 7 * k - age * 5, 13.4 - age * 3, r, int(235 * max(0.1, 1 - age * .9)))
            frames.append(pc.out())
    return frames


def f_dust():
    save_sheet('fx', 'fx_dust', 32, 16, [('run', dust_frames('run'), 20, False), ('land', dust_frames('land'), 20, False), ('roll', dust_frames('roll'), 20, False)], (16, 15), [16, 8])


GREEN = [(40, 150, 90), (90, 224, 130), (190, 255, 200), (255, 255, 255)]


def cross(pc, x, y, s, a=255):
    arm = max(1, s // 3 + (1 if s >= 5 else 0))
    pc.rect(x - s / 2, y - arm / 2, x + s / 2, y + arm / 2, (30, 120, 70, a))
    pc.rect(x - arm / 2, y - s / 2, x + arm / 2, y + s / 2, (30, 120, 70, a))
    s2, a2 = s - 2, max(1, arm - 2)
    pc.rect(x - s / 2 + 1, y - arm / 2 + .5, x + s / 2 - 1, y + arm / 2 - .5, (110, 240, 150, a))
    pc.rect(x - arm / 2 + .5, y - s / 2 + 1, x + arm / 2 - .5, y + s / 2 - 1, (110, 240, 150, a))
    pc.px(x - 1, y - 1, (230, 255, 235, a))


def heal_frames():
    W, H = 24, 32
    frames = []
    cr = [(6, 0.0, 7), (17, 0.3, 5), (11, 0.55, 7), (4, 0.75, 5), (19, 0.9, 5)]
    for i in range(8):
        pc = PC(W, H, 4)
        t = i / 8
        for (x, ph, s) in cr:
            p = (t + ph) % 1.0
            y = 30 - p * 28
            sz = s if p < .75 else (3 if p < .9 else 1)
            if sz <= 1:
                pc.px(int(x), int(y), (200, 255, 210, 255))
            else:
                cross(pc, int(x) + (0.5 if sz % 2 == 0 else 0.5), int(y), sz)
        im = pc.out()
        im = outline(im, 0.3, tint=(.7, 1, .8)) if False else im
        X, Y = grid(W, H)
        h = np.zeros_like(X)
        for k in range(4):
            rr = RS(k + 60)
            ph = (t * 1 + k * .25) % 1
            h = np.maximum(h, disc(X, Y, rr.uniform(-9, 9), 14 - ph * 26, 0.9) * (1 - ph) * .9)
        h = np.maximum(h, np.clip(1 - np.hypot(X / 9, (Y - 14) / 3), 0, 1) * .6 * (1 - t))
        im = over(heat_rgba(h, GREEN, thr=.25, dith=.1), im)
        frames.append(im)
    return frames


def f_heal():
    save_sheet('fx', 'fx_heal', 24, 32, [('rise', heal_frames(), 14, False)], (12, 28), [12, 28])


def hexdist(x, y):
    x, y = np.abs(x), np.abs(y)
    return np.maximum(x * 0.5 + y * 0.8660254, x)


def hexgrid(X, Y):
    rx, ry = 1.0, 1.7320508
    ax = (X % rx) - rx / 2
    ay = (Y % ry) - ry / 2
    bx = ((X - rx / 2) % rx) - rx / 2
    by = ((Y - ry / 2) % ry) - ry / 2
    ga = ax * ax + ay * ay
    gb = bx * bx + by * by
    gx = np.where(ga < gb, ax, bx)
    gy = np.where(ga < gb, ay, by)
    return 0.5 - hexdist(gx, gy)


def shield_frames():
    W = H = 48
    X, Y = grid(W, H)
    r = np.hypot(X, Y) / 22.0
    inside = r < 1
    frames = []
    for i in range(6):
        t = i / 6
        z = np.sqrt(np.clip(1 - r * r, 0.02, 1))
        u_, v_ = X / (z * 0.5 + 0.5) / 5.5, Y / (z * 0.5 + 0.5) / 5.5
        e = hexgrid(u_, v_)
        sweep = np.clip(1 - np.abs(((X + Y) * 0.7 / 30 - (t * 2 - 1))) * 4, 0, 1)
        sweep2 = np.clip(1 - np.abs(((X + Y) * 0.7 / 30 - (t * 2 - 1) + 2)) * 4, 0, 1)
        sweep = np.maximum(sweep, sweep2)
        rim = np.clip(1 - np.abs(r - 0.97) / 0.07, 0, 1)
        fres = np.clip((r - 0.55) / 0.45, 0, 1) ** 2 * inside
        h = np.maximum(rim * 1.2, fres * 0.8)
        h = np.maximum(h, (e < 0.07) * inside * (0.25 + 0.7 * sweep) * (r > 0.12))
        h = np.maximum(h, disc(X, Y, -8, -9, 3.2) * 1.2)
        h = np.maximum(h, ring(X, Y, 0, 0, 22 * 0.8, 1.0) * 0.0)
        img = heat_rgba(np.clip(h, 0, 1.2), [(110, 180, 240), (160, 220, 255), (210, 244, 255), (255, 255, 255)], thr=0.16, dith=0.1)
        body = inside & (img[..., 3] == 0)
        img[body] = [120, 190, 255, 38 + int(0)]
        frames.append(img)
    return frames


def f_shield():
    save_sheet('fx', 'fx_shield', 48, 48, [('bubble', shield_frames(), 12, True)], (24, 24), [44, 44])


def whirl_frames():
    W = H = 64
    X, Y = grid(W, H)
    nz = fbm(X * .3, Y * .3, 5, 2)
    frames = []
    k = 3
    n = 6
    for i in range(n):
        ph = 360.0 / k * i / n
        h = np.zeros_like(X)
        for j in range(k):
            head = ph + j * 360.0 / k
            h = np.maximum(h, arc_field(X, Y, 0, 0, 22, head - 75, head, 6.0, nz=nz, pw=.6))
            h = np.maximum(h, arc_field(X, Y, 0, 0, 14, head - 150 + 40, head - 50, 3.0, nz=nz, pw=.6) * .75)
        h = np.maximum(h, ring(X, Y, 0, 0, 26, 0.9) * 0.3)
        frames.append(heat_rgba(np.clip(h, 0, 1.2), NEUT, thr=0.12, glow=0.3, dith=.1))
    return frames


def f_whirl():
    save_sheet('fx', 'fx_whirl', 64, 64, [('spin', whirl_frames(), 24, True)], (32, 32), [48, 48])


TELE = [(100, 140, 230), (150, 190, 250), (205, 230, 255), (245, 252, 255), (255, 255, 255)]


def tele_frames(kind):
    W, H = 48, 64
    X, Y = grid(W, H)
    frames = []
    rs = RS(120)
    ps = [(rs.uniform(-10, 10), rs.uniform(-22, 22), rs.uniform(0.3, 1)) for _ in range(14)]
    for i in range(8):
        u = i / 7
        t = u if kind == 'out' else 1 - u
        # t: 0 = presente, 1 = desvanecido
        wd = 11 * (1 - t) ** 0.7 + 1.5 * t
        hgt = 26 + 24 * t
        body = np.clip(1 - np.abs(X) / np.maximum(wd, .5), 0, 1) ** .6 * np.clip(1 - np.abs(Y) / hgt, 0, 1) ** .5
        bands = (np.sin(Y * 0.9 - t * 12) > -0.2 + 1.4 * t)
        h = body * 1.1 * bands * (1 - 0.6 * t)
        core = np.clip(1 - np.abs(X) / (wd * .35 + .5), 0, 1) * np.clip(1 - np.abs(Y) / (hgt * 1.05), 0, 1) * (0.9 - 0.7 * t + 0.0)
        h = np.maximum(h, core)
        if (kind == 'out' and u < .3) or (kind == 'in' and u > .7):
            flash = disc(X, Y, 0, 0, 20) * 1.2
            h = np.maximum(h, flash * 0.8)
        for (px_, py_, sp) in ps:
            y = py_ - t * 22 * sp * (1 if kind == 'out' else 1)
            pp = (t if kind == 'out' else t)
            h = np.maximum(h, disc(X, Y, px_ * (1 + .5 * t), y, 1.0) * (0.9 if 0.0 < t < 0.95 else 0))
        frames.append(heat_rgba(np.clip(h, 0, 1.3), TELE, thr=0.12, glow=0.2, dith=0.14))
    return frames


def f_tele():
    save_sheet('fx', 'fx_tele', 48, 64, [('out', tele_frames('out'), 22, False), ('in', tele_frames('in'), 22, False)], (24, 32), [20, 44])


def shock_frames():
    W, H = 128, 32
    X, Y = grid(W, H, 64, 31)
    nz = fbm(X * .2, Y * .2, 3, 2)
    frames = []
    for i in range(7):
        u = i / 6
        d = 8 + 52 * u ** 0.75
        th = 9 * (1 - u * .8) + 2
        hh = 26 * (1 - u * .55)
        h = np.zeros_like(X)
        for s in (-1, 1):
            xx = np.abs(X) * 1.0
            hy = np.clip(-Y / hh, 0, 1)
            front = d - hy ** 1.6 * 14
            inb = (xx <= front) & (xx > front - th * (1 - hy * .6)) & (hy < 1) & (Y <= 0.5)
            tt = np.clip((xx - (front - th)) / th, 0, 1)
            h = np.maximum(h, inb * (0.35 + 0.65 * tt) * (1 - hy * .5))
        h = h * (1 + 0.2 * (nz - .5))
        dust = np.clip(1 - np.abs(Y + 2) / 3.5, 0, 1) * (np.abs(X) < d + 4) * (nz > .55) * .5 * (1 - u)
        h = np.maximum(h, dust)
        frames.append(heat_rgba(np.clip(h, 0, 1.2), NEUT, thr=0.14, glow=0.0, dith=.14, mul=1 - .4 * max(0, u - .6) / .4))
    return frames


def f_shock():
    save_sheet('fx', 'fx_shock', 128, 32, [('wave', shock_frames(), 22, False)], (64, 31), [120, 20])


def smoke_frames():
    W = H = 64
    X, Y = grid(W, H)
    nz = fbm(X * .09, Y * .09, 33, 4)
    nz2 = fbm(X * .17 + 10, Y * .17, 34, 3)
    frames = []
    SM = [(54, 50, 62), (92, 88, 102), (140, 136, 150), (190, 186, 198), (224, 220, 232)]
    rs = RS(35)
    blobs = [(rs.uniform(-8, 8), rs.uniform(-4, 6), rs.uniform(8, 14), rs.uniform(0, 1)) for _ in range(6)]
    for i in range(8):
        u = i / 7
        d = np.zeros_like(X)
        for (bx, by, br, ph) in blobs:
            rr = br * 1.5 * (0.5 + 0.9 * ease_out(u * 1.2)) * (0.8 + .4 * ph)
            d = np.maximum(d, 1 - np.hypot(X - bx * (0.6 + u), Y - by + 14 * u * (0.6 + ph * .6)) / rr)
        d = d + (nz - .5) * 0.7 * np.clip(d + .4, 0, 1)
        d = d * (1.1 - 0.5 * u)
        gy, gx = np.gradient(ndi.gaussian_filter(d, 1.2))
        light = np.clip(0.55 + (-gx * 1.2 - gy * 1.5) * 4, 0, 1)
        mask = d > 0.12 + 0.55 * u ** 1.5 * (nz2 + .3)
        idx = np.clip(((light * 0.7 + np.clip(d, 0, 1) * 0.35) + bayer_field(H, W) * 0.12) * 5, 0, 4).astype(int)
        img = np.zeros((H, W, 4))
        img[..., :3] = np.array(SM, float)[idx]
        img[..., 3] = mask * 235 * (1 - .4 * u)
        frames.append(img)
    return frames


def f_smoke():
    save_sheet('fx', 'fx_smoke', 64, 64, [('big', smoke_frames(), 14, False)], (32, 32), [40, 40])


def ring_frames():
    W = H = 96
    X, Y = grid(W, H)
    frames = []
    for i in range(8):
        u = i / 7
        R = 6 + 40 * ease_out(u * 1.1)
        w = 5.5 * (1 - u) + 1.2
        h = ring(X, Y, 0, 0, R, w) * 1.15
        h = np.maximum(h, ring(X, Y, 0, 0, R * .8, w * .6) * .6 * (u > .1))
        h = np.maximum(h, disc(X, Y, 0, 0, R) * .25 * (1 - u))
        frames.append(heat_rgba(np.clip(h, 0, 1.2), NEUT, thr=0.14, glow=0.0, dith=.12, mul=1 - .5 * max(0, u - .6) / .4))
    return frames


def f_ring():
    save_sheet('fx', 'fx_ring', 96, 96, [('pulse', ring_frames(), 24, False)], (48, 48), [48, 48])


# ---------------- proyectiles ----------------
def proj_energy(kind, i):
    W = H = 24
    X, Y = grid(W, H)
    t = i / 4
    h = np.zeros_like(X)
    s2 = math.sin(2 * math.pi * t)
    c2 = math.cos(2 * math.pi * t)
    if kind == 'fireball':
        ramp = [(150, 30, 28), (232, 84, 24), (255, 148, 38), (255, 214, 90), (255, 250, 200)]
        h = disc(X, Y, 4, 0, 6.2 + .4 * s2) * 1.15
        for k in range(3):
            ph = (t + k / 3) % 1
            h = np.maximum(h, capsule(X, Y, -2 - ph * 8, (k - 1) * 3 + s2, 3 - ph * 5, (k - 1) * 2, 0.5, 4.5 * (1 - ph) + .3) * .9)
    elif kind == 'iceshard':
        ramp = [(60, 120, 210), (110, 190, 240), (170, 236, 255), (230, 252, 255), (255, 255, 255)]
        h = capsule(X, Y, -6, 0, 11, 0, 3.8, 0.4) * 1.1
        h = np.maximum(h, capsule(X, Y, -4, 0, 6, 0, 1.2, 1.2) * 1.3)
        for k in range(3):
            ph = (t + k / 3) % 1
            h = np.maximum(h, star4(X, Y, -8 - ph * 4, (k - 1) * 3, 1.3, 1.3) * .9 * (1 - ph))
    elif kind == 'bolt':
        ramp = [(60, 90, 220), (110, 160, 255), (180, 220, 255), (235, 248, 255), (255, 255, 255)]
        pts = [(-11, 0)]
        rs = RS(500 + i)
        for k in range(1, 6):
            pts.append((-11 + k * 4.4, rs.uniform(-4, 4)))
        pts.append((12, 0))
        for a, b in zip(pts[:-1], pts[1:]):
            h = np.maximum(h, capsule(X, Y, a[0], a[1], b[0], b[1], 1.5))
        h = np.maximum(h, disc(X, Y, 11, 0, 3) * 1.2)
    elif kind == 'voidorb':
        ramp = [(60, 20, 120), (110, 50, 200), (170, 100, 250), (230, 190, 255)]
        h = ring(X, Y, 0, 0, 7.4, 2.2) * 1.2
        arm = (0.5 + .5 * np.cos(2 * (np.arctan2(Y, X) - 0.4 * np.hypot(X, Y) + 2 * math.pi * t))) * np.clip(1 - np.hypot(X, Y) / 10, 0, 1)
        h = np.maximum(h, arm * 0.9)
        h = np.maximum(h, ring(X, Y, 0, 0, 10, 1) * .4)
    elif kind == 'bloodorb':
        ramp = [(90, 8, 28), (160, 14, 36), (220, 30, 52), (255, 90, 100), (255, 190, 190)]
        h = disc(X, Y, 3, 0, 6 + .4 * s2) * 1.2
        for k in range(3):
            ph = (t + k / 3) % 1
            h = np.maximum(h, capsule(X, Y, -4 - ph * 8, (k - 1) * 2.5, 1 - ph * 3, (k - 1) * 2, 0.6, 3.2 * (1 - ph) + .3) * .85)
            h = np.maximum(h, disc(X, Y, -6 - ph * 7, (k - 1) * 4 + ph * 3, 1.6) * .9)
    elif kind == 'star':
        ramp = [(140, 90, 220), (200, 130, 250), (240, 190, 255), (255, 240, 255), (255, 255, 255)]
        a = t * math.pi / 2
        for aa in (a, a + math.pi / 2):
            h = np.maximum(h, capsule(X, Y, 9 * math.cos(aa), 9 * math.sin(aa), -9 * math.cos(aa), -9 * math.sin(aa), 0.4, 2.6) * 1.0)
            h = np.maximum(h, capsule(X, Y, 0, 0, 9 * math.cos(aa), 9 * math.sin(aa), 2.6, .3))
            h = np.maximum(h, capsule(X, Y, 0, 0, -9 * math.cos(aa), -9 * math.sin(aa), 2.6, .3))
        h = np.maximum(h, disc(X, Y, 0, 0, 4) * 1.2)
    elif kind == 'crescent':
        ramp = NEUT
        h = arc_field(X, Y, -9, 0, 15, -80, 80, 5.5, pw=.45) * 1.2
        h = np.maximum(h, arc_field(X, Y, -12, 0, 14, -60, 60, 2.5, pw=.5) * .6 * (0.8 + .2 * s2))
        for k in range(2):
            h = np.maximum(h, capsule(X, Y, -10 - k * 2, (k * 2 - 1) * 3, -2, (k * 2 - 1) * 2.5, .3, .8) * .5)
    elif kind == 'poison':
        ramp = [(30, 90, 40), (60, 160, 60), (120, 220, 80), (200, 255, 140), (240, 255, 210)]
        h = disc(X, Y, 3, 0, 6.2 + .3 * s2) * 1.1
        for k in range(3):
            ph = (t + k / 3) % 1
            h = np.maximum(h, ring(X, Y, -5 - ph * 5, (k - 1) * 4 - ph * 2, 1.2 + ph, .9) * .9 * (1 - ph * .4))
        h = np.maximum(h, disc(X, Y, 1, 3, 1.5) * 0)
    elif kind == 'magma':
        ramp = [(60, 36, 36), (110, 50, 36), (200, 70, 24), (255, 140, 38), (255, 214, 90)]
        rr = 7.5 + 0.5 * np.sin(np.arctan2(Y, X) * 3 + 2 * math.pi * t)
        h = np.clip(1 - np.hypot(X - 3, Y) / rr, 0, 1) * 1.1
        crack = (np.abs(np.sin((X * .9 + Y * .7) * .9 + 2)) < .15) * (h > 0.2)
        h = np.where(crack, 1.15, np.clip(h * .85, 0, .5))
        for k in range(3):
            ph = (t + k / 3) % 1
            h = np.maximum(h, disc(X, Y, -4 - ph * 8, (k - 1) * 3.5, 1.3 * (1 - ph * .5)) * 1.0)
    elif kind == 'holy':
        ramp = [(214, 150, 50), (255, 206, 96), (255, 240, 170), (255, 252, 226), (255, 255, 255)]
        h = disc(X, Y, 2, 0, 5.2 + .4 * s2) * 1.3
        h = np.maximum(h, capsule(X, Y, -10, 0, 12, 0, .8, .8) * .9)
        h = np.maximum(h, capsule(X, Y, 2, -9, 2, 9, .8, .8) * (.7 + .2 * c2))
        h = np.maximum(h, ring(X, Y, 2, 0, 8, 1) * .5)
    elif kind == 'leaf':
        ramp = [(30, 90, 44), (58, 150, 62), (120, 214, 90), (200, 255, 150)]
        ang = 0.35 * s2
        ca, sa = math.cos(ang), math.sin(ang)
        xr, yr = X * ca + Y * sa, -X * sa + Y * ca
        sq = 1 - 0.25 * (i % 2)
        shape = np.clip(1 - (np.abs(xr + 1) / 10) ** 1.7 - (np.abs(yr) / (4.4 * sq)) ** 2, 0, 1)
        h = (shape > 0) * (0.45 + 0.9 * shape)
        h = np.maximum(h, capsule(X, Y, -10, 0, 8, 0, .5, .5) * 0.0)
        vein = (np.abs(yr) < .6) & (xr > -9) & (xr < 8)
        h = np.where(vein & (shape > 0.05), 1.15, h)
    return heat_rgba(np.clip(h, 0, 1.2), ramp, thr=0.14, dith=.1)


def proj_obj(kind, i):
    W = H = 24
    pc = PC(W, H, 4)
    t = i / 4
    if kind == 'arrow':
        pc.line((2, 12), (18, 12), (120, 80, 48), 1.4)
        pc.line((2, 11.6), (18, 11.6), (176, 126, 76), 0.7)
        pc.poly([(23, 12), (17, 9.2), (18.6, 12), (17, 14.8)], (200, 210, 224))
        pc.poly([(23, 12), (17, 9.2), (18.6, 12)], (240, 246, 255))
        pc.poly([(1, 12), (5, 9), (6.5, 9), (4.5, 12)], (200, 60, 60))
        pc.poly([(1, 12), (5, 15), (6.5, 15), (4.5, 12)], (150, 36, 44))
        pc.px(int(5 + 12 * t), 11, (255, 255, 255)) if i % 2 == 0 else None
    elif kind == 'dagger':
        wob = [0, .6, 0, -.6][i]
        pc.poly([(7, 11 + wob), (20, 10 + wob), (23, 12 + wob), (19, 13.4 + wob), (7, 13 + wob)], (200, 212, 232))
        pc.poly([(7, 11 + wob), (20, 10 + wob), (23, 12 + wob), (7, 12 + wob)], (244, 250, 255))
        pc.rect(5, 9.5 + wob, 7, 14.5 + wob, (90, 60, 120))
        pc.rect(1.5, 11 + wob, 5, 13 + wob, (60, 40, 90))
        pc.px(2, 11 + wob, (255, 200, 90))
        gx = 8 + 12 * t
        pc.rect(gx, 11 + wob, gx + 2, 12 + wob, (255, 255, 255))
    elif kind == 'blade':
        pc.poly([(5, 10.5), (19, 10.5), (23.5, 12), (19, 13.5), (5, 13.5)], (180, 196, 224))
        pc.poly([(5, 10.5), (19, 10.5), (23.5, 12), (5, 12)], (236, 244, 255))
        pc.rect(3.5, 8, 5.5, 16, (255, 154, 60))
        pc.rect(0.5, 11, 3.5, 13, (150, 90, 50))
        gx = 6 + 14 * t
        pc.rect(gx, 11, gx + 3, 12, (255, 255, 255))
    elif kind == 'spike':
        pc.poly([(2, 7), (8, 6), (23, 12), (8, 18), (2, 17)], (110, 82, 60))
        pc.poly([(2, 7), (8, 6), (23, 12), (3, 12)], (190, 148, 96))
        pc.poly([(2, 7), (8, 6), (14, 9), (3, 11)], (232, 196, 140))
        pc.poly([(3, 17), (8, 18), (23, 12), (12, 14)], (70, 50, 42))
        pc.px(10 + (i % 2), 10, (255, 240, 200))
    elif kind == 'bone':
        ang = t * math.pi / 2 * 1.0 + 0.2
        ca, sa = math.cos(ang), math.sin(ang)
        cx, cy = 12, 12
        def P(x, y):
            return (cx + x * ca - y * sa, cy + x * sa + y * ca)
        pc.line(P(-7, 0), P(7, 0), (150, 140, 120), 2.2)
        pc.line(P(-7, -.4), P(7, -.4), (226, 218, 192), 1.2)
        for sx in (-1, 1):
            for sy in (-1, 1):
                q = P(sx * 7.5, sy * 1.8)
                pc.circ(q[0], q[1], 1.9, (232, 224, 198))
                pc.circ(q[0] - .4, q[1] - .4, 1.0, (252, 248, 232))
    elif kind == 'dagger2':
        pass
    return outline(pc.out(), 0.3, tint=(1, .9, 1))


def proj_frames(kind):
    fr = []
    for i in range(4):
        if kind in ('arrow', 'dagger', 'blade', 'spike', 'bone'):
            fr.append(proj_obj(kind, i))
        else:
            fr.append(proj_energy(kind, i))
    return fr


PROJ = ['arrow', 'dagger', 'fireball', 'iceshard', 'bolt', 'voidorb', 'bloodorb', 'leaf', 'star', 'blade', 'crescent', 'poison', 'magma', 'holy', 'spike', 'bone']


def f_proj():
    save_sheet('fx', 'fx_proj', 24, 24, [(k, proj_frames(k), 16, True) for k in PROJ], (12, 12), [8, 8])


def build():
    f_dust(); f_heal(); f_shield(); f_whirl(); f_tele(); f_shock(); f_smoke(); f_ring(); f_proj()


if __name__ == '__main__':
    build()
    preview_sheets('fx', ['fx_dust', 'fx_heal', 'fx_shield', 'fx_whirl', 'fx_tele', 'fx_shock', 'fx_smoke', 'fx_ring'], PREV + '/fx_c.png', scale=2, maxw=2200)
    preview_sheets('fx', ['fx_proj'], PREV + '/fx_proj.png', scale=5, maxw=1200, bg=(30, 24, 40))
