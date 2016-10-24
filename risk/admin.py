from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from modeltranslation.admin import TabbedTranslationAdmin

# from risk.forms import ScenarioCategoryForm
from .models import Standard, ControlDomain, ControlPractice, ControlProcess, ControlActivity,\
    Selection, Employee, Company, Scenario, ScenarioCategory, RiskMap, ProcessEnabler, Enabler, RiskType


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


class RiskTypeInline(admin.TabularInline):
    model = RiskType
    extra = 1


class EnablerInline(admin.TabularInline):
    model = Enabler
    extra = 1


class ProcessEnablerInline(admin.TabularInline):
    model = ProcessEnabler
    extra = 1


class ScenarioCategoryAdmin(admin.ModelAdmin):
    # form = ScenarioCategoryForm
    list_display = ('nr', 'name')
    inlines = (RiskTypeInline, EnablerInline, ProcessEnablerInline)


class ScenarioAdmin(admin.ModelAdmin):
    # inlines = (ProcessEnablerInline,)
    list_display = ('reference', 'title')


class RiskMapAdmin(admin.ModelAdmin):
    list_display = ('company', 'riskmap_id', 'name', 'risk_type', 'axis_type', 'position', 'descriptor', 'is_template')
    list_filter = (
        ('is_template', admin.BooleanFieldListFilter),
        ('company', admin.RelatedOnlyFieldListFilter),
    )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Company)
admin.site.register(RiskMap, RiskMapAdmin)
admin.site.register(Standard, StandardAdmin)
admin.site.register(ControlDomain, ControlDomainAdmin)
admin.site.register(ControlProcess, ControlProcessAdmin)
admin.site.register(ControlPractice, ControlPracticeAdmin)
admin.site.register(ControlActivity, ControlActivityAdmin)
admin.site.register(Selection)
admin.site.register(ScenarioCategory, ScenarioCategoryAdmin)
admin.site.register(Scenario, ScenarioAdmin)

admin.site.site_title = "EYERISK Administration"
admin.site.site_header = "EYERISK Administration"
