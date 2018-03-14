from django.test import TestCase, Client
from django.contrib import auth
from django.urls.base import reverse
from .forms import *

from risk.models import Employee
from .models import Company

# riskmap voorbeeld toevoegen bij het aanmaken/wijzigen van risk maps

# impact 4 van een risk map mag niet lager zijn dan impact 3 etc.

password = 'sup3rd1ff1cult'


class AdminTests(TestCase):
    fixtures = ['riskmap.json', 'riskmapvalue.json']

    def test_if_is_admin(self):
        user = User.objects.create_superuser(username='testadmin', password=password, email='test@eyerisk.nl')
        company = Company.objects.create(name='ACME')
        employee = Employee.objects.create(user=user, company=company)
        employee.save()
        self.assertTrue(user.is_authenticated())
        self.client.force_login(user=user)
        response = self.client.get('/risk/selection/')
        self.assertEqual(response.status_code, 200)


class SimpleTest(TestCase):
    fixtures = ['riskmap.json', 'riskmapvalue.json']

    url_names = [
        ['selection-list', [], {}],
        ['selection-add', [], {}],
        ['selection-edit', [], {'pk': '1'}],
        ['selection-delete', [], {'pk': '1'}],
        ['selection-response', [], {'pk': '1'}],

        ['risk-map-list', [], {}],
        ['risk-map-list', [], {'pk': '1'}],

        ['scenario-list', [], {}],
        ['scenario-edit', [], {'pk': '1'}],
        ['scenario-delete', [], {'pk': '1'}],

        ['impact-list', [], {}],
    ]

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(username='user', password=password)
        cls.user.set_password(password)
        cls.user.save()

        cls.company = Company.objects.create(name='ACME')
        cls.employee = User.objects.create_user(username='employee', password=password)
        cls.employee.set_password(password)
        cls.employee.save()
        emp = Employee.objects.create(user=cls.employee, company=cls.company)
        emp.save()

        cls.admin = User.objects.create_superuser(username='admin', email='me@eyerisk.nl', password=password)
        cls.admin.set_password(password)
        cls.admin.save()

    def test_no_access_as_anonymous(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_login_fails_with_invalid_credentials(self):
        response = self.client.post('/account/login/', {'auth-username': 'admin',
                                                        'auth-password': 'welcome123',
                                                        'login_view-current_step': 'auth'})
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated(), "Client with invalid credentials should not be authenticated")

    def test_views_are_invalid_for_client_without_company(self):
        self.client.force_login(self.user)
        response = self.client.get('/selection/')
        self.assertEqual(response.status_code, 302)

    def test_admin_can_access_admin_site(self):
        self.client.force_login(self.admin)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_employee_can_access_site(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse('risk-home'))
        self.assertEqual(response.status_code, 200)