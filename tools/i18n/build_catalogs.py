#!/usr/bin/env python3
"""Une tools/i18n/parts/*.tsv (es<TAB>en<TAB>fr<TAB>zh) en assets/i18n/{en,fr,zh-Hans}.tsv y valida."""
import glob, os, re, sys
root = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(root, '..', '..', 'Shared', 'assets', 'i18n')
langs = ['en', 'fr', 'zh-Hans']
data = {l: {} for l in langs}
errs = 0
def lig(s):  # la fuente pixel no tiene œ/Œ
    s = re.sub('Œ(?=[a-zà-ÿ])', 'Oe', s)
    return s.replace('Œ', 'OE').replace('œ', 'oe')
def esc(s): return s.replace('\\', '\\\\').replace('\n', '\\n').replace('\t', '\\t')
def unesc_nl(s): return s.replace('\\n', '\n')
for f in sorted(glob.glob(os.path.join(root, 'parts', '*.tsv'))):
    for n, line in enumerate(open(f, encoding='utf8').read().split('\n'), 1):
        if not line or line.startswith('#'): continue
        c = line.split('\t')
        if len(c) != 4:
            print('COLUMNAS', os.path.basename(f), n, repr(line[:60])); errs += 1; continue
        k = c[0]
        for i, l in enumerate(langs):
            v = lig(c[i + 1])
            if k.count('{}') != v.count('{}'):
                print('PLACEHOLDERS', l, os.path.basename(f), n, repr(k[:50])); errs += 1
            if v == '' : print('VACIO', l, k[:40]); errs += 1
            if k in data[l] and data[l][k] != v:
                print('CONFLICTO', l, repr(k[:50]), '|', data[l][k], '|', v); errs += 1
            data[l].setdefault(k, v)
os.makedirs(out, exist_ok=True)
for l in langs:
    with open(os.path.join(out, l + '.tsv'), 'w', encoding='utf8', newline='\n') as fh:
        fh.write('# %s generado por tools/i18n/build_catalogs.py (clave = texto en espanol)\n' % l)
        for k, v in data[l].items(): fh.write(esc(k) + '\t' + esc(v) + '\n')
    print(l, len(data[l]))
sys.exit(1 if errs else 0)
