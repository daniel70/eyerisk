import json

from django.core.urlresolvers import reverse_lazy, reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404

from .models import Standard, Selection, SelectionControl, ControlDomain, ControlProcess, RiskMap
from .forms import SelectionForm, SelectionControlForm, SelectionControlFormSet
from .serializers import StandardSerializer, SelectionSerializer, ControlDomainSerializer, SelectionControlSerializer, \
    ControlProcessSerializer
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from collections import OrderedDict, defaultdict


def riskmaps(request):
    maps = RiskMap.objects.filter(company=request.user.employee.company, is_template=False).values_list()
    maps_json = json.dumps(list(maps), cls=DjangoJSONEncoder)
    return render(request, template_name='risk/riskmaps.html', context={'riskmaps': maps_json})



class StandardListView(generics.ListAPIView):
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer


class StandardViewSet(viewsets.ModelViewSet):
    queryset = Standard.objects.filter()
    serializer_class = StandardSerializer


class SelectionViewSet(viewsets.ModelViewSet):
    queryset = Selection.objects.all()
    serializer_class = SelectionSerializer

    def get_queryset(self):
        return Selection.objects.filter(company=self.request.user.employee.company)

    @detail_route(methods=['get'], url_path='controls')
    def get_selection(self, request, pk=None):
        """
        This function will be available at: /api/selection/{pk}/controls
        It returns all the SelectionControls and all related information up to the Standard

        """
        return Response({"hello": "daniel"})


class SelectionControlViewSet(viewsets.ModelViewSet):
    queryset = SelectionControl.objects.all()
    serializer_class = SelectionControlSerializer

    def get_queryset(self):
        return SelectionControl.objects.filter(selection__company=self.request.user.employee.company)


# class SelectionStandardViewSet(viewsets.ModelViewSet):
#     queryset = SelectionStandard.objects.all()


class ControlDomainViewSet(viewsets.ModelViewSet):
    queryset = ControlDomain.objects.all()
    serializer_class = ControlDomainSerializer


class ControlProcessViewSet(viewsets.ModelViewSet):
    queryset = ControlProcess.objects.all()
    serializer_class = ControlProcessSerializer


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
    success_url = 'selection-edit'

    def form_valid(self, form):
        form.instance.company = self.request.user.employee.company
        return super(SelectionCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('selection-edit', args=(self.object.pk,))


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


class ControlSelectionView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'risk/control_selection.html'

    def get_context_data(self, **kwargs):
        context = super(ControlSelectionView, self).get_context_data(**kwargs)
        selection = get_object_or_404(Selection, pk=self.kwargs['pk'])
        context['selection'] = selection
        context['control_selection'] = SelectionControl.objects.filter(selection=selection).select_related(
            'control__controlpractice__controlprocess__controldomain__standard'
        ).order_by(
            'control__controlpractice__controlprocess__controldomain__standard__id',
            'control__controlpractice__controlprocess__controldomain__ordering',
            'control__controlpractice__controlprocess__ordering',
            'control__controlpractice__ordering',
            'control__ordering',
        )
        return context


def control_selection(request, pk):
    selection = get_object_or_404(Selection, pk=pk)

    if request.is_ajax():
        if request.method == "POST":
            post_dict = request.POST.dict()
            print(post_dict)
            if not post_dict['response'] in ['A', 'M', 'T']:
                return HttpResponse(status=422)  #unprocessable entry

        # update the database
        controls = post_dict['controls'].split('-')
        update = SelectionControl.objects.filter(selection=selection)
        # first filter on standard
        update = update.filter(control__controlpractice__controlprocess__controldomain__standard=controls.pop(0))
        if controls: # second is domain filter
            update = update.filter(control__controlpractice__controlprocess__controldomain=controls.pop(0))
        if controls: # third is process filter
            update = update.filter(control__controlpractice__controlprocess=controls.pop(0))
        if controls: # fourth is practice filter
            update = update.filter(control__controlpractice=controls.pop(0))
        if controls: # fifth is control filter
            update = update.filter(control=controls.pop(0))

        affected = update.update(response=post_dict['response'])
        print(affected, "row(s) affected")
        return HttpResponse(json.dumps("OK"))

    selected_controls = SelectionControl.objects.filter(selection=selection).select_related(
        'control__controlpractice__controlprocess__controldomain__standard'
    ).order_by(
        'control__controlpractice__controlprocess__controldomain__standard__id',
        'control__controlpractice__controlprocess__controldomain__ordering',
        'control__controlpractice__controlprocess__ordering',
        'control__controlpractice__ordering',
        'control__ordering',
    )

    context = {
        'selection': selection,
        'control_selection': selected_controls,
    }

    return render(request, template_name='risk/control_selection.html', context=context)


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


def control_selection_react(request, pk):
    selection = get_object_or_404(Selection, pk=pk)

    selected_controls = SelectionControl.objects.filter(selection=selection).select_related(
        'control__controlpractice__controlprocess__controldomain__standard'
    ).order_by(
        'control__controlpractice__controlprocess__controldomain__standard__id',
        'control__controlpractice__controlprocess__controldomain__ordering',
        'control__controlpractice__controlprocess__ordering',
        'control__controlpractice__ordering',
        'control__ordering',
    )

    # controls = SelectionControl.objects.filter(selection=selection).select_related(
    #     'control__controlpractice__controlprocess__controldomain__standard'
    # )

    tree = []

    standard_ids = []
    domain_ids = []
    process_ids = []
    practice_ids = []

    standard = {}
    domain = {}
    process = {}
    practice = {}

    for response in selected_controls:

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

    context = {
        'selection': selection,
        'tree': json.dumps(tree),
    }

    return render(request, template_name='risk/control_selection_react.html', context=context)