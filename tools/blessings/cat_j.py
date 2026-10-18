from bl import *

# ===================== J. HIBRIDAS =====================
B('J', R, 'fuego_rayo', ('Fuego y Rayo', 'Fire and Lightning', 'Feu et foudre', '火与雷'),
  ('Los críticos contra enemigos en llamas sueltan un rayo de 2 saltos (cada 0,5 s).', 'Critical hits against burning enemies release a 2-jump lightning bolt (every 0.5 s).', 'Les critiques contre les ennemis en flammes libèrent un éclair à 2 sauts (toutes les 0,5 s).', '对燃烧的敌人暴击时释放2次跳跃的闪电（每0.5秒）。'),
  ['CRIT|v:burn|CHAIN:2,0.45|icd=0.5'], ic=('flame', 'bolt', 'orange'))
B('J', R, 'explosion_hielo', ('Estallido Helado', 'Frost Burst', 'Éclat glacé', '冰霜爆裂'),
  ('Golpear a un enemigo congelado: 20% de causar un estallido (70% de daño, cada 1 s).', 'Hitting a frozen enemy: 20% chance to cause a burst (70% damage, every 1 s).', 'Frapper un ennemi gelé : 20 % de provoquer un éclat (70 % de dégâts, toutes les 1 s).', '攻击冰冻的敌人：20%几率引发爆裂（70%伤害，每1秒）。'),
  ['HIT|v:freeze|EXPLODE:56,0.7,slow,2|ch=0.2 icd=1'], ic=('snow', 'bomb', 'cyan'))
B('J', EP, 'choque_termico', ('Choque Térmico', 'Thermal Shock', 'Choc thermique', '热冲击'),
  ('Golpear a un enemigo en llamas y ralentizado a la vez provoca una explosión de vapor (120% de daño, cada 2 s).', 'Hitting an enemy that is burning and slowed at once causes a steam explosion (120% damage, every 2 s).', 'Frapper un ennemi à la fois en flammes et ralenti provoque une explosion de vapeur (120 % de dégâts, toutes les 2 s).', '攻击同时燃烧和减速的敌人，引发蒸汽爆炸（120%伤害，每2秒）。'),
  ['HIT|v:burn,v:slow|EXPLODE:70,1.2|icd=2'], stage=1, ic=('flame', 'snow', 'white'))
B('J', U, 'electro_veneno', ('Conducción Tóxica', 'Toxic Conduction', 'Conduction toxique', '毒导'),
  ('Golpear a un enemigo envenenado y electrizado provoca una explosión tóxica (80% de daño, cada 1,5 s).', 'Hitting an enemy that is poisoned and shocked causes a toxic explosion (80% damage, every 1.5 s).', 'Frapper un ennemi empoisonné et électrisé provoque une explosion toxique (80 % de dégâts, toutes les 1,5 s).', '攻击同时中毒和感电的敌人，引发毒爆（80%伤害，每1.5秒）。'),
  ['HIT|v:shock,v:poison|EXPLODE:50,0.8,poison,3|icd=1.5'], ic=('bolt', 'drop', 'green'))
B('J', R, 'sangre_hirviente', ('Sangre Hirviente', 'Boiling Blood', 'Sang bouillant', '沸血'),
  ('Los enemigos que sangran y arden a la vez reciben +30% de daño.', 'Enemies that are bleeding and burning at once take +30% damage.', 'Les ennemis qui saignent et brûlent à la fois subissent +30 % de dégâts.', '同时流血和燃烧的敌人受到的伤害+30%。'),
  ['MOD|v:bleed,v:burn|DMG:0.30'], ic=('drop', 'flame', 'red'))
B('J', R, 'parry_fuego', ('Parry Ardiente', 'Blazing Parry', 'Parade ardente', '烈焰格挡'),
  ('Cada parry prende fuego a los enemigos cercanos durante 3 s.', 'Each parry sets nearby enemies on fire for 3 s.', 'Chaque parade enflamme les ennemis proches pendant 3 s.', '每次格挡点燃附近的敌人，持续3秒。'),
  ['PARRY||STATUS:burn,3,1.5|aoe=100'], ic=('shield', 'flame', 'fire'))
B('J', R, 'parry_hielo', ('Parry Glacial', 'Glacial Parry', 'Parade glaciale', '寒冰格挡'),
  ('Cada parry congela 1,2 s a los enemigos cercanos (los jefes solo se ralentizan).', 'Each parry freezes nearby enemies for 1.2 s (bosses are only slowed).', 'Chaque parade gèle les ennemis proches pendant 1,2 s (les boss sont seulement ralentis).', '每次格挡冻结附近的敌人1.2秒（首领仅被减速）。'),
  ['PARRY||STATUS:freeze,1.2,1|aoe=90 icd=2'], ic=('shield', 'snow', 'ice'))
B('J', U, 'skill_critico', ('Hechizo Certero', 'Precise Spell', 'Sort précis', '精准法术'),
  ('Tras lanzar una habilidad, +25% de probabilidad de crítico durante 5 s.', 'After casting a skill, +25% critical chance for 5 s.', 'Après avoir lancé une compétence, +25 % de chance de critique pendant 5 s.', '施放技能后，暴击率+25%，持续5秒。'),
  ['SKILL||BUFF:crit,0.25,5,1'], ic=('book', 'eye', 'yel'))
B('J', U, 'veneno_critico', ('Toxina Crítica', 'Critical Toxin', 'Toxine critique', '暴击毒素'),
  ('+18% de probabilidad de crítico contra enemigos envenenados.', '+18% critical chance against poisoned enemies.', '+18 % de chance de critique contre les ennemis empoisonnés.', '对中毒的敌人暴击率+18%。'),
  ['MOD|v:poison|CRIT:0.18'], ic=('drop', 'star', 'green'))
B('J', U, 'frasco_explosivo', ('Frasco Explosivo', 'Explosive Flask', 'Fiole explosive', '爆裂药瓶'),
  ('Beber un frasco provoca una explosión a tu alrededor (150% de daño).', 'Drinking a flask causes an explosion around you (150% damage).', 'Boire une fiole provoque une explosion autour de vous (150 % de dégâts).', '饮用药瓶时在周围引发爆炸（150%伤害）。'),
  ['POTION||EXPLODE:90,1.5|aoe=-1'], ic=('potion', 'bomb', 'orange'))
B('J', R, 'triple_filo', ('Triple Filo', 'Triple Edge', 'Triple tranchant', '三重锋刃'),
  ('Cada 7 golpes lanzas 3 cuchillas (50% de daño).', 'Every 7 hits you throw 3 blades (50% damage).', 'Tous les 7 coups, vous lancez 3 lames (50 % de dégâts).', '每攻击7次投出3把飞刀（50%伤害）。'),
  ['STREAK||PROJ:blade,3,0.5|n=7'], ic=('dagger', 'sword', 'steel'))
B('J', U, 'corazon_ardiente', ('Corazón Ardiente', 'Burning Heart', 'Cœur ardent', '炽热之心'),
  ('Los enemigos en llamas pueden soltar un corazón al morir (cada 25 s).', 'Burning enemies may drop a heart on death (every 25 s).', 'Les ennemis en flammes peuvent lâcher un cœur à leur mort (toutes les 25 s).', '燃烧的敌人死亡时可能掉落一颗心（每25秒）。'),
  ['KILL|v:burn|HEARTDROP|icd=25'], ic=('heart', 'flame', 'fire'))
B('J', L, 'convergencia', ('Convergencia Elemental', 'Elemental Convergence', 'Convergence élémentaire', '元素汇聚'),
  ('En combate, cada 8 s un anillo de fuego y uno de hielo salen de ti y caen 2 rayos.', 'In combat, every 8 s a ring of fire and a ring of ice burst from you and 2 lightning bolts strike.', 'En combat, toutes les 8 s un anneau de feu et un de glace jaillissent de vous et 2 éclairs frappent.', '战斗中每8秒，火焰环和寒冰环从你身上迸发，并落下2道闪电。'),
  ['TICK|r:combat|PROJ:ring,8,0.6,burn every=8', 'TICK|r:combat|PROJ:ring,8,0.6,slow every=8', 'TICK|r:combat|STRIKE:2,1.0 every=8'], stage=1,
  req=('has', 3, ['BRASAS', 'GLACIAL', 'CHISPA', 'llama_voraz', 'escarcha_quebradiza', 'carga_estatica', 'fuego_rayo', 'choque_termico']), ic=('orb', 'sun', 'white'))
