from .models import Selection
from .serializers import SelectionSerializer


from rest_framework import viewsets

class SelectionViewSet(viewsets.ModelViewSet):
    serializer_class = SelectionSerializer

    def get_queryset(self):
        return Selection.objects.filter(company=self.request.user.employee.company)
