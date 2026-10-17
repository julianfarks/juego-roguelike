#!/usr/bin/env python3
"""Valida los assets contra el contrato de DESIGN.md.
Uso: python3 tools/validate_assets.py [categoria ...]
categorias: players enemies bosses props fx tiles bg ui audio   (sin argumentos = todas)
Sale con codigo 1 si hay errores. Las categorias sin archivos aun se informan como FALTANTES.
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, 'app/src/main/assets')

CLASSES = ['paladin', 'shadow', 'flame', 'storm', 'frost', 'verdant', 'blood', 'earth', 'astral', 'steel']
BIOMES = ['catacumbas', 'forja', 'helado', 'vacio', 'bosque', 'tormenta', 'sangre', 'eclipse', 'cazador']
ENEMIES = ['esqueleto', 'arquero_hueso', 'zombi', 'cubo_magma', 'llama', 'bruto_forja', 'lancero_escarcha',
           'hechicero_hielo', 'espiritu_vex', 'acechador', 'ojo_vacio', 'fantasma', 'arana', 'bruja', 'tronco_vivo',
           'saqueador', 'vex_tormenta', 'bestia_tormenta', 'vindicador', 'bruja_sangre', 'murcielago',
           'piglin_dorado', 'espectro', 'llama_solar']
BOSSES = ['rey_exanime', 'coloso_magma', 'reina_escarcha', 'devorador_vacio', 'ent_ancestral', 'titan_tormenta',
          'matriarca_sangre', 'guardian_eclipse', 'cazador1', 'cazador2', 'cazador3']
PLAYER_X_ANIMS = [('idle1', 16), ('idle2', 16), ('idle3', 16), ('idle4', 16), ('chest', 8), ('awe', 10), ('touch', 6),
                  ('victory', 14), ('weary', 6)]
PLAYER_ANIMS = [('idle', 6), ('run', 8), ('jump', 3), ('fall', 2), ('roll', 7), ('attack1', 6), ('attack2', 6),
                ('attack3', 7), ('airatk', 5), ('skill', 7), ('ult', 10), ('hurt', 2), ('death', 9), ('block', 2)]
ENEMY_ANIMS = ['idle', 'walk', 'windup', 'attack', 'hurt', 'death']
BOSS_ANIMS = [('idle', 6), ('walk', 8), ('windup1', 5), ('attack1', 8), ('windup2', 5), ('attack2', 8), ('windup3', 6),
              ('attack3', 9), ('cast', 8), ('hurt', 2), ('phase', 10), ('intro', 14), ('death', 14)]
PROPS = {'prop_door': ['closed', 'open', 'open_idle'], 'prop_portal': ['idle'], 'prop_altar': ['idle', 'used'],
         'prop_chest': ['closed', 'open', 'open_idle'], 'prop_fountain': ['idle'], 'prop_forge': ['idle'],
         'prop_merchant': ['idle'], 'prop_sanctuary': ['idle'], 'pick_gold': ['idle'], 'pick_soul': ['idle'],
         'pick_heart': ['idle'], 'pick_potion': ['idle'], 'pick_relic': ['idle'], 'prop_pot': ['closed', 'break']}
FX = {'fx_slash_sword': ['s1', 's2', 's3'], 'fx_slash_big': ['s1', 's2', 's3'], 'fx_stab': ['s1', 's2'],
      'fx_hit': ['spark', 'big', 'crit', 'magic', 'shock', 'ice'], 'fx_blood': ['splat', 'mist'],
      'fx_explosion': ['a', 'b'], 'fx_fire': ['burn', 'pillar'], 'fx_ice': ['spike', 'burst', 'frozen'],
      'fx_lightning': ['bolt', 'ground'], 'fx_thorn': ['vine', 'bloom'], 'fx_rock': ['pillar', 'debris'],
      'fx_star': ['burst', 'twinkle'], 'fx_void': ['hole', 'rift'], 'fx_holy': ['beam'], 'fx_shadow': ['puff', 'blade'],
      'fx_dust': ['run', 'land', 'roll'], 'fx_heal': ['rise'], 'fx_shield': ['bubble'], 'fx_whirl': ['spin'],
      'fx_tele': ['out', 'in'], 'fx_shock': ['wave'], 'fx_smoke': ['big'], 'fx_ring': ['pulse'],
      'fx_proj': ['arrow', 'dagger', 'fireball', 'iceshard', 'bolt', 'voidorb', 'bloodorb', 'leaf', 'star', 'blade',
                  'crescent', 'poison', 'magma', 'holy', 'spike', 'bone']}

errs = []
miss = []


def err(m):
    errs.append(m)


def check_noclip(rel):
    """Las animaciones de personalidad no pueden tocar el borde de la celda (seria un recorte: arma o brazo cortados)."""
    png = os.path.join(A, rel + '.png')
    js = os.path.join(A, rel + '.json')
    if not os.path.exists(png) or not os.path.exists(js):
        return
    im = Image.open(png).convert('RGBA')
    d = json.load(open(js))
    W, H = d['cell']
    for name, a in d['anims'].items():
        for i in range(a['n']):
            fr = im.crop((i * W, a['row'] * H, (i + 1) * W, (a['row'] + 1) * H)).getchannel('A')
            edge = [fr.crop((0, 0, W, 1)), fr.crop((0, H - 1, W, H)), fr.crop((0, 0, 1, H)), fr.crop((W - 1, 0, W, H))]
            if any(e.getbbox() for e in edge):
                err(f'{rel}: anim {name} fotograma {i} toca el borde de la celda (recortado)')
                break


def check_sheet(rel, anims_req, cell=None, must_hit=(), exact_n=None):
    png = os.path.join(A, rel + '.png')
    js = os.path.join(A, rel + '.json')
    if not os.path.exists(png) or not os.path.exists(js):
        miss.append(rel)
        return
    try:
        im = Image.open(png)
        d = json.load(open(js))
    except Exception as e:
        err(f'{rel}: no se pudo leer ({e})')
        return
    if im.mode != 'RGBA':
        err(f'{rel}: el PNG debe ser RGBA (es {im.mode})')
    W, H = d['cell']
    if cell and [W, H] != list(cell) and not isinstance(cell, (set,)):
        err(f'{rel}: celda {W}x{H} != esperada {cell}')
    for k in ('pivot',):
        if k not in d:
            err(f'{rel}: falta "{k}"')
    anims = d.get('anims', {})
    maxn = 0
    rows = 0
    for name in anims_req:
        if name not in anims:
            err(f'{rel}: falta anim "{name}"')
    for name, a in anims.items():
        n, r = a['n'], a['row']
        maxn = max(maxn, n)
        rows = max(rows, r + 1)
        if (r + 1) * H > im.height or n * W > im.width:
            err(f'{rel}: anim {name} fuera de la hoja ({n}x{W}, fila {r}, hoja {im.size})')
        else:
            # que no este vacia
            for i in range(n):
                fr = im.crop((i * W, r * H, (i + 1) * W, (r + 1) * H))
                if fr.getchannel('A').getbbox() is None:
                    err(f'{rel}: anim {name} fotograma {i} vacio')
                    break
        if exact_n and name in exact_n and exact_n[name] != n:
            err(f'{rel}: anim {name} n={n} != {exact_n[name]}')
        if name in must_hit and ('hit' not in a or 'box' not in a):
            err(f'{rel}: anim {name} necesita "hit" y "box"')
        if 'hit' in a:
            h0, h1 = a['hit']
            if not (0 <= h0 <= h1 < n):
                err(f'{rel}: anim {name} hit fuera de rango')
    if im.width != maxn * W:
        err(f'{rel}: ancho de hoja {im.width} != {maxn}*{W}')
    if im.height != rows * H:
        err(f'{rel}: alto de hoja {im.height} != {rows}*{H}')


def players():
    for c in CLASSES:
        check_sheet(f'sprites/plx_{c}', [a for a, _ in PLAYER_X_ANIMS], cell=(96, 96), exact_n=dict(PLAYER_X_ANIMS))
        check_noclip(f'sprites/plx_{c}')
        check_sheet(f'sprites/pl_{c}', [a for a, _ in PLAYER_ANIMS], cell=(64, 48),
                    must_hit=('attack1', 'attack2', 'attack3', 'airatk'), exact_n=dict(PLAYER_ANIMS))
        for nm, sz in ((f'sprites/portrait_{c}', (32, 32)), (f'sprites/splash_{c}', (128, 176))):
            p = os.path.join(A, nm + '.png')
            if not os.path.exists(p):
                miss.append(nm)
            elif Image.open(p).size != sz:
                err(f'{nm}: tamano {Image.open(p).size} != {sz}')


def enemies():
    for e in ENEMIES:
        check_sheet(f'sprites/en_{e}', ENEMY_ANIMS)


def bosses():
    for b in BOSSES:
        check_sheet(f'sprites/bs_{b}', [a for a, _ in BOSS_ANIMS], must_hit=('attack1', 'attack2', 'attack3'),
                    exact_n=dict(BOSS_ANIMS))


def props():
    for k, an in PROPS.items():
        check_sheet(f'sprites/{k}', an)


def fx():
    for k, an in FX.items():
        check_sheet(f'fx/{k}', an)


def tiles():
    for b in BIOMES:
        p = os.path.join(A, f'tiles/tiles_{b}.png')
        if not os.path.exists(p):
            miss.append(f'tiles/tiles_{b}')
            continue
        im = Image.open(p)
        if im.size != (256, 128):
            err(f'tiles_{b}: tamano {im.size} != (256,128)')
        # las 48 baldosas solidas no deben estar vacias
        for r in range(3):
            for c in range(16):
                t = im.crop((c * 16, r * 16, c * 16 + 16, r * 16 + 16))
                if t.getchannel('A').getbbox() is None and not (r > 0 and c == 0 and False):
                    err(f'tiles_{b}: baldosa solida fila {r} columna {c} vacia')


def bg():
    for b in BIOMES:
        for i in range(3):
            p = os.path.join(A, f'bg/bg_{b}_{i}.png')
            if not os.path.exists(p):
                miss.append(f'bg/bg_{b}_{i}')
            elif Image.open(p).size != (512, 288):
                err(f'bg_{b}_{i}: tamano {Image.open(p).size} != (512,288)')


def ui():
    need = {'ui_logo': None, 'ui_title_0': (512, 288), 'ui_title_1': (512, 288), 'ui_title_2': (512, 288),
            'ui_title_3': (512, 288), 'ui_panel': (32, 32), 'ui_panel_light': (32, 32), 'ui_panel_red': (32, 32),
            'ui_btn': (144, 20), 'ui_btn_round': (120, 40), 'ui_hp_frame': (104, 14), 'ui_hp_fill': (100, 10),
            'ui_ult_frame': (84, 10), 'ui_ult_fill': (80, 6), 'ui_boss_frame': (256, 18), 'ui_boss_fill': (244, 8),
            'ui_cursor': (16, 16), 'ui_arrow': (8, 8), 'ui_vignette': (128, 72)}
    for k, sz in need.items():
        p = os.path.join(A, f'ui/{k}.png')
        if not os.path.exists(p):
            miss.append(f'ui/{k}')
        elif sz and Image.open(p).size != sz:
            err(f'{k}: tamano {Image.open(p).size} != {sz}')
    ip, ij = os.path.join(A, 'ui/icons.png'), os.path.join(A, 'ui/icons.json')
    if not (os.path.exists(ip) and os.path.exists(ij)):
        miss.append('ui/icons')
    else:
        d = json.load(open(ij))
        im = Image.open(ip)
        names = d['names']
        if len(names) != 128:
            err(f'icons.json: {len(names)} nombres != 128')
        if im.width != 256 or im.height < ((len(names) + 15) // 16) * 16:
            err(f'icons.png: tamano {im.size} no cabe')
        for i, n in enumerate(names):
            t = im.crop(((i % 16) * 16, (i // 16) * 16, (i % 16) * 16 + 16, (i // 16) * 16 + 16))
            if t.getchannel('A').getbbox() is None:
                err(f'icons: icono "{n}" ({i}) vacio')
    for f, (cw, ch) in (('font_s', (8, 10)), ('font_b', (12, 16))):
        jp, pp = os.path.join(A, f'font/{f}.json'), os.path.join(A, f'font/{f}.png')
        if not (os.path.exists(jp) and os.path.exists(pp)):
            miss.append(f'font/{f}')
            continue
        d = json.load(open(jp))
        if d['cellW'] != cw or d['cellH'] != ch:
            err(f'{f}: celda {d["cellW"]}x{d["cellH"]} != {cw}x{ch}')
        if len(d['widths']) != len(d['chars']):
            err(f'{f}: widths ({len(d["widths"])}) != chars ({len(d["chars"])})')


def audio():
    mp = os.path.join(A, 'audio/manifest.json')
    if not os.path.exists(mp):
        miss.append('audio/manifest.json')
        return
    d = json.load(open(mp))
    for n in d.get('sfx', {}):
        if not os.path.exists(os.path.join(A, 'audio/sfx', n + '.ogg')):
            err(f'audio: sfx {n}.ogg listado pero no existe')
    for n in d.get('music', {}):
        if not os.path.exists(os.path.join(A, 'audio/music', n + '.ogg')):
            err(f'audio: music {n}.ogg listado pero no existe')
    req_sfx = ['ui_click', 'ui_confirm', 'ui_back', 'ui_error', 'ui_open', 'ui_pick_upgrade', 'ui_unlock', 'ui_start_run',
               'ui_pause', 'ui_hover', 'coin', 'soul', 'heart', 'potion', 'door_open', 'door_locked', 'portal_enter',
               'chest_open', 'shop_buy', 'forge_anvil', 'altar_bless', 'fountain_heal', 'spikes', 'break_pot',
               'room_clear', 'room_lock', 'secret', 'relic_get', 'step_1', 'step_2', 'step_3', 'jump', 'double_jump',
               'land', 'roll', 'hurt_1', 'hurt_2', 'death', 'heal', 'block', 'parry', 'heartbeat', 'level_up',
               'ult_ready', 'skill_fail', 'cd_ready', 'ult_charge', 'time_stop', 'swing_air', 'hit_crit', 'hit_magic',
               'hit_stone', 'hit_bone', 'hit_ice', 'hit_fire', 'hit_shock', 'hit_blood', 'hit_metal_1', 'hit_metal_2',
               'en_alert', 'en_hurt_1', 'en_hurt_2', 'en_die_bone', 'en_die_flesh', 'en_die_ghost', 'en_die_slime',
               'en_die_magic', 'en_attack_melee', 'en_cast', 'en_flap', 'en_dash', 'en_step_heavy', 'arrow_shot', 'spit',
               'magic_bolt', 'explosion_small', 'explosion_big', 'proj_hit', 'boss_title', 'boss_bar', 'boss_defeat']
    for w in ('sword', 'great', 'dagger', 'stab', 'scythe', 'hammer'):
        req_sfx += [f'swing_{w}_{i}' for i in (1, 2, 3)]
    req_sfx += [f'hit_flesh_{i}' for i in (1, 2, 3)]
    for c in CLASSES:
        req_sfx += [f'sk_{c}_1', f'sk_{c}_2', f'sk_{c}_3', f'sk_{c}_hit', f'ult_{c}']
    for b in ('rey_exanime', 'coloso_magma', 'reina_escarcha', 'devorador_vacio', 'ent_ancestral', 'titan_tormenta',
              'matriarca_sangre', 'guardian_eclipse', 'cazador'):
        req_sfx += [f'bs_{b}_{s}' for s in ('intro', 'roar', 'atk1', 'atk2', 'atk3', 'cast', 'hurt', 'phase', 'death', 'step')]
    req_sfx += [f'amb_{b}' for b in BIOMES]
    req_mus = ['mus_title', 'mus_sanctuary'] + [f'mus_{b}' for b in BIOMES[:8]] + \
              ['mus_boss_a', 'mus_boss_b', 'mus_final_1', 'mus_final_2', 'mus_final_3', 'mus_victory', 'mus_gameover', 'mus_credits']
    for n in req_sfx:
        if n not in d.get('sfx', {}):
            miss.append('sfx:' + n)
    for n in req_mus:
        if n not in d.get('music', {}):
            miss.append('music:' + n)


CATS = {'players': players, 'enemies': enemies, 'bosses': bosses, 'props': props, 'fx': fx, 'tiles': tiles, 'bg': bg,
        'ui': ui, 'audio': audio}

if __name__ == '__main__':
    sel = sys.argv[1:] or list(CATS)
    for c in sel:
        CATS[c]()
    for m in miss:
        print('FALTANTE:', m)
    for e in errs:
        print('ERROR:', e)
    print(f'--- {len(miss)} faltantes, {len(errs)} errores ---')
    sys.exit(1 if errs else 0)
