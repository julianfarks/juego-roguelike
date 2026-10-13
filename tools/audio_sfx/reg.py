import zlib
import numpy as np

REG = {}   # nombre -> (funcion(rng)->array, nivel_dB relativo a -3 dBFS)


def sfx(name, lvl=0.0):
    def deco(fn):
        REG[name] = (fn, lvl)
        return fn
    return deco


def add(name, fn, lvl=0.0):
    REG[name] = (fn, lvl)


def rng_for(name):
    return np.random.default_rng(zlib.crc32(name.encode()))
