from django.urls import path
from . import admin_views

app_name = 'admin_empleados'

urlpatterns = [
    path('', admin_views.lista_empleados, name='lista'),
    path('crear/', admin_views.crear_empleado, name='crear'),
    path('editar/<int:empleado_id>/', admin_views.editar_empleado, name='editar'),
    path('detalle/<int:empleado_id>/', admin_views.detalle_empleado, name='detalle'),
    path('toggle-activo/<int:empleado_id>/', admin_views.toggle_empleado_activo, name='toggle_activo'),

    # URLs para bitácora de ventas
    path('bitacora/', admin_views.bitacora_lista, name='bitacora_lista'),
    path('bitacora/detalle/<int:bitacora_id>/', admin_views.bitacora_detalle, name='bitacora_detalle'),
    path('bitacora/reporte/', admin_views.generar_reporte_tienda, name='reporte_tienda'),
    path('bitacora/reporte-web/', admin_views.reporte_web_view, name='reporte_web'),
    
    # URLs para Control Diario (Admin)
    path('control-diario/', admin_views.admin_listar_controles, name='control_diario_lista'),
    path('control-diario/<int:control_id>/', admin_views.admin_detalle_control, name='control_diario_detalle'),
]
