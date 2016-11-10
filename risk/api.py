from .models import RiskMap, Selection
from .serializers import RiskMapSerializer,  SelectionSerializer


from rest_framework import viewsets


class RiskMapViewSet(viewsets.ModelViewSet):
    serializer_class = RiskMapSerializer

    def get_queryset(self):
        return RiskMap.objects.filter(company=self.request.user.employee.company)


class SelectionViewSet(viewsets.ModelViewSet):
    serializer_class = SelectionSerializer

    def get_queryset(self):
        return Selection.objects.filter(company=self.request.user.employee.company)

    # @detail_route(methods=['get'], url_path='controls')
    # def get_selection(self, request, pk=None):
    #     """
    #     This function will be available at: /api/selection/{pk}/controls
    #     It returns all the SelectionControls and all related information up to the Standard
    #
    #     """
    #     return Response({"hello": "daniel"})

# from .models import Standard, Selection, SelectionControl, ControlDomain, ControlProcess
# from .serializers import StandardSerializer, SelectionSerializer, ControlDomainSerializer, SelectionControlSerializer, \
#     ControlProcessSerializer
# from rest_framework import generics
# from rest_framework.decorators import detail_route
# from rest_framework.response import Response
#
# class StandardListView(generics.ListAPIView):
#     queryset = Standard.objects.all()
#     serializer_class = StandardSerializer
#
#
# class StandardViewSet(viewsets.ModelViewSet):
#     queryset = Standard.objects.filter()
#     serializer_class = StandardSerializer
#
#
#
#
# class SelectionControlViewSet(viewsets.ModelViewSet):
#     queryset = SelectionControl.objects.all()
#     serializer_class = SelectionControlSerializer
#
#     def get_queryset(self):
#         return SelectionControl.objects.filter(selection__company=self.request.user.employee.company)
#
#
# # class SelectionStandardViewSet(viewsets.ModelViewSet):
# #     queryset = SelectionStandard.objects.all()
#
#
# class ControlDomainViewSet(viewsets.ModelViewSet):
#     queryset = ControlDomain.objects.all()
#     serializer_class = ControlDomainSerializer
#
#
# class ControlProcessViewSet(viewsets.ModelViewSet):
#     queryset = ControlProcess.objects.all()
#     serializer_class = ControlProcessSerializer
#
#
