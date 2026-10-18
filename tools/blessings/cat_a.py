from bl import *

# ===================== A. DAÑO FISICO =====================
a = 25
B('A', C, 'certero', ('Golpe Certero', 'Sure Strike', 'Frappe sûre', '精准一击'),
  ('Cada 4 golpes seguidos, el siguiente hace +{a}% de daño por nivel.', 'Every 4 consecutive hits, the next one deals +{a}% damage per level.',
   'Tous les 4 coups enchaînés, le suivant inflige +{a} % de dégâts par niveau.', '每连续命中4次，下一击伤害+{a}%（每级）。'),
  [f'STREAK||NEXTHIT:{a/100},4|n=4 scale'], mx=3, ic=('sword', 'star', 'steel'), a=a)
a = 7
B('A', C, 'hoja_rapida', ('Hoja Rápida', 'Swift Blade', 'Lame vive', '迅捷之刃'),
  ('+{a}% de velocidad de ataque por nivel.', '+{a}% attack speed per level.', '+{a} % de vitesse d\'attaque par niveau.', '攻击速度+{a}%（每级）。'),
  [f'MOD||ATKSPD:{a/100}|scale'], mx=3, ic=('sword', 'wing', 'white'), a=a)
a = 18
B('A', C, 'peso_pesado', ('Peso Pesado', 'Heavyweight', 'Poids lourd', '重量级'),
  ('+{a}% de daño por nivel a enemigos con más del 80% de vida.', '+{a}% damage per level to enemies above 80% health.',
   '+{a} % de dégâts par niveau aux ennemis à plus de 80 % de vie.', '对生命高于80%的敌人伤害+{a}%（每级）。'),
  [f'MOD|v:high|DMG:{a/100}|scale'], mx=2, ic=('hammer', 'heart', 'stone'), a=a)
a = 22
B('A', U, 'rompeguardias', ('Rompeguardias', 'Guard Breaker', 'Brise-garde', '破卫者'),
  ('+{a}% de daño por nivel contra mini-jefes y jefes.', '+{a}% damage per level against mini-bosses and bosses.',
   '+{a} % de dégâts par niveau contre mini-boss et boss.', '对精英和首领伤害+{a}%（每级）。'),
  [f'MOD|v:elite|DMG:{a/100}|scale'], mx=2, ic=('hammer', 'crown', 'copper'), a=a)
a = 35
B('A', U, 'punalada', ('Puñalada Trapera', 'Backstab', 'Coup dans le dos', '背刺'),
  ('Golpear a un enemigo por la espalda: +{a}% de daño.', 'Hitting an enemy from behind: +{a}% damage.',
   'Frapper un ennemi dans le dos : +{a} % de dégâts.', '从背后攻击敌人：伤害+{a}%。'),
  [f'MOD|v:back|DMG:{a/100}'], ic=('dagger', 'ghost', 'dark'), a=a)
a = 15
B('A', U, 'enjambre', ('Cazador de Enjambres', 'Swarm Hunter', 'Chasseur d\'essaims', '猎群者'),
  ('+{a}% de daño por nivel a enemigos con otros dos cerca.', '+{a}% damage per level to enemies with two others nearby.',
   '+{a} % de dégâts par niveau aux ennemis entourés d\'au moins deux autres.', '对周围有其他敌人的目标伤害+{a}%（每级）。'),
  [f'MOD|v:crowd|DMG:{a/100}|scale'], mx=2, ic=('sword', 'skull', 'bone'), a=a)
a = 18
B('A', U, 'alcance', ('Estocada Larga', 'Long Thrust', 'Estoc long', '长刺'),
  ('+{a}% de alcance de arma por nivel.', '+{a}% weapon reach per level.', '+{a} % de portée d\'arme par niveau.', '武器攻击范围+{a}%（每级）。'),
  [f'MOD||REACH:{a/100}|scale'], mx=2, ic=('sword', 'arrow', 'steel'), a=a)
B('A', U, 'sangria', ('Filo Sangrante', 'Bleeding Edge', 'Lame saignante', '放血之刃'),
  ('25% de causar sangrado. Los enemigos sangrando reciben +15% de daño de tus golpes.', '25% chance to cause bleeding. Bleeding enemies take +15% damage from your hits.',
   '25 % de provoquer un saignement. Les ennemis qui saignent subissent +15 % de dégâts de vos coups.', '25%几率造成流血。流血的敌人受到你的攻击伤害+15%。'),
  ['HIT|!v:bleed|STATUS:bleed,4,1.2|ch=0.25', 'MOD|v:bleed|DMG:0.15|src=W'], ic=('sword', 'drop', 'red'))
B('A', R, 'doble_tajo', ('Doble Tajo', 'Double Slash', 'Double entaille', '双重斩'),
  ('18% de que tu golpe se repita poco después con el 40% del daño.', '18% chance for your hit to repeat shortly after for 40% damage.',
   '18 % de chance que votre coup se répète peu après avec 40 % des dégâts.', '18%几率使你的攻击稍后重复，造成40%伤害。'),
  ['HIT||REPEAT:0.4|ch=0.18 icd=0.35'], ic=('sword', 'sword', 'white'))
B('A', EP, 'impulso_letal', ('Impulso Letal', 'Lethal Momentum', 'Élan létal', '致命势头'),
  ('Cada crítico da +7% de daño durante 4 s (hasta 5 cargas).', 'Each critical hit gives +7% damage for 4 s (up to 5 stacks).',
   'Chaque critique donne +7 % de dégâts pendant 4 s (jusqu\'à 5 cumuls).', '每次暴击伤害+7%，持续4秒（最多5层）。'),
  ['CRIT||BUFF:dmg,0.07,4,5'], ic=('star', 'sword', 'gold'))
a = 14
B('A', U, 'pulso_constante', ('Pulso Constante', 'Steady Pulse', 'Pouls régulier', '稳定节奏'),
  ('Los golpes no críticos hacen +{a}% de daño por nivel.', 'Non-critical hits deal +{a}% damage per level.',
   'Les coups non critiques infligent +{a} % de dégâts par niveau.', '非暴击攻击伤害+{a}%（每级）。'),
  [f'MOD||NONCRIT:{a/100}|scale'], mx=2, ic=('hand', 'sword', 'stone'), a=a)
a = 25
B('A', U, 'remate_brutal', ('Remate Brutal', 'Brutal Finisher', 'Finisseur brutal', '残暴终结'),
  ('El tercer golpe del combo hace +{a}% de daño por nivel.', 'The third hit of the combo deals +{a}% damage per level.',
   'Le troisième coup du combo inflige +{a} % de dégâts par niveau.', '连击第三击伤害+{a}%（每级）。'),
  [f'MOD||FINISHMUL:{a/100}|scale'], mx=2, ic=('fist', 'skull', 'red'), a=a)
B('A', R, 'combo_ritmo', ('Ritmo de Combate', 'Battle Rhythm', 'Rythme de combat', '战斗节奏'),
  ('Cada remate de combo da +10% de velocidad de ataque durante 3 s (hasta 3 cargas).', 'Each combo finisher gives +10% attack speed for 3 s (up to 3 stacks).',
   'Chaque fin de combo donne +10 % de vitesse d\'attaque pendant 3 s (jusqu\'à 3 cumuls).', '每次连击终结攻击速度+10%，持续3秒（最多3层）。'),
  ['FINISH||BUFF:atk,0.10,3,3'], ic=('fist', 'wing', 'orange'))
B('A', L, 'sentencia', ('Sentencia', 'Verdict', 'Sentence', '审判之刃'),
  ('Tu remate detona una explosión de 200% de daño cada 4 s.', 'Your finisher detonates an explosion for 200% damage every 4 s.',
   'Votre finisseur déclenche une explosion à 200 % de dégâts toutes les 4 s.', '连击终结引发爆炸，造成200%伤害，每4秒一次。'),
  ['FINISH||EXPLODE:72,2.0|icd=4'], stage=1, req=('cat', 'A', 3), ic=('sword', 'sun', 'gold'))
B('A', R, 'maestro_armas', ('Maestro de Armas', 'Weapon Master', 'Maître d\'armes', '武器大师'),
  ('Con la vida al 90% o más: +30% de daño de arma.', 'At 90% health or more: +30% weapon damage.',
   'À 90 % de vie ou plus : +30 % de dégâts d\'arme.', '生命值不低于90%时，武器伤害+30%。'),
  ['MOD|p:high|DMG:0.30|src=W'], ic=('sword', 'crown', 'gold'))
B('A', U, 'sed_batalla', ('Sed de Batalla', 'Battle Thirst', 'Soif de bataille', '战斗渴望'),
  ('Cada baja da +12% de velocidad de ataque durante 3 s (hasta 2 cargas).', 'Each kill gives +12% attack speed for 3 s (up to 2 stacks).',
   'Chaque kill donne +12 % de vitesse d\'attaque pendant 3 s (jusqu\'à 2 cumuls).', '每次击杀攻击速度+12%，持续3秒（最多2层）。'),
  ['KILL||BUFF:atk,0.12,3,2'], ic=('skull', 'wing', 'red'))
a = 5
B('A', C, 'ojo_halcon', ('Ojo de Halcón', 'Hawk Eye', 'Œil de faucon', '鹰眼'),
  ('+{a}% de probabilidad de crítico por nivel.', '+{a}% critical chance per level.', '+{a} % de chance de critique par niveau.', '暴击率+{a}%（每级）。'),
  [f'MOD||CRIT:{a/100}|scale'], mx=3, ic=('eye', 'star', 'yel'), a=a)
B('A', R, 'ensanamiento', ('Ensañamiento', 'Overkill', 'Acharnement', '赶尽杀绝'),
  ('Los críticos contra enemigos con menos del 30% de vida hacen +50% de daño crítico extra.', 'Critical hits against enemies below 30% health deal +50% extra critical damage.',
   'Les critiques contre les ennemis à moins de 30 % de vie infligent +50 % de dégâts critiques en plus.', '对生命低于30%的敌人暴击伤害额外+50%。'),
  ['MOD|v:low|CRITMUL:0.5'], ic=('eye', 'skull', 'red'))
B('A', EP, 'cadena_criticos', ('Cadena de Críticos', 'Critical Chain', 'Chaîne critique', '暴击连锁'),
  ('Tras 2 críticos seguidos, +20% de probabilidad de crítico hasta que falles un golpe o te hieran.', 'After 2 consecutive crits, +20% crit chance until you miss a crit or get hurt.',
   'Après 2 critiques d\'affilée, +20 % de chance de critique jusqu\'à un coup non critique ou une blessure.', '连续2次暴击后，暴击率+20%，直到某次攻击未暴击或你受伤。'),
  ['MOD|p:crits>=2|CRIT:0.20'], ic=('star', 'ring', 'gold'))
