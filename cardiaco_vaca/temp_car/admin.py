from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(PersonalInfo)
admin.site.register(TemperatureData)
admin.site.register(Pulsacion)
admin.site.register(Medicion)
admin.site.register(MedicionCompleto)