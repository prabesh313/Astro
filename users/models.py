from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class UserProfile(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    full_name= models.CharField(max_length=200)
    birth_place = models.CharField(max_length=100)
    birth_date=models.DateField()
    birth_time=models.TimeField()
    birth_longitude= models.FloatField(null=True, blank=True)
    birth_latitide=models.FloatField(null=True, blank=True)

    def __str__ (self):
        return self.full_name
