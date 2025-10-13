from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Cita, ServicioCorte, PerfilUsuario


# ==========================
# PERSONALIZACIÓN GLOBAL ADMIN
# ==========================

admin.site.site_header = "Citus Peluquería"
admin.site.site_title = "Panel Administrativo Citus"
admin.site.index_title = "Gestión de Citas y Servicios"


# ==========================
# PERFIL DE USUARIO
# ==========================

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono', 'es_peluquero')
    list_filter = ('es_peluquero',)
    search_fields = ('usuario__username', 'telefono')


# ==========================
# SERVICIOS
# ==========================

@admin.register(ServicioCorte)
class ServicioCorteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'duracion_minutos', 'precio', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


# ==========================
# CITAS
# ==========================

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'servicio', 'cliente_display', 'peluquero_display', 'estado_coloreado')
    list_filter = ('estado', 'fecha', 'servicio')
    search_fields = ('usuario__username', 'nombre_cliente', 'correo_cliente', 'peluquero__username')
    ordering = ('-fecha', '-hora')

    # ---- FILTRA SOLO PELUQUEROS EN EL ADMIN ----
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "peluquero":
            peluqueros_ids = PerfilUsuario.objects.filter(es_peluquero=True).values_list('usuario_id', flat=True)
            kwargs["queryset"] = User.objects.filter(id__in=peluqueros_ids)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # ---- CLIENTE (nombre mostrado correctamente) ----
    def cliente_display(self, obj):
        if obj.usuario:
            return obj.usuario.username
        return f"{obj.nombre_cliente or ''} {obj.apellido_cliente or ''}".strip()
    cliente_display.short_description = "Cliente"

    # ---- PELUQUERO (formato visual) ----
    def peluquero_display(self, obj):
        if obj.peluquero:
            return format_html(" <b>{}</b>", obj.peluquero.username)
        return "—"
    peluquero_display.short_description = "Peluquero"

    # ---- ESTADO CON COLOR ----
    def estado_coloreado(self, obj):
        color_map = {
            'pendiente': '#ffc107',   # Amarillo
            'confirmada': '#17a2b8',  # Celeste
            'completada': '#28a745',  # Verde
            'cancelada': '#dc3545',   # Rojo
        }
        color = color_map.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 8px; border-radius:4px;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_coloreado.short_description = "Estado"
