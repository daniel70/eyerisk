import json
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

from .forms import SelectionForm, ScenarioCategoryAnswerForm, ScenarioCategoryAnswerCreateForm


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

    context = {'form': form, 'tree': tree, 'json': json.dumps(tree)}
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
def selection_response(request, pk):
    if request.method == "POST":
        level = request.POST['level']
        id = request.POST['id']
        response = request.POST['response']

        if response not in ["N", "A", "T", "M"]:
            return HttpResponse("notok")

        if level not in ["standard", "domain", "process", "practice", "activity"]:
            return HttpResponse("notok")

        selection = get_object_or_404(Selection, pk=pk, company=request.user.employee.company)
        if level == "standard":
            ControlSelection.objects.filter(selection_id=pk).select_related(
                'control__controlpractice__controlprocess__controldomain__standard'
            ).filter(
                control__controlpractice__controlprocess__controldomain__standard_id=id
            ).update(response=response)
        elif level == "domain":
            ControlSelection.objects.filter(selection_id=pk).select_related(
                'control__controlpractice__controlprocess__controldomain'
            ).filter(
                control__controlpractice__controlprocess__controldomain_id=id
            ).update(response=response)
        elif level == "process":
            ControlSelection.objects.filter(selection_id=pk).select_related(
                'control__controlpractice__controlprocess'
            ).filter(
                control__controlpractice__controlprocess_id=id
            ).update(response=response)
        elif level == "practice":
            ControlSelection.objects.filter(selection_id=pk).select_related(
                'control__controlpractice'
            ).filter(
                control__controlpractice_id=id
            ).update(response=response)
        elif level == "activity":
            ControlSelection.objects.filter(selection_id=pk).select_related(
                'control'
            ).filter(
                control_id=id
            ).update(response=response)

        return HttpResponse("ok")
    return HttpResponse("notok")


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
    if not selected_controls:
        return tree

    a = None; b = None; c = None; d = None
    for cs in selected_controls:

        if cs.control.controlpractice.controlprocess.controldomain.standard.id not in tree:
            if a:
                calculate_response([d, c, b, a])

            a = tree[cs.control.controlpractice.controlprocess.controldomain.standard.id] = {}
            a['nodes'] = {}
            a['text'] = cs.control.controlpractice.controlprocess.controldomain.standard.name

        if cs.control.controlpractice.controlprocess.controldomain.id not in a['nodes']:
            if b:
                calculate_response([d, c, b])

            b = a['nodes'][cs.control.controlpractice.controlprocess.controldomain.id] = {}
            b['nodes'] = {}
            b['text'] = cs.control.controlpractice.controlprocess.controldomain.domain

        if cs.control.controlpractice.controlprocess.id not in b['nodes']:
            if c:
                calculate_response([d, c])

            c = b['nodes'][cs.control.controlpractice.controlprocess.id] = {}
            c['nodes'] = {}
            c['text'] = cs.control.controlpractice.controlprocess.process_name

        if cs.control.controlpractice.id not in c['nodes']:
            if d:
                calculate_response([d])

            d = c['nodes'][cs.control.controlpractice.id] = {}
            d['nodes'] = {}
            d['text'] = cs.control.controlpractice.practice_name

        if cs.control.id not in d['nodes']:
            e = d['nodes'][cs.control.id] = {}
            e['text'] = cs.control.activity
            e['response_id'] = cs.id
            e['response'] = cs.response

    # after iterating the QuerySet we need to calculate the reponses for the final row!
    calculate_response([d, c, b, a])

    return tree


def calculate_response(columns: list):
    for column in columns:
        answers = set([v['response'] for v in column['nodes'].values()])
        column['response'] = 'N' if len(answers) > 1 else answers.pop()


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
