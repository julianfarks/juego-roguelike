"""Ajuste final de rareza (el poder y la complejidad de cada bendicion deciden su rareza)."""
from bl import *

TO_COMMON = '''enjambre alcance pulso_constante remate_brutal sed_batalla llama_voraz rastro_ardiente aura_gelida voltio_arcano conductor ponzona_virulenta esporas
manantial parry_escudo parry_ulti bastion_limpio vitalidad sanacion_sala cosecha_vida impulso_rodar sombra_veloz racha_cazador golpe_corriendo acrobata buscador
disparo_gelido mercader_astuto reserva_pociones suerte_dorada botin_elites'''.split()
TO_EPIC = '''doble_tajo pira pararrayos plaga parry_maestro coraza_espinas espiritu_rayo proyectil_explosivo pacto_sangre vision_altar forma_bestial'''.split()


def apply():
    by = {e['key']: e for e in ENTRIES}
    for k in TO_COMMON:
        by[k]['rar'] = C
        by[k]['w'] = 10
    for k in TO_EPIC:
        by[k]['rar'] = EP
        by[k]['w'] = 4
        by[k]['stage'] = max(by[k]['stage'], 1)
    for e in ENTRIES:
        if e['rar'] == EP:
            e['stage'] = max(e['stage'], 1)
