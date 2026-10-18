from bl import *

# ===================== H. RIESGO Y RECOMPENSA =====================
B('H', U, 'desafio_doble', ('Desafío Doble', 'Double Challenge', 'Double défi', '双倍挑战'),
  ('Los enemigos tienen +15% de vida, pero ganas +35% de oro y +20% de almas.', 'Enemies have +15% health, but you earn +35% gold and +20% souls.', 'Les ennemis ont +15 % de vie, mais vous gagnez +35 % d\'or et +20 % d\'âmes.', '敌人生命+15%，但你获得的金币+35%，灵魂+20%。'),
  ['MOD||ENEMYHP:0.15', 'MOD||GOLDMUL:0.35', 'MOD||SOULMUL:0.20'], ic=('skull', 'coin', 'red'))
B('H', R, 'sed_riesgo', ('Sed de Riesgo', 'Thirst for Risk', 'Soif de risque', '冒险渴望'),
  ('Los enemigos te hacen +20% de daño, pero haces +25% de daño y +30% de daño crítico.', 'Enemies deal +20% damage to you, but you deal +25% damage and +30% critical damage.', 'Les ennemis vous infligent +20 % de dégâts, mais vous infligez +25 % de dégâts et +30 % de dégâts critiques.', '敌人对你的伤害+20%，但你的伤害+25%，暴击伤害+30%。'),
  ['MOD||ENEMYDMG:0.20', 'MOD||DMG:0.25', 'MOD||CRITMUL:0.3'], ic=('fang', 'sword', 'lava'))
B('H', U, 'vidrio_filo', ('Cañón de Cristal', 'Glass Cannon', 'Canon de verre', '玻璃大炮'),
  ('-25% de vida máxima, +25% de daño.', '-25% max health, +25% damage.', '-25 % de vie max, +25 % de dégâts.', '最大生命-25%，伤害+25%。'),
  ['MOD||MAXHP:-0.25', 'MOD||DMG:0.25'], ic=('heart', 'sword', 'white'))
B('H', R, 'pacto_sangre', ('Pacto de Sangre', 'Blood Pact', 'Pacte de sang', '血之契约'),
  ('Al entrar en cada sala pierdes el 8% de tu vida (nunca mueres por esto), pero haces +30% de daño.', 'Entering each room costs 8% of your health (this never kills you), but you deal +30% damage.', 'Entrer dans chaque salle coûte 8 % de votre vie (cela ne vous tue jamais), mais vous infligez +30 % de dégâts.', '进入每个房间会损失8%生命（不会致死），但伤害+30%。'),
  ['ROOM||LOSEHP:0.08', 'ROOM||BUFF:dmg,0.30,900,1'], stage=1, ic=('drop', 'sword', 'red'))
B('H', EP, 'todo_o_nada', ('Todo o Nada', 'All or Nothing', 'Tout ou rien', '孤注一掷'),
  ('Las salas perfectas (sin daño) dan 25 de oro y curan el 12%. Cada golpe recibido te cuesta 5 de oro.', 'Perfect rooms (no damage) give 25 gold and heal 12%. Each hit you take costs 5 gold.', 'Les salles parfaites (sans dégâts) donnent 25 d\'or et soignent 12 %. Chaque coup reçu coûte 5 d\'or.', '完美房间（未受伤）获得25金币并恢复12%生命。每次受伤损失5金币。'),
  ['PERFECT||GOLD:25', 'PERFECT||HEAL:0.12', 'HURT||LOSEGOLD:5|icd=2'], stage=1, ic=('crown', 'skull', 'gold'))
B('H', R, 'temerario', ('Temerario', 'Reckless', 'Téméraire', '无畏者'),
  ('Mientras no te hayan herido en la sala, haces +20% de daño.', 'As long as you haven\'t been hurt in the room, you deal +20% damage.', 'Tant que vous n\'avez pas été blessé dans la salle, vous infligez +20 % de dégâts.', '在房间中未受伤时，伤害+20%。'),
  ['MOD|p:noroomhit|DMG:0.20'], ic=('eye', 'fist', 'orange'))
B('H', U, 'sacrificio', ('Sacrificio', 'Sacrifice', 'Sacrifice', '牺牲'),
  ('Beber un frasco te cuesta el 5% de tu vida, pero carga un 25% de tu definitiva.', 'Drinking a flask costs 5% of your health but charges 25% of your ultimate.', 'Boire une fiole coûte 5 % de votre vie mais charge 25 % de votre ultime.', '饮用药瓶损失5%生命，但为终极技能充能25%。'),
  ['POTION||LOSEHP:0.05', 'POTION||ULT:25'], ic=('potion', 'skull', 'purple'))
B('H', U, 'apostador', ('Apostador', 'Gambler', 'Parieur', '赌徒'),
  ('Entrar en una sala cuesta 10 de oro; limpiarla sin que te hieran da 40 de oro.', 'Entering a room costs 10 gold; clearing it without being hurt gives 40 gold.', 'Entrer dans une salle coûte 10 d\'or ; la nettoyer sans être blessé donne 40 d\'or.', '进入房间花费10金币；不受伤地清理房间获得40金币。'),
  ['ROOM|p:gold>=10|LOSEGOLD:10', 'PERFECT||GOLD:40'], ic=('coin', 'clover', 'green'))
B('H', L, 'juicio', ('Juicio Final', 'Final Judgment', 'Jugement dernier', '最终审判'),
  ('+35% de daño, pero los enemigos tienen +20% de vida y hacen +30% de daño. Derrotar a un jefe te cura el 35%.', '+35% damage, but enemies have +20% health and deal +30% damage. Defeating a boss heals 35%.',
   '+35 % de dégâts, mais les ennemis ont +20 % de vie et infligent +30 % de dégâts. Vaincre un boss soigne 35 %.', '伤害+35%，但敌人生命+20%，伤害+30%。击败首领后恢复35%生命。'),
  ['MOD||DMG:0.35', 'MOD||ENEMYHP:0.20', 'MOD||ENEMYDMG:0.30', 'BOSSDEAD||HEAL:0.35'], stage=2, req=('cat', 'H', 2), ic=('crown', 'skull', 'lava'))
B('H', U, 'ultimo_recurso', ('Último Recurso', 'Last Resort', 'Dernier recours', '最后手段'),
  ('Beber un frasco con poca vida te da 0,6 s de invulnerabilidad.', 'Drinking a flask at low health gives you 0.6 s of invulnerability.', 'Boire une fiole à faible vie vous donne 0,6 s d\'invulnérabilité.', '生命值低时饮用药瓶，获得0.6秒无敌。'),
  ['POTION|p:low|INVULN:0.6'], ic=('potion', 'wing', 'white'))
B('H', R, 'caza_mayor', ('Caza Mayor', 'Big Game', 'Gros gibier', '猎杀巨兽'),
  ('Los enemigos tienen +20% de vida. Los mini-jefes y jefes sueltan un corazón y 8 almas al morir.', 'Enemies have +20% health. Mini-bosses and bosses drop a heart and 8 souls on death.', 'Les ennemis ont +20 % de vie. Les mini-boss et boss lâchent un cœur et 8 âmes à leur mort.', '敌人生命+20%。精英和首领死亡时掉落一颗心和8点灵魂。'),
  ['MOD||ENEMYHP:0.20', 'KILL|v:elite|HEARTDROP|icd=1', 'KILL|v:elite|SOULS:8'], ic=('skull', 'heart', 'bone'))
B('H', U, 'ayuno', ('Ayuno', 'Fasting', 'Jeûne', '禁食'),
  ('-1 frasco máximo, pero haces +20% de daño.', '-1 maximum flask, but you deal +20% damage.', '-1 fiole maximum, mais vous infligez +20 % de dégâts.', '最大药瓶数-1，但伤害+20%。'),
  ['MOD||POTMAX:-1', 'MOD||DMG:0.20'], ic=('potion', 'hourglass', 'stone'))
