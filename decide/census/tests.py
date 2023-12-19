import random
from django.contrib.auth.models import User
from django.test import TestCase
from .forms import ReuseCensusForm
from rest_framework.test import APIClient
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import xml.etree.ElementTree as ET
from .models import Census
from base import mods
from base.tests import BaseTestCase
from datetime import datetime


TEST_VOTING_ID=100


class CensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        response = self.client.get('/census/{}/?voter_id={}'.format(1, 2), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 'Invalid voter')
        response = self.client.get('/census/{}/?voter_id={}'.format(1, 1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Valid voter')

    def test_list_voting(self):
        response = self.client.get('/census/createCensus/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 401)
        self.login(user='noadmin')
        response = self.client.get('/census/createCensus/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 403)
        self.login()
        response = self.client.get('/census/createCensus/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'voters': [1]})

    def test_add_new_voters_conflict(self):
        data = {'voting_id': 1, 'voters': [1]}
        response = self.client.post('/census/createCensus/', data, format='json')
        self.assertEqual(response.status_code, 401)
        self.login(user='noadmin')
        response = self.client.post('/census/createCensus/', data, format='json')
        self.assertEqual(response.status_code, 403)
        '''self.login()
        response = self.client.post('/census/createCensus/', data, format='json')
        self.assertEqual(response.status_code, 409)'''

    def test_add_new_voters(self):
        data = {'voting_id': 2, 'voters': [1,2,3,4]}
        response = self.client.post('/census/createCensus/', data, format='json')
        self.assertEqual(response.status_code, 401)
        self.login(user='noadmin')
        response = self.client.post('/census/createCensus/', data, format='json')
        self.assertEqual(response.status_code, 403)
        self.login()
        response = self.client.post('/census/createCensus/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get('voters')), Census.objects.count() - 1)
        
    def test_destroy_voter(self):
        data = {'voters': [1]}
        response = self.client.delete('/census/{}/'.format(1), data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())


class CensusExportationXML(TestCase):
    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_positive_export_to_xml(self):
        response = self.client.get('/census/export-to-xml/', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/xml')

        expected_elements = ['<census>', '<entry>', '<voting_id>1</voting_id>', '<voter_id>1</voter_id>', '</entry>', '</census>']
        for element in expected_elements:
            self.assertIn(element, response.content.decode())

    def test_admin_access(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get('/census/export-to-xml/', format='json')
        self.assertEqual(response.status_code, 200)

    def test_download_from_html(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('export-page'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/html; charset=utf-8')

        # Verifica la presencia del botón en lugar del enlace
        expected_button = '<button onclick="window.location.href=\'/census/export-to-xml/\'">Export to XML</button>'
        self.assertIn(expected_button, response.content.decode())   

class CensusImportationXML(TestCase):
    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_positive_import_from_xml(self):
        xml_content = b'<census><entry><voting_id>1</voting_id><voter_id>1</voter_id></entry></census>'
        xml_file = SimpleUploadedFile("census.xml", xml_content, content_type="application/xml")

        response = self.client.post('/census/importar-xml/', {'xml_file': xml_file}, format='multipart')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Census imported successfully.", response.content.decode())
    
    def test_negative_import_from_xml(self):
        xml_content = b'Texto'
        xml_file = SimpleUploadedFile("census.xml", xml_content, content_type="application/xml")

        response = self.client.post('/census/importar-xml/', {'xml_file': xml_file}, format='multipart')

        self.assertEqual(response.status_code, 400)

    def test_import_invalid_xml(self):
        txt_content = b'This is not XML content.'
        xml_file = SimpleUploadedFile("invalid_format.xml", txt_content, content_type="application/xml")

        initial_count = Census.objects.all().count()

        response = self.client.post('/census/importar-xml/', {'xml_file': xml_file})

        self.assertEqual(response.status_code, 400)  
        self.assertIn("Error importing census. Invalid XML format.", response.content.decode())

        final_count = Census.objects.all().count()

        self.assertEqual(initial_count, final_count, "No new voters should be added to the database.")

    def test_admin_access(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get('/census/importar-xml/', format='json')
        self.assertEqual(response.status_code, 200)

class CensusTest(StaticLiveServerTestCase):
    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    
    def createCensusSuccess(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/census/census/add")
        now = datetime.now()
        self.cleaner.find_element(By.ID, "id_voting_id").click()
        self.cleaner.find_element(By.ID, "id_voting_id").send_keys(now.strftime("%m%d%M%S"))
        self.cleaner.find_element(By.ID, "id_voter_id").click()
        self.cleaner.find_element(By.ID, "id_voter_id").send_keys(now.strftime("%m%d%M%S"))
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/census/census")

    def createCensusEmptyError(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/census/census/add")

        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[3]/div/div[1]/div/form/div/p').text == 'Please correct the errors below.')
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/census/census/add")

    def createCensusValueError(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/census/census/add")
        now = datetime.now()
        self.cleaner.find_element(By.ID, "id_voting_id").click()
        self.cleaner.find_element(By.ID, "id_voting_id").send_keys('64654654654654')
        self.cleaner.find_element(By.ID, "id_voter_id").click()
        self.cleaner.find_element(By.ID, "id_voter_id").send_keys('64654654654654')
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[3]/div/div[1]/div/form/div/p').text == 'Please correct the errors below.')
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/census/census/add")
        
class ReuseCensusViewTests(TestCase):

    def setUp(self):
        Census.objects.create(voting_id='1', voter_id='1')
        Census.objects.create(voting_id='2', voter_id='2')

    def test_get_request_returns_form(self):
        response = self.client.get(reverse('reuse'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reuse.html')
        self.assertIsInstance(response.context['form'], ReuseCensusForm)

    def test_post_request_no_existing_census(self):
        response = self.client.post(reverse('reuse'), {'id_to_reuse': '999', 'new_id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No existen censos para todos los IDs proporcionados para reutilizar.")

    def test_invalid_post_request_returns_error_message_2(self):
        response = self.client.post(reverse('reuse'), {'id_to_reuse': 'abc', 'new_id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reuse.html')
        self.assertContains(response, "Error: Se proporcionó un ID no numérico.")

class CensusExportCSVTest(TestCase):
    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=100, voter_id=100)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_export_csv_existing_census(self):
        response = self.client.get('/census/' + str(100) + '/export_csv/', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/csv')

        # Leer el contenido de la respuesta y convertirlo a una lista de líneas no vacías
        content = response.content.decode('utf-8')
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        # Comprobar si el contenido del CSV es correcto
        self.assertEqual(len(lines), 2)  # Asegurarse de que hay dos líneas (encabezado y un dato)
        self.assertEqual(lines[0], 'voter_id')  # Comprobar el encabezado
        self.assertEqual(lines[1], '100')  # Comprobar el valor de voter_id

    def test_export_csv_not_existing_census(self):
        response = self.client.get('/census/' + str(101) + '/export_csv/', format='json')
        self.assertEqual(response.status_code, 404)

    def test_export_csv_invalid_id(self):
        response = self.client.get('/census/' + 'abc' + '/export_csv/', format='json')
        self.assertEqual(response.status_code, 404)

class CensusImportCSVTest(TestCase):

    def setUp(self):
        super().setUp()
    
    def tearDown(self):
        super().tearDown()

    def test_import_valid_csv(self):
        with open('census/test_files/valid_census.csv', 'rb') as file:  # Modo 'rb' para lectura binaria
            file_content = file.read()
        
        test_file = SimpleUploadedFile("testcensus.csv", file_content, content_type="text/csv")

        # Envío del archivo CSV a través de una solicitud POST
        response = self.client.post('/census/import_csv/', {'csv_file': test_file, 'voting_id': TEST_VOTING_ID})

        # Verificar la respuesta y el estado de la base de datos
        self.assertContains(response, "Census imported successfully.")
        self.assertTrue(Census.objects.filter(voting_id=TEST_VOTING_ID, voter_id=23).exists())
        self.assertTrue(Census.objects.filter(voting_id=TEST_VOTING_ID, voter_id=24).exists())

    def test_import_invalid_csv(self):
        with open('census/test_files/census_with_duplicates.csv', 'rb') as file:
            file_content = file.read()

        test_file = SimpleUploadedFile("testcensus.csv", file_content, content_type="text/csv")

        # Envío del archivo CSV a través de una solicitud POST
        response = self.client.post('/census/import_csv/', {'csv_file': test_file, 'voting_id': TEST_VOTING_ID})

        # Verificar la respuesta y el estado de la base de datos
        self.assertContains(response, "Census imported successfully.")
        
        # Asegurarse de que se importaron solo 4 votantes únicos
        unique_voters = Census.objects.filter(voting_id=TEST_VOTING_ID).count()
        self.assertEqual(unique_voters, 4)
        self.assertTrue(Census.objects.filter(voting_id=TEST_VOTING_ID, voter_id=1).exists())
        self.assertTrue(Census.objects.filter(voting_id=TEST_VOTING_ID, voter_id=2).exists())
        self.assertTrue(Census.objects.filter(voting_id=TEST_VOTING_ID, voter_id=3).exists())
        self.assertTrue(Census.objects.filter(voting_id=TEST_VOTING_ID, voter_id=4).exists())