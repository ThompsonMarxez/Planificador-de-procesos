"""Presentación de resultados: Gantt ASCII, tabla y promedios."""
from typing import List, Optional, Tuple

from .constantes import clave_natural
from .modelos import Proceso
from .motor import Simulador


class Reportero:
    @staticmethod
    def gantt(linea_tiempo: List[Optional[str]], ancho_max: int = 96) -> str:
        # Comprimir ticks consecutivos iguales en segmentos (etiqueta, inicio, fin)
        segs: List[Tuple[str, int, int]] = []
        for t, pid in enumerate(linea_tiempo):
            etq = pid or "--"                       # "--" = CPU ociosa
            if segs and segs[-1][0] == etq:
                segs[-1] = (etq, segs[-1][1], t + 1)
            else:
                segs.append((etq, t, t + 1))

        # Dibujar en bloques que no excedan ancho_max
        salida, i = [], 0
        while i < len(segs):
            bloque, ancho = [], 1
            while i < len(segs):
                etq, s, e = segs[i]
                w = max(len(etq) + 2, (e - s) * 3)  # ancho proporcional a duración
                if bloque and ancho + w + 1 > ancho_max:
                    break
                bloque.append((etq, s, e, w))
                ancho += w + 1
                i += 1
            arriba = "+" + "+".join("-" * w for *_, w in bloque) + "+"
            medio = "|" + "|".join(etq.center(w) for etq, _, _, w in bloque) + "|"
            regla, pos = [" "] * (len(arriba) + 4), 0
            for _, s, _, w in bloque:               # instante de inicio de cada segmento
                regla[pos:pos + len(str(s))] = str(s)
                pos += w + 1
            fin = str(bloque[-1][2])                # instante final del bloque
            regla[pos:pos + len(fin)] = fin
            salida += [arriba, medio, arriba, "".join(regla).rstrip()]
        return "\n".join(salida)

    @staticmethod
    def tabla(procs: List[Proceso]) -> str:
        cab = (f"{'ID':<5}{'Llegada':>8}{'Ráfaga':>8}{'Inicio':>8}"
               f"{'Fin':>6}{'Espera':>8}{'Retorno':>9}{'Respuesta':>11}")
        filas = [f"{p.pid:<5}{p.llegada:>8}{p.rafaga:>8}{p.inicio:>8}{p.fin:>6}"
                 f"{p.espera:>8}{p.retorno:>9}{p.respuesta:>11}"
                 for p in sorted(procs, key=lambda p: clave_natural(p.pid))]
        return "\n".join([cab, "-" * len(cab)] + filas)

    @staticmethod
    def informe(sim: Simulador) -> str:
        n = len(sim.finalizados)
        prom = lambda f: sum(f(p) for p in sim.finalizados) / n
        nombre = sim.planificador.nombre
        return "\n".join([
            f"\n DIAGRAMA GANTT ({nombre})",
            Reportero.gantt(sim.linea_tiempo),
            f"\nTABLA DE RESULTADOS({nombre})",
            Reportero.tabla(sim.finalizados),
            "\nPROMEDIOS GLOBALES",
            f"Tiempo de Espera    promedio: {prom(lambda p: p.espera):.2f}",
            f"Tiempo de Retorno   promedio: {prom(lambda p: p.retorno):.2f}",
            f"Tiempo de Respuesta promedio: {prom(lambda p: p.respuesta):.2f}",
            "\nNota: Espera = tiempo acumulado en la cola de Listos; el tiempo "
            "Bloqueado NO cuenta como espera (Retorno = Ráfaga + Espera + Bloqueado).",
        ])
