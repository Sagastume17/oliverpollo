"""
URL configuration for frituras project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Login.urls')),
    path('inicio/', include('Dash.urls')),
    path('productos/', include('Productos.urls')),
    path('gastos/', include('Gastos.urls')),
    path('cierre/', include('Cierre.urls')),
    path('venta/', include('Venta.urls')),
    path('factura/', include('Facturar.urls')),
    path('usuarios/', include('user.urls')),
    path('receta/', include('Receta.urls')),
    path('categoria/', include('Categoria.urls')),
    path('venta-tienda/', include('VentaTienda.urls')),
    path('empleados/', include('VentaTienda.admin_urls')),
]

# Solo en desarrollo (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
