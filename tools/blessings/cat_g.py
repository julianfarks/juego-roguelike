from bl import *

# ===================== G. INVOCACIONES Y COMPAÑEROS (espiritus que te acompañan) =====================
B('G', C, 'luciernaga', ('Luciérnaga', 'Firefly', 'Luciole', '萤火虫'),
  ('Una luciérnaga te acompaña y dispara a los enemigos cercanos (50% de daño cada 2 s).', 'A firefly accompanies you and shoots nearby enemies (50% damage every 2 s).', 'Une luciole vous accompagne et tire sur les ennemis proches (50 % de dégâts toutes les 2 s).', '一只萤火虫伴随你，攻击附近的敌人（每2秒造成50%伤害）。'),
  ['SPIRIT||WISP:2,0.5'], ic=('orb', 'wing', 'yel'))
B('G', U, 'llama_fatua', ('Llama Fatua', 'Wisp of Flame', 'Feu follet', '鬼火'),
  ('Un espíritu de fuego te acompaña: dispara cada 2,6 s (55%) y prende fuego.', 'A fire spirit accompanies you: shoots every 2.6 s (55%) and ignites.', 'Un esprit de feu vous accompagne : tire toutes les 2,6 s (55 %) et enflamme.', '火焰精灵伴随你：每2.6秒攻击一次（55%伤害）并点燃目标。'),
  ['SPIRIT||WISP:2.6,0.55,burn'], ic=('orb', 'flame', 'fire'))
B('G', U, 'espiritu_hielo', ('Espíritu Glacial', 'Frost Spirit', 'Esprit glacial', '寒冰精灵'),
  ('Un espíritu de hielo libera cada 5 s una onda helada que ralentiza (70% de daño).', 'An ice spirit releases a freezing pulse every 5 s that slows (70% damage).', 'Un esprit de glace libère toutes les 5 s une onde glacée qui ralentit (70 % de dégâts).', '冰霜精灵每5秒释放一次减速的寒冰脉冲（70%伤害）。'),
  ['SPIRIT||NOVA:5,0.7,0,70'], ic=('orb', 'snow', 'ice'))
B('G', R, 'espiritu_rayo', ('Espíritu del Trueno', 'Thunder Spirit', 'Esprit du tonnerre', '雷霆精灵'),
  ('Un espíritu eléctrico lanza cada 4 s un rayo de 3 saltos (60% de daño).', 'A lightning spirit casts a 3-jump bolt every 4 s (60% damage).', 'Un esprit électrique lance toutes les 4 s un éclair à 3 sauts (60 % de dégâts).', '雷电精灵每4秒释放一道3次跳跃的闪电（60%伤害）。'),
  ['SPIRIT||SCHAIN:4,0.6,3'], ic=('orb', 'bolt', 'yel'))
B('G', R, 'espiritu_maldicion', ('Espíritu Maldito', 'Cursed Spirit', 'Esprit maudit', '诅咒精灵'),
  ('Un espíritu oscuro maldice cada 8 s al enemigo más sano (+20% de daño recibido).', 'A dark spirit curses the healthiest enemy every 8 s (+20% damage taken).', 'Un esprit sombre maudit toutes les 8 s l\'ennemi le plus sain (+20 % de dégâts reçus).', '黑暗精灵每8秒诅咒生命最高的敌人（受到伤害+20%）。'),
  ['SPIRIT||SMARK:8'], ic=('orb', 'skull', 'purple'))
B('G', U, 'espiritu_curativo', ('Espíritu Sanador', 'Healing Spirit', 'Esprit guérisseur', '治愈精灵'),
  ('Un espíritu te cura el 4% de tu vida cada 9 s si estás herido (límite por sala).', 'A spirit heals 4% of your health every 9 s when you are hurt (limited per room).', 'Un esprit vous soigne de 4 % de votre vie toutes les 9 s si vous êtes blessé (limité par salle).', '精灵每9秒恢复你4%生命（受伤时，每个房间有上限）。'),
  ['SPIRIT||SHEAL:9,0.04'], ic=('orb', 'cross', 'green'))
B('G', R, 'espiritu_guardian', ('Espíritu Guardián', 'Guardian Spirit', 'Esprit gardien', '守护精灵'),
  ('Un espíritu te protege con un escudo de 18 cada 14 s si no tienes ninguno.', 'A spirit shields you for 18 every 14 s if you have none.', 'Un esprit vous protège avec un bouclier de 18 toutes les 14 s si vous n\'en avez pas.', '精灵每14秒为你提供18点护盾（若你没有护盾）。'),
  ['SPIRIT||SGUARD:14,18'], ic=('orb', 'shield', 'cyan'))
B('G', U, 'espiritu_veneno', ('Espíritu Venenoso', 'Venom Spirit', 'Esprit venimeux', '剧毒精灵'),
  ('Un espíritu de veneno dispara cada 3 s (45%) y envenena.', 'A venom spirit shoots every 3 s (45%) and poisons.', 'Un esprit de venin tire toutes les 3 s (45 %) et empoisonne.', '剧毒精灵每3秒攻击一次（45%伤害）并使目标中毒。'),
  ['SPIRIT||WISP:3,0.45,poison'], ic=('orb', 'drop', 'green'))
B('G', R, 'espiritu_sombra', ('Espíritu de Sombra', 'Shadow Spirit', 'Esprit d\'ombre', '暗影精灵'),
  ('Un espíritu de sombra hiere cada 2,8 s (60%) y causa sangrado.', 'A shadow spirit strikes every 2.8 s (60%) and causes bleeding.', 'Un esprit d\'ombre frappe toutes les 2,8 s (60 %) et provoque un saignement.', '暗影精灵每2.8秒攻击一次（60%伤害）并造成流血。'),
  ['SPIRIT||WISP:2.8,0.6,bleed'], ic=('orb', 'dagger', 'dark'))
B('G', U, 'vinculo_espiritual', ('Vínculo Espiritual', 'Spirit Bond', 'Lien spirituel', '灵魂羁绊'),
  ('Un espíritu menor te acompaña (35% cada 3 s) y todos tus espíritus actúan un 30% más rápido.', 'A minor spirit accompanies you (35% every 3 s) and all your spirits act 30% faster.', 'Un esprit mineur vous accompagne (35 % toutes les 3 s) et tous vos esprits agissent 30 % plus vite.', '一只小精灵伴随你（每3秒35%伤害），所有精灵行动速度+30%。'),
  ['SPIRIT||WISP:3,0.35', 'MOD|p:spirit|SPIRITRATE:0.3'], ic=('ring', 'orb', 'pink'))
B('G', EP, 'sinfonia_espiritual', ('Sinfonía Espiritual', 'Spirit Symphony', 'Symphonie spirituelle', '灵魂交响'),
  ('Tus espíritus actúan un 50% más rápido y cada baja los acelera aún más durante 4 s.', 'Your spirits act 50% faster and each kill speeds them up further for 4 s.', 'Vos esprits agissent 50 % plus vite et chaque kill les accélère encore pendant 4 s.', '你的精灵行动速度+50%，每次击杀使其在4秒内进一步加速。'),
  ['MOD|p:spirit|SPIRITRATE:0.5', 'KILL|p:spirit|BURSTUP:4'], stage=1, ic=('note', 'orb', 'gold'))
B('G', R, 'pastor_almas', ('Pastor de Almas', 'Soul Shepherd', 'Berger d\'âmes', '牧魂人'),
  ('Cada alma recogida acelera a tus espíritus durante 5 s.', 'Each soul picked up speeds up your spirits for 5 s.', 'Chaque âme ramassée accélère vos esprits pendant 5 s.', '每拾取一个灵魂，精灵加速5秒。'),
  ['PICK|p:spirit|BURSTUP:5|what=soul'], ic=('soul', 'orb', 'cyan'))
B('G', L, 'legion_espectral', ('Legión Espectral', 'Spectral Legion', 'Légion spectrale', '幽灵军团'),
  ('Invoca tres espíritus: uno de fuego, uno glacial y uno eléctrico.', 'Summons three spirits: one of fire, one of ice and one of lightning.', 'Invoque trois esprits : un de feu, un de glace et un électrique.', '召唤三个精灵：火焰、寒冰和雷电各一。'),
  ['SPIRIT||WISP:2.4,0.5,burn', 'SPIRIT||NOVA:6,0.7,0,70', 'SPIRIT||SCHAIN:4.5,0.55,3'], stage=1, req=('cat', 'G', 3), ic=('ghost', 'orb', 'white'))
