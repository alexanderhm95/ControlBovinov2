# forms.py
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from .models import PersonalInfo



class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        fields = ['cedula', 'telefono', 'nombre', 'apellido', 'email']
        labels = {
            'cedula': 'Cédula',
            'telefono': 'Teléfono',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'email': 'Correo Electrónico',
        }
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Cédula'}),
            'telefono': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Teléfono'}),
            'nombre': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Correo Electrónico'}),
        }

    def __init__(self, *args, **kwargs):
        super(PersonalInfoForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'input'


class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No hay ninguna cuenta asociada a este correo electrónico')
        return email