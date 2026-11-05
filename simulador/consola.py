"""Aplicación de consola (menú interactivo)."""
from typing import Optional

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
 6. Ejecutar simulación Round Robin
 7. Cargar caso Round Robin (10 procesos + bloqueo)
 8. Registrar proceso
 9. Configurar quantum de Round Robin (actual: {quantum})
 10. Ver última simulación
 0. Salir
"""

    def __init__(self):
        self.carga = CargaTrabajo()
        self.quantum = 4
        self.ultima_simulacion: Optional[Simulador] = None

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
            entrada = input(
                f"Quantum de Round Robin (entero > 0) [{self.quantum}]: "
            ).strip()
            try:
                quantum = int(entrada) if entrada else self.quantum
                planificador = ALGORITMOS["RR"](quantum)
            except ValueError:
                print("El quantum debe ser un entero mayor que cero.")
                continue
            break
        self.ejecutar_algoritmo(planificador)

    def registrar_proceso(self):
        pid = input("Identificador del proceso: ").strip()
        llegada = self._leer_entero("Tiempo de llegada (entero >= 0): ", minimo=0)
        rafaga = self._leer_entero("Ráfaga de CPU (entero > 0): ", minimo=1)
        try:
            self.carga.agregar(pid, llegada, rafaga)
        except ValueError as error:
            print(f"No se pudo registrar el proceso: {error}")
            return
        print(f"Proceso {pid} registrado.")
        self.mostrar_procesos()

    def configurar_quantum(self):
        self.quantum = self._leer_entero(
            "Nuevo quantum de Round Robin (entero > 0): ", minimo=1
        )
        print(f"Quantum de Round Robin configurado en {self.quantum}.")

    @staticmethod
    def _leer_entero(mensaje: str, minimo: int) -> int:
        while True:
            entrada = input(mensaje).strip()
            try:
                valor = int(entrada)
            except ValueError:
                print("Ingrese un número entero válido.")
                continue
            if valor < minimo:
                comparacion = "mayor que cero" if minimo == 1 else "mayor o igual a cero"
                print(f"El valor debe ser {comparacion}.")
                continue
            return valor

    def mostrar_procesos(self):
        if not self.carga.especs:
            print("No hay procesos cargados. Use la opción 1 o 7.")
            return
        print(f"\n{'ID':<6}{'Llegada':>8}{'Ráfaga':>8}   Evento E/S")
        print("-" * 46)
        for s in self.carga.especs:
            es = ", ".join(f"tras {a} u. de CPU bloquea {d} u." for a, d in s.eventos_es) or "-"
            print(f"{s.pid:<6}{s.llegada:>8}{s.rafaga:>8}   {es}")

    def mostrar_ultima_simulacion(self):
        if self.ultima_simulacion is None:
            print("Aún no se ha ejecutado ninguna simulación.")
            return
        print("\n".join(self.ultima_simulacion.traza))
        print(Reportero.informe(self.ultima_simulacion))

    def ejecutar_algoritmo(self, planificador: Planificador):
        if not self.carga.especs:
            print("Primero cargue los procesos (opción 1 o 7).")
            return
        sim = Simulador(self.carga.especs, planificador)  # copia nueva de la carga
        sim.ejecutar()
        self.ultima_simulacion = sim
        self.mostrar_ultima_simulacion()

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
        acciones["8"] = self.registrar_proceso
        acciones["9"] = self.configurar_quantum
        acciones["10"] = self.mostrar_ultima_simulacion
        while True:
            print(self.MENU.format(quantum=self.quantum))
            op = input("Seleccione una opción: ").strip()
            if op == "0":
                print("Fin del programa.")
                break
            (acciones.get(op) or (lambda: print("Opción inválida.")))()
