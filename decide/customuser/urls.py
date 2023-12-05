from django.urls import path

from .views import RegisterUserView


urlpatterns = [
    path("registrousuarios/", RegisterUserView.as_view()),]
