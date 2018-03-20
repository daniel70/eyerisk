from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
import time

class MySeleniumTests(StaticLiveServerTestCase):
    fixtures = ['users.json', 'riskmap.json', 'riskmapvalue.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        admin = User.objects.get(username='daniel')

        self.selenium.get('%s%s' % (self.live_server_url, '/admin/'))
        username_input = self.selenium.find_element_by_name("auth-username")
        username_input.send_keys('daniel')
        password_input = self.selenium.find_element_by_name("auth-password")
        password_input.send_keys('unittestpassword')
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()

        # create a company
        self.selenium.get(self.live_server_url + '/admin/risk/company/add/')
        name = self.selenium.find_element_by_name('name')
        name.send_keys('iRisk iT')
        name.submit()

        self.selenium.get(self.live_server_url + '/admin/risk/company/')

        # create a standard that is active
        self.selenium.get(self.live_server_url + '/admin/risk/standard/add/')
        name = self.selenium.find_element_by_name('name')
        name.send_keys('Cobit 5')
        name.submit()

        # create a standard that is not active
        self.selenium.get(self.live_server_url + '/admin/risk/standard/add/')
        name = self.selenium.find_element_by_name('name')
        name.send_keys('Cobit 4')
        self.selenium.find_element_by_name('is_active').click()
        name.submit()

        self.selenium.get(self.live_server_url + '/admin/risk/standard/')

        # create a department
        self.selenium.get(self.live_server_url + '/admin/risk/department/add/')
        company = Select(self.selenium.find_element_by_id('id_company'))
        company.select_by_visible_text('iRisk iT')
        name = self.selenium.find_element_by_id('id_name')
        name.send_keys('Human Resources')
        manager = self.selenium.find_element_by_id('id_manager')
        manager.send_keys('Anouk Reus')

        self.selenium.find_element_by_name('_save').click()
        time.sleep(4)

        # create a project





