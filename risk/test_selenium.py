from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver


class MySeleniumTests(StaticLiveServerTestCase):
    # fixtures = ['user-data.json']

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
        self.selenium.get('%s%s' % (self.live_server_url, '/account/login/'))
        username_input = self.selenium.find_element_by_name("auth-username")
        username_input.send_keys('daniel')
        password_input = self.selenium.find_element_by_name("auth-password")
        password_input.send_keys('wrongpassword')
        self.selenium.find_element_by_xpath('//button[@value="Next"]').click()