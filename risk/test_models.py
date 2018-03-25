from django.test import TestCase
from .models import Company, RiskMap, Impact, RiskMapValue, Standard, ControlDomain, ControlProcess, ControlPractice, \
    ControlActivity, Selection, Scenario, Project, ScenarioCategory, ScenarioCategoryAnswer


class CompanyModelTests(TestCase):
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
        self.assertEqual(self.company.riskmap_set.count(), 1, 'There should be exactly one risk map for Company')

    def test_if_ten_risk_map_values_are_created_when_company_is_created(self):
        risk_map = RiskMap.objects.get(company__name='ACME')
        self.assertEqual(risk_map.values.all().count(), 10)
        self.assertEqual(self.company.riskmap_set.get().values.count(), 10,
                         'There should be exactly ten RiskMapValue records for Company')

    def test_that_a_default_project_is_created_when_a_company_is_created(self):
        self.assertEqual(self.company.project_set.count(), 1)
        self.assertEqual(self.company.project_set.get().name, 'Default')

    def test_impacts_are_created_when_company_is_created(self):
        self.assertEqual(self.company.impact_set.count(), 1, 'Impact should be created when a company is created')


class RiskMapModelTests(TestCase):
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
            'There is not exactly one template risk map record'
        )

    def test_if_template_risk_map_values_exists(self):
        """
        There should be ten template records
        """
        self.assertEqual(
            RiskMapValue.objects.filter(risk_map__is_template=True).count(), 10,
            "There are not exactly ten template risk map records"
        )


class ImpactModelTests(TestCase):
    def test_empty_database_has_no_impacts(self):
        self.assertEqual(Impact.objects.count(), 0, "There should be no impacts in a new database")


class ActivityModelTests(TestCase):
    fixtures = ['riskmap.json', 'riskmapvalue.json']

    def test_empty_database_has_no_standards(self):
        self.assertEqual(Standard.objects.count(), 0)

    def test_activity(self):
        standard = Standard.objects.create(name='Cobit 5', is_active=True)
        self.assertTrue(Standard.objects.filter(name='Cobit 5').exists())

        domain = ControlDomain.objects.create(ordering=1, area=ControlDomain.MANAGEMENT,
                                              domain='Align, Plan and Organise',
                                              domain_en='Align, Plan and Organise',
                                              standard=standard
                                              )
        self.assertTrue(ControlDomain.objects.filter(domain__startswith='Align').exists())

        process = ControlProcess.objects.create(ordering=1,
                                                process_id='XXX',
                                                process_name='This is the name of the process',
                                                process_name_en='This is the name of the process',
                                                process_description='This is the process description',
                                                process_description_en='This is the English process description',
                                                process_purpose='What is the purpose of the process',
                                                process_purpose_en='What is the English purpose of the process',
                                                controldomain=domain
                                                )
        self.assertTrue(ControlProcess.objects.filter(process_id='XXX').exists())

        practice = ControlPractice.objects.create(ordering=1,
                                                  practice_id='XXX.XX',
                                                  practice_name='This is the name of the practice',
                                                  practice_name_en='This is the English name of the practice',
                                                  practice_governance='This is the governance of the practice',
                                                  practice_governance_en='This is the English governance of the practice',
                                                  controlprocess=process
                                                  )
        self.assertTrue(ControlPractice.objects.filter(practice_id='XXX.XX').exists())

        activity = ControlActivity.objects.create(ordering=1,
                                                  activity_id=1,
                                                  activity='This is the activity',
                                                  activity_en='This is the English activity',
                                                  activity_help='This is the help of the activity',
                                                  activity_help_en='This is the English help of the activity',
                                                  controlpractice=practice
                                                  )
        self.assertTrue(ControlActivity.objects.filter(activity_id=1).exists())

        irisk = Company.objects.create(name='iRiskIT')
        single = Company.objects.create(name='Single Source')

        selection = Selection.objects.create(name='Test Selection', company=irisk)
        self.assertTrue(Selection.objects.filter(name='Test Selection').exists())


class ScenarioModelTests(TestCase):
    fixtures = ['riskmap.json', 'riskmapvalue.json']

    def test_there_are_no_scenarios(self):
        self.assertEqual(Scenario.objects.count(), 0)

    def test_scenariocategory(self):
        company_irisk = Company.objects.create(name='iRiskIT')
        Company.objects.create(name='Single Source')
        project_irisk = Project.objects.get(company=company_irisk, name='Default', type=Project.PERIODIC)
        self.assertEqual(ScenarioCategory.objects.count(), 0)
        scenario_category = ScenarioCategory.objects.create(nr='15', name='Malware', risk_scenario='Description goes here')
        self.assertEqual(ScenarioCategory.objects.count(), 1)
        scenario_category_answer = ScenarioCategoryAnswer.objects.create(scenario_category=scenario_category,
                                                                         project=project_irisk,
                                                                         threat_type='1,2,3')
        self.assertEqual(ScenarioCategoryAnswer.objects.count(), 1)
