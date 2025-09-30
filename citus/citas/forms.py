from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import Cita, ServicioCorte
from django.utils import timezone
import datetime


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
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirmar contraseña'
        })
        
        self.fields['username'].label = 'Usuario'
        self.fields['email'].label = 'Email'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar Contraseña'
        
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre de usuario'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Contraseña'
        })
    )


class CitaForm(forms.ModelForm):
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        }),
        label='Fecha'
    )
    
    hora = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-input'
        }),
        label='Hora',
        choices=[]
    )
    
    servicio = forms.ModelChoiceField(
        queryset=ServicioCorte.objects.filter(activo=True),
        widget=forms.Select(attrs={
            'class': 'form-input'
        }),
        label='Tipo de Corte',
        empty_label="Selecciona un tipo de corte"
    )
    
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Notas adicionales (opcional)',
            'rows': 3
        }),
        label='Notas adicionales'
    )
    
    class Meta:
        model = Cita
        fields = ['servicio', 'fecha', 'hora', 'notas']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generar horarios disponibles por defecto (Lunes-Viernes 9:00-19:00)
        self.fields['hora'].choices = self.generar_horarios_disponibles()
    
    def generar_horarios_disponibles(self, fecha=None):
        """
        Genera horarios disponibles según el día de la semana
        - Lunes a Viernes: 9:00 - 19:00
        - Sábado: 9:00 - 14:00
        - Domingo: No disponible
        """
        horarios = []
        
        # Si no hay fecha, usar horario de semana por defecto
        if not fecha:
            hora_inicio = datetime.time(9, 0)
            hora_fin = datetime.time(19, 0)
        else:
            dia_semana = fecha.weekday()
            
            # Domingo cerrado
            if dia_semana == 6:
                return [('', 'No hay atención los domingos')]
            
            # Sábado: 9:00 - 14:00
            if dia_semana == 5:
                hora_inicio = datetime.time(9, 0)
                hora_fin = datetime.time(14, 0)
            # Lunes a Viernes: 9:00 - 19:00
            else:
                hora_inicio = datetime.time(9, 0)
                hora_fin = datetime.time(19, 0)
        
        hora_actual = datetime.datetime.combine(datetime.date.today(), hora_inicio)
        hora_final = datetime.datetime.combine(datetime.date.today(), hora_fin)
        
        while hora_actual < hora_final:
            tiempo = hora_actual.time()
            horarios.append((tiempo.strftime('%H:%M'), tiempo.strftime('%I:%M %p')))
            hora_actual += datetime.timedelta(minutes=30)
        
        return horarios
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_str = cleaned_data.get('hora')
        
        if fecha and hora_str:
            # Validar que no sea domingo
            if fecha.weekday() == 6:
                raise forms.ValidationError("No hay atención los domingos.")
            
            # Convertir hora string a time object
            hora = datetime.datetime.strptime(hora_str, '%H:%M').time()
            
            # Validar horario de atención
            en_horario, mensaje_error = Cita.esta_en_horario_atencion(fecha, hora)
            if not en_horario:
                raise forms.ValidationError(mensaje_error)
            
            # Verificar que no sea en el pasado
            fecha_hora = timezone.make_aware(datetime.datetime.combine(fecha, hora))
            if fecha_hora < timezone.now():
                raise forms.ValidationError("No puedes agendar citas en el pasado.")
            
            # Verificar disponibilidad
            citas_existentes = Cita.objects.filter(
                fecha=fecha,
                hora=hora,
                estado__in=['pendiente', 'confirmada']
            )
            
            if self.instance.pk:
                citas_existentes = citas_existentes.exclude(pk=self.instance.pk)
            
            if citas_existentes.exists():
                raise forms.ValidationError("Esta hora ya está ocupada. Por favor selecciona otra.")
            
            cleaned_data['hora'] = hora
        
        return cleaned_data