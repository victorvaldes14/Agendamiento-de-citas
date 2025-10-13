# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from citas.models import ServicioCorte, PerfilUsuario

# --- Crear peluquero por defecto ---
peluquero_user, creado = User.objects.get_or_create(
    username="admin_barber",
    defaults={
        "first_name": "Administrador",
        "last_name": "Barber",
        "email": "adminbarber@example.com",
        "is_staff": True,
        "is_active": True
    }
)
if creado:
    peluquero_user.set_password("barber123")
    peluquero_user.save()
    print("Usuario 'admin_barber' creado (contraseña: barber123)")
else:
    print("Usuario 'admin_barber' ya existía")

perfil, perfil_creado = PerfilUsuario.objects.get_or_create(
    usuario=peluquero_user,
    defaults={"telefono": "999999999", "es_peluquero": True}
)
if perfil_creado:
    print("Perfil de peluquero creado correctamente")
else:
    perfil.es_peluquero = True
    perfil.save()
    print("Perfil de peluquero ya existía, actualizado a es_peluquero=True")


# --- Lista de servicios ---
servicios = [
    # Cortes clásicos y modernos
    {"nombre": "Corte Clasico", "precio": 10000, "duracion_minutos": 30},
    {"nombre": "Corte Fade", "precio": 12000, "duracion_minutos": 40},
    {"nombre": "Corte Low Fade", "precio": 12000, "duracion_minutos": 35},
    {"nombre": "Corte Mid Fade", "precio": 12000, "duracion_minutos": 35},
    {"nombre": "Corte High Fade", "precio": 13000, "duracion_minutos": 40},
    {"nombre": "Corte Razor Fade", "precio": 14000, "duracion_minutos": 45},
    {"nombre": "Corte Militar", "precio": 9000, "duracion_minutos": 30},
    {"nombre": "Corte Buzz", "precio": 8000, "duracion_minutos": 30},
    {"nombre": "Corte Pompadour", "precio": 14000, "duracion_minutos": 45},
    {"nombre": "Corte Undercut", "precio": 14000, "duracion_minutos": 45},
    {"nombre": "Corte Peaky Blinders", "precio": 15000, "duracion_minutos": 50},
    {"nombre": "Corte Crop Texturizado", "precio": 13000, "duracion_minutos": 40},
    {"nombre": "Corte Spiky Moderno", "precio": 13000, "duracion_minutos": 40},
    {"nombre": "Corte Taper Fade", "precio": 13000, "duracion_minutos": 40},

    # Barba y afeitado
    {"nombre": "Perfilado de Barba", "precio": 9000, "duracion_minutos": 30},
    {"nombre": "Afeitado Clasico", "precio": 10000, "duracion_minutos": 30},
    {"nombre": "Arreglo Completo de Barba", "precio": 12000, "duracion_minutos": 40},
    {"nombre": "Diseno de Barba", "precio": 11000, "duracion_minutos": 35},
    {"nombre": "Afeitado Premium", "precio": 15000, "duracion_minutos": 45},

    # Combos populares
    {"nombre": "Corte + Barba", "precio": 18000, "duracion_minutos": 60},
    {"nombre": "Corte + Afeitado Clasico", "precio": 19000, "duracion_minutos": 60},
    {"nombre": "Corte + Diseno de Barba", "precio": 20000, "duracion_minutos": 60},
    {"nombre": "Corte + Afeitado Premium", "precio": 21000, "duracion_minutos": 60},
]

# --- Insertar servicios en la base de datos ---
for s in servicios:
    obj, creado = ServicioCorte.objects.get_or_create(
        nombre=s["nombre"],
        defaults={
            "precio": s["precio"],
            "duracion_minutos": s["duracion_minutos"],
            "activo": True,
        },
    )
    if creado:
        print(f"Servicio creado: {s['nombre']}")
    else:
        print(f"Ya existía: {s['nombre']}")

print("Carga completada exitosamente 💈")
