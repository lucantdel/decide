from django.urls import path, include
from . import views
from .views import CensusExportationToXML
from .views import CensusImportationFromXML

urlpatterns = [
    path('', views.CensusView.as_view()),
    path('createCensus/', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('export-to-xml/', CensusExportationToXML.export_to_xml, name='export-to-xml'),
    path('descargar-xml/', CensusExportationToXML.export_page, name='export-page'),
    path('importar-xml/', CensusImportationFromXML.as_view(), name='import-from-xml'),
    path('<int:voting_id>/export_csv/', views.CensusExportCSV.as_view(), name='download_csv'),
    path('export_csv/', views.CensusExportCSV.export_page, name='export_csv'),
    path('import_csv/', views.CensusImportCSV.as_view(), name='import_csv'),
]
