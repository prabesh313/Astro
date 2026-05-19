import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()
from django.core.files import File
from books.models import Book, BookCategory

# Create categories
cat, _ = BookCategory.objects.get_or_create(name="Karmakanda")

# Folder with your PDFs
PDF_FOLDER = "media/uploads/bulk/"

for filename in os.listdir(PDF_FOLDER):
    if filename.endswith('.pdf'):
        title = filename.replace('.pdf', '').replace('_', ' ')
        filepath = os.path.join(PDF_FOLDER, filename)

        with open(filepath, 'rb') as f:
            book = Book(title=title, category=cat)
            book.file.save(filename, File(f), save=True)
            print(f"Uploaded: {title}")