from bl import *

# ===================== D. VELOCIDAD, MOVILIDAD Y EVASION =====================
a = 25
B('D', U, 'impulso_rodar', ('Impulso de Rodada', 'Roll Momentum', 'Élan de roulade', '翻滚动力'),
  ('Tu rodada es un {a}% más rápida por nivel: recorre más distancia y termina antes.', 'Your roll is {a}% faster per level: it covers more distance and ends sooner.', 'Votre roulade est {a} % plus rapide par niveau : elle couvre plus de distance et finit plus tôt.', '翻滚速度提升{a}%（每级）：移动距离更远，结束更快。'),
  [f'MOD||ROLLCDR:{a/100}|scale'], mx=2, ic=('boot', 'wing', 'white'), a=a)
B('D', U, 'sombra_veloz', ('Sombra Veloz', 'Swift Shadow', 'Ombre véloce', '迅捷之影'),
  ('Tras rodar ganas +20% de velocidad de movimiento durante 2,5 s.', 'After rolling you gain +20% movement speed for 2.5 s.', 'Après une roulade, +20 % de vitesse de déplacement pendant 2,5 s.', '翻滚后移动速度+20%，持续2.5秒。'),
  ['ROLLEND||BUFF:spd,0.2,2.5,1'], ic=('boot', 'ghost', 'dark'))
B('D', U, 'racha_cazador', ('Racha del Cazador', 'Hunter\'s Streak', 'Série du chasseur', '猎手连杀'),
  ('Cada baja da +10% de velocidad de movimiento durante 4 s (hasta 3 cargas).', 'Each kill gives +10% movement speed for 4 s (up to 3 stacks).', 'Chaque kill donne +10 % de vitesse de déplacement pendant 4 s (jusqu\'à 3 cumuls).', '每次击杀移动速度+10%，持续4秒（最多3层）。'),
  ['KILL||BUFF:spd,0.10,4,3'], ic=('boot', 'skull', 'red'))
B('D', R, 'esquiva_sagrada', ('Esquiva Sagrada', 'Sacred Dodge', 'Esquive sacrée', '神圣闪避'),
  ('Cada esquiva da +15% de daño durante 4 s (hasta 2 cargas).', 'Each dodge gives +15% damage for 4 s (up to 2 stacks).', 'Chaque esquive donne +15 % de dégâts pendant 4 s (jusqu\'à 2 cumuls).', '每次闪避伤害+15%，持续4秒（最多2层）。'),
  ['DODGE||BUFF:dmg,0.15,4,2'], ic=('wing', 'star', 'white'))
B('D', R, 'danza_cuchillas', ('Baile de Cuchillas', 'Dagger Waltz', 'Valse des lames', '飞刀圆舞'),
  ('Cada esquiva lanza 3 cuchillas (60% de daño).', 'Each dodge throws 3 blades (60% damage).', 'Chaque esquive lance 3 lames (60 % de dégâts).', '每次闪避投出3把飞刀（60%伤害）。'),
  ['DODGE||PROJ:blade,3,0.6|icd=0.6'], ic=('dagger', 'wing', 'steel'))
B('D', R, 'evasion_magica', ('Evasión Mágica', 'Magic Evasion', 'Évasion magique', '魔法闪避'),
  ('Cada esquiva reduce 0,6 s tus habilidades y carga un 5% de tu definitiva.', 'Each dodge shortens your skill cooldowns by 0.6 s and charges 5% of your ultimate.', 'Chaque esquive réduit vos recharges de 0,6 s et charge 5 % de votre ultime.', '每次闪避使技能冷却缩短0.6秒，并为终极技能充能5%。'),
  ['DODGE||CDR:0.6', 'DODGE||ULT:5'], ic=('wing', 'book', 'purple'))
B('D', U, 'salto_explosivo', ('Salto Explosivo', 'Blast Jump', 'Saut explosif', '爆裂跳跃'),
  ('Cada salto en el aire detona una explosión del 50% de daño bajo ti.', 'Each mid-air jump detonates a 50% damage explosion beneath you.', 'Chaque saut en l\'air déclenche une explosion à 50 % de dégâts sous vous.', '每次空中跳跃在脚下引发50%伤害的爆炸。'),
  ['AIRJUMP||EXPLODE:54,0.5|aoe=-1 icd=0.6'], ic=('boot', 'bomb', 'orange'))
B('D', U, 'aterrizaje_sismico', ('Aterrizaje Sísmico', 'Seismic Landing', 'Atterrissage sismique', '震地降落'),
  ('Las caídas largas provocan una onda del 100% de daño al aterrizar.', 'Long falls cause a 100% damage shockwave on landing.', 'Les longues chutes provoquent une onde à 100 % de dégâts à l\'atterrissage.', '长距离坠落着地时引发100%伤害的冲击波。'),
  ['LAND||EXPLODE:76,1.0|aoe=-1 icd=0.8'], ic=('boot', 'hammer', 'stone'))
B('D', R, 'cadencia', ('Cadencia en Movimiento', 'Moving Cadence', 'Cadence en mouvement', '移动节奏'),
  ('Mientras te mueves, +18% de velocidad de ataque.', 'While moving, +18% attack speed.', 'En mouvement, +18 % de vitesse d\'attaque.', '移动时攻击速度+18%。'),
  ['MOD|p:moving|ATKSPD:0.18'], ic=('wing', 'sword', 'cyan'))
B('D', U, 'golpe_corriendo', ('Golpe en Carrera', 'Running Strike', 'Frappe en course', '冲刺打击'),
  ('Mientras te mueves, +12% de daño.', 'While moving, +12% damage.', 'En mouvement, +12 % de dégâts.', '移动时伤害+12%。'),
  ['MOD|p:moving|DMG:0.12'], ic=('boot', 'sword', 'orange'))
B('D', U, 'quieto_letal', ('Quietud Letal', 'Deadly Stillness', 'Immobilité mortelle', '静止杀机'),
  ('Quieto, haces +20% de daño y recibes un 10% menos.', 'Standing still, you deal +20% damage and take 10% less.', 'Immobile, vous infligez +20 % de dégâts et en subissez 10 % de moins.', '站立不动时，伤害+20%，受到的伤害降低10%。'),
  ['MOD|p:still|DMG:0.20', 'MOD|p:still|TAKEN:-0.10'], ic=('eye', 'stone', 'teal'))
B('D', U, 'rafaga_remate', ('Ráfaga de Remate', 'Finisher Rush', 'Rafale de finisseur', '终结疾风'),
  ('Cada remate de combo da +15% de velocidad de movimiento durante 3 s.', 'Each combo finisher gives +15% movement speed for 3 s.', 'Chaque finisseur de combo donne +15 % de vitesse de déplacement pendant 3 s.', '每次连击终结移动速度+15%，持续3秒。'),
  ['FINISH||BUFF:spd,0.15,3,1'], ic=('fist', 'boot', 'yel'))
B('D', R, 'viento_cola', ('Viento de Cola', 'Tailwind', 'Vent arrière', '顺风'),
  ('Cada salto en el aire da +20% de velocidad de movimiento durante 3 s.', 'Each mid-air jump gives +20% movement speed for 3 s.', 'Chaque saut en l\'air donne +20 % de vitesse de déplacement pendant 3 s.', '每次空中跳跃移动速度+20%，持续3秒。'),
  ['AIRJUMP||BUFF:spd,0.2,3,1'], ic=('wing', 'feather', 'cyan'))
B('D', R, 'segundo_aliento', ('Segundo Aliento', 'Second Wind', 'Second souffle', '回气'),
  ('Cada esquiva te da 0,4 s de invulnerabilidad (cada 3 s).', 'Each dodge gives you 0.4 s of invulnerability (every 3 s).', 'Chaque esquive vous donne 0,4 s d\'invulnérabilité (toutes les 3 s).', '每次闪避获得0.4秒无敌（每3秒）。'),
  ['DODGE||INVULN:0.4|icd=3'], ic=('wing', 'heart', 'white'))
B('D', L, 'reloj_destino', ('Reloj del Destino', 'Clock of Fate', 'Horloge du destin', '命运之钟'),
  ('Un parry o una esquiva ralentiza el tiempo 1,2 s para los enemigos (cada 18 s).', 'A parry or dodge slows time for enemies for 1.2 s (every 18 s).', 'Une parade ou une esquive ralentit le temps des ennemis pendant 1,2 s (toutes les 18 s).', '格挡或闪避使敌人时间减慢1.2秒（每18秒）。'),
  ['DODGE||TIMESLOW:1.2,0.45|icd=18', 'PARRY||TIMESLOW:1.2,0.45|icd=18'], stage=1, req=('cat', 'D', 3), ic=('hourglass', 'sun', 'cyan'))
B('D', R, 'maestro_trampas', ('Maestro de Trampas', 'Trap Master', 'Maître des pièges', '陷阱大师'),
  ('Sobrevolar pinchos sin tocarlos te da 15 de escudo y +20% de daño durante 5 s.', 'Passing over spikes without touching them gives 15 shield and +20% damage for 5 s.', 'Survoler des pointes sans les toucher donne 15 de bouclier et +20 % de dégâts pendant 5 s.', '越过尖刺而不受伤：获得15点护盾，伤害+20%，持续5秒。'),
  ['HAZARD||SHIELD:15', 'HAZARD||BUFF:dmg,0.2,5,1'], ic=('fang', 'boot', 'copper'))
B('D', U, 'acrobata', ('Acróbata', 'Acrobat', 'Acrobate', '杂技师'),
  ('Cada salto da +10% de velocidad de ataque durante 2 s.', 'Each jump gives +10% attack speed for 2 s.', 'Chaque saut donne +10 % de vitesse d\'attaque pendant 2 s.', '每次跳跃攻击速度+10%，持续2秒。'),
  ['JUMP||BUFF:atk,0.10,2,1'], ic=('boot', 'ring', 'pink'))
B('D', R, 'danza_aerea', ('Danza Aérea', 'Aerial Dance', 'Danse aérienne', '空中之舞'),
  ('En el aire haces +20% de daño.', 'While airborne you deal +20% damage.', 'En l\'air, vous infligez +20 % de dégâts.', '在空中时伤害+20%。'),
  ['MOD|p:air|DMG:0.20'], ic=('feather', 'sword', 'white'))
