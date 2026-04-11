from django.contrib import admin
from .models import Book,BookCategory

# Register your models here.
@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display=['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display=['title','category','language', 'uploaded_at']
    search_fields=['title']
    list_filter=['category', 'language']