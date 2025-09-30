from django.contrib import admin
from .models import Cita, ServicioCorte, HorarioDisponible


@admin.register(ServicioCorte)
class ServicioCorteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion_minutos', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo',)


@admin.register(HorarioDisponible)
class HorarioDisponibleAdmin(admin.ModelAdmin):
    list_display = ('get_dia_semana_display', 'hora_inicio', 'hora_fin', 'activo')
    list_filter = ('dia_semana', 'activo')
    list_editable = ('activo',)


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'servicio', 'fecha', 'hora', 'estado', 'creado_en')
    list_filter = ('estado', 'fecha', 'servicio')
    search_fields = ('usuario__username', 'usuario__email')
    date_hierarchy = 'fecha'
    ordering = ('-fecha', '-hora')
    readonly_fields = ('creado_en', 'actualizado_en')
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('usuario',)
        }),
        ('Detalles de la Cita', {
            'fields': ('servicio', 'fecha', 'hora', 'estado', 'notas')
        }),
        ('Información del Sistema', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )