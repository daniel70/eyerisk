from .models import Selection, RiskMap, RiskMapValue
from .serializers import SelectionSerializer, RiskMapSerializer, RiskMapAndValuesSerializer

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response


class SelectionViewSet(viewsets.ModelViewSet):
    serializer_class = SelectionSerializer

    def get_queryset(self):
        return Selection.objects.filter(company=self.request.user.employee.company)


class RiskMapViewSet(viewsets.ModelViewSet):
    serializer_class = RiskMapSerializer

    def get_queryset(self):
        return RiskMap.objects.filter(company=self.request.user.employee.company)

    def list(self, request):
        serializer = RiskMapSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        risk_map = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = RiskMapAndValuesSerializer(risk_map)
        return Response(serializer.data)
