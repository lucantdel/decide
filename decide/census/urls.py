from django.urls import path, include
from . import views


urlpatterns = [
    path('createCensus/', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('<int:voting_id>/export_csv/', views.CensusExportCSV.as_view(), name='census_export_csv'),
    path('export_csv/', views.CensusExportCSV.export_page, name='export_page'),
]
