from django.contrib import admin
from .models import Chat, PriestSchedule, Review, UserProfile,Message

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display=['full_name', 'birth_date', 'birth_place']
    list_filter = ['user_type', 'is_verified']
    search_fields = ['full_name', 'specializations']

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['participant1', 'participant2', 'created_at', 'is_active']
    list_filter = ['created_at', 'is_active']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'chat', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['jajaman', 'purohit', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']

@admin.register(PriestSchedule)
class PriestScheduleAdmin(admin.ModelAdmin):
    list_display = ['priest', 'busy_date', 'event_type', 'event_title', 'created_at']
    list_filter = ['busy_date', 'event_type']
    search_fields = ['priest__userprofile__full_name', 'event_title']
    ordering = ['-busy_date']