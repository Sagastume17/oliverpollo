from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, HttpResponse
from .models import UsuarioTienda, BitacoraVenta, DetalleBitacora
from .forms import UsuarioTiendaForm
from .permissions import admin_only
from Dash.models import Tienda
from datetime import date, datetime
import json


@login_required
def lista_empleados(request):
    """Vista para listar todos los empleados de tienda"""
    search_query = request.GET.get('search', '')
    tienda_filter = request.GET.get('tienda', '')
    
    empleados = UsuarioTienda.objects.all()
    
    if search_query:
        empleados = empleados.filter(
            Q(username__icontains=search_query) |
            Q(nombre__icontains=search_query) |
            Q(apellido__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if tienda_filter:
        empleados = empleados.filter(tienda_id=tienda_filter)
    
    empleados = empleados.order_by('username')
    
    # Paginación
    paginator = Paginator(empleados, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener tiendas para el filtro
    from Dash.models import Tienda
    tiendas = Tienda.objects.filter(estado=1).order_by('nombre')
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'tienda_filter': tienda_filter,
        'tiendas': tiendas,
    }
    
    return render(request, 'admin/empleados/lista.html', context)


@login_required
def crear_empleado(request):
    """Vista para crear un nuevo empleado de tienda"""
    if request.method == 'POST':
        form = UsuarioTiendaForm(request.POST)
        if form.is_valid():
            empleado = form.save()

            messages.success(request, f'Empleado {empleado.nombre_completo} creado exitosamente')
            return redirect('admin_empleados:lista')
    else:
        form = UsuarioTiendaForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Empleado',
        'accion': 'Crear'
    }
    
    return render(request, 'admin/empleados/form.html', context)


@admin_only
def editar_empleado(request, empleado_id):
    """Vista para editar un empleado de tienda"""
    empleado = get_object_or_404(UsuarioTienda, id=empleado_id)
    
    if request.method == 'POST':
        form = UsuarioTiendaForm(request.POST, instance=empleado)
        if form.is_valid():
            empleado = form.save()

            messages.success(request, f'Empleado {empleado.nombre_completo} actualizado exitosamente')
            return redirect('admin_empleados:lista')
    else:
        form = UsuarioTiendaForm(instance=empleado)
        # Limpiar el campo password para que no muestre el hash
        form.fields['password'].initial = ''
    
    context = {
        'form': form,
        'empleado': empleado,
        'titulo': f'Editar Empleado: {empleado.nombre_completo}',
        'accion': 'Actualizar'
    }
    
    return render(request, 'admin/empleados/form.html', context)


@admin_only
def detalle_empleado(request, empleado_id):
    """Vista para ver detalles de un empleado"""
    empleado = get_object_or_404(UsuarioTienda, id=empleado_id)
    
    # Obtener estadísticas del empleado
    from .models import BitacoraVenta
    total_ventas = BitacoraVenta.objects.filter(usuario_tienda=empleado).count()
    ventas_recientes = BitacoraVenta.objects.filter(
        usuario_tienda=empleado
    ).order_by('-fecha')[:10]
    
    context = {
        'empleado': empleado,
        'total_ventas': total_ventas,
        'ventas_recientes': ventas_recientes,
    }
    
    return render(request, 'admin/empleados/detalle.html', context)


@admin_only
def toggle_empleado_activo(request, empleado_id):
    """Vista para activar/desactivar un empleado"""
    empleado = get_object_or_404(UsuarioTienda, id=empleado_id)
    empleado.activo = not empleado.activo
    empleado.save()

    estado = "activado" if empleado.activo else "desactivado"
    messages.success(request, f'Empleado {empleado.nombre_completo} {estado} exitosamente')

    return redirect('admin_empleados:lista')


# ==================== VISTAS PARA BITÁCORA DE VENTAS ====================

@admin_only
def bitacora_lista(request):
    """Vista para listar todas las bitácoras de venta"""
    # Filtros
    tienda_id = request.GET.get('tienda')
    tipo = request.GET.get('tipo')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    empleado_id = request.GET.get('empleado')

    # Query base
    bitacoras = BitacoraVenta.objects.select_related('tienda', 'usuario_tienda').filter(estado=1)

    # Aplicar filtros
    if tienda_id:
        bitacoras = bitacoras.filter(tienda_id=tienda_id)

    if tipo:
        bitacoras = bitacoras.filter(tipo=tipo)

    if fecha_desde:
        bitacoras = bitacoras.filter(fecha__date__gte=fecha_desde)

    if fecha_hasta:
        bitacoras = bitacoras.filter(fecha__date__lte=fecha_hasta)

    if empleado_id:
        bitacoras = bitacoras.filter(usuario_tienda_id=empleado_id)

    # Ordenar por fecha descendente
    bitacoras = bitacoras.order_by('-fecha')

    # Paginación
    paginator = Paginator(bitacoras, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Datos para filtros
    tiendas = Tienda.objects.all()
    empleados = UsuarioTienda.objects.filter(activo=True).order_by('nombre', 'apellido')

    # Estadísticas
    total_bitacoras = bitacoras.count()
    total_fel = bitacoras.filter(tipo='FEL').count()
    total_inventario = bitacoras.filter(tipo='inventario').count()
    suma_total = bitacoras.aggregate(total=Sum('total'))['total'] or 0

    context = {
        'page_obj': page_obj,
        'tiendas': tiendas,
        'empleados': empleados,
        'filtros': {
            'tienda_id': tienda_id,
            'tipo': tipo,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'empleado_id': empleado_id,
        },
        'estadisticas': {
            'total_bitacoras': total_bitacoras,
            'total_fel': total_fel,
            'total_inventario': total_inventario,
            'suma_total': suma_total,
        }
    }

    return render(request, 'admin/bitacora/lista.html', context)


@admin_only
def bitacora_detalle(request, bitacora_id):
    """Vista para ver detalles de una bitácora específica"""
    bitacora = get_object_or_404(BitacoraVenta, id=bitacora_id)
    detalles = DetalleBitacora.objects.filter(bitacora=bitacora).select_related('producto', 'receta')

    context = {
        'bitacora': bitacora,
        'detalles': detalles,
    }

    return render(request, 'admin/bitacora/detalle.html', context)


@admin_only
def generar_reporte_tienda(request):
    """Vista para generar reporte de movimientos por tienda"""
    if request.method == 'POST':
        tienda_id = request.POST.get('tienda_id')
        fecha_reporte = request.POST.get('fecha_reporte')

        if not tienda_id or not fecha_reporte:
            messages.error(request, 'Debe seleccionar tienda y fecha')
            return redirect('admin_empleados:reporte_tienda')

        tienda = get_object_or_404(Tienda, id=tienda_id)
        fecha_obj = datetime.strptime(fecha_reporte, '%Y-%m-%d').date()

        # Obtener todas las bitácoras del día
        bitacoras = BitacoraVenta.objects.filter(
            tienda=tienda,
            fecha__date=fecha_obj,
            estado=1
        ).select_related('usuario_tienda')

        if not bitacoras.exists():
            messages.warning(request, f'No hay movimientos registrados para {tienda.nombre} el {fecha_obj.strftime("%d/%m/%Y")}')
            return redirect('admin_empleados:reporte_tienda')

        # Generar reporte
        from .reportes import generar_reporte_movimientos_tienda
        return generar_reporte_movimientos_tienda(tienda, fecha_obj, bitacoras)

    # GET - Mostrar formulario
    tiendas = Tienda.objects.all()
    context = {
        'tiendas': tiendas,
        'fecha_hoy': date.today().strftime('%Y-%m-%d')
    }

    return render(request, 'admin/bitacora/reporte_form.html', context)


@admin_only
def reporte_web_view(request):
    """Vista para mostrar el reporte web interactivo"""
    print(f"🔍 REPORTE WEB - Método: {request.method}")

    if request.method == 'POST':
        tienda_id = request.POST.get('tienda_id')
        fecha_reporte = request.POST.get('fecha_reporte')
        generar_pdf = request.POST.get('generar_pdf') == 'true'

        print(f"📊 POST Data - Tienda ID: {tienda_id}, Fecha: {fecha_reporte}, PDF: {generar_pdf}")

        if not tienda_id or not fecha_reporte:
            print("❌ ERROR: Faltan tienda_id o fecha_reporte")
            messages.error(request, 'Debe seleccionar tienda y fecha')
            return redirect('admin_empleados:reporte_web')

        tienda = get_object_or_404(Tienda, id=tienda_id)
        from datetime import datetime as dt
        fecha_obj = dt.strptime(fecha_reporte, '%Y-%m-%d').date()

        print(f"🏪 Tienda: {tienda.nombre}")
        print(f"📅 Fecha objeto: {fecha_obj}")

        # Obtener todas las bitácoras del día usando rango de fechas naive
        from datetime import datetime as dt, timedelta

        # Crear fechas naive (sin timezone) para el rango completo del día
        fecha_inicio = dt.combine(fecha_obj, dt.min.time())
        fecha_fin = dt.combine(fecha_obj, dt.max.time())

        bitacoras = BitacoraVenta.objects.filter(
            tienda=tienda,
            fecha__range=(fecha_inicio, fecha_fin),
            estado=1
        ).select_related('usuario_tienda')

        print(f"📋 Bitácoras encontradas: {bitacoras.count()}")

        # Debug: mostrar la consulta SQL
        print(f"🔍 SQL Query: {bitacoras.query}")

        # Debug: verificar si hay bitácoras para esta tienda en cualquier fecha
        todas_bitacoras_tienda = BitacoraVenta.objects.filter(tienda=tienda, estado=1)
        print(f"📊 Total bitácoras para {tienda.nombre}: {todas_bitacoras_tienda.count()}")

        for b in bitacoras[:3]:  # Mostrar primeras 3
            print(f"   - {b.numero_recibo} | {b.fecha} | {b.tipo} | Q{b.total}")

        if not bitacoras.exists():
            print("❌ NO HAY BITÁCORAS para esta fecha y tienda")
            # Debug: mostrar todas las fechas disponibles
            todas_fechas = BitacoraVenta.objects.filter(tienda=tienda, estado=1).values_list('fecha', flat=True)
            fechas_str = [f.strftime('%Y-%m-%d %H:%M') for f in todas_fechas[:5] if f is not None]  # Primeras 5
            print(f"📅 Fechas disponibles para {tienda.nombre}: {fechas_str}")
            messages.warning(request, f'No hay movimientos registrados para {tienda.nombre} el {fecha_obj.strftime("%d/%m/%Y")}. Fechas disponibles: {", ".join(fechas_str)}')
            return redirect('admin_empleados:reporte_web')

        # Si se solicita PDF, generarlo
        if generar_pdf:
            print("📄 GENERANDO PDF...")
            from .reportes import generar_reporte_movimientos_tienda
            return generar_reporte_movimientos_tienda(tienda, fecha_obj, bitacoras)

        # Procesar datos para el reporte web
        from collections import defaultdict

        # Resumen general
        total_movimientos = bitacoras.count()
        total_fel = bitacoras.filter(tipo='FEL').count()
        total_inventario = bitacoras.filter(tipo='inventario').count()
        total_monto = sum(float(b.total) for b in bitacoras)

        # Detalles por producto
        productos_vendidos = defaultdict(lambda: {'cantidad': 0, 'total': 0, 'fel': 0, 'inventario': 0, 'precio_unitario': 0})
        productos_fel = defaultdict(lambda: {'cantidad': 0, 'total': 0, 'precio_unitario': 0})
        productos_inventario = defaultdict(lambda: {'cantidad': 0, 'total': 0, 'precio_unitario': 0})

        # Totales por tipo
        total_monto_fel = 0
        total_monto_inventario = 0

        for bitacora in bitacoras:
            detalles = DetalleBitacora.objects.filter(bitacora=bitacora)
            for detalle in detalles:
                nombre = detalle.nombre_item
                cantidad = detalle.cantidad
                subtotal = float(detalle.subtotal)
                precio_unitario = subtotal / cantidad if cantidad > 0 else 0

                # Totales generales
                productos_vendidos[nombre]['cantidad'] += cantidad
                productos_vendidos[nombre]['total'] += subtotal
                productos_vendidos[nombre]['precio_unitario'] = precio_unitario

                # Separar por tipo
                if bitacora.tipo == 'FEL':
                    productos_vendidos[nombre]['fel'] += cantidad
                    productos_fel[nombre]['cantidad'] += cantidad
                    productos_fel[nombre]['total'] += subtotal
                    productos_fel[nombre]['precio_unitario'] = precio_unitario
                    total_monto_fel += subtotal
                else:
                    productos_vendidos[nombre]['inventario'] += cantidad
                    productos_inventario[nombre]['cantidad'] += cantidad
                    productos_inventario[nombre]['total'] += subtotal
                    productos_inventario[nombre]['precio_unitario'] = precio_unitario
                    total_monto_inventario += subtotal

        print(f"📊 RESUMEN CALCULADO:")
        print(f"   - Total movimientos: {total_movimientos}")
        print(f"   - Total FEL: {total_fel}")
        print(f"   - Total inventario: {total_inventario}")
        print(f"   - Total monto: {total_monto}")
        print(f"   - Productos vendidos: {len(productos_vendidos)}")

        context = {
            'tienda': tienda,
            'fecha': fecha_obj,
            'bitacoras': bitacoras,
            'resumen': {
                'total_movimientos': total_movimientos,
                'total_fel': total_fel,
                'total_inventario': total_inventario,
                'total_monto': total_monto,
                'total_monto_fel': total_monto_fel,
                'total_monto_inventario': total_monto_inventario,
            },
            'productos_vendidos': dict(productos_vendidos),
            'productos_fel': dict(productos_fel),
            'productos_inventario': dict(productos_inventario),
            'fecha_reporte': fecha_reporte,
            'tienda_id': tienda_id,
        }

        print("🌐 RENDERIZANDO TEMPLATE: admin/bitacora/reporte_web.html")
        return render(request, 'admin/bitacora/reporte_web.html', context)

    # GET - Mostrar formulario
    print("📝 MOSTRANDO FORMULARIO (GET)")
    tiendas = Tienda.objects.all()
    print(f"🏪 Tiendas disponibles: {[t.nombre for t in tiendas]}")

    # Debug: mostrar fechas con movimientos
    print("🔍 CONSULTANDO FECHAS...")

    # Primero verificar cuántos registros hay
    total_bitacoras = BitacoraVenta.objects.count()
    bitacoras_activas = BitacoraVenta.objects.filter(estado=1).count()
    print(f"📊 Total bitácoras: {total_bitacoras}, Activas: {bitacoras_activas}")

    # Obtener fechas usando una consulta más simple
    from django.db.models import Q
    from datetime import datetime, date

    bitacoras_recientes = BitacoraVenta.objects.filter(estado=1).order_by('-fecha')[:10]
    fechas_debug = []

    for bitacora in bitacoras_recientes:
        fecha_str = bitacora.fecha.strftime('%Y-%m-%d')
        if fecha_str not in fechas_debug:
            fechas_debug.append(fecha_str)

    print(f"📅 Fechas con movimientos: {fechas_debug}")
    print(f"📋 Bitácoras recientes:")
    for b in bitacoras_recientes[:3]:
        print(f"   - ID:{b.id} | {b.numero_recibo} | {b.fecha} | {b.tipo} | Estado:{b.estado} | Tienda:{b.tienda.nombre}")

    context = {
        'tiendas': tiendas,
        'fecha_hoy': date.today().strftime('%Y-%m-%d'),
        'fechas_debug': fechas_debug
    }

    print("📄 RENDERIZANDO FORMULARIO: admin/bitacora/reporte_form_web.html")
    return render(request, 'admin/bitacora/reporte_form_web.html', context)


#################   CONTROL DIARIO - ADMINISTRADOR   #############

from .models import ControlDiario

@login_required
def admin_listar_controles(request):
    """Vista para que administradores vean todos los controles diarios"""
    # Filtros
    tienda_id = request.GET.get('tienda')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    controles = ControlDiario.objects.all().select_related('tienda', 'usuario_tienda')
    
    if tienda_id:
        controles = controles.filter(tienda_id=tienda_id)
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            controles = controles.filter(fecha__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            controles = controles.filter(fecha__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # Paginación
    paginator = Paginator(controles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener tiendas para el filtro
    tiendas = Tienda.objects.all()
    
    context = {
        'page_obj': page_obj,
        'tiendas': tiendas,
        'tienda_seleccionada': tienda_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    return render(request, 'admin/control_diario_list.html', context)


@login_required
def admin_detalle_control(request, control_id):
    """Vista para que administradores vean el detalle de un control diario"""
    control = get_object_or_404(ControlDiario, id=control_id)
    
    # Calcular resumen de productos específicos (Tabla 6)
    productos_especificos = {}
    for producto in ['Pollo', 'Papas', 'Ensaladas']:
        if producto in control.venta_productos:
            productos_especificos[producto] = control.venta_productos[producto].get('cantidad', '')
    
    context = {
        'control': control,
        'productos_especificos': productos_especificos,
    }
    return render(request, 'admin/control_diario_detalle.html', context)
