from queue import Queue

class LineaProduccion:

    def __init__(self):
        self.procesos = []
        self.procesoInicial = None
        self.procesoFinal = None

        self.productosPendientes = Queue()
        self.productosCompletados = []

        self.tiempoGlobal = 0
        self.pausada = False

    def agregarProceso(self, proceso):

        self.procesos.append(proceso)

        if self.procesoInicial is None:
            self.procesoInicial = proceso

        self.procesoFinal = proceso

    def iniciarSimulacion(self):

        self.pausada = False
        print("Simulación iniciada")
        return True

    def pausar(self):

        self.pausada = True
        print("Simulación pausada")

    def reanudar(self):

        self.pausada = False
        print("Simulación reanudada")

    def avanzarCiclo(self):

        if self.pausada:
            print("La simulación está pausada")
            return

        self.tiempoGlobal += 1

        print(f"Ciclo avanzado. Tiempo global: {self.tiempoGlobal}")

    def mostrarEstado(self):

        print("=== Estado Línea Producción ===")
        print(f"Tiempo global: {self.tiempoGlobal}")
        print(f"Cantidad procesos: {len(self.procesos)}")
        print(f"Productos completados: {len(self.productosCompletados)}")

    def reiniciar(self):

        self.tiempoGlobal = 0
        self.productosCompletados = []

        while not self.productosPendientes.empty():
            self.productosPendientes.get()

        print("Sistema reiniciado")
