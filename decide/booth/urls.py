from django.urls import path

from . import views
from .views import BoothView

urlpatterns = [
    path("", views.index, name="homepage"),
    path("obtener_detalle_votacion/<int:votacion_id>/", views.obtener_detalle_votacion, name="obtener_detalle_votacion"),
    path("vote/<int:voting_id>/", BoothView.as_view()),
    path("voting-list", views.voting_list, name="voting-list"),
]