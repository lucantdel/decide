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
        
        error_messages = []

        if CustomUser.objects.filter(username=username).exists():
            error_messages.append(
                "El nombre de usuario se encuentra en la base de datos."
            )

        if len(pwd) < 8:
            error_messages.append("La contraseña debe de estar formada por mas de 8 carácteres.")

        if pwd.isdigit():
            error_messages.append(
                "La contraseña debe conetener letras, números y carácteres especiales."
            )

        if pwd != confirm_pwd:
            error_messages.append("Las contraseñas no coinciden.")

        if error_messages:
            return render(request, "register.html", {"error_messages": error_messages})

        try:
            hashed_pwd = make_password(pwd)
            user = CustomUser(username=username, email=email, password=hashed_pwd)
            user.save()
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        register_success = "Se ha creado correctamente su cuenta"
        return render(request, "register.html", {"register_success": register_success})

