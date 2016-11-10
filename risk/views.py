from pprint import pprint
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from django.forms import inlineformset_factory

from .models import Standard, Selection, ControlSelection, ControlDomain, ControlProcess, RiskMap, ScenarioCategory, \
    ScenarioCategoryAnswer, Company, RiskTypeAnswer, ProcessEnablerAnswer, EnablerAnswer
from .forms import SelectionForm, SelectionControlForm, SelectionControlFormSet, ScenarioCategoryAnswerForm, \
    ScenarioCategoryAnswerCreateForm


def is_employee(user):
    """
    Most views work with the set of objects that belong to a company.
    E.g. the list of scenario's only shows the scenario's that belong to the company of the currently logged in user.
    So most views should be protected to only show its contents when requested by an employee.
    """
    return hasattr(user, 'employee')


def riskmaps(request):
    return render(request, template_name='risk/riskmaps.html')


# @permission_required('risk.change_selection')
@user_passes_test(is_employee)
def selection_list(request):
    selection_list = Selection.objects.filter(company=request.user.employee.company).order_by('-updated')
    context = {'selection_list': selection_list}
    return render(request, template_name='risk/selection_list.html', context=context)


@user_passes_test(is_employee)
def selection_create(request):
    """
    When a Selection is created, we also need to associate SelectionDocuments
    and we need to copy the Questions for these Documents to the SelectionQuestion
    model. Also, when we save we need to check if any previously associated Document
    has now been removed and, if so, we need to remove their Questions from this Selection
    (or perhaps mark it as deleted to save the `decision` for this SelectionQuestion)
    """
    if request.method == "POST":
        form = SelectionForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.company = request.user.employee.company
            selection = form.save()
            return HttpResponseRedirect(reverse('selection-edit', args=[selection.pk]))

    else:
        form = SelectionForm()
    context = {'form': form}
    return render(request, template_name='risk/selection_create_form.html', context=context)


@user_passes_test(is_employee)
def selection_edit(request, pk):
    selection = get_object_or_404(Selection, pk=pk, company=request.user.employee.company)
    if request.method == "POST":
        form = SelectionForm(request.POST, request.FILES, instance=selection)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('selection-edit', args=[selection.pk]))
    else:
        form = SelectionForm(instance=selection)

    tree = get_control_selection(pk)
    context = {'form': form, 'tree': tree}
    return render(request, template_name='risk/selection_update_form.html', context=context)


@permission_required('risk.delete_selection')
def selection_delete(request, pk):
    selection = get_object_or_404(Selection, pk=pk, company=request.user.employee.company)
    if request.method == "POST":
        selection.delete()
        return HttpResponseRedirect(reverse('selection-list'))

    context = {'object': selection}
    return render(request, template_name='risk/selection_confirm_delete.html', context=context)


@user_passes_test(is_employee)
def scenario_list(request):
    """
    This view lists all the ScenarioCategoryAnswers. They can be edited and deleted.
    Also, a ScenarioCategoryAnswer can be created from this view.
    We first ask for the most basic information (name and category) and the post_save signal will do all the work
    of creating the corresponding risk types and enablers.
    After the ScenarioCategoryAnswer is created we redirect to the corresponding edit page.
    """
    if request.method == "POST":
        form = ScenarioCategoryAnswerCreateForm(request.POST, request.FILES)
        if form.is_valid():
            sca = ScenarioCategoryAnswer(scenario_category=form.cleaned_data['scenario_category'],
                                         project=form.cleaned_data['project'])
            sca.save()
            return HttpResponseRedirect(reverse('scenario-edit', args=[sca.pk]))

    else:
        form = ScenarioCategoryAnswerCreateForm()
    scenarios = ScenarioCategoryAnswer.objects.filter(project__company=request.user.employee.company).order_by('-updated')
    context = {'scenario_list': scenarios, 'form': form}
    return render(request, template_name='risk/scenario_list.html', context=context)


@user_passes_test(is_employee)
@permission_required('risk.change_scenariocategoryanswer')
def scenario_edit(request, pk):
    # hardcoded for now
    sca = get_object_or_404(ScenarioCategoryAnswer, pk=pk, project__company=request.user.employee.company)
    risk_type_answer_factory = inlineformset_factory(ScenarioCategoryAnswer, RiskTypeAnswer, fields=('description',),
                                                  extra=0, can_delete=False)
    process_enabler_answer_factory = inlineformset_factory(
        ScenarioCategoryAnswer, ProcessEnablerAnswer,
        fields=('effect_on_frequency', 'effect_on_impact', 'essential_control'),
        extra=0, can_delete=False
    )
    enabler_answer_factory = inlineformset_factory(
        ScenarioCategoryAnswer, EnablerAnswer,
        fields=('effect_on_frequency', 'effect_on_impact', 'essential_control'),
        extra=0, can_delete=False
    )

    if request.method == "POST":
        form = ScenarioCategoryAnswerForm(request.POST, request.FILES, instance=sca)
        risk_type_answer_formset = risk_type_answer_factory(request.POST, request.FILES, instance=sca)
        process_enabler_answer_formset = process_enabler_answer_factory(request.POST, request.FILES, instance=sca)
        enabler_answer_formset = enabler_answer_factory(request.POST, request.FILES, instance=sca)

        if form.is_valid() \
                and risk_type_answer_formset.is_valid() \
                and process_enabler_answer_formset.is_valid() \
                and enabler_answer_formset.is_valid:
            form.save()
            risk_type_answer_formset.save()
            process_enabler_answer_formset.save()
            enabler_answer_formset.save()
            return HttpResponseRedirect(reverse('scenario-list'))
        else:
            print(form.errors)
            print(risk_type_answer_formset.errors)
            print(process_enabler_answer_formset.errors)
            print(enabler_answer_formset.errors)
    else:
        form = ScenarioCategoryAnswerForm(instance=sca)
        risk_type_answer_formset = risk_type_answer_factory(instance=sca)
        process_enabler_answer_formset = process_enabler_answer_factory(instance=sca)
        enabler_answer_formset = enabler_answer_factory(instance=sca)


    context = {
        'form': form,
        'risk_type_answer_formset': risk_type_answer_formset,
        'process_enabler_answer_formset': process_enabler_answer_formset,
        'enabler_answer_formset': enabler_answer_formset,
    }

    template_name = 'risk/scenario_edit.html'
    return render(request, template_name=template_name, context=context)


@permission_required('risk.delete_scenariocategoryanswer')
def scenario_delete(request, pk):
    scenario_category_answer = get_object_or_404(ScenarioCategoryAnswer, pk=pk, project__company=request.user.employee.company)
    if request.method == "POST":
        scenario_category_answer.delete()
        return HttpResponseRedirect(reverse('scenario-list'))

    context = {'object': scenario_category_answer}
    return render(request, template_name='risk/scenario_confirm_delete.html', context=context)


class SelectionDetail(generic.DetailView):
    template_name = 'risk/selection_detail.html'
    model = Selection


# class SelectionList(LoginRequiredMixin, generic.ListView):
#     template_name = 'risk/selection_list.html'
#     # model = Selection
#     context_object_name = 'selection_list'
#
#     def get_queryset(self):
#         return Selection.objects.filter(company=self.request.user.employee.company)


# class SelectionCreate(LoginRequiredMixin, generic.CreateView):
#     template_name = 'risk/selection_create_form.html'
#     form_class = SelectionForm  # will point to SelectionDocumentForm later
#     success_url = 'selection-edit'
#
#     def form_valid(self, form):
#         form.instance.company = self.request.user.employee.company
#         return super(SelectionCreate, self).form_valid(form)
#
#     def get_success_url(self):
#         return reverse('selection-edit', args=(self.object.pk,))


# class SelectionUpdate(LoginRequiredMixin, generic.UpdateView):
#     template_name = 'risk/selection_update_form.html'
#     form_class = SelectionForm
#     model = Selection


class SelectionControlAssess(LoginRequiredMixin, generic.TemplateView):
    template_name = 'risk/selection_control_update_form.html'
    form_class = SelectionControlForm
    # model = ControlSelection

    def get_context_data(self, **kwargs):
        context = super(SelectionControlAssess, self).get_context_data(**kwargs)
        # context['formset'] = ControlSelection.objects.select_related().filter(selection=self.kwargs['selection_id'])
        context['formset'] = SelectionControlFormSet(
            queryset=ControlSelection.objects.filter(selection=self.kwargs['selection_id'])
        )
        return context


class ControlSelectionView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'risk/control_selection.html'

    def get_context_data(self, **kwargs):
        context = super(ControlSelectionView, self).get_context_data(**kwargs)
        selection = get_object_or_404(Selection, pk=self.kwargs['pk'])
        context['selection'] = selection
        context['control_selection'] = ControlSelection.objects.filter(selection=selection).select_related(
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
        update = ControlSelection.objects.filter(selection=selection)
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

    selected_controls = ControlSelection.objects.filter(selection=selection).select_related(
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


def get_control_selection(pk):
    selection = get_object_or_404(Selection, pk=pk)
    selected_controls = ControlSelection.objects.filter(selection=selection).select_related(
        'control__controlpractice__controlprocess__controldomain__standard'
    ).order_by(
        'control__controlpractice__controlprocess__controldomain__standard__id',
        'control__controlpractice__controlprocess__controldomain__ordering',
        'control__controlpractice__controlprocess__ordering',
        'control__controlpractice__ordering',
        'control__ordering',
    )

    tree = {}
    a = None; b = None; c = None; d = None
    for cs in selected_controls:

        if cs.control.controlpractice.controlprocess.controldomain.standard.id not in tree:
            if a:
                answers = set([v['response'] for v in d['nodes'].values()])
                d['response'] = 'N' if len(answers) > 1 else answers.pop()

                answers = set([v['response'] for v in c['nodes'].values()])
                c['response'] = 'N' if len(answers) > 1 else answers.pop()

                answers = set([v['response'] for v in b['nodes'].values()])
                b['response'] = 'N' if len(answers) > 1 else answers.pop()

                answers = set([v['response'] for v in a['nodes'].values()])
                a['response'] = 'N' if len(answers) > 1 else answers.pop()

            a = tree[cs.control.controlpractice.controlprocess.controldomain.standard.id] = {}
            a['nodes'] = {}
            a['text'] = cs.control.controlpractice.controlprocess.controldomain.standard.name

        if cs.control.controlpractice.controlprocess.controldomain.id not in a['nodes']:
            if b:
                answers = set([v['response'] for v in d['nodes'].values()])
                d['response'] = 'N' if len(answers) > 1 else answers.pop()

                answers = set([v['response'] for v in c['nodes'].values()])
                c['response'] = 'N' if len(answers) > 1 else answers.pop()

                answers = set([v['response'] for v in b['nodes'].values()])
                b['response'] = 'N' if len(answers) > 1 else answers.pop()

            b = a['nodes'][cs.control.controlpractice.controlprocess.controldomain.id] = {}
            b['nodes'] = {}
            b['text'] = cs.control.controlpractice.controlprocess.controldomain.domain

        if cs.control.controlpractice.controlprocess.id not in b['nodes']:
            if c:
                answers = set([v['response'] for v in d['nodes'].values()])
                d['response'] = 'N' if len(answers) > 1 else answers.pop()

                answers = set([v['response'] for v in c['nodes'].values()])
                c['response'] = 'N' if len(answers) > 1 else answers.pop()

            c = b['nodes'][cs.control.controlpractice.controlprocess.id] = {}
            c['nodes'] = {}
            c['text'] = cs.control.controlpractice.controlprocess.process_name

        if cs.control.controlpractice.id not in c['nodes']:
            if d:
                answers = set([v['response'] for v in d['nodes'].values()])
                d['response'] = 'N' if len(answers) > 1 else answers.pop()

            d = c['nodes'][cs.control.controlpractice.id] = {}
            d['nodes'] = {}
            d['text'] = cs.control.controlpractice.practice_name

        if cs.control.id not in d['nodes']:
            e = d['nodes'][cs.control.id] = {}
            e['text'] = cs.control.activity
            e['response_id'] = cs.id
            e['response'] = cs.response

    return tree


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

        controls = ControlSelection.objects.filter(selection=selection).select_related(
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

    selected_controls = ControlSelection.objects.filter(selection=selection).select_related(
        'control__controlpractice__controlprocess__controldomain__standard'
    ).order_by(
        'control__controlpractice__controlprocess__controldomain__standard__id',
        'control__controlpractice__controlprocess__controldomain__ordering',
        'control__controlpractice__controlprocess__ordering',
        'control__controlpractice__ordering',
        'control__ordering',
    )

    # controls = ControlSelection.objects.filter(selection=selection).select_related(
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
