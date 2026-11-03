"""Pruebas de los casos predefinidos de 10 procesos (RR y prioridades)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulador.algoritmos import ALGORITMOS, Planificador    # noqa: E402
from simulador.modelos import CargaTrabajo                   # noqa: E402
from simulador.motor import Simulador                        # noqa: E402


class RRPrueba(Planificador):
    nombre = "RR-prueba"

    def __init__(self, quantum):
        self.quantum = quantum

    def seleccionar(self, listos):
        return listos[0]


def cargar(metodo):
    c = CargaTrabajo()
    getattr(c, metodo)()
    return c


class PruebasCasos(unittest.TestCase):
    CASOS = ("cargar_predefinida", "cargar_caso_rr", "cargar_caso_prioridades")

    def test_diez_procesos_ids_unicos(self):
        for m in self.CASOS:
            with self.subTest(caso=m):
                especs = cargar(m).especs
                self.assertEqual(len(especs), 10)
                self.assertEqual(len({e.pid for e in especs}), 10)

    def test_todos_terminan_y_hay_bloqueo_que_vuelve(self):
        for m in self.CASOS:
            with self.subTest(caso=m):
                sim = Simulador(cargar(m).especs, ALGORITMOS["FIFO"]())
                sim.ejecutar()
                traza = "\n".join(sim.traza)
                self.assertEqual(len(sim.finalizados), 10)
                self.assertIn("(Ejecución -> Bloqueado)", traza)
                self.assertIn("(Bloqueado -> Listo)", traza)
                for p in sim.finalizados:
                    self.assertEqual(p.retorno, p.rafaga + p.espera + p.t_bloqueado)

    def test_prioridades_distintas(self):
        prios = [e.prioridad for e in cargar("cargar_caso_prioridades").especs]
        self.assertEqual(sorted(prios), list(range(1, 11)))

    def test_prioridades_no_siguen_orden_de_llegada(self):
        prios = [e.prioridad for e in cargar("cargar_caso_prioridades").especs]
        self.assertNotEqual(prios, sorted(prios))
        self.assertNotEqual(prios, sorted(prios, reverse=True))

    def test_rr_rota_la_cola(self):
        for q in (3, 4):
            with self.subTest(quantum=q):
                sim = Simulador(cargar("cargar_caso_rr").especs, RRPrueba(q))
                sim.ejecutar()
                self.assertEqual(len(sim.finalizados), 10)
                self.assertIn("agota su quantum", "\n".join(sim.traza))


if __name__ == "__main__":
    unittest.main()
