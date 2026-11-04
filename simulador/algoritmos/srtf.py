from ..constantes import clave_natural
from .base import Planificador


class PlanificadorSRTF(Planificador):
    """SRTF apropiativo: menor tiempo RESTANTE; clave (restante, llegada, ID)."""
    nombre = "SRTF"
    apropiativo = True

    def seleccionar(self, listos):
        return min(listos, key=lambda p: (p.restante, p.llegada, clave_natural(p.pid)))

    def debe_expropiar(self, en_ejecucion, listos):
        return self.seleccionar(listos).restante < en_ejecucion.restante
