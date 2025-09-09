from django.db import models
from toko.models import Jalur
from django.contrib.auth.models import User, Group

# Create your models here.
class baseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True 

class Product(baseModel):
    nama = models.CharField(max_length=30)
    foto_product = models.URLField(max_length=600)
    is_delete = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nama
    
class Harga(baseModel):
    TIPE_HARGA_CHOICES = [
        ('Harga pabrik', 'Harga pabrik'),
        ('Harga ke pasar', 'Harga ke pasar'),
        ('Harga di pasar', 'Harga di pasar'),
        ('Harga ke toko', 'Harga ke toko'),
        ('Harga di toko', 'Harga di toko'),
        ('Harga BS pasar', 'Harga BS pasar'),
        ('Harga BS toko', 'Harga BS toko'),
        ('Harga Ecer', 'Harga Ecer'),
    ]
    tipe_harga = models.CharField(max_length=20, choices=TIPE_HARGA_CHOICES, null= False)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    is_delete = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='harga_list')
    class Meta:
        unique_together = ('product', 'tipe_harga')

class Stock(baseModel):
    quantity = models.IntegerField(default= 0)
    product_id = models.OneToOneField(Product, on_delete= models.CASCADE, primary_key=True)
    
    
class Suplier(baseModel):
    pt = models.CharField(max_length= 20)
    nama = models.CharField(max_length= 20)
    alamat = models.CharField(max_length= 50)
    telepon = models.CharField(max_length=13)
    is_aktif = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.pt} - {self.nama}"
    
class ProductInSuplier(baseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_list')
    suplier = models.ForeignKey(Suplier, on_delete=models.CASCADE, related_name='suplier_list')
    jumlah_belanja = models.DecimalField(max_digits=10, decimal_places=2)
    tanggal_belanja = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(default= 0)
    
class Belanja(models.Model):
    suplier = models.ForeignKey(Suplier, on_delete=models.CASCADE)
    tanggal_belanja = models.DateField(auto_now_add=True)
    total_belanja = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class ItemBelanja(models.Model):
    belanja = models.ForeignKey(Belanja, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    jumlah_belanja = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    
class TransaksiPengambilan(baseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jalur = models.ForeignKey(Jalur, on_delete=models.CASCADE)
    tanggal_pengambilan = models.DateField(auto_now_add=True)
    total_pengambilan = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_konfirmasi = models.BooleanField(default=False)

class ItemPengambilan(models.Model):
    transaksi = models.ForeignKey(TransaksiPengambilan, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    harga_satuan = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    def __str__(self):
        return f"{self.product.nama}"
    
STATUS_PEMBAYARAN = [
    ('belum dibayar', 'Belum Dibayar'),
    ('belum lunas', 'Belum Lunas'),
    ('lunas', 'Lunas'),
]

class TransaksiPembayaran(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jalur = models.ForeignKey(Jalur, on_delete=models.CASCADE)
    tanggal_pembayaran = models.DateField(auto_now_add=True)
    total_pengambilan = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    jumlah_dibayar = models.DecimalField(max_digits=12, decimal_places=2)
    kekurangan_bayar = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status_pembayaran = models.CharField(max_length=20, choices=STATUS_PEMBAYARAN, default='belum dibayar')

    def save(self, *args, **kwargs):
        if self.status_pembayaran == 'lunas':
            self.kekurangan_bayar = 0
            
        self.kekurangan_bayar = self.total_pengambilan - self.jumlah_dibayar
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pembayaran {self.id} - {self.user.username}"


class ItemPembayaran(models.Model):
    transaksi_pembayaran = models.ForeignKey(TransaksiPembayaran, related_name='items', on_delete=models.CASCADE)
    item_pengambilan = models.ForeignKey('ItemPengambilan', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    harga_satuan = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.harga_satuan
        super().save(*args, **kwargs)