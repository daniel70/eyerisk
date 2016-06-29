from django.forms import ModelForm, TextInput, CheckboxSelectMultiple, RadioSelect, modelformset_factory
from .models import Selection, SelectionControl


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
