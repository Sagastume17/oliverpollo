from Facturar import views
from django.urls import path
from django.conf import settings#para agregar la ruta de la imagen 
from django.conf.urls.static import static#para agregar la ruta de la imagen 

urlpatterns = [
    path('nueva-factura/',views.nueva,name="NuevaFactura"),
    path('listado-factura/',views.listado,name="ListaFactura"),
    path('actualizar-factura/<int:id>',views.actualizar,name="UpdateFactura"),
    path('eliminiar-factura/<int:id>',views.eliminar,name="DeleteFactura"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)