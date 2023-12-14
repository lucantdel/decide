from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class LoginForm(forms.Form):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder":"Nombre de usuario", "class":"form-control"}))

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder":"Contraseña", "class":"form-control"}))