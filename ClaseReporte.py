class Reporte:
    def __init__(self, linea):
        self.linea = linea
        self.tiempo_primer_producto = 0
        self.tiempo_ultimo_producto = 0
        self.tiempo_promedio = 0
        self.cuello_botella = None
        self.promedio_espera = 0

    def generar_reporte(self):
        productos = self.linea.productos_completados

        if len(productos) == 0:
            print("\nNo hay productos completados.")
            return

        self.tiempo_primer_producto = productos[0].tiempo_finalizacion
        self.tiempo_ultimo_producto = productos[-1].tiempo_finalizacion

        suma_tiempos = 0

        for producto in productos:
            suma_tiempos += producto.calcular_tiempo_total()

        self.tiempo_promedio = suma_tiempos / len(productos)

        self.calcular_cuello_botella()
        self.calcular_promedio_espera()

    def calcular_cuello_botella(self):
        mayor_tiempo = 0

        for proceso in self.linea.procesos:
            for tarea in proceso.tareas:
                if tarea.tiempo_proceso > mayor_tiempo:
                    mayor_tiempo = tarea.tiempo_proceso
                    self.cuello_botella = tarea.nombre

    def calcular_promedio_espera(self):
        suma_colas = 0
        cantidad_tareas = 0

        for proceso in self.linea.procesos:
            for tarea in proceso.tareas:
                suma_colas += tarea.obtener_tamaño_cola()
                cantidad_tareas += 1

        if cantidad_tareas > 0:
            self.promedio_espera = suma_colas / cantidad_tareas
        else:
            self.promedio_espera = 0

    def mostrar_estadisticas(self):
        self.generar_reporte()

        print("\n--- REPORTE ---")
        print("Tiempo primer producto:", self.tiempo_primer_producto)
        print("Tiempo último producto:", self.tiempo_ultimo_producto)
        print("Tiempo promedio:", self.tiempo_promedio)
        print("Cuello de botella:", self.cuello_botella)
        print("Promedio de espera:", self.promedio_espera)

    def exportar_pdf(self):
        print("Exportar PDF no implementado.")
