from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime


class ServicioCorte(models.Model):
    """Tipos de cortes disponibles"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    duracion_minutos = models.IntegerField(help_text="Duración en minutos")
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Servicio de Corte"
        verbose_name_plural = "Servicios de Corte"
        ordering = ['precio']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio} ({self.duracion_minutos} min)"


class HorarioDisponible(models.Model):
    """Horarios de atención del peluquero"""
    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Horario Disponible"
        verbose_name_plural = "Horarios Disponibles"
        ordering = ['dia_semana', 'hora_inicio']
    
    def __str__(self):
        return f"{self.get_dia_semana_display()} {self.hora_inicio} - {self.hora_fin}"


class Cita(models.Model):
    """Citas agendadas"""
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citas')
    servicio = models.ForeignKey(ServicioCorte, on_delete=models.PROTECT)
    fecha = models.DateField()
    hora = models.TimeField(default='09:00:00')  # Valor por defecto temporal
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    notas = models.TextField(blank=True, null=True, help_text="Notas adicionales del cliente")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['-fecha', '-hora']
        unique_together = ['fecha', 'hora']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.servicio.nombre} - {self.fecha} {self.hora}"
    
    @staticmethod
    def esta_en_horario_atencion(fecha, hora):
        """
        Valida si la fecha y hora están dentro del horario de atención:
        - Lunes a Viernes: 9:00 - 19:00
        - Sábado: 9:00 - 14:00
        - Domingo: Cerrado
        """
        dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
        
        # Domingo cerrado
        if dia_semana == 6:
            return False, "No hay atención los domingos"
        
        # Sábado: 9:00 - 14:00
        if dia_semana == 5:
            if hora < datetime.time(9, 0):
                return False, "La atención los sábados inicia a las 9:00 AM"
            if hora >= datetime.time(14, 0):
                return False, "La atención los sábados termina a las 2:00 PM"
            return True, ""
        
        # Lunes a Viernes: 9:00 - 19:00
        if hora < datetime.time(9, 0):
            return False, "La atención inicia a las 9:00 AM"
        if hora >= datetime.time(19, 0):
            return False, "La atención termina a las 7:00 PM"
        
        return True, ""
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.fecha and self.hora:
            # No permitir citas en el pasado
            fecha_hora_cita = timezone.make_aware(
                timezone.datetime.combine(self.fecha, self.hora)
            )
            if fecha_hora_cita < timezone.now():
                raise ValidationError("No puedes agendar citas en el pasado.")
            
            # Validar horario de atención
            en_horario, mensaje_error = self.esta_en_horario_atencion(self.fecha, self.hora)
            if not en_horario:
                raise ValidationError(mensaje_error)
            
            # Verificar que no haya otra cita a la misma hora
            citas_conflicto = Cita.objects.filter(
                fecha=self.fecha,
                hora=self.hora,
                estado__in=['pendiente', 'confirmada']
            ).exclude(pk=self.pk)
            
            if citas_conflicto.exists():
                raise ValidationError("Ya existe una cita agendada para esta fecha y hora.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def puede_cancelar(self):
        """Verifica si la cita puede ser cancelada (al menos 2 horas antes)"""
        if self.estado in ['completada', 'cancelada']:
            return False
        
        fecha_hora_cita = timezone.make_aware(
            timezone.datetime.combine(self.fecha, self.hora)
        )
        tiempo_restante = fecha_hora_cita - timezone.now()
        return tiempo_restante.total_seconds() > 7200