from decimal import Decimal
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user.models import User
from Facturar.models import Facturar
from Facturar.forms import FacturarForm,UpdateFacturarForm
from datetime import datetime


@login_required
def nueva(request):
  
    form = FacturarForm()
    if request.method == 'POST':

        form = FacturarForm(request.POST)
        if form.is_valid():
            try:
                
                f = Facturar()
                f.facturar = form.cleaned_data['facturar']
                f.fecha = form.cleaned_data['fecha']
                f.usuario = User.objects.get(id=request.user.id)
                f.save()
                messages.success(request,f'Facturacion Ingresada Correctamente!')
                return redirect('NuevaFactura')

            except:
                messages.error(request,f'Error Al Ingresar Factuar!')
                return redirect('NuevaFactura')
        


    return render(request,'Facturar/nueva.html',{'form':form})
    


@login_required
def listado(request):

    prod = Facturar.objects.all().order_by('fecha')

    return render(request,'Facturar/listado.html',{'p':prod})


@login_required
def eliminar(request,id):
    
    prod = Facturar.objects.get(id=id)
    prod.delete()
    messages.success(request, f'Factuarcion Eliminada Exitosamente!')
    return redirect('ListaFactura')


@login_required
def actualizar(request,id):
    p = Facturar.objects.get(id=id)
    if request.method == 'GET':
        form = UpdateFacturarForm(instance=p)
    else:
        form = UpdateFacturarForm(request.POST,instance = p)
     
        if form.is_valid():
            try:
                p.fecha_mod = datetime.today()
                p.usuario = User.objects.get(id=request.user.id)
                form.save()
                messages.success(request, f'Facturacion Modificado Exitosamente!')
                return redirect('ListaFactura')
            except:
                messages.error(request, f'No Se Pudo Modificar Facturacion!')
                return redirect('ListaFactura')

    return render(request,'Facturar/actualizar.html',{'form':form})