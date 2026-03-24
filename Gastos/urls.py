from Gastos import views
from django.urls import path
from django.conf import settings#para agregar la ruta de la imagen 
from django.conf.urls.static import static#para agregar la ruta de la imagen 

urlpatterns = [
    path('nuevo-gasto/',views.nuevo,name="NuevoGasto"),
    path('listado-gastos/',views.listado,name="ListaGasto"),
    path('actualizar-gasto/<int:id>',views.actualizar,name="UpdateGasto"),
    path('eliminiar-gasto/<int:id>',views.eliminar,name="DeleteGasto"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)