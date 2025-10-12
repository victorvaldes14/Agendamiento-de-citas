from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import JsonResponse
from .forms import CustomUserCreationForm, CitaPublicaForm
from .models import Cita, ServicioCorte, PerfilUsuario
from django.contrib.auth import login as auth_login
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.utils import timezone
from .models import Cita, PerfilUsuario

def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente 👋")
    return redirect('inicio')


# -----------------------
#   REGISTRO DE USUARIO
# -----------------------
def registro(request):
    if request.user.is_authenticated:
        return redirect('panel_usuario')

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Cuenta creada correctamente 🎉")
            return redirect('panel_usuario')
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})


# -----------------------
#   FUNCIONES GENERALES
# -----------------------

def inicio(request):
    servicios = ServicioCorte.objects.filter(activo=True)
    return render(request, "index.html", {"servicios": servicios})


def obtener_horas_disponibles(request):
    fecha = request.GET.get("fecha")
    if not fecha:
        return JsonResponse({"error": "Fecha no válida"}, status=400)

    fecha = timezone.datetime.strptime(fecha, "%Y-%m-%d").date()
    horas_ocupadas = Cita.objects.filter(
        fecha=fecha,
        estado__in=["pendiente", "confirmada"]
    ).values_list("hora", flat=True)

    todas_horas = [timezone.datetime.strptime(f"{h:02d}:00", "%H:%M").time() for h in range(9, 19)]
    disponibles = [h.strftime("%H:%M") for h in todas_horas if h not in horas_ocupadas]
    return JsonResponse({"horas": disponibles})


def _asignar_peluquero_automatico(cita: Cita):
    """Asigna automáticamente un peluquero según menor carga"""
    peluqueros = PerfilUsuario.objects.filter(es_peluquero=True).select_related('usuario')
    if not peluqueros.exists():
        return  # ⚠️ Si no hay peluqueros, no hace nada
    cargas = []
    for p in peluqueros:
        cantidad = Cita.objects.filter(peluquero=p.usuario, fecha=cita.fecha).count()
        cargas.append((cantidad, p.usuario))
    cargas.sort(key=lambda x: x[0])
    cita.peluquero = cargas[0][1]  # ✅ Asignación directa



def agendar_cita_publica(request):
    """Permite agendar una cita (usuarios y público general)"""
    if request.method == "POST":
        form = CitaPublicaForm(request.POST, user=request.user)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.estado = "pendiente"

            # Asignar peluquero automáticamente
            _asignar_peluquero_automatico(cita)

            # Si el usuario está logeado, guardar sus datos
            if request.user.is_authenticated:
                cita.usuario = request.user
                cita.nombre_cliente = request.user.username
                cita.correo_cliente = request.user.email
                perfil = getattr(request.user, 'perfilusuario', None)
                if perfil:
                    cita.telefono_cliente = perfil.telefono or ""

            # Validar y guardar
            cita.full_clean()
            cita.save()

            messages.success(
                request,
                "Tu cita ha sido agendada correctamente 🎉 "
                "Recibirás un recordatorio automático 24 horas antes de la fecha programada."
            )
            return redirect("inicio")
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = CitaPublicaForm(user=request.user)
    return render(request, "agendar_cita.html", {"form": form})
@user_passes_test(lambda u: u.is_superuser)
def reportes_basicos(request):
    from django.db.models import Count

    # Días con más citas
    dias_populares = (
        Cita.objects.values('fecha')
        .annotate(total=Count('id'))
        .order_by('-total')[:7]
    )

    # Servicios más solicitados
    servicios_populares = (
        Cita.objects.values('servicio__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    # Peluqueros más activos
    peluqueros_activos = (
        Cita.objects.values('peluquero__username')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    return render(request, "reportes_admin.html", {
        "dias_populares": dias_populares,
        "servicios_populares": servicios_populares,
        "peluqueros_activos": peluqueros_activos
    })


# -----------------------
#   PANEL DE USUARIO
# -----------------------

@login_required
def panel_usuario(request):
    citas = Cita.objects.filter(usuario=request.user).order_by('-fecha', '-hora')
    return render(request, "panel_usuario.html", {"citas": citas})


@login_required
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)
    if request.method == "POST":
        cita.estado = "cancelada"
        cita.save()
        messages.success(request, "Cita cancelada correctamente ❌")
        return redirect("panel_usuario")
    return render(request, "cancelar_cita.html", {"cita": cita})


@login_required
def reagendar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    # Solo el dueño o el peluquero pueden reagendar
    if request.user != cita.usuario and not getattr(request.user, 'perfilusuario', None).es_peluquero:
        messages.error(request, "No tienes permiso para reagendar esta cita.")
        return redirect('panel_usuario')

    if request.method == "POST":
        form = CitaPublicaForm(request.POST, instance=cita, user=request.user)
        if form.is_valid():
            nueva_cita = form.save(commit=False)
            nueva_cita.estado = "pendiente"
            nueva_cita.full_clean()
            nueva_cita.save()
            messages.success(request, "Cita reagendada correctamente 📅")
            return redirect('panel_usuario')
    else:
        form = CitaPublicaForm(instance=cita, user=request.user)

    return render(request, "reagendar_cita.html", {"form": form, "cita": cita})


def es_peluquero(user):
    return hasattr(user, 'perfilusuario') and user.perfilusuario.es_peluquero

@user_passes_test(es_peluquero, login_url='login')
def panel_peluquero(request):
    perfil = getattr(request.user, 'perfilusuario', None)
    citas = Cita.objects.filter(peluquero=request.user).order_by('fecha', 'hora')

    print("🧠 Usuario logeado:", request.user.username, request.user.id)
    print("📋 Citas encontradas:", citas.count())

    for c in citas:
        print(f" - {c.servicio.nombre} | {c.fecha} | {c.hora} | Cliente: {c.nombre_cliente}")

    return render(request, "panel_peluquero.html", {
        "citas": citas,
        "perfil": perfil
    })



@user_passes_test(es_peluquero, login_url='login')
def editar_cita_peluquero(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, peluquero=request.user)
    if request.method == "POST":
        form = CitaPublicaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, "Cita actualizada correctamente.")
            return redirect("panel_peluquero")
    else:
        form = CitaPublicaForm(instance=cita)
    return render(request, "editar_cita_peluquero.html", {"form": form, "cita": cita})


@user_passes_test(es_peluquero, login_url='login')
def eliminar_cita_peluquero(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, peluquero=request.user)
    if request.method == "POST":
        cita.delete()
        messages.success(request, "Cita eliminada correctamente.")
        return redirect("panel_peluquero")
    return render(request, "confirmar_eliminar_cita.html", {"cita": cita})


@user_passes_test(es_peluquero, login_url='login')
def marcar_cita_atendida(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, peluquero=request.user)
    cita.estado = "completada"
    cita.save()
    messages.success(request, "Cita marcada como atendida ✅")
    return redirect("panel_peluquero")


# -----------------------
#   PANEL ADMIN
# -----------------------

@user_passes_test(lambda u: u.is_superuser)
def panel_admin(request):
    citas = Cita.objects.all().order_by("-fecha", "-hora")
    return render(request, "panel_admin.html", {"citas": citas})
