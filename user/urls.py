from django.urls import path
from rest_framework_simplejwt.views import (TokenRefreshView)
from .views import *


urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('edit/user/', EditUserView.as_view(), name='edit-user'),
    path('me/', MeView.as_view(), name='me'),
    path('roles/', GroupListCreateAPIView.as_view(), name='group-list-create'),
    path('roles/<int:pk>/', GroupDetailAPIView.as_view(), name='group-detail'),
    path('roles/assign-user/', AddUserToGroupAPIView.as_view(), name='assign-user-to-group'),
    path('roles/remove-user/', RemoveUserFromGroupAPIView.as_view(), name='remove-user-from-group'),
    path('all/users/', GetAllUsersAPIView.as_view(), name='get-all-users'),
    path('count/sales/', get_all_sales, name='get-all-users'),
]