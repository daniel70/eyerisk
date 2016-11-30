from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, CheckboxSelectMultiple, RadioSelect, modelformset_factory, \
    MultipleChoiceField, inlineformset_factory, BaseInlineFormSet, SelectMultiple, HiddenInput
from django.forms.models import BaseModelFormSet
from django.utils.translation import ugettext_lazy as _

from .models import Selection, ControlSelection, ScenarioCategory, ScenarioCategoryAnswer, RiskTypeAnswer, RiskType, \
    Project, RiskMap, RiskMapValue


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
            'timing': CheckboxSelectMultiple(choices=ScenarioCategoryAnswer.TIMING_CHOICES),
            'duration': CheckboxSelectMultiple(choices=ScenarioCategoryAnswer.DURATION_CHOICES),
            'detection': CheckboxSelectMultiple(choices=ScenarioCategoryAnswer.DETECTION_CHOICES),
            'time_lag': CheckboxSelectMultiple(choices=ScenarioCategoryAnswer.TIME_LAG_CHOICES),
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
        fields = ('name', 'parent_id')
        widgets = {'parent_id': HiddenInput()}


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
