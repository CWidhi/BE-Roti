from toko.models import Toko, Jalur
from rest_framework.response import Response
from toko.serializers import TokoSerializer, JalurSerializer, AssignJalurM2MSerializer, RemoveJalurFromUserSerializer
from rest_framework.views import APIView
from rest_framework import status
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema


# Create your views here.
class TokoList(APIView):
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
    def get_object(self, toko_id):
        try:
            return Toko.objects.get(pk=toko_id)
        except Toko.DoesNotExist:
            raise Http404

    def get(self, request, toko_id):
        toko = self.get_object(toko_id)
        serializer = TokoSerializer(toko)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=TokoSerializer, responses={200: TokoSerializer})
    def put(self, request, toko_id):
        toko = self.get_object(toko_id)
        serializer = TokoSerializer(toko, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, toko_id):
        toko = self.get_object(toko_id)
        toko.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class JalurList(APIView):
    @swagger_auto_schema(responses={200: JalurSerializer(many=True)})
    def get(self, request):
        jalur = Jalur.objects.all().order_by('-id')
        serializer = JalurSerializer(jalur, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        nama_jalur = request.data.get('nama')
        if Jalur.objects.filter(nama__iexact=nama_jalur).exists():
            return Response({"detail": "Nama jalur sudah ada"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = JalurSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None):
        jalur = Jalur.objects.get(pk=pk)
        serializer = JalurSerializer(jalur, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssignJalurM2MView(APIView):

    def post(self, request):
        serializer = AssignJalurM2MSerializer(data=request.data)
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
    def post(self, request, *args, **kwargs):
        serializer = RemoveJalurFromUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Jalur berhasil dihapus dari user."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)