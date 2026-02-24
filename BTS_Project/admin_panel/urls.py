from django.urls import path
from .views import *

app_name='admin_site'
urlpatterns = [
    path('packages/', PackageAPI.as_view(), name='packages'),          
    path('packages/<int:pk>/', PackageAPI.as_view(), name='packages'), 

    path('itineraries/', DayWiseItineraryAPI.as_view()),          
    path('itineraries/<int:pk>/', DayWiseItineraryAPI.as_view()),

    path('depotsignup/', DepotSignup.as_view(), name='depotsignup'),
    path('depotsignup/<int:pk>/', DepotSignup.as_view(), name='depotsignup'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    
    
    path('updatepackage/<int:pk>/', UpdatePackage.as_view(), name='updatepackage'),

    path('adminlogin/', AdminLogin.as_view(), name='adminlogin'),
    path('adminlogout/', AdminLogout.as_view(), name='adminlogout'),
    path('bookinglist/', BookingList.as_view(), name='bookinglist'),
    
    path('hotelsignup/', HotelSignup.as_view(), name='hotelsignup'),
    
    path('hotellist/', HotelList.as_view(), name='hotel-list'),
    path('hotellist/<int:pk>/', HotelList.as_view(), name='hotel-delete'),
    
    path('addhotel-template/', AddHotelTemplate.as_view(), name='addhotel_template'),
    path('addpackage-template/', AddPackageTemplate.as_view(), name='addpackage_template'),
    path('adminlogin-template/', AdminLoginTemplate.as_view(), name='adminlogin_template'),
    path('bookinglist-template/', BookingListTemplate.as_view(), name='bookinglist_template'),
    path('dashboard-template/', DashboardTemplate.as_view(), name='dashboard_template'),
    path('depotmanagers-template/', DepotManagersTemplate.as_view(), name='depotmanagers_template'),
    path('depotsignup-template/', DepotSignupTemplate.as_view(), name='depotsignup_template'),
    path('hotellist-template/', HotelListTemplate.as_view(), name='hotellist_template'),
]

9