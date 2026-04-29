from django.contrib import admin
from .models import Kundali, Panchang,Festival,BSCalendarData,Horoscope

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

@admin.register(Horoscope)
class HoroscopeAdmin(admin.ModelAdmin):
    list_display = ['rashi', 'date', 'horoscope_type', 'love_score', 'career_score', 'fetched_at']
    list_filter = ['rashi', 'date', 'horoscope_type']
    search_fields = ['rashi']
    readonly_fields = ['fetched_at', 'api_response']
    fieldsets = (
        ('Basic Info', {
            'fields': ('rashi', 'horoscope_type', 'date')
        }),
        ('Prediction', {
            'fields': ('prediction', 'advice')
        }),
        ('Scores', {
            'fields': ('love_score', 'career_score', 'health_score', 'money_score')
        }),
        ('Lucky Attributes', {
            'fields': ('lucky_color', 'lucky_number', 'lucky_time')
        }),
        ('Debug', {
            'fields': ('api_response', 'fetched_at'),
            'classes': ('collapse',)
        }),
    )