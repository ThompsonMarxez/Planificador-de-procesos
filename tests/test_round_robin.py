"""Pruebas de Round Robin: contrato, cola circular y simulación con E/S.

Las líneas de tiempo y métricas esperadas se calculan por turnos a mano;
no se usa otro Round Robin ni el motor para construir los resultados esperados.
"""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulador import algoritmos                                    # noqa: E402
from simulador.algoritmos import (ALGORITMOS, Planificador,           # noqa: E402
                                 PlanificadorFIFO, PlanificadorRoundRobin)
from simulador.algoritmos.round_robin import (                       # noqa: E402
    PlanificadorRoundRobin as ClaseRoundRobin)
from simulador.constantes import FINALIZADO                          # noqa: E402
from simulador.modelos import CargaTrabajo, EspecProceso, Proceso     # noqa: E402
from simulador.motor import Simulador                                # noqa: E402


def correr(especs, quantum=4):
    sim = Simulador(tuple(especs), PlanificadorRoundRobin(quantum))
    sim.ejecutar()
    return sim, {p.pid: p for p in sim.finalizados}


def metricas(procesos):
    """(inicio, fin, espera, retorno, respuesta, bloqueo) por proceso."""
    return {p.pid: (p.inicio, p.fin, p.espera, p.retorno,
                    p.respuesta, p.t_bloqueado) for p in procesos}


class PruebasContratoRoundRobin(unittest.TestCase):
    def test_quantum_por_defecto_y_nombre(self):
        rr = PlanificadorRoundRobin()
        self.assertIsInstance(rr, Planificador)
        self.assertEqual(rr.nombre, "RR")
        self.assertEqual(rr.quantum, 4)

    def test_quantum_entero_positivo(self):
        for quantum in (1, 2, 3, 4, 100):
            with self.subTest(quantum=quantum):
                self.assertEqual(PlanificadorRoundRobin(quantum).quantum, quantum)

    def test_rechaza_cero_y_enteros_negativos(self):
        for quantum in (0, -1, -100):
            with self.subTest(quantum=quantum):
                with self.assertRaises(ValueError):
                    PlanificadorRoundRobin(quantum)

    def test_rechaza_bool_y_tipos_no_enteros_con_value_error(self):
        for quantum in (True, False, None, "4", "", 4.0, 0.5,
                        float("inf"), float("nan"), 2 + 0j, [], {}, object()):
            with self.subTest(quantum=quantum):
                with self.assertRaises(ValueError):
                    PlanificadorRoundRobin(quantum)

    def test_registro_y_exportacion(self):
        self.assertIs(PlanificadorRoundRobin, ClaseRoundRobin)
        self.assertIs(ALGORITMOS["RR"], PlanificadorRoundRobin)
        self.assertIn("PlanificadorRoundRobin", algoritmos.__all__)
        self.assertEqual(ALGORITMOS["RR"]().quantum, 4)

    def test_selecciona_primero_sin_mutar_cola_ni_procesos(self):
        # Ni ID, llegada, ráfaga ni prioridad deben reordenar la cola recibida.
        listos = [Proceso(EspecProceso("P9", 5, 9, ((2, 1),), -2)),
                  Proceso(EspecProceso("P1", 0, 1, prioridad=99)),
                  Proceso(EspecProceso("P2", 0, 3))]
        originales = list(listos)
        estados = copy.deepcopy([vars(p) for p in listos])
        rr = PlanificadorRoundRobin(2)
        for _ in range(3):
            self.assertIs(rr.seleccionar(listos), originales[0])
            self.assertEqual(listos, originales)
            self.assertEqual([vars(p) for p in listos], estados)

    def test_cola_vacia_lanza_index_error_sin_mutarla(self):
        listos = []
        with self.assertRaises(IndexError):
            PlanificadorRoundRobin().seleccionar(listos)
        self.assertEqual(listos, [])


class PruebasRoundRobin(unittest.TestCase):
    def test_reincorpora_al_final_y_respeta_quantum_con_competencia(self):
        sim, _ = correr([EspecProceso("P1", 0, 4), EspecProceso("P2", 0, 4),
                         EspecProceso("P3", 0, 4)], 2)
        self.assertEqual(sim.linea_tiempo,
                         ["P1", "P1", "P2", "P2", "P3", "P3",
                          "P1", "P1", "P2", "P2", "P3", "P3"])
        self.assertEqual([p.pid for p in sim.finalizados], ["P1", "P2", "P3"])
        self.assertEqual("\n".join(sim.traza).count("agota su quantum"), 3)

    def test_llegada_durante_quantum_no_interrumpe(self):
        sim, _ = correr([EspecProceso("P1", 0, 5), EspecProceso("P2", 1, 1)], 3)
        self.assertEqual(sim.linea_tiempo, ["P1", "P1", "P1", "P2", "P1", "P1"])

    def test_llegada_al_vencer_quantum_precede_al_interrumpido(self):
        # P3 llega en t=2: queda después del P2 que esperaba, pero antes de P1.
        sim, _ = correr([EspecProceso("P1", 0, 4), EspecProceso("P2", 1, 4),
                         EspecProceso("P3", 2, 1)], 2)
        self.assertEqual(sim.linea_tiempo,
                         ["P1", "P1", "P2", "P2", "P3", "P1", "P1", "P2", "P2"])

    def test_metricas_exactas_caso_pequeno(self):
        sim, _ = correr([EspecProceso("P1", 0, 5), EspecProceso("P2", 1, 3),
                         EspecProceso("P3", 2, 1)], 2)
        self.assertEqual(sim.linea_tiempo,
                         ["P1", "P1", "P2", "P2", "P3", "P1", "P1", "P2", "P1"])
        self.assertEqual(metricas(sim.finalizados), {
            "P1": (0, 9, 4, 9, 0, 0),
            "P2": (2, 8, 4, 7, 1, 0),
            "P3": (4, 5, 2, 3, 2, 0),
        })
        self.assertEqual([p.pid for p in sim.finalizados], ["P3", "P2", "P1"])
        for p in sim.finalizados:
            self.assertEqual(p.estado, FINALIZADO)
            self.assertEqual(p.restante, 0)

    def test_bloqueo_y_reinicio_de_quantum_en_cada_despacho(self):
        # P1 usa 2 de sus 3 ticks y se bloquea hasta t=4. Al volver en t=7
        # recibe 3 ticks completos, no solo el tick que le quedaba antes de E/S.
        sim, _ = correr([EspecProceso("P1", 0, 6, ((2, 2),)),
                         EspecProceso("P2", 0, 7), EspecProceso("P3", 0, 2)], 3)
        self.assertEqual(sim.linea_tiempo,
                         ["P1"] * 2 + ["P2"] * 3 + ["P3"] * 2 +
                         ["P1"] * 3 + ["P2"] * 3 + ["P1", "P2"])
        self.assertEqual(metricas(sim.finalizados), {
            "P1": (0, 14, 6, 14, 0, 2),
            "P2": (2, 15, 8, 15, 2, 0),
            "P3": (5, 7, 5, 7, 5, 0),
        })
        traza = "\n".join(sim.traza)
        self.assertIn("P1 solicita E/S (Ejecución -> Bloqueado)", traza)
        self.assertIn("P1 termina E/S (Bloqueado -> Listo)", traza)
        for p in sim.finalizados:
            self.assertEqual(p.retorno, p.rafaga + p.espera + p.t_bloqueado)

    def test_fin_de_es_al_vencer_quantum_precede_al_interrumpido(self):
        # P1 despierta en t=3, exactamente cuando P2 agota sus dos ticks.
        sim, _ = correr([EspecProceso("P1", 0, 3, ((1, 2),)),
                         EspecProceso("P2", 0, 4)], 2)
        self.assertEqual(sim.linea_tiempo, ["P1", "P2", "P2", "P1", "P1", "P2", "P2"])
        self.assertEqual(metricas(sim.finalizados), {
            "P1": (0, 5, 0, 5, 0, 2),
            "P2": (1, 7, 3, 7, 1, 0),
        })

    def test_solicitud_de_es_al_consumir_quantum_no_reencola_bloqueado(self):
        sim, _ = correr([EspecProceso("P1", 0, 4, ((2, 2),)),
                         EspecProceso("P2", 0, 4)], 2)
        self.assertEqual(sim.linea_tiempo,
                         ["P1", "P1", "P2", "P2", "P1", "P1", "P2", "P2"])
        self.assertNotIn("P1 agota su quantum", "\n".join(sim.traza))

    def test_sin_competencia_continua_sin_expropiar(self):
        sim, p = correr([EspecProceso("P1", 0, 7)], 2)
        self.assertEqual(sim.linea_tiempo, ["P1"] * 7)
        self.assertNotIn("agota su quantum", "\n".join(sim.traza))
        self.assertEqual(metricas(p.values()), {"P1": (0, 7, 0, 7, 0, 0)})

    def test_sin_competencia_renueva_quantum_antes_de_una_llegada(self):
        # P1 renueva en t=2 y t=4. P2 llega en t=5 y espera hasta t=6.
        sim, _ = correr([EspecProceso("P1", 0, 8), EspecProceso("P2", 5, 1)], 2)
        self.assertEqual(sim.linea_tiempo, ["P1"] * 6 + ["P2", "P1", "P1"])

    def test_quantum_uno_alterna_y_admite_nuevos_antes_de_reencolar(self):
        sim, _ = correr([EspecProceso("P1", 0, 3), EspecProceso("P2", 0, 2),
                         EspecProceso("P3", 1, 1)], 1)
        self.assertEqual(sim.linea_tiempo, ["P1", "P2", "P3", "P1", "P2", "P1"])

    def test_quantum_grande_equivale_a_fifo(self):
        especs = (EspecProceso("P1", 0, 4), EspecProceso("P2", 1, 2),
                  EspecProceso("P3", 2, 1))
        sim, _ = correr(especs, 100)
        fifo = Simulador(especs, PlanificadorFIFO())
        fifo.ejecutar()
        # Expectativa literal además de la comparación con FIFO.
        self.assertEqual(sim.linea_tiempo, ["P1"] * 4 + ["P2"] * 2 + ["P3"])
        self.assertEqual(sim.linea_tiempo, fifo.linea_tiempo)
        self.assertEqual(metricas(sim.finalizados), metricas(fifo.finalizados))
        self.assertNotIn("agota su quantum", "\n".join(sim.traza))

    def test_carga_vacia_no_ejecuta_ni_despacha(self):
        sim, p = correr(())
        self.assertEqual(sim.procesos, [])
        self.assertEqual(sim.linea_tiempo, [])
        self.assertEqual(sim.finalizados, [])
        self.assertEqual(sim.cola_listos, [])
        self.assertEqual(sim.cola_bloqueados, [])
        self.assertIsNone(sim.cpu)
        self.assertEqual(p, {})
        self.assertNotIn("despachado", "\n".join(sim.traza))

    def test_cpu_ociosa_por_llegada_y_bloqueo(self):
        sim, _ = correr([EspecProceso("P1", 2, 3, ((1, 2),))], 1)
        self.assertEqual(sim.linea_tiempo, [None, None, "P1", None, None, "P1", "P1"])
        self.assertEqual(metricas(sim.finalizados), {"P1": (2, 7, 0, 5, 0, 2)})

    def test_caso_de_10_procesos_quantum_tres_y_cuatro(self):
        carga = CargaTrabajo()
        carga.cargar_caso_rr()
        # Turnos calculados a mano. P3 consume 3 ticks y se bloquea 4 unidades.
        turnos = {
            3: [("P1", 3), ("P2", 3), ("P3", 3), ("P4", 3), ("P1", 3),
                ("P5", 3), ("P6", 3), ("P2", 2), ("P7", 3), ("P8", 2),
                ("P9", 3), ("P10", 3), ("P3", 3), ("P1", 3), ("P5", 3),
                ("P6", 1), ("P7", 3), ("P9", 3), ("P10", 2), ("P3", 2),
                ("P1", 1), ("P7", 3), ("P9", 1)],
            4: [("P1", 4), ("P2", 4), ("P3", 3), ("P4", 3), ("P5", 4),
                ("P1", 4), ("P6", 4), ("P7", 4), ("P2", 1), ("P8", 2),
                ("P9", 4), ("P10", 4), ("P3", 4), ("P5", 2), ("P1", 2),
                ("P7", 4), ("P9", 3), ("P10", 1), ("P3", 1), ("P7", 1)],
        }
        finales = {
            3: {"P1": 55, "P2": 23, "P3": 54, "P4": 12, "P5": 43,
                "P6": 44, "P7": 58, "P8": 28, "P9": 59, "P10": 52},
            4: {"P1": 49, "P2": 31, "P3": 58, "P4": 14, "P5": 47,
                "P6": 26, "P7": 59, "P8": 33, "P9": 56, "P10": 57},
        }
        for quantum in (3, 4):
            with self.subTest(quantum=quantum):
                sim, p = correr(carga.especs, quantum)
                esperado = [pid for pid, duracion in turnos[quantum]
                            for _ in range(duracion)]
                self.assertEqual(sim.linea_tiempo, esperado)
                self.assertEqual({pid: proceso.fin for pid, proceso in p.items()},
                                 finales[quantum])
                self.assertEqual(len(sim.finalizados), 10)
                self.assertEqual(len(sim.linea_tiempo), 59)
                self.assertEqual(p["P3"].t_bloqueado, 4)
                for proceso in sim.finalizados:
                    self.assertEqual(sim.linea_tiempo.count(proceso.pid), proceso.rafaga)
                    self.assertEqual(proceso.estado, FINALIZADO)
                    self.assertEqual(proceso.retorno,
                                     proceso.rafaga + proceso.espera + proceso.t_bloqueado)

    def test_determinismo_y_carga_inmutable_en_ejecuciones_independientes(self):
        carga = CargaTrabajo()
        carga.cargar_caso_rr()
        originales = copy.deepcopy(carga.especs)
        for quantum in (3, 4):
            with self.subTest(quantum=quantum):
                rr = PlanificadorRoundRobin(quantum)
                primera = Simulador(carga.especs, rr)
                primera.ejecutar()
                segunda = Simulador(carga.especs, rr)
                segunda.ejecutar()
                self.assertEqual(carga.especs, originales)
                self.assertEqual(primera.linea_tiempo, segunda.linea_tiempo)
                self.assertEqual(primera.traza, segunda.traza)
                self.assertEqual(metricas(primera.finalizados), metricas(segunda.finalizados))
                for p1, p2 in zip(primera.procesos, segunda.procesos):
                    self.assertIsNot(p1, p2)
                    self.assertIsNot(p1.es_pendientes, p2.es_pendientes)
                self.assertEqual(carga.especs[2].eventos_es, ((3, 4),))
                self.assertEqual(primera.procesos[2].es_pendientes, [])
                self.assertEqual(segunda.procesos[2].es_pendientes, [])
                self.assertEqual(rr.quantum, quantum)


if __name__ == "__main__":
    unittest.main()
