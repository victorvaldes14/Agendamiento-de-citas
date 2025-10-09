from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PerfilUsuario


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea un PerfilUsuario automáticamente cuando se crea un nuevo usuario."""
    if created:
        PerfilUsuario.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Guarda el perfil asociado al actualizar un usuario."""
    PerfilUsuario.objects.get_or_create(usuario=instance)
