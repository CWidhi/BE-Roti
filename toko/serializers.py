from rest_framework import serializers
from toko.models import Toko, Jalur
from django.contrib.auth.models import User

class TokoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nama = serializers.CharField(required=True, allow_blank=True, max_length=20)
    koordinat = serializers.CharField(required = True, allow_blank = False, max_length = 100)
    alamat =serializers.CharField(required = True, allow_blank = False, max_length = 100)
    telepon = serializers.CharField(required = True)
    is_pasar = serializers.BooleanField(required=False)
    jalur = serializers.PrimaryKeyRelatedField(queryset=Jalur.objects.all())
    
    
    def create(self, validated_data):
         return Toko.objects.create(**validated_data)
     
    def update(self, instance, validated_data):
        
        instance.nama = validated_data.get('nama', instance.nama)
        instance.koordinat = validated_data.get('koordinat', instance.koordinat)
        instance.alamat = validated_data.get('alamat', instance.alamat)
        instance.telepon = validated_data.get('telepon', instance.telepon)
        instance.jalur = validated_data.get('jalur', instance.jalur)
        instance.is_pasar = validated_data.get('is_pasar', instance.is_pasar)
        instance.save()
        return instance
    
class JalurSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nama = serializers.CharField(required=True, allow_blank=True, max_length=20)
    toko_list =serializers.SerializerMethodField()
    
    def get_toko_list(self, obj):
        return TokoSerializer(Toko.objects.filter(jalur=obj), many=True).data
    
    def create(self, validated_data):
         return Jalur.objects.create(**validated_data)
     
    def update(self, instance, validated_data):
        
        instance.nama = validated_data.get('nama', instance.nama)
        instance.save()
        return instance
    
class AssignJalurM2MSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    jalur_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )

    def validate(self, attrs):
        try:
            attrs['user'] = User.objects.get(pk=attrs['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User tidak ditemukan.")

        jalur_queryset = Jalur.objects.filter(pk__in=attrs['jalur_ids'])
        if jalur_queryset.count() != len(attrs['jalur_ids']):
            raise serializers.ValidationError("Salah satu jalur tidak ditemukan.")

        attrs['jalur_list'] = jalur_queryset
        return attrs
    
    def create(self, validated_data):
        user = validated_data['user']
        jalur_list = validated_data['jalur_list']
        user.jalur_list.add(*jalur_list) 
        return user
    
class RemoveJalurFromUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    jalur_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False, required=True
    )

    def to_internal_value(self, data):
        # Normalisasi agar jalur_ids bisa single atau list
        if isinstance(data.get('jalur_ids'), int):
            data['jalur_ids'] = [data['jalur_ids']]
        return super().to_internal_value(data)

    def validate(self, attrs):
        try:
            attrs['user'] = User.objects.get(pk=attrs['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User tidak ditemukan.")

        jalur_queryset = Jalur.objects.filter(pk__in=attrs['jalur_ids'])
        if jalur_queryset.count() != len(attrs['jalur_ids']):
            raise serializers.ValidationError("Salah satu jalur tidak ditemukan.")

        attrs['jalur_list'] = jalur_queryset
        return attrs

    def save(self):
        user = self.validated_data['user']
        jalur_list = self.validated_data['jalur_list']
        user.jalur_list.remove(*jalur_list)
        return user