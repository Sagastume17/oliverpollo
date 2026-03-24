from Receta import views
from django.urls import path

urlpatterns = [
    path('nuevareceta/',views.nueva,name="NuevaReceta"),
    path('detallereceta/<str:t>',views.detallereceta,name="DetalleReceta"),
    path('listareceta/',views.lista,name="ListaReceta"),
    path('listareceta2/',views.lista2,name="ListaReceta2"),
    path('listasolicitudrecetas/',views.listapedidos,name="ListaPedidosReceta"),
    path('solicitarreceta/<str:t>',views.aplicar,name="AplicarReceta"),
    path('darbajareceta/<int:receta>',views.bajareceta,name='BajaReceta'),
    path('daraltareceta/<int:receta>',views.altareceta,name='AltaReceta'),
    path('obtener-productos/<int:tienda_id>/', views.obtener_productos, name='obtener_productos'),
]
