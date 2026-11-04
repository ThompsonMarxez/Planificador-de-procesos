"""Constantes y utilidades compartidas por todos los módulos."""
import re

NUEVO, LISTO, EJECUCION, BLOQUEADO, FINALIZADO = (
    "Nuevo", "Listo", "Ejecución", "Bloqueado", "Finalizado")


def clave_natural(pid: str):
    """Orden natural de identificadores: P2 < P10."""
    return tuple(int(t) if t.isdigit() else t
                 for t in re.split(r"(\d+)", pid) if t)
