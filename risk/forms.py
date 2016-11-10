from django.forms import ModelForm, TextInput, CheckboxSelectMultiple, RadioSelect, modelformset_factory, \
    MultipleChoiceField, inlineformset_factory, BaseInlineFormSet, SelectMultiple
from .models import Selection, ControlSelection, ScenarioCategory, ScenarioCategoryAnswer, RiskTypeAnswer, RiskType


class SelectionForm(ModelForm):
    class Meta:
        model = Selection
        fields = ('name', 'standards')
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'standards': CheckboxSelectMultiple(),
        }


class SelectionControlForm(ModelForm):
    class Meta:
        model = ControlSelection
        fields = ('response', )
        widgets = {
            'response': RadioSelect(),
        }


SelectionControlFormSet = modelformset_factory(ControlSelection, form=SelectionControlForm, extra=0, can_delete=False)


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
    class Meta:
        model = ScenarioCategoryAnswer
        fields = ('project', 'scenario_category')