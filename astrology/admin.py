from django.contrib import admin
from .models import Kundali, Panchang

# Register your models here.
@admin.register(Kundali)
class KundaliAdmin(admin.ModelAdmin):
    list_display=['user_profile', 'generated_at']

@admin.register(Panchang)
class PanchangAdmin(admin.ModelAdmin):
    list_display=['date','fetched_at']
