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
    CARD_GREEN = (76, 175, 80)
    CARD_GREEN_DARK = (46, 125, 50)
    CARD_GREEN_LIGHT = (233, 245, 234)


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
        self.max_visible = 4
        self.item_height = 35
        self.scroll_offset = 0

    def _draw_arrow(self, surface, open_state):
        cx = self.rect.right - 18
        cy = self.rect.centery
        if open_state:
            points = [(cx - 6, cy + 3), (cx + 6, cy + 3), (cx, cy - 4)]
        else:
            points = [(cx - 6, cy - 3), (cx + 6, cy - 3), (cx, cy + 4)]
        pygame.draw.polygon(surface, Color.DARK_GRAY, points)

    def get_dropdown_rect(self):
        dropdown_height = min(len(self.options), self.max_visible) * self.item_height
        return pygame.Rect(self.rect.x, self.rect.y + self.rect.height + 2, self.rect.width, dropdown_height)

    def handle_wheel(self, mouse_pos, wheel_y):
        if not self.open or len(self.options) <= self.max_visible:
            return False

        dropdown_rect = self.get_dropdown_rect()
        if not (self.rect.collidepoint(mouse_pos) or dropdown_rect.collidepoint(mouse_pos)):
            return False

        max_offset = len(self.options) - self.max_visible
        self.scroll_offset = max(0, min(max_offset, self.scroll_offset - wheel_y))
        return True

    def draw(self, surface, font):
        # Main dropdown box
        pygame.draw.rect(surface, Color.WHITE, self.rect)
        pygame.draw.rect(surface, Color.BORDER, self.rect, 2)

        display_text = self.selected if self.selected else self.placeholder
        text_color = Color.BLACK if self.selected else Color.TEXT_GRAY
        text_surf = font.render(display_text, True, text_color)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 8))

        # Arrow drawn as polygon to avoid missing-glyph squares.
        self._draw_arrow(surface, self.open)

        # Dropdown menu when open
        if self.open and self.options:
            dropdown_rect = self.get_dropdown_rect()
            
            # Draw dropdown background and border
            pygame.draw.rect(surface, Color.WHITE, dropdown_rect)
            pygame.draw.rect(surface, Color.BORDER, dropdown_rect, 2)

            # Draw options
            visible_options = self.options[self.scroll_offset:self.scroll_offset + self.max_visible]
            for i, option in enumerate(visible_options):
                y_pos = dropdown_rect.y + i * self.item_height
                item_rect = pygame.Rect(dropdown_rect.x, y_pos, dropdown_rect.width, self.item_height)
                
                # Highlight on hover
                mouse_pos = pygame.mouse.get_pos()
                if item_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(surface, Color.LIGHT_GRAY, item_rect)
                
                # Draw separator line
                if i < len(visible_options) - 1:
                    pygame.draw.line(surface, Color.BORDER, (item_rect.x, item_rect.y + self.item_height), 
                                   (item_rect.x + item_rect.width, item_rect.y + self.item_height), 1)
                
                option_text = font.render(option, True, Color.BLACK)
                surface.blit(option_text, (item_rect.x + 10, item_rect.y + 9))

            # Scrollbar for long lists.
            if len(self.options) > self.max_visible:
                track_rect = pygame.Rect(dropdown_rect.right - 7, dropdown_rect.y + 2, 5, dropdown_rect.height - 4)
                pygame.draw.rect(surface, Color.LIGHT_GRAY, track_rect)

                thumb_height = max(16, int(track_rect.height * (self.max_visible / len(self.options))))
                max_offset = len(self.options) - self.max_visible
                ratio = 0 if max_offset == 0 else (self.scroll_offset / max_offset)
                thumb_y = track_rect.y + int((track_rect.height - thumb_height) * ratio)
                pygame.draw.rect(surface, Color.DARK_GRAY, (track_rect.x, thumb_y, track_rect.width, thumb_height))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def get_clicked_option(self, pos):
        if not self.open or not self.options:
            return None

        dropdown_rect = self.get_dropdown_rect()
        
        if not dropdown_rect.collidepoint(pos):
            return None
        
        relative_y = pos[1] - dropdown_rect.y
        item_index = relative_y // self.item_height
        
        option_index = self.scroll_offset + item_index
        if 0 <= option_index < len(self.options):
            return self.options[option_index]
        
        return None

    def select(self, option):
        self.selected = option
        self.open = False

    def toggle(self):
        self.open = not self.open
        if self.open:
            self.scroll_offset = 0


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
        self.btn_crear_producto = Button(1025, 10, 165, 35, "CREAR PRODUCTOS", Color.ORANGE)
        self.input_cantidad_producto = InputField(965, 10, 55, 35, "Cant")

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

        self.products_count = 0
        self.process_products = {}
        self.process_meta = {}
        self.process_connections = {}
        self.sidebar_scroll = 0
        self.main_scroll_x = 0
        self.main_max_scroll = 0
        self.main_scroll_track_rect = None
        self.main_scroll_thumb_rect = None
        self.main_scroll_dragging = False
        self.main_scroll_drag_offset = 0

    def _left_sy(self, y):
        return y - self.sidebar_scroll

    def _left_panel_rect(self):
        return pygame.Rect(0, 60, 260, self.height - 100)

    def _main_panel_rect(self):
        return pygame.Rect(280, 80, 600, self.height - 140)

    def _left_content_bottom(self):
        layout = self._get_sidebar_layout()
        y = layout["procesos_title_y"]
        return y + 30 + len(self.procesos_list) * 20 + 20

    def _max_sidebar_scroll(self):
        panel_bottom = self.height - 40
        overflow = self._left_content_bottom() - panel_bottom
        return max(0, overflow + 10)

    def _scroll_sidebar(self, wheel_y):
        self.sidebar_scroll = max(0, min(self._max_sidebar_scroll(), self.sidebar_scroll - wheel_y * 24))

    def _create_products(self, qty):
        if qty <= 0:
            return
        self.products_count += qty
        if self.procesos_list:
            process_order = self._get_display_process_order()
            first_process = process_order[0] if process_order else self.procesos_list[0]
            self.process_products[first_process] = self.process_products.get(first_process, 0) + qty

    def _get_display_process_order(self):
        if not self.procesos_list:
            return []

        ordered = []
        visited = set()
        valid_nodes = set(self.procesos_list)

        next_map = {}
        indegree = {p: 0 for p in self.procesos_list}
        for src, dst in self.process_connections.items():
            if src in valid_nodes and dst in valid_nodes and src != dst:
                next_map[src] = dst
                indegree[dst] += 1

        starts = [p for p in self.procesos_list if indegree[p] == 0]
        for start in starts:
            cur = start
            while cur and cur not in visited:
                ordered.append(cur)
                visited.add(cur)
                cur = next_map.get(cur)

        for process_name in self.procesos_list:
            cur = process_name
            while cur and cur not in visited:
                ordered.append(cur)
                visited.add(cur)
                cur = next_map.get(cur)

        return ordered

    def _draw_process_pipe(self, src_rect, dst_rect):
        color = (83, 138, 201)
        thickness = 5
        start = (src_rect.right + 2, src_rect.centery)
        end = (dst_rect.left - 2, dst_rect.centery)

        # Use a simple horizontal connector when possible to keep the path clean.
        if abs(start[1] - end[1]) <= 8:
            pygame.draw.line(self.screen, color, start, end, thickness)
        else:
            mid_x = (start[0] + end[0]) // 2
            p1 = start
            p2 = (mid_x, start[1])
            p3 = (mid_x, end[1])
            p4 = end
            pygame.draw.line(self.screen, color, p1, p2, thickness)
            pygame.draw.line(self.screen, color, p2, p3, thickness)
            pygame.draw.line(self.screen, color, p3, p4, thickness)
            pygame.draw.circle(self.screen, color, p2, 4)
            pygame.draw.circle(self.screen, color, p3, 4)

        # Arrow tip on destination side.
        arrow = [(end[0], end[1]), (end[0] - 10, end[1] - 6), (end[0] - 10, end[1] + 6)]
        pygame.draw.polygon(self.screen, color, arrow)

    def _dropdown_extra_height(self, dropdown):
        if dropdown.open and dropdown.options:
            return dropdown.get_dropdown_rect().height + 2
        return 0

    def _get_sidebar_layout(self):
        section_gap = 14
        y = 120
        crear_y = y
        # Expanded height must match actual drawn controls in each section.
        y += (35 + 153 + section_gap) if self.crear_proceso_expanded else 32

        agregar_y = y
        agregar_extra = self._dropdown_extra_height(self.dropdown_proceso_tarea) if self.agregar_tarea_expanded else 0
        y += (35 + 215 + section_gap + agregar_extra) if self.agregar_tarea_expanded else 32

        conectar_y = y
        conectar_extra_desde = self._dropdown_extra_height(self.dropdown_desde) if self.conectar_procesos_expanded else 0
        conectar_extra_hacia = self._dropdown_extra_height(self.dropdown_hacia) if self.conectar_procesos_expanded else 0
        y += (35 + 125 + section_gap + conectar_extra_desde + conectar_extra_hacia) if self.conectar_procesos_expanded else 32

        return {
            "crear_y": crear_y,
            "agregar_y": agregar_y,
            "conectar_y": conectar_y,
            "agregar_extra": agregar_extra,
            "conectar_extra_desde": conectar_extra_desde,
            "conectar_extra_hacia": conectar_extra_hacia,
            "procesos_title_y": y + 20,
        }

    def _draw_disclosure_arrow(self, x, y, expanded):
        if expanded:
            points = [(x, y), (x + 10, y), (x + 5, y + 8)]
        else:
            points = [(x, y), (x + 8, y + 5), (x, y + 10)]
        pygame.draw.polygon(self.screen, Color.BLUE, points)

    def _tasks_for_process(self, process_name):
        tasks = []
        for name, data in self.tareas_list.items():
            if data.get("proceso") == process_name:
                try:
                    order = int(data.get("orden", "9999") or "9999")
                except ValueError:
                    order = 9999
                tasks.append((order, name, data.get("tiempo", "")))
        tasks.sort(key=lambda item: item[0])
        return tasks

    def draw_header(self):
        pygame.draw.rect(self.screen, Color.HEADER_BG, (0, 0, self.width, 50))
        title = self.font_title.render("Sistema de Simulación de Producción", True, Color.WHITE)
        self.screen.blit(title, (15, 12))

        self.btn_iniciar.draw(self.screen, self.font_small)
        self.btn_pausar.draw(self.screen, self.font_small)
        self.btn_reiniciar.draw(self.screen, self.font_small)
        self.btn_reporte.draw(self.screen, self.font_small)

        self.input_cantidad_producto.draw(self.screen, self.font_small)
        self.btn_crear_producto.draw(self.screen, self.font_small)

    def draw_sidebar_left(self):
        panel_rect = self._left_panel_rect()
        pygame.draw.rect(self.screen, Color.SIDEBAR_BG, (0, 60, 260, self.height - 80))
        pygame.draw.line(self.screen, Color.BORDER, (260, 60), (260, self.height - 40), 2)

        old_clip = self.screen.get_clip()
        self.screen.set_clip(panel_rect)

        titulo = self.font_title.render("Configuración", True, Color.BLACK)
        self.screen.blit(titulo, (20, self._left_sy(75)))

        layout = self._get_sidebar_layout()
        self._draw_section("Crear Proceso", layout["crear_y"], self.crear_proceso_expanded, self._draw_crear_proceso)
        self._draw_section("Agregar Tarea", layout["agregar_y"], self.agregar_tarea_expanded, self._draw_agregar_tarea)
        self._draw_section("Conectar Procesos", layout["conectar_y"], self.conectar_procesos_expanded, self._draw_conectar)

        y = layout["procesos_title_y"]
        titulo_procesos = self.font_normal.render("Procesos Creados", True, Color.BLACK)
        self.screen.blit(titulo_procesos, (20, self._left_sy(y)))
        
        process_order = self._get_display_process_order()
        for i, proceso in enumerate(process_order):
            texto = self.font_small.render(f"• {proceso}", True, Color.DARK_GRAY)
            self.screen.blit(texto, (30, self._left_sy(y + 30 + i * 20)))

        self.screen.set_clip(old_clip)

        max_scroll = self._max_sidebar_scroll()
        if max_scroll > 0:
            track = pygame.Rect(250, 70, 6, self.height - 120)
            pygame.draw.rect(self.screen, Color.LIGHT_GRAY, track)
            thumb_h = max(30, int(track.height * (track.height / (track.height + max_scroll))))
            ratio = self.sidebar_scroll / max_scroll
            thumb_y = track.y + int((track.height - thumb_h) * ratio)
            pygame.draw.rect(self.screen, Color.DARK_GRAY, (track.x, thumb_y, track.width, thumb_h))

    def _draw_section(self, title, y, expanded, draw_func):
        sy = self._left_sy(y)
        self._draw_disclosure_arrow(12, sy + 4, expanded)
        
        title_text = self.font_normal.render(title, True, Color.BLACK)
        self.screen.blit(title_text, (35, sy))
        
        pygame.draw.line(self.screen, Color.BORDER, (15, sy + 22), (235, sy + 22), 1)

        if expanded:
            draw_func(y + 35)

    def _draw_crear_proceso(self, y):
        self.input_proceso_name.rect.y = self._left_sy(y)
        self.input_proceso_name.draw(self.screen, self.font_small)
        
        check_y = self._left_sy(y + 54)
        pygame.draw.rect(self.screen, Color.BORDER, (20, check_y, 18, 18), 2)
        if self.checkbox_inicial:
            pygame.draw.rect(self.screen, Color.BLUE, (20, check_y, 18, 18))
            pygame.draw.line(self.screen, Color.WHITE, (23, check_y+10), (26, check_y+14), 2)
            pygame.draw.line(self.screen, Color.WHITE, (26, check_y+6), (32, check_y+15), 2)
        check_label = self.font_small.render("¿Es inicial?", True, Color.BLACK)
        self.screen.blit(check_label, (45, check_y))

        check_y2 = self._left_sy(y + 84)
        pygame.draw.rect(self.screen, Color.BORDER, (20, check_y2, 18, 18), 2)
        if self.checkbox_final:
            pygame.draw.rect(self.screen, Color.BLUE, (20, check_y2, 18, 18))
            pygame.draw.line(self.screen, Color.WHITE, (23, check_y2+10), (26, check_y2+14), 2)
            pygame.draw.line(self.screen, Color.WHITE, (26, check_y2+6), (32, check_y2+15), 2)
        check_label2 = self.font_small.render("¿Es final?", True, Color.BLACK)
        self.screen.blit(check_label2, (45, check_y2))

        self.btn_crear_proceso.rect.y = self._left_sy(y + 118)
        self.btn_crear_proceso.draw(self.screen, self.font_small)

    def _draw_agregar_tarea(self, y):
        dropdown_extra = self._dropdown_extra_height(self.dropdown_proceso_tarea)
        self.dropdown_proceso_tarea.rect.y = self._left_sy(y)
        self.dropdown_proceso_tarea.draw(self.screen, self.font_small)
        
        self.input_tarea_name.rect.y = self._left_sy(y + 45 + dropdown_extra)
        self.input_tarea_name.draw(self.screen, self.font_small)
        
        self.input_tiempo_proceso.rect.y = self._left_sy(y + 90 + dropdown_extra)
        self.input_tiempo_proceso.draw(self.screen, self.font_small)
        
        self.input_orden.rect.y = self._left_sy(y + 135 + dropdown_extra)
        self.input_orden.draw(self.screen, self.font_small)
        
        self.btn_agregar_tarea.rect.y = self._left_sy(y + 180 + dropdown_extra)
        self.btn_agregar_tarea.draw(self.screen, self.font_small)

    def _draw_conectar(self, y):
        extra_desde = self._dropdown_extra_height(self.dropdown_desde)
        y_hacia = y + 45 + extra_desde
        extra_hacia = self._dropdown_extra_height(self.dropdown_hacia)
        y_btn = y_hacia + 45 + extra_hacia

        self.dropdown_desde.rect.y = self._left_sy(y)
        self.dropdown_desde.draw(self.screen, self.font_small)
        
        self.dropdown_hacia.rect.y = self._left_sy(y_hacia)
        self.dropdown_hacia.draw(self.screen, self.font_small)
        
        self.btn_conectar.rect.y = self._left_sy(y_btn)
        self.btn_conectar.draw(self.screen, self.font_small)

    def draw_main_area(self):
        pygame.draw.rect(self.screen, Color.MAIN_BG, (260, 60, 640, self.height - 80))
        panel_rect = self._main_panel_rect()
        pygame.draw.rect(self.screen, Color.WHITE, panel_rect, 2)

        title = self.font_normal.render("Visualizacion de Procesos", True, Color.TEXT_GRAY)
        self.screen.blit(title, (300, 95))

        if not self.procesos_list:
            texto = self.font_normal.render("Crea un proceso para comenzar", True, Color.TEXT_GRAY)
            text_rect = texto.get_rect(center=(580, 220))
            self.screen.blit(texto, text_rect)
            products_base_y = 380
            self.main_scroll_x = 0
            self.main_max_scroll = 0
            self.main_scroll_track_rect = None
            self.main_scroll_thumb_rect = None
        else:
            process_order = self._get_display_process_order()
            card_w = 285
            card_h = 282
            col_gap = 22
            lane_left = panel_rect.x + 12
            start_y = 115
            lane_w = len(process_order) * card_w + max(0, len(process_order) - 1) * col_gap
            viewport_w = panel_rect.width - 24
            self.main_max_scroll = max(0, lane_w - viewport_w)
            self.main_scroll_x = max(0, min(self.main_max_scroll, self.main_scroll_x))

            old_clip = self.screen.get_clip()
            self.screen.set_clip(pygame.Rect(panel_rect.x + 2, panel_rect.y + 2, panel_rect.width - 4, panel_rect.height - 4))
            card_rects = {}

            for i, proceso in enumerate(process_order):
                x = lane_left + i * (card_w + col_gap) - self.main_scroll_x
                y = start_y
                card_rect = pygame.Rect(x, y, card_w, card_h)
                card_rects[proceso] = card_rect

                pygame.draw.rect(self.screen, Color.CARD_GREEN_LIGHT, card_rect, border_radius=4)
                pygame.draw.rect(self.screen, Color.CARD_GREEN, card_rect, 2, border_radius=4)

                title_text = self.font_title.render(proceso, True, Color.BLACK)
                self.screen.blit(title_text, (x + 18, y + 14))

                meta = self.process_meta.get(proceso, {"inicial": False, "final": False})
                if meta.get("inicial"):
                    init_rect = pygame.Rect(x + 18, y + 48, 62, 28)
                    pygame.draw.rect(self.screen, Color.CARD_GREEN_DARK, init_rect, border_radius=14)
                    init_text = self.font_normal.render("Inicial", True, Color.WHITE)
                    self.screen.blit(init_text, (x + 26, y + 55))
                elif meta.get("final"):
                    final_rect = pygame.Rect(x + 18, y + 48, 54, 28)
                    pygame.draw.rect(self.screen, Color.ORANGE, final_rect, border_radius=14)
                    final_text = self.font_normal.render("Final", True, Color.WHITE)
                    self.screen.blit(final_text, (x + 27, y + 55))

                tasks = self._tasks_for_process(proceso)
                if tasks:
                    order, task_name, tiempo = tasks[0]
                    task_rect = pygame.Rect(x + 18, y + 88, card_w - 36, 160)
                    pygame.draw.rect(self.screen, (207, 214, 210), task_rect, border_radius=4)
                    pygame.draw.rect(self.screen, Color.CARD_GREEN, task_rect, 2, border_radius=4)

                    pygame.draw.circle(self.screen, Color.CARD_GREEN, (x + 50, y + 126), 9)
                    task_title = self.font_title.render(task_name, True, (30, 30, 30))
                    self.screen.blit(task_title, (x + 70, y + 116))

                    estado_label = self.font_normal.render("Estado:", True, (90, 90, 90))
                    self.screen.blit(estado_label, (x + 40, y + 156))
                    libre_rect = pygame.Rect(x + 98, y + 148, 62, 28)
                    pygame.draw.rect(self.screen, Color.CARD_GREEN, libre_rect, border_radius=14)
                    libre_text = self.font_normal.render("Libre", True, Color.WHITE)
                    self.screen.blit(libre_text, (x + 109, y + 155))

                    fifo_rect = pygame.Rect(x + 40, y + 186, card_w - 78, 50)
                    pygame.draw.rect(self.screen, (220, 224, 221), fifo_rect, border_radius=4)
                    pygame.draw.rect(self.screen, (190, 194, 191), fifo_rect, 1, border_radius=4)
                    fifo_label = self.font_normal.render("Cola FIFO:", True, (85, 85, 85))
                    self.screen.blit(fifo_label, (x + 50, y + 190))

                    cola = self.process_products.get(proceso, 0)
                    fifo_count = self.font_title.render(str(cola), True, (35, 35, 35))
                    self.screen.blit(fifo_count, (x + 50, y + 206))
                    fifo_text = self.font_normal.render("producto(s) en espera", True, (85, 85, 85))
                    self.screen.blit(fifo_text, (x + 74, y + 212))

                    foot_text = self.font_normal.render(f"Orden: {order} | Tiempo: {tiempo} ciclos", True, (90, 90, 90))
                    self.screen.blit(foot_text, (x + 40, y + 258))

                    if len(tasks) > 1:
                        more_tasks = self.font_small.render(f"+{len(tasks) - 1} tarea(s) mas", True, Color.TEXT_GRAY)
                        self.screen.blit(more_tasks, (x + card_w - 120, y + 66))
                else:
                    empty_text = self.font_normal.render("Sin tareas", True, Color.TEXT_GRAY)
                    self.screen.blit(empty_text, (x + 18, y + 98))

            for src_name, dst_name in self.process_connections.items():
                if src_name in card_rects and dst_name in card_rects:
                    self._draw_process_pipe(card_rects[src_name], card_rects[dst_name])

            self.screen.set_clip(old_clip)
            cards_bottom = start_y + card_h
            products_base_y = max(380, cards_bottom + 24)

            if self.main_max_scroll > 0:
                track = pygame.Rect(panel_rect.x + 14, panel_rect.bottom - 16, panel_rect.width - 28, 6)
                pygame.draw.rect(self.screen, Color.LIGHT_GRAY, track)
                thumb_w = max(40, int(track.width * (viewport_w / lane_w)))
                ratio = self.main_scroll_x / self.main_max_scroll if self.main_max_scroll else 0
                thumb_x = track.x + int((track.width - thumb_w) * ratio)
                thumb_rect = pygame.Rect(thumb_x, track.y - 2, thumb_w, track.height + 4)
                pygame.draw.rect(self.screen, Color.DARK_GRAY, thumb_rect)
                self.main_scroll_track_rect = track
                self.main_scroll_thumb_rect = thumb_rect
            else:
                self.main_scroll_track_rect = None
                self.main_scroll_thumb_rect = None

        products_title = self.font_normal.render("Productos creados", True, Color.DARK_GRAY)
        self.screen.blit(products_title, (300, products_base_y))

        # Single visual box + count to avoid clutter.
        bx, by = 320, products_base_y + 40
        front_rect = pygame.Rect(bx, by, 95, 70)
        top_poly = [(bx, by), (bx + 20, by - 14), (bx + 115, by - 14), (bx + 95, by)]
        side_poly = [(bx + 95, by), (bx + 115, by - 14), (bx + 115, by + 56), (bx + 95, by + 70)]

        pygame.draw.polygon(self.screen, (230, 197, 130), top_poly)
        pygame.draw.polygon(self.screen, (205, 166, 99), side_poly)
        pygame.draw.rect(self.screen, (219, 180, 112), front_rect)
        pygame.draw.rect(self.screen, Color.BORDER, front_rect, 2)
        pygame.draw.line(self.screen, (170, 130, 70), (bx + 48, by), (bx + 48, by + 70), 2)

        count_text = self.font_large.render(f"x{self.products_count}", True, Color.BLUE)
        self.screen.blit(count_text, (450, by + 18))
        count_label = self.font_small.render("productos en cola", True, Color.TEXT_GRAY)
        self.screen.blit(count_label, (452, by + 52))

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

            if event.type == pygame.MOUSEWHEEL:
                mouse_pos = pygame.mouse.get_pos()
                handled = False
                for dropdown in [self.dropdown_proceso_tarea, self.dropdown_desde, self.dropdown_hacia]:
                    if dropdown.handle_wheel(mouse_pos, event.y):
                        handled = True
                        break
                if not handled and self._left_panel_rect().collidepoint(mouse_pos):
                    self._scroll_sidebar(event.y)
                    handled = True
                if not handled and self._main_panel_rect().collidepoint(mouse_pos):
                    self.main_scroll_x = max(0, min(self.main_max_scroll, self.main_scroll_x - event.y * 40))
                    handled = True
                if handled:
                    continue

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.main_scroll_dragging = False

            if event.type == pygame.MOUSEMOTION and self.main_scroll_dragging:
                if self.main_scroll_track_rect and self.main_scroll_thumb_rect and self.main_max_scroll > 0:
                    min_x = self.main_scroll_track_rect.x
                    max_x = self.main_scroll_track_rect.right - self.main_scroll_thumb_rect.width
                    new_x = max(min_x, min(max_x, event.pos[0] - self.main_scroll_drag_offset))
                    track_range = max(1, max_x - min_x)
                    ratio = (new_x - min_x) / track_range
                    self.main_scroll_x = int(ratio * self.main_max_scroll)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_iniciar.is_clicked(event.pos):
                    self.state = SimulationState.RUNNING
                elif self.btn_pausar.is_clicked(event.pos):
                    self.state = SimulationState.PAUSED
                elif self.btn_reiniciar.is_clicked(event.pos):
                    self.state = SimulationState.STOPPED
                    self.tiempo_global = 0
                elif self.btn_crear_producto.is_clicked(event.pos):
                    qty_text = self.input_cantidad_producto.text.strip()
                    qty = int(qty_text) if qty_text.isdigit() else 1
                    self._create_products(qty)
                elif self.main_scroll_thumb_rect and self.main_scroll_thumb_rect.collidepoint(event.pos):
                    self.main_scroll_dragging = True
                    self.main_scroll_drag_offset = event.pos[0] - self.main_scroll_thumb_rect.x
                elif self.main_scroll_track_rect and self.main_scroll_track_rect.collidepoint(event.pos):
                    if self.main_scroll_thumb_rect and self.main_max_scroll > 0:
                        target_x = event.pos[0] - self.main_scroll_thumb_rect.width // 2
                        min_x = self.main_scroll_track_rect.x
                        max_x = self.main_scroll_track_rect.right - self.main_scroll_thumb_rect.width
                        clamped_x = max(min_x, min(max_x, target_x))
                        track_range = max(1, max_x - min_x)
                        ratio = (clamped_x - min_x) / track_range
                        self.main_scroll_x = int(ratio * self.main_max_scroll)

                # Section toggles
                layout = self._get_sidebar_layout()
                if 15 < event.pos[0] < 35 and self._left_sy(layout["crear_y"] - 5) < event.pos[1] < self._left_sy(layout["crear_y"] + 20):
                    self.crear_proceso_expanded = not self.crear_proceso_expanded
                    self.sidebar_scroll = min(self.sidebar_scroll, self._max_sidebar_scroll())
                elif 15 < event.pos[0] < 35 and self._left_sy(layout["agregar_y"] - 5) < event.pos[1] < self._left_sy(layout["agregar_y"] + 20):
                        self.agregar_tarea_expanded = not self.agregar_tarea_expanded
                        self.sidebar_scroll = min(self.sidebar_scroll, self._max_sidebar_scroll())
                elif 15 < event.pos[0] < 35 and self._left_sy(layout["conectar_y"] - 5) < event.pos[1] < self._left_sy(layout["conectar_y"] + 20):
                        self.conectar_procesos_expanded = not self.conectar_procesos_expanded
                        self.sidebar_scroll = min(self.sidebar_scroll, self._max_sidebar_scroll())

                # Checkboxes
                elif 20 < event.pos[0] < 38:
                    check_y = layout["crear_y"] + 35 + 54
                    if self.crear_proceso_expanded and self._left_sy(check_y) < event.pos[1] < self._left_sy(check_y + 18):
                        self.checkbox_inicial = not self.checkbox_inicial
                        if self.checkbox_inicial:
                            self.checkbox_final = False
                    
                    check_y2 = layout["crear_y"] + 35 + 84
                    if self.crear_proceso_expanded and self._left_sy(check_y2) < event.pos[1] < self._left_sy(check_y2 + 18):
                        self.checkbox_final = not self.checkbox_final
                        if self.checkbox_final:
                            self.checkbox_inicial = False

                # Dropdowns
                if self.dropdown_proceso_tarea.is_clicked(event.pos):
                    self.dropdown_proceso_tarea.toggle()
                    self.dropdown_desde.open = False
                    self.dropdown_hacia.open = False
                elif self.dropdown_proceso_tarea.open:
                    option = self.dropdown_proceso_tarea.get_clicked_option(event.pos)
                    if option:
                        self.dropdown_proceso_tarea.select(option)
                    elif not self.dropdown_proceso_tarea.get_dropdown_rect().collidepoint(event.pos):
                        self.dropdown_proceso_tarea.open = False

                if self.dropdown_desde.is_clicked(event.pos):
                    self.dropdown_desde.toggle()
                    self.dropdown_proceso_tarea.open = False
                    self.dropdown_hacia.open = False
                elif self.dropdown_desde.open:
                    option = self.dropdown_desde.get_clicked_option(event.pos)
                    if option:
                        self.dropdown_desde.select(option)
                    elif not self.dropdown_desde.get_dropdown_rect().collidepoint(event.pos):
                        self.dropdown_desde.open = False

                if self.dropdown_hacia.is_clicked(event.pos):
                    self.dropdown_hacia.toggle()
                    self.dropdown_proceso_tarea.open = False
                    self.dropdown_desde.open = False
                elif self.dropdown_hacia.open:
                    option = self.dropdown_hacia.get_clicked_option(event.pos)
                    if option:
                        self.dropdown_hacia.select(option)
                    elif not self.dropdown_hacia.get_dropdown_rect().collidepoint(event.pos):
                        self.dropdown_hacia.open = False

                # Buttons
                if self.btn_crear_proceso.is_clicked(event.pos):
                    if self.input_proceso_name.text:
                        process_name = self.input_proceso_name.text.strip()
                        if process_name and process_name not in self.procesos_list:
                            self.procesos_list.append(process_name)
                            self.process_products[process_name] = self.process_products.get(process_name, 0)
                            self.process_meta[process_name] = {
                                "inicial": self.checkbox_inicial,
                                "final": self.checkbox_final,
                            }
                            self.sidebar_scroll = min(self.sidebar_scroll, self._max_sidebar_scroll())
                            self.checkbox_inicial = False
                            self.checkbox_final = False
                        self.input_proceso_name.text = ""
                elif self.btn_agregar_tarea.is_clicked(event.pos):
                    if self.input_tarea_name.text and self.dropdown_proceso_tarea.selected:
                        self.tareas_list[self.input_tarea_name.text] = {
                            "proceso": self.dropdown_proceso_tarea.selected,
                            "tiempo": self.input_tiempo_proceso.text,
                            "orden": self.input_orden.text
                        }
                        self.input_tarea_name.text = ""
                elif self.btn_conectar.is_clicked(event.pos):
                    desde = self.dropdown_desde.selected
                    hacia = self.dropdown_hacia.selected
                    if desde and hacia and desde != hacia:
                        self.process_connections[desde] = hacia
                        # Keep one incoming link per process for a clean single-chain visualization.
                        for src, dst in list(self.process_connections.items()):
                            if src != desde and dst == hacia:
                                del self.process_connections[src]

            self.input_proceso_name.handle_event(event)
            self.input_tarea_name.handle_event(event)
            self.input_tiempo_proceso.handle_event(event)
            self.input_orden.handle_event(event)
            self.input_cantidad_producto.handle_event(event)
            self.input_cantidad_producto.text = "".join(ch for ch in self.input_cantidad_producto.text if ch.isdigit())[:4]

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
