#!/usr/bin/env python3
"""Genera BlessData.java, las traducciones y la documentacion del catalogo de bendiciones.  Uso: python3 tools/blessings/gen.py"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalog import *

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
JAVA = os.path.join(ROOT, 'Shared/src/main/java/com/julianfarks/roguelike/core/BlessData.java')
TSV = os.path.join(ROOT, 'tools/i18n/parts/blessings200.tsv')


def jq(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def check():
    names, descs = set(), set()
    for e in ENTRIES:
        n, d = e['names'][0], e['descs'][0]
        assert n not in names, 'nombre repetido ' + n
        assert d not in descs, 'descripcion repetida ' + d
        names.add(n); descs.add(d)
        for t in e['names'] + e['descs']:
            assert t.strip(), e['key']
        assert len(n) <= 26, ('nombre largo', n)
        for r in e['rules']:
            assert r.count('|') >= 2, (e['key'], r)
        if e['req']:
            if e['req'][0] == 'has':
                for k in e['req'][2]:
                    assert k in ID, (e['key'], k)
    for s in SYNS:
        for m in s['members']:
            assert m in ID, (s['key'], m)
        assert s['need'] <= len(s['members'])


def req_str(e):
    r = e['req']
    if not r: return ''
    if r[0] == 'cat': return 'cat:%s:%d' % (r[1], r[2])
    return 'has:%d:%s' % (r[1], ','.join(str(ID[k]) for k in r[2]))


def gen_java():
    out = []
    out.append('''package com.julianfarks.roguelike.core;

/**
 * GENERADO por tools/blessings/gen.py a partir de tools/blessings/cat_*.py: NO editar a mano.
 * Definiciones (datos) del catalogo de 200 bendiciones y sus sinergias; la logica que las ejecuta vive en BlessFx / BlessEffects.
 * Las 28 primeras (ids 0..27) conservan su logica original en Stats/Player/Level; aqui solo se clasifican.
 */
final class BlessData {
    private BlessData() {}

    /** Categorias: A dano fisico, B magia y elementos, C defensa, D velocidad, E proyectiles, F recursos, G invocaciones, H riesgo, I maldiciones, J hibridas. */
    static final String CATS = "ABCDEFGHIJ";
    /** Categoria y rareza (0 comun .. 4 legendaria) de las 28 bendiciones originales. */
''')
    out.append('    static final String LEG_CAT = "%s";\n' % ''.join(LEGACY_META[k][0] for k in LEGACY))
    out.append('    static final int[] LEG_RAR = {%s};\n' % ', '.join(str(LEGACY_META[k][1]) for k in LEGACY))
    out.append('    static final String[] CAT_ES = {%s};\n' % ', '.join(jq(CAT_NAMES[c][0]) for c in CATS))
    out.append('    static final String[] LEG_KEY = {%s};\n\n' % ', '.join(jq(k.lower()) for k in LEGACY))
    out.append('    /** Nuevas bendiciones: clave, icono, nombre, descripcion, categoria, rareza, nivel maximo, peso, piso minimo, requisito, reglas separadas por ~. */\n')
    out.append('    static final String[][] NEW = {\n')
    for e in ENTRIES:
        out.append('        {%s, %s, %s, %s, %s, "%d", "%d", "%d", "%d", %s, %s},\n' % (
            jq(e['key']), jq('bx_' + e['key']), jq(e['names'][0]), jq(e['descs'][0]), jq(e['cat']), e['rar'], e['max'], e['w'], e['stage'], jq(req_str(e)),
            jq('~'.join(e['rules']))))
    out.append('    };\n\n')
    out.append('    /** Sinergias: clave, nombre, descripcion, pista, bendiciones necesarias, miembros (ids), reglas. */\n')
    out.append('    static final String[][] SYN = {\n')
    for s in SYNS:
        out.append('        {%s, %s, %s, %s, "%d", %s, %s},\n' % (jq(s['key']), jq(s['names'][0]), jq(s['descs'][0]), jq(s['hint'][0]), s['need'],
                                                              jq(','.join(str(ID[m]) for m in s['members'])), jq('~'.join(s['rules']))))
    out.append('    };\n\n')
    out.append('''    private static BSyn[] syns;
    private static int ruleIdx;

    static BRule[] rules(String joined, int owner, int syn) {
        if (joined.isEmpty()) return new BRule[0];
        String[] p = joined.split("~");
        BRule[] r = new BRule[p.length];
        for (int i = 0; i < p.length; i++) { r[i] = BRule.parse(p[i], owner); r[i].syn = syn; r[i].idx = ruleIdx++; }
        return r;
    }

    /** Construye las 200 bendiciones: las originales (ya declaradas) completadas con categoria y rareza, y las 172 nuevas. */
    static Blessing[] all(Blessing[] legacy) {
        Blessing[] a = new Blessing[200];
        for (int i = 0; i < legacy.length; i++) {
            Blessing b = legacy[i];
            a[i] = new Blessing(b.id, b.icon, b.name, b.desc, b.max, b.weight, LEG_CAT.charAt(i), LEG_RAR[i], 0, "", new BRule[0], LEG_KEY[i]);
        }
        for (int j = 0; j < NEW.length; j++) {
            String[] n = NEW[j];
            int id = legacy.length + j;
            a[id] = new Blessing(id, n[1], n[2], n[3], Integer.parseInt(n[6]), Integer.parseInt(n[7]), n[4].charAt(0), Integer.parseInt(n[5]), Integer.parseInt(n[8]), n[9], rules(n[10], id, -1), n[0]);
        }
        return a;
    }

    static BSyn[] syns() {
        if (syns == null) {
            BSyn[] s = new BSyn[SYN.length];
            for (int i = 0; i < s.length; i++) {
                String[] d = SYN[i];
                String[] m = d[5].split(",");
                int[] mem = new int[m.length];
                for (int k = 0; k < m.length; k++) mem[k] = Integer.parseInt(m[k]);
                s[i] = new BSyn(i, d[1], d[2], d[3], Integer.parseInt(d[4]), mem, rules(d[6], -1, i));
            }
            syns = s;
        }
        return syns;
    }
}
''')
    open(JAVA, 'w', encoding='utf8', newline='\n').write(''.join(out))


def gen_tsv():
    rows = []
    def add(es, en, fr, zh):
        for t in (es, en, fr, zh):
            assert '\t' not in t and '\n' not in t
        rows.append('\t'.join((es, en, fr, zh)))
    for e in ENTRIES:
        add(*e['names']); add(*e['descs'])
    for s in SYNS:
        add(*s['names']); add(*s['descs'])
    # pistas comunes de sinergia (plantillas con {})
    add('Reúne {} de sus bendiciones para activarla.', 'Gather {} of its blessings to activate it.', 'Réunissez {} de ses bénédictions pour l\'activer.', '集齐其中{}个祝福即可激活。')
    UI = [
        ('Sinergia activa', 'Synergy active', 'Synergie active', '协同已激活'),
        ('Sinergia {}/{}', 'Synergy {}/{}', 'Synergie {}/{}', '协同 {}/{}'),
        ('Bendiciones y sinergias', 'Blessings & synergies', 'Bénédictions et synergies', '祝福与协同'),
        ('Bendiciones', 'Blessings', 'Bénédictions', '祝福'),
        ('Bendiciones *', 'Blessings *', 'Bénédictions *', '祝福 *'),
        ('Sinergias', 'Synergies', 'Synergies', '协同'),
        ('Sinergias *', 'Synergies *', 'Synergies *', '协同 *'),
        ('BENDICIONES ACTIVAS', 'ACTIVE BLESSINGS', 'BÉNÉDICTIONS ACTIVES', '已有祝福'),
        ('SINERGIAS', 'SYNERGIES', 'SYNERGIES', '协同效果'),
        ('Pág. {}/{}', 'Page {}/{}', 'Page {}/{}', '第 {}/{} 页'),
        ('Aún no tienes ninguna sinergia en marcha.', 'You have no synergies going yet.', 'Aucune synergie en cours pour l\'instant.', '你还没有任何协同效果。'),
        ('ACTIVA {}/{}', 'ACTIVE {}/{}', 'ACTIVE {}/{}', '已激活 {}/{}'),
        ('Nv {}/{}', 'Lv {}/{}', 'Niv {}/{}', '等级 {}/{}'),
        ('+{} más', '+{} more', '+{} de plus', '另有 {} 个'),
        ('¡Sinergia activada!', 'Synergy activated!', 'Synergie activée !', '协同已激活！'),
        ('Aparece con {} bendiciones de su categoría', 'Appears with {} blessings of its category', 'Apparaît avec {} bénédictions de sa catégorie', '拥有{}个同类祝福时出现'),
        ('Aparece con {} bendiciones de su familia', 'Appears with {} blessings of its family', 'Apparaît avec {} bénédictions de sa famille', '拥有{}个同系祝福时出现'),
    ]
    for u in UI:
        add(*u)
    for c in CATS:
        add(*CAT_NAMES[c])
    for i, r in enumerate(RAR):
        add(r, RAR_EN[i], ['commune', 'peu commune', 'rare', 'épique', 'légendaire'][i], ['普通', '罕见', '稀有', '史诗', '传说'][i])
    seen = set(); out = []
    for r in rows:
        k = r.split('\t')[0]
        if k in seen: continue
        seen.add(k); out.append(r)
    open(TSV, 'w', encoding='utf8', newline='\n').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    check(); gen_java(); gen_tsv()
    print('ok', len(ENTRIES), 'nuevas;', len(SYNS), 'sinergias')
