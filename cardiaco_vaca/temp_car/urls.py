# En temperature_app/urls.py
from django.conf import settings
from . import views
from temp_car.views import *
#from turisticos.agenda.views import 
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls.static import static

urlpatterns = [
    ##################################
    #Rutas de Plataforma Web
    ##################################
    #Ruta para el Inicio de Sesion
    path('', user_login,name='login'),
    #Ruta para el Cierre de Sesion
    path('', user_logout, name='salir'),
    #Rutas de gestion de datos
    path('gestion/', gestion, name='gestion'),    
    path('crear_usuario/', crear_usuario, name='crear_usuario'),  
    #path('editar_usuario/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path('editar_usuario/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path('changeState/<int:usuario_id>/', desactivar_usuario, name='changeState'),
    #Rutas para restablecer contraseña
    path('reset-password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    #Rutas del dashboard
    path('monitoreo_actual/', monitoreo_actual, name='monitoreo_actual'),
    path('monitor/datos/', views.obtener_datos_json3, name='datos'),
    path('ultimo/registro/<int:collar_id>', views.ultimoRegistro, name='ultimo_registro'),
    #Ambas rutas trabajan juntas monitoreo y datos3
    path('reportes/', reportes, name='reportes'), 
    path('generar_pdf/', reporte_pdf, name='generar_pdf'),
    path('temperatura/', temperatura, name='temperatura'), 
    path('frecuencia/', frecuencia, name='frecuencia'),
       
  
    #Rutas para acceso al monitoreo de sensores

 
    

    ######################################
    #Rutas de Plataforma Movil  
    ######################################
    path('api/movil/login/', LoginView1.as_view(), name='api-login'),                     # Api para el login
    path('api/movil/datos/<int:id>', views.reporte_por_id, name='datos3_por_id'),   # Api para obtener datos de los collares
    path('api/register',apiRegister, name='registrar2'),                            #Desarrollado para pruebas
    path('api/listar',apiList, name='listar2'),                                     #Desarrollado para pruebas
    path('api/editar',apiEdit, name='listar2'),                                     #Desarrollado para pruebas
    #############################################################
    

    ######################################
    #Ruta para el Arduino 
    ######################################
    path('api/arduino/monitoreo', views.lecturaDatosArduino, name='recibir_datos2'),
    ######################################

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'temp_car.views.error_404_view'
