from rest_framework.response import Response
from rest_framework.status import (
        HTTP_400_BAD_REQUEST,
)
from rest_framework.views import APIView
from django.db import IntegrityError
from django.shortcuts import render
from django.shortcuts import  render

from .models import CustomUser
from django.contrib.auth.hashers import make_password

from django.core.mail import send_mail

class RegisterUserView(APIView):
    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        username = request.data.get("username", "")
        pwd = request.data.get("password", "")
        email = request.data.get("email", "")
        confirm_pwd = request.data.get("password_conf", "")
        if not username or not pwd or not email or not confirm_pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        error_messages = []

        if CustomUser.objects.filter(username=username).exists():
            error_messages.append("El nombre de usuario se encuentra en la base de datos.")
        if len(pwd) < 8:
            error_messages.append("La contraseña debe de estar formada por más de 8 caracteres.")
        if pwd.isdigit():
            error_messages.append("La contraseña debe contener letras, números y caracteres especiales.")
        if pwd != confirm_pwd:
            error_messages.append("Las contraseñas no coinciden.")
        if CustomUser.objects.filter(email=email).exists():
            error_messages.append("Esta dirección de correo pertenece a otro usuario")
        if len(username) < 0:
            error_messages.append("El nombre de usuario no puede estar vacío")
        if error_messages:
            return render(request, "register.html", {"error_messages": error_messages}, status=HTTP_400_BAD_REQUEST)
        try:
            hashed_pwd = make_password(pwd)
            user = CustomUser(username=username, email=email, password=hashed_pwd)
            user.save()
            
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        register_success = "Se ha creado correctamente su cuenta"
        enviar_correo_confirmacion(email)
        return render(request, "register.html", {"register_success": register_success})
    
def enviar_correo_confirmacion(user_email):
    # Customize this function to suit your email content and settings
    subject = 'Confirmación de Registro'
    message = f'Gracias por registrarse!'
    from_email = 'egc-rivera-register@outlook.es'
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)



