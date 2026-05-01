from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('jajaman', 'Jajaman (Customer)'),
        ('purohit', 'Purohit (Priest)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    
    full_name = models.CharField(max_length=200)
    birth_date = models.DateField(null=True, blank=True)
    birth_time = models.TimeField(null=True, blank=True)
    birth_place = models.CharField(max_length=200, blank=True)
    birth_latitude = models.FloatField(null=True, blank=True)
    birth_longitude = models.FloatField(null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    specializations = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # In NPR
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='priest_profiles/', blank=True)
    
    average_rating = models.FloatField(default=0)
    total_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.get_user_type_display()})"

    class Meta:
        verbose_name_plural = "User Profiles"


class Chat(models.Model):
    jajaman = models.ForeignKey(User,on_delete=models.CASCADE,related_name='chats_as_customer')
    purohit = models.ForeignKey(User,on_delete=models.CASCADE,related_name='chats_as_priest')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Chat: {self.jajaman.username} <--> {self.purohit.username}"

    class Meta:
        unique_together = ('jajaman', 'purohit')
        ordering = ['-updated_at']


class Message(models.Model):
    """Individual messages in a chat"""
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message_text = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message_text[:50]}"

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat', 'created_at']),
            models.Index(fields=['sender']),
        ]


class Review(models.Model):
    purohit = models.ForeignKey(User,on_delete=models.CASCADE,related_name='reviews')
    jajaman = models.ForeignKey(User,on_delete=models.CASCADE,related_name='given_reviews')
    
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.jajaman.username} --> {self.purohit.username}: {self.rating} stars"

    class Meta:
        unique_together = ('purohit', 'jajaman')
        ordering = ['-created_at']