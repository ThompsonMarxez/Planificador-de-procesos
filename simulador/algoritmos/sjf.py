from ..constantes import clave_natural
from .base import Planificador


class PlanificadorSJF(Planificador):
    """SJF no apropiativo: menor RÁFAGA; clave (ráfaga, llegada, ID)."""
    nombre = "SJF"

    def seleccionar(self, listos):
        return min(listos, key=lambda p: (p.rafaga, p.llegada, clave_natural(p.pid)))
