from django.contrib import admin
from .models import Document, Control, Question, Selection


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'nr_of_questions')


class ControlAdmin(admin.ModelAdmin):
    list_display = ('practice_id', 'activity', 'document')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('code', 'text', 'document')

admin.site.register(Document, DocumentAdmin)
admin.site.register(Control, ControlAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Selection)

admin.site.site_title = "EYE Risk Administration"
admin.site.site_header = "EYE Risk Administration"