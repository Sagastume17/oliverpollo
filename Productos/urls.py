from Productos import views
from django.urls import path
from django.conf import settings  # Para agregar la ruta de la imagen 
from django.conf.urls.static import static  # Para agregar la ruta de la imagen 

urlpatterns = [
    path('nuevo-producto/', views.nuevo_producto, name="NuevoProducto"),
    path('listado-productos/', views.listado_productos, name="ListaProducto"),
    path('actualizar-producto/<int:id>/', views.actualizar_producto, name="UpdateProducto"),
    # path('eliminar-producto/<int:id>/', views.eliminar_producto, name="DeleteProducto"),
    path('productos/tienda/<int:tienda>/', views.productos_por_tienda, name='productos_por_tienda'),
    path('ingreso-producto/<int:producto_id>/', views.ingreso_producto, name="IngresoProducto"),
    path('productos-baja/', views.listado_productos_baja, name="ProductosBaja"),
    path('cambiar-estado-producto/<int:producto_id>/', views.cambiar_estado_producto, name="CambiarEstadoProducto"),
    
    #insumos
    path('insumos/', views.listar_insumos, name='listar_insumos'),
    path('insumos/nuevo/', views.crear_insumo, name='crear_insumo'),
    path('insumos/editar/<int:id>/', views.editar_insumo, name='editar_insumo'),
    path('insumos/eliminar/<int:id>/', views.eliminar_insumo, name='eliminar_insumo'),
]

# Solo agregar static en modo DEBUG (desarrollo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)