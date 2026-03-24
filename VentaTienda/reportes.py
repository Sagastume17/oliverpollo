from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from django.http import HttpResponse
from io import BytesIO
import datetime


class ReciboPDF:
    """Generador de PDFs para recibos de impresora térmica 3 pulgadas"""

    def __init__(self):
        # Configuración para papel térmico 3 pulgadas (80mm)
        self.width = 80 * mm
        self.margin = 3 * mm
        self.content_width = self.width - (2 * self.margin)
        
    def generar_recibo(self, bitacora):
        """Genera un PDF de recibo para una bitácora de venta"""
        buffer = BytesIO()

        # Calcular altura dinámica basada en contenido
        num_items = bitacora.detalles.count()
        altura_base = 80 * mm  # Altura mínima
        altura_por_item = 8 * mm  # Altura adicional por cada item
        altura_total = altura_base + (num_items * altura_por_item)

        # Crear el documento con altura dinámica
        doc = SimpleDocTemplate(
            buffer,
            pagesize=(self.width, altura_total),
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # Estilos
        styles = self._get_styles()
        story = []
        
        # Encabezado
        story.append(Paragraph(bitacora.tienda.nombre, styles['titulo']))
        story.append(Paragraph("Pollo Express", styles['subtitulo']))
        story.append(Spacer(1, 3 * mm))

        # Información del cliente
        cliente_nit = getattr(bitacora, 'cliente_nit', 'C/F') or 'C/F'
        cliente_nombre = getattr(bitacora, 'cliente_nombre', 'Consumidor Final') or 'Consumidor Final'
        cliente_direccion = getattr(bitacora, 'cliente_direccion', 'Ciudad') or 'Ciudad'

        cliente_data = [
            ['NIT:', cliente_nit],
            ['Nombre:', cliente_nombre],
            ['Dirección:', cliente_direccion],
        ]

        cliente_table = Table(cliente_data, colWidths=[18 * mm, 52 * mm])
        cliente_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(cliente_table)
        story.append(Spacer(1, 3 * mm))
        
        # Línea separadora
        story.append(self._crear_linea_separadora())
        story.append(Spacer(1, 3 * mm))
        
        # Información del recibo
        info_data = [
            ['Recibo:', bitacora.numero_recibo],
            ['Fecha:', bitacora.fecha.strftime('%d/%m/%Y %H:%M')],
            ['Empleado:', bitacora.usuario_tienda.nombre_completo],
        ]
        
        info_table = Table(info_data, colWidths=[20 * mm, 50 * mm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 3 * mm))
        
        # Línea separadora
        story.append(self._crear_linea_separadora())
        story.append(Spacer(1, 3 * mm))
        
        # Productos/Recetas
        productos_data = [['Producto/Receta', 'Cant', 'Precio', 'Total']]
        
        for detalle in bitacora.detalles.all():
            productos_data.append([
                detalle.nombre_item,
                str(detalle.cantidad),
                f'Q{detalle.precio_unitario:.2f}',
                f'Q{detalle.subtotal:.2f}'
            ])
        
        productos_table = Table(productos_data, colWidths=[35 * mm, 10 * mm, 15 * mm, 15 * mm])
        productos_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(productos_table)
        story.append(Spacer(1, 3 * mm))
        
        # Línea separadora
        story.append(self._crear_linea_separadora())
        story.append(Spacer(1, 2 * mm))
        
        # Total
        total_data = [['TOTAL:', f'Q{bitacora.total:.2f}']]
        total_table = Table(total_data, colWidths=[50 * mm, 25 * mm])
        total_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        story.append(total_table)
        story.append(Spacer(1, 3 * mm))
        
        # Observaciones si existen
        if bitacora.observaciones:
            story.append(self._crear_linea_separadora())
            story.append(Spacer(1, 2 * mm))
            story.append(Paragraph(f"Obs: {bitacora.observaciones}", styles['observaciones']))
            story.append(Spacer(1, 3 * mm))
        
        # Línea separadora
        story.append(self._crear_linea_separadora())
        story.append(Spacer(1, 3 * mm))
        
        # Pie de página
        story.append(Paragraph("¡Gracias por su compra!", styles['pie']))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(f"Impreso: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['fecha_impresion']))
        
        # Construir el PDF
        doc.build(story)
        
        # Preparar respuesta
        buffer.seek(0)
        return buffer
    
    def _get_styles(self):
        """Define los estilos para el recibo"""
        styles = {
            'titulo': ParagraphStyle(
                'titulo',
                fontName='Helvetica-Bold',
                fontSize=12,
                alignment=TA_CENTER,
                spaceAfter=2
            ),
            'subtitulo': ParagraphStyle(
                'subtitulo',
                fontName='Helvetica',
                fontSize=8,
                alignment=TA_CENTER,
                spaceAfter=2
            ),
            'observaciones': ParagraphStyle(
                'observaciones',
                fontName='Helvetica',
                fontSize=7,
                alignment=TA_LEFT,
                leftIndent=2 * mm
            ),
            'pie': ParagraphStyle(
                'pie',
                fontName='Helvetica-Bold',
                fontSize=9,
                alignment=TA_CENTER
            ),
            'fecha_impresion': ParagraphStyle(
                'fecha_impresion',
                fontName='Helvetica',
                fontSize=6,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
        }
        return styles
    
    def _crear_linea_separadora(self):
        """Crea una línea separadora punteada"""
        linea_data = [['─' * 50]]
        linea_table = Table(linea_data, colWidths=[self.content_width])
        linea_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        return linea_table


def generar_pdf_recibo(bitacora):
    """Función helper para generar PDF de recibo"""
    generador = ReciboPDF()
    buffer = generador.generar_recibo(bitacora)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recibo_{bitacora.numero_recibo}.pdf"'
    response.write(buffer.getvalue())
    buffer.close()
    
    return response


def generar_pdf_recibo_inline(bitacora):
    """Función helper para mostrar PDF en el navegador"""
    generador = ReciboPDF()
    buffer = generador.generar_recibo(bitacora)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="recibo_{bitacora.numero_recibo}.pdf"'
    response.write(buffer.getvalue())
    buffer.close()
    
    return response


def generar_reporte_movimientos_tienda(tienda, fecha, bitacoras):
    """Generar reporte PDF de movimientos por tienda"""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from .models import DetalleBitacora
    from collections import defaultdict

    # Crear respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="reporte_movimientos_{tienda.nombre}_{fecha.strftime("%Y%m%d")}.pdf"'

    # Crear PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Movimientos Tienda: {tienda.nombre}")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, f"Fecha: {fecha.strftime('%d/%m/%Y')}")

    y_position = height - 100

    # Resumen general
    total_movimientos = bitacoras.count()
    total_fel = bitacoras.filter(tipo='FEL').count()
    total_inventario = bitacoras.filter(tipo='inventario').count()
    total_monto = sum(float(b.total) for b in bitacoras)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "RESUMEN GENERAL")
    y_position -= 25

    p.setFont("Helvetica", 10)
    p.drawString(50, y_position, f"Total de movimientos: {total_movimientos}")
    y_position -= 15
    p.drawString(50, y_position, f"Ventas FEL: {total_fel}")
    y_position -= 15
    p.drawString(50, y_position, f"Ajustes Inventario: {total_inventario}")
    y_position -= 15
    p.drawString(50, y_position, f"Monto total: Q{total_monto:.2f}")
    y_position -= 30

    # Detalles por producto
    productos_vendidos = defaultdict(lambda: {'cantidad': 0, 'total': 0})

    for bitacora in bitacoras:
        detalles = DetalleBitacora.objects.filter(bitacora=bitacora)
        for detalle in detalles:
            nombre = detalle.nombre_item
            productos_vendidos[nombre]['cantidad'] += detalle.cantidad
            productos_vendidos[nombre]['total'] += float(detalle.subtotal)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "PRODUCTOS VENDIDOS")
    y_position -= 25

    p.setFont("Helvetica", 10)
    for producto, datos in productos_vendidos.items():
        if y_position < 50:  # Nueva página si es necesario
            p.showPage()
            y_position = height - 50

        p.drawString(50, y_position, f"{producto}: {datos['cantidad']} unidades - Q{datos['total']:.2f}")
        y_position -= 15

    p.save()
    return response
