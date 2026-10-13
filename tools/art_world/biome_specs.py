"""Especificacion de props/luces/decoracion de cada bioma."""
from functools import partial as pt
from kit import ramp
import lib_props as L
from lib_props import *
from tiles_special import base_P
from biomes import CFG, BIOMES

SPECS = {}
PAL = {}


def mkP(name, **kw):
    P = base_P(CFG[name]['stone'])
    P.update(kw)
    return P


def with_(fn, **kw):
    """Version de fn con paleta modificada."""
    return lambda P, *a: fn({**P, **kw}, *a)


# ================================================================ CATACUMBAS
SPEC_GREEN = ramp('#0e2a22', '#1a5a46', '#2f9a6c', '#5cd8a0', '#b0ffd8')
P = mkP('catacumbas', metal=ramp('#10141c', '#222a38', '#3c4860', '#5c6c88', '#8ca0bc'), flame=FL_GREEN, glow=FL_GREEN, eye=FL_GREEN,
        moss=SPEC_GREEN, liquid=ramp('#0a3a2a', '#1a7a52', '#3cd88a', '#8cffc0', '#e0fff0'), cloth=ramp('#10202a', '#1e3a46', '#2e5c68', '#468a8a', '#78baa8'),
        plat=ramp('#1c2638', '#34445e', '#4c6080', '#7890b0', '#c4d4e4'), spike=ramp('#1a1c24', '#3a3e4c', '#5a6074', '#9aa2b8', '#e0e6f2'),
        haz=ramp('#0a3a2a', '#1a7a52', '#3cd88a', '#a0ffd0', '#e8fff4'), skin=ramp('#2a3a3a', '#5a7468', '#8aa898', '#b8d0bc'),
        wax=BONE, book1=CLOTH_B, book2=CLOTH_P, book3=ramp('#2a2a1a', '#4a4a2a', '#6a6a3a', '#8a8a4a'), urnramp=ramp('#1c2030', '#343c54', '#505c7c', '#7a88a8'))
PAL['catacumbas'] = P
SPECS['catacumbas'] = dict(plat_kind='stone', blood=False,
    glass=ramp('#10243a', '#2a5a8a', '#6aa8d8', '#c8ecff', '#ffffff'),
    torch=torch_bone, alt=with_(candelabra, flame=FL_AMBER),
    hang=[pt(h_chain), h_chain_hook, h_chains2, h_stalactites, h_web, h_bones, h_ribs, h_vines],
    props=[skull, bones, ribs, pt(skull, glow=True), candle_cluster, tomb, pt(tomb, cross=True), urn, chain_pile, hand, rock, pt(rock, big=False), coffin, puddle, books, vines],
    wall=[w_tattered, w_skull_plaque, pt(w_rune, g=0), w_bonepile, w_cross, w_shield, w_chains, pt(w_rune, g=2)])

# ================================================================ FORJA
P = mkP('forja', metal=ramp('#14121a', '#2a2630', '#483e48', '#6e5a60', '#a08478'), flame=FL_ORANGE, glow=FL_ORANGE, eye=FL_ORANGE,
        moss=ramp('#1c1410', '#3a2418', '#5a3a1e', '#7a5428'), liquid=ramp('#5a1008', '#b82a0a', '#ff6a14', '#ffb040', '#fff0b0'),
        cloth=ramp('#2a0c08', '#5a1a10', '#8a2a14', '#b84620', '#e07a38'), copper=COPPER, meat=ramp('#5a1008', '#b82a0a', '#ff6a14', '#ffb040'),
        plat=ramp('#14101a', '#2a2430', '#42383e', '#6a5a5c', '#c8a080'), spike=ramp('#1a1418', '#3a2c30', '#5a4448', '#a0867c', '#ffb868'),
        haz=ramp('#5a1008', '#b82a0a', '#ff6a14', '#ffc050', '#fff4c0'), hilt=COPPER, wood=ramp('#140c0a', '#2c1a14', '#482c1c', '#6a4426', '#8c6030'),
        bone=ramp('#2a2224', '#5a4a48', '#8a7870', '#b8a698', '#e0d0c0'), book1=CLOTH_R, book2=ramp('#2a1a10', '#5a3a1a', '#8a5a28', '#b88038'))
PAL['forja'] = P
SPECS['forja'] = dict(plat_kind='grate', blood=False,
    glass=ramp('#3a0e04', '#a8300a', '#ff7a18', '#ffd068', '#fff8d0'),
    torch=torch_brazier, alt=lambda P, f: gas_lamp(P, f),
    hang=[h_chain, h_chain_hook, h_chains2, h_hooks, h_stalactites, h_pipe, h_cables, h_lantern],
    props=[anvil, embers, barrel, crate, chain_pile, rock, pt(rock, big=False), brazier, gear, valve, skull, bones, cauldron, puddle, gargoyle, sword_ground],
    wall=[h_banner, w_shield, w_swords, gear, w_skull_plaque, pt(w_rune, g=1), w_chains, w_tattered])

# ================================================================ HELADO
P = mkP('helado', metal=ramp('#10182c', '#222e4c', '#3c507c', '#6482b0', '#a8c8e8'), flame=FL_BLUE, glow=FL_BLUE, eye=FL_BLUE,
        moss=ramp('#102a3a', '#1c4a62', '#3a7a98', '#78b8d0'), liquid=ramp('#0e2a52', '#1c5a96', '#48a0d8', '#a0e0ff', '#e8faff'),
        cloth=CLOTH_B, crystal=ICE, plat=ramp('#14305a', '#2a5890', '#4c8cc4', '#a0d4f0', '#ffffff'),
        spike=ramp('#10285a', '#24508c', '#4a88c4', '#98d0f0', '#f4fcff'), haz=ramp('#0e2a52', '#1c5a96', '#48a0d8', '#a0e8ff', '#f0fcff'),
        bone=ramp('#1c2a44', '#4a6088', '#8aa4c8', '#c4dcf2', '#f0faff'), wood=ramp('#10161c', '#222e3a', '#3a4c5c', '#587288', '#7c9ab4'),
        thorn=ramp('#10182c', '#222e4c', '#3a507c', '#6482b0'), moon=ramp('#3a4a6a', '#7a92b8', '#b8d0f0', '#e8f4ff', '#ffffff'),
        hilt=ramp('#10182c', '#3a507c', '#6482b0', '#a8c8e8', '#e0f0ff'), book1=CLOTH_B, book2=ramp('#1c2a44', '#3a507c', '#6482b0', '#a8c8e8'), book3=CLOTH_P)
PAL['helado'] = P
SPECS['helado'] = dict(plat_kind='ice', blood=False,
    glass=ramp('#0a2a5a', '#1c8a8a', '#46d8b0', '#b4ffe4', '#ffffff'),
    torch=lambda P, f: torch_generic(P, f), alt=lambda P, f: crystal_pulse(P, f, ICE),
    hang=[h_icicles, pt(h_stalactite, ramp_=ICE), pt(h_crystal, ramp_=ICE), h_chain, h_cloth, h_web, h_drips, pt(h_stalactites, ramp_=ICE)],
    props=[pt(crystals), ice_spikes, snow_mound, rock, pt(rock, big=False), skull, bones, stump, bush_dead, pt(crystals, h=(12, 8, 6)), puddle, pt(tomb, cross=True), tomb, urn, ribs, sword_ground],
    wall=[h_banner, w_shield, pt(w_rune, g=0), pt(w_window if False else w_vitral, cols=[ramp('#0a2a5a', '#1c4a9a', '#3a8ad8', '#b4e4ff'), ramp('#0a3a4a', '#1c7a8a', '#3ac8c8', '#b4ffff')]), w_moon, w_cross, w_tattered, pt(w_rune, g=3)])

# ================================================================ VACIO
P = mkP('vacio', metal=ramp('#0c0818', '#1c1230', '#32205a', '#503a88', '#7c64b8'), flame=FL_PURPLE, glow=FL_PURPLE, eye=FL_PURPLE,
        moss=ramp('#180a2c', '#32185a', '#52288a', '#7a40b8'), liquid=ramp('#1c0a3a', '#4a1a8a', '#8a3ad8', '#d08aff', '#f8e0ff'),
        cloth=CLOTH_P, crystal=ramp('#1c0a3a', '#4a1a8a', '#8a3ad8', '#c880ff', '#f8e0ff'), plat=ramp('#0c0818', '#1e1238', '#38235e', '#6a48a8', '#c88aff'),
        spike=ramp('#0c0818', '#1e1238', '#3a2468', '#7a52c0', '#e0b0ff'), haz=ramp('#1c0a3a', '#4a1a8a', '#8a3ad8', '#d08aff', '#fcf0ff'),
        bone=ramp('#161224', '#3a3256', '#6a5c92', '#a898d0', '#dcd0f8'), wood=ramp('#0c0818', '#1c1230', '#32205a', '#503a88', '#7c64b8'),
        gold=ramp('#1c0a3a', '#4a1a8a', '#8a3ad8', '#c880ff', '#f8e0ff'), thorn=ramp('#0c0818', '#1c1230', '#32205a', '#503a88'),
        moon=ramp('#2a1a4a', '#5a3a9a', '#9a6ad8', '#d8b0ff', '#ffffff'))
PAL['vacio'] = P
SPECS['vacio'] = dict(plat_kind='glow', blood=False,
    glass=ramp('#14082c', '#3a1a7a', '#7a3ad0', '#d8a0ff', '#ffffff'),
    torch=floating_flame, alt=lambda P, f: crystal_pulse(P, f, P['crystal']),
    hang=[h_tendrils, pt(h_crystal), pt(h_stalactites), h_chain, h_cloth, h_stars, h_drips, h_tendrils],
    props=[pt(crystals), void_tendril, rock, pt(rock, big=False), pt(skull, glow=True), orb_pedestal, puddle, bones, ribs, gargoyle, brazier, sword_ground, thorns, void_tendril, pt(crystals, h=(12, 8, 5)), chain_pile],
    wall=[pt(w_rune, g=0), w_eye, pt(w_rune, g=2), w_eye, w_moon, w_skull_plaque, pt(w_window, glass=ramp('#14082c', '#3a1a7a', '#7a3ad0', '#d8a0ff', '#ffffff')), pt(w_rune, g=3)])
P['plat_acc'] = P['haz']

# ================================================================ BOSQUE
P = mkP('bosque', metal=ramp('#14120c', '#2a261a', '#46402a', '#6a6040', '#9a8c5c'), flame=FL_AMBER, glow=FL_AMBER, eye=FL_AMBER,
        moss=MOSS, liquid=ramp('#1c2a0a', '#3a5a14', '#78a828', '#c4e060', '#f0ffb0'), cloth=CLOTH_G, plat=ramp('#1c1410', '#38281a', '#5a4020', '#86602c', '#a8c84a'),
        spike=ramp('#1c1408', '#3a2a14', '#5a4020', '#9a7438', '#e8d090'), haz=ramp('#1c2a0a', '#3a6a14', '#78b828', '#c8f060', '#f4ffc0'),
        wood=WOOD, bone=ramp('#2a2820', '#625a48', '#a09878', '#d4c8a0', '#f0e8c8'), cap=ramp('#4a1e08', '#9a4a14', '#e08a2a', '#ffc860'),
        cap2=ramp('#0a3a3a', '#1a7a72', '#3ac8b0', '#9cffe4'), gl_ramp=ramp('#6a3a08', '#c07a1c', '#ffbe48', '#ffe698', '#fffbe8'),
        bloom=FL_AMBER, thorn=ramp('#1a1a08', '#363814', '#566a20', '#80982c'), hilt=ramp('#1c1410', '#38281a', '#5a4020', '#86602c', '#a88442'))
PAL['bosque'] = P
SPECS['bosque'] = dict(plat_kind='plank', blood=False,
    glass=ramp('#1c2a0a', '#6a7a14', '#d8b02a', '#ffe070', '#fffbe0'),
    torch=torch_wood, alt=mushroom_light,
    hang=[h_roots, h_vines, pt(h_vines), h_moss, h_web, h_lantern, h_drips, h_roots],
    props=[shroom_small, shroom_tall, shroom_cluster, pt(grass), pt(grass, tall=6, n=4), flowers, stump, vines, rock, pt(rock, big=False), bush_dead, thorns, cocoon, bones, skull, cauldron],
    wall=[h_banner, w_skull_plaque, pt(w_rune, g=2), w_sign, w_shield, w_cross, pt(w_window, glass=ramp('#1c2a0a', '#6a7a14', '#d8b02a', '#ffe070', '#fffbe0')), w_tattered])
P['rockramp'] = CFG['bosque']['stone'] * 1.0

# ================================================================ TORMENTA
P = mkP('tormenta', metal=ramp('#10181c', '#222e34', '#3c4e56', '#628088', '#98b4b8'), flame=FL_ELEC, glow=FL_ELEC, eye=FL_ELEC,
        moss=ramp('#10382e', '#1e6a58', '#38a888', '#78e0c0'), liquid=ramp('#0e3a58', '#2e98d4', '#80dcff', '#dcf8ff', '#ffffff'), cloth=CLOTH_B,
        plat=ramp('#2a1614', '#5a2e20', '#94502c', '#c8783a', '#ffe0a8'), spike=ramp('#2a1614', '#5a2e20', '#94502c', '#d89860', '#ffe8c0'),
        haz=ramp('#0e3a58', '#2e98d4', '#80dcff', '#dcf8ff', '#ffffff'), copper=COPPER, wood=ramp('#161a1c', '#2a3236', '#44525a', '#6a8088', '#94acb0'),
        gold=COPPER, hilt=COPPER, bone=ramp('#1c2a2c', '#44605c', '#78a49a', '#aedccc', '#e0fff4'), book1=CLOTH_B, book2=ramp('#2a1614', '#5a2e20', '#94502c', '#c8783a'))
PAL['tormenta'] = P
SPECS['tormenta'] = dict(plat_kind='metal', blood=False,
    glass=ramp('#0c2a40', '#1e6a9a', '#58b8e8', '#c8f0ff', '#ffffff'),
    torch=tesla_torch, alt=lambda P, f: h_lantern(P) if False else orb_light(P, f),
    hang=[h_cables, pt(h_cables), h_chain, h_chain_hook, h_chains2, h_pipe, h_lantern, h_bell],
    props=[tesla_coil, gear, valve, barrel, crate, chain_pile, rock, pt(rock, big=False), anvil, cauldron, lamp_post, puddle, brazier, bell, skull, sword_ground],
    wall=[w_shield, h_banner, gear, w_bolt, pt(w_rune, g=2), w_swords, pt(w_window, glass=ramp('#0c2a40', '#1e6a9a', '#58b8e8', '#c8f0ff', '#ffffff')), pt(w_rune, g=1)])

# ================================================================ SANGRE
RED_G = [ramp('#4a0614', '#8a0e24', '#c41e3c', '#f0506a'), ramp('#3a0a3a', '#7a1a6a', '#b43a9a', '#e878d0'), ramp('#4a0614', '#8a0e24', '#c41e3c', '#f0506a'), ramp('#5a1a08', '#a83a14', '#e0702a', '#ffb060')]
P = mkP('sangre', metal=ramp('#16101a', '#2c2230', '#48384e', '#705a72', '#a08aa4'), flame=FL_RED, glow=FL_RED, eye=FL_RED,
        moss=ramp('#2a0a14', '#561224', '#861c36', '#b82c48'), liquid=ramp('#4a0614', '#9a0e26', '#d82444', '#ff6a80', '#ffc0c8'), cloth=CLOTH_R,
        plat=ramp('#1c0a10', '#3a1420', '#5c2030', '#8a3a48', '#e07a88'), spike=ramp('#2a2024', '#5a4a4a', '#8a7a74', '#c8bcae', '#f2eadc'),
        haz=ramp('#4a0614', '#9a0e26', '#d82444', '#ff6a80', '#ffd0d8'), bone=ramp('#2a2224', '#5a4a4c', '#9a8a84', '#d2c4b4', '#f4ecdc'),
        wood=ramp('#1a0c10', '#36181c', '#58282c', '#803c3c', '#a85a50'), wax=ramp('#3a2a2a', '#7a5a58', '#b89a90', '#e8d4c4', '#fff4e8'),
        book1=CLOTH_R, book2=CLOTH_P, book3=ramp('#2a1a0a', '#5a3a14', '#8a5a20', '#b88a38'))
PAL['sangre'] = P
SPECS['sangre'] = dict(plat_kind='slab', blood=True,
    glass=ramp('#3a0a14', '#8a1428', '#d03048', '#ff8aa0', '#ffe8ee'),
    torch=lambda P, f: candelabra(P, f), alt=lambda P, f: torch_brazier(P, f),
    hang=[h_hooks, h_drips, h_chain, h_chains2, h_web, h_bat, h_ribs, pt(h_banner)],
    props=[skull, pt(skull, glow=True), bones, ribs, candle_cluster, pt(tomb, cross=True), coffin, puddle, urn, chain_pile, hand, books, gargoyle, brazier, bell, sword_ground],
    wall=[pt(w_vitral, cols=RED_G), pt(w_vitral, cols=[RED_G[1], RED_G[0], RED_G[3], RED_G[0]]), pt(h_banner, emb='eye'), w_skull_plaque, w_blood_hand, w_cross, w_shield, pt(w_rune, g=3)])

# ================================================================ ECLIPSE
P = mkP('eclipse', metal=ramp('#14141c', '#282836', '#444458', '#6a6a84', '#9a9ab8'), flame=FL_GOLD, glow=FL_GOLD, eye=FL_GOLD,
        moss=ramp('#2a2410', '#5a4a1c', '#8a7028', '#b89a40'), liquid=ramp('#4a3410', '#a87a20', '#e8b840', '#fff0a0', '#ffffff'), cloth=ramp('#10101a', '#22223a', '#383860', '#585890', '#8888c0'),
        plat=ramp('#0c0c14', '#1c1c2a', '#303046', '#9a7428', '#fff0a0'), spike=ramp('#2a2010', '#7a5a1c', '#c89a38', '#f0d070', '#fff8c8'),
        haz=ramp('#6a4a10', '#c4901c', '#f6cc44', '#fff09e', '#ffffff'), gold=GOLD, hilt=GOLD, crystal=ramp('#4a3410', '#a87a20', '#e8b840', '#fff0a0', '#ffffff'),
        bone=ramp('#26242c', '#5a5664', '#98909c', '#cec6c0', '#f4eee6'), wood=ramp('#0c0c14', '#1c1c2a', '#303046', '#4a4a66', '#6a6a8a'), wax=GOLD,
        moon=ramp('#3a3a4a', '#7a7a90', '#b8b8d0', '#e8e8f8', '#ffffff'), paint=ramp('#10101a', '#22223a', '#383860', '#e8c050'))
PAL['eclipse'] = P
SPECS['eclipse'] = dict(plat_kind='slab', blood=False,
    glass=ramp('#10101a', '#5a4a1c', '#e8c050', '#fff2b0', '#ffffff'),
    torch=sun_brazier, alt=lambda P, f: orb_light(P, f),
    hang=[h_stars, pt(h_chain, links=7), h_bell, pt(h_banner, cloth=ramp('#10101a', '#22223a', '#383860', '#585890'), emb='sun'), h_lantern, pt(h_crystal), h_cloth, h_stalactites],
    props=[gold_pile, bell, orb_pedestal, col_stub, brazier, rock, skull, urn, pt(tomb, cross=True), gargoyle, sword_ground, pt(crystals), puddle, candle_cluster, chain_pile, bones],
    wall=[w_sun, w_moon, pt(h_banner, cloth=ramp('#10101a', '#22223a', '#383860', '#585890'), emb='sun'), w_shield, pt(w_rune, g=0), pt(w_window, glass=ramp('#10101a', '#5a4a1c', '#e8c050', '#fff2b0', '#ffffff')), w_eye, w_painting])
P['rockramp'] = CFG['eclipse']['stone'] * 1.0

# ================================================================ CAZADOR
P = mkP('cazador', metal=ramp('#0c0a12', '#1c1824', '#322c3e', '#52485e', '#7a6e86'), flame=FL_WARM, glow=FL_RED, eye=FL_RED,
        moss=ramp('#1a2a24', '#2e463a', '#4a6a58', '#7a9a80'), liquid=ramp('#3a0814', '#7a0e22', '#b81c34', '#e8506a', '#ffa0b0'), cloth=ramp('#1a0a14', '#36121e', '#5a1a2c', '#842a3c', '#b04458'),
        plat=ramp('#0e0c14', '#1e1a28', '#342e42', '#5a506c', '#d89aa4'), spike=ramp('#0c0a12', '#1c1824', '#322c3e', '#6a5e78', '#c8b8d0'),
        haz=ramp('#3a0814', '#7a0e22', '#b81c34', '#ff5a74', '#ffc0c8'), bone=ramp('#26222c', '#585066', '#948aa0', '#cac0c8', '#f2eaee'),
        wood=ramp('#140e12', '#2a1c20', '#46303a', '#6a4a52', '#8a6a6c'), book1=CLOTH_R, book2=ramp('#10182c', '#222e4c', '#3c507c', '#6482b0'),
        moon=ramp('#3a0a14', '#7a1a28', '#c03040', '#f06a70', '#ffb8b8'), feather=ramp('#08060c', '#14101c', '#241e30', '#382e48'))
PAL['cazador'] = P
SPECS['cazador'] = dict(plat_kind='plank', blood=True,
    glass=ramp('#3a0814', '#8a1428', '#d82e44', '#ff8a98', '#ffe0e4'),
    torch=gas_lamp, alt=lambda P, f: gas_lamp({**P, 'flame': FL_RED}, f),
    hang=[pt(h_lantern), h_lantern, h_chain, h_chains2, h_cloth, h_bat, h_gargoyle_drain, h_web],
    props=[lamp_post, fence, bench, gargoyle, crow, pt(tomb, cross=True), barrel, crate, rock, puddle, skull, bones, books, urn, sword_ground, bush_dead],
    wall=[pt(w_window, glass=ramp('#3a0814', '#8a1428', '#d82e44', '#ff8a98', '#ffe0e4')), pt(w_vitral, cols=RED_G), pt(h_banner, emb='eye'), w_eye, w_painting, w_moon, w_cross, pt(w_rune, g=1)])
P['rockramp'] = CFG['cazador']['stone'] * 1.0
