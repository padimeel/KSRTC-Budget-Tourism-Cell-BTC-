from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

app_name = "tourister"

urlpatterns = [
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('packagedetails/', PackageDetails.as_view(), name='Packagedetails'),
    path('packagedetails/<int:pk>/', PackageDetails.as_view(), name='Packagedetails'),
    path('index/', Index.as_view(), name='index'),
    path('packagelist/', Packagelist.as_view(), name='packagelist'),
    path('mybooking/', MyBooking.as_view(), name='mybooking'),
    path('mybooking/<int:pk>/', MyBooking.as_view(), name='mybooking'),
    path('logout/', Logout.as_view(), name='logout'),
    path('packagebooking/', PackageBooking.as_view(), name='packagebooking'),
    path('packagebooking/<int:pk>/', PackageBooking.as_view(), name='packagebooking'),
    path('token/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view(), name='refreshtoken'),
    path('ratereview/', RateReviewAPI.as_view(), name='ratereview'),
    path('hotels/', Hotels.as_view(), name='hotels'),
    path('roombook/', BookRoom.as_view(), name='bookroom'),
    path('roombook/<int:room_id>/', BookRoom.as_view(), name='bookroom'),
    path('hotelmybooking/', HotelMyBooking.as_view(), name='hotelmybooking'),
    
    
    # General Page Endpoints
    path('index-template/', IndexTemplate.as_view(), name='index_template'),
    path('signup-template/', SignupTemplate.as_view(), name='signup_template'),
    path('login-template/', LoginTemplate.as_view(), name='login_template'),
    
    
    path('hotels-template/', HotelsTemplate.as_view(), name='hotels_template'),
    path('packagelist-template/', PackageListTemplate.as_view(), name='packagelist_template'),
    path('packagedetails-template/', PackageDetailsTemplate.as_view(), name='packagedetails_template'),
    path('packagedetails-template/<int:pk>/', PackageDetailsTemplate.as_view(), name='packagedetails_template'),

    # Booking Endpoints
    path('mybooking-template/', MyBookingTemplate.as_view(), name='mybooking_template'),
    path('hotel-mybookings-template/', HotelMyBookingsTemplate.as_view(), name='hotel_mybookings_template'),
    path('roombooking-template/', RoomBookingTemplate.as_view(), name='roombooking_template'),
    path('roombooking-template/<int:pk>/', RoomBookingTemplate.as_view(), name='roombooking_template'),
    path('packagebooking-template/', PackageBookingTemplate.as_view(), name='packagebooking_template'),
    path('packagebooking-template/<int:pk>/', PackageBookingTemplate.as_view(), name='packagebooking_template'),

    # Payment Endpoints
    path('payment-template/', PaymentTemplate.as_view(), name='payment_template'),
    path('payment-success-template/', PaymentSuccessTemplate.as_view(), name='payment_success_template'),
]
