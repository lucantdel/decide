from django.http import HttpResponse
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from .form import LoginForm
from .serializers import UserSerializer

from rest_framework import status
import difflib
from .models import CustomUser
from django.contrib.auth.hashers import make_password

class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})


class RegisterView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)

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
        try:
            hashed_pwd = make_password(pwd)
            user = CustomUser(username=username, email=email, password=hashed_pwd)
            user.save()
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        register_success = "Se ha creado correctamente su cuenta"
        return render(request, "register.html", {"register_success": register_success})
    
class LoginUserView(APIView):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            print(username + " " + password)
            print(user)
            
            if not username or not password:
                return HttpResponse(status=400)  
            
            if user is not None:
                login(request, user)
                # Usuario autenticado con éxito.
                return HttpResponse("Inicio de sesión exitoso")
            else:
                # Usuario no autenticado.
                return render(request, "login.html", {"error_message": "Credenciales incorrectas"})
    
