from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import m2m_changed
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.conf import settings


class Company(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        verbose_name_plural = 'companies'


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
        return self.process_name

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
        return self.practice_name

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
    name = models.CharField(max_length=30, unique=True)
    is_template = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Impact(models.Model):
    riskmap = models.ForeignKey(RiskMap, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MaxValueValidator(settings.EYERISK['MAXIMUM_IMPACTS']),
                                             MinValueValidator(settings.EYERISK['MINIMUM_IMPACTS'])])
    descriptor = models.CharField(max_length=30)
    definition = models.TextField(blank=False)

    def __str__(self):
        return self.descriptor

    class Meta:
        unique_together = ('riskmap', 'descriptor')
        ordering = ['rating']


class Likelihood(models.Model):
    riskmap = models.ForeignKey(RiskMap, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MaxValueValidator(settings.EYERISK['MAXIMUM_LIKELIHOOD']),
                                             MinValueValidator(settings.EYERISK['MINIMUM_LIKELIHOOD'])])
    max_value = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    descriptor = models.CharField(max_length=30)
    definition = models.TextField(blank=False)

    def __str__(self):
        return self.descriptor

    class Meta:
        unique_together = ('riskmap', 'descriptor')
        ordering = ['rating']


class ScenarioCategory(models.Model):
    nr = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['nr']
        verbose_name_plural = 'scenario categories'


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

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['reference']
