from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .serializers import UserSerializer

from rest_framework import status
import difflib
from .models import CustomUser
from django.contrib.auth.hashers import make_password

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

        # Check if there are any error messages before returning
        if error_messages:
            return render(request, "register.html", {"error_messages": error_messages}, status=HTTP_400_BAD_REQUEST)

        try:
            hashed_pwd = make_password(pwd)
            user = CustomUser(username=username, email=email, password=hashed_pwd)
            user.save()
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        register_success = "Se ha creado correctamente su cuenta"
        return render(request, "register.html", {"register_success": register_success})

