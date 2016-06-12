from django.contrib import admin
from .models import Standard, Control, Question, Selection


class StandardAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'nr_of_questions')


class ControlAdmin(admin.ModelAdmin):
    list_display = ('practice_id', 'activity', 'standard')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('code', 'text', 'standard')

admin.site.register(Standard, StandardAdmin)
admin.site.register(Control, ControlAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Selection)

admin.site.site_title = "EYE Risk Administration"
admin.site.site_header = "EYE Risk Administration"