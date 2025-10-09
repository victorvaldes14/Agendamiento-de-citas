from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import JsonResponse
from .forms import CustomUserCreationForm, CitaPublicaForm
from .models import Cita, ServicioCorte, PerfilUsuario
from django.contrib.auth import login as auth_login


# -----------------------
#   REGISTRO DE USUARIO
# -----------------------
def registro(request):
    """Permite registrar nuevos usuarios."""
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
    """Página inicial - agendamiento público"""
    servicios = ServicioCorte.objects.filter(activo=True)
    return render(request, "index.html", {"servicios": servicios})


def obtener_horas_disponibles(request):
    """Devuelve horas libres en formato JSON para una fecha dada"""
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
        return
    cargas = [(Cita.objects.filter(peluquero=p.usuario, fecha=cita.fecha).count(), p.usuario) for p in peluqueros]
    cargas.sort(key=lambda x: x[0])
    cita.peluquero = cargas[0][1]


def agendar_cita_publica(request):
    """Permite agendar sin estar registrado"""
    if request.method == "POST":
        form = CitaPublicaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.estado = "pendiente"
            _asignar_peluquero_automatico(cita)
            cita.save()
            messages.success(request, "Cita agendada correctamente 🎉")
            return redirect("inicio")
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = CitaPublicaForm()
    return render(request, "agendar_cita.html", {"form": form})


# -----------------------
#   PANEL DE USUARIO
# -----------------------

@login_required
def panel_usuario(request):
    citas = Cita.objects.filter(usuario=request.user).order_by('-fecha', '-hora')
    return render(request, "panel_usuario.html", {"citas": citas})


# -----------------------
#   PANEL DE PELUQUERO
# -----------------------

def es_peluquero(user):
    return hasattr(user, 'perfilusuario') and user.perfilusuario.es_peluquero


@user_passes_test(es_peluquero, login_url='login')
def panel_peluquero(request):
    citas = Cita.objects.filter(peluquero=request.user).order_by('fecha', 'hora')
    return render(request, "panel_peluquero.html", {"citas": citas})


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
    """Permite al peluquero marcar una cita como completada"""
    cita = get_object_or_404(Cita, id=cita_id, peluquero=request.user)
    cita.estado = "completada"
    cita.save()
    messages.success(request, "Cita marcada como atendida ✅")
    return redirect("panel_peluquero")


# -----------------------
#   PANEL ADMIN
# -----------------------

@login_required
def panel_admin(request):
    citas = Cita.objects.all().order_by("-fecha", "-hora")
    return render(request, "panel_admin.html", {"citas": citas})
