from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Standard, Selection, SelectionControl, ControlDomain
from .forms import SelectionForm, SelectionControlForm, SelectionControlFormSet
from .serializers import StandardSerializer, SelectionSerializer, ControlDomainSerializer, SelectionControlSerializer
from rest_framework import viewsets


class StandardViewSet(viewsets.ModelViewSet):
    queryset = Standard.objects.filter(is_active=True)
    serializer_class = StandardSerializer


class SelectionViewSet(viewsets.ModelViewSet):
    queryset = Selection.objects.all()
    serializer_class = SelectionSerializer

    def get_queryset(self):
        return Selection.objects.filter(company=self.request.user.employee.company)


class SelectionControlViewSet(viewsets.ModelViewSet):
    queryset = SelectionControl.objects.all()
    serializer_class = SelectionControlSerializer

    def get_queryset(self):
        return SelectionControl.objects.filter(selection__company=self.request.user.employee.company)


class ControlDomainViewSet(viewsets.ModelViewSet):
    queryset = ControlDomain.objects.all()
    serializer_class = ControlDomainSerializer





class SelectionDetail(generic.DetailView):
    template_name = 'risk/selection_detail.html'
    model = Selection


class SelectionList(LoginRequiredMixin, generic.ListView):
    template_name = 'risk/selection_list.html'
    # model = Selection
    context_object_name = 'selection_list'

    def get_queryset(self):
        return Selection.objects.filter(company=self.request.user.employee.company)

class SelectionCreate(LoginRequiredMixin, generic.CreateView):
    """
    When a Selection is created, we also need to associate SelectionDocuments
    and we need to copy the Questions for these Documents to the SelectionQuestion
    model. Also, when we save we need to check if any previously associated Document
    has now been removed and, if so, we need to remove their Questions from this Selection
    (or perhaps mark it as deleted to save the `decision` for this SelectionQuestion)
    """
    template_name = 'risk/selection_create_form.html'
    form_class = SelectionForm  # will point to SelectionDocumentForm later

    def form_valid(self, form):
        form.instance.company = self.request.user.employee.company
        return super(SelectionCreate, self).form_valid(form)


class SelectionUpdate(LoginRequiredMixin, generic.UpdateView):
    template_name = 'risk/selection_update_form.html'
    form_class = SelectionForm
    model = Selection


class SelectionDelete(LoginRequiredMixin, generic.DeleteView):
    template_name = 'risk/selection_confirm_delete.html'
    model = Selection
    success_url = reverse_lazy('selection-list')


class SelectionControlAssess(LoginRequiredMixin, generic.TemplateView):
    template_name = 'risk/selection_control_update_form.html'
    form_class = SelectionControlForm
    # model = SelectionControl

    def get_context_data(self, **kwargs):
        context = super(SelectionControlAssess, self).get_context_data(**kwargs)
        # context['formset'] = SelectionControl.objects.select_related().filter(selection=self.kwargs['selection_id'])
        context['formset'] = SelectionControlFormSet(
            queryset=SelectionControl.objects.filter(selection=self.kwargs['selection_id'])
        )
        return context