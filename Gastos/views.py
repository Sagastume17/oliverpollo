from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user.models import User
from Gastos.models import Gastos
from Gastos.forms import GastosForm,UpdateGastosForm
from Dash.models import Tienda
from django.db.models import Q
from datetime import datetime


@login_required
def nuevo(request):
    form = GastosForm()
    
    if request.method == 'POST':
        form = GastosForm(request.POST)
        if form.is_valid():
            try:
                gasto = form.save(commit=False)   # No guardamos aún
                gasto.usuario = request.user      # Asignamos usuario
                # Calculamos el total automáticamente
                gasto.total = gasto.cantidad * gasto.precio
                gasto.save()                       # Guardamos en la DB
                messages.success(request, f'Gasto {gasto.nombre} ingresado correctamente!')
                return redirect('NuevoGasto')
            except Exception as e:
                print("Error al guardar gasto:", e)  # Para depuración
                messages.error(request, f'Error al ingresar gasto {form.cleaned_data.get("nombre","")}!')
                return redirect('NuevoGasto')
    
    return render(request, 'Gastos/nuevo.html', {'form': form})


@login_required
def listado(request):
    # Ordena de más reciente a más antiguo
    prod = Gastos.objects.all().order_by('-fecha')
    return render(request, 'Gastos/listado.html', {'p': prod})




@login_required
def eliminar(request,id):

    prod = Gastos.objects.get(id=id)
    prod.delete()
    messages.success(request, f'Producto {prod.nombre} Eliminado Exitosamente!')
    return redirect('ListaGasto')


@login_required
def actualizar(request, id):
    gasto = Gastos.objects.get(id=id)
    if request.method == 'POST':
        form = UpdateGastosForm(request.POST, instance=gasto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Gasto {gasto.nombre} actualizado correctamente!')
            return redirect('ListaGasto')  # Cambia al URL que uses
        else:
            messages.error(request, 'Error al actualizar el gasto.')
    else:
        form = UpdateGastosForm(instance=gasto)  # Carga los datos actuales
    
    return render(request, 'Gastos/actualizar.html', {'form': form})