from django.urls import path
from .views import PackageAPI, DayWiseItineraryAPI,DepotSignup,DepotManagerList,UpdatePackage,AdminLogin,AdminLogout,BookingList,HotelSignup,HotelList,Dashboard

app_name='admin_site'
urlpatterns = [
    path('packages/', PackageAPI.as_view(), name='packages'),          
    path('packages/<int:pk>/', PackageAPI.as_view(), name='packages'), 

    path('itineraries/', DayWiseItineraryAPI.as_view()),          
    path('itineraries/<int:pk>/', DayWiseItineraryAPI.as_view()),

    path('depotsignup/', DepotSignup.as_view(), name='depotsignup'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    
    path('managerlist/', DepotManagerList.as_view(), name='managerlist'),
    path('managerlist/<int:pk>/', DepotManagerList.as_view(), name='managerlist'),
    
    path('updatepackage/<int:pk>/', UpdatePackage.as_view(), name='updatepackage'),

    path('adminlogin/', AdminLogin.as_view(), name='adminlogin'),
    path('adminlogout/', AdminLogout.as_view(), name='adminlogout'),
    path('bookinglist/', BookingList.as_view(), name='bookinglist'),
    
    path('hotelsignup/', HotelSignup.as_view(), name='hotelsignup'),
    
    path('hotellist/', HotelList.as_view(), name='hotel-list'),
    path('hotellist/<int:pk>/', HotelList.as_view(), name='hotel-delete'),
    
]

9