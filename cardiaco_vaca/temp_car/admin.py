from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.

admin.site.register(Temperatura)
admin.site.register(Pulsaciones)
admin.site.register(Bovinos)
admin.site.register(Lectura)
admin.site.register(PersonalInfo)