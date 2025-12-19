import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_recognization_notes_app.settings')
django.setup()

from django.contrib.auth.models import User

users = User.objects.all()
count = users.count()
users.delete()
print(f"Deleted {count} users.")
