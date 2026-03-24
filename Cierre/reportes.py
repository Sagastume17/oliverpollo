from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import date, datetime
from django.db.models import Sum
from decimal import Decimal
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from VentaTienda.models import CierreDiario

from .models import CuadreReporte
from .forms import CuadreReporteForm, crear_detalle_inventario
from Venta.models import Venta, DetalleVenta
from Productos.models import Producto, IngresoProducto
from Gastos.models import Gastos
from Dash.models import Tienda


@login_required
def nuevo_cuadre(request):
    fecha_hoy = date.today()
    tienda_id = request.GET.get('tienda')
    tienda = None

    if tienda_id:
        try:
            tienda = Tienda.objects.get(id=tienda_id)
        except Tienda.DoesNotExist:
            messages.error(request, "La tienda seleccionada no existe.")

    if request.method == 'POST':
        form = CuadreReporteForm(request.POST)
        if form.is_valid():
            cuadre = form.save(commit=False)
            cuadre.usuario = request.user
            fecha = form.cleaned_data['fecha']
            tienda = form.cleaned_data['tienda']

            # Asegurar que fecha sea date
            if isinstance(fecha, str):
                from datetime import datetime
                fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

            # Obtener cierre diario
            try:
                from VentaTienda.models import CierreDiario
                cierre = CierreDiario.objects.filter(fecha=fecha, tienda=tienda).first()
                if cierre:
                    if hasattr(cierre, 'cierre_diario'):
                        total_ventas = cierre.cierre_diario
                    elif hasattr(cierre, 'total_ventas'):
                        total_ventas = cierre.total_ventas
                    else:
                        total_ventas = Decimal('0.00')
                else:
                    total_ventas = Decimal('0.00')
                    
            except ImportError:
                # Fallback: calcular desde modelo Venta
                total_ventas = Venta.objects.filter(
                    fecha__date=fecha,
                    tienda=tienda,
                    estado=1
                ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
            
            total_gastos = Gastos.objects.filter(fecha=fecha, tienda=tienda).aggregate(
                total=Sum('total'))['total'] or Decimal('0.00')

            # Obtener el faltante del formulario (CORRECCIÓN: SE SUMA)
            faltante = form.cleaned_data.get('faltante', Decimal('0.00'))
            
            # Calcular el efectivo en caja (ventas - gastos + faltante) ← ¡CORREGIDO!
            efectivo_caja = total_ventas - total_gastos + faltante

            # Asignar los valores calculados
            cuadre.venta_total = total_ventas
            cuadre.gasto_diario = total_gastos
            cuadre.faltante = faltante
            cuadre.efectivo_caja = efectivo_caja
            
            cuadre.save()

            messages.success(request, f'Cuadre para {tienda.nombre} creado correctamente.')
            return redirect('listar_cuadres')
        else:
            messages.error(request, "Formulario no válido.")
    else:
        initial_data = {'fecha': fecha_hoy}
        if tienda:
            # Obtener datos usando la misma lógica
            try:
                from VentaTienda.models import CierreDiario
                cierre = CierreDiario.objects.filter(fecha=fecha_hoy, tienda=tienda).first()
                if cierre:
                    if hasattr(cierre, 'cierre_diario'):
                        total_ventas = cierre.cierre_diario
                    elif hasattr(cierre, 'total_ventas'):
                        total_ventas = cierre.total_ventas
                    else:
                        total_ventas = Decimal('0.00')
                else:
                    total_ventas = Decimal('0.00')
                    
            except ImportError:
                # Fallback: calcular desde modelo Venta
                total_ventas = Venta.objects.filter(
                    fecha__date=fecha_hoy,
                    tienda=tienda,
                    estado=1
                ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
            
            total_gastos = Gastos.objects.filter(fecha=fecha_hoy, tienda=tienda).aggregate(
                total=Sum('total'))['total'] or Decimal('0.00')

            # Calcular efectivo en caja inicial (sin faltante)
            efectivo_caja = total_ventas - total_gastos

            initial_data.update({
                'tienda': tienda,
                'venta_total': total_ventas,
                'gasto_diario': total_gastos,
                'efectivo_caja': efectivo_caja,
                'faltante': Decimal('0.00')  # Valor inicial para faltante
            })

        form = CuadreReporteForm(initial=initial_data)

    return render(request, 'Cierre/cuadre_form.html', {
        'form': form,
        'title': 'Nuevo Cuadre'
    })
    
    
@login_required
def listar_cuadres(request):
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    tienda_id = request.GET.get('tienda')

    cuadres = CuadreReporte.objects.all().order_by('-fecha', '-fecha_creacion')
    tiendas = Tienda.objects.filter(estado=True)

    if fecha_desde:
        cuadres = cuadres.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        cuadres = cuadres.filter(fecha__lte=fecha_hasta)
    if tienda_id:
        cuadres = cuadres.filter(tienda_id=tienda_id)

    return render(request, 'Cierre/cuadre_list.html', {
        'cuadres': cuadres,
        'tiendas': tiendas,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'tienda_filtro': tienda_id
    })

@login_required
def editar_cuadre(request, pk):
    cuadre = get_object_or_404(CuadreReporte, pk=pk)
    if request.method == 'POST':
        form = CuadreReporteForm(request.POST, instance=cuadre)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cuadre de {cuadre.tienda} actualizado exitosamente')
            return redirect('listar_cuadres')
    else:
        form = CuadreReporteForm(instance=cuadre)
    
    return render(request, 'Cierre/cuadre_form.html', {
        'form': form,
        'title': 'Editar Cuadre'
    })

@login_required
def eliminar_cuadre(request, pk):
    cuadre = get_object_or_404(CuadreReporte, pk=pk)
    tienda_nombre = cuadre.tienda.nombre
    cuadre.delete()
    messages.success(request, f'Cuadre de {tienda_nombre} eliminado exitosamente')
    return redirect('listar_cuadres')

@login_required
def generar_pdf_cuadre(request, pk):
    cuadre = get_object_or_404(CuadreReporte, pk=pk)

    # Crear el objeto HttpResponse con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cuadre_{cuadre.tienda.nombre}_{cuadre.fecha}.pdf"'

    # Crear el PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Función para crear nueva página si es necesario
    def check_page_break(y_position, needed_space=100):
        if y_position < needed_space:
            p.showPage()
            return height - 50  # Nueva posición Y
        return y_position

    # Encabezado
    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, y, "CUADRE DE REPORTE DIARIO")

    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Tienda: {cuadre.tienda.nombre}")
    p.drawString(350, y, f"Fecha: {cuadre.fecha.strftime('%d/%m/%Y')}")

    y -= 20
    p.drawString(50, y, f"Usuario: {cuadre.usuario.get_full_name()}")
    p.drawString(350, y, f"Fecha de Creación: {cuadre.fecha_creacion.strftime('%d/%m/%Y %H:%M')}")

    # Línea separadora
    y -= 20
    p.line(50, y, width-50, y)
    y -= 30

    # SECCIÓN DE TOTALES
    y = check_page_break(y, 150)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "RESUMEN FINANCIERO")
    y -= 25

    # Crear tabla de totales más compacta
    totales_data = [
        ['Concepto', 'Monto (Q)'],
        ['Total de Venta', f'{int(cuadre.venta_total):,}'],
        ['Gasto Diario', f'{int(cuadre.gasto_diario):,}'],
        ['Efectivo en Caja', f'{int(cuadre.efectivo_caja):,}'],
        ['Total a Depositar', f'{int(cuadre.total_depositar):,}']
    ]

    totales_table = Table(totales_data, colWidths=[200, 120])
    totales_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    totales_table.wrapOn(p, width, height)
    totales_table.drawOn(p, 50, y - 80)
    y -= 130

    # SECCIÓN DE CONTROL DE INVENTARIO
    y = check_page_break(y, 250)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y+25, "CONTROL DE INVENTARIO")
    y -= 65

    # Obtener datos de inventario
    inventario = obtener_inventario_preview(cuadre.tienda, cuadre.fecha)

    if inventario:
        # Crear tabla de inventario con formato de enteros
        inventario_data = [['Producto', 'Stock Inicial', 'Ingreso', 'Venta', 'Stock Final']]
        for item in inventario:
            inventario_data.append([
                item['nombre'][:25] + ('...' if len(item['nombre']) > 25 else ''),  # Truncar nombres largos
                str(int(item['stock_inicial'])),
                str(int(item['ingreso'])),
                str(int(item['venta'])),
                str(int(item['stock_final']))
            ])

        # Calcular altura necesaria
        rows_per_page = 25
        total_rows = len(inventario_data) - 1  # Sin contar el header

        for i in range(0, total_rows, rows_per_page):
            y = check_page_break(y, 300)

            # Datos para esta página
            page_data = [inventario_data[0]]  # Header
            end_idx = min(i + rows_per_page, total_rows)
            page_data.extend(inventario_data[i+1:end_idx+1])

            inventario_table = Table(page_data, colWidths=[140, 70, 70, 70, 70])
            inventario_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Producto alineado a la izquierda
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),  # Números centrados
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))

            table_height = len(page_data) * 15
            inventario_table.wrapOn(p, width, height)
            inventario_table.drawOn(p, 50, y - table_height)
            y -= table_height + 30

    # SECCIÓN DE RESUMEN DE VENTAS
    y = check_page_break(y, 200)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "RESUMEN DE VENTAS POR PRODUCTO")
    y -= 25

    # Obtener datos de ventas
    ventas_resumen = obtener_resumen_ventas(cuadre.tienda, cuadre.fecha)

    if ventas_resumen:
        ventas_data = [['Producto', 'Cantidad Vendida', 'Monto Total (Q)']]
        total_cantidad = 0
        total_monto = 0

        for item in ventas_resumen:
            cantidad = int(item['cantidad'])
            monto = float(item['monto'])
            total_cantidad += cantidad
            total_monto += monto

            ventas_data.append([
                item['nombre'][:30] + ('...' if len(item['nombre']) > 30 else ''),
                str(cantidad),
                f'{monto:,.2f}'
            ])

        # Agregar fila de totales
        ventas_data.append(['TOTAL', str(total_cantidad), f'{total_monto:,.2f}'])

        ventas_table = Table(ventas_data, colWidths=[200, 100, 100])
        ventas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Fila de totales en negrita
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),  # Fondo gris para totales
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightyellow]),
        ]))

        table_height = len(ventas_data) * 18
        y = check_page_break(y, table_height + 50)
        ventas_table.wrapOn(p, width, height)
        ventas_table.drawOn(p, 50, y - table_height)
        y -= table_height + 30

    # INFORMACIÓN ADICIONAL
    y = check_page_break(y, 200)

    # Información de depósito
    if cuadre.numero_boleta:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "INFORMACIÓN DE DEPÓSITO")
        y -= 20
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"No. de Boleta: {cuadre.numero_boleta}")
        y -= 30

    # Información de Pollo Rey
    if cuadre.total_pollo_rey and cuadre.total_pollo_rey > 0:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "INFORMACIÓN DE POLLO REY")
        y -= 20
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Total de Pollo Rey: Q{cuadre.total_pollo_rey:,.2f}")
        y -= 15
        if cuadre.numero_factura_pollo:
            p.drawString(50, y, f"No. Factura: {cuadre.numero_factura_pollo}")
            y -= 15
        if cuadre.libras_pollo:
            p.drawString(50, y, f"Libras de Pollo: {cuadre.libras_pollo:,.2f}")
        y -= 30

    # Otros comentarios
    if cuadre.otros:
        y = check_page_break(y, 100)
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "OBSERVACIONES")
        y -= 20
        p.setFont("Helvetica", 10)

        # Dividir texto en líneas que quepan en la página
        lines = cuadre.otros.split('\n')
        for line in lines:
            if len(line) > 80:  # Si la línea es muy larga, dividirla
                words = line.split(' ')
                current_line = ''
                for word in words:
                    if len(current_line + word) < 80:
                        current_line += word + ' '
                    else:
                        if current_line:
                            y = check_page_break(y, 20)
                            p.drawString(50, y, current_line.strip())
                            y -= 15
                        current_line = word + ' '
                if current_line:
                    y = check_page_break(y, 20)
                    p.drawString(50, y, current_line.strip())
                    y -= 15
            else:
                y = check_page_break(y, 20)
                p.drawString(50, y, line)
                y -= 15

    # Pie de página en cada página
    def add_footer():
        p.setFont("Helvetica-Oblique", 8)
        p.drawCentredString(width/2, 30, f"Generado el {timezone.now().strftime('%d/%m/%Y a las %H:%M')} - Sistema de Gestión")
        p.drawCentredString(width/2, 20, f"Cuadre de {cuadre.tienda.nombre} - {cuadre.fecha.strftime('%d/%m/%Y')}")

    add_footer()

    # Finalizar el PDF
    p.save()

    # Obtener el valor del buffer y escribirlo a la respuesta
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response


@login_required
def actualizar_preview_cuadre(request):
    """Vista AJAX para actualizar la previsualización del cuadre"""
    if request.method == 'GET':
        tienda_id = request.GET.get('tienda')
        fecha_str = request.GET.get('fecha')

        inventario = []
        ventas_resumen = []
        venta_total = 0
        gasto_diario = 0
        efectivo_caja = 0

        if tienda_id and fecha_str:
            try:
                tienda = Tienda.objects.get(id=tienda_id)
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

                # OBTENER CIERRE DIARIO DE LA OTRA APP - CORREGIDO
                try:
                    # Prueba con diferentes posibles ubicaciones
                    try:
                        from VentaTienda.models import CierreDiario
                    except ImportError:
                        try:
                            from VentaTienda.models import CierreDiario
                        except ImportError:
                            from VentaTienda.models import CierreDiario
                    
                    cierre = CierreDiario.objects.filter(fecha=fecha, tienda=tienda).first()
                    if cierre:
                        # Verifica si el campo se llama 'cierre_diario' o 'total_ventas'
                        if hasattr(cierre, 'cierre_diario'):
                            ventas_total = cierre.cierre_diario
                        elif hasattr(cierre, 'total_ventas'):
                            ventas_total = cierre.total_ventas
                        else:
                            ventas_total = Decimal('0.00')
                    else:
                        ventas_total = Decimal('0.00')
                        
                except ImportError as e:
                    # Fallback: calcular desde modelo Venta
                    ventas_total = Venta.objects.filter(
                        fecha__date=fecha,
                        tienda=tienda,
                        estado=1
                    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

                # Calcular gastos
                gastos_total = Gastos.objects.filter(
                    fecha=fecha,
                    tienda=tienda
                ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

                venta_total = float(ventas_total)
                gasto_diario = float(gastos_total)
                efectivo_caja = venta_total - gasto_diario

                # Obtener inventario y ventas
                inventario = obtener_inventario_preview(tienda, fecha)
                ventas_resumen = obtener_resumen_ventas(tienda, fecha)

                # Convertir Decimal a float para JSON
                for item in inventario:
                    item['stock_inicial'] = float(item['stock_inicial'])
                    item['ingreso'] = float(item['ingreso'])
                    item['venta'] = float(item['venta'])
                    item['stock_final'] = float(item['stock_final'])

                for item in ventas_resumen:
                    item['cantidad'] = float(item['cantidad'])
                    item['monto'] = float(item['monto'])

            except (Tienda.DoesNotExist, ValueError):
                pass

    return JsonResponse({
        'inventario': inventario,
        'ventas_resumen': ventas_resumen,
        'venta_total': venta_total,
        'gasto_diario': gasto_diario,
        'efectivo_caja': efectivo_caja,
    })


def obtener_inventario_preview(tienda, fecha):
    """Obtener inventario para la previsualización del cuadre"""
    inventario = []

    # Obtener todos los productos de la tienda
    productos = Producto.objects.filter(tienda=tienda, estado=True)

    for producto in productos:
        # Stock actual del producto
        stock_actual = producto.stock

        # Ingresos del día específico
        ingresos_dia = IngresoProducto.objects.filter(
            producto=producto,
            fecha__date=fecha
        ).aggregate(total=Sum('cantidad'))['total'] or Decimal('0.00')

        # Ventas del día específico
        ventas_dia = DetalleVenta.objects.filter(
            producto=producto,
            venta__fecha__date=fecha,
            venta__tienda=tienda,
            venta__estado=1
        ).aggregate(total=Sum('cantidad'))['total'] or Decimal('0.00')

        # Stock inicial = Stock actual - ingresos del día + ventas del día
        stock_inicial = stock_actual - ingresos_dia + ventas_dia

        # Stock final = Stock inicial + ingresos - ventas
        stock_final = stock_inicial + ingresos_dia - ventas_dia

        inventario.append({
            'nombre': producto.nombre,
            'stock_inicial': stock_inicial,
            'ingreso': ingresos_dia,
            'venta': ventas_dia,
            'stock_final': stock_final
        })

    return inventario


def obtener_resumen_ventas(tienda, fecha):
    """Obtener resumen de ventas por producto para una fecha específica"""
    ventas = DetalleVenta.objects.filter(
        venta__fecha__date=fecha,
        venta__tienda=tienda,
        venta__estado=1
    ).values(
        'producto__nombre'
    ).annotate(
        cantidad=Sum('cantidad'),
        monto=Sum('subtotal')
    ).order_by('producto__nombre')

    resumen = []
    for venta in ventas:
        resumen.append({
            'nombre': venta['producto__nombre'],
            'cantidad': venta['cantidad'] or Decimal('0.00'),
            'monto': venta['monto'] or Decimal('0.00')
        })

    return resumen
