from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.CensusView.as_view()),
    path('createCensus/', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
]
