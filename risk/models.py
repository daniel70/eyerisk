from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import m2m_changed
from django.core.validators import MaxValueValidator, MinValueValidator

class Standard(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def nr_of_controls(self):
        return Control.objects.filter(standard=self).count()

    class Meta:
        ordering = ['name']


class Control(models.Model):
    GOVERNANCE = 'G'
    MANAGEMENT = 'M'
    AREA_CHOICES = (
        (GOVERNANCE, 'Governance'),
        (MANAGEMENT, 'Management'),
    )
    ordering = models.IntegerField()
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE)
    area = models.CharField(max_length=1, choices=AREA_CHOICES, default=MANAGEMENT)
    domain = models.CharField(max_length=75, blank=True)
    process_id = models.CharField(max_length=15, blank=True)
    process_name = models.CharField(max_length=200, blank=True)
    process_description = models.TextField(blank=True)
    process_purpose = models.TextField(blank=True)
    practice_id = models.CharField(max_length=15, blank=True)
    practice_name = models.CharField(max_length=100, blank=True)
    practice_governance  = models.TextField(blank=True) # code_text
    activity_id = models.CharField(max_length=15)
    activity = models.TextField(blank=True)
    activity_help = models.TextField(blank=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.activity_id

    class Meta:
        ordering = ['standard', 'ordering']


class Selection(models.Model):
    name = models.CharField(max_length=30, unique=True)
    standards = models.ManyToManyField(Standard, limit_choices_to={'is_active': True}, blank=True)
    # questions = also M2M???
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
            for control in Control.objects.filter(standard=pk):
                selection_controls.append(SelectionControl(selection=instance, control=control, response='A'))

            SelectionControl.objects.bulk_create(selection_controls)

    if action == "pre_remove":
        SelectionControl.objects.filter(selection=instance, control__standard__in=pk_set).delete()

m2m_changed.connect(selection_changed, sender=Selection.standards.through)


class SelectionControl(models.Model):
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
    control = models.ForeignKey(Control, on_delete=models.CASCADE)
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
    rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(0)])
    descriptor = models.CharField(max_length=30, unique=True)
    definition = models.TextField(blank=False)

    def __str__(self):
        return self.descriptor

    class Meta:
        ordering = ['rating']


class Likelyhood(models.Model):
    riskmap = models.ForeignKey(RiskMap, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(0)])
    descriptor = models.CharField(max_length=30, unique=True)
    definition = models.TextField(blank=False)

    def __str__(self):
        return self.descriptor

    class Meta:
        ordering = ['rating']

