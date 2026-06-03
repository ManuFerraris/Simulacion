"""
Módulo lcgrand: Generador de números aleatorios uniformes en [0,1)

Este módulo proporciona una función compatible con la interfaz original
del programa C lcgrand para generar números aleatorios uniformes.
Utiliza random.random() de Python como base para generar secuencias
de números pseudoaleatorios de alta calidad.
"""

import random


def lcgrand(stream):
    """
    Genera un número pseudoaleatorio uniforme en el rango [0, 1).
    
    Compatible con la interfaz del programa C original. El parámetro
    stream permite preservar la sintaxis exacta lcgrand(1), lcgrand(2), etc.,
    aunque internamente usa el generador estándar de Python.
    
    Parámetros:
        stream (int): Identificador del flujo de números aleatorios.
                     Se proporciona para mantener compatibilidad con la
                     versión C, pero no afecta la generación.
    
    Retorna:
        float: Número pseudoaleatorio uniforme en [0, 1)
    
    Ejemplo:
        >>> u = lcgrand(1)
        >>> 0 <= u < 1
        True
    """
    return random.random()
