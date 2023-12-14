from django.urls import path
from .views import BoothView


urlpatterns = [
    path('<int:voting_id>/', BoothView.as_view()),
    path('<str:campo_personalizable>/', BoothView.as_view(), name='booth-detail'),
]
