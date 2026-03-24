from django.urls import path
from . import views

app_name = 'venta_tienda'

urlpatterns = [
    path('', views.menu_principal, name='menu_principal'),
    path('venta/', views.venta_view, name='venta'),
    path('caja/', views.caja_view, name='caja'),
    path('reimpresion/', views.reimpresion_view, name='reimpresion'),
    path('inventario/', views.inventario_view, name='inventario'),
    path('consulta-movimientos/', views.consulta_movimientos_view, name='consulta_movimientos'),
    path('detalle-bitacora/<int:bitacora_id>/', views.detalle_bitacora, name='detalle_bitacora'),
    path('pdf-recibo/<str:numero_recibo>/', views.descargar_pdf_recibo, name='pdf_recibo'),
    path('pdf-venta/<int:bitacora_id>/', views.generar_pdf_venta, name='pdf_venta'),
    path('api/productos-categoria/<int:categoria_id>/', views.get_productos_categoria, name='productos_categoria'),
    path('api/procesar-venta/', views.procesar_venta, name='procesar_venta'),
    path('api/procesar-inventario/', views.procesar_inventario, name='procesar_inventario'),
    path('api/ultimas-ventas/', views.ultimas_ventas, name='ultimas_ventas'),
    path('anular-fel/<int:id>', views.anularfel, name='AnularFel'),
    path('cierre-diario/', views.cierre_diario, name='cierre_diario'),
    path('cierre-diario/pdf/<int:cierre_id>/', views.descargar_pdf_cierre, name='descargar_pdf_cierre'),
    path('cierres/', views.listar_cierres, name='listar_cierres'),
     
    #################   CONTROL DIARIO    ####################
    path('control-diario/nuevo/', views.crear_control_diario, name='crear_control_diario'),

]