from django.db import models
from users.models import UserProfile

# Create your models here.
class Kundali(models.Model):
    user_profile= models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    chart_data= models.JSONField()
    generated_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Kundali of {self.user_profile.full_name}"
    

class Panchanga(models.Model):
    date=models.DateField(unique=True)
    data= models.JSONField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Panchanga for {self.date}"
    

