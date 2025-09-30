"""
URL configuration for citus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from citas import views as v

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Página de inicio
    path('', v.inicio, name='inicio'),
    
    # Autenticación
    path('login/', v.iniciar_sesion, name='login'),
    path('logout/', v.cerrar_sesion, name='logout'),
    path('registro/', v.registro, name='registrarse'),
    
    # Panel de usuario
    path('panel/', v.panel_usuario, name='panel_usuario'),
    
    # Gestión de citas
    path('agendar/', v.agendar_cita, name='agendar_cita'),
    path('cita/<int:cita_id>/', v.detalle_cita, name='detalle_cita'),
    path('cita/<int:cita_id>/cancelar/', v.cancelar_cita, name='cancelar_cita'),
]