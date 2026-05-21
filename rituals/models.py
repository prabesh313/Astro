from django.db import models
from rituals.storage import AudioCloudinaryStorage


# Create your models here.
class Mantra(models.Model):
    name= models.CharField(max_length=200)
    text= models.TextField()
    meaning= models.TextField(blank=True)
    audio = models.FileField(upload_to='mantras/audio/',storage=AudioCloudinaryStorage(),blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, default='Sanskrit')

    def __str__(self):
        return self.name
    
class Ritual(models.Model):
    name= models.CharField(max_length=200)
    description= models.TextField()
    steps= models.JSONField()
    required_items=models.JSONField()
    mantras=models.ManyToManyField(Mantra, blank=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    category=models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
    
