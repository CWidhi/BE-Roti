from django.urls import path
from toko.views import *

urlpatterns = [
    # path('', views.GetAllAndCreated, name='toko'),
    # path('<int:toko_id>', views.GetEditDeleteById, name='toko'),
    path('store/', TokoList.as_view(), name='toko-list'),
    path('store/<int:toko_id>', TokoDetail.as_view(), name='toko-detail'),
    path('jalur/', JalurList.as_view(), name='jalur-list'),
    path('jalur/<int:pk>', JalurList.as_view(), name='jalur-detail'),
    path('jalur/assign/', AssignJalurM2MView.as_view(), name='assign-jalur-to-user'),
    path('jalur/remove/', RemoveJalurFromUserAPIView.as_view(), name='remove-jalur-user'),
    path("jalur/user/<int:user_id>/", get_user_jalur, name="get_user_jalur"),
    path("jalur/count", get_jalur_count, name="get_jalur_count"),
 ] 