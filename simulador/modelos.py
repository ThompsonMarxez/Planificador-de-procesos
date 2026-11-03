"""Modelo de datos: especificación inmutable, proceso y carga de trabajo."""
from dataclasses import dataclass
from typing import Optional, Tuple

from .constantes import NUEVO


@dataclass(frozen=True)
class EspecProceso:
    pid: str
    llegada: int                                    # T_llegada
    rafaga: int                                     # T_rafaga
    eventos_es: Tuple[Tuple[int, int], ...] = ()    # (CPU ejecutada, duración E/S)
    prioridad: int = 0                              # mayor valor = mayor prioridad


class Proceso:
    def __init__(self, espec: EspecProceso):
        self.pid = espec.pid
        self.llegada = espec.llegada
        self.rafaga = espec.rafaga
        self.restante = espec.rafaga
        self.prioridad = espec.prioridad
        self.estado = NUEVO
        self.inicio: Optional[int] = None
        self.fin: Optional[int] = None
        self.es_pendientes = list(espec.eventos_es)
        self.t_despertar: Optional[int] = None
        self.t_espera = 0               # ticks acumulados en la cola de listos
        self.t_bloqueado = 0            # ticks acumulados en la cola de bloqueados

    @property
    def ejecutado(self) -> int:
        return self.rafaga - self.restante

    @property
    def retorno(self) -> int:
        return self.fin - self.llegada

    @property
    def espera(self) -> int:
        """Solo el tiempo en la cola de listos (el tiempo bloqueado no cuenta)."""
        return self.t_espera

    @property
    def respuesta(self) -> int:
        return self.inicio - self.llegada


class CargaTrabajo:
    """Procesos ingresados. El menú solo usa agregar / eliminar / limpiar / cargar_predefinida;
    el simulador recibe `especs` (tupla inmutable), sea cual sea su origen."""

    def __init__(self):
        self.especs: Tuple[EspecProceso, ...] = ()

    def agregar(self, pid: str, llegada: int, rafaga: int,
                eventos_es: Tuple[Tuple[int, int], ...] = (), prioridad: int = 0) -> EspecProceso:
        """Valida y registra un proceso. Lanza ValueError con un mensaje legible."""
        pid = str(pid).strip()
        if not pid:
            raise ValueError("El identificador no puede estar vacío.")
        if any(e.pid == pid for e in self.especs):
            raise ValueError(f"Ya existe un proceso con ID {pid}.")
        if llegada < 0:
            raise ValueError("La llegada no puede ser negativa.")
        if rafaga <= 0:
            raise ValueError("La ráfaga debe ser mayor que cero.")
        eventos_es = tuple((int(a), int(d)) for a, d in eventos_es)
        puntos = [a for a, _ in eventos_es]
        if any(a <= 0 or a >= rafaga for a in puntos) or len(set(puntos)) != len(puntos):
            raise ValueError("Cada E/S debe ocurrir tras 1..ráfaga-1 u. de CPU, sin repetirse.")
        if any(d <= 0 for _, d in eventos_es):
            raise ValueError("La duración de la E/S debe ser mayor que cero.")
        espec = EspecProceso(pid, llegada, rafaga, tuple(sorted(eventos_es)), prioridad)
        self.especs += (espec,)
        return espec

    def eliminar(self, pid: str) -> bool:
        antes = len(self.especs)
        self.especs = tuple(e for e in self.especs if e.pid != pid)
        return len(self.especs) < antes

    def limpiar(self) -> None:
        self.especs = ()

    def cargar_predefinida(self) -> None:
        datos = [("P1", 0, 8), ("P2", 1, 4), ("P3", 2, 9), ("P4", 3, 5),
                 ("P5", 4, 2), ("P6", 5, 6), ("P7", 6, 3), ("P8", 7, 7),
                 ("P9", 8, 1), ("P10", 9, 4)]
        es = {"P3": ((3, 4),)}                      # evento de bloqueo
        self.especs = tuple(EspecProceso(p, a, b, es.get(p, ()))
                            for p, a, b in datos)

    def cargar_caso_rr(self) -> None:
        """10 procesos para Round Robin (probar con quantum 3 o 4); P3 se bloquea."""
        datos = [("P1", 0, 10), ("P2", 1, 5), ("P3", 2, 8), ("P4", 3, 3),
                 ("P5", 4, 6), ("P6", 6, 4), ("P7", 7, 9), ("P8", 9, 2),
                 ("P9", 10, 7), ("P10", 12, 5)]
        es = {"P3": ((3, 4),)}
        self.especs = tuple(EspecProceso(p, a, b, es.get(p, ()))
                            for p, a, b in datos)

    def cargar_caso_prioridades(self) -> None:
        """10 procesos con prioridades distintas (1..10; MAYOR valor = MAYOR prioridad).
        No siguen el orden de llegada, así que el orden difiere de FIFO.
        P4 y P5 llegan juntos en t=3; P2 se bloquea."""
        datos = [("P1", 0, 6, 4), ("P2", 1, 4, 9), ("P3", 2, 8, 2), ("P4", 3, 3, 7),
                 ("P5", 3, 5, 1), ("P6", 5, 2, 10), ("P7", 6, 7, 5), ("P8", 8, 4, 3),
                 ("P9", 9, 6, 8), ("P10", 10, 3, 6)]
        es = {"P2": ((2, 3),)}
        self.especs = tuple(EspecProceso(p, a, b, es.get(p, ()), pr)
                            for p, a, b, pr in datos)
