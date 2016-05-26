from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Selection


class SelectionIndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'compliance/index.html'
    model = Selection
    context_object_name = 'selection_list'


class SelectionCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'compliance/selection-create.html'
    model = Selection
    fields = ['name']