from django.urls import path, include
from . import views


urlpatterns = [
    path('createCensus/', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('<int:voting_id>/export_csv/', views.CensusExportCSV.as_view(), name='download_csv'),
    path('export_csv/', views.CensusExportCSV.export_page, name='export_csv'),
    path('import_csv/', views.CensusImportCSV.as_view(), name='import_csv'),
]
