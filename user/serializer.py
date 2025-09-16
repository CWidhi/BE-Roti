from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Personal
from django.db import transaction
from rest_framework import serializers
from .models import Personal
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user 

        if not user.groups.filter(name__in=["admin", "sales"]).exists():
            raise AuthenticationFailed(
                "Anda tidak memiliki izin untuk mengakses Aplikasi ini (harap hubungi admin)."
            )

        group = user.groups.first()
        data['role'] = group.name if group else None 

        return data
 

class RegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True, max_length=13)
    address = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone', 'address', 'first_name', 'last_name']

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        address = validated_data.pop('address')
        password = validated_data.pop('password')
        with transaction.atomic():
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data.get('email', ''),
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', '')
            )
            user.set_password(password)
            user.save()

            Personal.objects.create(
                user=user,
                phone=phone,
                address=address
            )

        return user

class EditUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False, max_length=12)
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    def update(self, instance, validated_data):
        personal = instance.personal  

        if 'email' in validated_data:
            instance.email = validated_data['email']
        
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.save()

        if 'phone' in validated_data:
            personal.phone = validated_data['phone']
            personal.save()

        return instance

class UserDetailSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='personal.phone')
    address = serializers.CharField(source='personal.address')
    groups = serializers.SerializerMethodField()

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'address', 'first_name', 'last_name', 'groups']
    

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']