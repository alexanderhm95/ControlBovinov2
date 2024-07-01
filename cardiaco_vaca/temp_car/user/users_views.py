from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model,login,logout,authenticate, login
from django.contrib import messages

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.conf import settings
from temp_car.models import *
from temp_car.forms import *

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('monitoreo_actual')
        else:
            messages.error(request, 'Credenciales inválidas. Inténtalo nuevamente.')
    return render(request, 'appMonitor/login.html')

def user_logout(request): 
    logout(request)
    return redirect('/')


def crear_usuario(request):
    if request.method == 'POST':
        form = PersonalInfoForm(request.POST)
        if form.is_valid():
            #Ahora se crea el usuario con el modelo CustomUserManager
            user = get_user_model().objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['cedula'],
                first_name=form.cleaned_data['nombre'],
                last_name=form.cleaned_data['apellido']
            )
            user.save()
            form.save()

            # Redirige a alguna página de éxito
            return redirect('/')
        else:
            # Si hay errores, pasa el formulario y los errores al contexto de la plantilla
            return render(request, 'appMonitor/user/register.html', {'form': form, 'errors': form.errors}, status=400)
    else:
        # Si el método de solicitud no es POST, simplemente renderiza el formulario vacío
        form = PersonalInfoForm()
        return render(request, 'appMonitor/user/register.html', {'form': form}, status=400)
#Gestion de usuarios

@login_required
def listar_usuario(request):
    usuarios = {}
    usuario_queryset = User.objects.all()
    profile_queryset = PersonalInfo.objects.all()

    for user in usuario_queryset:
        #sino esta en el staff no se muestra
        if  user.is_superuser == True:
            continue
        else:
            profile = profile_queryset.filter(email=user.email).first()
            usuarios[user.id] = {
                'userId': user.id,
                'id': user.id if profile else "Nulo",
                'nombre': user.first_name or "Nulo",
                'apellido': user.last_name or "Nulo",
                'email': user.email or "Nulo",
                'cedula': profile.cedula if profile else "Nulo",
                'telefono': profile.telefono if profile else "Nulo",
                'activo': user.is_active,
                'is_staff': user.is_staff,
            }

    return render(request, 'appMonitor/user/listar.html', {'usuarios': usuarios})


@login_required
def desactivar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    if usuario.is_active:
        usuario.is_active = False
        messages.error(request, f'Usuario {usuario.username} desactivado correctamente.')
    else:
        usuario.is_active = True
        messages.success(request, f'Usuario {usuario.username} activado correctamente.')
    usuario.save()
    return redirect('gestion')

@login_required
def editar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(PersonalInfo, email=user.email)

    if request.method == 'POST':
        personal_info_form = EditPersonalInfoForm(request.POST, instance=profile)
        user_form = EditUserForm(request.POST, instance=user)

        if personal_info_form.is_valid() and user_form.is_valid():
            personal_info_form.save()

            user.email = personal_info_form.cleaned_data['email']
            user.username = personal_info_form.cleaned_data['email']
            user.first_name = personal_info_form.cleaned_data['nombre']
            user.last_name = personal_info_form.cleaned_data['apellido']
            user.is_staff = user_form.cleaned_data['is_staff']
            user.save()

            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('gestion')
        else:
            messages.error(request, 'Error al actualizar el usuario. Inténtalo de nuevo.')
    else:
        personal_info_form = EditPersonalInfoForm(instance=profile)
        user_form = EditUserForm(instance=user)

    return render(request, 'appMonitor/user/editar.html', {
        'personal_info_form': personal_info_form,
        'user_form': user_form,
        'profile': profile
    })




class CustomPasswordResetView(View):
    template_name = 'appMonitor/resetPassword/password_reset_form.html'

    def get(self, request):
        form = PasswordResetForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PasswordResetForm(request.POST)
        print("Entro aqui")
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    subject = 'Restablecimiento de contraseña solicitado'
                    email_template_name = 'appMonitor/resetPassword/password_reset_email.html'
                    c = {
                        'email': user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'Control y Monitoreo de Constantes Fisiológicas UNL',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http' if not request.is_secure() else 'https',
                    }
                    email_content = render_to_string(email_template_name, c)
                    print(email_content)
                    es = send_mail(subject, email_content, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    print("Correo enviado",es)
                return redirect('passwordResetDone')
            else:
                messages.error(request, 'No hay usuario registrado con el correo electrónico proporcionado.')
        return render(request, self.template_name, {'form': form})

class ResetPasswordDoneView(View):
    template_name = 'appMonitor/resetPassword/password_reset_done.html'

    def get(self, request):
        return render(request, self.template_name)


class CustomPasswordResetConfirmView(View):
    template_name = 'appMonitor/resetPassword/password_reset_confirm.html'

    def get(self, request, uidb64=None, token=None):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                form = SetPasswordForm(user)
                return render(request, self.template_name, {
                    'form': form,
                    'validlink': True,
                    'uidb64': uidb64,
                    'token': token
                })
            else:
                messages.error(request, 'El enlace de restablecimiento de contraseña no era válido, posiblemente porque ya se usó. Solicite un nuevo restablecimiento de contraseña.')
                return render(request, self.template_name, {'validlink': False})
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'El enlace de restablecimiento de contraseña no era válido. Solicite un nuevo restablecimiento de contraseña.')
            return render(request, self.template_name, {'validlink': False})

    def post(self, request, uidb64=None, token=None):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Tu contraseña ha sido restablecida con éxito.')
                return redirect('passwordResetComplete')
            return render(request, self.template_name, {
                'form': form,
                'validlink': True,
                'uidb64': uidb64,
                'token': token
            })
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'El enlace de restablecimiento de contraseña no era válido. Solicite un nuevo restablecimiento de contraseña.')
            return render(request, self.template_name, {'validlink': False})


class ResetPasswordCompleteView(View):
    template_name = 'appMonitor/resetPassword/password_reset_complete.html'

    def get(self, request):
        return render(request, self.template_name)
