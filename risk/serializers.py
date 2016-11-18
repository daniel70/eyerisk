from .models import Selection
from rest_framework import serializers



# class RiskMapSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RiskMap


class SelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Selection
        fields = ('id', 'name', 'standards')
        depth = 1
