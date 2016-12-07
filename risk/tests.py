from django.test import TestCase, SimpleTestCase
from django.contrib import auth
from django.urls.base import reverse
from django.conf import settings
from django.contrib.auth.models import User, Group

from risk.models import Employee, Impact
from .models import Company, RiskMap, RiskMapValue

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
        cls.user = User.objects.create_user(username='testuser', password=password)
        cls.user.set_password(password)
        cls.user.save()

        cls.admin = User.objects.create_superuser(username='adminuser', email='me@eyerisk.nl', password=password)
        cls.admin.set_password(password)
        cls.admin.save()

        cls.company = Company.objects.create(name='ACME')

    def test_no_access_as_anonymous(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_login_fails_with_invalid_credentials(self):
        response = self.client.post('/account/login/', {'auth-username': 'admin',
                                                        'auth-password': 'welcome123',
                                                        'login_view-current_step': 'auth'})
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated(), "Client with invalid credentials should not be authenticated")

    def test_views_redirect_to_login_for_unauthorized_client(self):
        self.assertEqual(self.client.get(reverse('risk-map-create')).status_code, 302)
        self.assertEqual(self.client.get(reverse('risk-map-create-category')).status_code, 302)

        login_url = settings.LOGIN_URL
        for name, args, kwargs in SimpleTest.url_names:
            url = reverse(name, args=args, kwargs=kwargs)
            expected_url = "%s?next=%s" % (login_url, url)
            self.assertRedirects(self.client.get(url, follow=True), expected_url=expected_url)

    def test_views_are_invalid_for_client_without_company(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/selection/').status_code, 302)

    def test_views_are_accessible_for_admins(self):
        employee = Employee.objects.create(user=self.admin, company=self.company)
        self.client.force_login(self.admin)
        response = self.client.get(reverse('selection-list'))
        self.assertEqual(response.status_code, 200)


class CompanyTests(TestCase):
    """
    When a company is created then a risk map called 'ENTERPRISE' shoud also be created as well as 10 risk map values.
    """
    fixtures = ['riskmap.json', 'riskmapvalue.json']

    def setUp(self):
        pass

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name='ACME')

    def test_if_company_exists(self):
        self.assertTrue(Company.objects.filter(name='ACME').exists())

    def test_if_risk_map_is_created_when_company_is_created(self):
        self.assertEqual(RiskMap.objects.get(company__name='ACME').name, 'ENTERPRISE')
        self.assertEqual(self.company.riskmap_set.count(), 1, "There should be exactly one risk map for Company")

    def test_if_ten_risk_map_values_are_created_when_company_is_created(self):
        risk_map = RiskMap.objects.get(company__name='ACME')
        self.assertEqual(risk_map.riskmapvalue_set.all().count(), 10)
        self.assertEqual(self.company.riskmap_set.get().riskmapvalue_set.count(), 10,
                         "There should be exactly ten RiskMapValue records for Company")


class RiskMapTests(TestCase):
    """
    Various test for risk maps.
    """
    fixtures = ['riskmap.json', 'riskmapvalue.json']

    def test_if_template_risk_map_exists(self):
        """
        There should be exactly one template record
        """
        self.assertEqual(
            RiskMap.objects.filter(is_template=True, level=0, name="COSO").count(), 1,
            "There is not exactly one template risk map record"
        )

    def test_if_template_risk_map_values_exists(self):
        """
        There should be ten template records
        """
        self.assertEqual(
            RiskMapValue.objects.filter(risk_map__is_template=True).count(), 10,
            "There are not exactly ten template risk map records"
        )


class ImpactTests(TestCase):
    fixtures = ['riskmap.json', 'riskmapvalue.json']

    def test_empty_database_has_no_impacts(self):
        self.assertEqual(Impact.objects.count(), 0, "There should be no impacts in a new database")

    def test_impacts_are_created_when_company_is_create(self):
        company = Company.objects.create(name='ACME')
        self.assertEqual(company.impact_set.count(), 1, "Impacts should be created when a company is created")