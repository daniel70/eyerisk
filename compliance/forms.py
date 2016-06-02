from django.forms import ModelForm, TextInput
from .models import Selection


class SelectionForm(ModelForm):
    class Meta:
        model = Selection
        fields = ('name',)
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'})
        }


class SelectionDocumentForm(ModelForm):
    """
    This form will hold a Selection object
    and a queryset with Document objects (where is_active=True)
    The documents can be selected through checkboxes.
    """
    class Meta:
        model = Selection
        fields = ('name',)
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'})
        }