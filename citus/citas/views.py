from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CitaForm
from .models import Cita, ServicioCorte
import datetime


def inicio(request):
    """Página de inicio - landing page"""
    if request.user.is_authenticated:
        return redirect('panel_usuario')
    return render(request, "index.html")


def registro(request):
    """Registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('panel_usuario')
    
    if request.method == "POST":
        formulario = CustomUserCreationForm(request.POST)
        if formulario.is_valid():
            user = formulario.save()
            username = formulario.cleaned_data.get('username')
            messages.success(request, f'Cuenta creada exitosamente para {username}. Ahora puedes iniciar sesión.')
            return redirect("login")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        formulario = CustomUserCreationForm()
    
    return render(request, "register.html", {"form": formulario})


def iniciar_sesion(request):
    """Login de usuarios"""
    if request.user.is_authenticated:
        return redirect('panel_usuario')
    
    if request.method == "POST":
        formulario = CustomAuthenticationForm(request, data=request.POST)
        if formulario.is_valid():
            user = formulario.get_user()
            auth_login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            
            next_url = request.GET.get('next', 'panel_usuario')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        formulario = CustomAuthenticationForm()
    
    return render(request, "login.html", {"form": formulario})


def cerrar_sesion(request):
    """Logout de usuarios"""
    username = request.user.username if request.user.is_authenticated else None
    auth_logout(request)
    if username:
        messages.info(request, f'Hasta pronto {username}, has cerrado sesión.')
    return redirect('inicio')


@login_required(login_url='login')
def panel_usuario(request):
    """Panel de control del usuario autenticado"""
    citas_proximas = Cita.objects.filter(
        usuario=request.user,
        fecha__gte=timezone.now().date(),
        estado__in=['pendiente', 'confirmada']
    ).order_by('fecha', 'hora')[:5]
    
    citas_pasadas = Cita.objects.filter(
        usuario=request.user,
        fecha__lt=timezone.now().date()
    ).order_by('-fecha', '-hora')[:5]
    
    context = {
        'citas_proximas': citas_proximas,
        'citas_pasadas': citas_pasadas,
    }
    return render(request, "panel.html", context)


@login_required(login_url='login')
def agendar_cita(request):
    """Vista para agendar una nueva cita"""
    if request.method == "POST":
        formulario = CitaForm(request.POST)
        if formulario.is_valid():
            cita = formulario.save(commit=False)
            cita.usuario = request.user
            cita.estado = 'pendiente'
            try:
                cita.save()
                messages.success(request, '¡Cita agendada exitosamente! Te esperamos.')
                return redirect('panel_usuario')
            except Exception as e:
                messages.error(request, f'Error al agendar la cita: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        formulario = CitaForm()
    
    servicios = ServicioCorte.objects.filter(activo=True)
    context = {
        'form': formulario,
        'servicios': servicios,
    }
    return render(request, "agendar_cita.html", context)


@login_required(login_url='login')
def cancelar_cita(request, cita_id):
    """Vista para cancelar una cita"""
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)
    
    if not cita.puede_cancelar:
        messages.error(request, 'No puedes cancelar esta cita. Debe ser con al menos 2 horas de anticipación.')
        return redirect('panel_usuario')
    
    if request.method == "POST":
        cita.estado = 'cancelada'
        cita.save()
        messages.success(request, 'Cita cancelada exitosamente.')
        return redirect('panel_usuario')
    
    return render(request, "cancelar_cita.html", {'cita': cita})


@login_required(login_url='login')
def detalle_cita(request, cita_id):
    """Vista para ver el detalle de una cita"""
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)
    return render(request, "detalle_cita.html", {'cita': cita})