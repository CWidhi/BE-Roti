from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'harga', HargaViewSet, basename='harga')

urlpatterns = [
    path('', include(router.urls)),
    path('stock/', StockList.as_view(), name='stock-list'),
    path('stock/<int:product_id>', StockDetail.as_view(), name='stock-detail'),
    path('suplier/', SuplierList.as_view(), name='suplier-list'),
    path('suplier/<int:pk>/', SuplierUpdateView.as_view(), name='suplier-update'),
    path('belanja/', BelanjaView.as_view(), name='belanja'),
    path('belanja/<int:pk>/', BelanjaView.as_view(), name='edit-belanja'),
    
    path('products-count/', product_count, name='product-count'),
    path('suplier-count/', suplier_count, name='suplier-count'),
    
    path('transaksi-pengambilan/', TransaksiPengambilanAPIView.as_view(), name='transaksi-pengambilan'),
    path('transaksi-pengambilan/getall', TransaksiPengambilanListView.as_view(), name='transaksi-pengambilan-all'),
    path('transaksi-pengambilan/<int:pk>/konfirmasi/', KonfirmasiTransaksiPengambilanAPIView.as_view(), name='konfirmasi-transaksi-pengambilan'),
    path('transaksi-pengambilan/<int:pk>/', TransaksiPengambilanUpdateView.as_view(), name='edit-transaksi-pengambilan'),
    
    
    path('transaksi-pembayaran/', BayarAPIView.as_view(), name='bayar'),
    path('transaksi-pelunasan/', PelunasanView.as_view(), name='pelunasan'),
    path('transaksi-cicil/', CicilPembayaranView.as_view(), name='cicil'),
]
  