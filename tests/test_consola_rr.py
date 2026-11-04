"""Pruebas de la integración de Round Robin con el menú de consola."""
import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulador.algoritmos import PlanificadorRoundRobin  # noqa: E402
from simulador.consola import AppConsola                  # noqa: E402
from simulador.modelos import CargaTrabajo                # noqa: E402


class PruebasConsolaRoundRobin(unittest.TestCase):
    def setUp(self):
        self.app = AppConsola()
        self.salida = io.StringIO()

    def test_cargar_caso_rr(self):
        with redirect_stdout(self.salida):
            self.app.cargar_caso_rr()
        esperada = CargaTrabajo()
        esperada.cargar_caso_rr()
        self.assertEqual(self.app.carga.especs, esperada.especs)
        self.assertIn("Caso Round Robin cargado.", self.salida.getvalue())
        self.assertIn("P10", self.salida.getvalue())

    def test_sin_carga_no_pide_quantum_ni_simula(self):
        with patch("builtins.input") as entrada, \
                patch.object(self.app, "ejecutar_algoritmo") as ejecutar, \
                redirect_stdout(self.salida):
            self.app.ejecutar_round_robin()
        entrada.assert_not_called()
        ejecutar.assert_not_called()
        self.assertIn("opción 1 o 7", self.salida.getvalue())

    def test_quantum_predeterminado_y_personalizado(self):
        self.app.carga.cargar_caso_rr()
        for entrada, quantum in (("", 4), ("   ", 4), ("3", 3), (" 1 ", 1)):
            with self.subTest(entrada=entrada), \
                    patch("builtins.input", return_value=entrada), \
                    patch.object(self.app, "ejecutar_algoritmo") as ejecutar:
                self.app.ejecutar_round_robin()
                ejecutar.assert_called_once()
                planificador = ejecutar.call_args[0][0]
                self.assertIsInstance(planificador, PlanificadorRoundRobin)
                self.assertEqual(planificador.quantum, quantum)

    def test_quantum_invalido_se_vuelve_a_pedir(self):
        self.app.carga.cargar_caso_rr()
        with patch("builtins.input", side_effect=["0", "-2", "abc", "2.5", "3"]) as entrada, \
                patch.object(self.app, "ejecutar_algoritmo") as ejecutar, \
                redirect_stdout(self.salida):
            self.app.ejecutar_round_robin()
        self.assertEqual(entrada.call_count, 5)
        ejecutar.assert_called_once()
        self.assertEqual(ejecutar.call_args[0][0].quantum, 3)
        self.assertEqual(self.salida.getvalue().count("entero mayor que cero"), 4)

    def test_menu_ejecuta_rr_con_reporte_y_permite_repetir(self):
        # Cargar RR, ejecutar con q=3, repetir con q=4 por defecto y salir.
        with patch("builtins.input", side_effect=["7", "6", "3", "6", "", "0"]), \
                redirect_stdout(self.salida):
            self.app.ejecutar()
        texto = self.salida.getvalue()
        self.assertEqual(texto.count("=== TRAZA DE SIMULACIÓN: RR ==="), 2)
        self.assertIn("agota su quantum de 3 u.", texto)
        self.assertIn("agota su quantum de 4 u.", texto)
        self.assertEqual(texto.count("Todos los procesos finalizaron en t=59"), 2)
        self.assertIn("GANTT", texto)
        self.assertIn("Fin del programa.", texto)
        esperada = CargaTrabajo()
        esperada.cargar_caso_rr()
        self.assertEqual(self.app.carga.especs, esperada.especs)

    def test_menu_rr_tambien_acepta_caso_base(self):
        with patch("builtins.input", side_effect=["1", "6", "2", "0"]), \
                redirect_stdout(self.salida):
            self.app.ejecutar()
        texto = self.salida.getvalue()
        self.assertIn("=== TRAZA DE SIMULACIÓN: RR ===", texto)
        self.assertIn("Todos los procesos finalizaron", texto)
        self.assertIn("Fin del programa.", texto)


if __name__ == "__main__":
    unittest.main()
