from common import *

NEUT = [(120, 134, 184), (166, 180, 222), (208, 220, 244), (242, 247, 255), (255, 255, 255)]
FIRE = [(92, 18, 28), (170, 36, 26), (232, 84, 24), (255, 148, 38), (255, 208, 84), (255, 246, 190)]
BLOOD = [(70, 6, 22), (126, 10, 30), (186, 18, 40), (228, 48, 62), (255, 120, 120)]
WARM = [(214, 120, 40), (255, 176, 70), (255, 222, 130), (255, 248, 210), (255, 255, 255)]


def arc_field(X, Y, cx, cy, R, tail, head, hw, pw=0.55, nz=None, b0=0.7, b1=0.4):
    dx, dy = X - cx, Y - cy
    r = np.hypot(dx, dy)
    a = np.degrees(np.arctan2(dy, dx))
    span = head - tail
    if abs(span) < 2:
        return np.zeros_like(X)
    q = (((a - tail) * np.sign(span)) % 360) / abs(span)
    valid = q <= 1.0
    qc = np.clip(q, 0, 1)
    w = hw * qc ** pw * (1 - 0.85 * np.clip((qc - 0.86) / 0.14, 0, 1) ** 2)
    if nz is not None:
        w = w * (1 + 0.3 * (nz - 0.5))
    h = np.clip(1 - np.abs(r - R) / np.maximum(w, 0.05), 0, 1)
    h = np.where(valid & (w > 0.25), h, 0) * (b0 + b1 * qc)
    return h


def sweep_state(u):
    hf = min(1.0, 0.2 + 0.8 * (u / 0.5) ** 0.75)
    tf = 0.0 if u < 0.2 else 0.9 * ((u - 0.2) / 0.8) ** 1.3
    fade = 1.0 - 0.4 * max(0, (u - 0.6) / 0.4)
    return hf, tf, fade


def slash_frames(W, H, n, cx, cy, R, a0, a1, hw, ramp=NEUT, seed=1, echo=None, sparks=6, burst=False):
    X, Y = grid(W, H)
    rs = RS(seed)
    nzf = fbm(X * 0.35, Y * 0.35, seed, 2)
    sp = [(rs.uniform(0.2, 1.0), rs.uniform(-1, 1), rs.uniform(2, 7)) for _ in range(sparks)]
    frames = []
    for i in range(n):
        u = i / (n - 1)
        hf, tf, fade = sweep_state(u)
        tail, head = a0 + (a1 - a0) * tf, a0 + (a1 - a0) * hf
        h = arc_field(X, Y, cx, cy, R, tail, head, hw * 1.45, nz=nzf) * fade
        if echo:
            er, ew, lag = echo
            hf2, tf2 = max(0.05, hf - lag), tf
            h = np.maximum(h, arc_field(X, Y, cx, cy, R * er, a0 + (a1 - a0) * tf2, a0 + (a1 - a0) * hf2, hw * ew * 1.4, nz=nzf) * fade * 0.9)
        if 0.0 < u < 0.85:
            for (pos, off, dist) in sp:
                ang = math.radians(a0 + (a1 - a0) * min(hf, pos * hf))
                rr = R + off * hw * 0.8 + dist * (0.4 + u)
                h = np.maximum(h, disc(X, Y, cx + rr * math.cos(ang), cy + rr * math.sin(ang), 1.1) * 0.95 * (1 - u))
        if burst and i >= n - 4:
            ang = math.radians(a1)
            bx, by = cx + R * math.cos(ang), cy + R * math.sin(ang)
            k = (i - (n - 4)) / 3.0
            h = np.maximum(h, ring(X, Y, bx, by, 3 + 7 * k, 1.3) * (1 - k) * 0.9)
        frames.append(heat_rgba(h, ramp, thr=0.12, glow=0.28))
    return frames


def f_slash_sword():
    W = H = 64
    rows = [
        ('s1', slash_frames(W, H, 5, -12, 0, 26, -72, 72, 5.0, seed=3, echo=(0.8, 0.4, 0.25)), 24, False),
        ('s2', slash_frames(W, H, 5, -12, 2, 25, 70, -70, 4.6, seed=4, echo=(0.82, 0.4, 0.25)), 24, False),
        ('s3', slash_frames(W, H, 6, -16, 0, 29, -112, 100, 6.4, seed=5, echo=(0.76, 0.45, 0.3), sparks=9, burst=True), 22, False),
    ]
    save_sheet('fx', 'fx_slash_sword', W, H, rows, (32, 32), [20, 20])


def f_slash_big():
    W = H = 96
    rows = [
        ('s1', slash_frames(W, H, 6, -22, 4, 42, -78, 76, 8.0, seed=6, echo=(0.8, 0.4, 0.2), sparks=8), 22, False),
        ('s2', slash_frames(W, H, 6, -22, 0, 41, 80, -80, 7.6, seed=7, echo=(0.82, 0.4, 0.2), sparks=8), 22, False),
        ('s3', slash_frames(W, H, 7, -26, 2, 46, -120, 110, 10.5, seed=8, echo=(0.78, 0.45, 0.28), sparks=12, burst=True), 20, False),
    ]
    save_sheet('fx', 'fx_slash_big', W, H, rows, (48, 48), [32, 32])


def stab_frames(variant):
    W, H, n = 80, 32, 5
    X, Y = grid(W, H)
    rs = RS(10 + variant)
    nzf = fbm(X * 0.3, Y * 0.3, 4 + variant, 2)
    frames = []
    streaks = [(rs.uniform(-9, 9), rs.uniform(10, 24), rs.uniform(0.5, 1.2)) for _ in range(5)]
    for i in range(n):
        u = i / (n - 1)
        xh = -34 + 74 * ease_out(min(1, u / 0.5))
        xt = -38 + 52 * (max(0, u - 0.15) / 0.85) ** 1.2
        if xh - xt < 4:
            xt = xh - 4
        s = np.clip((X - xt) / (xh - xt), 0, 1)
        inside = (X >= xt) & (X <= xh)
        hwmax = (5.2 if variant == 0 else 4.0) * (1 - 0.35 * max(0, u - 0.5) / 0.5)
        prof = (s ** 0.55) * ((1 - s) ** 0.45) / 0.5 if True else s
        prof = np.clip(prof, 0, 1) * (s > 0.001)
        yoff = 0 if variant == 0 else 1.5 * math.sin(u * 3)
        hw = hwmax * (0.25 + 0.75 * prof) * (1 + 0.15 * (nzf - 0.5))
        hh = np.clip(1 - np.abs(Y - yoff) / np.maximum(hw, 0.1), 0, 1) * inside
        hh = hh * (0.5 + 0.5 * s ** 0.8)
        # filo central blanco: línea fina más brillante
        core = np.clip(1 - np.abs(Y - yoff) / 1.1, 0, 1) * inside * (s > 0.15)
        h = np.maximum(hh, core * 0.95)
        for (yo, ln, wd) in streaks:
            sx1 = xh - 8 - 10 * u
            sx0 = sx1 - ln * (1 - 0.3 * u)
            h = np.maximum(h, capsule(X, Y, sx0, yo * 1.1, sx1, yo * 1.1, 0.3, wd * 0.9) * 0.55 * (1 - u * 0.7))
        if u < 0.7:
            h = np.maximum(h, star4(X, Y, xh, yoff, 9 * (1 - u * 0.5), 5.5 * (1 - u * 0.5)) * 0.95)
        frames.append(heat_rgba(h, NEUT, thr=0.12, glow=0.25, mul=1 - 0.35 * max(0, u - 0.7) / 0.3))
    return frames


def f_stab():
    save_sheet('fx', 'fx_stab', 80, 32, [('s1', stab_frames(0), 26, False), ('s2', stab_frames(1), 26, False)], (40, 16), [40, 12])


# ---------------- impactos ----------------
def rays_field(X, Y, cx, cy, angs, r0, r1, w0, w1=0.3):
    h = np.zeros_like(X)
    for a in angs:
        ca, sa = math.cos(a), math.sin(a)
        h = np.maximum(h, capsule(X, Y, cx + r0 * ca, cy + r0 * sa, cx + r1 * ca, cy + r1 * sa, w0, w1))
    return h


def hit_frames(kind):
    W = H = 32
    X, Y = grid(W, H)
    rs = RS({'spark': 21, 'big': 22, 'crit': 23, 'magic': 24, 'shock': 25, 'ice': 26}[kind])
    n = {'spark': 5, 'big': 6, 'crit': 6, 'magic': 5, 'shock': 5, 'ice': 5}[kind]
    ramp = {'spark': WARM, 'big': NEUT, 'crit': [(230, 110, 30), (255, 176, 60), (255, 224, 120), (255, 250, 200), (255, 255, 255)],
            'magic': [(110, 120, 230), (150, 170, 255), (200, 220, 255), (240, 248, 255), (255, 255, 255)],
            'shock': [(60, 90, 220), (110, 160, 255), (180, 220, 255), (235, 248, 255), (255, 255, 255)],
            'ice': [(60, 120, 210), (110, 190, 240), (170, 236, 255), (230, 252, 255), (255, 255, 255)]}[kind]
    base = rs.uniform(0, 6.28)
    frames = []
    for i in range(n):
        u = i / (n - 1)
        h = np.zeros_like(X)
        if kind == 'spark':
            angs = [base + k * 2 * math.pi / 7 + rs.uniform(-.2, .2) for k in range(7)]
            r0 = 1 + 7 * u
            r1 = r0 + 9 * (1 - u) ** 0.6 + 2
            h = rays_field(X, Y, 0, 0, angs, r0, r1, 1.5 * (1 - u * .5), 0.2)
            h = np.maximum(h, disc(X, Y, 0, 0, 7 * (1 - u) ** 1.2 + 1) * 1.2 * (u < 0.8))
        elif kind == 'big':
            angs = [base + k * 2 * math.pi / 9 for k in range(9)]
            r0 = 2 + 8 * u
            h = rays_field(X, Y, 0, 0, angs, r0, r0 + 11 * (1 - u) ** 0.5 + 2, 2.0 * (1 - u * .6), 0.2)
            h = np.maximum(h, ring(X, Y, 0, 0, 4 + 10 * u, 1.6) * (1 - u) * 0.9)
            h = np.maximum(h, disc(X, Y, 0, 0, 9 * (1 - u) ** 1.2 + 1.5) * 1.2 * (u < .75))
        elif kind == 'crit':
            sz = 15 * (math.sin(math.pi * min(1, 0.25 + u * 0.95)) ** 0.7 + 0.1)
            h = rays_field(X, Y, 0, 0, [0, math.pi / 2, math.pi, -math.pi / 2], 0, sz, 2.6, 0.2)
            h = np.maximum(h, rays_field(X, Y, 0, 0, [0.785 + k * 1.5708 for k in range(4)], 0, sz * .68, 1.8, 0.2) * 0.95)
            h = np.maximum(h, disc(X, Y, 0, 0, 8 * (1 - u) + 2.5) * 1.3)
            h = np.maximum(h, ring(X, Y, 0, 0, 3 + 12 * u, 1.3) * (1 - u) * .8)
        elif kind == 'magic':
            h = ring(X, Y, 0, 0, 3 + 11 * u, 2.0 - u) * (1 - u * .6)
            h = np.maximum(h, disc(X, Y, 0, 0, 6 * (1 - u) + 1.5) * 1.2 * (u < .8))
            for k in range(5):
                a = base + k * 1.2566 + u * 1.0
                rr = 5 + 8 * u + (k % 2) * 2
                h = np.maximum(h, star4(X, Y, rr * math.cos(a), rr * math.sin(a), 3.2 * (1 - u * .6), 3.2 * (1 - u * .6)) * 0.95)
        elif kind == 'shock':
            for k in range(5):
                a = base + k * 1.2566
                r = 3 + 12 * ease_out(u)
                pts = [(0, 0)]
                px_, py_ = 0, 0
                rr_ = RS(k + 50 + i)
                steps = 4
                for s_ in range(steps):
                    t = (s_ + 1) / steps
                    rad = t * r
                    jit = rr_.uniform(-2.2, 2.2) * (1 - u * .4)
                    pts.append((rad * math.cos(a) - jit * math.sin(a), rad * math.sin(a) + jit * math.cos(a)))
                for p0, p1 in zip(pts[:-1], pts[1:]):
                    h = np.maximum(h, capsule(X, Y, p0[0], p0[1], p1[0], p1[1], 1.0 * (1 - u * .5) + .3))
            h = np.maximum(h, disc(X, Y, 0, 0, 6 * (1 - u) + 1.2) * 1.2 * (u < .7))
        elif kind == 'ice':
            angs = [base + k * 2 * math.pi / 6 for k in range(6)]
            r0 = 1.5 + 6 * u
            r1 = r0 + 8.5 * (1 - u * .5)
            for a in angs:
                ca, sa = math.cos(a), math.sin(a)
                h = np.maximum(h, capsule(X, Y, ca * r0, sa * r0, ca * r1, sa * r1, 2.0 * (1 - u * .4), 0.2))
            h = np.maximum(h, star4(X, Y, 0, 0, 7 * (1 - u) + 1, 7 * (1 - u) + 1) * 1.2)
        fade = 1 - 0.3 * max(0, u - 0.7) / 0.3
        frames.append(heat_rgba(h, ramp, thr=0.14, glow=0.0, mul=fade))
    return frames


def f_hit():
    rows = [(k, hit_frames(k), fps, False) for k, fps in (('spark', 30), ('big', 28), ('crit', 28), ('magic', 28), ('shock', 28), ('ice', 28))]
    save_sheet('fx', 'fx_hit', 32, 32, rows, (16, 16), [16, 16])


# ---------------- sangre ----------------
def blood_frames(kind):
    W = H = 48
    X, Y = grid(W, H)
    rs = RS(31 if kind == 'splat' else 32)
    n = 6
    drops = []
    for k in range(14 if kind == 'splat' else 0):
        a = math.radians(rs.uniform(-160, -20)) if k < 10 else math.radians(rs.uniform(-30, 30))
        v = rs.uniform(10, 24)
        drops.append((a, v, rs.uniform(1.3, 2.6)))
    frames = []
    nz = fbm(X * 0.18, Y * 0.18, 9, 3)
    for i in range(n):
        u = i / (n - 1)
        h = np.zeros_like(X)
        if kind == 'splat':
            R = 13 * math.sin(math.pi * min(1, 0.2 + u * 0.65)) + 2.5
            blob = np.clip(1 - np.hypot(X, Y) / R + (nz - 0.5) * 0.9, 0, 1) * (1.3 - u * 0.9)
            h = blob
            for (a, v, r) in drops:
                t = 0.08 + u * 0.55
                px_ = v * math.cos(a) * t * 1.4
                py_ = v * math.sin(a) * t * 1.4 + 38 * t * t
                pp = max(0, t - 0.1)
                qx = v * math.cos(a) * pp * 1.4
                qy = v * math.sin(a) * pp * 1.4 + 38 * pp * pp
                h = np.maximum(h, capsule(X, Y, qx, qy, px_, py_, r * 0.7, r * 1.4 * (1 - u * 0.5)) * 0.95)
        else:
            for k in range(6):
                rr = RS(k + 5)
                a = rr.uniform(0, 6.28)
                d = rr.uniform(2, 11) * (0.3 + u)
                cx, cy = d * math.cos(a), d * math.sin(a) - 4 * u
                R = (6 + rr.uniform(0, 6)) * (0.5 + u * 0.9)
                h += np.clip(1 - np.hypot(X - cx, Y - cy) / R + (nz - 0.5) * 0.7, 0, 1) * 0.8
            h = h * (1.0 - u * 0.95) * 0.9
        frames.append(heat_rgba(h, BLOOD, thr=0.16, glow=0.0, mul=1.0 if kind == 'splat' else 0.82, dith=0.2))
    return frames


def f_blood():
    save_sheet('fx', 'fx_blood', 48, 48, [('splat', blood_frames('splat'), 24, False), ('mist', blood_frames('mist'), 20, False)], (24, 24), [24, 24])


# ---------------- explosión ----------------
def explosion_frames(kind):
    W = H = 96
    X, Y = grid(W, H)
    n = 9
    nz = fbm(X * 0.09, Y * 0.09, 40 if kind == 'a' else 41, 4)
    nz2 = fbm(X * 0.2, Y * 0.2, 45, 3)
    rs = RS(44 if kind == 'a' else 45)
    parts = [(rs.uniform(0, 6.28), rs.uniform(30, 52), rs.uniform(0.8, 1.8)) for _ in range(16)]
    ramp = FIRE if kind == 'a' else [(100, 120, 200), (140, 170, 240), (186, 214, 255), (226, 242, 255), (250, 253, 255), (255, 255, 255)]
    smk = [(36, 28, 34), (62, 48, 54), (96, 76, 80)] if kind == 'a' else [(70, 80, 140), (100, 120, 190), (140, 160, 220)]
    frames = []
    for i in range(n):
        u = i / (n - 1)
        R = 40 * ease_out(min(1, u * 1.5)) + 3
        I = 1.35 - 1.25 * u ** 1.1
        r = np.hypot(X, Y + 3 * u)
        img = blank(W, H)
        if kind == 'a':
            sm = np.clip(1 - np.hypot(X, Y + 16 * u) / (R * (0.5 + 0.5 * u)) + (nz - 0.5) * 1.1, 0, 1) * (0.2 + 0.9 * min(1, u * 2)) * (1 - 0.6 * max(0, u - .7) / .3)
            if u > 0.25:
                img = over(img, heat_rgba(sm, smk, thr=0.25, dith=0.15))
            core = np.clip(np.clip(1 - r / R, 0, 1) ** 0.85 + (nz - 0.5) * 0.7 * (r / R + 0.2), 0, 1.6) * I
            core = core * (r < R * 1.15)
            img = over(img, heat_rgba(np.clip(core, 0, 1), ramp, thr=0.1, dith=0.14))
            h2 = ring(X, Y, 0, 0, R * 1.08, 2.0 * (1 - u * .7)) * (1 - u) * 0.6 * (nz2 > 0.35)
            if u < 0.75:
                img = over(img, heat_rgba(h2, [(255, 170, 70), (255, 220, 140), (255, 250, 220)], thr=0.15, dith=0.1))
            hp = np.zeros_like(X)
            for (a, d0, rr) in parts:
                dd = d0 * ease_out(u * 1.2) + 4
                ca, sa = math.cos(a), math.sin(a)
                hp = np.maximum(hp, capsule(X, Y, ca * (dd - 8 * (1 - u)), sa * (dd - 8 * (1 - u)) + 12 * u * u, ca * dd, sa * dd + 12 * u * u, 0.4, rr * (1 - u * .6)))
            if u > 0.1:
                img = over(img, heat_rgba(hp * (1 - u * .5), [(255, 130, 40), (255, 210, 100), (255, 250, 200)], thr=0.2, dith=0.0))
        else:
            shell = ring(X, Y, 0, 0, R * 0.92, max(1.5, 6 * (1 - u) + 1.5) ) * (1.1 - u * .6)
            glow = np.clip(1 - r / (R * 1.0) + (nz - 0.5) * 0.6, 0, 1) ** 1.6 * 0.5 * (1.2 - u)
            core = disc(X, Y, 0, 0, 22 * (1 - u) ** 0.9 + 3) * 1.4 * (u < 0.7)
            h = np.maximum(np.maximum(shell, glow), core)
            for k in range(8):
                a = k * 0.7854 + 0.4 + u * 0.5
                ca, sa = math.cos(a), math.sin(a)
                L = R * 1.15 * (1 - (1 - u) ** 2 if u > 0.3 else u / 0.3)
                h = np.maximum(h, capsule(X, Y, ca * R * 0.3, sa * R * 0.3, ca * L, sa * L, 2.0 * (1 - u), 0.2) * (0.9 if k % 2 == 0 else 0.6) * (1 - u * .7))
            h = np.maximum(h, ring(X, Y, 0, 0, R * 1.18, 1.2) * (1 - u) * 0.8)
            for (a, d0, rr) in parts[:10]:
                dd = d0 * 0.9 * ease_out(u * 1.2) + 6
                h = np.maximum(h, star4(X, Y, dd * math.cos(a), dd * math.sin(a), 2.8 * (1 - u * .7), 2.8 * (1 - u * .7)) * 0.95)
            img = heat_rgba(np.clip(h, 0, 1), ramp, thr=0.1, dith=0.14, mul=1 - 0.5 * max(0, u - .75) / .25)
        frames.append(img)
    return frames


def f_explosion():
    save_sheet('fx', 'fx_explosion', 96, 96, [('a', explosion_frames('a'), 24, False), ('b', explosion_frames('b'), 24, False)], (48, 48), [48, 48])


# ---------------- fuego ----------------
def flame_field(X, Y, cx, base_y, height, width, t, seed=0, amp=2.5, tongues=3, inten=1.0):
    hn = np.clip((base_y - Y) / max(height, 1), -0.2, 1.2)
    ok = (hn > -0.05) & (hn < 1.0)
    sway = amp * hn * np.sin(2 * math.pi * (t - hn * 0.9))
    out = np.zeros_like(X)
    offs = np.linspace(-1, 1, tongues) if tongues > 1 else [0]
    for k, o in enumerate(offs):
        hk = 1.0 - 0.28 * abs(o) - 0.1 * (k % 2)
        ph = t + k * 0.37
        hnk = hn / hk
        w = width * (1 - np.clip(hnk, 0, 1)) ** 0.75 * (0.62 if tongues > 1 else 1.0)
        sw = amp * hnk * np.sin(2 * math.pi * (ph - hnk * 0.9))
        dxx = X - cx - o * width * 0.55 - sw
        tur = 0.16 * np.sin(2 * math.pi * (2 * t - hnk * 2.6 + k * .31) + dxx * 0.5)
        hh = np.clip(1 - np.abs(dxx) / np.maximum(w, 0.3), 0, 1) * np.clip(1 - np.clip(hnk, 0, 1) * 0.55, 0, 1)
        hh = np.clip(hh + tur * (hh > 0.05), 0, 1) * (hnk < 1) * (hnk > -0.02)
        out = np.maximum(out, hh)
    return out * inten


def fire_frames(kind):
    W, H = 32, 48
    X, Y = grid(W, H)
    by = 45.5 - H / 2
    frames = []
    if kind == 'burn':
        n = 6
        for i in range(n):
            t = i / n
            h = flame_field(X, Y, 0, by, 36, 9.5, t, amp=2.0, tongues=3) * 1.25
            base = np.clip(1 - np.hypot((X) / 11, (Y - by) / 3.5), 0, 1) * 0.9
            h = np.maximum(h, base)
            for k in range(4):
                ph = (t + k * 0.25) % 1.0
                ex = 4 * math.sin(2 * math.pi * (ph + k * .2)) + (k - 1.5) * 3
                ey = by - 8 - ph * 32
                h = np.maximum(h, disc(X, Y, ex, ey, 1.1) * 0.95 * (1 - ph * .6))
            frames.append(heat_rgba(np.clip(h, 0, 1.2), FIRE, thr=0.1, dith=0.16))
    else:
        n = 8
        hs = [8, 22, 40, 44, 44, 42, 34, 20]
        ws = [5, 8, 11, 12, 12.5, 12, 9, 5]
        inten = [1.0, 1.2, 1.3, 1.3, 1.25, 1.1, .85, .55]
        for i in range(n):
            t = i / n
            h = flame_field(X, Y, 0, by, hs[i], ws[i], t * 2, amp=2.5, tongues=3) * inten[i]
            h = np.maximum(h, flame_field(X, Y, 0, by, hs[i] * .62, ws[i] * .75, t * 2 + .3, amp=1.5, tongues=1) * inten[i] * 1.1)
            ring_ = ring(X, Y * 3.2, 0, by * 3.2, 5 + i * 1.7, 2.0) * (1 - i / 9)
            h = np.maximum(h, ring_ * 0.9)
            if i >= 2:
                for k in range(5):
                    rr = RS(k + 3)
                    ph = (t * 1.5 + k * .2) % 1
                    h = np.maximum(h, disc(X, Y, rr.uniform(-8, 8), by - ph * hs[i] * 1.1, 1.0) * 0.9 * (1 - ph))
            frames.append(heat_rgba(np.clip(h, 0, 1.2), FIRE, thr=0.1, dith=0.16))
    return frames


def f_fire():
    save_sheet('fx', 'fx_fire', 32, 48, [('burn', fire_frames('burn'), 14, True), ('pillar', fire_frames('pillar'), 16, False)], (16, 46), [14, 30])


def build():
    f_slash_sword(); f_slash_big(); f_stab(); f_hit(); f_blood(); f_explosion(); f_fire()


if __name__ == '__main__':
    build()
    preview_sheets('fx', ['fx_slash_sword', 'fx_slash_big', 'fx_stab', 'fx_hit', 'fx_blood', 'fx_explosion', 'fx_fire'],
                   PREV + '/fx_a.png', scale=2, maxw=2400)
