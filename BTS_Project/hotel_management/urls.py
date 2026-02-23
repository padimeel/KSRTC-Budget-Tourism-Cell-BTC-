from django.urls import path
from .views import *

app_name='hotel'

urlpatterns = [
    path('hotellogin/', HotelLogin.as_view(), name='hotellogin'),
    path('hotelinfo/', HotelInfo.as_view(), name='hotelinfo'),
    path('rooms/', RoomManagementView.as_view(), name='roommanage'),
    path('rooms/<int:pk>/', RoomManagementView.as_view(), name='roomdetail'),
    path('displaybooking/', DisplayRoomBookings.as_view(), name='displaybooking'),
    path('logout/', HotelLogout.as_view(), name='logout'),
    
    
    path('displayroombookings-template/', DisplayRoomBookingsTemplate.as_view(), name='displayroombookings_template'),
    path('home-template/', HomeTemplate.as_view(), name='home_template'),
    path('hotellogin-template/', HotelLoginTemplate.as_view(), name='hotellogin_template'),
    path('hotelprofile-template/', HotelProfileTemplate.as_view(), name='hotelprofile_template'),
    path('roommanagement-template/', RoomManagementTemplate.as_view(), name='roommanagement_template'),
    
]
