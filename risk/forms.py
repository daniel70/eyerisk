from django.forms import ModelForm, TextInput, CheckboxSelectMultiple, RadioSelect, modelformset_factory, \
    MultipleChoiceField, inlineformset_factory, BaseInlineFormSet
from .models import Selection, SelectionControl, ScenarioCategory, ScenarioCategoryAnswer, RiskTypeAnswer, RiskType


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
        model = SelectionControl
        fields = ('response', )
        widgets = {
            'response': RadioSelect(),
        }


SelectionControlFormSet = modelformset_factory(SelectionControl, form=SelectionControlForm, extra=0, can_delete=False)


class ScenarioCategoryAnswerForm(ModelForm):
    # threat_type = MultipleChoiceField(widget=CheckboxSelectMultiple, choices=ScenarioCategory.THREAT_TYPE_CHOICES)

    class Meta:
        model = ScenarioCategoryAnswer
        fields = ('name', 'company', 'scenario_category', 'threat_type', 'actor', 'event', 'asset', 'resource',
                  'timing', 'duration', 'detection', 'time_lag')

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
