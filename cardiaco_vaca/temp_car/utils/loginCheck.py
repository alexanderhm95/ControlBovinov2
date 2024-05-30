#Utilizado para verificar si un usuario es Admin o User

# Variable global para almacenar si el usuario está en el staff
usuario_en_staff = False

#Funcion para verificar si el correo del usuario está registrado 
def correo_registrado(correo):
    from django.contrib.auth.models import User
    try:
        User.objects.get(email=correo)
        return True
    except User.DoesNotExist:
        return False

def es_Admin(user):
    return user.groups.filter(name='Admin').exists()

def es_User(user):
    return user.groups.filter(name='User').exists()
    