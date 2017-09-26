from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.db.models.signals import m2m_changed, post_save, post_delete
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from random import randint


def select_avatar_color():
    """Select a random color for a users avator"""
    avatar_colors = [
        "#f44336",
        "#e91e63",
        "#9c27b0",
        "#673ab7",
        "#3f51b5",
        "#2196f3",
        "#03a9f4",
        "#00bcd4",
        "#009688",
        "#4caf50",
        "#8bc34a",
        "#cddc39",
        "#ffeb3b",
        "#ffc107",
        "#ff9800",
        "#ff5722",
        "#795548",
        "#9e9e9e",
        "#607d8b",
    ]
    return avatar_colors[randint(0, len(avatar_colors)-1)]


def shortener(number: int) -> str:
    """Return a short version of a large number. 1_000_000 -> 1M"""
    for scale in ['', 'K', 'M', 'G']:
        if abs(number) < 1000:
            return "%i%s" % (number, scale)
        number /= 1000
    return "%iT" % (number)


class Company(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        verbose_name_plural = 'companies'


@receiver(signal=post_save, sender=Company)
def company_created(sender, instance, created, **kwargs):
    """
    When a Company is created, the COSO risk map is copied into this company.
    This risk map consists of Likelihood and Risk tuples.
    The template record has a 'is_template' column that is True for templates.
    """
    if created:
        t = RiskMap.objects.get(is_template=True)
        if t is None:
            # no risk map template defined!
            # log error
            return

        # before making changes to the RiskMap, first get its Values
        rmv_list = list(RiskMapValue.objects.filter(risk_map=t))
        t.parent_id = t.pk
        t.pk = None
        t.company = instance
        t.is_template = False
        t.name = 'ENTERPRISE'
        t.level = 1  # Enterprise level
        t.save()

        # create the CIA Impacts
        Impact.objects.create(company=instance, cia_type='C', level=1, description='Low direct and indirect costs < € 1m')


class Software(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_saas = models.BooleanField('Is SAAS', default=False)

    class Meta:
        verbose_name_plural = 'Software'
        unique_together = ('company', 'name')
        ordering = ('name', )

    def __str__(self):
        return self.name


class Department(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    manager = models.CharField(max_length=50)
    software = models.ManyToManyField(Software, blank=True)

    class Meta:
        unique_together = ('company', 'name')
        ordering = ('company', 'name')

    def __str__(self):
        return self.name


class Process(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    owner = models.CharField(max_length=50)
    scope = models.TextField()

    class Meta:
        verbose_name_plural = 'Processes'

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name() or self.user.get_username()


class Project(models.Model):
    """
    A project acts as a container for Scenario's bla bla
    """
    PERIODIC = 'Q'
    PROJECT = 'P'
    CHANGE = 'C'
    PROJECT_TYPE_CHOICES = (
        (PERIODIC, 'Company'),
        (PROJECT, 'Project'),
        (CHANGE, 'Change'),
    )
    name = models.CharField(max_length=30, blank=False)
    type = models.CharField(max_length=1, blank=False, choices=PROJECT_TYPE_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'company')

    def __str__(self):
        return self.name


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
        return '{0} - {1}'.format(self.process_id, self.process_name)

    class Meta:
        ordering = ['controldomain__standard', 'controldomain__ordering', 'ordering']
        verbose_name_plural = 'Control processes'

    @property
    def has_raci(self):
        """
        Does this process have a raci model attached?
        This is only for Cobit practices.
        """
        return self.controlpractice_set.filter(controlpracticeraci__isnull=False).exists()


class ControlPractice(models.Model):
    controlprocess = models.ForeignKey(ControlProcess, on_delete=models.CASCADE)
    ordering = models.IntegerField()
    practice_id = models.CharField(max_length=15, blank=True)
    practice_name = models.CharField(max_length=100, blank=True)
    practice_governance = models.TextField(blank=True)  # code_text

    def __str__(self):
        return '{0} - {1}'.format(self.practice_id, self.practice_name)

    class Meta:
        ordering = ['controlprocess__controldomain__standard',
                    'controlprocess__controldomain__ordering',
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
        ordering = ['controlpractice__controlprocess__controldomain__standard',
                    'controlpractice__controlprocess__controldomain__ordering',
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


@receiver(m2m_changed, sender=Selection.standards.through)
def selection_changed(sender, **kwargs):
    """
    When a Standard is added or removed from a Selection, all of the Questions that belong to that
    Standard also need to be added or removed from the SelectionQuestion table.
    This functionality is not provided in class based views save() method (or save_m2m).
    However, a signal is fired every time this happens with a "pre_add" and a "post_add" action
    """
    action = kwargs.pop('action', None)
    instance = kwargs.pop('instance', None)
    pk_set = kwargs.pop('pk_set', [])
    if action == "pre_add":
        for pk in pk_set:
            selection_controls = []
            for control in ControlActivity.objects.filter(controlpractice__controlprocess__controldomain__standard=pk):
                selection_controls.append(ControlSelection(selection=instance, control=control, response='N'))

            ControlSelection.objects.bulk_create(selection_controls)

    if action == "pre_remove":
        ControlSelection.objects.filter(
            selection=instance, control__controlpractice__controlprocess__controldomain__standard__in=pk_set
        ).delete()


class ControlSelection(models.Model):
    NOTHING = 'N'  # no choice has been made yet
    ACCEPT = 'A'
    MITIGATE = 'M'
    TRANSFER = 'T'
    AVOID = 'O'
    SELECTION_CHOICES = (
        (NOTHING, 'No selection'),
        (ACCEPT, 'Accept'),
        (MITIGATE, 'Mitigate'),
        (TRANSFER, 'Transfer'),
        (AVOID, 'Avoid'),
    )

    selection = models.ForeignKey(Selection, on_delete=models.CASCADE)
    control = models.ForeignKey(ControlActivity, on_delete=models.CASCADE)
    response = models.CharField(max_length=1, choices=SELECTION_CHOICES, default=NOTHING)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('selection', 'control')


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
    """
    These are the 20 standard Cobit scenarios plus any company specific scenarios
    """
    nr = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    risk_scenario = models.TextField(blank=True)
    risk_types = models.ManyToManyField(RiskType, blank=True)
    process_enablers = models.ManyToManyField(ControlPractice, blank=True)

    class Meta:
        ordering = ['nr']
        verbose_name_plural = 'scenario categories'

    def __str__(self):
        return "{} - {}".format(self.nr, self.name)


@receiver(m2m_changed, sender=ScenarioCategory.risk_types.through)
def risk_types_changed(sender, **kwargs):
    """
    One or more risk_types have been added to (or removed from) a ScenarioCategory.
    All of the ScenarioCategoryAnswers that are linked to this ScenarioCategory need to have these new risk_types
    created as RiskTypeAnswer so that they can be answered.
    """
    action = kwargs.pop('action', None)         # pre_add | post_add | pre_remove | post_remove
    instance = kwargs.pop('instance', None)     # the instance of ScenarioCategory
    pk_set = kwargs.pop('pk_set', None)         # {1, 2, 3}
    reverse = kwargs.pop('reverse', None)       # boolean

    if action == "pre_add":
        risk_types = RiskType.objects.filter(pk__in=pk_set)
        for scenario_category_answer in ScenarioCategoryAnswer.objects.filter(scenario_category=instance):
            RiskTypeAnswer.objects.bulk_create(
                [RiskTypeAnswer(risk_type=risk_type, scenario_category_answer=scenario_category_answer)
                 for risk_type in risk_types])

    if action == "pre_remove":
        RiskTypeAnswer.objects.filter(risk_type__in=pk_set, scenario_category_answer__scenario_category=instance).delete()


@receiver(m2m_changed, sender=ScenarioCategory.process_enablers.through)
def process_enablers_changed(sender, **kwargs):
    """
    One or more process_enablers have been added to (or removed from) a ScenarioCategory.
    All of the ScenarioCategoryAnswers that are linked to this ScenarioCategory need to have these new process enablers
    created as ProcessEnablerAnswer so that they can be answered.
    """

    action = kwargs.pop('action', None)         # pre_add | post_add | pre_remove | post_remove
    instance = kwargs.pop('instance', None)     # the instance of ScenarioCategory
    pk_set = kwargs.pop('pk_set', None)         # {1, 2, 3}
    reverse = kwargs.pop('reverse', None)       # boolean

    if action == "pre_add":
        process_enablers = ControlPractice.objects.filter(pk__in=pk_set)
        for scenario_category_answer in ScenarioCategoryAnswer.objects.filter(scenario_category=instance):
            ProcessEnablerAnswer.objects.bulk_create(
                [ProcessEnablerAnswer(control_practice=process_enabler, scenario_category_answer=scenario_category_answer)
                 for process_enabler in process_enablers])

    if action == "pre_remove":
        ProcessEnablerAnswer.objects.filter(control_practice__in=pk_set, scenario_category_answer__scenario_category=instance).delete()


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

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # name = models.CharField(max_length=50)
    # company = models.ForeignKey(Company, on_delete=models.CASCADE)
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
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['project', 'scenario_category']

    def __str__(self):
        return "{}".format(self.project)


@receiver(post_save, sender=ScenarioCategoryAnswer)
def scenario_category_answer_saved(sender, **kwargs):
    """
    create an EnablerAnswer from this Enabler and save it to all ScenarioCategoryAnswers that point to the
    scenario_category that this Enabler points to.
    """
    instance = kwargs.pop('instance', None)
    created = kwargs.pop('created', None)
    raw = kwargs.pop('raw', None)
    using = kwargs.pop('using', None)
    update_fields = kwargs.pop('update_fields', None)

    if created:
        sc = instance.scenario_category
        # get the risk types
        risk_types = []
        for risk_type in sc.risk_types.all():
            risk_types.append(RiskTypeAnswer(risk_type=risk_type, scenario_category_answer=instance))

        process_enablers = []
        for process_enabler in sc.process_enablers.all():
            process_enablers.append(ProcessEnablerAnswer(control_practice=process_enabler, scenario_category_answer=instance))

        enablers = []
        for enabler in sc.enabler_set.all():
            enablers.append(EnablerAnswer(enabler=enabler, scenario_category_answer=instance))

        with transaction.atomic():
            RiskTypeAnswer.objects.bulk_create(risk_types)
            ProcessEnablerAnswer.objects.bulk_create(process_enablers)
            EnablerAnswer.objects.bulk_create(enablers)


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
    """
    Enablers are questions on Scenario Category Forms.
    They have a reference and a contribution to response (text).
    As with process enablers, the response is effect on frequency, impact and essential control.
    The difference with process enablers and risk types is that those are many-to-many relationships,
    while these are created as foreign-key relationships.
    Each scenario category has its own specific enablers and they are copied to the scenario category answers
    when they are created.
    """
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
    reference = models.CharField(max_length=150, blank=False)
    contribution_to_response = models.TextField()

    def __str__(self):
        return self.reference


@receiver(post_save, sender=Enabler)
def enabler_saved(sender, **kwargs):
    """
    create an EnablerAnswer from this Enabler and save it to all ScenarioCategoryAnswers that point to the
    scenario_category that this Enabler points to.
    """
    instance = kwargs.pop('instance', None)
    created = kwargs.pop('created', None)
    raw = kwargs.pop('raw', None)
    using = kwargs.pop('using', None)
    update_fields = kwargs.pop('update_fields', None)

    if created:
        for scenario_category_answer in ScenarioCategoryAnswer.objects.filter(scenario_category=instance.scenario_category):
            EnablerAnswer.objects.create(enabler=instance, scenario_category_answer=scenario_category_answer)


class EnablerAnswer(models.Model):
    HIGH = 'H'
    MEDIUM = 'M'
    LOW = 'L'
    EFFECTS = (
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    )
    enabler = models.ForeignKey(Enabler, on_delete=models.CASCADE)
    scenario_category_answer = models.ForeignKey(ScenarioCategoryAnswer, on_delete=models.CASCADE)
    effect_on_frequency = models.CharField(max_length=1, choices=EFFECTS, blank=True)
    effect_on_impact = models.CharField(max_length=1, choices=EFFECTS, blank=True)
    essential_control = models.CharField(max_length=1, choices=[('Y', 'Y'), ('N', 'N')], blank=True)
    percentage_complete = models.IntegerField('% complete', default=0,
                                              validators=(MinValueValidator(0), MaxValueValidator(100)))
    class Meta:
        unique_together = ('enabler', 'scenario_category_answer')

    def __str__(self):
        return '{} - {}'.format(self.enabler, self.scenario_category_answer)


class ProcessEnablerAnswer(models.Model):
    HIGH = 'H'
    MEDIUM = 'M'
    LOW = 'L'
    EFFECTS = (
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    )
    control_practice = models.ForeignKey(ControlPractice, on_delete=models.CASCADE)
    scenario_category_answer = models.ForeignKey(ScenarioCategoryAnswer, on_delete=models.CASCADE)
    effect_on_frequency = models.CharField(max_length=1, choices=EFFECTS, blank=True)
    effect_on_impact = models.CharField(max_length=1, choices=EFFECTS, blank=True)
    essential_control = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], blank=True)
    percentage_complete = models.IntegerField('% complete', default=0,
                                              validators=(MinValueValidator(0), MaxValueValidator(100)))

    class Meta:
        unique_together = ('control_practice', 'scenario_category_answer')

    def __str__(self):
        return '{} - {}'.format(self.control_practice, self.scenario_category_answer)


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


class RiskMap(models.Model):
    """
    A new risk map is automatically created for each new company when the company is created (company_created).
    That is the Enterprise risk type.
    """
    LEVEL_CHOICES = (
        (0, 'TEMPLATE'),
        (1, 'ENTERPRISE'),
        (2, 'RISK TYPE'),
        (3, 'RISK CATEGORY'),
    )

    STRATEGIC = 'S'
    FINANCIAL = 'F'
    OPERATIONAL = 'O'
    COMPLIANCE = 'C'
    RISK_TYPE_CHOICES = (
        (STRATEGIC, 'STRATEGIC'),
        (FINANCIAL, 'FINANCIAL'),
        (OPERATIONAL, 'OPERATIONAL'),
        (COMPLIANCE, 'COMPLIANCE'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=50)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    parent = models.ForeignKey('self', to_field='id', blank=True, null=True, on_delete=models.CASCADE)
    risk_type = models.CharField(max_length=1, choices=RISK_TYPE_CHOICES, blank=True, null=True)
    is_template = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'name')
        ordering = ('name',)

    def __str__(self):
        return self.name


@receiver(signal=post_save, sender=RiskMap)
def risk_map_created(sender, instance, created, **kwargs):
    """
    When a RiskMap is created we automatically create the RiskMapValues.
    """
    if created and instance.is_template is False:
        parent = RiskMap.objects.get(pk=instance.parent_id)
        for rmv in RiskMapValue.objects.filter(risk_map=parent):
            rmv.pk = None
            rmv.risk_map = instance
            rmv.save()


class RiskMapValue(models.Model):
    IMPACT = 'I'
    LIKELIHOOD = 'L'
    AXIS_TYPE_CHOICES = (
        (IMPACT, 'Impact'),
        (LIKELIHOOD, 'Likelihood'),
    )

    risk_map = models.ForeignKey(RiskMap, related_name='values', on_delete=models.CASCADE)
    axis_type = models.CharField(max_length=1, choices=AXIS_TYPE_CHOICES)
    position = models.IntegerField(validators=[MaxValueValidator(5)])
    rating = models.IntegerField(validators=[MinValueValidator(0)])
    descriptor = models.CharField(max_length=30)
    definition = models.TextField(blank=False)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('risk_map', 'axis_type', 'position')
        ordering = ('risk_map', 'axis_type', 'position')

    def __str__(self):
        return "{} ({}, {})".format(self.risk_map.name, self.get_axis_type_display(), self.position)

    def clean(self):
        """
        Each higher position on the same risk map and same axis, should have a higher rating than the previous.
        (this has moved to the modelformset validation because this check needs to take place before the form is saved)
        """
    #     if self.position > 1:
    #         if RiskMapValue.objects.get(risk_map=self.risk_map, axis_type=self.axis_type, position=self.position-1)\
    #                 .rating >= self.rating:
    #             raise ValidationError({'rating': 'Rating can not be lower than or equal to previous rating.'})

        """Check that rating of type L is between 1 and 100"""
        if self.axis_type == "L" and (self.rating < 1 or self.rating > 100):
            raise ValidationError({'rating': _('Rating of likelihood must be between 1 and 100')})

    def short_rating(self):
        if self.position == 1:
            pre = "< "
        elif self.position == 5:
            pre = "> "
        else:
            previous = RiskMapValue.objects.get(risk_map=self.risk_map, axis_type=self.axis_type,
                                                   position=self.position-1)

            pre = "€{} - ".format(shortener(previous.rating)) if self.axis_type == "I" else "{}% - ".format(previous.rating)

        short = shortener(self.rating)
        val = "{}€{}".format(pre, short) if self.axis_type == "I" else "{}{}%".format(pre, short)
        return val

    # def short_rating(self):
    #     sign = ">" if self.position == 5 else "<"
    #     short = shortener(self.rating)
    #     val = "{} € {}".format(sign, short) if self.axis_type == "I" else "{} {}%".format(sign, short)
    #     return val
    #


class Impact(models.Model):
    CIA_TYPE_CHOICES = (
        ('C', _('Confidentiality')),
        ('I', _('Integrity')),
        ('A', _('Availability')),
    )

    IMPACT_LEVEL_CHOICES = (
        (1, _('Very Low')),
        (2, _('Low')),
        (3, _('Medium')),
        (4, _('High')),
        (5, _('Very High')),
    )

    company = models.ForeignKey(to=Company, on_delete=models.CASCADE)
    cia_type = models.CharField(max_length=1, choices=CIA_TYPE_CHOICES)
    level = models.IntegerField(choices=IMPACT_LEVEL_CHOICES)
    description = models.CharField(max_length=300)

    class Meta:
        unique_together = ('company', 'cia_type', 'level')
        ordering = ('company', 'cia_type', 'level')

    def __str__(self):
        return self.description


class Register(models.Model):
    RISK_CATEGORY_CHOICES = (
        ('S', _('Strategic')),
        ('D', _('Project Delivery')),
        ('O', _('Operational')),
    )

    RISK_CLASSIFICATION_CHOICES = (
        (2, _('Low')),
        (3, _('Medium')),
        (4, _('High')),
        (5, _('Very High')),
    )

    ACCEPT = 'A'
    MITIGATE = 'M'
    TRANSFER = 'T'
    AVOID = 'O'
    RISK_RESPONSE_CHOICES = (
        (ACCEPT, _('Accept')),
        (MITIGATE, _('Mitigate')),
        (TRANSFER, _('Transfer')),
        (AVOID, _('Avoid')),
    )

    risk_statement = models.CharField(max_length=150, blank=True)
    risk_owner = models.ForeignKey(to=Employee, on_delete=models.CASCADE)
    last_assessment = models.DateField(_('Date of last risk assessment'))
    next_assessment = models.DateField(_('Due date for update of risk assessment'))
    risk_category = models.CharField(max_length=1, choices=RISK_CATEGORY_CHOICES, blank=False, default='')
    risk_classification = models.IntegerField(choices=RISK_CLASSIFICATION_CHOICES, blank=False, default=0)
    risk_response = models.CharField(max_length=1, choices=RISK_RESPONSE_CHOICES, blank=False, default='A')


class ControlPracticeRACI(models.Model):
    RACI_CHOICES = (
        ('', _('No choice')),
        ('R', _('Responsible')),
        ('A', _('Accountable')),
        ('C', _('Consulted')),
        ('I', _('Informed')),
    )

    controlpractice = models.OneToOneField(ControlPractice, on_delete=models.CASCADE, primary_key=True)
    board = models.CharField(_('Board'), max_length=1, blank=True, choices=RACI_CHOICES)
    chief_executive_officer = models.CharField(_('Chief Executive Officer'), max_length=1, blank=True, choices=RACI_CHOICES)
    chief_financial_officer = models.CharField(_('Chief Financial Officer'), max_length=1, blank=True, choices=RACI_CHOICES)
    chief_operating_officer = models.CharField(_('Chief Operating Officer'), max_length=1, blank=True, choices=RACI_CHOICES)
    business_executives = models.CharField(_('Business Executives'), max_length=1, blank=True, choices=RACI_CHOICES)
    business_process_owners = models.CharField(_('Business Process Owners'), max_length=1, blank=True, choices=RACI_CHOICES)
    strategy_executive_committee = models.CharField(_('Strategy Executive Committee'), max_length=1, blank=True, choices=RACI_CHOICES)
    steering_committee = models.CharField(_('Steering Committee'), max_length=1, blank=True, choices=RACI_CHOICES)
    project_management_office = models.CharField(_('Project Management Office'), max_length=1, blank=True, choices=RACI_CHOICES)
    value_management_office = models.CharField(_('Value Management Office'), max_length=1, blank=True, choices=RACI_CHOICES)
    chief_risk_officer = models.CharField(_('Chief Risk Officer'), max_length=1, blank=True, choices=RACI_CHOICES)
    chief_information_security_officer = models.CharField(_('Chief Information Security Officer'), max_length=1, blank=True, choices=RACI_CHOICES)
    architecture_board = models.CharField(_('Architecture Board'), max_length=1, blank=True, choices=RACI_CHOICES)
    enterprice_risk_committee = models.CharField(_('Enterprice Risk Committee'), max_length=1, blank=True, choices=RACI_CHOICES)
    head_human_resources = models.CharField(_('Head Human Resources'), max_length=1, blank=True, choices=RACI_CHOICES)
    compliance = models.CharField(_('Compliance'), max_length=1, blank=True, choices=RACI_CHOICES)
    audit = models.CharField(_('Audit'), max_length=1, blank=True, choices=RACI_CHOICES)
    chief_information_officer = models.CharField(_('Chief Information Officer'), max_length=1, blank=True, choices=RACI_CHOICES)
    head_architect = models.CharField(_('Head Architect'), max_length=1, blank=True, choices=RACI_CHOICES)
    head_development = models.CharField(_('Head Development'), max_length=1, blank=True, choices=RACI_CHOICES)
    head_it_operations = models.CharField(_('Head IT Operations'), max_length=1, blank=True, choices=RACI_CHOICES)
    head_it_administration = models.CharField(_('Head IT Administration'), max_length=1, blank=True, choices=RACI_CHOICES)
    service_manager = models.CharField(_('Service Manager'), max_length=1, blank=True, choices=RACI_CHOICES)
    information_security_manager = models.CharField(_('Information Security Manager'), max_length=1, blank=True, choices=RACI_CHOICES)
    business_continuity_manager = models.CharField(_('Business Continuity Manager'), max_length=1, blank=True, choices=RACI_CHOICES)
    privacy_officer = models.CharField(_('Privacy Officer'), max_length=1, blank=True, choices=RACI_CHOICES)

    def __str__(self):
        return "RACI: {}".format(self.controlpractice.practice_id)

    class Meta:
        verbose_name_plural = 'Practice RACIs'
