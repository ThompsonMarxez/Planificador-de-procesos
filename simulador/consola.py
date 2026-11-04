"""Aplicación de consola (menú interactivo)."""
from .algoritmos import ALGORITMOS, Planificador
from .modelos import CargaTrabajo
from .motor import Simulador
from .reportes import Reportero


class AppConsola:
    MENU = """
 SIMULADOR DE PLANIFICACIÓN DE CPU 
 1. Cargar caso de prueba predefinido (10 procesos + bloqueo)
 2. Visualizar procesos ingresados
 3. Ejecutar simulación FIFO
 4. Ejecutar simulación SJF
 5. Ejecutar simulación SRTF
 6. Ejecutar simulación Round Robin (configurar quantum)
 7. Cargar caso Round Robin (10 procesos + bloqueo)
 0. Salir
"""

    def __init__(self):
        self.carga = CargaTrabajo()

    def cargar_predefinida(self):
        self.carga.cargar_predefinida()
        print("Caso predefinido cargado.")
        self.mostrar_procesos()

    def cargar_caso_rr(self):
        self.carga.cargar_caso_rr()
        print("Caso Round Robin cargado.")
        self.mostrar_procesos()

    def ejecutar_round_robin(self):
        if not self.carga.especs:
            print("Primero cargue los procesos (opción 1 o 7).")
            return
        while True:
            entrada = input("Quantum de Round Robin (entero > 0) [4]: ").strip()
            try:
                quantum = int(entrada) if entrada else 4
                planificador = ALGORITMOS["RR"](quantum)
            except ValueError:
                print("El quantum debe ser un entero mayor que cero.")
                continue
            break
        self.ejecutar_algoritmo(planificador)

    def mostrar_procesos(self):
        if not self.carga.especs:
            print("No hay procesos cargados. Use la opción 1 o 7.")
            return
        print(f"\n{'ID':<6}{'Llegada':>8}{'Ráfaga':>8}   Evento E/S")
        print("-" * 46)
        for s in self.carga.especs:
            es = ", ".join(f"tras {a} u. de CPU bloquea {d} u." for a, d in s.eventos_es) or "-"
            print(f"{s.pid:<6}{s.llegada:>8}{s.rafaga:>8}   {es}")

    def ejecutar_algoritmo(self, planificador: Planificador):
        if not self.carga.especs:
            print("Primero cargue los procesos (opción 1 o 7).")
            return
        sim = Simulador(self.carga.especs, planificador)  # copia nueva de la carga
        sim.ejecutar()
        print("\n".join(sim.traza))
        print(Reportero.informe(sim))

    def ejecutar(self):
        acciones = {
            "1": self.cargar_predefinida,
            "2": self.mostrar_procesos,
            "3": lambda: self.ejecutar_algoritmo(ALGORITMOS["FIFO"]()),
            "4": lambda: self.ejecutar_algoritmo(ALGORITMOS["SJF"]()),
            "5": lambda: self.ejecutar_algoritmo(ALGORITMOS["SRTF"]()),
            "6": self.ejecutar_round_robin,
            "7": self.cargar_caso_rr,
        }
        while True:
            print(self.MENU)
            op = input("Seleccione una opción: ").strip()
            if op == "0":
                print("Fin del programa.")
                break
            (acciones.get(op) or (lambda: print("Opción inválida.")))()
