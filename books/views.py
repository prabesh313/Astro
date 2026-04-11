from django.shortcuts import render
from rest_framework import viewsets,filters
from .models import Book, BookCategory
from .serializers import BookSerializer, BookCategorySerializer

# Create your views here.
class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Book.objects.all().order_by('-uploaded_at')
    serializer_class=BookSerializer
    search_filters=[filters.SearchFilter]
    search_fields=['title', 'description', 'category__name']

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__id=category)
        return queryset
