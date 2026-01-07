from django.urls import path
from .views import Signup,Login,PackageDetails,Index,Navbar,Footer,Packagelist,MyBooking,Logout,PackageBooking,RateReviewAPI,Hotels,BookRoom,HotelMyBooking
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

app_name = "tourister"

urlpatterns = [
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('packagedetails/', PackageDetails.as_view(), name='Packagedetails'),
    path('packagedetails/<int:pk>/', PackageDetails.as_view(), name='Packagedetails'),
    path('index/', Index.as_view(), name='index'),
    path('navbar/', Navbar.as_view(), name='navbar'),
    path('footer/', Footer.as_view(), name='footer'),
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
]
