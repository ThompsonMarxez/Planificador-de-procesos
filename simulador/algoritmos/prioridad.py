"""Planificación por prioridades  ->  responsable: Francisco.

ERROR 404: CODE NOT FOUND
    \\(°o°)/   "Este algoritmo tiene prioridad máxima...
      |_|      ...pero nadie lo ha escrito todavía."
      / \\

Qué hay que hacer (ver todo.md, secciones 2 y 3):
  - Heredar de `Planificador` (algoritmos/base.py).
  - Elegir una variante (apropiativa o no) y documentarla en el README:
    qué valor es MAYOR prioridad, desempates, riesgo de inanición, envejecimiento.
  - Usar `p.prioridad` (ya existe en Proceso). Desempate sugerido por el
    enunciado: (prioridad, llegada, clave_natural(pid)).
  - Si es apropiativo: `apropiativo = True` y implementar `debe_expropiar`.
  - Registrarlo en `algoritmos/__init__.py` (diccionario ALGORITMOS).
"""
from .base import Planificador


class PlanificadorPrioridad(Planificador):
    nombre = "PRIORIDAD"

    def __init__(self):
        raise NotImplementedError(
            "404 - Code not found: las prioridades aún no existen. "
            "Pregúntale a Francisco :)")

    def seleccionar(self, listos):
        raise NotImplementedError("404 - Code not found (Francisco)")
