# Simulador de planificación de procesos de corto plazo

Simulador por consola en Python 3 (solo biblioteca estándar).
Algoritmos: **FIFO**, **SJF** (no apropiativo), **SRTF** (apropiativo), **Round Robin** y **prioridades**
(estos dos últimos en integración, ver [Estado](#estado-de-la-integración)). Incluye el estado
**Bloqueado** por eventos de E/S.

## Integrantes

| Integrante | Responsabilidad |
|---|---|
| Benjamin Zamora (motor) | Arquitectura, motor de simulación, integración |
| José Luna | Round Robin (`simulador/algoritmos/round_robin.py`) |
| Francisco | Algoritmo con prioridades (`simulador/algoritmos/prioridad.py`) |
| Benja (menú) | Menú de consola (`simulador/consola.py`) |
| Thomas | Pruebas (`tests/`) |

## Ejecución

```
python3 main.py                              # abre el menú
python3 -m unittest discover -s tests -v     # ejecuta las pruebas
```

Requiere Python 3.8 o superior; no hay dependencias externas.

## Estructura

```
main.py                      # punto de entrada
simulador/
  constantes.py              # estados y clave_natural (orden P2 < P10)
  modelos.py                 # EspecProceso, Proceso, CargaTrabajo
  motor.py                   # Simulador: reloj, colas y CPU
  reportes.py                # Reportero: Gantt ASCII, tabla y promedios
  consola.py                 # AppConsola: menú interactivo
  algoritmos/
    base.py                  # Planificador (interfaz)
    fifo.py  sjf.py  srtf.py
    round_robin.py           # pendiente (José Luna)
    prioridad.py             # pendiente (Francisco)
    __init__.py              # registro ALGORITMOS
tests/                       # regresión, motor y esqueletos de RR/prioridades
```

## Clases

| Clase | Rol |
|---|---|
| `EspecProceso` | Copia inmutable del proceso: id, llegada, ráfaga, eventos de E/S, prioridad |
| `Proceso` | Proceso en simulación: restante, estado, inicio, fin, espera, bloqueado y métricas |
| `CargaTrabajo` | Guarda la carga ingresada y el caso predefinido |
| `Planificador` | Interfaz (patrón Strategy); un algoritmo por clase |
| `Simulador` | Reloj, cola de listos, cola de bloqueados y CPU |
| `Reportero` | Gantt ASCII, tabla de resultados y promedios |
| `AppConsola` | Menú interactivo |

El simulador crea objetos `Proceso` nuevos a partir de las `EspecProceso`, así que la carga
original no se modifica y se puede simular varias veces.

## Listas y estados

Listas: **cola de listos** (se agrega al final), **cola de bloqueados** y **CPU** (un solo proceso a la vez).

```
Nuevo -> Listo -> Ejecución -> Finalizado
                    |   ^
                    v   |
                 Bloqueado        (E/S: vuelve a Listo al terminar)
Ejecución -> Listo                (expropiado por SRTF/prioridad o por fin de quantum)
```

Cada unidad de tiempo (tick) el motor hace, en este orden:

1. **Admisión:** entran a listos las llegadas y los que terminan E/S (desempate: llegada, luego ID).
2. **Fin de quantum** (si el algoritmo define `quantum`) y **expropiación** (si es apropiativo).
3. **Despacho:** si la CPU está libre, el planificador elige de la cola de listos.
4. **Ejecución** de una unidad (o CPU ociosa) y contabilidad de espera/bloqueo.
5. **Fin de tick:** el proceso finaliza o pasa a Bloqueado si le toca un evento de E/S.

Los eventos de E/S son `(CPU ejecutada, duración)`: tras ejecutar esa cantidad de CPU el proceso se bloquea.

## Métricas

- **Retorno** = fin − llegada.
- **Respuesta** = primer inicio − llegada.
- **Espera** = tiempo acumulado en la cola de listos. **No** incluye el tiempo bloqueado.
- Se cumple `Retorno = Ráfaga + Espera + Bloqueado`.

Desempates generales: primero el que llegó antes y luego el de menor identificador.

## Quantum (Round Robin)

- Un algoritmo con quantum expone `self.quantum` (entero > 0). Con 0 o negativo el simulador lanza `ValueError`.
- El proceso ejecuta como máximo `quantum` unidades seguidas; si no termina, vuelve al **final** de la cola de listos.
- Si no hay otros procesos listos, continúa ejecutando otro quantum sin ser interrumpido.
- Si un proceso llega en el mismo instante en que vence un quantum, **entra a la cola antes** que el proceso interrumpido.
- Un proceso que se bloquea o termina antes del quantum libera la CPU y el siguiente parte con un quantum completo.

## Algoritmo con prioridades

**Convención del equipo: el valor numérico MÁS ALTO es la MAYOR prioridad.**

> Pendiente (Francisco). Debe documentar aquí: algoritmo elegido, apropiativo o no,
> desempates, riesgo de inanición y uso de envejecimiento (si se implementa).

## Casos predefinidos

Todos tienen 10 procesos y un proceso que se bloquea y vuelve a listos (`CargaTrabajo`):

| Método | Uso |
|---|---|
| `cargar_predefinida()` | Caso base de FIFO/SJF/SRTF (P3 se bloquea) |
| `cargar_caso_rr()` | Round Robin; probar con quantum 3 o 4 (P3 se bloquea) |
| `cargar_caso_prioridades()` | Prioridades 1..10 todas distintas y fuera del orden de llegada, por lo que el orden difiere de FIFO. P4 y P5 llegan juntos en t=3; P2 se bloquea |

También se pueden ingresar procesos a mano con `CargaTrabajo.agregar(...)`.

## Cómo integrar un algoritmo nuevo

1. Crear la clase en `simulador/algoritmos/` heredando de `Planificador`:
   - `seleccionar(listos)` devuelve el próximo proceso de la cola.
   - `apropiativo = True` y `debe_expropiar(en_ejecucion, listos)` si expropia por prioridad o tiempo restante.
   - `quantum` para Round Robin.
2. Registrarla en `ALGORITMOS` (`simulador/algoritmos/__init__.py`).
3. Conectarla en el menú (`simulador/consola.py`).
4. Agregar pruebas en `tests/`.

Contrato del motor: `Simulador(especs, planificador).ejecutar()` y luego `Reportero.informe(sim)`.

## Pruebas

- `tests/test_regresion.py`: FIFO, SJF y SRTF con el caso predefinido (promedios y salida completa).
- `tests/test_motor.py`: espera sin bloqueo, ciclo de estados, métricas, Gantt y quantum.
- `tests/test_carga.py` y `tests/test_casos.py`: validación del ingreso de procesos y de los casos de 10 procesos.
- `tests/test_round_robin.py`, `tests/test_prioridad.py`: esqueletos omitidos hasta integrar los algoritmos.

## Estado de la integración

- [x] FIFO, SJF, SRTF
- [x] Motor con quantum, espera corregida y prioridad en el modelo
- [ ] Round Robin
- [ ] Prioridades
- [ ] Menú final: registrar procesos, configurar quantum, ver última simulación, ayuda

## Decisión de lenguaje

Se eligió Python por su legibilidad: las listas nativas modelan las colas directamente, la
programación orientada a objetos es limpia (`dataclass` inmutable para las especificaciones y
`ABC` para el patrón Strategy), la simulación necesita pocos ticks y solo se usan bibliotecas estándar.
