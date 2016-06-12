from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import m2m_changed


class Standard(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def nr_of_questions(self):
        return Question.objects.filter(standard=self).count()

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
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, blank=True, null=True)
    area = models.CharField(max_length=1, choices=AREA_CHOICES, default=MANAGEMENT)
    domain = models.CharField(max_length=75)
    process_id = models.CharField(max_length=15)
    process_name = models.CharField(max_length=200, blank=True)
    process_description = models.CharField(max_length=200, blank=True)
    process_purpose = models.CharField(max_length=200, blank=True)
    practice_id = models.CharField(max_length=15) # code
    practice_name = models.CharField(max_length=100) # code_text
    practice_governance  = models.CharField(max_length=200, blank=True) # code_text
    activity_id = models.CharField(max_length=15, blank=True) # code, blank=True should be removed
    activity = models.TextField() # text
    activity_help = models.TextField
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.activity_id

    class Meta:
        ordering = ['standard', 'ordering']


class Question(models.Model):
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE)
    ordering = models.IntegerField()
    code = models.CharField(max_length=15)
    code_text = models.TextField()
    text = models.TextField()
    description = models.TextField()
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

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
            selectionquestions = []
            for question in Question.objects.filter(standard=pk):
                selectionquestions.append(SelectionQuestion(selection=instance, question=question, response='A'))

            SelectionQuestion.objects.bulk_create(selectionquestions)

    if action == "pre_remove":
        SelectionQuestion.objects.filter(selection=instance, question__standard__in=pk_set).delete()

m2m_changed.connect(selection_changed, sender=Selection.standards.through)


class SelectionQuestion(models.Model):
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
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.CharField(max_length=1, choices=SELECTION_CHOICES, default=ACCEPT)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('selection', 'question')
