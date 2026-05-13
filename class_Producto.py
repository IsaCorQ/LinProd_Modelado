class Producto:
    def __init__(self, id, nombre, tiempo_ingreso=0):
        self.id = id
        self.nombre = nombre
        self.tiempo_ingreso = tiempo_ingreso
        self.tiempo_finalizacion = None
        self.estado = "pendiente"

    def actualizar_estado(self, estado):
        self.estado = estado

    def finalizar(self, tiempo_finalizacion):
        self.tiempo_finalizacion = tiempo_finalizacion
        self.estado = "finalizado"

    def calcular_tiempo_total(self):
        if self.tiempo_finalizacion is None:
            return None
        return self.tiempo_finalizacion - self.tiempo_ingreso

    def __str__(self):
        return f"Producto {self.id}: {self.nombre} - Estado: {self.estado}"

    def __repr__(self):
        return self.__str__()
