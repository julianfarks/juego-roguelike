#!/usr/bin/env python3
"""Genera el hash de un codigo canjeable para anadirlo a Codes.java (los codigos no se guardan en claro en el cliente).
Uso: python3 tools/code_hash.py MI_CODIGO"""
import hashlib, sys
code = ''.join(sys.argv[1].lower().split())
print(hashlib.sha256(('swr1:' + code).encode()).hexdigest())
