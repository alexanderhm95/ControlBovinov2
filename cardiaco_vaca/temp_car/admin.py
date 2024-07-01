from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Temperatura)
admin.site.register(Pulsaciones)
admin.site.register(Bovinos)
admin.site.register(Lectura)
admin.site.register(PersonalInfo)
admin.site.register(ControlMonitoreo)