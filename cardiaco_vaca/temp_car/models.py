# En temperature_app/models.py

from django.contrib.auth.models import User
from django.db import models
from .utils import getHours



class PersonalInfo(models.Model):
    cedula = models.CharField(max_length=15, blank=True, null=True, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    apellido = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True, unique=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"



class Temperatura(models.Model):
    id_Temperatura = models.AutoField(primary_key=True)
    valor = models.IntegerField()

    def __str__(self):
        return str(self.valor)

class Pulsaciones(models.Model):
    id_Pulsaciones = models.AutoField(primary_key=True)
    valor = models.IntegerField()

    def __str__(self):
        return str(self.valor)

class Bovinos(models.Model):
    id_Bovinos = models.AutoField(primary_key=True)
    idCollar = models.IntegerField(unique=True)
    macCollar = models.CharField(max_length=100, blank=True, null=True, unique=True)
    nombre = models.CharField(max_length=100)
    fecha_registro = models.DateField()
    def __str__(self):
        return self.nombre
    
class Lectura(models.Model):
    id_Lectura = models.AutoField(primary_key=True)
    id_Temperatura = models.ForeignKey(Temperatura, on_delete=models.CASCADE)
    id_Pulsaciones = models.ForeignKey(Pulsaciones, on_delete=models.CASCADE)
    fecha_lectura = models.DateField(default=getHours.getDate)
    hora_lectura = models.TimeField(default=getHours.getTime)
    id_Bovino = models.ForeignKey(Bovinos, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_Lectura} - {self.id_Bovino.nombre} - {self.fecha_lectura} - {self.hora_lectura}"



