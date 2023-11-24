from django.urls import path
from . import views
#from voting.views import index,obtener_detalle_votacion


urlpatterns = [
    #path("", views.index, name="index"),
    #path("obtener_detalle_votacion/<int:votacion_id>/", obtener_detalle_votacion, name="obtener_detalle_votacion"),

    path("", views.VotingView.as_view(), name="voting"),
    path("<int:voting_id>/", views.VotingUpdate.as_view(), name="voting"),
]
