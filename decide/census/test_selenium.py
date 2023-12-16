from django.test import TestCase
from base.tests import BaseTestCase
from .models import Census
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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
