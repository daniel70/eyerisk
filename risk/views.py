from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Selection
from .forms import SelectionForm


class SelectionDetailView(generic.DetailView):
    template_name = 'risk/selection_detail.html'
    model = Selection


class SelectionListView(LoginRequiredMixin, generic.ListView):
    template_name = 'risk/selection_list.html'
    model = Selection
    context_object_name = 'selection_list'


class SelectionCreateView(LoginRequiredMixin, generic.CreateView):
    """
    When a Selection is created, we also need to associate SelectionDocuments
    and we need to copy the Questions for these Documents to the SelectionQuestion
    model. Also, when we save we need to check if any previously associated Document
    has now been removed and, if so, we need to remove their Questions from this Selection
    (or perhaps mark it as deleted to save the `decision` for this SelectionQuestion)
    """
    template_name = 'risk/selection_create_form.html'
    form_class = SelectionForm  # will point to SelectionDocumentForm later



class SelectionUpdate(LoginRequiredMixin, generic.UpdateView):
    template_name = 'risk/selection_update_form.html'
    form_class = SelectionForm
    model = Selection


class SelectionDelete(LoginRequiredMixin, generic.DeleteView):
    template_name = 'risk/selection_confirm_delete.html'
    model = Selection
    success_url = reverse_lazy('selection-list')