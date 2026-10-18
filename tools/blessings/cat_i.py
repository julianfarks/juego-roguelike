from bl import *

# ===================== I. MALDICIONES Y TRANSFORMACIONES =====================
B('I', U, 'marca_maldita', ('Marca Maldita', 'Cursed Mark', 'Marque maudite', '诅咒印记'),
  ('15% de maldecir al golpear: los malditos reciben +20% de daño tuyo durante 6 s.', '15% chance to curse on hit: cursed enemies take +20% damage from you for 6 s.', '15 % de maudire en frappant : les maudits subissent +20 % de vos dégâts pendant 6 s.', '攻击时15%几率施加诅咒：被诅咒的敌人受到你的伤害+20%，持续6秒。'),
  ['HIT|!v:curse|STATUS:curse,6,1|ch=0.15'], ic=('skull', 'eye', 'purple'))
B('I', R, 'sentencia_oscura', ('Sentencia Oscura', 'Dark Verdict', 'Verdict sombre', '黑暗判决'),
  ('En combate, cada 9 s maldices al enemigo con más vida.', 'In combat, every 9 s you curse the enemy with the most health.', 'En combat, toutes les 9 s vous maudissez l\'ennemi avec le plus de vie.', '战斗中每9秒诅咒生命最高的敌人。'),
  ['TICK|r:combat|MARKTOP:8 every=9'], ic=('book', 'skull', 'dark'))
B('I', R, 'maldicion_expansiva', ('Maldición Contagiosa', 'Contagious Curse', 'Malédiction contagieuse', '蔓延诅咒'),
  ('Cuando muere un enemigo maldito, la maldición salta a los cercanos.', 'When a cursed enemy dies, the curse jumps to nearby enemies.', 'Quand un ennemi maudit meurt, la malédiction saute aux ennemis proches.', '被诅咒的敌人死亡时，诅咒传给附近的敌人。'),
  ['KILL|v:curse|SPREAD:curse,110'], ic=('skull', 'chain', 'purple'))
B('I', U, 'cosecha_maldita', ('Cosecha Maldita', 'Cursed Harvest', 'Moisson maudite', '诅咒收获'),
  ('Los enemigos malditos sueltan 3 almas al morir (límite por sala).', 'Cursed enemies drop 3 souls on death (limited per room).', 'Les ennemis maudits lâchent 3 âmes à leur mort (limité par salle).', '被诅咒的敌人死亡时掉落3点灵魂（每个房间有上限）。'),
  ['KILL|v:curse|SOULS:3'], ic=('soul', 'skull', 'purple'))
B('I', R, 'festin_oscuro', ('Festín Oscuro', 'Dark Feast', 'Festin sombre', '黑暗盛宴'),
  ('Contra enemigos malditos robas un 4% del daño como vida.', 'Against cursed enemies you steal 4% of damage as health.', 'Contre les ennemis maudits, vous volez 4 % des dégâts en vie.', '对被诅咒的敌人，吸取4%伤害作为生命。'),
  ['MOD|v:curse|LIFESTEAL:0.04'], ic=('fang', 'skull', 'dark'))
B('I', R, 'crit_maldito', ('Crítico Maldito', 'Cursed Critical', 'Critique maudit', '诅咒暴击'),
  ('+20% de probabilidad de crítico contra enemigos malditos.', '+20% critical chance against cursed enemies.', '+20 % de chance de critique contre les ennemis maudits.', '对被诅咒的敌人暴击率+20%。'),
  ['MOD|v:curse|CRIT:0.20'], ic=('star', 'skull', 'purple'))
B('I', L, 'forma_sombra', ('Forma de Sombra', 'Shadow Form', 'Forme d\'ombre', '暗影形态'),
  ('Tu definitiva te transforma 8 s: +30% de daño, +25% de velocidad y -20% de daño recibido; dejas un rastro de sombra y maldices al enemigo más sano.', 'Your ultimate transforms you for 8 s: +30% damage, +25% speed and -20% damage taken; you leave a shadow trail and curse the healthiest enemy.',
   'Votre ultime vous transforme 8 s : +30 % de dégâts, +25 % de vitesse et -20 % de dégâts reçus ; vous laissez une traînée d\'ombre et maudissez l\'ennemi le plus sain.', '终极技能使你变身8秒：伤害+30%，速度+25%，受到伤害-20%；留下暗影轨迹并诅咒最健康的敌人。'),
  ['ULT||BUFF:dmg,0.30,8,1', 'ULT||BUFF:spd,0.25,8,1', 'ULT||BUFF:taken,-0.20,8,1', 'ULT||TRAIL:shadow,3,1.0', 'ULT||MARKTOP:10'], stage=1, req=('cat', 'I', 3), ic=('ghost', 'moon', 'dark'))
B('I', R, 'forma_bestial', ('Forma Bestial', 'Beast Form', 'Forme bestiale', '野兽形态'),
  ('Al caer por debajo del 35% de vida te transformas 6 s: +30% de velocidad de ataque y +20% de velocidad (cada 30 s).', 'Dropping below 35% health transforms you for 6 s: +30% attack speed and +20% speed (every 30 s).', 'Passer sous 35 % de vie vous transforme 6 s : +30 % de vitesse d\'attaque et +20 % de vitesse (toutes les 30 s).', '生命低于35%时变身6秒：攻击速度+30%，移动速度+20%（每30秒）。'),
  ['LOWHP||BUFF:atk,0.30,6,1|icd=30', 'LOWHP||BUFF:spd,0.20,6,1|icd=30'], ic=('fang', 'fist', 'copper'))
B('I', R, 'espectro', ('Forma Espectral', 'Spectral Form', 'Forme spectrale', '幽魂形态'),
  ('Cada parry te vuelve espectral: +25% de velocidad 3 s y maldices al enemigo más sano.', 'Each parry makes you spectral: +25% speed for 3 s and curses the healthiest enemy.', 'Chaque parade vous rend spectral : +25 % de vitesse pendant 3 s et maudit l\'ennemi le plus sain.', '每次格挡使你变为幽魂：移动速度+25%，持续3秒，并诅咒最健康的敌人。'),
  ['PARRY||BUFF:spd,0.25,3,1', 'PARRY||MARKTOP:8'], ic=('ghost', 'shield', 'white'))
B('I', EP, 'vacio_voraz', ('Vacío Voraz', 'Hungry Void', 'Vide vorace', '饥饿虚空'),
  ('Cada baja carga un 3% de tu definitiva y, al terminar la definitiva, te curas el 10%.', 'Each kill charges 3% of your ultimate, and when the ultimate ends you heal 10%.', 'Chaque kill charge 3 % de votre ultime et, à la fin de l\'ultime, vous soignez 10 %.', '每次击杀为终极技能充能3%，终极技能结束时恢复10%生命。'),
  ['KILL||ULT:3', 'ULTEND||HEAL:0.10'], stage=1, ic=('moon', 'skull', 'dark'))
B('I', U, 'corrupcion', ('Corrupción', 'Corruption', 'Corruption', '腐化'),
  ('30% de envenenar al golpear a un enemigo maldito.', '30% chance to poison when hitting a cursed enemy.', '30 % d\'empoisonner en frappant un ennemi maudit.', '攻击被诅咒的敌人时，30%几率使其中毒。'),
  ['HIT|v:curse|STATUS:poison,3,1|ch=0.3'], ic=('drop', 'skull', 'purple'))
B('I', U, 'aura_penumbra', ('Aura de Penumbra', 'Penumbra Aura', 'Aura de pénombre', '幽影光环'),
  ('Al rodar dejas dos charcos de sombra que maldicen a los enemigos que los pisan.', 'Rolling leaves two shadow patches that curse enemies who step on them.', 'En roulant, vous laissez deux flaques d\'ombre qui maudissent les ennemis qui marchent dessus.', '翻滚时留下两处暗影，诅咒踩上去的敌人。'),
  ['ROLL||TRAIL:shadow,3,1.0', 'ROLLEND||TRAIL:shadow,3,1.0'], ic=('moon', 'boot', 'purple'))
