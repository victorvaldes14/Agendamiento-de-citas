from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from citas import views as v

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', v.inicio, name='inicio'),
    path('registro/', v.registro, name='registrarse'),
    path('agendar/', v.agendar_cita_publica, name='agendar_cita_publica'),
    path('horas/', v.obtener_horas_disponibles, name='obtener_horas_disponibles'),
    path('cita/<int:cita_id>/reagendar/', v.reagendar_cita, name='reagendar_cita'),


    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', v.logout_view, name='logout'),

    path('panel/', v.panel_usuario, name='panel_usuario'),
    path('panel/cita/<int:cita_id>/cancelar/', v.cancelar_cita, name='cancelar_cita'),
    path('cita/<int:cita_id>/detalle/', v.detalle_cita, name='detalle_cita'),
    path('peluquero/', v.panel_peluquero, name='panel_peluquero'),
    path('peluquero/cita/<int:cita_id>/editar/', v.editar_cita_peluquero, name='editar_cita_peluquero'),
    path('peluquero/cita/<int:cita_id>/eliminar/', v.eliminar_cita_peluquero, name='eliminar_cita_peluquero'),
    path('peluquero/cita/<int:cita_id>/atendida/', v.marcar_cita_atendida, name='marcar_cita_atendida'),
    path('reportes/', v.reportes_basicos, name='reportes_basicos'),
    path('peluquero/cita/<int:cita_id>/finalizar/', v.finalizar_cita, name='finalizar_cita'),
    path('peluquero/cita/<int:cita_id>/reagendar/', v.reagendar_cita_peluquero, name='reagendar_cita_peluquero'),
    path('peluquero/cita/<int:cita_id>/cancelar/', v.cancelar_cita_peluquero, name='cancelar_cita_peluquero'),


    path('admin_panel/', v.panel_admin, name='panel_admin'),
]
