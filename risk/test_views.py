from django.contrib.auth.models import User
from django.test import TestCase

from risk.forms import SelectionForm, RiskMapValueFormSet
from risk.models import Company, Standard

password = 'sup3rd1ff1cult'


class SelectionViewTests(TestCase):

    def test_selection_form_without_standard_is_invalid(self):
        form = SelectionForm(data={'name': 'TestSelection', 'standards': None})
        self.assertFalse(form.is_valid(), 'At least one Standard must be filled in.')

    def test_selection_form_with_standard_is_valid(self):
        cobit = Standard.objects.create(name='Cobit 5', is_active=True)
        iso = Standard.objects.create(name='ISO 270001:2013', is_active=True)

        form = SelectionForm(data={'name': 'TestSelection', 'standards': [cobit]})
        self.assertTrue(form.is_valid(), form.errors)

        form = SelectionForm(data={'name': 'TestSelection', 'standards': [cobit, iso]})
        self.assertTrue(form.is_valid(), form.errors)


class RiskMapViewTests(TestCase):
    fixtures = ['riskmap.json', 'riskmapvalue.json']

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name='ACME')

    # an unbound form is always invalid, use POST to check the validity
    # def test_that_the_default_form_is_valid(self):
    #     riskmap = self.company.riskmap_set.get(level=1, is_template=False)
    #     form = RiskMapValueFormSet(queryset=riskmap.values.all())
    #     self.assertTrue(form.is_valid(), form.errors)