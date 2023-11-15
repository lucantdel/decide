from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.status import (
        HTTP_200_OK as ST_200,
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)

from django.shortcuts import render
from django.views import View
from base.perms import UserIsStaff
from .models import Census
import xml.etree.ElementTree as ET

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


"""
@csrf_exempt
def import_to_xml(request):
    if request.method == 'POST':
        try:
            # Verificar si la solicitud tiene el atributo content_type
            if request.content_type == 'application/xml':
                # Obtener el archivo XML del cuerpo de la solicitud
                xml_file = request.FILES.get('censusFile')

                # Verificar si se proporcionó un archivo
                if xml_file:
                    # Parsear el archivo XML
                    tree = ET.parse(xml_file)
                    root = tree.getroot()

                    # Procesar los elementos XML y realizar la importación
                    for entry in root.findall('entry'):
                        voting_id = entry.find('voting_id').text
                        voter_id = entry.find('voter_id').text

                        # Crear una nueva entrada en el censo o actualizar según sea necesario
                        Census.objects.update_or_create(
                            voting_id=voting_id,
                            voter_id=voter_id,
                            defaults={'voting_id': voting_id, 'voter_id': voter_id}
                        )

                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'No se proporcionó un archivo'}, status=400)
            else:
                return JsonResponse({'status': 'error', 'message': 'Tipo de contenido no admitido'}, status=415)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


            path('importar-xml/', CensusImportationFromXML.import_page, name='import_page'),

"""

class CensusImportationFromXML(View):
    def post(self, request, *args, **kwargs):
        xml_file = request.FILES['xml_file']

        # Parse el archivo XML
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Itera sobre las entradas del censo y guárdalas en la base de datos
        for entry_element in root.findall('entry'):
            voting_id = entry_element.find('voting_id').text
            voter_id = entry_element.find('voter_id').text

            # Verifica si la entrada ya existe para evitar duplicados
            if not Census.objects.filter(voting_id=voting_id, voter_id=voter_id).exists():
                Census.objects.create(voting_id=voting_id, voter_id=voter_id)

        return HttpResponse("Census imported successfully.")

    def get(self, request, *args, **kwargs):
        return render(request, 'import_xml.html')






class CensusExportationToXML():

    @staticmethod
    def export_to_xml(request):
        census = Census.objects.all()

        # Crear el elemento raíz del documento XML
        root = ET.Element("census")

        # Crear elementos XML para cada entrada en el censo
        for row in census:
            census_entry = ET.SubElement(root, "entry")
            voting_id_element = ET.SubElement(census_entry, "voting_id")
            voting_id_element.text = str(row.voting_id)
            voter_id_element = ET.SubElement(census_entry, "voter_id")
            voter_id_element.text = str(row.voter_id)

        # Convertir el árbol XML a una cadena y configurar la respuesta HTTP
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        response = HttpResponse(xml_data, content_type="application/xml")
        response["Content-Disposition"] = 'attachment; filename="censo.xml"'
        return response

    @staticmethod
    def export_page(request):
        return render(request, 'export_xml.html')


class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (UserIsStaff,)

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        try:
            for voter in voters:
                census = Census(voting_id=voting_id, voter_id=voter)
                census.save()
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')
