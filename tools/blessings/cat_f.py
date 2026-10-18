from bl import *

# ===================== F. RECURSOS, COFRES Y RECOMPENSAS =====================
B('F', U, 'mercader_astuto', ('Mercader Astuto', 'Shrewd Trader', 'Marchand rusé', '精明商人'),
  ('Los precios de las tiendas bajan un 10% por nivel (máx. 50%).', 'Shop prices drop 10% per level (max 50%).', 'Les prix des boutiques baissent de 10 % par niveau (max 50 %).', '商店价格降低10%（每级，最多50%）。'),
  ['MOD||SHOPDISC:0.10|scale'], mx=2, ic=('coin', 'hand', 'gold'))
B('F', R, 'interes', ('Interés Compuesto', 'Compound Interest', 'Intérêts composés', '复利'),
  ('Al limpiar una sala con 100 o más de oro, ganas 12 de oro extra.', 'Clearing a room with 100 or more gold earns 12 extra gold.', 'Nettoyer une salle avec au moins 100 d\'or rapporte 12 d\'or de plus.', '持有100以上金币时清理房间，额外获得12金币。'),
  ['CLEAR|p:gold>=100|GOLD:12'], ic=('coin', 'hourglass', 'gold'))
B('F', R, 'oro_poder', ('Poder del Oro', 'Power of Gold', 'Pouvoir de l\'or', '黄金之力'),
  ('Con 150 o más de oro, haces +12% de daño.', 'With 150 or more gold, you deal +12% damage.', 'Avec 150 d\'or ou plus, vous infligez +12 % de dégâts.', '持有150以上金币时，伤害+12%。'),
  ['MOD|p:gold>=150|DMG:0.12'], ic=('coin', 'sword', 'yel'))
B('F', U, 'cosecha_almas', ('Cosecha de Almas', 'Soul Harvest', 'Moisson d\'âmes', '灵魂收割'),
  ('Los mini-jefes y jefes sueltan 6 almas extra al morir.', 'Mini-bosses and bosses drop 6 extra souls on death.', 'Les mini-boss et boss lâchent 6 âmes de plus à leur mort.', '精英和首领死亡时额外掉落6点灵魂。'),
  ['KILL|v:elite|SOULS:6'], ic=('soul', 'skull', 'cyan'))
B('F', EP, 'almas_poder', ('Almas en Furia', 'Souls Ablaze', 'Âmes en furie', '魂之狂怒'),
  ('Cada alma recogida da +5% de daño durante 6 s (hasta 5 cargas).', 'Each soul picked up gives +5% damage for 6 s (up to 5 stacks).', 'Chaque âme ramassée donne +5 % de dégâts pendant 6 s (jusqu\'à 5 cumuls).', '每拾取一个灵魂，伤害+5%，持续6秒（最多5层）。'),
  ['PICK|-|BUFF:dmg,0.05,6,5|what=soul'], stage=1, ic=('soul', 'flame', 'purple'))
B('F', U, 'corazon_escudo', ('Corazón Blindado', 'Armored Heart', 'Cœur blindé', '铁心'),
  ('Un corazón recogido con la vida llena te da 12 de escudo.', 'A heart picked up at full health gives 12 shield.', 'Un cœur ramassé à pleine vie donne 12 de bouclier.', '满血时拾取心形物品，获得12点护盾。'),
  ['OVERFLOW|-|SHIELD:12|what=heart'], ic=('heart', 'shield', 'red'))
B('F', U, 'alquimista', ('Alquimista', 'Alchemist', 'Alchimiste', '炼金术士'),
  ('Beber un frasco te da +20% de daño durante 8 s y limpia tus estados alterados.', 'Drinking a flask gives +20% damage for 8 s and cleanses your status effects.', 'Boire une fiole donne +20 % de dégâts pendant 8 s et purifie vos états altérés.', '饮用药瓶后伤害+20%，持续8秒，并清除你的异常状态。'),
  ['POTION||BUFF:dmg,0.2,8,1', 'POTION||CLEANSE'], ic=('potion', 'flame', 'green'))
B('F', U, 'reserva_pociones', ('Reserva de Frascos', 'Flask Reserve', 'Réserve de fioles', '药瓶储备'),
  ('+1 frasco de curación máximo.', '+1 maximum healing flask.', '+1 fiole de soin maximum.', '最大药瓶数量+1。'),
  ['MOD||POTMAX:1'], ic=('potion', 'cross', 'pink'))
B('F', U, 'brebaje_extra', ('Brebaje Rebosante', 'Overflowing Brew', 'Breuvage débordant', '满溢药剂'),
  ('Un frasco recogido con la reserva llena cura el 12% de tu vida.', 'A flask picked up with a full reserve heals 12% of your health.', 'Une fiole ramassée avec une réserve pleine soigne 12 % de votre vie.', '药瓶已满时拾取药瓶，恢复12%生命。'),
  ['OVERFLOW|-|HEAL:0.12|what=potion'], ic=('potion', 'heart', 'teal'))
B('F', R, 'vision_altar', ('Visión del Altar', 'Altar Vision', 'Vision de l\'autel', '祭坛视界'),
  ('Los altares de bendición ofrecen una opción adicional.', 'Blessing altars offer one additional option.', 'Les autels de bénédiction offrent une option de plus.', '祝福祭坛多提供一个选项。'),
  ['MOD||OFFER:1'], ic=('eye', 'altar', 'purple'))
B('F', U, 'suerte_dorada', ('Suerte Dorada', 'Golden Luck', 'Chance dorée', '金色幸运'),
  ('+1 de suerte: mejores recompensas en cofres y tiendas.', '+1 luck: better rewards from chests and shops.', '+1 chance : de meilleures récompenses dans les coffres et boutiques.', '幸运+1：宝箱和商店的奖励更好。'),
  ['MOD||LUCK:1'], ic=('clover', 'coin', 'green'))
B('F', U, 'botin_elites', ('Botín de Élite', 'Elite Spoils', 'Butin d\'élite', '精英战利品'),
  ('Los mini-jefes y jefes sueltan 15 de oro extra.', 'Mini-bosses and bosses drop 15 extra gold.', 'Les mini-boss et boss lâchent 15 d\'or de plus.', '精英和首领额外掉落15金币。'),
  ['KILL|v:elite|GOLD:15'], ic=('coin', 'crown', 'copper'))
B('F', C, 'recaudador', ('Recaudador', 'Tax Collector', 'Collecteur', '收税官'),
  ('Cada baja con tu arma te da 1 de oro (límite por sala).', 'Each weapon kill gives you 1 gold (limited per room).', 'Chaque kill à l\'arme vous donne 1 d\'or (limité par salle).', '每次用武器击杀获得1金币（每个房间有上限）。'),
  ['KILL|s:W|GOLD:1'], ic=('coin', 'sword', 'stone'))
B('F', C, 'cazatesoros', ('Cazatesoros', 'Treasure Hunter', 'Chasseur de trésors', '寻宝者'),
  ('Al entrar en una sala ganas 8 de oro.', 'Entering a room gives you 8 gold.', 'Entrer dans une salle vous donne 8 d\'or.', '进入房间时获得8金币。'),
  ['ROOM||GOLD:8'], ic=('key', 'coin', 'yel'))
B('F', U, 'ladron_almas', ('Ladrón de Almas', 'Soul Thief', 'Voleur d\'âmes', '盗魂者'),
  ('Los críticos te dan 2 almas (cada 0,8 s, límite por sala).', 'Critical hits give you 2 souls (every 0.8 s, limited per room).', 'Les critiques vous donnent 2 âmes (toutes les 0,8 s, limité par salle).', '暴击获得2点灵魂（每0.8秒，每个房间有上限）。'),
  ['CRIT||SOULS:2|icd=0.8'], ic=('soul', 'star', 'white'))
B('F', L, 'corona_avaro', ('Corona del Avaro', 'Miser\'s Crown', 'Couronne de l\'avare', '守财奴之冠'),
  ('+50% de oro. Con 200 o más de oro haces +20% de daño y cada baja te da 2 de oro (límite por sala).', '+50% gold. With 200 or more gold you deal +20% damage and each kill gives 2 gold (limited per room).',
   '+50 % d\'or. Avec 200 d\'or ou plus : +20 % de dégâts et chaque kill donne 2 d\'or (limité par salle).', '金币+50%。持有200以上金币时伤害+20%，每次击杀获得2金币（每个房间有上限）。'),
  ['MOD||GOLDMUL:0.5', 'MOD|p:gold>=200|DMG:0.2', 'KILL|p:gold>=200|GOLD:2'], stage=1, req=('cat', 'F', 3), ic=('crown', 'coin', 'gold'))
