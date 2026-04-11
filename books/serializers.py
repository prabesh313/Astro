from rest_framework import serializers
from .models import Book, BookCategory

class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=BookCategory
        fields='__all__'


class BookSerializer(serializers.ModelSerializer):
    category_name= serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model=Book
        fields=['id', 'title', 'category', 'category_name', 'description', 'file', 'cover_image', 'language', 'uploaded_at']
