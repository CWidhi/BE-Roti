from django.urls import path
from toko.views import TokoList, TokoDetail, JalurList, AssignJalurM2MView, RemoveJalurFromUserAPIView

urlpatterns = [
    # path('', views.GetAllAndCreated, name='toko'),
    # path('<int:toko_id>', views.GetEditDeleteById, name='toko'),
    path('store/', TokoList.as_view(), name='toko-list'),
    path('store/<int:toko_id>', TokoDetail.as_view(), name='toko-detail'),
    path('jalur/', JalurList.as_view(), name='jalur-list'),
    path('jalur/<int:pk>', JalurList.as_view(), name='jalur-detail'),
    path('jalur/assign/', AssignJalurM2MView.as_view(), name='assign-jalur-to-user'),
    path('jalur/remove/', RemoveJalurFromUserAPIView.as_view(), name='remove-jalur-user'),
 ] 