from django.urls import path
from .views import VotingView, VotingUpdate

urlpatterns = [
    path('', VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', VotingUpdate.as_view(), name='voting'),
    path('<str:campo_personalizable>/', VotingView.as_view(), name='voting-detail'),
]
