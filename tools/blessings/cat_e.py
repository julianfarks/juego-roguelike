from bl import *

# ===================== E. PROYECTILES =====================
B('E', C, 'punta_afilada', ('Punta Afilada', 'Sharp Tip', 'Pointe affûtée', '锋利箭头'),
  ('Tus proyectiles atraviesan 1 enemigo más por nivel.', 'Your projectiles pierce 1 more enemy per level.', 'Vos projectiles transpercent 1 ennemi de plus par niveau.', '你的投射物多穿透1个敌人（每级）。'),
  ['MOD||PIERCE:1|scale'], mx=2, ic=('arrow', 'dagger', 'steel'))
B('E', C, 'vuelo_veloz', ('Vuelo Veloz', 'Swift Flight', 'Vol rapide', '迅疾飞行'),
  ('Tus proyectiles van un 25% más rápido y son un 20% más grandes.', 'Your projectiles fly 25% faster and are 20% bigger.', 'Vos projectiles vont 25 % plus vite et sont 20 % plus gros.', '你的投射物速度+25%，体积+20%。'),
  ['MOD||PROJSPEED:0.25', 'MOD||PROJSIZE:0.20'], ic=('arrow', 'wing', 'white'))
B('E', U, 'ricochet', ('Ricochet', 'Ricochet', 'Ricochet', '弹射'),
  ('Tus proyectiles rebotan una vez contra paredes o enemigos.', 'Your projectiles bounce once off walls or enemies.', 'Vos projectiles rebondissent une fois sur les murs ou les ennemis.', '你的投射物在墙壁或敌人上弹射一次。'),
  ['MOD||BOUNCE:1'], stage=1, ic=('arrow', 'spiral', 'orange'))
B('E', U, 'buscador', ('Buscador', 'Seeker', 'Chercheur', '追踪者'),
  ('Tus proyectiles giran ligeramente hacia los enemigos cercanos.', 'Your projectiles curve slightly toward nearby enemies.', 'Vos projectiles s\'orientent légèrement vers les ennemis proches.', '你的投射物会略微转向附近的敌人。'),
  ['MOD||HOMING:1'], ic=('eye', 'arrow', 'cyan'))
B('E', R, 'perforante', ('Perforante', 'Armor Piercer', 'Perforant', '穿甲'),
  ('Tus proyectiles hacen +20% de daño por cada enemigo que atraviesan.', 'Your projectiles deal +20% damage for each enemy they pass through.', 'Vos projectiles infligent +20 % de dégâts pour chaque ennemi traversé.', '你的投射物每穿透一个敌人，伤害+20%。'),
  ['MOD||PIERCEDMG:0.20', 'MOD||PIERCE:1'], ic=('arrow', 'fang', 'red'))
B('E', R, 'doble_lanzamiento', ('Doble Lanzamiento', 'Double Throw', 'Double lancer', '双重投掷'),
  ('20% de que tus proyectiles se lancen dos veces.', '20% chance for your projectiles to be launched twice.', '20 % de chance que vos projectiles soient lancés deux fois.', '20%几率使你的投射物发射两次。'),
  ['MOD||PROJDOUBLE:0.2'], stage=1, ic=('arrow', 'arrow', 'gold'))
B('E', R, 'onda_expansiva', ('Onda Expansiva', 'Expanding Wave', 'Onde expansive', '扩散波'),
  ('Tus ondas de energía (Hoja Fantasma y similares) hacen +40% de daño y son más grandes.', 'Your energy waves (Phantom Blade and similar) deal +40% damage and are larger.', 'Vos ondes d\'énergie (Lame fantôme et similaires) infligent +40 % de dégâts et sont plus grandes.', '你的能量波（幽灵之刃等）伤害+40%，范围更大。'),
  ['MOD||WAVEDMG:0.4'], ic=('ring', 'sword', 'white'))
B('E', R, 'proyectil_explosivo', ('Proyectil Explosivo', 'Explosive Shot', 'Projectile explosif', '爆裂弹'),
  ('Tus proyectiles explotan al terminar su trayecto (50% de daño).', 'Your projectiles explode at the end of their path (50% damage).', 'Vos projectiles explosent à la fin de leur trajet (50 % de dégâts).', '你的投射物在飞行终点爆炸（50%伤害）。'),
  ['PROJEND||EXPLODE:46,0.5|icd=0.15'], stage=1, ic=('arrow', 'bomb', 'fire'))
B('E', U, 'disparo_incendiario', ('Disparo Incendiario', 'Incendiary Shot', 'Tir incendiaire', '燃烧弹'),
  ('30% de que tus proyectiles prendan fuego al impactar.', '30% chance for your projectiles to ignite on hit.', '30 % de chance que vos projectiles enflamment à l\'impact.', '30%几率使你的投射物命中时点燃目标。'),
  ['PROJ||STATUS:burn,3,1|ch=0.3'], ic=('arrow', 'flame', 'fire'))
B('E', U, 'disparo_gelido', ('Disparo Gélido', 'Frost Shot', 'Tir glacial', '寒冰弹'),
  ('50% de que tus proyectiles ralenticen al impactar.', '50% chance for your projectiles to slow on hit.', '50 % de chance que vos projectiles ralentissent à l\'impact.', '50%几率使你的投射物命中时减速目标。'),
  ['PROJ||STATUS:slow,2.5,1|ch=0.5'], ic=('arrow', 'snow', 'ice'))
B('E', U, 'disparo_voltaico', ('Disparo Voltaico', 'Voltaic Shot', 'Tir voltaïque', '雷电弹'),
  ('Tus proyectiles descargan un rayo de 2 saltos al impactar (cada 0,5 s).', 'Your projectiles discharge a 2-jump lightning on hit (every 0.5 s).', 'Vos projectiles libèrent un éclair à 2 sauts à l\'impact (toutes les 0,5 s).', '你的投射物命中时释放2次跳跃的闪电（每0.5秒）。'),
  ['PROJ||CHAIN:2,0.4|icd=0.5'], ic=('arrow', 'bolt', 'yel'))
B('E', R, 'lluvia_hojas', ('Lluvia de Hojas', 'Leaf Rain', 'Pluie de feuilles', '落叶雨'),
  ('Cada habilidad invoca una lluvia de 5 hojas cortantes sobre los enemigos.', 'Each skill summons a rain of 5 cutting leaves on enemies.', 'Chaque compétence invoque une pluie de 5 feuilles tranchantes sur les ennemis.', '每次施放技能，在敌人头上降下5片锋利的叶子。'),
  ['SKILL||PROJ:rain,5,0.5'], ic=('leaf', 'arrow', 'green'))
B('E', R, 'rafaga_estelar', ('Ráfaga Estelar', 'Star Burst', 'Rafale stellaire', '星芒连发'),
  ('Cada 5 golpes sueltas 3 estrellas teledirigidas (50% de daño).', 'Every 5 hits you release 3 homing stars (50% damage).', 'Tous les 5 coups, vous libérez 3 étoiles à tête chercheuse (50 % de dégâts).', '每攻击5次释放3颗追踪星星（50%伤害）。'),
  ['STREAK||PROJ:star,3,0.5|n=5'], ic=('star', 'arrow', 'yel'))
B('E', R, 'estela_mortal', ('Estela de Rodada', 'Roll Wake', 'Sillage de roulade', '翻滚余波'),
  ('Al terminar un rodar lanzas una onda de energía (80% de daño).', 'Finishing a roll fires an energy wave (80% damage).', 'Terminer une roulade lance une onde d\'énergie (80 % de dégâts).', '翻滚结束时发射能量波（80%伤害）。'),
  ['ROLLEND||PROJ:wave,1,0.8'], ic=('ring', 'boot', 'cyan'))
B('E', U, 'francotirador', ('Tirador Experto', 'Marksman', 'Tireur expert', '神射手'),
  ('Los proyectiles que impactan a enemigos lejanos hacen +40% de daño.', 'Projectiles that hit distant enemies deal +40% damage.', 'Les projectiles touchant des ennemis éloignés infligent +40 % de dégâts.', '命中远处敌人的投射物伤害+40%。'),
  ['MOD|v:far|PROJDMG:0.4'], ic=('eye', 'arrow', 'teal'))
B('E', EP, 'foco_letal', ('Foco Letal', 'Lethal Focus', 'Concentration létale', '致命专注'),
  ('Impactos seguidos con proyectiles al mismo enemigo: +8% de daño acumulable (hasta 5).', 'Consecutive projectile hits on the same enemy: +8% damage, stacking (up to 5).', 'Impacts successifs de projectiles sur le même ennemi : +8 % de dégâts cumulables (jusqu\'à 5).', '投射物连续命中同一敌人：伤害+8%可叠加（最多5层）。'),
  ['MOD||FOCUS:0.08'], stage=1, ic=('eye', 'star', 'red'))
B('E', R, 'orbe_santo', ('Orbe Santo', 'Holy Orb', 'Orbe sacré', '圣光球'),
  ('Matar con un proyectil libera un orbe sagrado teledirigido (70% de daño).', 'Killing with a projectile releases a homing holy orb (70% damage).', 'Tuer avec un projectile libère un orbe sacré à tête chercheuse (70 % de dégâts).', '用投射物击杀敌人会释放追踪圣光球（70%伤害）。'),
  ['KILL|s:P|PROJ:holy,1,0.7|icd=0.3'], ic=('orb', 'cross', 'white'))
B('E', L, 'tormenta_acero', ('Tormenta de Acero', 'Steel Storm', 'Tempête d\'acier', '钢铁风暴'),
  ('Cada habilidad lanza 10 cuchillas desde el cielo y tu definitiva 16. Tus proyectiles atraviesan 1 enemigo más.', 'Each skill rains 10 blades from the sky and your ultimate 16. Your projectiles pierce 1 more enemy.',
   'Chaque compétence fait pleuvoir 10 lames du ciel et votre ultime 16. Vos projectiles transpercent 1 ennemi de plus.', '每次技能从天而降10把刀刃，终极技能16把。你的投射物多穿透1个敌人。'),
  ['SKILL||PROJ:rain,10,0.45', 'ULT||PROJ:rain,16,0.6', 'MOD||PIERCE:1'], stage=1, req=('cat', 'E', 3), ic=('dagger', 'sun', 'steel'))
