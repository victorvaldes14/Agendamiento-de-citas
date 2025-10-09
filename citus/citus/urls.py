from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from citas import views as v

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página pública
    path('', v.inicio, name='inicio'),
    path('registro/', v.registro, name='registrarse'),
    path('agendar/', v.agendar_cita_publica, name='agendar_cita_publica'),
    path('horas/', v.obtener_horas_disponibles, name='obtener_horas_disponibles'),

    # Autenticación (login/logout)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),

    # Paneles
    path('panel/', v.panel_usuario, name='panel_usuario'),
    path('peluquero/', v.panel_peluquero, name='panel_peluquero'),
    path('admin_panel/', v.panel_admin, name='panel_admin'),

    # Funciones de peluquero
    path('peluquero/cita/<int:cita_id>/editar/', v.editar_cita_peluquero, name='editar_cita_peluquero'),
    path('peluquero/cita/<int:cita_id>/eliminar/', v.eliminar_cita_peluquero, name='eliminar_cita_peluquero'),
    path('peluquero/cita/<int:cita_id>/atendida/', v.marcar_cita_atendida, name='marcar_cita_atendida'),

]
