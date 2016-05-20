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
        return self.text

    class Meta:
        ordering = ['document', 'ordering']