from django.test import TestCase

from .models import Company, RiskMap, RiskMapValue


class SimpleTest(TestCase):
    def test_no_access_as_anonymous(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)


class CompanyTests(TestCase):
    """
    When a company is created then a risk map called 'ENTERPRISE' shoud also be created as well as 10 risk map values.
    """
    fixtures = ['riskmap.json', 'riskmapvalue.json']

    def setUp(self):
        Company.objects.create(name='ACME')

    def test_if_company_exists(self):
        self.assertTrue(RiskMap.objects.filter(company__name='ACME').exists())

    def test_if_risk_map_is_created_when_company_is_created(self):
        self.assertEqual(RiskMap.objects.get(company__name='ACME').name, 'ENTERPRISE')

    def test_if_ten_risk_map_values_are_created_when_company_is_created(self):
        risk_map = RiskMap.objects.get(company__name='ACME')
        self.assertEqual(risk_map.riskmapvalue_set.all().count(), 10)


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
