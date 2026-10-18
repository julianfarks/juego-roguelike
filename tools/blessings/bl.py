"""Ayudantes del catalogo de bendiciones (ver docs/BENDICIONES.md). Cada entrada: B(...) y cada sinergia: S(...)."""
CATS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
CAT_NAMES = {
    'A': ('Daño físico', 'Physical damage', 'Dégâts physiques', '物理伤害'),
    'B': ('Magia y elementos', 'Magic & elements', 'Magie et éléments', '魔法与元素'),
    'C': ('Defensa y supervivencia', 'Defense & survival', 'Défense et survie', '防御与生存'),
    'D': ('Velocidad y evasión', 'Speed & evasion', 'Vitesse et esquive', '速度与闪避'),
    'E': ('Proyectiles', 'Projectiles', 'Projectiles', '投射物'),
    'F': ('Recursos y recompensas', 'Resources & rewards', 'Ressources et récompenses', '资源与奖励'),
    'G': ('Invocaciones y compañeros', 'Summons & companions', 'Invocations et compagnons', '召唤与伙伴'),
    'H': ('Riesgo y recompensa', 'Risk & reward', 'Risque et récompense', '风险与回报'),
    'I': ('Maldiciones y transformaciones', 'Curses & transformations', 'Malédictions et transformations', '诅咒与变身'),
    'J': ('Híbridas', 'Hybrids', 'Hybrides', '混合'),
}
RAR = ['común', 'poco común', 'rara', 'épica', 'legendaria']
RAR_EN = ['common', 'uncommon', 'rare', 'epic', 'legendary']
C, U, R, EP, L = 0, 1, 2, 3, 4

ENTRIES = []
SYNS = []
KEYS = set()


def pc(x):
    return str(int(round(x * 100)))


def fmt(s, kw):
    return s.format(**kw) if kw else s


def B(cat, rar, key, names, descs, rules=(), mx=1, w=None, stage=0, req=None, ic=None, **kw):
    """names/descs = (es,en,fr,zh); las descripciones usan {x} con los numeros de kw (los mismos que las reglas)."""
    assert key not in KEYS, key
    KEYS.add(key)
    assert len(names) == 4 and len(descs) == 4, key
    if w is None:
        w = [10, 8, 6, 4, 2][rar]
    ENTRIES.append(dict(cat=cat, rar=rar, key=key, names=names, descs=tuple(fmt(d, kw) for d in descs), rules=list(rules), max=mx,
                        w=w, stage=stage, req=req, ic=ic))


def S(key, names, descs, need, members, rules, hint):
    """Sinergia. members = claves de bendicion (nuevas o heredadas); hint = (es,en,fr,zh) pista corta de como activarla."""
    SYNS.append(dict(key=key, names=names, descs=descs, need=need, members=members, rules=list(rules), hint=hint))

LEGACY = ['FILO', 'CORAZON', 'ALAS', 'FURIA', 'SANGRE', 'BRASAS', 'GLACIAL', 'CHISPA', 'ESPINAS', 'PIEDRA', 'FANTASMA', 'DOBLE_SALTO', 'CRITICO', 'ALMA', 'FORTUNA',
          'ESCUDO', 'ENFRIAMIENTO', 'HABILIDAD', 'EJECUTOR', 'IMAN', 'VENGANZA', 'SEGUNDA', 'ONDA', 'EGIDA', 'SABIO', 'GIGANTE', 'SOMBRA', 'ECLIPSE']
# categoria y rareza de las 28 bendiciones originales (su logica sigue en Stats/Player/Level; solo se clasifican)
LEGACY_META = {
    'FILO': ('A', C), 'CORAZON': ('C', C), 'ALAS': ('D', C), 'FURIA': ('A', U), 'SANGRE': ('C', U), 'BRASAS': ('B', U), 'GLACIAL': ('B', U), 'CHISPA': ('B', U),
    'ESPINAS': ('B', U), 'PIEDRA': ('C', C), 'FANTASMA': ('D', R), 'DOBLE_SALTO': ('D', U), 'CRITICO': ('A', U), 'ALMA': ('F', C), 'FORTUNA': ('F', C),
    'ESCUDO': ('C', U), 'ENFRIAMIENTO': ('B', C), 'HABILIDAD': ('B', C), 'EJECUTOR': ('A', U), 'IMAN': ('F', C), 'VENGANZA': ('J', R), 'SEGUNDA': ('C', EP),
    'ONDA': ('E', U), 'EGIDA': ('C', U), 'SABIO': ('B', U), 'GIGANTE': ('A', R), 'SOMBRA': ('D', R), 'ECLIPSE': ('A', EP)}
