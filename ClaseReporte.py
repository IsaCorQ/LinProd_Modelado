class Reporte:
    def __init__(self, linea):
        self.linea = linea
        self.tiempo_primer_producto = 0
        self.tiempo_ultimo_producto = 0
        self.tiempo_promedio = 0
        self.cuello_botella = None
        self.promedio_espera = 0
        self.cuello_botella_proceso = None

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
                    self.cuello_botella_proceso = proceso.nombre

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
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.units import inch
            from datetime import datetime
            
            filename = f"reporte_simulacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1976D2'),
                spaceAfter=30,
                alignment=1  # Center
            )
            elements.append(Paragraph("Reporte de Simulación de Línea de Producción", title_style))
            elements.append(Spacer(1, 0.3 * inch))
            
            # Summary data
            data = [
                ['Métrica', 'Valor'],
                ['Tiempo Primer Producto', f'{self.tiempo_primer_producto} ciclos'],
                ['Tiempo Último Producto', f'{self.tiempo_ultimo_producto} ciclos'],
                ['Tiempo Promedio por Producto', f'{self.tiempo_promedio:.2f} ciclos'],
                ['Cuello de Botella', f'{self.cuello_botella or "No detectado"}'],
                ['Proceso del Cuello de Botella', f'{self.cuello_botella_proceso or "N/A"}'],
                ['Promedio de Espera', f'{self.promedio_espera:.2f} productos'],
                ['Total de Productos Completados', f'{len(self.linea.productosCompletados)}'],
            ]
            
            table = Table(data, colWidths=[3.5*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.5 * inch))
            
            # Process details
            if self.linea.procesos:
                elements.append(Paragraph("Detalle de Procesos", styles['Heading2']))
                elements.append(Spacer(1, 0.2 * inch))
                
                for proceso in self.linea.procesos:
                    elements.append(Paragraph(f"<b>Proceso:</b> {proceso.nombre}", styles['Normal']))
                    elements.append(Spacer(1, 0.1 * inch))
                    
                    if proceso.tareas:
                        task_data = [['Tarea', 'Tiempo de Proceso', 'Cola Actual']]
                        for tarea in proceso.tareas:
                            task_data.append([
                                tarea.nombre,
                                f'{tarea.tiempo_proceso} ciclos',
                                f'{tarea.obtener_tamaño_cola()} productos'
                            ])
                        
                        task_table = Table(task_data, colWidths=[2*inch, 2*inch, 2*inch])
                        task_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 10),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ]))
                        elements.append(task_table)
                    elements.append(Spacer(1, 0.3 * inch))
            
            # Footer
            elements.append(Spacer(1, 0.5 * inch))
            footer_text = f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}"
            elements.append(Paragraph(footer_text, styles['Italic']))
            
            doc.build(elements)
            print(f"\n✓ Reporte PDF generado exitosamente: {filename}")
            return filename
            
        except ImportError:
            print("\nError: La librería 'reportlab' no está instalada.")
            print("Instala con: pip install reportlab")
            return None
        except Exception as e:
            print(f"\nError al generar PDF: {e}")
            return None
