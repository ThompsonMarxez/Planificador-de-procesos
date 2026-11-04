"""Round Robin  ->  responsable: José Luna.

ERROR 404: CODE NOT FOUND
    (   )
   ( o_o )   "Aquí debería haber un Round Robin, pero el quantum
    |   |     se fue a dar vueltas y todavía no vuelve a la cola."
   /|___|\\

Qué hay que hacer (ver todo.md, secciones 2 y 3):
  - Heredar de `Planificador` (algoritmos/base.py) y ponerle `nombre = "RR"`.
  - Recibir el quantum (> 0) en el constructor y exponerlo en `self.quantum`;
    el motor lo leerá para interrumpir al proceso al agotarlo y devolverlo
    al FINAL de la cola de listos.
  - `seleccionar(listos)`: cola circular -> devolver `listos[0]`.
  - Registrarlo en `algoritmos/__init__.py` (diccionario ALGORITMOS).
"""
from .base import Planificador


class PlanificadorRoundRobin(Planificador):
    nombre = "RR"

    def __init__(self, quantum: int = 4):
        raise NotImplementedError(
            "404 - Code not found: Round Robin aún no existe. "
            "Pregúntale a José Luna :)")

    def seleccionar(self, listos):
        raise NotImplementedError("404 - Code not found (José Luna)")
