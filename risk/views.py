from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .models import Standard, Selection, SelectionControl, ControlDomain
from .forms import SelectionForm, SelectionControlForm, SelectionControlFormSet
from .serializers import StandardSerializer, SelectionSerializer, ControlDomainSerializer, SelectionControlSerializer
from rest_framework import viewsets
from collections import OrderedDict, defaultdict

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


class SelectionControlView(LoginRequiredMixin, generic.TemplateView):
    """
    Given a selection, we load all the control domains, processes, practices and activities.
    We also return all the currently selected activities.
    Selection --> selectioncontrol_set
    Selection --> standards.all() --> controldomain_set
    """
    template_name = 'risk/selection_control_react.html'

    def get_context_data(self, **kwargs):
        columns = ['id', 'selection_id', 'control_id']
        context = super(SelectionControlView, self).get_context_data(**kwargs)
        selection = get_object_or_404(Selection, pk = self.kwargs['pk'])
        context['selection'] = selection

        controls = SelectionControl.objects.filter(selection=selection).select_related(
            'control__controlpractice__controlprocess__controldomain__standard'
        )
        tree = []

        standard_ids = []
        domain_ids = []
        process_ids = []
        practice_ids = []

        standard = {}
        domain = {}
        process = {}
        practice = {}

        for response in controls:

            id = response.control.controlpractice.controlprocess.controldomain.standard.pk
            if id not in standard_ids:
                # we add the *old* standard to the dict and create a new one
                if standard:
                    tree.append(standard)
                standard = {
                    "id": id,
                    "text": response.control.controlpractice.controlprocess.controldomain.standard.name,
                    "all": False,
                    "domains": []

                }
                standard_ids.append(id)

            id = response.control.controlpractice.controlprocess.controldomain.pk
            if id not in domain_ids:
                if domain:
                    standard['domains'].append(domain)
                domain = {
                    "id": id,
                    "text": response.control.controlpractice.controlprocess.controldomain.domain,
                    "all": False,
                    "processes": []
                }
                domain_ids.append(id)

            id = response.control.controlpractice.controlprocess.pk
            if id not in process_ids:
                if process:
                    domain['processes'].append(process)
                process = {
                    "id": id,
                    "text": response.control.controlpractice.controlprocess.process_name,
                    "all": False,
                    "practices": []
                }
                process_ids.append(id)

            id = response.control.controlpractice.pk
            if id not in practice_ids:
                if practice:
                    process['practices'].append(practice)
                practice = {
                    "id": id,
                    "text": response.control.controlpractice.practice_name,
                    "all": False,
                    "activities": []
                }
                practice_ids.append(id)

            practice['activities'].append(
                {
                    "id": response.control.pk,
                    "text": response.control.activity,
                    "response_id": response.pk,
                    "value": response.response,
                }
            )

        if practice:
            process['practices'].append(practice)
        if process:
            domain['processes'].append(process)
        if domain:
            standard['domains'].append(domain)
        if standard:
            tree.append(standard)


        context['tree'] = tree

        return context