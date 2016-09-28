from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from modeltranslation.admin import TabbedTranslationAdmin
from .models import Standard, ControlDomain, ControlPractice, ControlProcess, ControlActivity,\
    Selection, Impact, Likelihood, RiskMap, Employee, Company, Scenario, ScenarioCategory


class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = True


class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline, )


class StandardAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'nr_of_controls')


class ControlDomainAdmin(TabbedTranslationAdmin):
    list_display = ('domain', 'area', 'standard')
    list_filter = (
        ('standard', admin.RelatedOnlyFieldListFilter),
    )


class ControlProcessAdmin(TabbedTranslationAdmin):
    list_display = ('process_id', 'process_name', 'get_domain', 'get_standard')

    def get_domain(self, obj):
        return obj.controldomain.domain
    get_domain.short_description = 'Domain'
    get_domain.admin_order_field = 'controldomain__domain'

    def get_standard(self, obj):
        return obj.controldomain.standard
    get_standard.short_description = 'Standard'
    get_standard.admin_order_field = 'controldomain__standard'

    # list_filter = (
    #     ('standard', admin.RelatedOnlyFieldListFilter),
    # )


class ControlPracticeAdmin(TabbedTranslationAdmin):
    list_display = ('practice_id', 'practice_name', 'get_process', 'get_domain', 'get_standard')

    def get_process(self, obj):
        return obj.controlprocess.process_id
    get_process.short_description = 'Process'
    get_process.admin_order_field = 'controlprocess__process_id'

    def get_domain(self, obj):
        return obj.controlprocess.controldomain.domain
    get_domain.short_description = 'Domain'
    get_domain.admin_order_field = 'controlprocess__controldomain__domain'

    def get_standard(self, obj):
        return obj.controlprocess.controldomain.standard
    get_standard.short_description = 'Standard'
    get_standard.admin_order_field = 'controlprocess__controldomain__standard'

    # list_filter = (
    #     ('standard', admin.RelatedOnlyFieldListFilter),
    # )


class ControlActivityAdmin(TabbedTranslationAdmin):
    list_display = ('activity_id', 'activity')
    # list_filter = (
    #     ('standard', admin.RelatedOnlyFieldListFilter),
    # )


class ImpactAdmin(admin.ModelAdmin):
    list_display = ('rating', 'descriptor')


class LikelihoodAdmin(admin.ModelAdmin):
    list_display = ('rating', 'descriptor')


class ScenarioCategoryAdmin(admin.ModelAdmin):
    list_display = ('nr', 'name')

class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('reference', 'title')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Company)
admin.site.register(Standard, StandardAdmin)
admin.site.register(ControlDomain, ControlDomainAdmin)
admin.site.register(ControlProcess, ControlProcessAdmin)
admin.site.register(ControlPractice, ControlPracticeAdmin)
admin.site.register(ControlActivity, ControlActivityAdmin)
admin.site.register(Selection)
admin.site.register(RiskMap)
admin.site.register(Impact, ImpactAdmin)
admin.site.register(Likelihood, LikelihoodAdmin)
admin.site.register(ScenarioCategory, ScenarioCategoryAdmin)
admin.site.register(Scenario, ScenarioAdmin)

admin.site.site_title = "EYERISK Administration"
admin.site.site_header = "EYERISK Administration"
