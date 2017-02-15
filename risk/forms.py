from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, CheckboxSelectMultiple, RadioSelect, modelformset_factory, \
    MultipleChoiceField, inlineformset_factory, BaseInlineFormSet, SelectMultiple, HiddenInput, CharField
from django.forms.models import BaseModelFormSet, ModelChoiceField
from django.utils.translation import ugettext_lazy as _

from risk.models import Company
from .models import Selection, ControlSelection, ScenarioCategory, ScenarioCategoryAnswer, RiskTypeAnswer, RiskType, \
    Project, RiskMap, RiskMapValue, Department, Software, Impact


class SelectionForm(ModelForm):
    class Meta:
        model = Selection
        fields = ('name', 'standards')
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'standards': CheckboxSelectMultiple(),
        }


class ScenarioCategoryForm(ModelForm):
    """
    We want a larger selectmultiple box for process enablers.
    """
    class Meta:
        model = ScenarioCategory
        fields = ('nr', 'name', 'risk_scenario', 'risk_types', 'process_enablers')
        widgets = {
            'process_enablers': SelectMultiple(attrs={'size': 12, 'style': 'min-height:300px'})
        }


class ScenarioCategoryAnswerForm(ModelForm):
    class Meta:
        model = ScenarioCategoryAnswer
        fields = ('threat_type', 'actor', 'event', 'asset', 'resource', 'timing', 'duration', 'detection', 'time_lag')
        widgets = {
            'threat_type': CheckboxSelectMultiple(choices=ScenarioCategoryAnswer.THREAT_TYPE_CHOICES),
            'actor': CheckboxSelectMultiple(choices=ScenarioCategoryAnswer.ACTOR_CHOICES),
            'event': CheckboxSelectMultiple(choices=ScenarioCategoryAnswer.EVENT_CHOICES),
            'asset': CheckboxSelectMultiple(choices=ScenarioCategoryAnswer.ASSET_RESOURCE_CHOICES),
            'resource': CheckboxSelectMultiple(choices=ScenarioCategoryAnswer.ASSET_RESOURCE_CHOICES),
            'timing': RadioSelect(choices=ScenarioCategoryAnswer.TIMING_CHOICES),
            'duration': RadioSelect(choices=ScenarioCategoryAnswer.DURATION_CHOICES),
            'detection': RadioSelect(choices=ScenarioCategoryAnswer.DETECTION_CHOICES),
            'time_lag': RadioSelect(choices=ScenarioCategoryAnswer.TIME_LAG_CHOICES),
        }


class ScenarioCategoryAnswerAdminForm(ScenarioCategoryAnswerForm):
    """
    Only difference with the 'normal' form is that we show a few extra fields in admin.
    Note the trick to override Meta class. Nice.
    """
    class Meta(ScenarioCategoryAnswerForm.Meta):
        fields = ('project', 'scenario_category') + ScenarioCategoryAnswerForm.Meta.fields


class ScenarioCategoryAnswerCreateForm(ModelForm):
    """
    This form is used to create a new ScenarioCategoryAnswer.
    After the form is created the risk types, and enablers are copied over from the ScenarioCategory.
    """
    def __init__(self, company, *args, **kwargs):
        super(ScenarioCategoryAnswerCreateForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(company=company)

    class Meta:
        model = ScenarioCategoryAnswer
        fields = ('project', 'scenario_category')


class RiskMapCategoryCreateForm(ModelForm):
    """
    When a new RiskMap of type CATEGORY is created we only need a name and a parent_id.
    """
    class Meta:
        model = RiskMap
        fields = ('name', 'parent')
        widgets = {'parent': HiddenInput()}


class RiskMapValueForm(ModelForm):
    class Meta:
        model = RiskMapValue
        fields = ('rating', 'descriptor', 'definition')


class BaseRiskMapValueFormSet(BaseModelFormSet):
    """Override BaseModelFormSet for use in RiskMapValueFormSet in order to be able to check if the form is valid"""
    def clean(self):
        if any(self.errors):
            return
        x_rating, y_rating = 0, 0
        for form in self.forms:
            """Check that a higher position on the same axis also has a higher rating"""
            if form.instance.axis_type == 'I':
                if form.cleaned_data['rating'] <= x_rating:
                    form.add_error('rating', ValidationError(_('Rating cannot be lower than a previous rating')))
                else:
                    x_rating = form.cleaned_data['rating']

            if form.instance.axis_type == 'L':
                if form.cleaned_data['rating'] <= y_rating:
                    form.add_error('rating', ValidationError(_('Rating cannot be lower than a previous rating')))
                else:
                    y_rating = form.cleaned_data['rating']


RiskMapValueFormSet = modelformset_factory(RiskMapValue, form=RiskMapValueForm, formset=BaseRiskMapValueFormSet, extra=0)


class DepartmentAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        """If there is a software field then filter the list to only show software for this company"""
        super(DepartmentAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance and 'software' in self.fields:
            self.fields['software'].queryset = Software.objects.filter(company=instance.company)

    class Meta:
        model = Department
        fields = '__all__'


class DepartmentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        """If there is a software field then filter the list to only show software for this company"""
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance and 'software' in self.fields:
            self.fields['software'].queryset = Software.objects.filter(company=instance.company)

    class Meta:
        model = Department
        fields = ['name', 'manager', 'software']
        widgets = {'software': CheckboxSelectMultiple()}


class SoftwareForm(ModelForm):
    class Meta:
        model = Software
        fields = ['name', 'description', 'is_saas']


ImpactDescriptionFormSet = modelformset_factory(model=Impact, fields=('id', 'description',), extra=0)

# class ImpactChangeForm(ModelForm):
#     """
#     Only used to change the description of an Impact.
#     """
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         """Only allow the description to be changed, cia_type and level are readonly"""
#         self.fields['cia_type'].disabled = True
#         self.fields['level'].disabled = True
#
#     class Meta:
#         model = Impact
#         fields = ('cia_type', 'level', 'description')
#
# ImpactChangeFormSet = modelformset_factory(Impact, ImpactChangeForm, extra=0)


class UserSettingsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True
        self.fields['username'].help_text = ''
        self.fields['last_login'].disabled = True
        self.fields['date_joined'].disabled = True
        self.fields['is_staff'].disabled = True
        self.fields['is_staff'].help_text = ''
        self.fields['is_superuser'].disabled = True
        self.fields['is_superuser'].help_text = ''

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined', 'is_staff', 'is_superuser')


class CompanySettingsForm(ModelForm):
    class Meta:
        model = Company
        fields = ('name',)
