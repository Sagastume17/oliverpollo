from decimal import Decimal
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user.models import User
from Cierre.models import Cierre
from Cierre.forms import CierreForm,UpdateCierreForm
from Dash.models import Tienda
from django.db.models import Q
from datetime import datetime
from Productos.models import Producto
from Venta.models import Venta
from Gastos.models import Gastos
from django.db.models import Sum


@login_required
def nuevo(request):
    v = Venta.objects.filter(fecha=datetime.today()).aggregate(vt=Sum('total'))
    g = Gastos.objects.filter(fecha=datetime.today()).aggregate(gt=Sum('total'))   

    if v['vt'] == None:
        v['vt'] = 0.00
    else:
        v['vt'] = v['vt'] 

    if g['gt'] == None:
        g['gt'] = 0.00
    else:
        g['gt'] = g['gt']        

    r = v['vt']-g['gt']
  
    form = CierreForm()
    if request.method == 'POST':

        form = CierreForm(request.POST)
        if form.is_valid():
            #try:
                
                c = Cierre()
                c.ventas = v['vt']
                c.gastos = g['gt']
                c.liquido = r
                c.caja = form.cleaned_data['caja']
                c.deposito = form.cleaned_data['deposito']
                c.boleta = form.cleaned_data['boleta']
                c.pollo = form.cleaned_data['pollo']
                c.boleta_pollo = form.cleaned_data['boleta_pollo']
                c.libras = form.cleaned_data['libras']
                c.tienda = Tienda.objects.get(id=form.cleaned_data['tienda'].pk)
                c.usuario = User.objects.get(id=request.user.id)
                c.save()
                messages.success(request,f'Cierre de Venta en Tienda {c.tienda} Ingresado Correctamente!')
                return redirect('NuevoCierre')

            #except:
                #messages.error(request,f'Error Al Ingresar Cierre en Tienda {c.tienda}!')
                #return redirect('NuevoCierre')
        


    return render(request,'Cierre/nuevo.html',{'form':form,'v':v['vt'],'g':g['gt'],'r':r})
    


@login_required
def listado(request):

    prod = Cierre.objects.all().order_by('fecha')

    return render(request,'Cierre/listado.html',{'p':prod})


@login_required
def eliminar(request,id):
    
    prod = Cierre.objects.get(id=id)
    prod.delete()
    messages.success(request, f'Cierre de Tienda {prod.tienda} Eliminado Exitosamente!')
    return redirect('ListaCierre')


@login_required
def actualizar(request,id):
    p = Cierre.objects.get(id=id)
    if request.method == 'GET':
        form = UpdateCierreForm(instance=p)
    else:
        form = UpdateCierreForm(request.POST,instance = p)
     
        if form.is_valid():
            try:
                p.fecha_mod = datetime.today()
                p.usuario = User.objects.get(id=request.user.id)
                form.save()
                messages.success(request, f'Cierre de Tienda {p.tienda} Modificado Exitosamente!')
                return redirect('ListaCierre')
            except:
                messages.error(request, f'No Se Pudo Modificar Cierre de Tienda {p.tienda}!')
                return redirect('ListaCierre')

    return render(request,'Cierre/actualizar.html',{'form':form})
    
    
    
# views.py de la app cierre
from django.shortcuts import render
from django.db.models import Sum
from VentaTienda.models import CierreDiario, Tienda


from django.shortcuts import render, get_object_or_404
from django.utils import timezone

@login_required
def listado_tiendas(request):
    """
    Muestra todas las tiendas con enlace a sus cierres diarios.
    """
    tiendas = Tienda.objects.all().order_by('nombre')
    return render(request, 'Cierre/listado_tiendas.html', {'tiendas': tiendas})



@login_required
def cierres_por_tienda(request, tienda_id):
    """
    Muestra los cierres diarios de una tienda específica.
    """
    tienda = get_object_or_404(Tienda, id=tienda_id)
    # Filtra solo cierres con fecha válida
    cierres = CierreDiario.objects.filter(tienda=tienda).order_by('-fecha')
    
    return render(request, 'Cierre/cierres_tienda.html', {
        'tienda': tienda,
        'cierres': cierres
    })



from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from VentaTienda.views import generar_pdf_ticket_8cm  # si esta función está en utils de venta_tienda

def descargar_pdf_cierre(request, cierre_id):
    cierre = get_object_or_404(CierreDiario, id=cierre_id)
    buffer = generar_pdf_ticket_8cm(cierre.ticket_texto or "")
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cierre_{cierre.fecha}.pdf"'
    return response
