import pygame
import sys
from enum import Enum


class SimulationState(Enum):
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2


class Color:
    HEADER_BG = (25, 118, 210)
    SIDEBAR_BG = (255, 255, 255)
    MAIN_BG = (230, 230, 230)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK_GRAY = (80, 80, 80)
    LIGHT_GRAY = (220, 220, 220)
    VERY_LIGHT_GRAY = (245, 245, 245)
    GREEN = (76, 175, 80)
    RED = (244, 67, 54)
    BLUE = (33, 150, 243)
    ORANGE = (255, 152, 0)
    BORDER = (180, 180, 180)
    TEXT_GRAY = (100, 100, 100)


class Button:
    def __init__(self, x, y, width, height, text, color, text_color=Color.WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface, font):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, Color.BORDER, self.rect, 2)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class InputField:
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 30:
                self.text += event.unicode
        return None

    def draw(self, surface, font):
        border_color = Color.BLUE if self.active else Color.BORDER
        pygame.draw.rect(surface, Color.WHITE, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)

        display_text = self.text if self.text else self.placeholder
        text_color = Color.BLACK if self.text else Color.TEXT_GRAY
        text_surf = font.render(display_text, True, text_color)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 8))


class Dropdown:
    def __init__(self, x, y, width, height, options, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected = None
        self.placeholder = placeholder
        self.open = False
        self.max_visible = 3
        self.item_height = 35

    def draw(self, surface, font):
        # Main dropdown box
        pygame.draw.rect(surface, Color.WHITE, self.rect)
        pygame.draw.rect(surface, Color.BORDER, self.rect, 2)

        display_text = self.selected if self.selected else self.placeholder
        text_color = Color.BLACK if self.selected else Color.TEXT_GRAY
        text_surf = font.render(display_text, True, text_color)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 8))

        # Arrow (larger and more visible)
        arrow = "▼"
        arrow_font = pygame.font.Font(None, 22)
        arrow_surf = arrow_font.render(arrow, True, Color.DARK_GRAY)
        surface.blit(arrow_surf, (self.rect.x + self.rect.width - 28, self.rect.y + 6))

        # Dropdown menu when open
        if self.open and self.options:
            dropdown_height = min(len(self.options), self.max_visible) * self.item_height
            dropdown_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height + 2, self.rect.width, dropdown_height)
            
            # Draw dropdown background and border
            pygame.draw.rect(surface, Color.WHITE, dropdown_rect)
            pygame.draw.rect(surface, Color.BORDER, dropdown_rect, 2)

            # Draw options
            for i, option in enumerate(self.options[:self.max_visible]):
                y_pos = dropdown_rect.y + i * self.item_height
                item_rect = pygame.Rect(dropdown_rect.x, y_pos, dropdown_rect.width, self.item_height)
                
                # Highlight on hover
                mouse_pos = pygame.mouse.get_pos()
                if item_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(surface, Color.LIGHT_GRAY, item_rect)
                
                # Draw separator line
                if i < len(self.options[:self.max_visible]) - 1:
                    pygame.draw.line(surface, Color.BORDER, (item_rect.x, item_rect.y + self.item_height), 
                                   (item_rect.x + item_rect.width, item_rect.y + self.item_height), 1)
                
                option_text = font.render(option, True, Color.BLACK)
                surface.blit(option_text, (item_rect.x + 10, item_rect.y + 9))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def get_clicked_option(self, pos):
        if not self.open or not self.options:
            return None
        
        dropdown_height = min(len(self.options), self.max_visible) * self.item_height
        dropdown_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height + 2, self.rect.width, dropdown_height)
        
        if not dropdown_rect.collidepoint(pos):
            return None
        
        relative_y = pos[1] - dropdown_rect.y
        item_index = relative_y // self.item_height
        
        if 0 <= item_index < len(self.options):
            return self.options[item_index]
        
        return None

    def select(self, option):
        self.selected = option
        self.open = False

    def toggle(self):
        self.open = not self.open


class GUIManager:
    def __init__(self, width=1200, height=750):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sistema de Simulación de Producción")

        self.font_title = pygame.font.Font(None, 28)
        self.font_normal = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 16)
        self.font_large = pygame.font.Font(None, 36)
        self.font_arrow = pygame.font.Font(None, 24)

        self.state = SimulationState.STOPPED
        self.tiempo_global = 0
        self.velocidad = 1

        self.init_ui()

    def init_ui(self):
        self.btn_iniciar = Button(420, 10, 85, 35, "INICIAR", Color.GREEN)
        self.btn_pausar = Button(515, 10, 85, 35, "PAUSAR", Color.DARK_GRAY)
        self.btn_reiniciar = Button(610, 10, 85, 35, "REINICIAR", Color.RED)
        self.btn_reporte = Button(705, 10, 85, 35, "REPORTE", Color.BLUE)

        self.crear_proceso_expanded = False
        self.agregar_tarea_expanded = False
        self.conectar_procesos_expanded = False

        self.input_proceso_name = InputField(20, 140, 220, 35, "Nombre del proceso")
        self.checkbox_inicial = False
        self.checkbox_final = False
        self.btn_crear_proceso = Button(20, 220, 220, 35, "+ CREAR PROCESO", Color.LIGHT_GRAY, Color.DARK_GRAY)

        # Dynamic lists for dropdowns (empty, will be populated from simulator)
        self.procesos_list = []
        self.tareas_list = {}
        
        self.dropdown_proceso_tarea = Dropdown(20, 320, 220, 35, self.procesos_list, "Proceso")
        self.input_tarea_name = InputField(20, 365, 220, 35, "Nombre de tarea")
        self.input_tiempo_proceso = InputField(20, 410, 220, 35, "Tiempo procesamiento")
        self.input_orden = InputField(20, 455, 220, 35, "Orden")
        self.btn_agregar_tarea = Button(20, 500, 220, 35, "+ AGREGAR TAREA", Color.LIGHT_GRAY, Color.DARK_GRAY)

        self.dropdown_desde = Dropdown(20, 580, 220, 35, self.procesos_list, "Desde")
        self.dropdown_hacia = Dropdown(20, 625, 220, 35, self.procesos_list, "Hacia")
        self.btn_conectar = Button(20, 670, 220, 35, "CONECTAR", Color.LIGHT_GRAY, Color.DARK_GRAY)

    def draw_header(self):
        pygame.draw.rect(self.screen, Color.HEADER_BG, (0, 0, self.width, 50))
        title = self.font_title.render("Sistema de Simulación de Producción", True, Color.WHITE)
        self.screen.blit(title, (15, 12))

        self.btn_iniciar.draw(self.screen, self.font_small)
        self.btn_pausar.draw(self.screen, self.font_small)
        self.btn_reiniciar.draw(self.screen, self.font_small)
        self.btn_reporte.draw(self.screen, self.font_small)

    def draw_sidebar_left(self):
        pygame.draw.rect(self.screen, Color.SIDEBAR_BG, (0, 60, 260, self.height - 80))
        pygame.draw.line(self.screen, Color.BORDER, (260, 60), (260, self.height - 40), 2)

        titulo = self.font_title.render("Configuración", True, Color.BLACK)
        self.screen.blit(titulo, (20, 75))

        y = 120
        self._draw_section("Crear Proceso", y, self.crear_proceso_expanded, self._draw_crear_proceso)
        
        if self.crear_proceso_expanded:
            y += 35 + 110
        else:
            y += 25

        self._draw_section("Agregar Tarea", y, self.agregar_tarea_expanded, self._draw_agregar_tarea)
        
        if self.agregar_tarea_expanded:
            y += 35 + 190
        else:
            y += 25

        self._draw_section("Conectar Procesos", y, self.conectar_procesos_expanded, self._draw_conectar)
        
        if self.conectar_procesos_expanded:
            y += 35 + 120
        else:
            y += 25

        y += 20
        titulo_procesos = self.font_normal.render("Procesos Creados", True, Color.BLACK)
        self.screen.blit(titulo_procesos, (20, y))
        
        for i, proceso in enumerate(self.procesos_list):
            texto = self.font_small.render(f"• {proceso}", True, Color.DARK_GRAY)
            self.screen.blit(texto, (30, y + 30 + i * 20))

    def _draw_section(self, title, y, expanded, draw_func):
        arrow = "▼" if expanded else "▶"
        arrow_text = self.font_arrow.render(arrow, True, Color.BLUE)
        self.screen.blit(arrow_text, (10, y - 3))
        
        title_text = self.font_normal.render(title, True, Color.BLACK)
        self.screen.blit(title_text, (35, y))
        
        pygame.draw.line(self.screen, Color.BORDER, (15, y + 22), (235, y + 22), 1)

        if expanded:
            draw_func(y + 35)

    def _draw_crear_proceso(self, y):
        self.input_proceso_name.rect.y = y
        self.input_proceso_name.draw(self.screen, self.font_small)
        
        check_y = y + 50
        pygame.draw.rect(self.screen, Color.BORDER, (20, check_y, 18, 18), 2)
        if self.checkbox_inicial:
            pygame.draw.rect(self.screen, Color.BLUE, (20, check_y, 18, 18))
            pygame.draw.line(self.screen, Color.WHITE, (23, check_y+10), (26, check_y+14), 2)
            pygame.draw.line(self.screen, Color.WHITE, (26, check_y+6), (32, check_y+15), 2)
        check_label = self.font_small.render("¿Es inicial?", True, Color.BLACK)
        self.screen.blit(check_label, (45, check_y))

        check_y2 = y + 75
        pygame.draw.rect(self.screen, Color.BORDER, (20, check_y2, 18, 18), 2)
        if self.checkbox_final:
            pygame.draw.rect(self.screen, Color.BLUE, (20, check_y2, 18, 18))
            pygame.draw.line(self.screen, Color.WHITE, (23, check_y2+10), (26, check_y2+14), 2)
            pygame.draw.line(self.screen, Color.WHITE, (26, check_y2+6), (32, check_y2+15), 2)
        check_label2 = self.font_small.render("¿Es final?", True, Color.BLACK)
        self.screen.blit(check_label2, (45, check_y2))

        self.btn_crear_proceso.rect.y = y + 85
        self.btn_crear_proceso.draw(self.screen, self.font_small)

    def _draw_agregar_tarea(self, y):
        self.dropdown_proceso_tarea.rect.y = y
        self.dropdown_proceso_tarea.draw(self.screen, self.font_small)
        
        self.input_tarea_name.rect.y = y + 45
        self.input_tarea_name.draw(self.screen, self.font_small)
        
        self.input_tiempo_proceso.rect.y = y + 90
        self.input_tiempo_proceso.draw(self.screen, self.font_small)
        
        self.input_orden.rect.y = y + 135
        self.input_orden.draw(self.screen, self.font_small)
        
        self.btn_agregar_tarea.rect.y = y + 145
        self.btn_agregar_tarea.draw(self.screen, self.font_small)

    def _draw_conectar(self, y):
        self.dropdown_desde.rect.y = y
        self.dropdown_desde.draw(self.screen, self.font_small)
        
        self.dropdown_hacia.rect.y = y + 45
        self.dropdown_hacia.draw(self.screen, self.font_small)
        
        self.btn_conectar.rect.y = y + 55
        self.btn_conectar.draw(self.screen, self.font_small)

    def draw_main_area(self):
        pygame.draw.rect(self.screen, Color.MAIN_BG, (260, 60, 640, self.height - 80))
        pygame.draw.rect(self.screen, Color.WHITE, (280, 80, 600, 280), 2)
        texto = self.font_normal.render("Visualización de Procesos", True, Color.TEXT_GRAY)
        text_rect = texto.get_rect(center=(580, 220))
        self.screen.blit(texto, text_rect)

    def draw_sidebar_right(self):
        pygame.draw.rect(self.screen, Color.SIDEBAR_BG, (900, 60, 300, self.height - 80))
        pygame.draw.line(self.screen, Color.BORDER, (900, 60), (900, self.height - 40), 2)

        y_pos = 80
        stats = [
            ("En Proceso Activo", "0", Color.BLUE),
            ("Tiempo Promedio por Producto", "0 ciclos", Color.BLACK),
            ("Cuello de Botella", "No detectado", Color.RED),
        ]

        for i, (label, value, color) in enumerate(stats):
            label_text = self.font_small.render(label, True, Color.DARK_GRAY)
            self.screen.blit(label_text, (920, y_pos + i * 100))
            value_text = self.font_normal.render(value, True, color)
            self.screen.blit(value_text, (920, y_pos + 25 + i * 100))

        y_tareas = 410
        titulo_tareas = self.font_small.render("Tareas por Estado", True, Color.BLACK)
        self.screen.blit(titulo_tareas, (920, y_tareas))

        estados = [("Libres", "1", Color.GREEN), ("Ocupadas", "0", Color.ORANGE), ("Saturadas", "0", Color.RED)]
        for i, (label, value, color) in enumerate(estados):
            pygame.draw.rect(self.screen, color, (920, y_tareas + 30 + i * 24, 65, 20))
            label_text = self.font_small.render(label, True, Color.WHITE)
            self.screen.blit(label_text, (925, y_tareas + 32 + i * 24))
            value_text = self.font_small.render(value, True, Color.BLACK)
            self.screen.blit(value_text, (995, y_tareas + 32 + i * 24))

        y_velocidad = 570
        velocidad_text = self.font_small.render("Velocidad de Simulación", True, Color.BLACK)
        self.screen.blit(velocidad_text, (920, y_velocidad))

        pygame.draw.line(self.screen, Color.BORDER, (920, y_velocidad + 30), (1070, y_velocidad + 30), 2)
        pygame.draw.circle(self.screen, Color.BLUE, (950, y_velocidad + 30), 8)

        vel_labels = ["x1", "x2", "x3", "x4", "x5"]
        for i, label in enumerate(vel_labels):
            vel_text = self.font_small.render(label, True, Color.DARK_GRAY)
            self.screen.blit(vel_text, (920 + i * 30, y_velocidad + 45))

    def draw_statusbar(self):
        pygame.draw.rect(self.screen, Color.DARK_GRAY, (0, self.height - 40, self.width, 40))

        estado_text = self.font_small.render(f"Estado: {self.state.name}", True, Color.WHITE)
        tiempo_text = self.font_small.render(f"Tiempo global: {self.tiempo_global} ciclos", True, Color.WHITE)
        velocidad_text = self.font_small.render(f"Velocidad: x{self.velocidad}", True, Color.WHITE)

        self.screen.blit(estado_text, (15, self.height - 32))
        self.screen.blit(tiempo_text, (320, self.height - 32))
        self.screen.blit(velocidad_text, (self.width - 130, self.height - 32))

    def draw(self):
        self.screen.fill(Color.VERY_LIGHT_GRAY)
        self.draw_header()
        self.draw_sidebar_left()
        self.draw_main_area()
        self.draw_sidebar_right()
        self.draw_statusbar()
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_iniciar.is_clicked(event.pos):
                    self.state = SimulationState.RUNNING
                elif self.btn_pausar.is_clicked(event.pos):
                    self.state = SimulationState.PAUSED
                elif self.btn_reiniciar.is_clicked(event.pos):
                    self.state = SimulationState.STOPPED
                    self.tiempo_global = 0

                # Section toggles
                elif 15 < event.pos[0] < 35 and 115 < event.pos[1] < 140:
                    self.crear_proceso_expanded = not self.crear_proceso_expanded
                elif 15 < event.pos[0] < 35:
                    y1 = 115 + 30 + (120 if self.crear_proceso_expanded else 0)
                    if y1 < event.pos[1] < y1 + 25:
                        self.agregar_tarea_expanded = not self.agregar_tarea_expanded
                    
                    y2 = y1 + 30 + (200 if self.agregar_tarea_expanded else 0)
                    if y2 < event.pos[1] < y2 + 25:
                        self.conectar_procesos_expanded = not self.conectar_procesos_expanded

                # Checkboxes
                elif 20 < event.pos[0] < 38:
                    check_y = 115 + 35 + 50
                    if self.crear_proceso_expanded and check_y < event.pos[1] < check_y + 18:
                        self.checkbox_inicial = not self.checkbox_inicial
                        if self.checkbox_inicial:
                            self.checkbox_final = False
                    
                    check_y2 = 115 + 35 + 75
                    if self.crear_proceso_expanded and check_y2 < event.pos[1] < check_y2 + 18:
                        self.checkbox_final = not self.checkbox_final
                        if self.checkbox_final:
                            self.checkbox_inicial = False

                # Dropdowns
                if self.dropdown_proceso_tarea.is_clicked(event.pos):
                    self.dropdown_proceso_tarea.toggle()
                elif self.dropdown_proceso_tarea.open:
                    option = self.dropdown_proceso_tarea.get_clicked_option(event.pos)
                    if option:
                        self.dropdown_proceso_tarea.select(option)

                if self.dropdown_desde.is_clicked(event.pos):
                    self.dropdown_desde.toggle()
                elif self.dropdown_desde.open:
                    option = self.dropdown_desde.get_clicked_option(event.pos)
                    if option:
                        self.dropdown_desde.select(option)

                if self.dropdown_hacia.is_clicked(event.pos):
                    self.dropdown_hacia.toggle()
                elif self.dropdown_hacia.open:
                    option = self.dropdown_hacia.get_clicked_option(event.pos)
                    if option:
                        self.dropdown_hacia.select(option)

                # Buttons
                if self.btn_crear_proceso.is_clicked(event.pos):
                    if self.input_proceso_name.text:
                        self.procesos_list.append(self.input_proceso_name.text)
                        self.input_proceso_name.text = ""
                elif self.btn_agregar_tarea.is_clicked(event.pos):
                    if self.input_tarea_name.text:
                        self.tareas_list[self.input_tarea_name.text] = {
                            "proceso": self.dropdown_proceso_tarea.selected,
                            "tiempo": self.input_tiempo_proceso.text,
                            "orden": self.input_orden.text
                        }
                        self.input_tarea_name.text = ""

            self.input_proceso_name.handle_event(event)
            self.input_tarea_name.handle_event(event)
            self.input_tiempo_proceso.handle_event(event)
            self.input_orden.handle_event(event)

        return True

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            running = self.handle_events()

            if self.state == SimulationState.RUNNING:
                self.tiempo_global += 1

            self.draw()
            clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    gui = GUIManager()
    gui.run()
