from django.contrib import admin
from .models import Ritual, Mantra

# Register your models here.
@admin.register(Mantra)
class MantraAdmin(admin.ModelAdmin):
    list_display=['name','language']
    search_fields=['name', 'text']

@admin.register(Ritual)
class RitualAdmin(admin.ModelAdmin):
    list_display=['name','category', 'duration_minutes']
    search_fields=['name']
    filter_horizontal=['mantras']
