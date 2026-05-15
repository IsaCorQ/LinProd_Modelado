from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime
import os


class Reporte:
    def __init__(self, linea):
        self.linea = linea
        self.tiempo_primer_producto = 0
        self.tiempo_ultimo_producto = 0
        self.tiempo_promedio = 0
        self.cuello_botella = None
        self.promedio_espera = 0

    def generar_reporte(self):
        productos = self.linea.productosCompletados

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
        """Export report to PDF file"""
        try:
            # Generate PDF filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Reporte_Produccion_{timestamp}.pdf"
            
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom title style
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1976D2'),
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            # Add title
            title = Paragraph("REPORTE DE SIMULACIÓN DE LINEA DE PRODUCCIÓN", title_style)
            story.append(title)
            
            # Add timestamp
            timestamp_style = ParagraphStyle(
                'Timestamp',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                spaceAfter=20,
                alignment=1
            )
            timestamp_text = Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", timestamp_style)
            story.append(timestamp_text)
            story.append(Spacer(1, 0.2 * inch))
            
            # Regenerate report data
            self.generar_reporte()
            
            # Create metrics table
            metrics_data = [
                ['Métrica', 'Valor'],
                ['Tiempo primer producto', f"{self.tiempo_primer_producto} ciclos"],
                ['Tiempo último producto', f"{self.tiempo_ultimo_producto} ciclos"],
                ['Tiempo promedio por producto', f"{self.tiempo_promedio:.2f} ciclos"],
                ['Cuello de botella', str(self.cuello_botella) if self.cuello_botella else 'N/A'],
                ['Promedio de espera en colas', f"{self.promedio_espera:.2f} productos"],
            ]
            
            metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ]))
            
            story.append(metrics_table)
            story.append(Spacer(1, 0.3 * inch))
            
            # Add products completed info
            info_style = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=10
            )
            productos_info = Paragraph(
                f"<b>Productos completados:</b> {len(self.linea.productosCompletados)}",
                info_style
            )
            story.append(productos_info)
            
            # Add processes info
            procesos_info = Paragraph(
                f"<b>Cantidad de procesos:</b> {len(self.linea.procesos)}",
                info_style
            )
            story.append(procesos_info)
            
            # Count total tasks
            total_tareas = sum(len(proceso.tareas) for proceso in self.linea.procesos)
            tareas_info = Paragraph(
                f"<b>Cantidad de tareas:</b> {total_tareas}",
                info_style
            )
            story.append(tareas_info)
            
            # Build PDF
            doc.build(story)
            
            print(f"\n✓ PDF exportado exitosamente: {filename}")
            return filename
            
        except ImportError:
            print("\n✗ Error: reportlab no está instalada. Instale con: pip install reportlab")
            return None
        except Exception as e:
            print(f"\n✗ Error al exportar PDF: {str(e)}")
            return None
