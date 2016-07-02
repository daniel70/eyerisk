from .models import Standard, Selection, SelectionControl, ControlDomain, ControlActivity, ControlPractice, ControlProcess
from rest_framework import serializers


class StandardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Standard
        fields = ('id', 'name', 'is_active')


class SelectionSerializer(serializers.HyperlinkedModelSerializer):
    standards = StandardSerializer(many=True, read_only=True)

    class Meta:
        model = Selection
        fields = ('id', 'name', 'standards')


class ControlDomainSerializer(serializers.HyperlinkedModelSerializer):
    standard = StandardSerializer(many=False, read_only=True)

    class Meta:
        model = ControlDomain
        fields = ('id', 'standard', 'ordering', 'area', 'domain')


class ControlProcessSerializer(serializers.HyperlinkedModelSerializer):
    controldomain = ControlDomainSerializer(many=False, read_only=True)

    class Meta:
        model = ControlProcess
        fields = ('id', 'controldomain', 'ordering', 'process_id', 'process_name', 'process_description', 'process_purpose')


class ControlPracticeSerializer(serializers.HyperlinkedModelSerializer):
    controlprocess = ControlProcessSerializer(many=False, read_only=True)

    class Meta:
        model = ControlPractice
        fields = ('id', 'controlprocess', 'ordering', 'practice_id', 'practice_name', 'practice_governance')


class ControlActivitySerializer(serializers.HyperlinkedModelSerializer):
    controlpractice = ControlPracticeSerializer(many=False, read_only=True)

    class Meta:
        model = ControlActivity
        fields = ('id', 'controlpractice', 'ordering', 'activity_id', 'activity', 'activity_help')


class SelectionControlSerializer(serializers.HyperlinkedModelSerializer):
    selection = SelectionSerializer(many=False, read_only=True)
    control = ControlActivitySerializer(many=False, read_only=True)

    class Meta:
        model = SelectionControl
        fields = ('id', 'selection', 'control', 'response')
