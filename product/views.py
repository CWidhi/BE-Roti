from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ItemPengambilan, Product, Harga, Stock, Suplier, ProductInSuplier, Belanja, TransaksiPengambilan, TransaksiPembayaran
from .serializers import (ProductSerializer, HargaSerializer, StockSerializer, HargaProductSerializer,
                          SuplierSerializer, ProductInSuplierSerializer, BelanjaSerializer, TransaksiPengambilanSerializer,
                          TransaksiPengambilanReadSerializer, TransaksiPengambilanUpdateSerializer, TransaksiPengambilanDetailSerializer,
                          BayarSerializer, TransaksiPembayaranSerializer, CicilPembayaranSerializer)
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.generics import UpdateAPIView
from rest_framework.decorators import api_view
from django.db.models import Prefetch
from django.db import transaction


@api_view(['GET'])
def product_count(request):
    count = Product.objects.count()
    return Response({'count': count})
@api_view(['GET'])
def suplier_count(request):
    count = Suplier.objects.count()
    return Response({'count': count})
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_delete=False).prefetch_related('harga_list')
    serializer_class = ProductSerializer
    
    @action(detail=True, methods=['post'], url_path='add-harga')
    def add_harga(self, request, pk=None):
        product = self.get_object()
        serializer = HargaProductSerializer(data=request.data)
        if serializer.is_valid():
            tipe_harga_baru = serializer.validated_data['tipe_harga']
            if product.harga_list.filter(tipe_harga=tipe_harga_baru).exists():
                return Response(
                    {"detail": f"Tipe harga '{tipe_harga_baru}' sudah ada untuk produk ini."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class HargaViewSet(viewsets.ModelViewSet):
    queryset = Harga.objects.all().order_by('-id')
    serializer_class = HargaSerializer
    
    
class StockList(APIView):
    @swagger_auto_schema(responses={200: StockSerializer(many=True)})
    def get(self, request):
        stocks = Stock.objects.all().order_by('-id')
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(request_body=StockSerializer, responses={201: StockSerializer})
    def post(self, request):
        serializer = StockSerializer(data=request.data)
        try:
            product = Product.objects.get(pk=request.data['product_id'])
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        if serializer.is_valid():
            if product.stock is None:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"detail": "Stock sudah ada"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StockDetail(APIView):
    @swagger_auto_schema(request_body=StockSerializer, responses={200: StockSerializer})
    def put(self, request, product_id):
        stock = get_object_or_404(Stock, pk=product_id)
        serializer = StockSerializer(stock, data=request.data)
        try:
            product = Product.objects.get(pk=request.data['product_id'])
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SuplierList(APIView):
    @swagger_auto_schema(responses={200: SuplierSerializer(many=True)})
    def get(self, request):
        supliers = Suplier.objects.all().order_by('-id')
        serializer = SuplierSerializer(supliers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SuplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None):
        try:
            suplier = Suplier.objects.get(pk=pk)
        except Suplier.DoesNotExist:
            return Response({"detail": "Suplier not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SuplierSerializer(suplier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SuplierUpdateView(UpdateAPIView):
    queryset = Suplier.objects.all()
    serializer_class = SuplierSerializer
    
class ProsuctInSuplierView(APIView):
    
    @swagger_auto_schema(responses={200: ProductInSuplierSerializer(many=True)})
    def get(self, request):
        product_in_suplier = ProductInSuplier.objects.all()
        serializer = ProductInSuplierSerializer(product_in_suplier, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ProductInSuplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return Response({"detail": "Produk berhasil dihapus."}, status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, pk=None):
        try:
            product = ProductInSuplier.objects.get(pk=pk)
        except ProductInSuplier.DoesNotExist:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductInSuplierSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BelanjaView(APIView):
    @swagger_auto_schema(responses={200: BelanjaSerializer(many=True)})
    def get(self, request):
        belanja_list = Belanja.objects.all().order_by('-id')
        serializer = BelanjaSerializer(belanja_list, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BelanjaSerializer, responses={201: BelanjaSerializer})
    def post(self, request):
        serializer = BelanjaSerializer(data=request.data)
        if serializer.is_valid():
            belanja = serializer.save()
            return Response(BelanjaSerializer(belanja).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(request_body=BelanjaSerializer, responses={200: BelanjaSerializer})
    def put(self, request, pk=None):
        try:
            belanja = Belanja.objects.get(pk=pk)
        except Belanja.DoesNotExist:
            return Response({"error": "Belanja not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BelanjaSerializer(belanja, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class TransaksiPengambilanAPIView(APIView):
    def post(self, request):
        serializer = TransaksiPengambilanSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            transaksi = serializer.save()
            response_data = TransaksiPengambilanDetailSerializer(transaksi).data
            return Response({
                'status': True,
                'message': 'Transaksi pengambilan berhasil dibuat.',
                'data': response_data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        transaksi = get_object_or_404(TransaksiPengambilan, pk=pk)
        
        serializer = TransaksiPengambilanSerializer(
            transaksi, data=request.data, context={'request': request}
        )
        
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TransaksiPengambilanListView(APIView):
     def get(self, request):
        queryset = TransaksiPengambilan.objects.all().select_related('user', 'jalur').prefetch_related(
            Prefetch('items', queryset=ItemPengambilan.objects.select_related('product'))
        )
        serializer = TransaksiPengambilanReadSerializer(queryset, many=True)
        return Response(serializer.data)

class KonfirmasiTransaksiPengambilanAPIView(APIView):
    def post(self, request, pk):
        transaksi = get_object_or_404(TransaksiPengambilan, pk=pk)

        if transaksi.is_konfirmasi:
            return Response({
                "status": False,
                "message": "Transaksi sudah dikonfirmasi sebelumnya.",
                "data": TransaksiPengambilanDetailSerializer(transaksi).data
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            for item in transaksi.items.all():
                stock = get_object_or_404(Stock, product_id=item.product.id)

                if stock.quantity < item.quantity:
                    return Response({
                        "status": False,
                        "message": f"Stok tidak cukup untuk produk: {item.product.nama}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                stock.quantity -= item.quantity
                stock.save()

            transaksi.is_konfirmasi = True
            transaksi.save()

        return Response({
            "status": True,
            "message": "Transaksi berhasil dikonfirmasi dan stok diperbarui.",
            "data": TransaksiPengambilanDetailSerializer(transaksi).data
        }, status=status.HTTP_200_OK)
        
class TransaksiPengambilanUpdateView(APIView):
    def put(self, request, pk):
        try:
            transaksi = TransaksiPengambilan.objects.get(pk=pk)
        except TransaksiPengambilan.DoesNotExist:
            return Response({"detail": "Transaksi tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TransaksiPengambilanUpdateSerializer(transaksi, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, 
                             "message": "Transaksi berhasil diperbarui",
                             "data": TransaksiPengambilanDetailSerializer(transaksi).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class BayarAPIView(APIView):
    def post(self, request):
        serializer = BayarSerializer(data=request.data)
        if serializer.is_valid():
            pembayaran = serializer.save()
            return Response(TransaksiPembayaranSerializer(pembayaran).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PelunasanView(APIView):
    def post(self, request, *args, **kwargs):
        pembayaran_id = request.data.get("pembayaran_id")
        pembayaran = get_object_or_404(TransaksiPembayaran, id=pembayaran_id)

        # hitung sisa kekurangan
        sisa = pembayaran.total_pengambilan - pembayaran.jumlah_dibayar

        if sisa <= 0:
            return Response({"detail": "Pembayaran sudah lunas"}, status=status.HTTP_400_BAD_REQUEST)

        # langsung lunasi
        pembayaran.jumlah_dibayar = pembayaran.total_pengambilan
        pembayaran.kekurangan_bayar = 0
        pembayaran.status_pembayaran = "lunas"
        pembayaran.save()

        return Response(TransaksiPembayaranSerializer(pembayaran).data, status=status.HTTP_200_OK)
    
class CicilPembayaranView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CicilPembayaranSerializer(data=request.data)
        if serializer.is_valid():
            pembayaran = serializer.save()
            return Response({
                "message": "Cicilan berhasil ditambahkan",
                "pembayaran_id": pembayaran.id,
                "jumlah_dibayar": pembayaran.jumlah_dibayar,
                "kekurangan_bayar": pembayaran.kekurangan_bayar,
                "status_pembayaran": pembayaran.status_pembayaran,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)