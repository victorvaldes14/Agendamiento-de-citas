from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cita, ServicioCorte

class CitaEstadoForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['estado']

class ReagendarCitaPeluqueroForm(forms.ModelForm):
    nueva_fecha = forms.DateField(label="Nueva fecha", widget=forms.DateInput(attrs={'type': 'date'}))
    nueva_hora = forms.TimeField(label="Nueva hora", widget=forms.TimeInput(attrs={'type': 'time'}))
    motivo_reagendamiento = forms.CharField(label="Motivo del reagendamiento", widget=forms.Textarea, required=True)

    class Meta:
        model = Cita
        fields = ['nueva_fecha', 'nueva_hora', 'motivo_reagendamiento']

class CancelarCitaPeluqueroForm(forms.ModelForm):
    motivo_cancelacion = forms.CharField(label="Motivo de cancelación", widget=forms.Textarea, required=True)

    class Meta:
        model = Cita
        fields = ['motivo_cancelacion']

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



class CitaPublicaForm(forms.ModelForm):
    """Formulario de agendamiento (dinámico: público o usuario registrado)"""

    nombre_cliente = forms.CharField(
        label="Nombre",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre'})
    )
    apellido_cliente = forms.CharField(
        label="Apellido",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apellido'})
    )
    correo_cliente = forms.EmailField(
        label="Correo",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'ejemplo@correo.com'})
    )
    telefono_cliente = forms.CharField(
        label="Teléfono",
        required=False,
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
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['hora'].choices = self.generar_horas_disponibles()

        # Si el usuario está logeado, ocultamos los campos de contacto
        if user and user.is_authenticated:
            for field in ['nombre_cliente', 'apellido_cliente', 'correo_cliente', 'telefono_cliente']:
                self.fields[field].widget = forms.HiddenInput()

    def generar_horas_disponibles(self):
        import datetime
        horas = []
        hora_actual = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 0))
        hora_final = datetime.datetime.combine(datetime.date.today(), datetime.time(19, 0))
        while hora_actual < hora_final:
            horas.append((hora_actual.time().strftime('%H:%M'), hora_actual.time().strftime('%H:%M')))
            hora_actual += datetime.timedelta(minutes=30)
        return horas

