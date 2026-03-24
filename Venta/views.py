# views.py
from multiprocessing import Value
from django.forms import CharField, IntegerField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from Productos.models import Producto
from Receta.models import DetalleReceta, Receta
from Dash.models import Tienda
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaForm
from django.urls import reverse
import json
from django.db.models import Sum

@login_required
def nueva_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Crear la venta
                    venta = form.save(commit=False)
                    venta.usuario = request.user
                    venta.save()

                    # Procesar los items de la venta
                    items = json.loads(request.POST.get('items', '[]'))

                    if not items:
                        raise ValueError('No hay items en la venta')

                    total_venta = 0

                    for item in items:
                        cantidad = int(item['cantidad'])
                        precio_unitario = float(item['precio'])
                        subtotal = cantidad * precio_unitario

                        detalle = DetalleVenta(
                            venta=venta,
                            cantidad=cantidad,
                            precio_unitario=precio_unitario,
                            subtotal=subtotal
                        )

                        if item['tipo'] == 'producto':
                            producto = Producto.objects.get(id=item['id'])
                            if producto.stock < cantidad:
                                raise ValueError(f'Stock insuficiente para {producto.nombre}')

                            detalle.producto = producto
                            # Actualizar stock del producto
                            producto.save()

                        else:  # tipo == 'receta'
                            receta = Receta.objects.get(id=item['id'])
                            detalle.receta = receta

                            # Verificar y actualizar stock de los ingredientes
                            detalles_receta = DetalleReceta.objects.filter(receta=receta)
                            for det_receta in detalles_receta:
                                cantidad_necesaria = det_receta.cantidad * cantidad
                                if det_receta.producto.stock < cantidad_necesaria:
                                    raise ValueError(f'Stock insuficiente de {det_receta.producto.nombre} para la receta {receta.nombre}')

                                # Actualizar stock de los ingredientes
                                #det_receta.producto.stock -= cantidad_necesaria
                                det_receta.producto.save()

                        detalle.save()
                        total_venta += subtotal

                    # Actualizar el total de la venta
                    venta.total = total_venta
                    venta.save()

                    return JsonResponse({
                        'status': 'success',
                        'message': 'Venta registrada correctamente',
                        'redirect_url': reverse('ListadoVentas')
                    })

            except ValueError as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error al procesar la venta: {str(e)}'
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Formulario inválido'
            })
    else:
        form = VentaForm()

    context = {
        'form': form,
        'tiendas': Tienda.objects.all()
    }
    return render(request, 'Venta/nueva.html', context)

@login_required
def get_items_tienda(request):
    tienda_id = request.GET.get('tienda_id')
    if not tienda_id:
        return JsonResponse({'error': 'Tienda no especificada'}, status=400)

    try:
        # Obtener productos de la tienda
        productos = Producto.objects.filter(tienda_id=tienda_id).values(
            'id', 'nombre', 'precio_venta', 'stock'
        ).annotate(
            tipo=Value('producto', output_field=CharField())
        )

        # Obtener recetas de la tienda
        recetas = Receta.objects.filter(tienda_id=tienda_id).values(
            'id', 'nombre', 'precio_receta'
        ).annotate(
            tipo=Value('receta', output_field=CharField()),
            precio=F('precio_receta'),
            stock=Value(None, output_field=IntegerField())
        )

        # Combinar productos y recetas
        items = list(productos) + list(recetas)
        return JsonResponse(items, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@login_required
def eliminar_detalle(request, detalle_id):
    detalle = get_object_or_404(DetalleVenta, id=detalle_id)
    venta = detalle.venta

    with transaction.atomic():
        detalle.delete()
        venta.actualizar_total()

    return JsonResponse({
        'status': 'success',
        'message': 'Item eliminado correctamente'
    })

@login_required
def get_items_tienda(request):
    tienda_id = request.GET.get('tienda_id')

    productos = Producto.objects.filter(
        tienda_id=tienda_id,
        estado=True,
        stock__gt=0
    ).values('id', 'nombre', 'precio_venta', 'stock')

    recetas = Receta.objects.filter(
        tienda_id=tienda_id,
        estado=1
    ).values('id', 'nombre', 'precio_receta')

    data = []

    for p in productos:
        data.append({
            'id': p['id'],
            'nombre': p['nombre'],
            'precio': float(p['precio_venta']),
            'stock': p['stock'],
            'tipo': 'producto'
        })

    for r in recetas:
        data.append({
            'id': r['id'],
            'nombre': r['nombre'],
            'precio': float(r['precio_receta']),
            'stock': None,
            'tipo': 'receta'
        })

    return JsonResponse(data, safe=False)


@login_required
def listado_ventas(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin    = request.GET.get('fecha_fin')
    tienda_id    = request.GET.get('tienda')

    ventas = Venta.objects.all().prefetch_related('detalles', 'detalles__producto', 'detalles__receta')

    if fecha_inicio and fecha_fin:
        ventas = ventas.filter(fecha__date__range=[fecha_inicio, fecha_fin])

    if tienda_id:
        ventas = ventas.filter(tienda_id=tienda_id)

    # --- recalcular totales (por si acaso) ---
    for v in ventas:
        v.actualizar_total()

    total_general = ventas.aggregate(suma=Sum('total'))['suma'] or 0

    context = {
        'ventas'             : ventas.order_by('-fecha'),
        'tiendas'            : Tienda.objects.all(),
        'fecha_inicio'       : fecha_inicio,
        'fecha_fin'          : fecha_fin,
        'tienda_seleccionada': tienda_id,
        'total_general'      : total_general,
    }
    return render(request, 'Venta/listado.html', context)

# ───────────────────────────────────────────────────────────
@login_required
def detalle_venta(request, venta_id):
    """
    Devuelve un fragmento HTML con el detalle de la venta.
    Se usa vía fetch desde el listado.
    """
    venta    = get_object_or_404(Venta.objects.prefetch_related('detalles',
                                                                'detalles__producto',
                                                                'detalles__receta'),
                                 pk=venta_id)
    detalles = venta.detalles.all()
    return render(request, 'Venta/detalle_venta_snippet.html', {
        'venta'   : venta,
        'detalles': detalles
    })

@login_required
def anular_venta(request, venta_id):
    with transaction.atomic():
        venta = get_object_or_404(Venta, id=venta_id)

        # Devolver stock de todos los detalles
        for detalle in venta.detalles.all():
            if detalle.producto:
                detalle.producto.stock += detalle.cantidad
                detalle.producto.save()
            elif detalle.receta:
                for det_receta in DetalleReceta.objects.filter(id_receta=detalle.receta):
                    det_receta.producto.stock += (det_receta.cantidad * detalle.cantidad)
                    det_receta.producto.save()

        venta.estado = False
        venta.save()

    messages.success(request, 'Venta anulada correctamente')
    return redirect('ListadoVentas')