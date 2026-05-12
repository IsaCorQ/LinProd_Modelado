from queue import Queue

class Tarea:
    def __init__(self,idn,nombre,tiempo):
        self.idn = idn
        self.nombre = nombre
        self.tiempoProcesamiento = tiempo
        self.tiempoRestante = tiempo
        self.ocupada = False
        self.colaEspera = Queue() #Cola de productos, hay que crear clase
        self.productoAnual = "productoAnual" #Ligar a clase producto

    def iniciar_proceso(self, producto): #help
        print(f"iniciar proceso")
    
    def avanzar_ciclo(self):
        self.tiempoRestante = self.tiempoRestante-1 #checar esto

    def finalizar_proceso(self): #help
        print(f"finalizar proceso")
        proceso = self.colaEspera.get()
        return proceso

    def esta_disponible(self):
        print(f"finalizar proceso")
        return self.ocupada

    def agregar_cola(self, producto):
        self.colaEspera.put(producto)
        