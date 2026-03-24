from Venta import views
from django.urls import path
from django.conf import settings#para agregar la ruta de la imagen 
from django.conf.urls.static import static#para agregar la ruta de la imagen 

urlpatterns = [
    path('nueva-venta/', views.nueva_venta, name='NuevaVenta'),
    path('eliminar-detalle/<int:detalle_id>/', views.eliminar_detalle, name='EliminarDetalle'),
    path('get-items-tienda/', views.get_items_tienda, name='GetItemsTienda'),
    path('listado-ventas/', views.listado_ventas, name='ListadoVentas'),
    path('anular-venta/<int:venta_id>/', views.anular_venta, name='AnularVenta'),
    path('detalle-venta/<int:venta_id>/', views.detalle_venta, name='DetalleVenta'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)