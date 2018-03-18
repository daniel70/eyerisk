from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver


class MySeleniumTests(StaticLiveServerTestCase):
    fixtures = ['users.json']

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

        # create a standard that is active
        self.selenium.get(self.live_server_url + '/admin/risk/standard/add/')
        name = self.selenium.find_element_by_name("name")
        name.send_keys('Cobit 5')
        name.submit()

        # create a standard that is not active
        self.selenium.get(self.live_server_url + '/admin/risk/standard/add/')
        name = self.selenium.find_element_by_name("name")
        name.send_keys('Cobit 4')
        name.submit()

        self.selenium.get(self.live_server_url + '/admin/risk/standard/')
        self.selenium.implicitly_wait(100)

