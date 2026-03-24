from django.shortcuts import render,redirect
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Categoria.models import Categoria
from Categoria.forms import CategoriaForm,UpdateCategoriaForm
from user.models import User
from django.utils.timezone import now


@login_required
def nueva(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.usuario = request.user
            categoria.fecha = now().strftime('%d-%m-%Y')
            categoria.save()
            messages.success(request, "Categoría guardada correctamente.")
            return redirect('ListaCategoria')  # Reemplaza con la URL que corresponda
        else:
            messages.error(request, "Error al guardar la categoría.")
    else:
        form = CategoriaForm()
    
    return render(request, 'Categoria/nueva.html', {'form': form})



@login_required
def listado(request):
    datos = Categoria.objects.all().order_by('id')
    return render(request,'Categoria/lista.html',{'cate':datos})


@login_required
def actualizar(request, id):
    cate = Categoria.objects.get(id=id)
    
    if request.method == 'GET':
        form = UpdateCategoriaForm(instance=cate)
    else:
        form = UpdateCategoriaForm(request.POST, request.FILES, instance=cate)  # <- Aquí está la clave
        if form.is_valid():
            try:
                cate.fecha = str(datetime.today().strftime('%Y-%m-%d'))
                cate.usuario = request.user  # Puedes usar directamente el usuario actual
                form.save()
                messages.success(request, f'Categoría {cate.nombre} modificada exitosamente!')
                return redirect('ListaCategoria')
            except Exception as e:
                messages.error(request, f'No se pudo modificar {cate.nombre}: {e}')
                return redirect('ListaCategoria')

    return render(request, 'Categoria/actualizar.html', {'form': form})

    
    

@login_required
def eliminar(request,id):
    try:
        cate = Categoria.objects.get(id=id)
        cate.delete()
        messages.success(request,f'{cate.nombre} Eliminado!')
        return redirect('ListaCategoria')
    except:
        messages.error(request,f'No Se Puede Eliminar {cate.nombre}')
        return redirect('ListaCategoria')        

