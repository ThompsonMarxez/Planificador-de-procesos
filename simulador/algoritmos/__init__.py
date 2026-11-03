"""Registro de algoritmos disponibles.

El menú se construye leyendo este diccionario: para integrar un algoritmo nuevo
(Round Robin, Prioridades) basta crear su archivo y agregarlo aquí.
"""
from .base import Planificador
from .fifo import PlanificadorFIFO
from .sjf import PlanificadorSJF
from .srtf import PlanificadorSRTF

ALGORITMOS = {
    "FIFO": PlanificadorFIFO,
    "SJF": PlanificadorSJF,
    "SRTF": PlanificadorSRTF,
}

__all__ = ["Planificador", "ALGORITMOS", "PlanificadorFIFO",
           "PlanificadorSJF", "PlanificadorSRTF"]
