from django.contrib import messages
from django.db.utils import IntegrityError
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from base.perms import UserIsStaff
import csv
from .models import Census
import xml.etree.ElementTree as ET

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

class CensusExportCSV(generics.ListAPIView):
    #permission_classes = (UserIsStaff,)

    def list(self, request, *args, **kwargs):
        voting_id = self.kwargs['voting_id']

        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)

        # Crear el objeto HttpResponse con el tipo de contenido adecuado para un archivo CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="voting_{voting_id}_census.csv"'

        # Crear el escritor CSV
        writer = csv.writer(response)

        # Escribir la fila de encabezados si es necesario
        writer.writerow(['voter_id'])

        # Escribir los datos en filas
        for voter_id in voters:
            writer.writerow([voter_id])

        return response
    
    @staticmethod
    def export_page(request):
        return render(request, 'export_csv.html')

class CensusImportCSV(generics.ListAPIView):
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES['csv_file']
        voting_id = self.request.POST.get('voting_id')  # Obtener el voting_id desde el formulario
        
        # Procesar el archivo CSV utilizando csv.reader
        csv_reader = csv.reader(csv_file.read().decode('utf-8').splitlines())

        # Itera sobre las filas del CSV y guárdalas en la base de datos
        for row in csv_reader:
            # Ignora la primera fila si tiene encabezado
            if not row[0].isdigit():
                next(csv_reader)
                
            # Suponiendo que tu archivo CSV tiene una columna: voter_id
            voter_id = row[0]  # Ajusta el índice según la posición de la columna en tu CSV

            # Verifica si la entrada ya existe para evitar duplicados
            if not Census.objects.filter(voting_id=voting_id, voter_id=voter_id).exists():
                Census.objects.create(voting_id=voting_id, voter_id=voter_id)

        return HttpResponse("Census imported successfully.")

    def get(self, request, *args, **kwargs):
        return render(request, 'import_csv.html')

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


class CensusView(TemplateView):
    template_name = 'census/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        censos = Census.objects.all().order_by('voting_id')
        censos_por_voting_id = {}

        for censo in censos:
            voting_id = censo.voting_id
            if voting_id not in censos_por_voting_id:
                censos_por_voting_id[voting_id] = []
            censos_por_voting_id[voting_id].append(censo)

        context['censos_por_voting_id'] = censos_por_voting_id
        return context

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


def reuse_census_view(request):
    if request.method == 'POST':
        form = ReuseCensusForm(request.POST)
        if form.is_valid():
            reuse_voting_id = form.cleaned_data['id_to_reuse']

            # Lógica de reutilización de censos similar a la de reuse_action
            if reuse_voting_id is not None:
                reuse_voting_id = str(reuse_voting_id)  # Convierte a cadena si es un número entero

                if reuse_voting_id.strip():
                    for census in Census.objects.all():
                        if Census.objects.filter(voting_id=reuse_voting_id, voter_id=census.voter_id).exists():
                            messages.error(request, f"Ya existe Censo con voter_id {census.voter_id} y voting_id {reuse_voting_id} en la base de datos.")
                            continue
                        re_census = Census()
                        re_census.voter_id = census.voter_id
                        re_census.voting_id = reuse_voting_id
                        re_census.save()
                    messages.success(request, f"Censos reutilizados con ID: {reuse_voting_id}") 
                    return redirect('home')
                else:
                    messages.error(request, "Error: Formulario no válido. Asegúrate de ingresar un ID válido.")
    else:
        form = ReuseCensusForm()

    return render(request, 'reuse.html', {'form': form})
