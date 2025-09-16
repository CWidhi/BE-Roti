from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import RegisterSerializer, EditUserSerializer, UserDetailSerializer, GroupSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view

from rest_framework_simplejwt.views import TokenObtainPairView
from user.serializer import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['GET'])
def get_all_sales(request):
    if not request.user.is_authenticated:
        return Response({"detail": "Anda tidak memiliki izin untuk mengakses data ini."}, 
                        status=status.HTTP_401_UNAUTHORIZED)
    count = User.objects.filter(groups__name='sales').count()
    return Response({'count': count})

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EditUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = EditUserSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
class GroupListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GroupDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Group, pk=pk)

    def get(self, request, pk):
        group = self.get_object(pk)
        serializer = GroupSerializer(group)
        return Response(serializer.data)

    def put(self, request, pk):
        group = self.get_object(pk)
        serializer = GroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        group = self.get_object(pk)
        group.delete()
        return Response({"message": "Group deleted."}, status=status.HTTP_204_NO_CONTENT)
    
class AddUserToGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.data.get('username')
        group_name = request.data.get('group')
        
        if not request.user.groups.filter(name="admin").exists():
            return Response(
                {"detail": "Anda tidak memiliki izin untuk mengakses data ini."},
                status=status.HTTP_403_FORBIDDEN
            )

        if not username or not group_name:
            return Response({"error": "username and group are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, username=username)
        group = get_object_or_404(Group, name=group_name)
 
        user.groups.add(group)
        return Response({"message": f"User '{username}' added to group '{group_name}'."}, status=status.HTTP_200_OK)
    
class RemoveUserFromGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.data.get('username')
        group_name = request.data.get('group')
        
        if not request.user.groups.filter(name="admin").exists():
            return Response(
                {"detail": "Anda tidak memiliki izin untuk mengakses data ini."},
                status=status.HTTP_403_FORBIDDEN
            )

        if not username or not group_name:
            return Response({"error": "username and group are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, username=username)
        group = get_object_or_404(Group, name=group_name)

        if group not in user.groups.all():
            return Response({"error": f"User '{username}' is not in group '{group_name}'."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.groups.remove(group)
        return Response({"message": f"User '{username}' removed from group '{group_name}'."},
                        status=status.HTTP_200_OK)
        
        
class GetAllUsersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.groups.filter(name="admin").exists():
            return Response(
                {"detail": "Anda tidak memiliki izin untuk mengakses data ini."},
                status=status.HTTP_403_FORBIDDEN
            )

        users = User.objects.all().order_by('-id').exclude(groups__name='admin')
        serializer = UserDetailSerializer(users, many=True)
        return Response(serializer.data)
    
