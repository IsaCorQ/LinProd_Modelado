from queue import Queue

class Tarea:
    def __init__(self, idn, nombre, tiempo_proceso):

        self.idn = idn
        self.nombre = nombre
        self.tiempo_proceso = tiempo_proceso  # TP
        self.tiempo_restante = 0
        self.esta_procesando = False  # EP
        self.contenido_esperando = Queue()  # CE
        self.producto_actual = None

    def agregar_cola(self, producto):
        self.contenido_esperando.put(producto)

    def iniciar_proceso(self):
        if not self.esta_procesando and not self.contenido_esperando.empty():
            self.producto_actual = self.contenido_esperando.get()
            self.esta_procesando = True
            self.tiempo_restante = self.tiempo_proceso
            return True
        return False

    def avanzar_ciclo(self):
        if self.esta_procesando:
            self.tiempo_restante -= 1
            if self.tiempo_restante <= 0:
                return self.finalizar_proceso()
        return None

    def finalizar_proceso(self):
        if self.esta_procesando:
            producto_completado = self.producto_actual
            self.producto_actual = None
            self.esta_procesando = False
            self.tiempo_restante = 0
            return producto_completado
        return None

    def esta_disponible(self):
        return not self.esta_procesando

    def obtener_tamaño_cola(self):
        return self.contenido_esperando.qsize()
        