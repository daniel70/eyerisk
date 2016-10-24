from django.forms import ModelForm, TextInput, CheckboxSelectMultiple, RadioSelect, modelformset_factory, \
    MultipleChoiceField
from .models import Selection, SelectionControl, ScenarioCategory


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


# class ScenarioCategoryForm(ModelForm):
#     # threat_type = MultipleChoiceField(widget=CheckboxSelectMultiple, choices=ScenarioCategory.THREAT_TYPE_CHOICES)
#
#     class Meta:
#         model = ScenarioCategory
#         fields = ('nr', 'name', 'risk_scenario', 'threat_type', 'actor', 'event', 'asset', 'resource')
#         widgets = {
#             'threat_type': CheckboxSelectMultiple(choices=ScenarioCategory.THREAT_TYPE_CHOICES),
#             'actor': CheckboxSelectMultiple(choices=ScenarioCategory.ACTOR_CHOICES),
#             'event': CheckboxSelectMultiple(choices=ScenarioCategory.EVENT_CHOICES),
#             'asset': CheckboxSelectMultiple(choices=ScenarioCategory.ASSET_RESOURCE_CHOICES),
#             'resource': CheckboxSelectMultiple(choices=ScenarioCategory.ASSET_RESOURCE_CHOICES),
#
#         }
#
