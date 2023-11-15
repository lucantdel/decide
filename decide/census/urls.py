from django.urls import path, include
from . import views
from .views import CensusExportationToXML

urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('export-to-xml/', CensusExportationToXML.export_to_xml, name='export-to-xml'),
    path('descargar-xml/', CensusExportationToXML.export_page, name='export-page'),
]

