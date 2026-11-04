"""Pruebas del motor: espera sin bloqueo, quantum, estados y Gantt.

Usa un Round Robin de prueba (definido aquí) para no depender del código de José.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulador.algoritmos import Planificador, PlanificadorFIFO   # noqa: E402
from simulador.modelos import EspecProceso                         # noqa: E402
from simulador.motor import Simulador                              # noqa: E402
from simulador.reportes import Reportero                           # noqa: E402


class RRPrueba(Planificador):
    nombre = "RR-prueba"

    def __init__(self, quantum):
        self.quantum = quantum

    def seleccionar(self, listos):
        return listos[0]


def correr(especs, planificador):
    sim = Simulador(tuple(especs), planificador)
    sim.ejecutar()
    return sim, {p.pid: p for p in sim.finalizados}


class PruebasEsperaConBloqueo(unittest.TestCase):
    def setUp(self):
        # P1 se bloquea 3 u. tras 2 u. de CPU; P2 ocupa la CPU mientras tanto.
        self.sim, self.p = correr(
            [EspecProceso("P1", 0, 4, ((2, 3),)), EspecProceso("P2", 0, 6)],
            PlanificadorFIFO())

    def test_espera_excluye_bloqueo(self):
        self.assertEqual(self.p["P1"].espera, 3)    # t=5,6,7 en listos
        self.assertEqual(self.p["P2"].espera, 2)    # t=0,1 en listos

    def test_bloqueo_se_contabiliza_aparte(self):
        self.assertEqual(self.p["P1"].t_bloqueado, 3)

    def test_retorno_es_rafaga_mas_espera_mas_bloqueo(self):
        for p in self.p.values():
            self.assertEqual(p.retorno, p.rafaga + p.espera + p.t_bloqueado)

    def test_ciclo_de_estados_completo(self):
        traza = "\n".join(self.sim.traza)
        orden = ["P1 llega (Nuevo -> Listo)",
                 "P1 despachado (Listo -> Ejecución)",
                 "P1 solicita E/S (Ejecución -> Bloqueado)",
                 "P1 termina E/S (Bloqueado -> Listo)",
                 "P1 finaliza (Ejecución -> Finalizado)"]
        pos = [traza.index(e) for e in orden]
        self.assertEqual(pos, sorted(pos))

    def test_metricas_y_gantt(self):
        p1 = self.p["P1"]
        self.assertEqual((p1.inicio, p1.fin, p1.retorno, p1.respuesta), (0, 10, 10, 0))
        self.assertEqual(self.sim.linea_tiempo,
                         ["P1", "P1", "P2", "P2", "P2", "P2", "P2", "P2", "P1", "P1"])
        self.assertIn("P1", Reportero.gantt(self.sim.linea_tiempo))


class PruebasQuantum(unittest.TestCase):
    def setUp(self):
        self.sim, self.p = correr(
            [EspecProceso("P1", 0, 5), EspecProceso("P2", 1, 3), EspecProceso("P3", 2, 1)],
            RRPrueba(2))

    def test_linea_de_tiempo(self):
        self.assertEqual(self.sim.linea_tiempo,
                         ["P1", "P1", "P2", "P2", "P3", "P1", "P1", "P2", "P1"])

    def test_nunca_excede_el_quantum_con_cola_no_vacia(self):
        # Rachas de un mismo pid mientras otros esperan: <= 2
        tl, racha = self.sim.linea_tiempo, 1
        for a, b in zip(tl, tl[1:]):
            racha = racha + 1 if a == b else 1
            self.assertLessEqual(racha, 2)

    def test_finalizaciones_y_metricas(self):
        self.assertEqual({k: v.fin for k, v in self.p.items()},
                         {"P1": 9, "P2": 8, "P3": 5})
        self.assertEqual({k: v.espera for k, v in self.p.items()},
                         {"P1": 4, "P2": 4, "P3": 2})

    def test_traza_registra_fin_de_quantum(self):
        self.assertIn("agota su quantum", "\n".join(self.sim.traza))

    def test_sin_competencia_no_hay_expropiacion(self):
        sim, _ = correr([EspecProceso("P1", 0, 5)], RRPrueba(2))
        self.assertEqual(sim.linea_tiempo, ["P1"] * 5)
        self.assertNotIn("agota su quantum", "\n".join(sim.traza))

    def test_quantum_invalido(self):
        for q in (0, -1):
            with self.assertRaises(ValueError):
                Simulador((EspecProceso("P1", 0, 1),), RRPrueba(q))

    def test_llegada_en_el_mismo_tick_del_vencimiento_va_antes(self):
        # P1 vence su quantum en t=2, justo cuando llega P3: P3 debe quedar antes que P1.
        sim, _ = correr([EspecProceso("P1", 0, 4), EspecProceso("P2", 1, 4),
                         EspecProceso("P3", 2, 1)], RRPrueba(2))
        self.assertEqual(sim.linea_tiempo[:5], ["P1", "P1", "P2", "P2", "P3"])


if __name__ == "__main__":
    unittest.main()
