# En temperature_app/urls.py
from django.conf import settings
from . import views
from temp_car.views import *
#from turisticos.agenda.views import 
from django.contrib.auth import views as auth_views
from django.urls import path


urlpatterns = [
    ##################################
    #Rutas de Plataforma Web
    ##################################
    #Ruta para el Inicio de Sesion
    path('', user_login,name='login'),
    #Ruta para el Cierre de Sesion
    path('', user_logout, name='salir'),
    #Ruta para crear un usuario
    path('crear_usuario/', crear_usuario, name='crear_usuario'),
    #Rutas para restablecer contraseña
    path('reset-password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('generar_pdf/', reporte_pdf, name='generar_pdf'),
    #Rutas del dashboard
    path('monitoreo_actual/', monitoreo_actual, name='monitoreo_actual'), 
    path('reportes/', reportes, name='reportes'), 
    path('temperatura/', temperatura, name='temperatura'), 
    path('frecuencia/', frecuencia, name='frecuencia'),
    path('gestion/', gestion, name='gestion'),       
    #Rutas de gestion de datos
    path('editar_usuario/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path('desactivar/<int:usuario_id>/', desactivar_usuario, name='desactivar'),
    #Rutas para acceso al monitoreo de sensores
    path('TemperaturaListView/', TemperaturaListView.as_view(), name='TemperaturaListView'),
    path('datos-temperatura/', TemperatureDataView.as_view(), name='temperature_data_post'),
    path('pulsaciones_list/', views.pulsaciones_list, name='pulsaciones_list'),
    path('pulsaciones_list2/', views.pulsaciones_list2, name='pulsaciones_list2'),
    path('datos/', views.recibir_datos, name='recibir_datos'),
    path('mostrar_datos/', views.mostrar_datos, name='mostrar_datos'),
    path('mostrar_datos1/', views.mostrar_datos1, name='mostrar_datos1'),
    path('recibir_datos/', views.recibir_datos2, name='recibir_datos2'),
    

    ######################################
    #Rutas de Plataforma Movil  
    ######################################
    path('api/login/', user_login2, name='login2'),
    path('api/register',apiRegister, name='registrar2'),
    path('api/listar',apiList, name='listar2'),
    path('api/editar',apiEdit, name='listar2'),
    path('api/datos3/', views.obtener_datos_json3, name='obtener_datos_json3'),
    path('api/datos3/id1', views.datos3_id1, name='datos3_id1'),
    path('api/datos3/id2', views.datos3_id2, name='datos3_id2'),
    path('api/', views.pulsaciones_api, name='pulsaciones_api'),  # Nueva URL para la API REST
    path('api/datos/', views.obtener_datos_json, name='obtener_datos_json'),
    path('api/datos2/', views.obtener_datos_json2, name='obtener_datos_json2'),

]
