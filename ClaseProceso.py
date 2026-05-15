from queue import Queue
from ClaseTarea import Tarea


class Proceso:
    def __init__(self, idn, nombre, tareas):
        self.idn = idn
        self.nombre = nombre
        self.tareas = tareas
        self.cola_entrada = Queue()
        self.cola_salida = Queue()
        self.proceso_anterior = None
        self.proceso_siguiente = None
        self.esInicial = False
        self.esFinal = False

    def agregar_producto(self, producto):
        self.cola_entrada.put(producto)

    def obtener_producto_completado(self):
        if not self.cola_salida.empty():
            return self.cola_salida.get()
        return None

    def avanzar_ciclo(self):
        if not self.tareas:
            return
            
        if not self.cola_entrada.empty() and self.tareas[0].esta_disponible():
            producto = self.cola_entrada.get()
            self.tareas[0].agregar_cola(producto)
        for i, tarea in enumerate(self.tareas):
            if tarea.esta_disponible() and tarea.obtener_tamaño_cola() > 0:
                tarea.iniciar_proceso(producto=None)

            producto_completado = tarea.avanzar_ciclo()

            if producto_completado is not None:
                if i < len(self.tareas) - 1:
                    self.tareas[i + 1].agregar_cola(producto_completado)
                else:
                    self.cola_salida.put(producto_completado)

    def obtener_estado(self):
        estado = {
            'id': self.idn,
            'nombre': self.nombre,
            'tareas': []
        }
        for tarea in self.tareas:
            estado['tareas'].append({
                'id': tarea.idn,
                'nombre': tarea.nombre,
                'esta_procesando': tarea.esta_procesando,
                'contenido_esperando': tarea.obtener_tamaño_cola(),
                'tiempo_restante': tarea.tiempo_restante
            })
        return estado

    def agregarTarea(self, tarea):
        """Adds a task to this process"""
        self.tareas.append(tarea)

    def obtenerSiguienteTarea(self):
        """Gets the next available task"""
        for tarea in self.tareas:
            if tarea.esta_disponible():
                return tarea
        return None

    def procesar(self):
        """Process all tasks in this process"""
        for tarea in self.tareas:
            tarea.avanzar_ciclo()

    def calcularCongestion(self):
        """Calculate the congestion level of this process (0-100)"""
        if not self.tareas:
            return 0
        
        total_en_cola = 0
        for tarea in self.tareas:
            total_en_cola += tarea.obtener_tamaño_cola()
            if tarea.esta_procesando:
                total_en_cola += 1
        
        # Congestion is based on average queue size per task
        # Scale from 0-100 where 10+ items per task = 100% congestion
        congestion = min(100, int((total_en_cola / len(self.tareas)) * 10))
        return congestion

    def conectar_siguiente(self, proceso):
        self.proceso_siguiente = proceso
        proceso.proceso_anterior = self
