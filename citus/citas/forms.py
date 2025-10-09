from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cita, ServicioCorte
import datetime


# ----------------------------
# FORMULARIO DE REGISTRO USUARIO
# ----------------------------
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'ejemplo@correo.com'
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['username'].label = 'Nombre de Usuario'
        self.fields['username'].help_text = ''

        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Contraseña'
        })
        self.fields['password1'].label = 'Contraseña'
        self.fields['password1'].help_text = ''

        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirmar contraseña'
        })
        self.fields['password2'].label = 'Contraseña (confirmación)'
        self.fields['password2'].help_text = ''


# ----------------------------
# FORMULARIO DE CITAS PÚBLICO
# ----------------------------
class CitaPublicaForm(forms.ModelForm):
    """Formulario para agendar citas sin necesidad de registro"""

    nombre_cliente = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre'})
    )
    apellido_cliente = forms.CharField(
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apellido'})
    )
    correo_cliente = forms.EmailField(
        label="Correo",
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'ejemplo@correo.com'})
    )
    telefono_cliente = forms.CharField(
        label="Teléfono",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+56 9 1234 5678'})
    )

    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        label="Fecha"
    )
    hora = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-input'}),
        label="Hora",
        choices=[]
    )
    servicio = forms.ModelChoiceField(
        queryset=ServicioCorte.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'form-input'}),
        label="Servicio"
    )
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Notas adicionales (opcional)'}),
        label="Notas adicionales"
    )

    class Meta:
        model = Cita
        fields = [
            'nombre_cliente', 'apellido_cliente', 'correo_cliente', 'telefono_cliente',
            'servicio', 'fecha', 'hora', 'notas'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hora'].choices = self.generar_horas_disponibles()

    def generar_horas_disponibles(self):
        horas = []
        hora_actual = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 0))
        hora_final = datetime.datetime.combine(datetime.date.today(), datetime.time(19, 0))
        while hora_actual < hora_final:
            horas.append((hora_actual.time().strftime('%H:%M'), hora_actual.time().strftime('%H:%M')))
            hora_actual += datetime.timedelta(minutes=30)
        return horas
