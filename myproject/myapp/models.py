from django.db import models

# Create your models here.
class DataFile(models.Model):
    file = models.FileField(upload_to='data/')
    uploaded_at = models.DateTimeField(auto_now_add=True)