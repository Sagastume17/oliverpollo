from Cierre import views, reportes
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('nuevo-cierre/', views.nuevo, name="NuevoCierre"),
    path('listado-cierres/', views.listado, name="ListaCierre"),
    path('actualizar-cierre/<int:id>', views.actualizar, name="UpdateCierre"),
    path('eliminiar-cierre/<int:id>', views.eliminar, name="DeleteCierre"),
    path('tiendas/', views.listado_tiendas, name='listado_tiendas'),
    path('tienda/<int:tienda_id>/cierres/', views.cierres_por_tienda, name='cierres_tienda'),
    path("pdf/<int:cierre_id>/", views.descargar_pdf_cierre, name="descargar_pdf_cierre"),
    
    # URLs para el módulo de cuadre
    path('cuadre/nuevo/', reportes.nuevo_cuadre, name='nuevo_cuadre'),
    path('cuadre/lista/', reportes.listar_cuadres, name='listar_cuadres'),
    path('cuadre/editar/<int:pk>/', reportes.editar_cuadre, name='editar_cuadre'),
    path('cuadre/eliminar/<int:pk>/', reportes.eliminar_cuadre, name='eliminar_cuadre'),
    path('cuadre/pdf/<int:pk>/', reportes.generar_pdf_cuadre, name='generar_pdf_cuadre'),
    path('cuadre/preview/', reportes.actualizar_preview_cuadre, name='actualizar_preview_cuadre'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)