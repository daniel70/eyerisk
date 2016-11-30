from django.test import TestCase

from .models import Company, RiskMap, RiskMapValue

# riskmap voorbeeld toevoegen bij het aanmaken/wijzigen van risk maps

# impact 4 van een risk map mag niet lager zijn dan impact 3 etc.

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
