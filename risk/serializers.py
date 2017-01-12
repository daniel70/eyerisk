from .models import Selection, RiskMap, RiskMapValue
from rest_framework import serializers


class RiskMapValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskMapValue
        fields = ['axis_type', 'position', 'rating', 'descriptor', 'definition', 'short_rating']


class RiskMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskMap
        fields = '__all__'


class RiskMapAndValuesSerializer(serializers.ModelSerializer):
    values = RiskMapValueSerializer(many=True, read_only=True)

    class Meta:
        model = RiskMap
        fields = '__all__'


class SelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Selection
        fields = ('id', 'name', 'standards')
        depth = 1
