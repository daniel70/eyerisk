from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import m2m_changed


class Document(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def nr_of_questions(self):
        return Question.objects.filter(document=self).count()

    class Meta:
        ordering = ['name']


class Control(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    ordering = models.IntegerField()
    area = models.CharField(max_length=25)
    domain = models.CharField(max_length=75)
    process_id = models.CharField(max_length=15)
    process = models.CharField(max_length=200)
    practice_id = models.CharField(max_length=15) # code
    practice_name = models.CharField(max_length=100) # code_text
    activity = models.TextField() # text
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    class Meta:
        ordering = ['document', 'ordering']


class Question(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
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
        ordering = ['document', 'ordering']


class Selection(models.Model):
    name = models.CharField(max_length=30, unique=True)
    documents = models.ManyToManyField(Document, limit_choices_to={'is_active': True}, blank=True)
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
    When a Document is added or removed from a Selection, all of the Questions that belong to that
    Document also need to be added or removed from the SelectionQuestion table.
    This functionality is not provided in class based views save() method (or save_m2m).
    However, a signal is fired every time this happens with a "pre_add" and a "post_add" action
    """
    action = kwargs.pop('action', None)
    instance = kwargs.pop('instance', None)
    pk_set = kwargs.pop('pk_set', None)
    if action == "pre_add":
        for pk in pk_set:
            selectionquestions = []
            for question in Question.objects.filter(document=pk):
                selectionquestions.append(SelectionQuestion(selection=instance, question=question, response='A'))

            SelectionQuestion.objects.bulk_create(selectionquestions)

    if action == "pre_remove":
        SelectionQuestion.objects.filter(selection=instance, question__document__in=pk_set).delete()

m2m_changed.connect(selection_changed, sender=Selection.documents.through)


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
