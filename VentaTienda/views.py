import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.db.models import Sum
from datetime import date, datetime, timedelta, timezone
from django.core.paginator import Paginator

from Categoria.models import Categoria
from Productos.models import Producto
from Receta.models import Receta
from .models import CierreDiario, UsuarioTienda, BitacoraVenta, DetalleBitacora, CajaTienda, ControlDiario
from .forms import BitacoraVentaForm, CajaTiendaForm, ControlDiarioForm
from .permissions import tienda_login_required, get_current_usuario_tienda, get_current_tienda

import emisor
import receptor
import InfileFel
from django.http import HttpResponse


def normalizar_nombre_campo(nombre):
    """Convierte nombre de producto a formato de campo de formulario.
    Solo reemplaza espacios por guiones, mantiene todo lo demás igual."""
    return nombre.lower().replace(' ', '-')


##############   Cierre ####################



from django.utils import timezone
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas

from .models import  CierreDiario
from Dash.models import Tienda
from VentaTienda.models import UsuarioTienda


# Función PDF ticket 8cm
def generar_pdf_ticket_8cm(ticket_texto):
    buffer = BytesIO()
    width_mm, height_mm = 80, 200
    width_pt = width_mm * 2.83465
    height_pt = height_mm * 2.83465
    c = canvas.Canvas(buffer, pagesize=(width_pt, height_pt))
    y = height_pt - 20
    c.setFont("Courier", 8)
    for linea in ticket_texto.split('\n'):
        c.drawString(5, y, linea)
        y -= 10
        if y < 10:
            c.showPage()
            y = height_pt - 20
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Vista descarga PDF
def descargar_pdf_cierre(request, cierre_id):
    cierre = get_object_or_404(CierreDiario, id=cierre_id)
    buffer = generar_pdf_ticket_8cm(cierre.ticket_texto or "")
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cierre_{cierre.fecha}.pdf"'
    return response

@tienda_login_required
def cierre_diario(request):
    """Vista para el cierre diario de caja con detalle por tipo de venta"""
    usuario_tienda = get_current_usuario_tienda(request)
    tienda = get_current_tienda(request)

    ahora = timezone.now()
    hoy = ahora.date()

    # Caja del día
    caja = CajaTienda.objects.filter(tienda=tienda, fecha=hoy).first()
    dinero_inicial = caja.dinero_inicial if caja else 0
    if not caja:
        messages.warning(request, "No se ha registrado la caja del día.")

    # Ventas del día que sean activas o anuladas
    ventas = BitacoraVenta.objects.filter(
        tienda=tienda, fecha=hoy, estado__in=[1, 2]
    )

    # Separar en listas para mostrar detalles
    ventas_activas = ventas.filter(estado=1)
    ventas_anuladas = ventas.filter(estado=2)

    # Totales
    total_ventas_activas = ventas_activas.aggregate(total=Sum('total'))['total'] or 0
    total_ventas_anuladas = ventas_anuladas.aggregate(total=Sum('total'))['total'] or 0
    total_ventas = total_ventas_activas + total_ventas_anuladas

    # Cálculo del cierre
    cierre_valor = total_ventas_activas  # cierre = solo ventas activas

    # Nombre del negocio
    nombre_negocio = "Pollo Express"

    # Ticket con detalle por tipo de venta
    ticket_texto = f"""
===============================
NEGOCIO: {nombre_negocio}
TIENDA : {tienda.nombre}
FECHA  : {hoy}
-------------------------------
DINERO INICIAL : Q{str(dinero_inicial).rjust(8)}
-------------------------------
VENTAS ACTIVAS :   Q{str(total_ventas).rjust(8)}
VENTAS ANULADAS: - Q{str(total_ventas_anuladas).rjust(8)}
-------------------------------
CIERRE DIARIO  :   Q{str(cierre_valor).rjust(8)}
===============================
""".strip()

    # Guardar o actualizar cierre diario
    cierre, created = CierreDiario.objects.update_or_create(
        tienda=tienda,
        fecha=hoy,
        defaults={
            'dinero_inicial': dinero_inicial,
            'total_ventas': total_ventas,
            'cierre_diario': cierre_valor,
            'ticket_texto': ticket_texto,
        }
    )

    context = {
        'ventas': ventas_activas,
        'ventas_anuladas': ventas_anuladas,
        'total_ventas': total_ventas,
        'total_ventas_activas': total_ventas_activas,
        'total_ventas_anuladas': total_ventas_anuladas,
        'dinero_inicial': dinero_inicial,
        'cierre_diario': cierre_valor,
        'fecha': hoy,
        'usuario_tienda': usuario_tienda,
        'tienda': tienda,
        'cierre': cierre,
        'ticket_texto': ticket_texto,
    }

    return render(request, 'venta_tienda/cierre_diario.html', context)



# views.py
@tienda_login_required
def listar_cierres(request):
    usuario_tienda = get_current_usuario_tienda(request)
    tienda = get_current_tienda(request)
    
    cierres = CierreDiario.objects.filter(tienda=tienda).order_by('-fecha')
    
    context = {
        'cierres': cierres,
        'usuario_tienda': usuario_tienda,
        'tienda': tienda,
    }
    
    return render(request, 'venta_tienda/listar_cierres.html', context)


    
@tienda_login_required
def menu_principal(request):
    """Vista para el menú principal con las 3 cards"""
    usuario_tienda = get_current_usuario_tienda(request)
    tienda = get_current_tienda(request)

    context = {
        'usuario_tienda': usuario_tienda,
        'tienda': tienda,
    }
    return render(request, 'venta_tienda/menu_principal.html', context)

@tienda_login_required
def venta_view(request):
    """Vista principal para la interfaz de venta"""
    usuario_tienda = get_current_usuario_tienda(request)
    tienda = get_current_tienda(request)

    # Obtener todas las categorías
    categorias = Categoria.objects.all()

    # Formulario para observaciones
    form = BitacoraVentaForm()

    context = {
        'categorias': categorias,
        'tienda': tienda,
        'usuario_tienda': usuario_tienda,
        'form': form,
    }

    return render(request, 'venta_tienda/venta.html', context)

@tienda_login_required
def get_productos_categoria(request, categoria_id):
    """API para obtener productos y recetas por categoría"""
    tienda = get_current_tienda(request)

    # Obtener productos de la categoría
    productos = Producto.objects.filter(
        id_cate_id=categoria_id,
        estado=True,
        tienda=tienda
    )

    # Obtener recetas de la categoría (asumiendo que tienen relación con categoría)
    # Nota: Necesitaremos agregar campo categoria a Receta más adelante
    recetas = Receta.objects.filter(
        estado=1,
        tienda=tienda
    )

    items_list = []

    # Agregar productos
    for producto in productos:
        imagen_url = producto.imagen.url if producto.imagen else None
        items_list.append({
            'id': f'producto_{producto.id}',
            'nombre': producto.nombre,
            'precio': float(producto.precio_venta),
            'medida': producto.medida,
            'tipo': 'producto',
            'item_id': producto.id,
            'imagen': imagen_url
        })

    # Agregar recetas
    for receta in recetas:
        imagen_url = receta.imagen.url if receta.imagen else None
        items_list.append({
            'id': f'receta_{receta.id}',
            'nombre': receta.nombre,
            'precio': float(receta.precio_receta),
            'medida': receta.unidad,
            'tipo': 'receta',
            'item_id': receta.id,
            'imagen': imagen_url
        })

    return JsonResponse({'items': items_list})



@tienda_login_required
def caja_view(request):
    """Vista para gestión de caja diaria"""
    usuario_tienda = get_current_usuario_tienda(request)
    tienda = get_current_tienda(request)

    from datetime import date
    hoy = date.today()

    # Verificar si ya existe registro de caja para hoy
    caja_hoy = CajaTienda.objects.filter(tienda=tienda, fecha=hoy).first()

    if request.method == 'POST':
        # Solo permitir registro si no existe caja para hoy
        if caja_hoy:
            messages.error(request, 'La caja del día ya ha sido registrada y no se puede modificar.')
            return redirect('venta_tienda:caja')

        form = CajaTiendaForm(request.POST)

        if form.is_valid():
            caja = form.save(commit=False)
            caja.tienda = tienda
            caja.usuario_tienda = usuario_tienda
            caja.fecha = hoy
            caja.save()

            messages.success(request, 'Caja registrada correctamente')
            return redirect('venta_tienda:caja')
    else:
        # Solo mostrar formulario si no existe caja para hoy
        if not caja_hoy:
            form = CajaTiendaForm()
        else:
            form = None

    context = {
        'form': form,
        'caja_hoy': caja_hoy,
        'usuario_tienda': usuario_tienda,
        'tienda': tienda,
        'fecha': hoy
    }

    return render(request, 'venta_tienda/caja.html', context)


@tienda_login_required
def reimpresion_view(request):
    """Vista para reimpresión de recibos"""
    usuario_tienda = get_current_usuario_tienda(request)
    tienda = get_current_tienda(request)

    # Obtener solo bitácoras de tipo FEL (con factura) de la tienda
    bitacoras = BitacoraVenta.objects.filter(
        tienda=tienda,
        #estado=1,
        tipo='FEL'  # Solo ventas con factura que se pueden reimprimir
    ).order_by('-fecha')[:50]  # Últimas 50 ventas FEL

    context = {
        'bitacoras': bitacoras,
        'usuario_tienda': usuario_tienda,
        'tienda': tienda,
    }

    return render(request, 'venta_tienda/reimpresion.html', context)


@tienda_login_required
def consulta_movimientos_view(request):
    """Vista para consultar todos los movimientos (FEL + Inventario)"""
    usuario_tienda = get_current_usuario_tienda(request)
    tienda = get_current_tienda(request)

    # Obtener TODAS las bitácoras de la tienda (FEL + Inventario)
    bitacoras = BitacoraVenta.objects.filter(
        tienda=tienda,
        estado=1  # Solo activas
    ).order_by('-fecha')[:50]  # Últimos 50 movimientos

    context = {
        'bitacoras': bitacoras,
        'usuario_tienda': usuario_tienda,
        'tienda': tienda,
    }

    return render(request, 'venta_tienda/consulta_movimientos.html', context)


@tienda_login_required
def detalle_bitacora(request, bitacora_id):
    """Vista para ver detalle de una bitácora específica"""
    usuario_tienda = get_current_usuario_tienda(request)
    tienda = get_current_tienda(request)

    bitacora = get_object_or_404(BitacoraVenta, id=bitacora_id, tienda=tienda)
    detalles = bitacora.detalles.all()

    context = {
        'bitacora': bitacora,
        'detalles': detalles,
        'usuario_tienda': usuario_tienda,
        'tienda': tienda,
    }

    return render(request, 'venta_tienda/detalle_bitacora.html', context)


@tienda_login_required
def generar_pdf_recibo(request, bitacora_id):
    """Vista para generar PDF de recibo"""
    usuario_tienda = get_current_usuario_tienda(request)
    tienda = get_current_tienda(request)

    bitacora = get_object_or_404(BitacoraVenta, id=bitacora_id, tienda=tienda)

    from .reportes import generar_pdf_recibo_inline
    return generar_pdf_recibo_inline(bitacora)


@tienda_login_required
def ultimas_ventas(request):
    """Obtener las últimas 10 ventas de la tienda"""
    try:
        tienda = get_current_tienda(request)
        ventas = BitacoraVenta.objects.filter(
            tienda=tienda,
            estado=1  # Solo ventas activas
        ).order_by('-fecha')[:10]

        ventas_list = []
        for venta in ventas:
            # Convertir a zona horaria local
            from django.utils import timezone
            fecha_local = timezone.localtime(venta.fecha)

            ventas_list.append({
                'numero_recibo': venta.numero_recibo,
                'fecha': fecha_local.strftime('%d/%m/%Y %H:%M'),
                'total': float(venta.total),
                'cliente': venta.cliente_nombre,
                'tipo': venta.tipo
            })

        return JsonResponse({'ventas': ventas_list})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

        # Diccionario de precios por defecto, escalable
        default_precios = {
            'Pollo': 72,
            'Papas': 7,
            'Hamburguesa': 15,
            'Ensaladas': 5,
            'Pay': 5,
            'Gran pieza': 15,
            'Mollejas': 12,
            'Medallones de 4': 6,
            'Medallones de 8': 12,
            'Soda Lata': 6,
            'Soda desechable': 8,
            'agua pura botella': 5,
            'agua pura bolsa': 1,
            'ISO MAX': 2,
            'coca vidrio': 4,
        }

        context['default_precios'] = default_precios

@tienda_login_required
def descargar_pdf_recibo(request, numero_recibo):
    """Vista para descargar PDF de recibo por número"""
    usuario_tienda = get_current_usuario_tienda(request)
    tienda = get_current_tienda(request)

    bitacora = get_object_or_404(BitacoraVenta, numero_recibo=numero_recibo, tienda=tienda)

    from .reportes import generar_pdf_recibo_inline
    return generar_pdf_recibo_inline(bitacora)


@tienda_login_required
def generar_pdf_venta(request, bitacora_id):
    """Vista para generar PDF inmediatamente después de la venta"""
    usuario_tienda = get_current_usuario_tienda(request)
    tienda = get_current_tienda(request)

    bitacora = get_object_or_404(BitacoraVenta, id=bitacora_id, tienda=tienda)

    from .reportes import generar_pdf_recibo_inline
    return generar_pdf_recibo_inline(bitacora)


@tienda_login_required
def inventario_view(request):
    """Vista para el módulo de inventario"""
    usuario_tienda = get_current_usuario_tienda(request)
    tienda = get_current_tienda(request)

    from Categoria.models import Categoria
    from .forms import BitacoraVentaForm

    categorias = Categoria.objects.all().order_by('nombre')
    form = BitacoraVentaForm()

    context = {
        'categorias': categorias,
        'form': form,
        'usuario_tienda': usuario_tienda,
        'tienda': tienda
    }

    return render(request, 'venta_tienda/inventario.html', context)


@tienda_login_required
@require_POST
def procesar_inventario(request):
    """Procesar el registro de inventario (sin generar PDF)"""
    try:
        data = json.loads(request.body)
        items = data.get('productos', [])
        observaciones = data.get('observaciones', '')

        if not items:
            return JsonResponse({'status': 'error', 'message': 'No hay items en el inventario'})

        usuario_tienda = get_current_usuario_tienda(request)
        tienda = get_current_tienda(request)

        # Crear la bitácora de inventario (sin información del cliente)
        bitacora = BitacoraVenta.objects.create(
            tienda=tienda,
            usuario_tienda=usuario_tienda,
            observaciones=observaciones,
            tipo='inventario'  # Tipo inventario
        )

        # Crear los detalles de la bitácora
        for item in items:
            item_id = item['id']
            cantidad = item['cantidad']

            # Determinar si es producto o receta
            if item_id.startswith('producto_'):
                producto_id = int(item_id.replace('producto_', ''))
                producto = get_object_or_404(Producto, id=producto_id)

                DetalleBitacora.objects.create(
                    bitacora=bitacora,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta
                )

            elif item_id.startswith('receta_'):
                receta_id = int(item_id.replace('receta_', ''))
                receta = get_object_or_404(Receta, id=receta_id)

                DetalleBitacora.objects.create(
                    bitacora=bitacora,
                    receta=receta,
                    cantidad=cantidad,
                    precio_unitario=receta.precio_venta
                )

        # Actualizar el total
        bitacora.actualizar_total()
        bitacora.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Inventario registrado correctamente',
            'inventario_id': bitacora.id,
            'numero_recibo': bitacora.numero_recibo
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error al procesar inventario: {str(e)}'})
    

@tienda_login_required
@require_POST
def procesar_venta(request):
    """Procesar la venta usando BitacoraVenta (sin afectar stock)"""
    try:
        data = json.loads(request.body)
        items = data.get('productos', [])  # Puede contener productos y recetas
        observaciones = data.get('observaciones', '')
        cliente_data = data.get('cliente', {})

        if not items:
            return JsonResponse({'status': 'error', 'message': 'No hay items en la venta'})

        usuario_tienda = get_current_usuario_tienda(request)
        tienda = get_current_tienda(request)

        # Crear la bitácora de venta con información del cliente
        bitacora = BitacoraVenta.objects.create(
            tienda=tienda,
            usuario_tienda=usuario_tienda,
            observaciones=observaciones,
            cliente_nit=cliente_data.get('nit', 'CF'), # y los datos del usuario???????
            cliente_nombre=cliente_data.get('nombre', 'Consumidor Final'),
            cliente_direccion=cliente_data.get('direccion', 'Ciudad'),
            fecha=datetime.now()
        )
        # Crear los detalles de la bitácora
        for item in items:
            item_id = item['id']
            cantidad = item['cantidad']

            # Determinar si es producto o receta
            if item_id.startswith('producto_'):
                producto_id = int(item_id.replace('producto_', ''))
                producto = get_object_or_404(Producto, id=producto_id)

                DetalleBitacora.objects.create(
                    bitacora=bitacora,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta
                )

            elif item_id.startswith('receta_'):
                receta_id = int(item_id.replace('receta_', ''))
                receta = get_object_or_404(Receta, id=receta_id)

                DetalleBitacora.objects.create(
                    bitacora=bitacora,
                    receta=receta,
                    cantidad=cantidad,
                    precio_unitario=receta.precio_receta
                )

        # Actualizar el total de la bitácora
        bitacora.actualizar_total()
        fel(request,bitacora.id)

        if fel:
            b = BitacoraVenta.objects.get(id=bitacora.id)
            return JsonResponse({
                    'status': 'success',
                    'message': 'Venta procesada correctamente',
                    'venta_id': b.id,
                    'link': b.link,
                    'bitacora_id': b.id,
                    'numero_recibo': b.numero_recibo,
            })
      

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error al procesar venta: {str(e)}'})




# FEL
@tienda_login_required
def fel(request, id):
            factura = BitacoraVenta.objects.filter(id=id)
            factura_ver = BitacoraVenta.objects.get(id=id)
            detalle = DetalleBitacora.objects.filter(bitacora=id)
            cd = DetalleBitacora.objects.filter(bitacora=id).aggregate(
                cantidad=Sum('cantidad'))  # total de la venta
            total = DetalleBitacora.objects.filter(bitacora=id).aggregate(
                tot=Sum('subtotal'))  # total de la venta
            miventa = DetalleBitacora.objects.filter(bitacora=id).aggregate(
                t=Sum('subtotal'))  # total de la venta


            #BitacoraVenta.objects.filter(id=id).update(
            #    cliente_nit=request.POST["cliente-nit"], cliente_nombre=request.POST["cliente-nombre"], cliente_direccion=request.POST["cliente-direccion"], estado=1)
            # miventa = Venta.objects.filter(factura=id).values_list('nit','direccion','negocio')
            # facturar(request,id)

            # crear el DTE a Certificar

            dte_fel_a_certificar = InfileFel.fel_dte()  # aki mandamos el correlativo

            # crear el emisor
            emisor_fel = emisor.emisor()

            # crear el receptor
            receptor_fel = receptor.receptor()

            # crear los totales
            total_fel = InfileFel.totales()

            # totales impuestos
            totales_impuestos = InfileFel.total_impuesto()

            for datoscliente in BitacoraVenta.objects.filter(id=id):
                print(datoscliente.cliente_nit, datoscliente.cliente_nombre,
                      datoscliente.cliente_direccion)

            if datoscliente.tienda.pk == 1:
                # Setear dirección del emisor
                emisor_fel.set_direccion(
                        'CALLE REAL 5-38 BARRIO ARRIBA ZONA 3 SAN JERONIMO, BAJA VERAPAZ \n',
                        '15001', 'TEL.', '3010-7086', 'GT'
                    )

                # Setear datos del emisor
                emisor_fel.set_datos_emisor(
                        'GEN', '1', 'atencion@friturasdeoriente.com', '98276522',
                        'POLLO EXPRESS', 'SALGUERO OVALLE COPROPIEDADO'
                    )

                # Setear dirección del receptor
                receptor_fel.set_direccion(
                        factura_ver.cliente_direccion, '14001', 'Baja Verapaz', 'guatemala', 'GT'
                    )
            elif datoscliente.tienda.pk == 2:

                # Setear dirección del emisor
                emisor_fel.set_direccion(
                        '3 CALLE CANTON ILOM CHAJUL, QUICHE \n',
                        '14005', 'TEL.', '3010-7086', 'GT'
                    )

                # Setear datos del emisor
                emisor_fel.set_datos_emisor(
                        'GEN', '2', 'atencion@friturasdeoriente.com', '98276522',
                        'POLLO EXPRESS', 'SALGUERO OVALLE COPROPIEDAD'
                    )

                # Setear dirección del receptor
                receptor_fel.set_direccion(
                        factura_ver.cliente_direccion, '14005', 'Quiche', 'guatemala', 'GT'
                    )


            elif datoscliente.tienda.pk == 3:

                # Setear dirección del emisor
                emisor_fel.set_direccion(
                        'BARRIO EL CENTRO 1-01 ZONA 1 RIO HONDO,ZACAPA \n',
                        '19003', 'TEL.', '3010-7086', 'GT'
                    )

                # Setear datos del emisor
                emisor_fel.set_datos_emisor(
                        'GEN', '3', 'atencion@friturasdeoriente.com', '98276522',
                        'POLLO EXPRESS', 'SALGUERO OVALLE COPROPIEDAD'
                    )

                # Setear dirección del receptor
                receptor_fel.set_direccion(
                        factura_ver.cliente_direccion, '19003', 'Zacapa', 'guatemala', 'GT'
                    )    

            elif datoscliente.tienda.pk == 4:

                # Setear dirección del emisor
                emisor_fel.set_direccion(
                        'AVENIDA PUENTE FRENTE AL MERCADO SACAPULAS, QUICHE \n',
                        '14001', 'TEL.', '3010-7086', 'GT'
                    )

                # Setear datos del emisor
                emisor_fel.set_datos_emisor(
                        'GEN', '4', 'atencion@friturasdeoriente.com', '98276522',
                        'POLLO EXPRESS', 'SALGUERO OVALLE COPROPIEDAD'
                    )

                # Setear dirección del receptor
                receptor_fel.set_direccion(
                        factura_ver.cliente_direccion, '14001', 'Quiche', 'guatemala', 'GT'
                    )    

            elif datoscliente.tienda.pk == 5:

                # Setear dirección del emisor
                emisor_fel.set_direccion(
                        '2 CALLE A BARRIO ARRIBA ZONA 1 ESTANZUELA,ZACAPA \n',
                        '19002', 'TEL.', '3010-7086', 'GT'
                    )

                # Setear datos del emisor
                emisor_fel.set_datos_emisor(
                        'GEN', '5', 'atencion@friturasdeoriente.com', '98276522',
                        'POLLO EXPRESS', 'SALGUERO OVALLE COPROPIEDAD'
                    )

                # Setear dirección del receptor
                receptor_fel.set_direccion(
                        factura_ver.cliente_direccion, '19002', 'Zacapa', 'guatemala', 'GT'
                    )       

            elif datoscliente.tienda.pk == 6:

                # Setear dirección del emisor
                emisor_fel.set_direccion(
                        'BARRIO SAN SEBASTIAN SAN AGUSTIN ACASAGUASTLAN, EL PROGRESO \n',
                        '02003', 'TEL.', '3010-7086', 'GT'
                    )

                # Setear datos del emisor
                emisor_fel.set_datos_emisor(
                        'GEN', '6', 'atencion@friturasdeoriente.com', '98276522',
                        'POLLO EXPRESS', 'SALGUERO OVALLE COPROPIEDAD'
                    )

                # Setear dirección del receptor
                receptor_fel.set_direccion(
                        factura_ver.cliente_direccion, '02003', 'El Progreso', 'guatemala', 'GT'
                    )      

            elif datoscliente.tienda.pk == 7:

                # Setear dirección del emisor
                emisor_fel.set_direccion(
                        '3 CALLE A 7-47 ZONA 1 CHICAMAN,QUICHE \n',
                        '14020', 'TEL.', '3010-7086', 'GT'
                    )

                # Setear datos del emisor
                emisor_fel.set_datos_emisor(
                        'GEN', '7', 'atencion@friturasdeoriente.com', '98276522',
                        'POLLO EXPRESS', 'SALGUERO OVALLE COPROPIEDAD'
                    )

                # Setear dirección del receptor
                receptor_fel.set_direccion(
                        factura_ver.cliente_direccion, '14020', 'Quiche', 'guatemala', 'GT'
                    )                


            else:
                # Setear dirección del emisor
                emisor_fel.set_direccion(
                        '2 AVENIDA 3-022 CANTON BATZBACA ZONA 0 NEBAJ,QUICHE \n',
                        '14013', 'TEL.', '3010-7086', 'GT'
                    )

                # Setear datos del emisor
                emisor_fel.set_datos_emisor(
                        'GEN', '8', 'atencion@friturasdeoriente.com', '98276522',
                        'POLLO EXPRESS', 'SALGUERO OVALLE COPROPIEDAD'
                    )

                # Setear dirección del receptor
                receptor_fel.set_direccion(
                        factura_ver.cliente_direccion, '14013', 'Quiche', 'guatemala', 'GT'
                    )



            # Setear datos del receptor
            receptor_fel.set_datos_receptor(
                    'atencion@friturasdeoriente.com', factura_ver.cliente_nit, factura_ver.cliente_nombre
                )
            
            # identificador unico del dte del cliente
            dte_fel_a_certificar.set_clave_unica(f'2022252{id}')  # no importa

            # setear datos generales
            dte_fel_a_certificar.set_datos_generales(
                'GTQ', f'{datoscliente.fecha}T00:00:00-06:00', 'FACT')  # fecha de venta

            # agregar los datos del emisor
            dte_fel_a_certificar.set_datos_emisor(emisor_fel)
            # agregar los datos del receptor
            dte_fel_a_certificar.set_datos_receptor(receptor_fel)

            # agregar las frases
            dte_fel_a_certificar.frase_fel.set_frase('1', '1')
            #dte_fel_a_certificar.frase_fel.set_frase('1', '2')
            # dte_fel_a_certificar.frase_fel.set_frase('1','1','20185687029123456789','2018-10-11')

            num = 1
            acutotal = 0
            acuiva = 0
            miventa = 0
            for item in DetalleBitacora.objects.filter(bitacora=id):

                num = num+1

                item_1 = InfileFel.item()

                item_1_impuesto = InfileFel.impuesto()

                # llenar el item con los datos necesarios
                item_1.set_numero_linea(num)  # esto falta
                item_1.set_bien_o_servicio('B')
                item_1.set_cantidad(item.cantidad)
                item_1.set_unidad_medida('UND')  # no se puede cambiar
                item_1.set_descripcion(item.producto.nombre)
                item_1.set_precio_unitario(item.producto.precio_venta)
                item_1.set_precio(item.cantidad*item.precio_unitario)
                item_1.set_descuento(0)
                item_1.set_total(item.subtotal)

                grav = round((item.subtotal/112)*100, 2)
                iva = round((grav*12)/100, 2)

                # llenar los impuestos del item
                item_1_impuesto.set_monto_impuesto(iva)
                item_1_impuesto.set_monto_gravable(grav)
                item_1_impuesto.set_codigo_unidad_gravable(1)
                item_1_impuesto.set_nombre_corto('IVA')
                item_1.set_impuesto(item_1_impuesto)

                acutotal = acutotal + grav
                acuiva = acuiva + iva
                miventa = miventa + item.subtotal

                # Agregar el item 1
                dte_fel_a_certificar.agregar_item(item_1)

                # agregar el gran total

            total_fel.set_gran_total(miventa)

            # agregar datos del gran total de impuestos

            totales_impuestos.set_nombre_corto('IVA')
            totales_impuestos.set_total_monto_impuesto(acuiva)

            total_fel.set_total_impuestos(totales_impuestos)

            # agregar los totales
            dte_fel_a_certificar.agregar_totales(total_fel)

          
            print("#### CERTIFICANDO FACTURA ####")

            # contingencia
            # dte_fel_a_certificar.set_acceso('123123')

            # agregando el tipo de personeria
            # dte_fel_a_certificar.set_tipo_personeria('2')

            # realizar el llamado a la certificada
            certificacion_fel = dte_fel_a_certificar.certificar()
            if (certificacion_fel["resultado"]):
                print("UUID:" + certificacion_fel["uuid"])
                print("FECHA:" + certificacion_fel["fecha"])
                print("SERIE:" + certificacion_fel["serie"])
                print("numero:" + str(certificacion_fel["numero"]))
                total = DetalleBitacora.objects.filter(bitacora=id).aggregate(
                    tot=Sum('subtotal'))  # total de la venta
                messages.info(
                    request, f"https://report.feel.com.gt/ingfacereport/ingfacereport_documento?uuid={certificacion_fel['uuid']}")
                BitacoraVenta.objects.filter(id=id).update(fecha_fel=str(certificacion_fel['fecha']), estado=1, link=f"https://report.feel.com.gt/ingfacereport/ingfacereport_documento?uuid={certificacion_fel['uuid']}", anula=certificacion_fel['uuid'], serie=certificacion_fel['serie'], numero=certificacion_fel['numero'])
                # Venta.objects.filter(factura=id).update(link=f"https://report.feel.com.gt/ingfacereport/ingfacereport_documento?uuid={certificacion_fel['uuid']}")
                # messages.info(request,factura_ver.link)
                return redirect('/procesar-venta/')

            else:
                print("No pudo ser certificada")
                print("Descripcion: " + certificacion_fel["descripcion"])

                for error_fel in certificacion_fel["descripcion_errores"]:
                    print("Mensaje Error: " + error_fel["fuente"])
                    print("fuente: " + error_fel["mensaje_error"])
                    print("categoria: " + error_fel["categoria"])
                    print("numeral: " + error_fel["numeral"])
                    print("validacion: " + error_fel["validacion"])

      

        ###################################################################################################################################

    # return render(request,"PagoApp/pagoefectivo.html",{'factura':factura,'detalle':detalle,'cd':cd,'total':total,'id':id})


@tienda_login_required
def anularfel(request, id):
        print('#### Anulando ####')
        datoscliente = BitacoraVenta.objects.get(id=id)

        dte_fel_a_anular = InfileFel.fel_dte()

        # realizar el llamado a la certificada
        certificacion_fel = dte_fel_a_anular.anular(str(datoscliente.fecha_fel), '98276522', str(
            datoscliente.fecha_fel), datoscliente.cliente_nit, datoscliente.anula, datoscliente.serie)
        if (certificacion_fel["resultado"]):
            print("UUID:" + certificacion_fel["uuid"])
            print("FECHA:" + certificacion_fel["fecha"])
            print("SERIE:" + certificacion_fel["serie"])
            print("numero:" + str(certificacion_fel["numero"]))
        else:
            print("No pudo ser certificada")
            print("Descripcion: " + certificacion_fel["descripcion"])

            for error_fel in certificacion_fel["descripcion_errores"]:
                print("Mensaje Error: " + error_fel["fuente"])
                print("fuente: " + error_fel["mensaje_error"])
                print("categoria: " + error_fel["categoria"])
                print("numeral: " + error_fel["numeral"])
                print("validacion: " + error_fel["validacion"])

        total = DetalleBitacora.objects.all().filter(bitacora=id).aggregate(
            tot=Sum('subtotal'))  # total de la venta
        BitacoraVenta.objects.filter(id=id).update(fecha_fel=datoscliente.fecha_fel, estado=2)
        #messages.success(request, 'Anulacion FEL Exitosa')
        return redirect('venta_tienda:reimpresion')    


#################   CONTROL DIARIO - TIENDA   #############

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from VentaTienda.models import ControlDiario, UsuarioTienda
from VentaTienda.forms import ControlDiarioForm
from VentaTienda.views import normalizar_nombre_campo


def crear_control_diario(request):
    """Vista para que empleados de tienda creen el control diario"""

    # Verificar sesión
    if 'usuario_tienda_id' not in request.session:
        messages.error(request, 'Debe iniciar sesión')
        return redirect('venta_tienda:login')
    
    usuario_tienda = get_object_or_404(UsuarioTienda, id=request.session['usuario_tienda_id'])
    tienda = usuario_tienda.tienda
    fecha_hoy = timezone.now().date()

    # Verificar si ya existe un control para HOY
    existe_control = ControlDiario.objects.filter(tienda=tienda, fecha=fecha_hoy).exists()

    # ============================================================
    # GET → Mostrar formulario
    # ============================================================
    if request.method == 'GET':

        if existe_control:
            messages.warning(request, 'Ya existe un control diario para el día de hoy.')
            form = None

        else:
            form = ControlDiarioForm()

        # Cargar saldos finales del día anterior para prellenar "Inicio"
        # Buscar el control más reciente de esta tienda (puede ser ayer u otro día)
        control_anterior = ControlDiario.objects.filter(
            tienda=tienda,
            fecha__lt=fecha_hoy
        ).order_by('-fecha').first()

        saldos_iniciales = {}
        
        if control_anterior and control_anterior.productos_saldos:
            saldos_anterior = control_anterior.productos_saldos
            print(f"[DEBUG] Control anterior encontrado: fecha={control_anterior.fecha}, tienda={tienda.id}")
            print(f"[DEBUG] Saldos anterior: {saldos_anterior}")
            
            for producto in ControlDiarioForm.PRODUCTOS_SALDOS:
                # Buscar por nombre exacto del producto
                datos = saldos_anterior.get(producto, {})
                valor_final = float(datos.get('final', 0)) if isinstance(datos, dict) else 0
                saldos_iniciales[producto] = valor_final
                if valor_final > 0:
                    print(f"[DEBUG] {producto} -> final={valor_final}")
        else:
            print(f"[DEBUG] No se encontró control anterior para tienda={tienda.id}, fecha_hoy={fecha_hoy}")
            # Si no hay control anterior, iniciar en 0
            for producto in ControlDiarioForm.PRODUCTOS_SALDOS:
                saldos_iniciales[producto] = 0
        
        print(f"[DEBUG] saldos_iniciales: {saldos_iniciales}")

        context = {
            'form': form,
            'usuario_tienda': usuario_tienda,
            'tienda': tienda,
            'fecha_hoy': fecha_hoy,
            'existe_control': existe_control,
            'productos_saldos': ControlDiarioForm.PRODUCTOS_SALDOS,
            'productos_venta': ControlDiarioForm.PRODUCTOS_VENTA,
            'conceptos_fechas': ControlDiarioForm.CONCEPTOS_FECHAS,
            'saldos_iniciales': saldos_iniciales,
        }

        # Precios por defecto
        context['default_precios'] = {
            'Pollo': 72, 'Papas': 7, 'Hamburguesa': 15, 'Ensaladas': 5, 'Pay': 5,
            'Gran pieza': 15, 'Mollejas': 12, 'Medallones de 4': 6, 'Medallones de 8': 12,
            'Soda Lata': 6, 'Soda desechable': 8, 'agua pura botella': 5,
            'agua pura bolsa': 1, 'ISO MAX': 2, 'coca vidrio': 4,
        }

        return render(request, 'venta_tienda/control_diario_form.html', context)

    # ============================================================
    # POST → Guardar datos del formulario
    # ============================================================
    if request.method == 'POST':

        if existe_control:
            messages.error(request, 'Ya existe un control diario para hoy.')
            return redirect('venta_tienda:menu_principal')

        form = ControlDiarioForm(request.POST)

        if form.is_valid():

            control = form.save(commit=False)
            control.tienda = tienda
            control.usuario_tienda = usuario_tienda
            control.fecha = fecha_hoy

            # -----------------------------------
            # TABLA 1: Productos y Saldos
            # -----------------------------------
            productos_saldos = {}

            for producto in ControlDiarioForm.PRODUCTOS_SALDOS:
                key = normalizar_nombre_campo(producto)

                inicio = float(request.POST.get(f'saldo_{key}_inicio', 0) or 0)
                ingreso = float(request.POST.get(f'saldo_{key}_ingreso', 0) or 0)
                salida = float(request.POST.get(f'saldo_{key}_salida', 0) or 0)
                final = inicio + ingreso - salida

                productos_saldos[producto] = {
                    'inicio': inicio,
                    'ingreso': ingreso,
                    'salida': salida,
                    'final': final,
                }

            control.productos_saldos = productos_saldos

            # -----------------------------------
            # TABLA 2: Ventas
            # -----------------------------------
            venta_productos = {}
            total_venta_calculado = 0

            for producto in ControlDiarioForm.PRODUCTOS_VENTA:
                key = normalizar_nombre_campo(producto)

                cantidad = int(request.POST.get(f'venta_{key}_cantidad', 0) or 0)
                precio = float(request.POST.get(f'venta_{key}_precio', 0) or 0)
                total = cantidad * precio

                venta_productos[producto] = {
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'total': total
                }

                total_venta_calculado += total

            control.venta_productos = venta_productos
            control.total_venta = total_venta_calculado

            # -----------------------------------
            # TABLA 4: Gastos
            # -----------------------------------
            gastos = []
            idx = 0
            while f'gasto_descripcion_{idx}' in request.POST:
                descripcion = request.POST.get(f'gasto_descripcion_{idx}', '').strip()
                if descripcion:
                    gastos.append({
                        'descripcion': descripcion,
                        'no_factura': request.POST.get(f'gasto_factura_{idx}', ''),
                        'cantidad': float(request.POST.get(f'gasto_cantidad_{idx}', 0) or 0)
                    })
                idx += 1

            control.gastos = gastos
            control.gasto_diario = sum(g['cantidad'] for g in gastos)

            # -----------------------------------
            # TABLA 5: Fechas de control
            # -----------------------------------
            fechas_control = {}

            for concepto in ControlDiarioForm.CONCEPTOS_FECHAS:
                key = normalizar_nombre_campo(concepto)
                fecha = request.POST.get(f'fecha_{key}', '')

                if fecha:
                    fechas_control[concepto] = fecha

            control.fechas_control = fechas_control

            # -----------------------------------
            # TOTAL A DEPOSITAR
            # -----------------------------------
            control.total_depositar = control.total_venta - control.gasto_diario

            control.save()

            messages.success(request, 'Control diario registrado exitosamente.')
            return redirect('venta_tienda:menu_principal')

    return redirect('venta_tienda:menu_principal')
