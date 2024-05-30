# En temperature_app/models.py
from django.contrib.auth.models import BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('El correo es obligatorio'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class PersonalInfo(models.Model):
    cedula = models.CharField(max_length=15, blank=True, null=True, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    apellido = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True, unique=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    

class TemperatureData(models.Model):
    temperature = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Temperature: {self.temperature} °C - Timestamp: {self.timestamp}"
    
class Pulsacion(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    pulsaciones_por_minuto = models.IntegerField()

    def __str__(self):
        return f'{self.fecha} - {self.pulsaciones_por_minuto} bpm'

class Medicion(models.Model):
    humedad = models.FloatField()
    temperatura = models.FloatField()
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Medicion: Humedad={self.humedad}%, Temperatura={self.temperatura}°C"
    
class MedicionCompleto(models.Model):
    temperatura = models.FloatField()
    pulsaciones = models.IntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    collar_id = models.CharField(max_length=5000)  # Agrega la variable 'collar_id'
    nombre_vaca = models.CharField(max_length=100)

    def __str__(self):
        return f"ID: {self.id}, Nombre: {self.nombre_vaca}, Temperatura: {self.temperatura}, Pulsaciones: {self.pulsaciones}, Collar ID: {self.collar_id}, Fecha: {self.fecha_creacion}"