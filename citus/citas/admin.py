from django.contrib import admin
from .models import Cita, ServicioCorte, PerfilUsuario


@admin.register(ServicioCorte)
class ServicioCorteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion_minutos', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'servicio', 'estado', 'usuario', 'nombre_cliente')
    list_filter = ('estado', 'fecha', 'servicio')
    search_fields = ('usuario__username', 'nombre_cliente', 'correo_cliente')
    ordering = ('-fecha', '-hora')


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono', 'es_peluquero')
    list_filter = ('es_peluquero',)
    search_fields = ('usuario__username', 'telefono')
