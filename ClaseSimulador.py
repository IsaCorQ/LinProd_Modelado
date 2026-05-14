class Simulador:
    def __init__(self, linea):
        self.linea = linea
        self.ciclo_actual = 0
        self.activo = False

    def ejecutar(self, ciclos):
        if self.linea.iniciar_simulacion() == False:
            return

        self.activo = True

        for i in range(ciclos):
            if self.activo == False:
                break

            self.avanzar_tiempo()
            self.linea.mostrar_estado()

    def detener(self):
        self.activo = False

    def pausar(self):
        self.linea.pausar()

    def reanudar(self):
        self.linea.reanudar()

    def avanzar_tiempo(self):
        self.ciclo_actual += 1
        print("\nCiclo:", self.ciclo_actual)
        self.linea.avanzar_ciclo()
