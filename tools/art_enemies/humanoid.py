from common import *


def human(c, P, a, M, head_fn, weapon_fn, back_fn=None, torso_extra=None, hip_h=13.5, torso_w=3.8, legs=(6.6, 6.6), thick=(2.0, 1.8), arm_len=(5.4, 5.8),
          front_cb=None):
    """Humanoide generico. P: hx, dy, lean, ph, walk, stride, lift, rear, front (manos absolutas), head, feet(opcional).
    M: skin, cloth, cloth_d, boot, boot_d, vest, vest_d. head_fn(c, hxn, hyn, ang, P); weapon_fn(c, P, rear, front)"""
    hx, dy, lean, ph = P['hx'], P['dy'], P['lean'], P['ph']
    hip = (hx, -hip_h + dy)
    sl = (math.sin(lean), -math.cos(lean))
    neck = (hip[0] + 11 * sl[0], hip[1] + 11 * sl[1])
    sho = (hip[0] + 9.2 * sl[0], hip[1] + 9.2 * sl[1])
    if P.get('walk'):
        f1 = gait(ph, P['stride'], P['lift']); f2 = gait((ph + 0.5) % 1, P['stride'], P['lift'])
    elif 'feet' in P:
        f1, f2 = P['feet']
    else:
        f1, f2 = (-3.5, 0), (3.5, 0)
    if back_fn:
        back_fn(c, hip, neck, sho, lean, ph)
    L1, L2 = legs
    leg(c, (hip[0] - 1, hip[1] + 1), (hip[0] - 1 + f1[0], f1[1]), L1, L2, thick[0], thick[1] * 0.95, M['cloth_d'], bend=-1, footmat=M['boot_d'], footlen=4)
    if 'grip' in P:
        g = P['grip']; ax = P['axa']
        P['rear'] = g
        P['front'] = (g[0] + 5.5 * math.cos(ax), g[1] + 5.5 * math.sin(ax))
    rear = (hx + P['rear'][0], P['rear'][1] + dy)
    front = (hx + P['front'][0], P['front'][1] + dy)
    ef = ik2(sho, front, arm_len[0], arm_len[1], bend=1)
    with c.part(M['cloth_d'], line=0.4, bevel=1.4) as p:
        p.limb((sho[0] + 0.5, sho[1]), ef, thick[0], thick[1]); p.limb(ef, front, thick[1], thick[1] * 0.9)
    with c.part(M['skin'], bevel=0.8) as p:
        p.ell(front[0], front[1], 1.5)
    weapon_fn(c, P, rear, front)
    with c.at(hip[0], hip[1], lean):
        with c.part(M['cloth'], line=0.5, bevel=1.8) as p:
            p.poly([(-3.8, 0), (3.5, 0.5), (3.8, 3.5), (-3.5, 3.8)])
        with c.part(M['vest'], line=0.5, bevel=2.2) as p:
            p.poly([(-4.4, -1.5), (4.6, -1.8), (5.2, -9), (3.6, -12), (-3.2, -12), (-5.2, -8)])
        if torso_extra:
            torso_extra(c, P)
    leg(c, (hip[0] + 1, hip[1] + 1), (hip[0] + 1 + f2[0], f2[1]), L1, L2, thick[0] + 0.1, thick[1], M['cloth'], bend=-1, footmat=M['boot'], footlen=4)
    hxn = neck[0] + 3.2 * math.sin(lean + P['head']) + 0.5
    hyn = neck[1] - 3.2 * math.cos(lean + P['head'])
    head_fn(c, hxn, hyn, lean * 0.5 + P['head'], P)
    er = ik2(sho, rear, arm_len[0], arm_len[1], bend=1)
    with c.part(M['cloth'], line=0.4, bevel=1.4) as p:
        p.limb(sho, er, thick[0] + 0.1, thick[1] + 0.1); p.limb(er, rear, thick[1] + 0.1, thick[1])
    with c.part(M['skin'], bevel=0.8) as p:
        p.ell(rear[0], rear[1], 1.6)
    if front_cb:
        front_cb(c, P, rear, front)
    return dict(hip=hip, neck=neck, sho=sho, rear=rear, front=front)
