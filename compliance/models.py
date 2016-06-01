from django.core.urlresolvers import reverse
from django.db import models


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
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('selection-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['name']


class SelectionDocument(models.Model):
    selection = models.ForeignKey(Selection, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} : {}".format(self.selection, self.document)

    class Meta:
        unique_together = ('selection', 'document')


class SelectionQuestion(models.Model):
    ACCEPT = 'A'
    MITIGATE = 'M'
    TRANSFER = 'T'
    SELECTION_CHOICES = (
        (ACCEPT, 'Accept'),
        (MITIGATE, 'Mitigate'),
        (TRANSFER, 'Transfer'),
    )

    selection = models.ForeignKey(Selection, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    decision = models.CharField(max_length=1, choices=SELECTION_CHOICES, default=ACCEPT)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('selection', 'question')
