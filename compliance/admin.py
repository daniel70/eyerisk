from django.contrib import admin
from .models import Document, Question, Selection, SelectionDocument


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'nr_of_questions')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('code', 'text', 'document')

admin.site.register(Document, DocumentAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Selection)
admin.site.register(SelectionDocument)

admin.site.site_title = "EyeRisk Administration"
admin.site.site_header = "EyeRisk Administration"