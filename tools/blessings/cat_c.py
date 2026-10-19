from bl import *

# ===================== C. DEFENSA, PARRY Y SUPERVIVENCIA =====================
B('C', U, 'contra_parry', ('Contra del Parry', 'Parry Counter', 'Contre de parade', '格挡反击'),
  ('Tras un parry, tu siguiente golpe hace +60% de daño (4 s).', 'After a parry, your next hit deals +60% damage (4 s).', 'Après une parade, votre prochain coup inflige +60 % de dégâts (4 s).', '格挡后，下一次攻击伤害+60%（4秒）。'),
  ['PARRY||NEXTHIT:0.6,4'], ic=('shield', 'sword', 'steel'))
B('C', U, 'parry_escudo', ('Parry Templado', 'Tempered Parry', 'Parade trempée', '格挡护盾'),
  ('Cada parry te da un escudo de 15.', 'Each parry grants a 15-point shield.', 'Chaque parade vous donne un bouclier de 15.', '每次格挡获得15点护盾。'),
  ['PARRY||SHIELD:15'], ic=('shield', 'star', 'blue'))
B('C', U, 'parry_ulti', ('Parry Cargado', 'Charged Parry', 'Parade chargée', '格挡蓄能'),
  ('Cada parry carga un 8% de tu definitiva.', 'Each parry charges 8% of your ultimate.', 'Chaque parade charge 8 % de votre ultime.', '每次格挡为终极技能充能8%。'),
  ['PARRY||ULT:8'], ic=('shield', 'orb', 'gold'))
B('C', R, 'eco_defensivo', ('Eco Defensivo', 'Defensive Echo', 'Écho défensif', '防御回响'),
  ('Cada parry libera una onda de 100% de daño que empuja a los enemigos.', 'Each parry releases a 100% damage wave that pushes enemies back.', 'Chaque parade libère une onde à 100 % de dégâts qui repousse les ennemis.', '每次格挡释放100%伤害的冲击波，击退敌人。'),
  ['PARRY||EXPLODE:72,1.0|aoe=-1 icd=0.5'], ic=('shield', 'ring', 'white'))
B('C', R, 'parry_maestro', ('Maestro del Parry', 'Parry Master', 'Maître de la parade', '格挡大师'),
  ('Cada parry da +12% de daño durante 5 s (hasta 3 cargas).', 'Each parry gives +12% damage for 5 s (up to 3 stacks).', 'Chaque parade donne +12 % de dégâts pendant 5 s (jusqu\'à 3 cumuls).', '每次格挡伤害+12%，持续5秒（最多3层）。'),
  ['PARRY||BUFF:dmg,0.12,5,3'], ic=('shield', 'crown', 'gold'))
B('C', EP, 'reflejo', ('Reflejo Estelar', 'Star Reflection', 'Reflet stellaire', '星辰反射'),
  ('Cada parry dispara un anillo de 8 estrellas (50% de daño).', 'Each parry fires a ring of 8 stars (50% damage).', 'Chaque parade tire un anneau de 8 étoiles (50 % de dégâts).', '每次格挡发射8颗星星组成的环（50%伤害）。'),
  ['PARRY||PROJ:ring,8,0.5|icd=0.8'], stage=1, ic=('shield', 'star', 'yel'))
B('C', U, 'parry_calma', ('Calma del Guardián', 'Guardian\'s Calm', 'Calme du gardien', '守护者的平静'),
  ('Cada parry cura el 3% de tu vida máxima (límite por sala).', 'Each parry heals 3% of your max health (limited per room).', 'Chaque parade soigne 3 % de votre vie max (limité par salle).', '每次格挡恢复3%最大生命（每个房间有上限）。'),
  ['PARRY||HEAL:0.03'], ic=('shield', 'heart', 'green'))
B('C', U, 'escudo_reactivo', ('Escudo Reactivo', 'Reactive Shield', 'Bouclier réactif', '反应护盾'),
  ('Cuando tu escudo absorbe un golpe, estalla con 80% de daño a tu alrededor.', 'When your shield absorbs a hit, it bursts for 80% damage around you.', 'Quand votre bouclier absorbe un coup, il explose à 80 % de dégâts autour de vous.', '护盾吸收攻击时，在周围爆发80%伤害。'),
  ['BLOCKED||EXPLODE:62,0.8|aoe=-1 icd=1'], ic=('shield', 'bomb', 'cyan'))
B('C', U, 'bastion_limpio', ('Bastión de Victoria', 'Victory Bastion', 'Bastion de victoire', '胜利壁垒'),
  ('Al limpiar una sala ganas un escudo de 20.', 'Clearing a room grants a 20-point shield.', 'Nettoyer une salle donne un bouclier de 20.', '清理房间后获得20点护盾。'),
  ['CLEAR||SHIELD:20'], ic=('tower', 'shield', 'stone'))
B('C', R, 'armadura_hierro', ('Armadura de Hierro', 'Iron Armor', 'Armure de fer', '铁甲'),
  ('Tus golpes dan 3 de escudo (cada 1,2 s) y tu escudo puede acumular 30 más.', 'Your hits grant 3 shield (every 1.2 s) and your shield can hold 30 more.', 'Vos coups donnent 3 de bouclier (toutes les 1,2 s) et votre bouclier peut contenir 30 de plus.', '攻击获得3点护盾（每1.2秒），护盾上限+30。'),
  ['HIT||SHIELD:3|icd=1.2', 'MOD||SHIELDCAP:30'], ic=('shield', 'hammer', 'steel'))
B('C', R, 'coraza_espinas', ('Coraza de Espinas', 'Thorn Carapace', 'Carapace d\'épines', '荆棘外壳'),
  ('Al recibir daño estallas dañando (70%) a los enemigos cercanos (cada 1,5 s).', 'When hurt you burst, damaging (70%) nearby enemies (every 1.5 s).', 'Quand vous êtes blessé, vous explosez et infligez 70 % de dégâts aux ennemis proches (toutes les 1,5 s).', '受伤时爆发，对附近敌人造成70%伤害（每1.5秒）。'),
  ['HURT||EXPLODE:60,0.7|aoe=-1 icd=1.5'], ic=('fang', 'shield', 'red'))
B('C', R, 'contragolpe', ('Contragolpe Desesperado', 'Desperate Counter', 'Contre désespéré', '绝地反击'),
  ('Al recibir daño, tu siguiente golpe hace +70% de daño (4 s).', 'When hurt, your next hit deals +70% damage (4 s).', 'Quand vous êtes blessé, votre prochain coup inflige +70 % de dégâts (4 s).', '受伤后，下一次攻击伤害+70%（4秒）。'),
  ['HURT||NEXTHIT:0.7,4'], ic=('fist', 'heart', 'red'))
B('C', U, 'sangre_fria', ('Sangre Fría', 'Cold Blood', 'Sang-froid', '冷血'),
  ('Al caer por debajo del 35% de vida ganas un escudo de 40 (cada 20 s).', 'Dropping below 35% health grants a 40-point shield (every 20 s).', 'Passer sous 35 % de vie donne un bouclier de 40 (toutes les 20 s).', '生命低于35%时获得40点护盾（每20秒）。'),
  ['LOWHP||SHIELD:40|icd=20'], ic=('drop', 'shield', 'ice'))
B('C', R, 'supervivencia', ('Instinto de Supervivencia', 'Survival Instinct', 'Instinct de survie', '求生本能'),
  ('Al caer por debajo del 35% de vida: 0,6 s de invulnerabilidad y cura del 8% (cada 25 s).', 'Dropping below 35% health: 0.6 s of invulnerability and an 8% heal (every 25 s).', 'Passer sous 35 % de vie : 0,6 s d\'invulnérabilité et 8 % de soin (toutes les 25 s).', '生命低于35%时：0.6秒无敌并恢复8%生命（每25秒）。'),
  ['LOWHP||INVULN:0.6|icd=25', 'LOWHP||HEAL:0.08|icd=25'], ic=('heart', 'wing', 'pink'))
B('C', EP, 'ultimo_bastion', ('Último Bastión', 'Last Bastion', 'Dernier bastion', '最后堡垒'),
  ('Con menos del 35% de vida recibes un 30% menos de daño.', 'Below 35% health you take 30% less damage.', 'Sous 35 % de vie, vous subissez 30 % de dégâts en moins.', '生命低于35%时，受到的伤害降低30%。'),
  ['MOD|p:low|TAKEN:-0.30'], ic=('tower', 'heart', 'red'))
B('C', R, 'rabia_herida', ('Rabia Herida', 'Wounded Rage', 'Rage blessée', '负伤之怒'),
  ('Con menos del 35% de vida haces +35% de daño.', 'Below 35% health you deal +35% damage.', 'Sous 35 % de vie, vous infligez +35 % de dégâts.', '生命低于35%时，伤害+35%。'),
  ['MOD|p:low|DMG:0.35'], ic=('skull', 'heart', 'red'))
B('C', R, 'sanguinario', ('Sanguinario', 'Bloodthirsty', 'Sanguinaire', '嗜血者'),
  ('Con menos del 35% de vida robas un 5% del daño que infliges.', 'Below 35% health you steal 5% of the damage you deal.', 'Sous 35 % de vie, vous volez 5 % des dégâts infligés.', '生命低于35%时，吸取你所造成伤害的5%。'),
  ['MOD|p:low|LIFESTEAL:0.05'], ic=('fang', 'drop', 'red'))
a = 10
B('C', U, 'vitalidad', ('Vitalidad', 'Vitality', 'Vitalité', '活力'),
  ('+{a}% de vida máxima por nivel.', '+{a}% max health per level.', '+{a} % de vie max par niveau.', '最大生命+{a}%（每级）。'),
  [f'MOD||MAXHP:{a/100}|scale'], mx=3, ic=('heart', 'cross', 'red'), a=a)
B('C', U, 'sanacion_sala', ('Sanación de Victoria', 'Victory Mending', 'Soin de victoire', '胜利疗愈'),
  ('Al limpiar una sala recuperas el 5% de tu vida máxima.', 'Clearing a room restores 5% of your max health.', 'Nettoyer une salle restaure 5 % de votre vie max.', '清理房间后恢复5%最大生命。'),
  ['CLEAR||HEAL:0.05'], ic=('cross', 'tower', 'green'))
B('C', U, 'cosecha_vida', ('Cosecha de Vida', 'Life Harvest', 'Moisson de vie', '生命收割'),
  ('Cada baja cura el 1,5% de tu vida máxima (límite por sala).', 'Each kill heals 1.5% of your max health (limited per room).', 'Chaque kill soigne 1,5 % de votre vie max (limité par salle).', '每次击杀恢复1.5%最大生命（每个房间有上限）。'),
  ['KILL||HEAL:0.015|icd=0.3'], ic=('skull', 'cross', 'green'))
B('C', L, 'egida_perpetua', ('Égida Perpetua', 'Perpetual Aegis', 'Égide perpétuelle', '永恒神盾'),
  ('En combate ganas un escudo de 30 cada 8 s. Si el escudo absorbe un golpe, 0,5 s de invulnerabilidad (cada 3 s).', 'In combat you gain a 30-point shield every 8 s. When it absorbs a hit: 0.5 s of invulnerability (every 3 s).',
   'En combat, vous gagnez un bouclier de 30 toutes les 8 s. S\'il absorbe un coup : 0,5 s d\'invulnérabilité (toutes les 3 s).', '战斗中每8秒获得30点护盾。护盾吸收攻击时获得0.5秒无敌（每3秒）。'),
  ['TICK|r:combat|SHIELD:30|every=8', 'BLOCKED||INVULN:0.5|icd=3'], stage=2, req=('cat', 'C', 3), ic=('tower', 'sun', 'gold'))
B('C', U, 'onda_choque', ('Onda de Choque', 'Shockwave', 'Onde de choc', '冲击波'),
  ('Al recibir un golpe empujas a los enemigos cercanos (cada 1,2 s).', 'When hit, you push nearby enemies away (every 1.2 s).', 'Quand vous êtes touché, vous repoussez les ennemis proches (toutes les 1,2 s).', '受到攻击时击退附近的敌人（每1.2秒）。'),
  ['HURT||PUSH:80,170|icd=1.2'], ic=('ring', 'hand', 'stone'))
