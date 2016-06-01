from django.forms import ModelForm, TextInput
from .models import Selection

class SelectionForm(ModelForm):
    class Meta:
        model = Selection
        fields = ('name',)
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'})
        }