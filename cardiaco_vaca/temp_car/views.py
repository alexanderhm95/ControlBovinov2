from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model,login,logout,authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from xhtml2pdf import pisa
from io import BytesIO
from .forms import *
from .models import *
import json
import urllib.parse

####################################
#Metodos de plataforma web       
####################################
def error_404_view(request, exception):
    return render(request, '404.html', status=404)

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Autenticar al usuario
        user = authenticate(request, username=username, password=password)
        if user is not None:
            #verificar si el usuario es admin y esta en el staff
            login(request, user)
            return redirect('monitoreo_actual')
        else:
            messages.error(request, 'Credenciales inválidas. Inténtalo de nuevo.')
    return  render(request, 'Usuario/login.html')

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
            return render(request, 'Usuario/newUsuario.html', {'form': form, 'errors': form.errors}, status=400)
    else:
        # Si el método de solicitud no es POST, simplemente renderiza el formulario vacío
        form = PersonalInfoForm()
        return render(request, 'Usuario/newUsuario.html', {'form': form}, status=400)
#Gestion de usuarios

@login_required
def gestion(request):
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

    return render(request, 'Usuario/gestion.html', {'usuarios': usuarios})

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

    return render(request, 'Usuario/editar_usuario.html', {
        'personal_info_form': personal_info_form,
        'user_form': user_form,
        'profile': profile
    })

############Dashboard################
# Dashboard Monitoreo Actual toda la logica esta dentro 
@login_required
def monitoreo_actual(request):
    return render(request, 'panel_tecnico_docente/monitoreo_reciente.html')

from django.http import JsonResponse
from .models import Lectura

def obtener_datos_json3(request):
    fecha_busqueda = request.GET.get('fecha', None)

    if fecha_busqueda:
        # Filtrar por fecha si se proporciona
        datos = Lectura.objects.filter(fecha_lectura=fecha_busqueda).order_by('-fecha_lectura', '-hora_lectura')
    else:
        # Obtener todos los datos si no se proporciona fecha
        datos = Lectura.objects.all().order_by('-fecha_lectura', '-hora_lectura')

    if datos:
        reportes = []
        for dato in datos:
            fecha_creacion = dato.fecha_lectura.strftime('%Y-%m-%d') + ' ' + dato.hora_lectura.strftime('%H:%M:%S')
            reporte = {
                'fecha_creacion': fecha_creacion,
                'temperatura': dato.id_Temperatura.valor,
                'nombre_vaca': dato.id_Bovino.nombre,
                'pulsaciones': dato.id_Pulsaciones.valor,
                'collar_id': dato.id_Bovino.idCollar,
            }
            reportes.append(reporte)
        return JsonResponse({'reportes': reportes})
    else:
        return JsonResponse({'error': 'No hay datos disponibles'})



def ultimoRegistro(request, collar_id):
    print("Llegue a la vista el collar id es: ", collar_id)
    # Filtrar por collar_id y ordenar por fecha y hora para obtener el último
    bovino = Bovinos.objects.filter(idCollar=collar_id).first()
    if bovino is  None:
        return JsonResponse({'error': 'No hay datos disponibles para el collar_id proporcionado'}, status=404)
    datos = Lectura.objects.filter(id_Bovino=bovino).order_by('-fecha_lectura', '-hora_lectura').first()
    

    if datos is not None:
        reporte = {
            'fecha_lectura': datos.fecha_lectura.strftime('%Y-%m-%d'),
            'hora_lectura': datos.hora_lectura.strftime('%H:%M:%S'),
            'temperatura': datos.id_Temperatura.valor,
            'nombre_vaca': datos.id_Bovino.nombre,
            'pulsaciones': datos.id_Pulsaciones.valor,
            'collar_id': datos.id_Bovino.idCollar,
        }
        print(datos)

        return JsonResponse(reporte, status=200)
    else:
        return JsonResponse({'error': 'No hay datos disponibles para el collar_id proporcionado'})





@login_required
def reportes(request):
    # Obtener la página actual de la URL, por ejemplo, "/reportes/?page=2"
    page = request.GET.get('page', 1)

    # Obtener la fecha de búsqueda desde el formulario
    fecha_busqueda = request.GET.get('fecha_busqueda')

    # Obtener todos los reportes (o filtrar según tus necesidades)
    reportes_list = Lectura.objects.all().order_by('-fecha_lectura', '-hora_lectura')

    # Filtrar los reportes por fecha si se proporciona una fecha de búsqueda
    if fecha_busqueda:
        try:
            fecha_busqueda = datetime.strptime(fecha_busqueda, '%Y-%m-%d')
            reportes_list = reportes_list.filter(fecha_creacion__date=fecha_busqueda)
        except ValueError:
            # Manejar el caso en que la fecha proporcionada no sea válida
            pass

    # Configurar la paginación
    paginator = Paginator(reportes_list, 10)  # Muestra 10 elementos por página
    try:
        reportes = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un número entero, muestra la primera página
        reportes = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, muestra la última página
        reportes = paginator.page(paginator.num_pages)

    context = {
        'reportes': reportes,
        'fecha_busqueda': fecha_busqueda,
    }

    return render(request, 'panel_tecnico_docente/reportes.html', context)

def reporte_pdf(request):
    fecha_busqueda = request.GET.get('fecha_busqueda')
    reportes = Lectura.objects.all()

    if fecha_busqueda:
        reportes = reportes.filter(fecha_lectura__date=fecha_busqueda)

    context = {
        'reportes': reportes,
        'fecha_busqueda': fecha_busqueda,
    }

    table_content = get_template('panel_tecnico_docente/reportes.html').render(context).split('<table id="tablaReportes">')[1].split('</table>')[0]
    table_content = table_content.replace('<th>', '<th style="padding: 8px; text-align: center; background-color: #72b4fc;">')
    table_content = table_content.replace('<td>', '<td style="padding: 8px; text-align: center; border: 1px solid #ddd;">')
    table_html = f'<table id="tablaReportes" style="width: 80%; margin: 20px auto; border-collapse: collapse;">{table_content}</table>'

    pdf = render_to_pdf(table_html, context)

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"reporte_monitoreos_{fecha_busqueda or datetime.now().strftime('%Y-%m-%d')}.pdf"
        content = f'attachment; filename="{filename}"'
        response['Content-Disposition'] = content
        return response

    return HttpResponse("Error al generar el PDF.", status=500)

def render_to_pdf(html_content, context_dict={}):
    header_html = """
<table style="width: 100%; border-collapse: collapse;">
    <tr>
        <td style="padding: 10px;">
            <img src="./temp_car/static/assets/img/logounl.png" alt="Left Logo" style="width: 195px; height: auto; margin-right: 10px;">
        </td>
        <td style="padding: 10px; vertical-align: top; text-align: right;">
            <img src="./temp_car/static/assets/img/logoComputacion.png" alt="Right Logo" style="width: 100px; height: auto; margin-left: 10px;">
        </td>
    </tr>
</table>
<div style="text-align: center; margin: 20px 0;">
    <h1 style="font-size: 24px; color: #333; margin: 0;">Reporte de Monitoreos al Ganado Bovino Lechero</h1>
</div>

"""

    full_html = header_html + html_content

    footer_html = """
        <footer style="text-align: center; margin-top: 20px; background-color: #f8f8f8; padding: 10px;">
            <p style="font-size: 12px; color: #white; margin: 0;">© All rights reserved | Carrera de Ingeniería en Computación</p>
        </footer>
    """

    full_html += footer_html

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(full_html.encode("ISO-8859-1")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


@login_required
def temperatura(request):
    try:
        page = request.GET.get('page', 1)
        reportes_list = Lectura.objects.all().order_by('-fecha_lectura', '-hora_lectura')

        paginator = Paginator(reportes_list, 10)
        reportes = paginator.get_page(page)

    except PageNotAnInteger:
        reportes = paginator.get_page(1)
    except EmptyPage:
        reportes = paginator.get_page(paginator.num_pages)
    except Exception as e:
        print(f"Error al obtener reportes: {e}")
        reportes = []

    context = {
        'reportes': reportes,
    }
    return render(request, 'panel_tecnico_docente/temperatura.html', context)

@login_required
def frecuencia(request):
    try:
        # Obtener la página actual desde la solicitud GET
        page = request.GET.get('page', 1)
        reportes_list = Lectura.objects.all().order_by('-fecha_lectura', '-hora_lectura')
        paginator = Paginator(reportes_list, 10)
        reportes = paginator.page(page)

    except PageNotAnInteger:
        reportes = paginator.page(1)

    except EmptyPage:
        reportes = paginator.page(paginator.num_pages)

    except Exception as e:
        # Manejar cualquier otro error que pueda ocurrir durante la obtención de datos
        print(f"Error al obtener reportes: {e}")
        reportes = []

    context = {
        'reportes': reportes,
    }

    return render(request, 'panel_tecnico_docente/frecuencia.html', context)

##########################################
#Metodos que consume de la plataforma movil
##########################################

class LoginView1(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'detail': 'Authentication successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

#Metodo Actualizado 
def reporte_por_id(request, id):
    # Obtener el último dato registrado para el id proporcionado
    bovino = Bovinos.objects.filter(idCollar=id).first()
    dato = Lectura.objects.filter(id_Bovino=bovino).order_by('-fecha_lectura', '-hora_lectura').first()

    if dato:
        fecha_creacion = dato.fecha_lectura.strftime('%Y-%m-%d') + ' ' + dato.hora_lectura.strftime('%H:%M:%S')
        reporte = {
            'collar_id': dato.id_Bovino.idCollar,
            'nombre_vaca': dato.id_Bovino.nombre,
            'temperatura': dato.id_Temperatura.valor,
            'pulsaciones': dato.id_Pulsaciones.valor,
            'fecha_creacion': fecha_creacion,
        }
        return JsonResponse({'reportes ': reporte}, status=200)
    else:
        return JsonResponse({'error': 'No hay datos disponibles'})
##########################################

def apiRegister(request):
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
            # Se guarda el usuario en la base de datos            
            user.save()
            # Se crea el objeto PersonalInfo y se guarda en la base de datos
            form.save()
            # Redirige a alguna página de éxito
            return JsonResponse({'message': 'Usuario creado exitosamente.'}, status=200)
        else:
            # Si hay errores, pasa el formulario y los errores al contexto de la plantilla
            return JsonResponse({'error': 'Error al crear el usuario. Inténtalo de nuevo.'}, status=400)
    else:
        # Si el método de solicitud no es POST, simplemente renderiza el formulario vacío
        form = PersonalInfoForm()
        return JsonResponse({'error': 'Intento de creación de usuario inválido.'}, status=405)

def apiList(request):
    usuarios = {}
    usuario_queryset = User.objects.all()
    profile_queryset = PersonalInfo.objects.all()

    for user in usuario_queryset:
        #sino esta en el staff no se muestra
        if  user.is_staff == True:
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
                'activo': user.is_active
            }
    if usuarios!= {}:
        return JsonResponse(usuarios, status=200)
    else:
        return JsonResponse({'error': 'No hay usuarios disponibles.'}, status=404)

def apiEdit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    print(user)
    profile = get_object_or_404(PersonalInfo, email=user.email)
    print(profile)

    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['email']
            user.first_name = form.cleaned_data['nombre']
            user.last_name = form.cleaned_data['apellido']
            user.save()
            return JsonResponse({'message': 'Usuario actualizado correctamente.'})
        else:
            return JsonResponse({'error': 'Error al actualizar el usuario. Inténtalo de nuevo.'}, status=400)
    else:
        # Si la solicitud es GET, instancia el formulario con la instancia de perfil
        form = PersonalInfoForm(instance=profile)

    return JsonResponse({'error': 'Intento de edición de usuario inválido.'}, status=405)
#########################################

##########################################
#Metodos que consume el Arduino
##########################################
@csrf_exempt  # Esto es para deshabilitar la protección CSRF en esta vista (deberías tomar medidas de seguridad apropiadas en un entorno de producción)
def lecturaDatosArduino(request):
    body_unicode = request.body.decode('utf-8')
    lecturaDecoded = json.loads(body_unicode)
    
    if request.method == 'POST':
        collar_id = lecturaDecoded.get('collar_id', None)
        nombre_vaca = lecturaDecoded.get('nombre_vaca', None)
        mac_collar = lecturaDecoded.get('mac_collar', None)
        temperatura = lecturaDecoded.get('temperatura', None)
        pulsaciones = lecturaDecoded.get('pulsaciones', None)

        if collar_id and nombre_vaca and mac_collar and temperatura and pulsaciones:
            #Primero verifica si el collar y la mac del collar ya existen en la base de datos
            if Bovinos.objects.filter(idCollar=collar_id, macCollar=mac_collar).exists():
                pass
            else:
                # Si no existen, crea un nuevo registro
                Bovinos.objects.create(
                    idCollar=collar_id,
                    macCollar=mac_collar,
                    nombre=nombre_vaca,
                    fecha_registro=datetime.now()
                )
            #Crea un nuevo registro de temperatura y pulsaciones
            temperatura_obj = Temperatura.objects.create(valor=temperatura)
            pulsaciones_obj = Pulsaciones.objects.create(valor=pulsaciones)
            Lectura.objects.create(
                id_Temperatura=temperatura_obj,
                id_Pulsaciones=pulsaciones_obj,
                id_Bovino=Bovinos.objects.get(idCollar=collar_id),
                fecha_lectura=datetime.now(),
                hora_lectura=datetime.now().time()
            )           
            return JsonResponse({'mensaje': 'Datos guardados exitosamente.'})
        else:
            print('Datos incompletos.', request.POST)
            return JsonResponse({'error': 'Datos incompletos.'})
    return JsonResponse({'error': 'Solicitud no permitida.'}, status=405)
#########################################

