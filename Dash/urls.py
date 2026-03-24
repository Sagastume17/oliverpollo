from Dash import views
from django.urls import path
from django.conf import settings#para agregar la ruta de la imagen 
from django.conf.urls.static import static#para agregar la ruta de la imagen 

urlpatterns = [
    path('admin/',views.admin,name="Admin"),
    path('dash/',views.dash,name="Dash"),
    path('nueva-tienda/',views.tienda,name="NuevaTienda"),
    path('listado-tiendas/',views.listado,name="ListaTiendas"),
    path('actualizar-tienda/<int:id>',views.actualizar,name="UpdateTienda"),
    path('eliminiar-tienda/<int:id>',views.eliminar,name="DeleteTienda"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)