from django.contrib import admin
from .models import Kundali, Panchang,Festival,BSCalendarData

# Register your models here.
@admin.register(Kundali)
class KundaliAdmin(admin.ModelAdmin):
    list_display=['user_profile', 'generated_at']
    search_fields=['user_profile__full_name']
    readonly_fields=['generated_at']

@admin.register(Panchang)
class PanchangAdmin(admin.ModelAdmin):
    list_display=['date','fetched_at']
    search_fields=['date']
    readonly_fields=['fetched_at']
    ordering =['-date']


@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
    list_display = ['name_nepali', 'name_english', 'bs_date', 'ad_date', 'category', 'year']
    list_filter = ['category', 'year']
    search_fields = ['name_nepali', 'name_english', 'bs_date']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name_nepali', 'name_english', 'category', 'year')
        }),
        ('Dates', {
            'fields': ('bs_date', 'ad_date')
        }),
        ('Details', {
            'fields': ('description', 'significance')
        }),
    )

@admin.register(BSCalendarData)
class BSCalendarDataAdmin(admin.ModelAdmin):
    list_display = ['bs_year', 'bs_month', 'num_days', 'ad_month_start']
    list_filter = ['bs_year']
    ordering = ['bs_year', 'bs_month']
    readonly_fields = ['bs_year', 'bs_month']