from Categoria import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.nueva,name="NuevaCategoria"),
    path('listadocategoria/',views.listado,name="ListaCategoria"),
    path('modificarcategoria/<int:id>',views.actualizar,name="UpdateCategoria"),
    path('eliminarcategoria/<int:id>',views.eliminar,name="DeleteCategoria"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)