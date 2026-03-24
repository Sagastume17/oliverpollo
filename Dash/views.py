from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user.models import User
from Dash.models import Tienda
from Dash.forms import TiendaForm,UpdateTiendaForm
from django.db.models import Q
from datetime import datetime,time
from decimal import Decimal
from django.http import HttpResponse
#from Dash.reportes import Comprobante

@login_required
def admin(request):
    return render(request,'Dash/admin.html')



@login_required
def dash(request):
    return render(request,'Dash/dash.html')


@login_required
def tienda(request):
    form = TiendaForm()
    if request.method == 'POST':
        form=TiendaForm(request.POST)
        if form.is_valid():
            try:
                t = Tienda()
                t.nombre = form.cleaned_data['nombre']
                t.usuario = User.objects.get(id=request.user.id)
                t.save()
                messages.success(request,f'Tienda {t.nombre} Ingresada Correctamente!')
                return redirect('NuevaTienda')
            except:
                messages.error(request,f'Error al Ingresar Tienda {t.nombre}!')
                return redirect('NuevaTienda')
        
    return render(request,'Dash/tienda.html',{'form':form})



@login_required
def listado(request):

    prod = Tienda.objects.all().order_by('id')

    return render(request,'Dash/listado.html',{'p':prod})


@login_required
def eliminar(request,id):

    prod = Tienda.objects.get(id=id)
    prod.delete()
    messages.success(request, f'Tienda {prod.nombre} Eliminada Exitosamente!')
    return redirect('ListaTiendas')


@login_required
def actualizar(request,id):
    p = Tienda.objects.get(id=id)
    if request.method == 'GET':
        form = UpdateTiendaForm(instance=p)
    else:
        form = UpdateTiendaForm(request.POST,instance = p)
     
        if form.is_valid():
            try:
                p.fecha_mod = datetime.today()
                p.usuario = User.objects.get(id=request.user.id)
                form.save()
                messages.success(request, f'Tienda {p.nombre} Modificada Exitosamente!')
                return redirect('ListaTiendas')
            except:
                messages.error(request, f'No Se Pudo Modificar Tienda {p.nombre}!')
                return redirect('ListaTiendas')

    return render(request,'Dash/tiendaupdate.html',{'form':form})
