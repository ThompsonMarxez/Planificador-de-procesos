"""Registro de algoritmos disponibles.

El menú instancia los planificadores desde este diccionario. Para integrar un
algoritmo nuevo, registrarlo aquí y agregar su opción en la consola.
"""
from .base import Planificador
from .fifo import PlanificadorFIFO
from .round_robin import PlanificadorRoundRobin
from .sjf import PlanificadorSJF
from .srtf import PlanificadorSRTF

ALGORITMOS = {
    "FIFO": PlanificadorFIFO,
    "SJF": PlanificadorSJF,
    "SRTF": PlanificadorSRTF,
    "RR": PlanificadorRoundRobin,
}

__all__ = ["Planificador", "ALGORITMOS", "PlanificadorFIFO",
           "PlanificadorSJF", "PlanificadorSRTF", "PlanificadorRoundRobin"]
