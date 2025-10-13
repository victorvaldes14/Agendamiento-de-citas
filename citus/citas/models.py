from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    es_peluquero = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario.username} ({'Peluquero' if self.es_peluquero else 'Cliente'})"


class ServicioCorte(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    duracion_minutos = models.IntegerField(help_text="Duración en minutos")
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class Cita(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='citas')
    servicio = models.ForeignKey(ServicioCorte, on_delete=models.PROTECT)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    # Datos para usuarios no registrados
    nombre_cliente = models.CharField(max_length=100, blank=True)
    apellido_cliente = models.CharField(max_length=100, blank=True)
    correo_cliente = models.EmailField(blank=True)
    telefono_cliente = models.CharField(max_length=15, blank=True)

    peluquero = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='citas_asignadas')
    notas = models.TextField(blank=True, null=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    motivo_cancelacion = models.TextField(blank=True, null=True)
    motivo_reagendamiento = models.TextField(blank=True, null=True)


    class Meta:
        ordering = ['-fecha', '-hora']
        unique_together = ['fecha', 'hora', 'peluquero']

    def clean(self):
        if self.peluquero and Cita.objects.exclude(id=self.id).filter(
            fecha=self.fecha, hora=self.hora, peluquero=self.peluquero
        ).exists():
            raise ValidationError("El peluquero ya tiene una cita a esa hora.")

    def __str__(self):
        cliente = self.usuario.username if self.usuario else f"{self.nombre_cliente} {self.apellido_cliente}"
        return f"{cliente} - {self.servicio.nombre} ({self.fecha} {self.hora})"

    @property
    def puede_cancelar(self):
        if self.estado in ['completada', 'cancelada']:
            return False
        fecha_hora_cita = timezone.make_aware(
            timezone.datetime.combine(self.fecha, self.hora)
        )
        return (fecha_hora_cita - timezone.now()).total_seconds() > 7200
