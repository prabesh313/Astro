from django.contrib import admin
from .models import Kundali, Panchanga

# Register your models here.
@admin.register(Kundali)
class KundaliAdmin(admin.ModelAdmin):
    list_display=['user_profile', 'generated_at']

@admin.register(Panchanga)
class PanchangaAdmin(admin.ModelAdmin):
    list_display=['date','fetched_at']
