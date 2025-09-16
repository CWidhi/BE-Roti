from toko.models import Toko, Jalur
from rest_framework.response import Response
from toko.serializers import TokoSerializer, JalurSerializer, AssignJalurM2MSerializer, RemoveJalurFromUserSerializer
from rest_framework.views import APIView
from rest_framework import status
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User


# Create your views here.
class TokoList(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(responses={200: TokoSerializer(many=True)})
    def get(self, request):
        toko = Toko.objects.all().order_by('-id')
        serializer = TokoSerializer(toko, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=TokoSerializer, responses={201: TokoSerializer})
    def post(self, request):
        serializer = TokoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TokoDetail(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, toko_id):
        try:
            return Toko.objects.get(pk=toko_id)
        except Toko.DoesNotExist:
            raise Http404

    def get(self, request, toko_id):
        if not request.user.groups.filter(name__in=["admin", "sales"]).exists():
            return Response(
                {"detail": "Anda tidak memiliki izin untuk mengakses data ini."},
                status=status.HTTP_403_FORBIDDEN
            )
        toko = self.get_object(toko_id)
        serializer = TokoSerializer(toko)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=TokoSerializer, responses={200: TokoSerializer})
    def put(self, request, toko_id):
        if not request.user.groups.filter(name__in=["admin"]).exists():
            return Response(
                {"detail": "Anda tidak memiliki izin untuk mengakses data ini."},
                status=status.HTTP_403_FORBIDDEN
            )
        toko = self.get_object(toko_id)
        serializer = TokoSerializer(toko, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, toko_id):
        if not request.user.groups.filter(name__in=["admin"]).exists():
            return Response(
                {"detail": "Anda tidak memiliki izin untuk mengakses data ini."},
                status=status.HTTP_403_FORBIDDEN
            )
        toko = self.get_object(toko_id)
        toko.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class JalurList(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(responses={200: JalurSerializer(many=True)})
    def get(self, request):
        if request.user.groups.filter(name__in=["admin"]).exists():
            jalur = Jalur.objects.all().order_by('-id')
        elif request.user.groups.filter(name__in=["sales"]).exists():
            jalur = Jalur.objects.filter(users=request.user).order_by('-id')
        else:
            return Response(
                {"detail": "Anda tidak memiliki izin untuk mengakses data ini."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = JalurSerializer(jalur, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if not request.user.groups.filter(name__in=["admin"]).exists():
            return Response(
                {"detail": "Anda tidak memiliki izin untuk mengakses data ini."},
                status=status.HTTP_403_FORBIDDEN
            )
        nama_jalur = request.data.get('nama')
        if Jalur.objects.filter(nama__iexact=nama_jalur).exists():
            return Response({"detail": "Nama jalur sudah ada"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = JalurSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None):
        if not request.user.groups.filter(name__in=["admin"]).exists():
            return Response(
                {"detail": "Anda tidak memiliki izin untuk mengakses data ini."},
                status=status.HTTP_403_FORBIDDEN
            )
        jalur = Jalur.objects.get(pk=pk)
        serializer = JalurSerializer(jalur, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssignJalurM2MView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AssignJalurM2MSerializer(data=request.data)
        if not request.user.groups.filter(name__in=["admin"]).exists():
            return Response(
                {"detail": "Anda tidak memiliki izin untuk mengakses data ini."},
                status=status.HTTP_403_FORBIDDEN
            )
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Jalur berhasil ditambahkan ke user.",
                "user_id": user.id,
                "username": user.username,
                "jalur_ids": [jalur.id for jalur in user.jalur_list.all()],
                "jalur_names": [jalur.nama for jalur in user.jalur_list.all()],
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RemoveJalurFromUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = RemoveJalurFromUserSerializer(data=request.data)
        if not request.user.groups.filter(name__in=["admin"]).exists():
            return Response(
                {"detail": "Anda tidak memiliki izin untuk mengakses data ini."},
                status=status.HTTP_403_FORBIDDEN
            )
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Jalur berhasil dihapus dari user."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_jalur(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User tidak ditemukan"}, status=404)

    jalur = user.jalur_list.all()  # relasi ManyToMany
    serializer = JalurSerializer(jalur, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_jalur_count(request):
    if request.user.groups.filter(name__in=["admin"]).exists():
        count = Jalur.objects.all().count()
    elif request.user.groups.filter(name__in=["sales"]).exists():
        count = Jalur.objects.filter(users=request.user).count()
    else:
        count = 0
    return Response({'count': count})