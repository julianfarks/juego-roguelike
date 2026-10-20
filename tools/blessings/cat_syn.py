from bl import *

HINT = ('Reúne {need} de sus bendiciones para activarla.', 'Gather {need} of its blessings to activate it.', 'Réunissez {need} de ses bénédictions pour l\'activer.', '集齐其中{need}个祝福即可激活。')


def SS(key, names, descs, need, members, rules):
    S(key, names, descs, need, members, rules, tuple(h.format(need=need) for h in HINT))


SS('infierno', ('Infierno', 'Inferno', 'Enfer', '炼狱'),
   ('Tus golpes contra enemigos en llamas propagan el fuego a los cercanos (cada 0,6 s) y los quemados reciben +10% de daño.', 'Your hits on burning enemies spread the fire to nearby ones (every 0.6 s) and burning enemies take +10% damage.',
    'Vos coups sur un ennemi en flammes propagent le feu aux proches (0,6 s) ; les ennemis en flammes subissent +10 % de dégâts.', '你对燃烧敌人的攻击会将火焰传给附近敌人（每0.6秒），燃烧的敌人受到的伤害+10%。'),
   3, 'BRASAS llama_voraz brasa_critica contagio_igneo pira aliento_dragon rastro_ardiente combustion llama_fatua disparo_incendiario parry_fuego corazon_ardiente fuego_rayo sangre_hirviente'.split(),
   ['HIT|v:burn|SPREAD:burn,70|icd=0.6', 'MOD|v:burn|DMG:0.10'])
SS('cripta_hielo', ('Cripta de Hielo', 'Ice Crypt', 'Crypte de glace', '寒冰地窖'),
   ('Tus críticos contra enemigos ralentizados o congelados estallan en escarcha (70% de daño, cada 0,8 s).', 'Your critical hits against slowed or frozen enemies burst into frost (70% damage, every 0.8 s).',
    'Vos critiques contre les ennemis ralentis ou gelés explosent en givre (70 % de dégâts, toutes les 0,8 s).', '你对减速或冰冻敌人的暴击会爆发寒霜（70%伤害，每0.8秒）。'),
   3, 'GLACIAL escarcha_quebradiza esquirlas_hielo aura_gelida ventisca congelacion_profunda disparo_gelido espiritu_hielo parry_hielo explosion_hielo choque_termico'.split(),
   ['CRIT|v:slow|EXPLODE:56,0.7,slow,2|icd=0.8'])
SS('tormenta_viva', ('Tormenta Viva', 'Living Storm', 'Tempête vivante', '活风暴'),
   ('Cada descarga arcana te da +15% de velocidad de ataque 4 s y carga un 6% de tu definitiva.', 'Each arcane discharge gives +15% attack speed for 4 s and charges 6% of your ultimate.',
    'Chaque décharge arcanique donne +15 % de vitesse d\'attaque pendant 4 s et charge 6 % de votre ultime.', '每次奥术放电使攻击速度+15%，持续4秒，并为终极技能充能6%。'),
   3, 'CHISPA carga_estatica pararrayos voltio_arcano bateria descarga_mayor conductor disparo_voltaico espiritu_rayo fuego_rayo tempestad_eterna'.split(),
   ['DISCHARGED||BUFF:atk,0.15,4,1', 'DISCHARGED||ULT:6'])
SS('muerte_lenta', ('Muerte Lenta', 'Slow Death', 'Mort lente', '缓慢死亡'),
   ('El daño periódico hace +25% y los enemigos con 2 o más estados alterados reciben +15% de daño.', 'Damage over time deals +25% and enemies with 2 or more status effects take +15% damage.',
    'Les dégâts sur la durée font +25 % et les ennemis avec 2 états altérés ou plus subissent +15 % de dégâts.', '持续伤害+25%，拥有2种及以上异常状态的敌人受到的伤害+15%。'),
   3, 'ESPINAS combustion ponzona_virulenta plaga toxina_nerviosa esporas sangria sangre_hirviente espiritu_veneno espiritu_sombra corrupcion veneno_critico electro_veneno'.split(),
   ['MOD||DOT:0.25', 'MOD|v:multi>=2|DMG:0.15'])
SS('contragolpe_perfecto', ('Contragolpe Perfecto', 'Perfect Counter', 'Contre parfait', '完美反击'),
   ('Cada parry reduce 1 s tus habilidades y te da +20% de velocidad de ataque durante 4 s.', 'Each parry shortens your skill cooldowns by 1 s and gives +20% attack speed for 4 s.',
    'Chaque parade réduit vos recharges de 1 s et donne +20 % de vitesse d\'attaque pendant 4 s.', '每次格挡使技能冷却缩短1秒，并获得+20%攻击速度，持续4秒。'),
   3, 'contra_parry parry_escudo parry_ulti eco_defensivo parry_maestro reflejo parry_calma parry_fuego parry_hielo pararrayos espectro reloj_destino'.split(),
   ['PARRY||CDR:1.0', 'PARRY||BUFF:atk,0.2,4,1'])
SS('muro_viviente', ('Muro Viviente', 'Living Wall', 'Mur vivant', '活墙'),
   ('Mientras tengas escudo haces +15% de daño, y cuando absorbe un golpe te curas el 3%.', 'While you have a shield you deal +15% damage, and when it absorbs a hit you heal 3%.',
    'Tant que vous avez un bouclier, vous infligez +15 % de dégâts, et quand il absorbe un coup, vous vous soignez de 3 %.', '拥有护盾时伤害+15%，护盾吸收攻击时恢复3%生命。'),
   3, 'ESCUDO EGIDA escudo_reactivo bastion_limpio armadura_hierro sangre_fria espiritu_guardian egida_perpetua corazon_escudo parry_escudo'.split(),
   ['MOD|p:shield|DMG:0.15', 'BLOCKED||HEAL:0.03|icd=1'])
SS('sangre_furia', ('Sangre y Furia', 'Blood and Fury', 'Sang et fureur', '血与怒'),
   ('Con poca vida: +15% de velocidad de ataque; matar cura el 4% y al ser herido tu siguiente golpe hace +50%.', 'At low health: +15% attack speed; killing heals 4% and when hurt your next hit deals +50%.',
    'À faible vie : +15 % de vitesse d\'attaque ; tuer soigne 4 % et, si vous êtes blessé, votre prochain coup inflige +50 %.', '生命值低时：攻击速度+15%；击杀恢复4%生命；受伤后下一击伤害+50%。'),
   3, 'rabia_herida ultimo_bastion sanguinario contragolpe coraza_espinas supervivencia forma_bestial sangre_fria SANGRE PIEDRA SEGUNDA FURIA'.split(),
   ['MOD|p:low|ATKSPD:0.15', 'KILL|p:low|HEAL:0.04|icd=0.3', 'HURT|p:low|NEXTHIT:0.5,5'])
SS('ritmo_imparable', ('Ritmo Imparable', 'Unstoppable Rhythm', 'Rythme inarrêtable', '势不可挡'),
   ('Cada crítico da +8% de velocidad de ataque durante 3 s (hasta 3 cargas) y +6% de probabilidad de crítico.', 'Each critical hit gives +8% attack speed for 3 s (up to 3 stacks) and +6% critical chance.',
    'Chaque critique donne +8 % de vitesse d\'attaque pendant 3 s (jusqu\'à 3 cumuls) et +6 % de chance de critique.', '每次暴击攻击速度+8%，持续3秒（最多3层），并且暴击率+6%。'),
   3, 'CRITICO ojo_halcon impulso_letal cadena_criticos combo_ritmo hoja_rapida cadencia rafaga_remate sed_batalla ensanamiento skill_critico remate_brutal'.split(),
   ['CRIT||BUFF:atk,0.08,3,3', 'MOD||CRIT:0.06'])
SS('artilleria', ('Artillería', 'Artillery', 'Artillerie', '炮兵'),
   ('Tus proyectiles hacen +20% de daño y explotan al terminar (35% de daño).', 'Your projectiles deal +20% damage and explode at the end of their path (35% damage).',
    'Vos projectiles infligent +20 % de dégâts et explosent à la fin de leur trajet (35 % de dégâts).', '你的投射物伤害+20%，并在飞行终点爆炸（35%伤害）。'),
   3, 'proyectil_explosivo ricochet perforante doble_lanzamiento punta_afilada buscador vuelo_veloz onda_expansiva ONDA lluvia_hojas rafaga_estelar disparo_incendiario disparo_gelido disparo_voltaico orbe_santo tormenta_acero foco_letal francotirador triple_filo estela_mortal'.split(),
   ['MOD||PROJDMG:0.20', 'PROJEND||EXPLODE:40,0.35|icd=0.4'])
SS('danza_eterea', ('Danza Etérea', 'Ethereal Dance', 'Danse éthérée', '空灵之舞'),
   ('Cada esquiva carga un 8% de tu definitiva y potencia tu siguiente habilidad un 40% (5 s).', 'Each dodge charges 8% of your ultimate and empowers your next skill by 40% (5 s).',
    'Chaque esquive charge 8 % de votre ultime et renforce votre prochaine compétence de 40 % (5 s).', '每次闪避为终极技能充能8%，并使下一个技能强化40%（5秒）。'),
   3, 'esquiva_sagrada danza_cuchillas evasion_magica bateria segundo_aliento sombra_veloz FANTASMA SOMBRA viento_cola reloj_destino aura_penumbra rastro_ardiente estela_mortal'.split(),
   ['DODGE||ULT:8', 'DODGE||NEXTSKILL:0.4,5'])
SS('alquimia_mayor', ('Alquimia Mayor', 'Grand Alchemy', 'Grande alchimie', '大炼金术'),
   ('Cada moneda carga 1,5% de tu definitiva y cada alma 3%; con 100 de oro o más haces +8% de daño.', 'Each coin charges 1.5% of your ultimate and each soul 3%; with 100 gold or more you deal +8% damage.',
    'Chaque pièce charge 1,5 % de votre ultime et chaque âme 3 % ; avec 100 d\'or ou plus, vous infligez +8 % de dégâts.', '每枚金币为终极技能充能1.5%，每个灵魂3%；持有100以上金币时伤害+8%。'),
   3, 'FORTUNA ALMA IMAN interes oro_poder cosecha_almas almas_poder alquimista reserva_pociones brebaje_extra suerte_dorada botin_elites recaudador cazatesoros ladron_almas corona_avaro mercader_astuto corazon_escudo'.split(),
   ['PICK|-|ULT:1.5|what=gold', 'PICK|-|ULT:3|what=soul', 'MOD|p:gold>=100|DMG:0.08'])
SS('legion_mas_alla', ('Legión del Más Allá', 'Legion Beyond', 'Légion de l\'au-delà', '彼岸军团'),
   ('Mientras tengas espíritus haces +10% de daño; al ser herido uno te protege con 12 de escudo (cada 8 s).', 'While you have spirits you deal +10% damage; when hurt, one shields you for 12 (every 8 s).',
    'Avec des esprits, +10 % de dégâts ; si vous êtes blessé, l\'un d\'eux vous donne 12 de bouclier (toutes les 8 s).', '拥有精灵时伤害+10%；受伤时一只精灵为你提供12点护盾（每8秒）。'),
   2, 'luciernaga llama_fatua espiritu_hielo espiritu_rayo espiritu_maldicion espiritu_curativo espiritu_guardian espiritu_veneno espiritu_sombra vinculo_espiritual sinfonia_espiritual pastor_almas legion_espectral'.split(),
   ['MOD|p:spirit|DMG:0.10', 'HURT|p:spirit|SHIELD:12|icd=8'])
SS('oscuridad', ('Oscuridad Total', 'Total Darkness', 'Ténèbres totales', '无尽黑暗'),
   ('Los enemigos malditos reciben +15% de daño extra y al morir cargan un 5% de tu definitiva.', 'Cursed enemies take +15% extra damage and charge 5% of your ultimate when they die.',
    'Les ennemis maudits subissent +15 % de dégâts supplémentaires et chargent 5 % de votre ultime à leur mort.', '被诅咒的敌人受到的伤害额外+15%，死亡时为终极技能充能5%。'),
   3, 'marca_maldita sentencia_oscura maldicion_expansiva cosecha_maldita festin_oscuro crit_maldito corrupcion espiritu_maldicion forma_sombra espectro aura_penumbra'.split(),
   ['MOD|v:curse|DMG:0.15', 'KILL|v:curse|ULT:5'])
SS('pacto_riesgo', ('Pacto del Riesgo', 'Risk Pact', 'Pacte du risque', '风险契约'),
   ('Limpiar una sala sin recibir daño da +15% de daño durante 25 s y 10 de oro.', 'Clearing a room without being hurt gives +15% damage for 25 s and 10 gold.',
    'Nettoyer une salle sans être blessé donne +15 % de dégâts pendant 25 s et 10 d\'or.', '不受伤地清理房间，获得+15%伤害（25秒）和10金币。'),
   2, 'desafio_doble sed_riesgo vidrio_filo pacto_sangre todo_o_nada temerario caza_mayor juicio ayuno sacrificio apostador ultimo_recurso'.split(),
   ['CLEAR|p:noroomhit|BUFF:dmg,0.15,25,1', 'CLEAR|p:noroomhit|GOLD:10'])
SS('hechicero_supremo', ('Hechicero Supremo', 'Supreme Sorcerer', 'Sorcier suprême', '至尊术士'),
   ('Cada habilidad reduce 0,8 s las demás y tu definitiva potencia tus habilidades un 30% durante 8 s.', 'Each skill shortens the others by 0.8 s and your ultimate empowers skills by 30% for 8 s.',
    'Chaque compétence réduit les autres de 0,8 s et votre ultime renforce vos compétences de 30 % pendant 8 s.', '每个技能使其他技能冷却缩短0.8秒，终极技能使技能强化30%（8秒）。'),
   3, 'HABILIDAD ENFRIAMIENTO SABIO canalizador catalizador resonancia manantial runa_poder eco_arcano voltio_arcano ventisca lluvia_hojas skill_critico aliento_dragon tormenta_acero'.split(),
   ['SKILL||CDR:0.8', 'ULT||BUFF:skill,0.3,8,1'])
SS('cazador_elites', ('Cazador de Élites', 'Elite Hunter', 'Chasseur d\'élite', '精英猎手'),
   ('+15% de probabilidad de crítico contra mini-jefes y jefes; matarlos te cura el 5%.', '+15% critical chance against mini-bosses and bosses; killing them heals 5%.',
    '+15 % de chance de critique contre les mini-boss et boss ; les tuer vous soigne de 5 %.', '对精英和首领暴击率+15%；击杀它们恢复5%生命。'),
   3, 'rompeguardias EJECUTOR ensanamiento punalada peso_pesado enjambre caza_mayor cosecha_almas botin_elites GIGANTE sentencia remate_brutal'.split(),
   ['MOD|v:elite|CRIT:0.15', 'KILL|v:elite|HEAL:0.05'])
SS('terremoto', ('Terremoto', 'Earthquake', 'Séisme', '地震'),
   ('Al aterrizar de una caída larga ganas +20% de daño 4 s y cada salto en el aire te da 8 de escudo (cada 2 s).', 'Landing from a long fall gives +20% damage for 4 s and each mid-air jump gives 8 shield (every 2 s).',
    'Atterrir d\'une longue chute donne +20 % de dégâts pendant 4 s et chaque saut en l\'air donne 8 de bouclier (toutes les 2 s).', '长距离坠落着地后伤害+20%（4秒），每次空中跳跃获得8点护盾（每2秒）。'),
   3, 'DOBLE_SALTO salto_explosivo aterrizaje_sismico danza_aerea acrobata viento_cola ALAS maestro_trampas'.split(),
   ['LAND||BUFF:dmg,0.2,4,1', 'AIRJUMP||SHIELD:8|icd=2'])
SS('reaccion_cadena', ('Reacción en Cadena', 'Chain Reaction', 'Réaction en chaîne', '连锁反应'),
   ('Tus golpes a enemigos rodeados tienen 15% de provocar una explosión (40% de daño, cada 1 s).', 'Your hits on surrounded enemies have a 15% chance to cause an explosion (40% damage, every 1 s).',
    'Vos coups sur des ennemis entourés ont 15 % de chance de provoquer une explosion (40 % de dégâts, toutes les 1 s).', '你对被包围的敌人发动攻击时，有15%几率引发爆炸（40%伤害，每1秒）。'),
   3, 'VENGANZA pira escudo_reactivo coraza_espinas eco_defensivo frasco_explosivo sentencia proyectil_explosivo salto_explosivo aterrizaje_sismico choque_termico explosion_hielo electro_veneno'.split(),
   ['HIT|v:crowd|EXPLODE:50,0.4|ch=0.15 icd=1'])
SS('resonancia_elemental', ('Resonancia Elemental', 'Elemental Resonance', 'Résonance élémentaire', '元素共鸣'),
   ('Golpear a un enemigo con 2 o más estados alterados lanza un rayo de 2 saltos (cada 1,2 s).', 'Hitting an enemy with 2 or more status effects casts a 2-jump lightning bolt (every 1.2 s).',
    'Frapper un ennemi avec 2 états altérés ou plus lance un éclair à 2 sauts (toutes les 1,2 s).', '攻击拥有2种及以上异常状态的敌人，释放2次跳跃的闪电（每1.2秒）。'),
   3, 'BRASAS GLACIAL CHISPA ESPINAS marca_maldita sangria disparo_incendiario disparo_gelido disparo_voltaico llama_fatua espiritu_hielo espiritu_rayo espiritu_veneno'.split(),
   ['HIT|v:multi>=2|CHAIN:2,0.4|icd=1.2'])
SS('frasco_vida', ('Frasco de Vida', 'Life Flask', 'Fiole de vie', '生命之瓶'),
   ('Toda curación recibida es un 25% mayor y beber un frasco te da 25 de escudo.', 'All healing received is 25% greater and drinking a flask gives you 25 shield.',
    'Tous les soins reçus sont 25 % plus importants et boire une fiole vous donne 25 de bouclier.', '所有受到的治疗效果+25%，饮用药瓶获得25点护盾。'),
   3, 'alquimista reserva_pociones brebaje_extra ayuno frasco_explosivo ultimo_recurso sacrificio CORAZON vitalidad cosecha_vida sanacion_sala parry_calma espiritu_curativo supervivencia'.split(),
   ['MOD||HEALMUL:0.25', 'POTION||SHIELD:25'])

# ---- Cadenas de reaccion (etapa 4): critico -> explosion elemental -> muerte -> mas explosion/propagacion.
# Los KILL anidados estan limitados por BlessFx (profundidad < 3) y cada regla lleva su icd, asi nada se dispara en bucle.
SS('detonacion_critica', ('Detonación Crítica', 'Critical Detonation', 'Détonation critique', '暴击爆裂'),
   ('Tus críticos provocan una explosión que quema (50% de daño, cada 0,6 s).', 'Your critical hits cause an explosion that burns (50% damage, every 0.6 s).',
    'Vos critiques provoquent une explosion qui brûle (50 % de dégâts, toutes les 0,6 s).', '你的暴击会引发灼烧爆炸（50%伤害，每0.6秒）。'),
   3, 'CRITICO brasa_critica veneno_critico proyectil_explosivo salto_explosivo frasco_explosivo explosion_hielo VENGANZA pira'.split(),
   ['CRIT||EXPLODE:50,0.5,burn,2|icd=0.6'])
SS('funeral_igneo', ('Funeral Ígneo', 'Fiery Funeral', 'Funérailles ardentes', '烈焰葬礼'),
   ('Los enemigos que mueren en llamas explotan y siguen quemando (50% de daño, cada 0,25 s).', 'Enemies that die burning explode and keep burning (50% damage, every 0.25 s).',
    'Les ennemis qui meurent en flammes explosent et continuent de brûler (50 % de dégâts, toutes les 0,25 s).', '燃烧中死亡的敌人会爆炸并继续燃烧（50%伤害，每0.25秒）。'),
   3, 'BRASAS llama_voraz pira combustion rastro_ardiente VENGANZA corazon_ardiente aliento_dragon disparo_incendiario'.split(),
   ['KILL|v:burn|EXPLODE:55,0.5,burn,2|icd=0.25'])
SS('plaga_viva', ('Plaga Viva', 'Living Plague', 'Peste vivante', '活体瘟疫'),
   ('Los enemigos que mueren envenenados esparcen el veneno a los cercanos (cada 0,25 s).', 'Enemies that die poisoned spread the poison to nearby ones (every 0.25 s).',
    'Les ennemis qui meurent empoisonnés répandent le poison aux proches (toutes les 0,25 s).', '中毒死亡的敌人会将毒素传给附近敌人（每0.25秒）。'),
   3, 'ESPINAS plaga ponzona_virulenta toxina_nerviosa esporas veneno_critico espiritu_veneno corrupcion'.split(),
   ['KILL|v:poison|SPREAD:poison,80|icd=0.25'])
