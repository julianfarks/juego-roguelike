from bl import *

# ===================== B. MAGIA Y ELEMENTOS =====================
a = 20
B('B', C, 'combustion', ('Combustión', 'Combustion', 'Combustion', '燃烧强化'),
  ('El daño periódico (fuego, veneno, sangrado) hace +{a}% por nivel.', 'Damage over time (burn, poison, bleed) deals +{a}% per level.',
   'Les dégâts sur la durée (feu, poison, saignement) font +{a} % par niveau.', '持续伤害（燃烧、中毒、流血）+{a}%（每级）。'),
  [f'MOD||DOT:{a/100}|scale'], mx=2, ic=('flame', 'drop', 'lava'), a=a)
B('B', U, 'llama_voraz', ('Llama Voraz', 'Ravenous Flame', 'Flamme vorace', '贪婪之焰'),
  ('Los enemigos en llamas reciben +15% de daño de tus golpes y habilidades.', 'Burning enemies take +15% damage from your hits and skills.',
   'Les ennemis en flammes subissent +15 % de dégâts de vos coups et compétences.', '燃烧中的敌人受到你的攻击和技能伤害+15%。'),
  ['MOD|v:burn|DMG:0.15'], ic=('flame', 'sword', 'fire'))
B('B', R, 'brasa_critica', ('Brasa Crítica', 'Critical Ember', 'Braise critique', '暴击余烬'),
  ('+25% de probabilidad de crítico contra enemigos en llamas.', '+25% critical chance against burning enemies.',
   '+25 % de chance de critique contre les ennemis en flammes.', '对燃烧中的敌人暴击率+25%。'),
  ['MOD|v:burn|CRIT:0.25'], ic=('flame', 'star', 'orange'))
B('B', U, 'contagio_igneo', ('Contagio Ígneo', 'Fire Contagion', 'Contagion ignée', '火焰传染'),
  ('Cuando muere un enemigo en llamas, el fuego salta a los cercanos.', 'When a burning enemy dies, the fire jumps to nearby enemies.',
   'Quand un ennemi en flammes meurt, le feu saute aux ennemis proches.', '燃烧的敌人死亡时，火焰蔓延到附近的敌人。'),
  ['KILL|v:burn|SPREAD:burn,85'], ic=('flame', 'chain', 'fire'))
B('B', R, 'pira', ('Pira Viviente', 'Living Pyre', 'Bûcher vivant', '活体火葬'),
  ('Los enemigos en llamas explotan al morir (60% de daño) y prenden fuego alrededor.', 'Burning enemies explode on death (60% damage) and ignite those around.',
   'Les ennemis en flammes explosent à leur mort (60 % de dégâts) et enflamment les alentours.', '燃烧的敌人死亡时爆炸（60%伤害）并点燃周围。'),
  ['KILL|v:burn|EXPLODE:52,0.6,burn,3|icd=0.15'], stage=1, ic=('flame', 'bomb', 'lava'))
B('B', EP, 'aliento_dragon', ('Aliento de Dragón', 'Dragon Breath', 'Souffle de dragon', '龙息'),
  ('Tu definitiva prende fuego a todos los enemigos durante 4 s.', 'Your ultimate sets all enemies on fire for 4 s.',
   'Votre ultime enflamme tous les ennemis pendant 4 s.', '你的终极技能点燃所有敌人，持续4秒。'),
  ['ULT||STATUS:burn,4,1.5|aoe=9999'], stage=1, ic=('flame', 'crown', 'lava'))
B('B', U, 'rastro_ardiente', ('Rastro Ardiente', 'Burning Trail', 'Traînée ardente', '烈焰轨迹'),
  ('Al rodar dejas dos charcos de fuego que queman a los enemigos.', 'Rolling leaves two fire patches that burn enemies.',
   'En roulant, vous laissez deux flaques de feu qui brûlent les ennemis.', '翻滚时留下两处火焰，灼烧敌人。'),
  ['ROLL||TRAIL:fire,2.5,1.2', 'ROLLEND||TRAIL:fire,2.5,1.2'], ic=('flame', 'boot', 'orange'))
B('B', R, 'escarcha_quebradiza', ('Escarcha Quebradiza', 'Brittle Frost', 'Givre fragile', '易碎寒霜'),
  ('+35% de probabilidad de crítico contra enemigos ralentizados o congelados.', '+35% critical chance against slowed or frozen enemies.',
   '+35 % de chance de critique contre les ennemis ralentis ou gelés.', '对减速或冰冻的敌人暴击率+35%。'),
  ['MOD|v:slow|CRIT:0.35'], ic=('snow', 'star', 'ice'))
B('B', U, 'esquirlas_hielo', ('Esquirlas de Hielo', 'Ice Shards', 'Éclats de glace', '冰晶碎片'),
  ('Los enemigos ralentizados o congelados sueltan 3 esquirlas al morir.', 'Slowed or frozen enemies release 3 shards on death.',
   'Les ennemis ralentis ou gelés libèrent 3 éclats à leur mort.', '减速或冰冻的敌人死亡时释放3枚冰晶。'),
  ['KILL|v:slow|PROJ:shard,3,0.45,slow|icd=0.2'], ic=('snow', 'dagger', 'cyan'))
B('B', U, 'aura_gelida', ('Aura Gélida', 'Frost Aura', 'Aura glaciale', '寒霜光环'),
  ('Cada 3 s ralentizas a los enemigos cercanos.', 'Every 3 s you slow nearby enemies.', 'Toutes les 3 s, vous ralentissez les ennemis proches.', '每3秒使附近的敌人减速。'),
  ['TICK|r:combat|STATUS:slow,2,1|aoe=80 every=3'], ic=('snow', 'ring', 'blue'))
B('B', U, 'ventisca', ('Ventisca', 'Blizzard', 'Blizzard', '暴风雪'),
  ('Tus habilidades ralentizan a los enemigos en un radio amplio.', 'Your skills slow enemies in a wide radius.', 'Vos compétences ralentissent les ennemis dans un large rayon.', '你的技能使大范围内的敌人减速。'),
  ['SKILL||STATUS:slow,3,1|aoe=140'], ic=('snow', 'orb', 'white'))
B('B', EP, 'congelacion_profunda', ('Congelación Profunda', 'Deep Freeze', 'Gel profond', '深度冻结'),
  ('Golpear a un enemigo ralentizado: 12% de congelarlo 1,2 s (cada 2 s). Los jefes solo se ralentizan.', 'Hitting a slowed enemy: 12% chance to freeze it for 1.2 s (every 2 s). Bosses only get slowed.',
   'Frapper un ennemi ralenti : 12 % de le geler 1,2 s (toutes les 2 s). Les boss sont seulement ralentis.', '攻击减速的敌人：12%几率冻结1.2秒（每2秒）。首领仅被减速。'),
  ['HIT|v:slow,!v:freeze|STATUS:freeze,1.2,1|ch=0.12 icd=2'], ic=('snow', 'crown', 'ice'))
B('B', C, 'carga_estatica', ('Carga Estática', 'Static Charge', 'Charge statique', '静电充能'),
  ('Tus golpes acumulan carga arcana (máx. 10). Al llegar a 10 se libera un rayo encadenado.', 'Your hits build arcane charge (max 10). At 10 it releases a chain lightning.',
   'Vos coups accumulent de la charge arcanique (max 10). À 10, elle libère un éclair en chaîne.', '攻击积累奥术电荷（最多10）。满10时释放连锁闪电。'),
  ['HIT||ARC:1|icd=0.1', 'HIT|p:arc>=10|DISCHARGE:2,0.3|icd=1'], ic=('bolt', 'orb', 'yel'))
B('B', R, 'pararrayos', ('Pararrayos', 'Lightning Rod', 'Paratonnerre', '避雷针'),
  ('Cada parry da 2 cargas arcanas y libera una descarga con todas tus cargas.', 'Each parry grants 2 arcane charges and releases a discharge with all your charges.',
   'Chaque parade donne 2 charges arcaniques et libère une décharge avec toutes vos charges.', '每次格挡获得2点电荷并释放全部电荷的放电。'),
  ['PARRY||ARC:2', 'PARRY|p:arc>=1|DISCHARGE:3,0.4'], ic=('bolt', 'shield', 'blue'))
B('B', U, 'voltio_arcano', ('Voltio Arcano', 'Arcane Volt', 'Volt arcanique', '奥术伏特'),
  ('Cada habilidad que lanzas te da 3 cargas arcanas.', 'Each skill you cast gives you 3 arcane charges.', 'Chaque compétence lancée vous donne 3 charges arcaniques.', '每次施放技能获得3点电荷。'),
  ['SKILL||ARC:3'], ic=('bolt', 'book', 'purple'))
B('B', R, 'bateria', ('Batería Viva', 'Living Battery', 'Batterie vivante', '活体电池'),
  ('Cada esquiva o rodar exitoso da 2 cargas arcanas.', 'Each dodge or roll grants 2 arcane charges.', 'Chaque esquive ou roulade donne 2 charges arcaniques.', '每次闪避或翻滚获得2点电荷。'),
  ['ROLL||ARC:2|icd=0.4', 'DODGE||ARC:2|icd=0.4'], ic=('bolt', 'boot', 'cyan'))
B('B', EP, 'descarga_mayor', ('Descarga Mayor', 'Grand Discharge', 'Grande décharge', '大放电'),
  ('Con 6 o más cargas arcanas, tus golpes sueltan una descarga de 4 saltos (cada 1,5 s).', 'With 6 or more arcane charges, your hits release a 4-jump discharge (every 1.5 s).',
   'Avec 6 charges arcaniques ou plus, vos coups libèrent une décharge à 4 sauts (toutes les 1,5 s).', '电荷不少于6时，攻击释放4次跳跃的放电（每1.5秒）。'),
  ['HIT|p:arc>=6|DISCHARGE:4,0.35|icd=1.5'], stage=1, ic=('bolt', 'crown', 'yel'))
B('B', U, 'conductor', ('Conductor', 'Conductor', 'Conducteur', '导体'),
  ('Tus rayos encadenados saltan a 1 enemigo más.', 'Your chain lightning jumps to 1 more enemy.', 'Vos éclairs en chaîne sautent vers 1 ennemi de plus.', '你的连锁闪电多跳跃1个敌人。'),
  ['MOD||CHAINJUMPS:1'], ic=('bolt', 'chain', 'white'))
B('B', L, 'tempestad_eterna', ('Tempestad Eterna', 'Eternal Tempest', 'Tempête éternelle', '永恒风暴'),
  ('En combate, cada 4 s caen 3 rayos sobre enemigos al azar.', 'In combat, every 4 s three lightning bolts strike random enemies.',
   'En combat, toutes les 4 s trois éclairs frappent des ennemis au hasard.', '战斗中每4秒有3道闪电劈向随机敌人。'),
  ['TICK|r:combat|STRIKE:3,1.1|every=4'], stage=2, req=('has', 2, ['carga_estatica', 'pararrayos', 'voltio_arcano', 'bateria', 'descarga_mayor', 'conductor', 'CHISPA']),
  ic=('bolt', 'sun', 'yel'))
B('B', U, 'ponzona_virulenta', ('Ponzoña Virulenta', 'Virulent Venom', 'Venin virulent', '剧毒'),
  ('Tus estados alterados duran 40% más.', 'Your status effects last 40% longer.', 'Vos états altérés durent 40 % plus longtemps.', '你的异常状态持续时间延长40%。'),
  ['MOD||STATUSDUR:0.4'], ic=('drop', 'hourglass', 'green'))
B('B', R, 'plaga', ('Plaga', 'Plague', 'Peste', '瘟疫'),
  ('Cuando muere un enemigo envenenado, el veneno se contagia a los cercanos.', 'When a poisoned enemy dies, the poison spreads to nearby enemies.',
   'Quand un ennemi empoisonné meurt, le poison se propage aux ennemis proches.', '中毒的敌人死亡时，毒素传染给附近的敌人。'),
  ['KILL|v:poison|SPREAD:poison,95'], ic=('skull', 'drop', 'green'))
B('B', U, 'toxina_nerviosa', ('Toxina Nerviosa', 'Nerve Toxin', 'Toxine nerveuse', '神经毒素'),
  ('40% de ralentizar al golpear a un enemigo envenenado.', '40% chance to slow when hitting a poisoned enemy.', '40 % de ralentir en frappant un ennemi empoisonné.', '攻击中毒的敌人时，40%几率使其减速。'),
  ['HIT|v:poison|STATUS:slow,2,1|ch=0.4'], ic=('drop', 'snow', 'teal'))
B('B', U, 'esporas', ('Esporas Tóxicas', 'Toxic Spores', 'Spores toxiques', '毒孢子'),
  ('En combate, cada 6 s una nube envenena a los enemigos cercanos.', 'In combat, every 6 s a cloud poisons nearby enemies.', 'En combat, toutes les 6 s un nuage empoisonne les ennemis proches.', '战斗中每6秒，毒云使附近的敌人中毒。'),
  ['TICK|r:combat|STATUS:poison,4,1|aoe=100 every=6'], ic=('leaf', 'drop', 'green'))
B('B', R, 'eco_arcano', ('Eco Arcano', 'Arcane Echo', 'Écho arcanique', '奥术回响'),
  ('Tras lanzar una habilidad, tu siguiente golpe hace +50% de daño (5 s).', 'After casting a skill, your next hit deals +50% damage (5 s).',
   'Après avoir lancé une compétence, votre prochain coup inflige +50 % de dégâts (5 s).', '施放技能后，下一次攻击伤害+50%（5秒）。'),
  ['SKILL||NEXTHIT:0.5,5'], ic=('book', 'sword', 'purple'))
B('B', U, 'canalizador', ('Canalizador', 'Channeler', 'Canalisateur', '导能者'),
  ('Cada golpe acorta 0,25 s la reutilización de tu habilidad más lenta (límite por segundo).', 'Each hit shortens your slowest skill cooldown by 0.25 s (rate-limited).',
   'Chaque coup réduit de 0,25 s la recharge de votre compétence la plus lente (limité).', '每次攻击使最慢的技能冷却缩短0.25秒（有速率上限）。'),
  ['HIT|!p:cdall|CDR:0.25,1|icd=0.3'], ic=('book', 'hourglass', 'blue'))
B('B', EP, 'catalizador', ('Catalizador', 'Catalyst', 'Catalyseur', '催化剂'),
  ('Al usar tu definitiva, tus habilidades se reponen al instante.', 'Using your ultimate instantly resets your skills.', 'Utiliser votre ultime réinitialise instantanément vos compétences.', '使用终极技能时，立即重置所有技能冷却。'),
  ['ULT||COOLDOWNALL'], stage=1, ic=('hourglass', 'crown', 'purple'))
B('B', U, 'resonancia', ('Resonancia', 'Resonance', 'Résonance', '共鸣'),
  ('Cada habilidad potencia la siguiente: +35% de daño (6 s).', 'Each skill empowers the next one: +35% damage (6 s).', 'Chaque compétence renforce la suivante : +35 % de dégâts (6 s).', '每个技能强化下一个技能：伤害+35%（6秒）。'),
  ['SKILL||NEXTSKILL:0.35,6'], ic=('book', 'ring', 'pink'))
B('B', U, 'manantial', ('Manantial de Maná', 'Mana Spring', 'Source de mana', '法力之泉'),
  ('Cada habilidad lanzada carga un 6% de tu definitiva.', 'Each skill cast charges 6% of your ultimate.', 'Chaque compétence lancée charge 6 % de votre ultime.', '每次施放技能为终极技能充能6%。'),
  ['SKILL||ULT:6'], ic=('orb', 'star', 'cyan'))
B('B', R, 'runa_poder', ('Runa de Poder', 'Rune of Power', 'Rune de puissance', '力量符文'),
  ('+25% de carga de definitiva y +10% de daño de habilidades.', '+25% ultimate charge and +10% skill damage.', '+25 % de charge d\'ultime et +10 % de dégâts de compétence.', '终极技能充能+25%，技能伤害+10%。'),
  ['MOD||ULTGAIN:0.25', 'MOD||SKILLDMG:0.10'], ic=('star', 'book', 'gold'))
