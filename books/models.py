from django.db import models
from rituals.storage import PDFCloudinaryStorage
# Create your models here.
class BookCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Book(models.Model):
    title= models.CharField(max_length=200)
    category = models.ForeignKey(BookCategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='books/pdfs/', storage=PDFCloudinaryStorage())
    cover_image = models.ImageField(upload_to='books/covers/', blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, default='Nepali')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

