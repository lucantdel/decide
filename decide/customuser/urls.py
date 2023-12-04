from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import RegisterUserView


urlpatterns = [
    path("registrousuarios/", RegisterUserView.as_view()),]
