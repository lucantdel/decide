from base.tests import BaseTestCase
from .models import Census
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ReuseCensusSeleniumTest(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        Census.objects.create(voting_id='1', voter_id='1')
        Census.objects.create(voting_id='1', voter_id='2')
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.base.tearDown()

    def test_reuse_census_interface_error(self):
        self.driver.get(self.live_server_url + '/census/reuse/')
        id_to_reuse_input = self.driver.find_element(By.ID, 'id_id_to_reuse')
        new_id_input = self.driver.find_element(By.ID, 'id_new_id')

        id_to_reuse_input.send_keys('3')
        new_id_input.send_keys('2', Keys.ENTER)

        error_message = self.driver.find_element(By.CLASS_NAME, 'alert-error')
        self.assertTrue(error_message.is_displayed())
        
    def test_reuse_census_interface(self):
        self.driver.get(self.live_server_url + '/census/reuse/')
        id_to_reuse_input = self.driver.find_element(By.ID, 'id_id_to_reuse')
        new_id_input = self.driver.find_element(By.ID, 'id_new_id')

        id_to_reuse_input.send_keys('1')
        new_id_input.send_keys('10', Keys.ENTER)

        success_message = self.driver.find_element(By.TAG_NAME, 'td').text
        self.assertTrue(success_message,"10")
        
    def test_index_census_interface(self):
        self.driver.get(self.live_server_url + '/census/')
        success_message = self.driver.find_element(By.TAG_NAME, 'td').text
        self.assertTrue(success_message,"1")

class TestExportCensusCSV(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        super().setUp()

    def tearDown(self):
        self.driver.quit()
        self.base.tearDown()
        super().tearDown()
    
    def test_empty_id(self):
        self.driver.get(self.live_server_url + "/census/")
        self.driver.set_window_size(1850, 1053)
        self.driver.find_element(By.LINK_TEXT, "Exportar Censo CSV").click()
        self.driver.find_element(By.CSS_SELECTOR, "button:nth-child(4)").click()  # Boton de previsualizar

        # Esperar y manejar la alerta
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        self.assertEqual("Por favor, introduce un valor para el ID.", alert.text)
        alert.accept()  # Aceptar la alerta

        # Proceder con la siguiente acción después de manejar la alerta
        self.driver.find_element(By.CSS_SELECTOR, "button:nth-child(5)").click()  # Boton de exportar

        # Manejar la segunda alerta si es necesario
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        self.assertEqual("Por favor, introduce un valor para el ID.", alert.text)
        alert.accept()  # Aceptar la alerta

class TestExportCensusXML(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        super().setUp()

    def tearDown(self):
        self.driver.quit()
        self.base.tearDown()
        super().tearDown()

    def test_export(self):
        self.driver.get(self.live_server_url + "/census/")
        self.driver.set_window_size(1850, 1053)
        self.driver.find_element(By.LINK_TEXT, "Exportar Censo XML").click()
        boton_export = self.driver.find_element(By.TAG_NAME, "button").text
        self.assertTrue(boton_export,"Export to XML")
