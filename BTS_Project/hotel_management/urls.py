from django.urls import path
from .views import HotelLogin,Home,HotelInfo,HotelLogout,RoomManagementView,DisplayRoomBookings

app_name='hotel'

urlpatterns = [
    path('hotellogin/', HotelLogin.as_view(), name='hotellogin'),
    path('home/', Home.as_view(), name='home'),
    path('hotelinfo/', HotelInfo.as_view(), name='hotelinfo'),
    path('rooms/', RoomManagementView.as_view(), name='roommanage'),
    path('rooms/<int:pk>/', RoomManagementView.as_view(), name='roomdetail'),
    path('displaybooking/', DisplayRoomBookings.as_view(), name='displaybooking'),
    path('logout/', HotelLogout.as_view(), name='logout'),
]
