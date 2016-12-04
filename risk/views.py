from datetime import datetime as dt
from collections import OrderedDict
from pprint import pprint
import json
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, get_list_or_404, _get_queryset
from django.forms import inlineformset_factory, modelformset_factory
from django.db.utils import IntegrityError
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext_lazy as _

from .models import Selection, ControlSelection, ScenarioCategoryAnswer, RiskTypeAnswer, ProcessEnablerAnswer, EnablerAnswer, \
    RiskMap, RiskMapValue, Impact

from .forms import SelectionForm, ScenarioCategoryAnswerForm, ScenarioCategoryAnswerCreateForm, \
    RiskMapCategoryCreateForm, RiskMapValueFormSet, ImpactDescriptionFormSet


def is_employee(user):
    """
    Most views work with the set of objects that belong to a company.
    E.g. the list of scenario's only shows the scenario's that belong to the company of the currently logged in user.
    So most views should be protected to only show its contents when requested by an employee.
    """
    return hasattr(user, 'employee')


# @permission_required('risk.change_selection')
@user_passes_test(is_employee)
def selection_list(request):
    selection = Selection.objects.filter(company=request.user.employee.company).order_by('-updated')
    context = {'selection_list': selection}
    return render(request, template_name='risk/selection_list.html', context=context)


# @user_passes_test(lambda u: u.is_authenitated())
def no_company(request):
    return render(request, template_name='risk/no_company.html')


@user_passes_test(is_employee, login_url='no-company')
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
@permission_required('risk.change_selection')
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
        messages.success(request, "Selection deleted successfully")
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


@user_passes_test(is_employee, login_url='no-company')
def scenario_list(request):
    """
    This view lists all the ScenarioCategoryAnswers. They can be edited and deleted.
    Also, a ScenarioCategoryAnswer can be created from this view.
    We first ask for the most basic information (name and category) and the post_save signal will do all the work
    of creating the corresponding risk types and enablers.
    After the ScenarioCategoryAnswer is created we redirect to the corresponding edit page.
    """
    if request.method == "POST":
        form = ScenarioCategoryAnswerCreateForm(data=request.POST, files=request.FILES, company=request.user.employee.company)
        if form.is_valid():
            sca = ScenarioCategoryAnswer(scenario_category=form.cleaned_data['scenario_category'],
                                         project=form.cleaned_data['project'])
            sca.save()
            return HttpResponseRedirect(reverse('scenario-edit', args=[sca.pk]))

    else:
        form = ScenarioCategoryAnswerCreateForm(company=request.user.employee.company)
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


def riskmaps(request):
    return render(request, template_name='risk/riskmaps.html')


@user_passes_test(is_employee)
def risk_map_list(request, pk=None):

    if pk is None:
        risk_map = get_object_or_404(RiskMap, company=request.user.employee.company, level=1)
    else:
        risk_map = get_object_or_404(RiskMap, company=request.user.employee.company, pk=pk)

    if request.method == "POST":
        formset = RiskMapValueFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('risk-map-list', args=[risk_map.pk,]))
        else:
            messages.error(request, _('An error occured. The form has NOT been saved.'))
    else:
        formset = RiskMapValueFormSet(queryset=risk_map.riskmapvalue_set.all())

    risk_map_tree = get_risk_map_tree(request.user.employee.company, pk)
    # risk_map_values = get_list_or_404(RiskMapValue, risk_map=pk)
    # add a form to the context in case the client wants to create a new CATEGORY
    form = RiskMapCategoryCreateForm()
    context = {
        'risk_map': risk_map,
        'risk_form': form,
        'risk_formset': formset,
        'risk_map_tree': risk_map_tree,
        # 'risk_map_values': risk_map_values,
    }
    return render(request, template_name='risk/risk_map_list.html', context=context)


@user_passes_test(is_employee)
@require_http_methods(["POST", ])
@permission_required('risk.add_riskmap')
def risk_map_create(request):
    if request.method == "POST":
        level = request.POST.get('level', None)
        risk_type = request.POST.get('risk_type', None)

        if risk_type is not None:
            for k, v in RiskMap.RISK_TYPE_CHOICES:
                if v.upper() == risk_type.upper():
                    risk_type_key = k

        if level == '2':
            #  we are going to create a new risk type level, copying from the ENTERPRISE level
            #  make sure it does not already exist
            if RiskMap.objects.filter(company=request.user.employee.company, level=2, risk_type=risk_type_key).exists():
                messages.warning(request, "Risk map could not be created because it already exists.")
                return HttpResponseRedirect(reverse('risk-map-list'))

            risk_map = get_object_or_404(RiskMap, company=request.user.employee.company, level=1, is_template=False)
            risk_map.parent_id_id = risk_map.pk
            risk_map.pk = None
            risk_map.name = risk_type
            risk_map.level = level
            risk_map.risk_type = risk_type_key
            risk_map.is_template = False
            risk_map.created = dt.now()
            risk_map.save()

        return HttpResponseRedirect(reverse('risk-map-list', args=[risk_map.pk]))


@user_passes_test(is_employee)
def impact_list(request):
    formset = ImpactDescriptionFormSet(queryset=Impact.objects.filter(company=request.user.employee.company))
    context = {'formset': formset}
    return render(request, template_name='risk/impact_list.html', context=context)

@user_passes_test(is_employee)
@require_http_methods(["POST", ])
@permission_required('risk.add_riskmap')
def risk_map_create_category(request):
    if request.method == "POST":
        form = RiskMapCategoryCreateForm(request.POST, request.FILES)
        if form.is_valid():
            parent = form.cleaned_data['parent']  # parent_id points to the parent record, not the int value
            new_risk_map = form.save(commit=False)
            new_risk_map.company = request.user.employee.company
            new_risk_map.level = 3
            new_risk_map.risk_type = parent.risk_type
            new_risk_map.is_template = False
            try:
                new_risk_map.save()
                return HttpResponseRedirect(reverse('risk-map-list', args=[new_risk_map.pk]))
            except IntegrityError as e:
                form.add_error('name', "A risk map with this name already exists.")
                risk_map = get_risk_map_tree(request.user.employee.company)
                context = {
                    'risk_form': form,
                    'risk_map': risk_map,
                    # 'risk_map_values': risk_map_values,
                }
                return render(request, template_name='risk/risk_map_list.html', context=context)


@user_passes_test(is_employee)
@permission_required('risk.delete_riskmap')
def risk_map_delete(request, pk):
    risk_map = get_object_or_404(RiskMap, pk=pk, company=request.user.employee.company)
    if request.method == "POST":
        risk_map.delete()
        messages.success(request, "Risk Map deleted successfully")
        return HttpResponseRedirect(reverse('risk-map-list'))

    context = {'object': risk_map}
    return render(request, template_name='risk/risk_map_confirm_delete.html', context=context)


def get_risk_map_tree(company, pk=None):
    """
    risk_maps = {
        "ENTERPRISE": {
            "id": 42,
            "level": "ENTERPRISE",
            "risk_type": "",
            "maps": {
                "STRATEGIC": {},
                "FINANCIAL": {},
                "OPERATIONAL": {
                    "id": 13,
                    "level": "RISK TYPE",
                    "risk_type": "Operational",
                    "maps": {
                        "RISK ABC": {
                            "id": 14,
                            "level": "RISK CATEGORY",
                            "risk_type": "Operational",
                        },
                    },
                },
                "COMPLIANCE": {},
            }
        }
    }
    """
    risk_map = {
        "ENTERPRISE": {
            "maps": OrderedDict(),
        },
    }
    for k, v in RiskMap.RISK_TYPE_CHOICES:
        risk_map["ENTERPRISE"]["maps"][v.upper()] = {"maps": OrderedDict()}

    risk_maps = RiskMap.objects.filter(company=company)
    for map in risk_maps:
        level = map.get_level_display()
        if level == 'ENTERPRISE':
            risk_map['ENTERPRISE']['id'] = map.pk
            if pk is None:
                pk = map.pk
        elif level == 'RISK TYPE':
            risk_map['ENTERPRISE']['maps'][map.get_risk_type_display().upper()]['id'] = map.pk
        elif level == 'RISK CATEGORY':
            risk_map['ENTERPRISE']['maps'][map.get_risk_type_display().upper()]['maps'][map.name] = map.pk

    return risk_map
