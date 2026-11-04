from .base import Planificador


class PlanificadorFIFO(Planificador):
    """FIFO: atiende en el orden de entrada a la cola -> el primero (listos[0])."""
    nombre = "FIFO"

    def seleccionar(self, listos):
        return listos[0]
