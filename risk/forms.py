from django.forms import ModelForm, TextInput, CheckboxSelectMultiple
from .models import Selection


class SelectionForm(ModelForm):
    class Meta:
        model = Selection
        fields = ('name', 'documents')
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'documents': CheckboxSelectMultiple(),
        }
