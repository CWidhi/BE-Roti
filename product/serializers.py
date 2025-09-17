from rest_framework import serializers
from .models import (Product, Harga, Stock, Suplier, 
                    ProductInSuplier, Belanja, ItemBelanja,
                    ItemPengambilan, TransaksiPengambilan,
                    ItemPembayaran, TransaksiPembayaran)
from toko.models import Jalur
from django.db import transaction
from django.contrib.auth.models import User


class HargaSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_nama = serializers.CharField(source='product.nama', read_only=True)
    class Meta:
        model = Harga
        fields = ['id', 'tipe_harga', 'harga', 'product', 'product_nama']
        
    def validate(self, attrs):
        tipe_harga = attrs['tipe_harga']
        harga = attrs['harga']
        product = attrs['product']

        existing_qs = Harga.objects.filter(tipe_harga=tipe_harga, product=product)

        if self.instance:
            existing_qs = existing_qs.exclude(id=self.instance.id)

        if existing_qs.exists():
            raise serializers.ValidationError(f"Tipe harga '{tipe_harga}' sudah ada untuk produk ini.")

        return attrs

        
class HargaProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harga
        fields = ['id', 'tipe_harga', 'harga']
        
class StockSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Stock
        fields = ['product_id', 'quantity']
        
class SuplierSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    pt = serializers.CharField(required = True, allow_blank = False, max_length = 20)
    nama = serializers.CharField(required = True, allow_blank = False, max_length = 20)
    alamat =serializers.CharField(required = True, allow_blank = False, max_length = 50)
    telepon = serializers.CharField(required = True)
    
    class Meta:
        model = Product
        fields = ['id', 'pt', 'nama', 'alamat', 'telepon']

    
    def validate(self, attrs):
        pt = attrs.get('pt')
        nama = attrs.get('nama')
        if self is None:
            if Suplier.objects.filter(pt=pt).exists():
                raise serializers.ValidationError("PT sudah ada")
            if Suplier.objects.filter(nama=nama).exists():
                raise serializers.ValidationError("Nama sudah ada")
        return attrs
    
    def create(self, validated_data):
        return Suplier.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        
        instance.pt = validated_data.get('pt', instance.pt)
        instance.nama = validated_data.get('nama', instance.nama)
        instance.alamat = validated_data.get('alamat', instance.alamat)
        instance.telepon = validated_data.get('telepon', instance.telepon)
        instance.save()
        return instance

class ProductSerializer(serializers.ModelSerializer):
    harga_list = HargaProductSerializer(many=True)
    stock = StockSerializer(read_only=True) 
  
    class Meta:
        model = Product
        fields = ['id', 'nama', 'foto_product', 'harga_list', 'stock']

    def validate_harga_list(self, value):
        if not value:
            raise serializers.ValidationError("Minimal harus ada satu harga.")

        tipe_harga_set = set()
        for item in value:
            tipe = item.get('tipe_harga')
            if tipe in tipe_harga_set:
                raise serializers.ValidationError(f"Tipe harga '{tipe}' tidak boleh duplikat.")
            tipe_harga_set.add(tipe)

        return value

    def create(self, validated_data):
        harga_data = validated_data.pop('harga_list')
        product = Product.objects.create(**validated_data)
        Stock.objects.create(product_id=product, quantity = 0)
        for harga in harga_data:
            Harga.objects.create(product=product, **harga)
        return product
    
class ProductInSuplierSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    jumlah_belanja = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    tanggal_belanja = serializers.DateField(read_only=True)
    product = ProductSerializer(read_only=True)
    suplier = SuplierSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')
    suplier_id = serializers.PrimaryKeyRelatedField(queryset=Suplier.objects.all(), write_only=True, source='suplier')
    
    def validate(self, attrs):
        jumlah_belanja = attrs.get('jumlah_belanja')
        quantity = attrs.get('quantity')
        if jumlah_belanja is None or quantity is None:
            raise serializers.ValidationError("Jumlah belanja atau quantity harus diisi.")
        return attrs
    
    class Meta:
        model = ProductInSuplier
        fields = ['id', 'product', 'product_id', 'suplier', 'suplier_id', 'jumlah_belanja', 'quantity', 'tanggal_belanja']
        
    def create(self, validated_data):
        product_in_suplier = ProductInSuplier.objects.create(**validated_data)
        product = product_in_suplier.product
        try:
            stock = Stock.objects.get(product_id=product)
        except Stock.DoesNotExist:
            stock = Stock.objects.create(product_id=product, quantity=0)

        stock.quantity += product_in_suplier.quantity
        stock.save()

        return product_in_suplier
    

class ItemBelanjaSerializer(serializers.ModelSerializer):
    product_nama = serializers.CharField(source='product.nama', read_only=True)

    class Meta:
        model = ItemBelanja
        fields = ['id', 'product', 'product_nama', 'jumlah_belanja', 'quantity']


class BelanjaSerializer(serializers.ModelSerializer):
    items = ItemBelanjaSerializer(many=True)

    class Meta:
        model = Belanja
        fields = ['id', 'suplier', 'total_belanja','tanggal_belanja', 'items']
        
    def validate(self, data):
        items = data.get('items', [])
        total_dari_items = sum([item['jumlah_belanja'] for item in items])
        if 'total_belanja' in data and data['total_belanja'] != total_dari_items:
            raise serializers.ValidationError("Total belanja tidak sesuai dengan jumlah item.")
        return data


    def create(self, validated_data):
        items_data = validated_data.pop('items')
        belanja = Belanja.objects.create(**validated_data)

        for item in items_data:
            item_obj = ItemBelanja.objects.create(belanja=belanja, **item)

            product = item['product']
            stock, _ = Stock.objects.get_or_create(product_id=product)
            stock.quantity += item['quantity']
            stock.save()

        return belanja

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')

        instance.suplier = validated_data.get('suplier', instance.suplier)
        instance.tanggal_belanja = validated_data.get('tanggal_belanja', instance.tanggal_belanja)
        instance.total_belanja = validated_data.get('total_belanja', instance.total_belanja)
        instance.save()

        # 1. Revert stock quantity dari item lama
        for item in instance.items.all():
            stock = Stock.objects.filter(product_id=item.product).first()
            if stock:
                stock.quantity -= item.quantity
                stock.save()

        # 2. Delete all old item belanja
        instance.items.all().delete()

        # 3. Create item baru dan update stock-nya
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            # Create ItemBelanja baru
            ItemBelanja.objects.create(belanja=instance, **item_data)

            # Tambahkan quantity ke Stock
            stock, created = Stock.objects.get_or_create(product_id=product)
            stock.quantity += quantity
            stock.save()

        return instance

class ItemPengambilanDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.nama', read_only=True)

    class Meta:
        model = ItemPengambilan
        fields = ['id', 'product', 'product_name', 'quantity', 'harga_satuan', 'subtotal']


class TransaksiPengambilanDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    jalur = serializers.StringRelatedField()
    items = ItemPengambilanDetailSerializer(many=True, source='items.all')

    class Meta:
        model = TransaksiPengambilan
        fields = ['id', 'user', 'jalur', 'tanggal_pengambilan', 'total_pengambilan', 'items']


class ItemPengambilanCreateSerializer(serializers.ModelSerializer):
    tipe_harga = serializers.CharField()
    
    class Meta:
        model = ItemPengambilan
        fields = ['product', 'quantity', 'tipe_harga']
        
class TransaksiPengambilanSerializer(serializers.Serializer):
    # sales = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    jalur = serializers.PrimaryKeyRelatedField(queryset=Jalur.objects.all())
    items = ItemPengambilanCreateSerializer(many=True)

    def validate_sales(self, sales_user):
        if not sales_user.groups.filter(name='sales').exists():
            raise serializers.ValidationError("User yang dipilih bukan sales.")
        return sales_user

    def create(self, validated_data):
        request = self.context.get('request')
        sales = request.user
        jalur = validated_data['jalur']
        items_data = validated_data['items']

        with transaction.atomic():
            transaksi = TransaksiPengambilan.objects.create(user=sales, jalur=jalur)
            total = 0

            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                tipe_harga = item_data['tipe_harga']

                try:
                    stock = Stock.objects.select_for_update().get(product_id=product)
                except Stock.DoesNotExist:
                    raise serializers.ValidationError(f"Stok untuk produk '{product.nama}' tidak ditemukan.")

                if stock.quantity < quantity:
                    raise serializers.ValidationError(f"Stok tidak mencukupi untuk produk '{product.nama}'. Sisa stok: {stock.quantity}")

                harga = Harga.objects.filter(
                    product=product,
                    tipe_harga=tipe_harga,
                    is_delete=False
                ).order_by('tipe_harga').first()

                harga_satuan = harga.harga if harga else 0
                subtotal = harga_satuan * quantity

                item_pengambilan = ItemPengambilan.objects.create(
                    transaksi=transaksi,
                    product=product,
                    quantity=quantity,
                    harga_satuan=harga_satuan,
                    subtotal=subtotal
                )

                stock.quantity -= quantity
                stock.save()

                total += subtotal

            transaksi.total_pengambilan = total
            transaksi.save()

            transaksi_pembayaran = TransaksiPembayaran.objects.create(
                user=sales,
                jalur=jalur,
                total_pengambilan=total,
                jumlah_dibayar=0,
                status_pembayaran='belum dibayar'
            )

            for item_pengambilan in transaksi.items.all():
                ItemPembayaran.objects.create(
                    transaksi_pembayaran=transaksi_pembayaran,
                    item_pengambilan=item_pengambilan,
                    quantity=item_pengambilan.quantity,
                    harga_satuan=item_pengambilan.harga_satuan,
                    subtotal=item_pengambilan.subtotal
                )

            return transaksi


class ItemPengambilanReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.nama', read_only=True)

    class Meta:
        model = ItemPengambilan
        fields = ['id', 'product', 'product_name', 'quantity', 'harga_satuan', 'subtotal']


class TransaksiPengambilanReadSerializer(serializers.ModelSerializer):
    sales_name = serializers.CharField(source='user.username', read_only=True)
    jalur_name = serializers.CharField(source='jalur.nama', read_only=True)
    items = ItemPengambilanReadSerializer(many=True, read_only=True)

    class Meta:
        model = TransaksiPengambilan
        fields = ['id', 'sales_name', 'jalur_name', 'tanggal_pengambilan', 'total_pengambilan', 'is_konfirmasi', 'items']


class ItemPengambilanUpdateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()
    tipe_harga = serializers.CharField()


class TransaksiPengambilanUpdateSerializer(serializers.Serializer):
    sales = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    jalur = serializers.PrimaryKeyRelatedField(queryset=Jalur.objects.all())
    items = ItemPengambilanCreateSerializer(many=True)

    def validate_sales(self, sales_user):
        if not sales_user.groups.filter(name='sales').exists():
            raise serializers.ValidationError("User yang dipilih bukan sales.")
        return sales_user
    
class ItemPengambilanUpdateSerializer(serializers.ModelSerializer):
    tipe_harga = serializers.CharField()
    
    class Meta:
        model = ItemPengambilan
        fields = ['product', 'quantity', 'tipe_harga']

class TransaksiPengambilanUpdateSerializer(serializers.Serializer):
    sales = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    jalur = serializers.PrimaryKeyRelatedField(queryset=Jalur.objects.all())
    items = ItemPengambilanUpdateSerializer(many=True)

    def validate_sales(self, sales_user):
        if not sales_user.groups.filter(name='sales').exists():
            raise serializers.ValidationError("User yang dipilih bukan sales.")
        return sales_user

    def update(self, instance, validated_data):
        if instance.is_konfirmasi:
            raise serializers.ValidationError("Transaksi yang sudah dikonfirmasi tidak dapat diupdate.")

        sales = validated_data['sales']
        jalur = validated_data['jalur']
        items_data = validated_data['items']

        with transaction.atomic():
            instance.user = sales
            instance.jalur = jalur
            instance.save()

            total_pengambilan = 0
            existing_items = {item.id: item for item in instance.items.all()}
            request_item_ids = [item.get('id') for item in items_data if item.get('id') is not None]

            # Hapus item yang tidak ada lagi di request
            for item_id, item in existing_items.items():
                if item_id not in request_item_ids:
                    stock = Stock.objects.select_for_update().get(product_id=item.product.id)
                    stock.quantity += item.quantity
                    stock.save()

                    ItemPembayaran.objects.filter(item_pengambilan=item).delete()
                    item.delete()

            for item_data in items_data:
                item_id = item_data.get('id')
                product = item_data['product']
                quantity = item_data['quantity']
                tipe_harga = item_data['tipe_harga']

                harga = Harga.objects.filter(
                    product=product,
                    tipe_harga=tipe_harga,
                    is_delete=False
                ).order_by('tipe_harga').first()

                harga_satuan = harga.harga if harga else 0
                subtotal = harga_satuan * quantity

                stock = Stock.objects.select_for_update().get(product_id=product.id)

                if item_id and item_id in existing_items:
                    # Update item yang sudah ada
                    item = existing_items[item_id]
                    if item.product.id != product.id:
                        raise serializers.ValidationError("Produk tidak boleh diganti pada item yang sudah ada.")

                    selisih = quantity - item.quantity
                    if selisih > 0 and stock.quantity < selisih:
                        raise serializers.ValidationError(
                            f"Stok tidak mencukupi untuk produk '{product.nama}'. Sisa stok: {stock.quantity}"
                        )

                    stock.quantity -= selisih
                    stock.save()

                    item.quantity = quantity
                    item.harga_satuan = harga_satuan
                    item.subtotal = subtotal
                    item.save()
                else:
                    # Tambah item baru
                    if stock.quantity < quantity:
                        raise serializers.ValidationError(
                            f"Stok tidak mencukupi untuk produk '{product.nama}'. Sisa stok: {stock.quantity}"
                        )

                    ItemPengambilan.objects.create(
                        transaksi=instance,
                        product=product,
                        quantity=quantity,
                        harga_satuan=harga_satuan,
                        subtotal=subtotal
                    )
                    stock.quantity -= quantity
                    stock.save()

                total_pengambilan += subtotal

            instance.total_pengambilan = total_pengambilan
            instance.save()

            # Transaksi Pembayaran
            transaksi_pembayaran, _ = TransaksiPembayaran.objects.get_or_create(
                user=sales,
                jalur=jalur,
                tanggal_pembayaran=instance.tanggal_pengambilan,
                defaults={
                    'total_pengambilan': total_pengambilan,
                    'jumlah_dibayar': 0,
                    'status_pembayaran': 'belum dibayar',
                }
            )
            if not transaksi_pembayaran._state.adding:
                transaksi_pembayaran.total_pengambilan = total_pengambilan
                transaksi_pembayaran.save()

            # Update ulang ItemPembayaran
            transaksi_pembayaran.items.all().delete()
            for item in instance.items.all():
                ItemPembayaran.objects.create(
                    transaksi_pembayaran=transaksi_pembayaran,
                    item_pengambilan=item,
                    quantity=item.quantity,
                    harga_satuan=item.harga_satuan,
                    subtotal=item.subtotal
                )

            return instance

class ItemPembayaranSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPembayaran
        fields = ["id", "item_pengambilan", "quantity", "harga_satuan", "subtotal"]


class TransaksiPembayaranSerializer(serializers.ModelSerializer):
    items = ItemPembayaranSerializer(many=True, read_only=True)

    class Meta:
        model = TransaksiPembayaran
        fields = [
            "id",
            "user",
            "jalur",
            "tanggal_pembayaran",
            "total_pengambilan",
            "jumlah_dibayar",
            "kekurangan_bayar",
            "status_pembayaran",
            "items",
        ]


class BayarSerializer(serializers.Serializer):
    pembayaran_id = serializers.IntegerField()
    jumlah_dibayar = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate(self, data):
        try:
            pembayaran = TransaksiPembayaran.objects.get(id=data["pembayaran_id"])
        except TransaksiPembayaran.DoesNotExist:
            raise serializers.ValidationError("Transaksi pembayaran tidak ditemukan")

        data["pembayaran"] = pembayaran
        return data

    def save(self, **kwargs):
        pembayaran = self.validated_data["pembayaran"]
        jumlah_dibayar = self.validated_data["jumlah_dibayar"]

        # update jumlah dibayar
        pembayaran.jumlah_dibayar += jumlah_dibayar

        # hitung kekurangan
        pembayaran.kekurangan_bayar = pembayaran.total_pengambilan - pembayaran.jumlah_dibayar

        # tentukan status
        if pembayaran.jumlah_dibayar <= 0:
            pembayaran.status_pembayaran = "belum dibayar"
        elif 0 < pembayaran.jumlah_dibayar < pembayaran.total_pengambilan:
            pembayaran.status_pembayaran = "belum lunas"
        elif pembayaran.jumlah_dibayar >= pembayaran.total_pengambilan:
            pembayaran.status_pembayaran = "lunas"
            pembayaran.kekurangan_bayar = 0

        pembayaran.save()
        return pembayaran
    
    
class CicilPembayaranSerializer(serializers.Serializer):
    pembayaran_id = serializers.IntegerField()
    jumlah_dibayar = serializers.IntegerField()

    def validate(self, data):
        if data["jumlah_dibayar"] <= 0:
            raise serializers.ValidationError("Jumlah dibayar harus lebih dari 0")
        return data

    def save(self, **kwargs):
        pembayaran_id = self.validated_data["pembayaran_id"]
        jumlah_dibayar = self.validated_data["jumlah_dibayar"]

        try:
            pembayaran = TransaksiPembayaran.objects.get(id=pembayaran_id)
        except TransaksiPembayaran.DoesNotExist:
            raise serializers.ValidationError("Transaksi pembayaran tidak ditemukan")

        # Tambahkan cicilan
        pembayaran.jumlah_dibayar += jumlah_dibayar
        pembayaran.kekurangan_bayar = pembayaran.total_pengambilan - pembayaran.jumlah_dibayar

        # Tidak boleh minus
        if pembayaran.kekurangan_bayar < 0:
            pembayaran.kekurangan_bayar = 0
            pembayaran.jumlah_dibayar = pembayaran.total_pengambilan

        # Tentukan status
        if pembayaran.jumlah_dibayar >= pembayaran.total_pengambilan:
            pembayaran.status_pembayaran = "lunas"
        elif pembayaran.jumlah_dibayar > 0:
            pembayaran.status_pembayaran = "belum lunas"
        else:
            pembayaran.status_pembayaran = "belum dibayar"

        pembayaran.save()
        return pembayaran