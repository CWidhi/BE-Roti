from django.contrib import admin
from .models import (
    Product, Harga, Stock, Suplier, ProductInSuplier,
    Belanja, ItemBelanja,
    TransaksiPengambilan, ItemPengambilan,
    TransaksiPembayaran, ItemPembayaran
)

# Inline Harga di Product
class HargaInline(admin.TabularInline):
    model = Harga
    extra = 1
    
    def get_max_num(self, request, obj=None, **kwargs):
        return 8 


# Inline Stock di Product (karena OneToOne)
class StockInline(admin.StackedInline):
    model = Stock
    extra = 0
    can_delete = False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nama', 'is_delete', 'created_at', 'updated_at')
    search_fields = ('nama',)
    inlines = [HargaInline, StockInline]


@admin.register(Suplier)
class SuplierAdmin(admin.ModelAdmin):
    list_display = ( 'pt', 'nama', 'telepon', 'is_aktif')
    search_fields = ('pt', 'nama')


@admin.register(ProductInSuplier)
class ProductInSuplierAdmin(admin.ModelAdmin):
    list_display = ( 'product', 'suplier', 'jumlah_belanja', 'quantity', 'tanggal_belanja')
    search_fields = ('product__nama', 'suplier__nama')


# Inline ItemBelanja di Belanja
class ItemBelanjaInline(admin.TabularInline):
    model = ItemBelanja
    extra = 1


@admin.register(Belanja)
class BelanjaAdmin(admin.ModelAdmin):
    list_display = ( 'suplier', 'tanggal_belanja', 'total_belanja')
    search_fields = ('suplier__nama',)
    inlines = [ItemBelanjaInline]


# Inline ItemPengambilan di TransaksiPengambilan
class ItemPengambilanInline(admin.TabularInline):
    model = ItemPengambilan
    extra = 1


@admin.register(TransaksiPengambilan)
class TransaksiPengambilanAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'jalur', 'tanggal_pengambilan', 'total_pengambilan', 'is_konfirmasi')
    search_fields = ('user__username', 'jalur__nama')
    inlines = [ItemPengambilanInline]


# Inline ItemPembayaran di TransaksiPembayaran
class ItemPembayaranInline(admin.TabularInline):
    model = ItemPembayaran
    extra = 1


@admin.register(TransaksiPembayaran)
class TransaksiPembayaranAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'jalur', 'tanggal_pembayaran', 'total_pengambilan', 'jumlah_dibayar', 'kekurangan_bayar', 'status_pembayaran')
    list_filter = ('status_pembayaran', 'tanggal_pembayaran')
    search_fields = ('user__username', 'jalur__nama')
    inlines = [ItemPembayaranInline]
