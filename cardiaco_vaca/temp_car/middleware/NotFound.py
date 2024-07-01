from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse

class NotFoundMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Verificar si la respuesta es un 404
        if response.status_code == 404:
            return self.handle_not_found(request)
        
        # Verificar si la URL contiene '/accounts/login/' y 'next' en los parámetros GET
        if '/accounts/login/' in request.path and 'next' in request.GET:
            return redirect('/')

        return response

    def handle_not_found(self, request):
        # Devuelve una respuesta HTTP 404 con la plantilla personalizada
        return HttpResponseNotFound(render(request, '404.html'))
