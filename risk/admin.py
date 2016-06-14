from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Standard, Control, Selection, Impact, Likelyhood, RiskMap


class StandardAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'nr_of_controls')


class ControlAdmin(TabbedTranslationAdmin):
    list_display = ('practice_id', 'activity', 'standard')
    list_filter = (
        ('standard', admin.RelatedOnlyFieldListFilter),
    )


class ImpactAdmin(admin.ModelAdmin):
    list_display = ('rating', 'descriptor')


class LikelyhoodAdmin(admin.ModelAdmin):
    list_display = ('rating', 'descriptor')

admin.site.register(Standard, StandardAdmin)
admin.site.register(Control, ControlAdmin)
admin.site.register(Selection)
admin.site.register(RiskMap)
admin.site.register(Impact, ImpactAdmin)
admin.site.register(Likelyhood, LikelyhoodAdmin)

admin.site.site_title = "EYE Risk Administration"
admin.site.site_header = "EYE Risk Administration"
