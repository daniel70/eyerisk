from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from modeltranslation.admin import TabbedTranslationAdmin

from .forms import ScenarioCategoryForm, ScenarioCategoryAnswerAdminForm

from .models import Standard, ControlDomain, ControlPractice, ControlProcess, ControlActivity,\
    Selection, Employee, Company, Scenario, ScenarioCategory, Enabler, RiskType, \
    ScenarioCategoryAnswer, RiskTypeAnswer, ProcessEnablerAnswer, EnablerAnswer, Project, RiskMap, RiskMapValue, \
    Software, Department, Process


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


class EnablerInline(admin.TabularInline):
    model = Enabler
    extra = 1


class ScenarioCategoryAdmin(admin.ModelAdmin):
    form = ScenarioCategoryForm
    list_display = ('nr', 'name')
    inlines = (EnablerInline,)


class RiskTypeAnswerInline(admin.TabularInline):
    model = RiskTypeAnswer
    extra = 0
    can_delete = False


class ProcessEnablerAnswerInline(admin.TabularInline):
    model = ProcessEnablerAnswer
    extra = 0
    can_delete = False


class EnablerAnswerInline(admin.TabularInline):
    model = EnablerAnswer
    extra = 0
    can_delete = False


class ScenarioCategoryAnswerAdmin(admin.ModelAdmin):
    form = ScenarioCategoryAnswerAdminForm
    list_display = ('__str__', 'project', 'created', 'updated')
    # exclude = ('risk_type_answer',)
    inlines = (RiskTypeAnswerInline, ProcessEnablerAnswerInline, EnablerAnswerInline)


class ScenarioAdmin(admin.ModelAdmin):
    # inlines = (ProcessEnablerInline,)
    list_display = ('reference', 'title')


class RiskMapValueInline(admin.TabularInline):
    model = RiskMapValue
    extra = 0
    can_delete = False


class RiskMapAdmin(admin.ModelAdmin):
    model = RiskMap
    list_display = ('__str__', 'company', 'level', 'risk_type')
    list_filter = (
        ('is_template', admin.BooleanFieldListFilter),
        ('company', admin.RelatedOnlyFieldListFilter),
    )
    inlines = (RiskMapValueInline,)


class SoftwareAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'company')
    list_filter = (
        ('company', admin.RelatedOnlyFieldListFilter),
    )


class SoftwareInline(admin.TabularInline):
    model = Software
    can_delete = True
    extra = 1


class ProcessAdmin(admin.ModelAdmin):
    model = Process
    list_display = ('__str__', 'department',)
    list_filter = (
        ('department', admin.RelatedOnlyFieldListFilter),
    )


class ProcessInline(admin.TabularInline):
    model = Process
    can_delete = True
    extra = 1


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'company')
    list_filter = (
        ('company', admin.RelatedOnlyFieldListFilter),
    )
    inlines = (ProcessInline,)


class DepartmentInline(admin.TabularInline):
    model = Department
    can_delete = True
    extra = 1


class CompanyAdmin(admin.ModelAdmin):
    model = Company
    inlines = (DepartmentInline, SoftwareInline)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Company, CompanyAdmin)
admin.site.register(Software, SoftwareAdmin)
admin.site.register(Project)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Process, ProcessAdmin)
admin.site.register(Standard, StandardAdmin)
admin.site.register(ControlDomain, ControlDomainAdmin)
admin.site.register(ControlProcess, ControlProcessAdmin)
admin.site.register(ControlPractice, ControlPracticeAdmin)
admin.site.register(ControlActivity, ControlActivityAdmin)
admin.site.register(Selection)
admin.site.register(ScenarioCategory, ScenarioCategoryAdmin)
admin.site.register(ScenarioCategoryAnswer, ScenarioCategoryAnswerAdmin)
admin.site.register(Scenario, ScenarioAdmin)

admin.site.register(RiskMap, RiskMapAdmin)


#no need to clutter the admin with these inlines
admin.site.register(Enabler)
admin.site.register(EnablerAnswer)
admin.site.register(RiskType)
admin.site.register(RiskTypeAnswer)
admin.site.register(ProcessEnablerAnswer)

admin.site.site_title = "EYERISK Administration"
admin.site.site_header = "EYERISK Administration"
