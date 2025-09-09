from django.db import models
from django.contrib.auth.models import User


class Personal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personal')
    phone = models.CharField(max_length=12)
    address = models.TextField()
