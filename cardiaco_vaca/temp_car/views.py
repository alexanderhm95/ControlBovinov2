from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model,login,logout,authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from xhtml2pdf import pisa
from io import BytesIO
from .models import *
from .forms import *
import random
import json
import urllib.parse
from datetime import time

####################################
#Metodos de plataforma web       
####################################

def prueba(request):
    return render(request, 'appMonitor/dashboard/temperature.html')

def error_404_view(request, exception):
    return render(request, '404.html', status=404)

############Dashboard################
# Dashboard Monitoreo Actual toda la logica esta dentro 
@login_required
def monitoreo_actual(request):
    collares = Bovinos.objects.all()  # Ejemplo de obtener todos los collares
    context = {
        'collares': collares,
        'idCollar': 1,  # Ejemplo de pasar un id de collar específico
    }
    return render(request, 'appMonitor/dashboard/monitor.html', context)

def dashBoardData(request, id_collar=None):
    # Validar si se proporcionó un id_collar
    if id_collar is None:
        return JsonResponse({'error': 'Se requiere un id_collar'}, status=400)

    # Obtener el bovino asociado al id_collar
    try:
        bovino = Bovinos.objects.get(idCollar=id_collar)
    except Bovinos.DoesNotExist:
        return JsonResponse({'error': 'Collar no encontrado'}, status=404)

    # Obtener el último registro de lectura del bovino
    lectura = Lectura.objects.filter(id_Bovino=bovino).order_by('-fecha_lectura', '-hora_lectura').first()
    if not lectura:
        return JsonResponse({'error': 'No hay lecturas disponibles para este collar'}, status=404)

    # Crear la información del collar
    collar_info = {
        'idCollar': bovino.idCollar,
        'nombre': bovino.nombre,
        'temperatura': lectura.id_Temperatura.valor,
        'pulsaciones': lectura.id_Pulsaciones.valor,
        'fecha_registro': lectura.fecha_lectura.strftime('%Y-%m-%d') + " " + lectura.hora_lectura.strftime('%H:%M:%S'),
    }

    # Obtener las últimas 10 lecturas del bovino
    ultimas_lecturas = ControlMonitoreo.objects.filter(id_Lectura__id_Bovino=bovino).order_by('-fecha_lectura', '-hora_lectura')[:10]

    # Crear la lista de registros
    registros = []
    for lectura in ultimas_lecturas:
        registros.append({
            'temperatura': lectura.id_Lectura.id_Temperatura.valor,
            'pulsaciones': lectura.id_Lectura.id_Pulsaciones.valor,
            'fecha_registro': lectura.fecha_lectura.strftime('%Y-%m-%d') + " " + lectura.hora_lectura.strftime('%H:%M:%S'),
        })

    # Crear el cuerpo de la respuesta
    body = {
        'collar_info': collar_info,
        'ultimos_registros': registros,
    }

    return JsonResponse(body, status=200)


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
            # Convertir la fecha de búsqueda a un objeto datetime
            fecha_busqueda = datetime.strptime(fecha_busqueda, '%Y-%m-%d')

            # Calcular el rango de tiempo para el día específico
            inicio_dia = fecha_busqueda
            fin_dia = fecha_busqueda + timedelta(days=1)

            # Filtrar los reportes en el rango del día
            reportes_list = reportes_list.filter(fecha_lectura__gte=inicio_dia, fecha_lectura__lt=fin_dia)
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
        'fecha_busqueda': fecha_busqueda.strftime('%Y-%m-%d') if fecha_busqueda else '',
    }

    return render(request, 'appMonitor/dashboard/reports.html', context)

def reporte_pdf(request):
    fecha_busqueda = request.GET.get('fecha_busqueda')
    reportes = Lectura.objects.all()

    if fecha_busqueda:
        try:
            fecha_busqueda = datetime.strptime(fecha_busqueda, '%Y-%m-%d').date()
            reportes = reportes.filter(fecha_lectura__date=fecha_busqueda)
        except ValueError:
            # Manejo de error si la fecha ingresada no es válida
            return HttpResponse("Fecha de búsqueda inválida.", status=400)

    context = {
        'reportes': reportes,
        'fecha_busqueda': fecha_busqueda.strftime('%Y-%m-%d') if fecha_busqueda else None,
    }

    table_content = get_template('appMonitor/dashboard/reports.html').render(context).split('<table id="tablaReportes" class="table table-bordered table-hover">')[1].split('</table>')[0]
    print(table_content)
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
    <p style="font-size: 12px; color: #333; margin: 0;">© All rights reserved | Carrera de Ingeniería en Computación</p>
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
        
        collares = Bovinos.objects.all()

    except PageNotAnInteger:
        reportes = paginator.get_page(1)
    except EmptyPage:
        reportes = paginator.get_page(paginator.num_pages)
    except Exception as e:
        print(f"Error al obtener reportes: {e}")
        reportes = []

    context = {
        'reportes': reportes,
        'collares': collares,
    }
    print("Collares: ", collares)
    return render(request, 'appMonitor/dashboard/temperature.html', context)


@login_required
def frecuencia(request):
    try:
        # Obtener la página actual desde la solicitud GET
        page = request.GET.get('page', 1)
        reportes_list = Lectura.objects.all().order_by('-fecha_lectura', '-hora_lectura')
        paginator = Paginator(reportes_list, 10)
        reportes = paginator.page(page)
        
        collares = Bovinos.objects.all()

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
        'collares': collares,
    }

    return render(request, 'appMonitor/dashboard/heartRate.html', context)

##########################################
#Metodos que consume de la plataforma movil
##########################################

class LoginView1(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        print("Usuario: ", user)
        personaInfo = PersonalInfo.objects.filter(email=username).first()
        print("Persona: ", personaInfo)
        # Dividir el nombre y tomar solo la primera parte
        primer_nombre = personaInfo.nombre.split(' ')[0]
        # Dividir el apellido y tomar solo la primera parte
        primer_apellido = personaInfo.apellido.split(' ')[0]
        body = {
            'username': username,
            'Nombres': primer_nombre + ' ' + primer_apellido,
        }
        if user is not None:
            login(request, user)
            return Response({'detalle': 'Inicio de sesión exitoso', 'data': body}, status=status.HTTP_200_OK)
        else:
            return Response({'detalle': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

#Metodo Actualizado 
from temp_car.utils.monitorChecking import checkingMorning, checkingAfternoon,checkHoursMorning,checkHoursAfternoon, checkDate

@csrf_exempt
def reporte_por_id(request):
    # Obtener el último dato registrado para el id proporcionado
    bovino = Bovinos.objects.filter(idCollar=request.POST.get('sensor')).first()
    user = User.objects.filter(username=request.POST.get('username')).first()
    dato = Lectura.objects.filter(id_Bovino=bovino).order_by('-fecha_lectura', '-hora_lectura').first()

    if dato:
        fecha_creacion = dato.fecha_lectura.strftime('%Y-%m-%d') + ' ' + dato.hora_lectura.strftime('%H:%M:%S')
        registro = False

        # Verificar condiciones para la mañana
        if checkingMorning(bovino) and checkHoursMorning(dato.hora_lectura) and checkDate(dato.fecha_lectura):
            ControlMonitoreo.objects.create(
                id_Lectura=dato,
                id_User=user,
            )
            registro = True

        # Verificar condiciones para la tarde
        elif checkingAfternoon(bovino) and checkHoursAfternoon(dato.hora_lectura) and checkDate(dato.fecha_lectura):
            ControlMonitoreo.objects.create(
                id_Lectura=dato,
                id_User=user,
            )
            registro = True

        reporte = {
            'collar_id': dato.id_Bovino.idCollar,
            'nombre_vaca': dato.id_Bovino.nombre,
            'temperatura': dato.id_Temperatura.valor,
            'pulsaciones': dato.id_Pulsaciones.valor,
            'fecha_creacion': fecha_creacion,
            'registrado': registro,
        }
        return JsonResponse({'reporte': reporte}, status=200)
    else:
        return JsonResponse({'error': 'No hay datos disponibles'}, status=400)


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
    print("Entro al 1")
    body_unicode = request.body.decode('utf-8')
    lecturaDecoded = json.loads(body_unicode)
    
    if request.method == 'POST':
        print("Entro al 2")
        collar_id = lecturaDecoded.get('collar_id', None)
        nombre_vaca = lecturaDecoded.get('nombre_vaca', None)
        mac_collar = lecturaDecoded.get('mac_collar', None)
        temperatura = lecturaDecoded.get('temperatura', None)
        pulsaciones = random.randint(41, 60)

        if collar_id and nombre_vaca and mac_collar and temperatura and pulsaciones:
            print("Entro al 3")

            #Primero verifica si el collar y la mac del collar ya existen en la base de datos
            if Bovinos.objects.filter(idCollar=collar_id, macCollar=mac_collar).exists():
                print("Entro al 4")
                pass
            else:
                print("Entro al 4 crear")
                # Si no existen, crea un nuevo registro
                Bovinos.objects.create(
                    idCollar=collar_id,
                    macCollar=mac_collar,
                    nombre=nombre_vaca,
                    fecha_registro=datetime.now()
                )
            #Crea un nuevo registro de temperatura y pulsaciones
            print("Entro al 5")
            temperatura_obj = Temperatura.objects.create(valor=temperatura)
            pulsaciones_obj = Pulsaciones.objects.create(valor=pulsaciones)
            Lectura.objects.create(
                id_Temperatura=temperatura_obj,
                id_Pulsaciones=pulsaciones_obj,
                id_Bovino=Bovinos.objects.get(idCollar=collar_id),
                fecha_lectura=datetime.now(),
                hora_lectura=datetime.now().time()
            )  
            print("Entro al 6")         
            return JsonResponse({'mensaje': 'Datos guardados exitosamente.'})
        else:
            print('Datos incompletos.', request.POST)
            return JsonResponse({'error': 'Datos incompletos.'})
    return JsonResponse({'error': 'Solicitud no permitida.'}, status=405)
#########################################

