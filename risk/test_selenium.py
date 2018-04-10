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

        # create a project
        self.selenium.get(self.live_server_url + '/admin/risk/project/add/')
        name = self.selenium.find_element_by_name('name')
        name.send_keys('Action')
        type = Select(self.selenium.find_element_by_name('type'))
        type.select_by_index(1)
        company = Select(self.selenium.find_element_by_name('company'))
        company.select_by_index(1)

        self.selenium.find_element_by_name('_save').click()

        # add software
        self.selenium.get(self.live_server_url + '/admin/risk/software/add/')
        company = Select(self.selenium.find_element_by_name('company'))
        company.select_by_index(1)
        name = self.selenium.find_element_by_name('name')
        name.send_keys('EYErisk')
        description = self.selenium.find_element_by_name('description')
        description.send_keys('Software for risk management')
        self.selenium.find_element_by_name('is_saas').click()

        self.selenium.find_element_by_name('_save').click()

        # create a selection
        self.selenium.get(self.live_server_url + '/admin/risk/selection/add/')
        name = self.selenium.find_element_by_name('name')
        name.send_keys('Selenium test')
        company = Select(self.selenium.find_element_by_name('company'))
        company.select_by_index(1)
        standard = Select(self.selenium.find_element_by_name('standards'))
        standard.select_by_visible_text('Cobit 5')

        self.selenium.find_element_by_name('_save').click()

        # create a process
        self.selenium.get(self.live_server_url + '/admin/risk/process/add/')
        department = Select(self.selenium.find_element_by_name('department'))
        department.select_by_index(1)
        name = self.selenium.find_element_by_name('name')
        name.send_keys('abc')
        owner = self.selenium.find_element_by_name('owner')
        owner.send_keys('Daniel')
        scope = self.selenium.find_element_by_name('scope')
        scope.send_keys('abc')

        self.selenium.find_element_by_name('_save').click()

        # create a risk type
        self.selenium.get(self.live_server_url + '/admin/risk/risktype/add/')
        description = self.selenium.find_element_by_name('description')
        description.send_keys('IT program and project delivery')
        impact = Select(self.selenium.find_element_by_name('impact'))
        impact.select_by_index(1)

        self.selenium.find_element_by_name('_save').click()

        # create control domain
        self.selenium.get(self.live_server_url + '/admin/risk/controldomain/add/')
        standard = Select(self.selenium.find_element_by_name('standard'))
        standard.select_by_visible_text('Cobit 5')
        ordering = self.selenium.find_element_by_name('ordering')
        ordering.send_keys('1')
        area = Select(self.selenium.find_element_by_name('area'))
        area.select_by_index(0)
        domain = self.selenium.find_element_by_name('domain_en')
        domain.send_keys('Security')

        self.selenium.find_element_by_name('_save').click()

        # create a control process
        self.selenium.get(self.live_server_url + '/admin/risk/controlprocess/add/')
        controldomain = Select(self.selenium.find_element_by_name('controldomain'))
        controldomain.select_by_index(1)
        ordering = self.selenium.find_element_by_name('ordering')
        ordering.send_keys('1')
        id = self.selenium.find_element_by_name('process_id')
        id.send_keys('TEST01')
        name = self.selenium.find_element_by_name('process_name_en')
        name.send_keys('Selenium test')
        description = self.selenium.find_element_by_name('process_description_en')
        description.send_keys('Process description')
        purpose = self.selenium.find_element_by_name('process_purpose_en')
        purpose.send_keys('Process purpose')

        self.selenium.find_element_by_name('_save').click()

        # create a control practice
        self.selenium.get(self.live_server_url + '/admin/risk/controlpractice/add/')
        process = Select(self.selenium.find_element_by_name('controlprocess'))
        process.select_by_index(1)
        ordering = self.selenium.find_element_by_name('ordering')
        ordering.send_keys('1')
        id = self.selenium.find_element_by_name('practice_id')
        id.send_keys('TEST01')
        name = self.selenium.find_element_by_name('practice_name_en')
        name.send_keys('Selenium test')
        governance = self.selenium.find_element_by_name('practice_governance_en')
        governance.send_keys('Practice governance')

        self.selenium.find_element_by_name('_save').click()

        # create a control activity
        self.selenium.get(self.live_server_url + '/admin/risk/controlactivity/add/')
        practice = Select(self.selenium.find_element_by_name('controlpractice'))
        practice.select_by_index(1)
        ordering = self.selenium.find_element_by_name('ordering')
        ordering.send_keys('1')
        id = self.selenium.find_element_by_name('activity_id')
        id.send_keys('1')
        activity = self.selenium.find_element_by_name('activity_en')
        activity.send_keys('Control activity')
        help = self.selenium.find_element_by_name('activity_help_en')
        help.send_keys('Control activity help text')

        self.selenium.find_element_by_name('_save').click()

        # create a scenario category
        self.selenium.get(self.live_server_url + '/admin/risk/scenariocategory/add/')
        nr = self.selenium.find_element_by_name('nr')
        nr.send_keys('01')
        name = self.selenium.find_element_by_name('name')
        name.send_keys('Selenium test')
        scenario = self.selenium.find_element_by_name('risk_scenario')
        scenario.send_keys('Risk scenario')
        type = Select(self.selenium.find_element_by_name('risk_types'))
        type.select_by_value('1')
        process_enabler = Select(self.selenium.find_element_by_name('process_enablers'))
        process_enabler.select_by_value('1')
        enabler = Select(self.selenium.find_element_by_name('enabler_set-0-type'))
        enabler.select_by_index(2)
        reference = self.selenium.find_element_by_name('enabler_set-0-reference')
        reference.send_keys('Reference 1')
        ctr = self.selenium.find_element_by_name('enabler_set-0-contribution_to_response')
        ctr.send_keys('Contribution to response 1')
        self.selenium.find_element_by_link_text('Add another Enabler').click()
        enabler2 = Select(self.selenium.find_element_by_name('enabler_set-1-type'))
        enabler2.select_by_index(3)
        reference2 = self.selenium.find_element_by_name('enabler_set-1-reference')
        reference2.send_keys('Reference 2')
        ctr2 = self.selenium.find_element_by_name('enabler_set-1-contribution_to_response')
        ctr2.send_keys('Contribution to response 2')

        self.selenium.find_element_by_name('_save').click()

        # create a scenario category answer
        self.selenium.get(self.live_server_url + '/admin/risk/scenariocategoryanswer/add/')
        project = Select(self.selenium.find_element_by_name('project'))
        project.select_by_value('2')
        sc = Select(self.selenium.find_element_by_name('scenario_category'))
        sc.select_by_index(1)
        self.selenium.find_element_by_id('id_threat_type_2').click()
        self.selenium.find_element_by_id('id_actor_1').click()
        self.selenium.find_element_by_id('id_event_7').click()
        self.selenium.find_element_by_id('id_asset_3').click()
        self.selenium.find_element_by_id('id_resource_4').click()
        self.selenium.find_element_by_id('id_timing_0').click()
        self.selenium.find_element_by_id('id_duration_1').click()
        self.selenium.find_element_by_id('id_detection_2').click()
        self.selenium.find_element_by_id('id_time_lag_1').click()
        self.selenium.find_element_by_id('id_gross_frequency_1').click()
        self.selenium.find_element_by_id('id_gross_impact_1').click()

        self.selenium.find_element_by_name('_save').click()

        # create an enabler
        self.selenium.get(self.live_server_url + '/admin/risk/enabler/add/')
        sc = Select(self.selenium.find_element_by_name('scenario_category'))
        sc.select_by_index(1)
        type = Select(self.selenium.find_element_by_name('type'))
        type.select_by_index(3)
        ref = self.selenium.find_element_by_name('reference')
        ref.send_keys('Reference')
        ctr = self.selenium.find_element_by_name('contribution_to_response')
        ctr.send_keys('Contribution to response')

        self.selenium.find_element_by_name('_save').click()

        # Create an enabler answer
        self.selenium.get(self.live_server_url + '/admin/risk/enableranswer/add/')
        enabler = Select(self.selenium.find_element_by_name('enabler'))
        enabler.select_by_index(3)
        sca = Select(self.selenium.find_element_by_name('scenario_category_answer'))
        sca.select_by_index(1)
        frequency = Select(self.selenium.find_element_by_name('effect_on_frequency'))
        frequency.select_by_value('H')
        impact = Select(self.selenium.find_element_by_name('effect_on_impact'))
        impact.select_by_value('M')
        essential = Select(self.selenium.find_element_by_name('essential_control'))
        essential.select_by_value('Y')
        percentage = self.selenium.find_element_by_name('percentage_complete')
        percentage.send_keys('23')

        self.selenium.find_element_by_name('_save').click()

        # Create an impact
        self.selenium.get(self.live_server_url + '/admin/risk/impact/add/')
        company = Select(self.selenium.find_element_by_name('company'))
        company.select_by_index(1)
        cia = Select(self.selenium.find_element_by_name('cia_type'))
        cia.select_by_index(3)
        level = Select(self.selenium.find_element_by_name('level'))
        level.select_by_index(2)
        description = self.selenium.find_element_by_name('description')
        description.send_keys('Test impact')

        self.selenium.find_element_by_name('_save').click()

        # Create a practice RACI
        self.selenium.get(self.live_server_url + '/admin/risk/controlpracticeraci/add/')
        cp = Select(self.selenium.find_element_by_name('controlpractice'))
        cp.select_by_index(1)

        self.selenium.find_element_by_name('_save').click()

        # Create a process enabler answer
        self.selenium.get(self.live_server_url + '/admin/risk/processenableranswer/add/')
        cp = Select(self.selenium.find_element_by_name('control_practice'))
        cp.select_by_index(1)
        sca = Select(self.selenium.find_element_by_name('scenario_category_answer'))
        sca.select_by_index(1)
        frequency = Select(self.selenium.find_element_by_name('effect_on_frequency'))
        frequency.select_by_value('H')
        impact = Select(self.selenium.find_element_by_name('effect_on_impact'))
        impact.select_by_value('M')
        essential = Select(self.selenium.find_element_by_name('essential_control'))
        essential.select_by_value('Y')
        percentage = self.selenium.find_element_by_name('percentage_complete')
        percentage.send_keys('5')

        self.selenium.find_element_by_name('_save').click()

        # Add a register TODO: doesn't work, no risk owner?
        # self.selenium.get(self.live_server_url + '/admin/risk/register/add/')
        # rs = self.selenium.find_element_by_name('risk_statement')
        # rs.send_keys('Test 2018')
        # owner = Select(self.selenium.find_element_by_name('risk_owner'))
        # owner.select_by_index(1)
        # last = self.selenium.find_element_by_name('last_assessment')
        # last.send_keys('2018-03-19')
        # next = self.selenium.find_element_by_name('next_assessment')
        # next.send_keys('2018-04-20')
        # category = Select(self.selenium.find_element_by_name('risk_category'))
        # category.select_by_index(2)
        # classification = Select(self.selenium.find_element_by_name('risk_classification'))
        # classification.select_by_index(3)
        # response = Select(self.selenium.find_element_by_name('risk_response'))
        # response.select_by_index(1)
        #
        # self.selenium.find_element_by_name('_save').click()
        # time.sleep(5)

        # Create a risk type answer
        self.selenium.get(self.live_server_url + '/admin/risk/risktypeanswer/add/')
        type = Select(self.selenium.find_element_by_name('risk_type'))
        type.select_by_index(1)
        sca = Select(self.selenium.find_element_by_name('scenario_category_answer'))
        sca.select_by_index(1)
        description = self.selenium.find_element_by_name('description')
        description.send_keys('Test answer')

        self.selenium.find_element_by_name('_save').click()

        # Create a scenario
        self.selenium.get(self.live_server_url + '/admin/risk/scenario/add/')
        ref = self.selenium.find_element_by_name('reference')
        ref.send_keys('Test')
        category = Select(self.selenium.find_element_by_name('category'))
        category.select_by_index(1)
        title = self.selenium.find_element_by_name('title')
        title.send_keys('Test title')
        scenario = self.selenium.find_element_by_name('risk_scenario')
        scenario.send_keys('Test scenario')
        tt = self.selenium.find_element_by_name('threat_type')
        tt.send_keys('Test threat type')
        actor = self.selenium.find_element_by_name('actor')
        actor.send_keys('Test actor')
        event = self.selenium.find_element_by_name('event')
        event.send_keys('Test event')
        cause = self.selenium.find_element_by_name('cause')
        cause.send_keys('Test cause')
        effect = self.selenium.find_element_by_name('effect')
        effect.send_keys('Test effect')
        time = self.selenium.find_element_by_name('time')
        time.send_keys('Test time')
        benefit = Select(self.selenium.find_element_by_name('it_benefit'))
        benefit.select_by_index(1)
        programme = Select(self.selenium.find_element_by_name('it_programme'))
        programme.select_by_index(1)
        operations = Select(self.selenium.find_element_by_name('it_operations'))
        operations.select_by_index(1)
        avoidance = self.selenium.find_element_by_name('avoidance')
        avoidance.send_keys('Test avoidance')
        acceptance = self.selenium.find_element_by_name('acceptance')
        acceptance.send_keys('Test acceptance')
        transfer = self.selenium.find_element_by_name('transfer')
        transfer.send_keys('Test transfer')
        mitigation = self.selenium.find_element_by_name('mitigation')
        mitigation.send_keys('Test mitigation')

        self.selenium.find_element_by_name('_save').click()