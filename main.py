from simulador.consola import AppConsola

if __name__ == "__main__":
    try:
        AppConsola().ejecutar()
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma interrumpido.")
