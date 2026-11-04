"""Pruebas del ingreso de procesos (CargaTrabajo.agregar / eliminar / limpiar)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulador.algoritmos import ALGORITMOS    # noqa: E402
from simulador.modelos import CargaTrabajo     # noqa: E402
from simulador.motor import Simulador          # noqa: E402


class PruebasCarga(unittest.TestCase):
    def setUp(self):
        self.c = CargaTrabajo()

    def test_agregar_y_simular(self):
        self.c.agregar("A", 0, 3, prioridad=2)
        self.c.agregar("B", 1, 2, eventos_es=((1, 2),))
        sim = Simulador(self.c.especs, ALGORITMOS["FIFO"]())
        sim.ejecutar()
        self.assertEqual(len(sim.finalizados), 2)
        self.assertEqual(self.c.especs[0].prioridad, 2)

    def test_rechaza_datos_invalidos(self):
        self.c.agregar("A", 0, 3)
        invalidos = [
            dict(pid="", llegada=0, rafaga=1),
            dict(pid="A", llegada=0, rafaga=1),                      # duplicado
            dict(pid="B", llegada=-1, rafaga=1),
            dict(pid="B", llegada=0, rafaga=0),
            dict(pid="B", llegada=0, rafaga=3, eventos_es=((3, 1),)),  # E/S al final
            dict(pid="B", llegada=0, rafaga=3, eventos_es=((1, 0),)),
            dict(pid="B", llegada=0, rafaga=4, eventos_es=((1, 1), (1, 2))),
        ]
        for datos in invalidos:
            with self.subTest(datos=datos), self.assertRaises(ValueError):
                self.c.agregar(**datos)
        self.assertEqual(len(self.c.especs), 1)

    def test_eliminar_y_limpiar(self):
        self.c.agregar("A", 0, 1)
        self.assertTrue(self.c.eliminar("A"))
        self.assertFalse(self.c.eliminar("A"))
        self.c.cargar_predefinida()
        self.c.limpiar()
        self.assertEqual(self.c.especs, ())


if __name__ == "__main__":
    unittest.main()
