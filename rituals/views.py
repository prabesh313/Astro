from django.shortcuts import render
from rest_framework import viewsets,filters
from .models import Ritual, Mantra
from .serializers import RitualSerializer, MantraSerializer

# Create your views here.
class MantraViewSet(viewsets.ModelViewSet):
    queryset=Mantra.objects.all()
    serializer_class=MantraSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'text']

class RitualViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Ritual.objects.all()
    serializer_class=RitualSerializer
    filter_backends=[filters.SearchFilter]
    search_filds=['name', 'description', 'category']
