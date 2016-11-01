from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.conf import settings
from django.dispatch import receiver

class Company(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        verbose_name_plural = 'companies'


def company_created(sender, instance, created, **kwargs):
    """
    When a Company is created, the COSO risk map is copied into this company.
    This risk map consists of Likelihood and Risk tuples.
    The template records have an 'is_template' column that is True for templates.
    """
    if created:
        max_riskmap_id = RiskMap.objects.latest('riskmap_id').riskmap_id
        for rm in RiskMap.objects.filter(is_template=True):
            rm.pk = None
            rm.riskmap_id = max_riskmap_id + 1
            rm.company = instance
            rm.is_template = False
            rm.name = 'Enterprise'
            rm.level = 1 #Enterprise level
            rm.save()

post_save.connect(company_created, sender=Company)


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)


class Standard(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def nr_of_controls(self):
        return ControlActivity.objects.filter(controlpractice__controlprocess__controldomain__standard=self).count()

    class Meta:
        ordering = ['name']


class ControlDomain(models.Model):
    GOVERNANCE = 'G'
    MANAGEMENT = 'M'
    AREA_CHOICES = (
        (GOVERNANCE, 'Governance'),
        (MANAGEMENT, 'Management'),
    )
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE)
    ordering = models.IntegerField()
    area = models.CharField(max_length=1, choices=AREA_CHOICES, default=MANAGEMENT)
    domain = models.CharField(max_length=75, blank=True)

    def __str__(self):
        return self.domain

    class Meta:
        ordering = ['standard', 'ordering']


class ControlProcess(models.Model):
    controldomain = models.ForeignKey(ControlDomain, on_delete=models.CASCADE)
    ordering = models.IntegerField()
    process_id = models.CharField(max_length=15, blank=True)
    process_name = models.CharField(max_length=200, blank=True)
    process_description = models.TextField(blank=True)
    process_purpose = models.TextField(blank=True)

    def __str__(self):
        return '{0}. {1}'.format(self.process_id, self.process_name)

    class Meta:
        ordering = ['controldomain__standard', 'controldomain__ordering', 'ordering',]
        verbose_name_plural = 'Control processes'


class ControlPractice(models.Model):
    controlprocess = models.ForeignKey(ControlProcess, on_delete=models.CASCADE)
    ordering = models.IntegerField()
    practice_id = models.CharField(max_length=15, blank=True)
    practice_name = models.CharField(max_length=100, blank=True)
    practice_governance = models.TextField(blank=True) # code_text

    def __str__(self):
        return '{0}. {1}'.format(self.practice_id, self.practice_name)

    class Meta:
        ordering = ['controlprocess__controldomain__standard', 'controlprocess__controldomain__ordering',
                    'controlprocess__ordering', 'ordering']


class ControlActivity(models.Model):
    controlpractice = models.ForeignKey(ControlPractice, on_delete=models.CASCADE)
    ordering = models.IntegerField()
    activity_id = models.CharField(max_length=15)
    activity = models.TextField(blank=True)
    activity_help = models.TextField(blank=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.activity

    class Meta:
        ordering = ['controlpractice__controlprocess__controldomain__standard', 'controlpractice__controlprocess__controldomain__ordering',
                    'controlpractice__controlprocess__ordering', 'controlpractice__ordering', 'ordering']
        verbose_name_plural = 'Control activities'


class Selection(models.Model):
    name = models.CharField(max_length=30, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    standards = models.ManyToManyField(Standard, limit_choices_to={'is_active': True}, blank=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('selection-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['name']


def selection_changed(sender, **kwargs):
    """
    When a Standard is added or removed from a Selection, all of the Questions that belong to that
    Standard also need to be added or removed from the SelectionQuestion table.
    This functionality is not provided in class based views save() method (or save_m2m).
    However, a signal is fired every time this happens with a "pre_add" and a "post_add" action
    """
    action = kwargs.pop('action', None)
    instance = kwargs.pop('instance', None)
    pk_set = kwargs.pop('pk_set', None)
    if action == "pre_add":
        for pk in pk_set:
            selection_controls = []
            for control in ControlActivity.objects.filter(controlpractice__controlprocess__controldomain__standard=pk):
                selection_controls.append(SelectionControl(selection=instance, control=control, response='N'))

            SelectionControl.objects.bulk_create(selection_controls)

    if action == "pre_remove":
        SelectionControl.objects.filter(
            selection=instance, control__controlpractice__controlprocess__controldomain__standard__in=pk_set
        ).delete()

m2m_changed.connect(selection_changed, sender=Selection.standards.through)


class SelectionControl(models.Model):
    NOTHING = 'N'  # no choice has been made yet
    ACCEPT = 'A'
    MITIGATE = 'M'
    TRANSFER = 'T'
    AVOID = 'O'
    SELECTION_CHOICES = (
        (ACCEPT, 'Accept'),
        (MITIGATE, 'Mitigate'),
        (TRANSFER, 'Transfer'),
        (AVOID, 'Avoid'),
    )

    selection = models.ForeignKey(Selection, on_delete=models.CASCADE)
    control = models.ForeignKey(ControlActivity, on_delete=models.CASCADE)
    response = models.CharField(max_length=1, choices=SELECTION_CHOICES, default=ACCEPT)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('selection', 'control')


class RiskMap(models.Model):
    STRATEGIC = 'S'
    FINANCIAL = 'F'
    OPERATIONAL = 'O'
    COMPLIANCE = 'C'
    LEVEL_CHOICES = (
        (0, 'TEMPLATE'),
        (1, 'ENTERPRISE'),
        (2, 'RISK TYPE'),
        (3, 'RISK CATEGORY')
    )

    RISKTYPE_CHOICES = (
        (STRATEGIC, 'Strategic'),
        (FINANCIAL, 'Financial'),
        (OPERATIONAL, 'Operational'),
        (COMPLIANCE, 'Compliance'),
    )

    IMPACT = 'I'
    LIKELIHOOD = 'L'
    AXISTYPE_CHOICES = (
        (IMPACT, 'Impact'),
        (LIKELIHOOD, 'Likelihood'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    riskmap_id = models.IntegerField(auto_created=True)
    parent_id = models.IntegerField(blank=True, null=True)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    # parent_id = models.ForeignKey('self', to_field='riskmap_id', blank=True, null=True)
    risk_type = models.CharField(max_length=1, choices=RISKTYPE_CHOICES, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    axis_type = models.CharField(max_length=1, choices=AXISTYPE_CHOICES)
    position = models.IntegerField(validators=[MaxValueValidator(5)])
    rating = models.IntegerField(validators=[MinValueValidator(0)])
    descriptor = models.CharField(max_length=30)
    definition = models.TextField(blank=False)
    is_template = models.BooleanField(default=False)

    class Meta:
        unique_together = ('company', 'riskmap_id', 'risk_type', 'axis_type', 'position')
        ordering = ('company', 'risk_type', 'name', 'axis_type', 'position')

    def __str__(self):
        return self.name



class RiskType(models.Model):
    """
    As part of the Risk Scenario Category the customer needs to fill out some risk types
    They consist of a name and a choice between Primary of Secundary (menno fills this in).
    The customer will add a Risk Description to this when the form is filled out.
    """
    IMPACT_CHOICES = (
        ('N', 'N/A'),
        ('P', 'Primary'),
        ('S', 'Secondary'),
    )
    # scenario_category = models.ForeignKey(ScenarioCategory, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    impact = models.CharField(max_length=1, choices=IMPACT_CHOICES, default='N')


    def __str__(self):
        return '{} ({})'.format(self.description, self.impact)


class ScenarioCategory(models.Model):
    nr = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    risk_scenario = models.TextField(blank=True)
    risk_types = models.ManyToManyField(RiskType, blank=True)
    process_enabler = models.ManyToManyField(ControlPractice, through='ProcessEnabler')

    class Meta:
        ordering = ['nr']
        verbose_name_plural = 'scenario categories'

    def __str__(self):
        return self.name


@receiver(m2m_changed, sender=ScenarioCategory.risk_types.through)
def risk_types_changed(sender, **kwargs):
    """
    One or more risk_types have been added to (or removed from) a ScenarioCategory.
    All of the ScenarioCategoryAnswers that are linked to this ScenarioCategory need to have these new risk_types
    created as risk_type_answers so that the can be answered.
    """
    action = kwargs.pop('action', None)     # pre_add | post_add | pre_remove | post_remove
    instance = kwargs.pop('instance', None) # the instance of ScenarioCategory
    pk_set = kwargs.pop('pk_set', None)     # {1, 2, 3}
    reverse = kwargs.pop('reverse', None)   # boolean

    if action == "pre_add":
        risk_types = RiskType.objects.filter(pk__in=pk_set)
        for scenario_category_answer in ScenarioCategoryAnswer.objects.filter(scenario_category=instance):
            RiskTypeAnswer.objects.bulk_create(
                [RiskTypeAnswer(risk_type=risk_type, scenario_category_answer=scenario_category_answer)
                 for risk_type in risk_types])

    if action == "pre_remove":
        RiskTypeAnswer.objects.filter(risk_type__in=pk_set, scenario_category_answer__scenario_category=instance).delete()


class ScenarioCategoryAnswer(models.Model):
    threat_type_help = "The nature of the event"

    THREAT_TYPE_CHOICES = (
        (1, 'Malicious'),
        (2, 'Accidental'),
        (3, 'Error'),
        (4, 'Failure'),
        (5, 'Natural'),
        (6, 'External requirement'),
    )

    actor_help = """
    Who or what triggers the threat that exploits a vulnerability.
    """

    ACTOR_CHOICES = (
        (1, 'Internal'),
        (2, 'External'),
        (3, 'Human'),
        (4, 'Non-human'),
    )

    event_help = """
    Something happened that was not supposed to happen,
    something does not happen that was supposed to happen,
    or a change in circumstances.
    Events always have causes and usually have consequences.
    A consequence is the outcome of an event and has an impact on objectives.
    """

    EVENT_CHOICES = (
        (1, 'Disclosure'),
        (2, 'Interruption'),
        (3, 'Modification'),
        (4, 'Theft'),
        (5, 'Destruction'),
        (6, 'Ineffective design'),
        (7, 'Ineffective execution'),
        (8, 'Rules and regulations'),
        (9, 'Inappropriate use'),
    )

    asset_help = """
    An asset is something of either tangible or intangible value
    that is worth protecting, including people, systems,
    infrastructure, finances and reputation.
    """

    resource_help = """
    A resource is anything that helps to achieve a goal.
    """

    ASSET_RESOURCE_CHOICES = (
        (1, 'Process'),
        (2, 'People and Skills'),
        (3, 'Organizational Structure'),
        (4, 'Physical Infrastructure'),
        (5, 'IT Infrastructure'),
        (6, 'Information'),
        (7, 'Applications'),
    )

    TIMING_CHOICES = (
        (1, 'Non-Critical'),
        (2, 'Critical'),
    )

    DURATION_CHOICES = (
        (1, 'Short'),
        (2, 'Moderate'),
        (3, 'Extended'),
    )

    DETECTION_CHOICES = (
        (1, 'Slow'),
        (2, 'Moderate'),
        (3, 'Instant'),
    )

    TIME_LAG_CHOICES = (
        (1, 'Immediate'),
        (2, 'Delayed'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    scenario_category = models.ForeignKey(ScenarioCategory, on_delete=models.CASCADE)
    threat_type = models.CharField(max_length=100, help_text=threat_type_help, blank=True)
    actor = models.CharField(max_length=100, help_text=actor_help, blank=True)
    event = models.CharField(max_length=100, help_text=event_help, blank=True)
    asset = models.CharField(max_length=100, help_text=asset_help, blank=True)
    resource = models.CharField(max_length=100, help_text=resource_help, blank=True)
    timing = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    detection = models.CharField(max_length=100, blank=True)
    time_lag = models.CharField(max_length=100, blank=True)
    # risk_type_answer = models.ManyToManyField('RiskType', through='RiskTypeAnswer')
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} answers to {}".format(self.company, self.scenario_category)

class Scenario(models.Model):
    NOT_AVAILABLE = 'N/A'
    PRIMARY = 'P'
    SECONDARY = 'S'
    RISK_TYPE_CHOICES = (
        (NOT_AVAILABLE, 'Not Available'),
        (PRIMARY, 'Primary'),
        (SECONDARY, 'Secondary'),
    )
    reference = models.CharField(max_length=4, primary_key=True)
    category = models.ForeignKey(ScenarioCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    risk_scenario = models.TextField(blank=False)
    threat_type = models.TextField(blank=False)
    actor = models.TextField(blank=False)
    event = models.TextField(blank=False)
    cause = models.TextField(blank=False)
    effect = models.TextField(blank=False)
    time = models.TextField(blank=False)
    it_benefit = models.CharField(max_length=3, choices=RISK_TYPE_CHOICES, default=NOT_AVAILABLE)
    it_programme = models.CharField(max_length=3, choices=RISK_TYPE_CHOICES, default=NOT_AVAILABLE)
    it_operations = models.CharField(max_length=3, choices=RISK_TYPE_CHOICES, default=NOT_AVAILABLE)
    avoidance = models.TextField()
    acceptance = models.TextField()
    transfer = models.TextField()
    mitigation = models.TextField()
    negative = models.TextField(blank=True)
    positive = models.TextField(blank=True)
    # process_enabler = models.ManyToManyField(ControlPractice, through='ProcessEnabler')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['reference']


class Enabler(models.Model):
    ENABLER_CHOICES = (
        (1, 'Principles, Policies and Frameworks Enabler'),
        (2, 'Organisational Structures Enabler'),
        (3, 'Culture, Ethics and Behaviour Enabler'),
        (4, 'Information Enabler'),
        (5, 'Services, Infrastructure and Applications Enabler'),
        (6, 'People, Skills and Competencies Enabler'),
    )
    scenario_category = models.ForeignKey(ScenarioCategory, on_delete=models.CASCADE)
    type = models.IntegerField(choices=ENABLER_CHOICES)
    reference = models.CharField(max_length=50, blank=False)
    contribution_to_response = models.TextField()

    def __str__(self):
        return self.reference


class ProcessEnabler(models.Model):
    HIGH = 'H'
    MEDIUM = 'M'
    LOW = 'L'
    EFFECTS = (
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    )
    scenario_category = models.ForeignKey(ScenarioCategory, on_delete=models.CASCADE)
    practice = models.ForeignKey(ControlPractice, on_delete=models.CASCADE)
    # scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    # freq_effect = models.CharField(max_length=1, choices=EFFECTS, default=MEDIUM)
    # impact_effect = models.CharField(max_length=1, choices=EFFECTS, default=MEDIUM)
    # is_essential_control = models.BooleanField(default=True)

# class ScenarioComponent(models.Model):
#     group = models.CharField()


class RiskTypeAnswer(models.Model):
    """
    This model is used for its extra fields on many-to-many relationships.
    https://docs.djangoproject.com/en/dev/topics/db/models/#extra-fields-on-many-to-many-relationships
    """
    risk_type = models.ForeignKey(RiskType, on_delete=models.CASCADE)
    scenario_category_answer = models.ForeignKey(ScenarioCategoryAnswer, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('risk_type', 'scenario_category_answer')

    def __str__(self):
        return '{} - {}'.format(self.risk_type, self.scenario_category_answer)
