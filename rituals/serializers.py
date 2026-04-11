from rest_framework import serializers
from .models import Ritual,Mantra

class MantraSerializer(serializers.ModelSerializer):
    class Meta:
        model=Mantra
        fields='__all__'

class RitualSerializer(serializers.ModelSerializer):
    mantras = MantraSerializer(many=True, read_only=True)
    class Meta:
        model=Ritual
        fields='__all__'
