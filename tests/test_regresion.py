"""Regresión de la etapa 02: FIFO, SJF y SRTF deben seguir iguales tras modularizar.

Ejecutar desde la raíz del proyecto:  python3 -m unittest discover -s tests -v
"""
import contextlib
import io
import os
import sys
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from simulador.algoritmos import ALGORITMOS          # noqa: E402
from simulador.consola import AppConsola             # noqa: E402
from simulador.modelos import CargaTrabajo           # noqa: E402
from simulador.motor import Simulador                # noqa: E402

# (espera, retorno, respuesta) promedio sobre el caso predefinido.
# La espera ya NO incluye el bloqueo de P3 (-0.4 respecto de la etapa 02);
# retorno y respuesta no cambian.
PROMEDIOS_ESPERADOS = {
    "FIFO": (19.20, 24.50, 16.80),
    "SJF": (13.70, 19.00, 13.70),
    "SRTF": (12.10, 17.40, 9.50),
}


def simular(nombre):
    carga = CargaTrabajo()
    carga.cargar_predefinida()
    sim = Simulador(carga.especs, ALGORITMOS[nombre]())
    sim.ejecutar()
    return sim


class PruebasAlgoritmosBase(unittest.TestCase):
    def test_promedios(self):
        for nombre, esperado in PROMEDIOS_ESPERADOS.items():
            with self.subTest(algoritmo=nombre):
                sim = simular(nombre)
                n = len(sim.finalizados)
                obtenido = tuple(round(sum(getattr(p, a) for p in sim.finalizados) / n, 2)
                                 for a in ("espera", "retorno", "respuesta"))
                self.assertEqual(obtenido, esperado)

    def test_todos_finalizan(self):
        for nombre in PROMEDIOS_ESPERADOS:
            with self.subTest(algoritmo=nombre):
                sim = simular(nombre)
                self.assertEqual(len(sim.finalizados), 10)
                # Gantt: ticks de CPU == suma de ráfagas (no hay ociosidad evitable aquí)
                self.assertEqual(sum(1 for x in sim.linea_tiempo if x),
                                 sum(p.rafaga for p in sim.procesos))

    def test_p3_se_bloquea_y_vuelve_a_listo(self):
        sim = simular("FIFO")
        texto = "\n".join(sim.traza)
        self.assertIn("P3 solicita E/S (Ejecución -> Bloqueado)", texto)
        self.assertIn("P3 termina E/S (Bloqueado -> Listo)", texto)

    def test_la_carga_original_no_se_modifica(self):
        carga = CargaTrabajo()
        carga.cargar_predefinida()
        antes = carga.especs
        Simulador(carga.especs, ALGORITMOS["SRTF"]()).ejecutar()
        self.assertEqual(carga.especs, antes)


class PruebaSalidaIdentica(unittest.TestCase):
    def test_salida_igual_al_main_original(self):
        base = os.path.join(RAIZ, "tests", "salida_base.txt")
        with open(base, encoding="utf-8") as f:
            esperado = f.read()
        buf = io.StringIO()
        entradas = iter(["1", "3", "4", "5", "0"])

        def input_simulado(prompt=""):
            print(prompt, end="")                   # input() real escribe el prompt
            return next(entradas)

        with mock.patch("builtins.input", input_simulado), \
                contextlib.redirect_stdout(buf):
            AppConsola().ejecutar()
        self.assertEqual(buf.getvalue(), esperado)


if __name__ == "__main__":
    unittest.main()
