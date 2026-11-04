"""Planificador Round Robin (responsable: José Luna).

Selecciona el primer proceso de la cola de listos. El motor administra el
quantum y devuelve al final de la cola los procesos que agotan su turno;
el planificador no retira ni reordena procesos.
"""
from typing import List

from .base import Planificador
from ..modelos import Proceso


class PlanificadorRoundRobin(Planificador):
    """Turnos FIFO con un quantum entero positivo (4 unidades por defecto).

    La expropiación por tiempo la realiza el motor al leer ``quantum``.
    No se usa ``apropiativo``: esa bandera habilita expropiaciones por
    prioridad o tiempo restante, no el vencimiento del turno.
    """

    nombre = "RR"

    def __init__(self, quantum: int = 4):
        if isinstance(quantum, bool) or not isinstance(quantum, int) or quantum <= 0:
            raise ValueError("El quantum debe ser un entero mayor que cero.")
        self.quantum = quantum

    def seleccionar(self, listos: List[Proceso]) -> Proceso:
        """Devuelve la cabeza sin modificar la cola; el motor la pasa no vacía."""
        return listos[0]
