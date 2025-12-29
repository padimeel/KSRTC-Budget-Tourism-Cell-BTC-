from django.urls import path
from .views import Signup,Login,PackageDetails,Index,Navbar,Footer,Payment,Payment_Success,Packagelist,MyBooking,Logout,PackageBooking,RateReviewAPI
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
    path('payment/', Payment.as_view(), name='payment'),
    path('payment_success/', Payment_Success.as_view(), name='payment_sucess'),
    path('packagelist/', Packagelist.as_view(), name='packagelist'),
    path('mybooking/', MyBooking.as_view(), name='mybooking'),
    path('mybooking/<int:pk>/', MyBooking.as_view(), name='mybooking'),
    path('logout/', Logout.as_view(), name='logout'),
    path('packagebooking/', PackageBooking.as_view(), name='packagebooking'),
    path('packagebooking/<int:pk>/', PackageBooking.as_view(), name='packagebooking'),
    path('token/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view(), name='refreshtoken'),
    path('ratereview/', RateReviewAPI.as_view(), name='ratereview')
]
