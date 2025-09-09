from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Jalur(models.Model):
    users = models.ManyToManyField(User, related_name='jalur_list', blank=True)
    nama = models.CharField(max_length= 20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nama
class Toko(models.Model):
    nama = models.CharField(max_length= 20)
    alamat = models.CharField(max_length= 50)
    koordinat = models.CharField(max_length=100)
    telepon = models.CharField(max_length=13)
    is_pasar = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    jalur = models.ForeignKey(Jalur, on_delete=models.CASCADE, related_name='toko_list')
    
